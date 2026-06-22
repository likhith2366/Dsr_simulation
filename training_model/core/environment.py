"""
DSR Environment (Simulator)
============================
Pure physics only — no decision logic here.

Computation each step:
  state(t-1) + action(t) --> state(t)

  1. Move each agent forward by speed × 1h along their assigned path
  2. Check fault discovery at new positions / traversed edges
  3. Apply repair progress to active faults
  4. Restore EGraph edges for newly repaired faults; close section switches
  5. Recompute powered nodes via EGraph BFS
  6. Update load on/off states

All strategy (where to move, which fault to repair) lives in policy.py.
To swap the decision maker: env.policy = YourPolicy()
"""

from typing import Dict, List, Set
from .graphs import TGraph, EGraph
from .agents import RepairCrew, Scout, MPS, DamagePoint, Load
from .policy import GreedyPolicy
from ..config.ieee13new_cases import IEEE13NewNetwork as IEEE13Network, IEEE13NewCases as IEEE13Cases
from ..config.ieee13new_cases import IEEE13NewNetwork, IEEE13NewCases


class DSREnvironment:

    def __init__(self, policy=None):
        self.tgraph  = TGraph()
        self.egraph  = EGraph()
        self.rcs:    Dict[str, RepairCrew]  = {}
        self.scouts: Dict[str, Scout]       = {}
        self.mps:    Dict[str, MPS]         = {}
        self.faults: Dict[str, DamagePoint] = {}
        self.loads:  Dict[str, Load]        = {}
        self.time    = 0
        self.case_name = None
        self.network = IEEE13Network  # default; overridden by setup()
        self.policy  = policy if policy is not None else GreedyPolicy()

        # Nodes physically arrived at by any agent (truly visited)
        self.global_visited: Set[str] = set()
        # Nodes currently claimed as a travel target (prevents duplicate assignments)
        # Separate from global_visited so unclaimed nodes stay searchable
        self.globally_claimed: Set[str] = set()
        # Nodes the operator knows are in outage (from SCADA/customer calls).
        self.outage_zones: Set[str] = set()
        # RCs currently in search mode (vs moving to a known fault)
        self.rc_searching: Set[str] = set()

    # ─────────────────────────────────────────
    # Setup
    # ─────────────────────────────────────────

    def setup(self, case_name: str, num_scouts: int = 1, known_faults: bool = False,
              network_cls=None, cases_cls=None):
        self.time = 0
        self.case_name = case_name
        self.rcs    = {}
        self.scouts = {}
        self.mps    = {}
        self.faults = {}
        self.loads  = {}
        self.tgraph = TGraph()
        self.egraph = EGraph()
        self.global_visited  = set()
        self.globally_claimed = set()
        self.outage_zones    = set()
        self.rc_searching    = set()

        self.network = network_cls if network_cls is not None else IEEE13Network
        _cases_cls   = cases_cls   if cases_cls   is not None else IEEE13Cases
        net  = self.network
        case = _cases_cls.get(case_name)

        # Build TGraph
        for _, frm, to, km in net.ROADS:
            self.tgraph.add_node(frm)
            self.tgraph.add_node(to)
            self.tgraph.add_edge(f'R_{frm}_{to}', frm, to, km)

        # Build EGraph
        for node_id, node_type in net.NODES.items():
            self.egraph.add_node(node_id, node_type)
        for eid, frm, to, km, state in net.EDGES:
            self.egraph.add_edge(eid, frm, to, state)

        # Loads
        for load_id, ldata in net.LOADS.items():
            self.loads[load_id] = Load(load_id, ldata['node'], ldata['P'], ldata['Q'], ldata['W'])

        # Faults (hidden + apply to EGraph)
        for f in case['faults']:
            dp = DamagePoint(f['id'], f['type'],
                             node=f.get('node'),
                             edge=f.get('edge'),
                             demand=f['demand'],
                             cap=f['cap'])
            self.faults[dp.id] = dp
            self.egraph.apply_fault(f)

        # RCs — mark start as visited and check for faults right there
        for rc_id, rdata in case['repair_crews'].items():
            rc = RepairCrew(rc_id, rdata['position'], rdata['speed'],
                            rdata['efficiency'], rdata['resources'])
            self.rcs[rc_id] = rc
            self.global_visited.add(rc.position)
            self.globally_claimed.add(rc.position)

        # MPS
        for mps_id, mdata in case.get('mobile_power', {}).items():
            mps = MPS(mps_id, mdata['position'], mdata['speed'],
                      mdata['p_limit'], mdata['energy'])
            self.mps[mps_id] = mps

        # Scouts — start at RC positions in insertion order (deterministic)
        rc_positions = list(dict.fromkeys(r.position for r in self.rcs.values()))
        for i in range(num_scouts):
            sid = f'Scout{i+1}'
            pos = rc_positions[i % len(rc_positions)]
            scout = Scout(sid, pos, speed=10.0)
            self.scouts[sid] = scout
            self.global_visited.add(pos)
            self.globally_claimed.add(pos)

        # ── Section protection: open switches for sections with faults,
        #    then auto-compute outage zones from EGraph BFS ──────────────
        affected_sections: Set[str] = set()
        for dp in self.faults.values():
            affected_sections.update(self._fault_in_sections(dp))
        for sec_name in affected_sections:
            self._open_section_switches(sec_name)
        self._recompute_outage_zones()

        self._update_loads()

        # Hand off initial assignments to the policy
        self.policy.on_setup(self.get_policy_state(), known_faults)

    # ─────────────────────────────────────────
    # Time Step
    # ─────────────────────────────────────────

    def step(self) -> dict:
        self.time += 1
        events = []

        # ── 1. Step RCs (move + repair) ──────────────────────
        for rc in self.rcs.values():
            prev_pos = rc.position

            # Snapshot fault states before step
            before = {dp_id: dp.state for dp_id, dp in self.faults.items()}

            rc_events = rc.step(self.faults, current_time=self.time)
            events.extend(rc_events)

            # If RC arrived at new node → mark physically visited + check discovery
            if rc.position != prev_pos or rc.state == 'idle':
                self.global_visited.add(rc.position)
                self.globally_claimed.add(rc.position)
                events.extend(self._check_discovery(rc.position, rc.id, 'RC'))
                # Edge traversal: discover edge faults on the segment just crossed
                if rc.position != prev_pos:
                    events.extend(self._check_edge_traversal(prev_pos, rc.position, rc.id, 'RC'))
            # If RC became idle, clear search flag
            if rc.state == 'idle':
                self.rc_searching.discard(rc.id)

            # Restore EGraph for any newly repaired faults
            for dp_id, dp in self.faults.items():
                if before[dp_id] == 'active' and dp.state == 'repaired':
                    self._restore_fault(dp)
                    # Clear on_edge for any RC that was stopped on this edge
                    if dp.type == 'edge':
                        for r in self.rcs.values():
                            if r.on_edge and set(r.on_edge) == set(dp.edge or []):
                                r.on_edge = None

        # ── 2. Move Scouts ───────────────────────────────────
        for scout in self.scouts.values():
            prev_scout_pos = scout.position
            arrived_at = scout.step(current_time=self.time)
            if arrived_at:
                self.global_visited.add(arrived_at)
                self.globally_claimed.add(arrived_at)
                events.append(f'Scout {scout.id} arrived at {arrived_at}')
                events.extend(self._check_discovery(arrived_at, scout.id, 'Scout'))
                # Edge traversal: discover edge faults on the segment just crossed
                events.extend(self._check_edge_traversal(prev_scout_pos, arrived_at, scout.id, 'Scout'))
                # Policy decides next target for this scout
                self.policy.on_scout_arrived(self.get_policy_state(), scout.id, arrived_at)

        # ── 2c. Step MPS (move + connect) ───────────────────────
        for mps in self.mps.values():
            arrived_at = mps.step(current_time=self.time)
            if arrived_at:
                events.append(f'{mps.id} arrived at {arrived_at}')
                self.policy.on_mps_arrived(self.get_policy_state(), mps, arrived_at, events)
            # Physics: auto-disconnect if grid now powers this node
            if mps.state == 'connected':
                grid_powered = self.egraph.get_powered_nodes()
                if mps.position in grid_powered:
                    mps.disconnect()
                    events.append(f'{mps.id} disconnected at {mps.position} (grid restored)')
            # Policy: standing by — connect or reassign
            if mps.state == 'idle' and mps.energy > 0:
                self.policy.on_mps_idle(self.get_policy_state(), mps, events)

        # ── 2b. Policy: redirect moving RCs to newly discovered faults ──
        self.policy.on_fault_discovered(self.get_policy_state(), events)

        # ── 3. Policy: assign idle RCs (repair / traverse / search) ─────
        for rc in self.rcs.values():
            if rc.state == 'idle' and rc.repair_target is None and rc.resources > 0:
                self.policy.on_rc_idle(self.get_policy_state(), rc, events)

        # ── 4. Update power ──────────────────────────────────
        self._update_loads()

        return {
            'time':   self.time,
            'events': events,
            'reward': self.get_reward(),
            'done':   self.is_done()
        }

    # ─────────────────────────────────────────
    # Coordinated Search (shared visited set)
    # ─────────────────────────────────────────
    # Decisions live in policy.py — these helpers remain here because
    # they are pure simulator utilities (path planning, movement commands)
    # that the policy calls back into.

    # ─────────────────────────────────────────
    # Discovery
    # ─────────────────────────────────────────

    def _check_edge_traversal(self, from_node: str, to_node: str,
                              agent_id: str, agent_type: str) -> List[str]:
        """Discover edge faults when an agent physically traverses the faulted cable segment.
        Also sets on_edge for already-discovered active faults so RC stops at midpoint."""
        events = []
        for dp in self.faults.values():
            if dp.type != 'edge':
                continue
            if dp.edge and {from_node, to_node} == set(dp.edge):
                agent = self.rcs.get(agent_id) or self.scouts.get(agent_id)
                if not dp.discovered:
                    dp.discovered = True
                    dp.discovered_by = f'{agent_type}:{agent_id}'
                    dp.discovered_at_step = self.time
                    if agent:
                        agent.log_discovery(dp.id, self.time)
                    events.append(
                        f'*** {agent_type} {agent_id} DISCOVERED {dp.id} '
                        f'on edge {from_node}-{to_node} (t={self.time}h) ***'
                    )
                # Only RC agents stop at midpoint; Scout keeps moving (no on_edge)
                if agent_type == 'RC' and dp.state == 'active':
                    rc_agent = self.rcs.get(agent_id)
                    if rc_agent:
                        rc_agent.on_edge = (from_node, to_node)
        return events

    def _check_discovery(self, position: str, agent_id: str, agent_type: str) -> List[str]:
        events = []
        for dp in self.faults.values():
            if dp.discovered:
                continue
            found = False
            if dp.type == 'node' and dp.node == position:
                found = True
            elif dp.type == 'edge' and dp.edge and position in dp.edge:
                # Discovered by arriving at an endpoint node (fallback when traversal didn't happen)
                found = True
            if found:
                dp.discovered = True
                dp.discovered_by = f'{agent_type}:{agent_id}'
                dp.discovered_at_step = self.time
                # Log to agent stats
                agent = self.rcs.get(agent_id) or self.scouts.get(agent_id)
                if agent:
                    agent.log_discovery(dp.id, self.time)
                events.append(
                    f'*** {agent_type} {agent_id} DISCOVERED {dp.id} '
                    f'at {position} (t={self.time}h) ***'
                )
        return events

    # ─────────────────────────────────────────
    # Section Protection Helpers
    # ─────────────────────────────────────────

    def _fault_in_sections(self, dp: DamagePoint) -> List[str]:
        """Return list of section names whose nodes contain this fault."""
        affected = []
        for sec_name, sec_data in self.network.SECTIONS.items():
            sec_nodes = sec_data['nodes']
            if dp.type == 'node' and dp.node in sec_nodes:
                affected.append(sec_name)
            elif dp.type == 'edge' and dp.edge:
                if dp.edge[0] in sec_nodes or dp.edge[1] in sec_nodes:
                    affected.append(sec_name)
        return affected

    def _open_section_switches(self, section_name: str):
        """Open all switch edges for the given section (protection trip)."""
        sec = self.network.SECTIONS.get(section_name)
        if sec:
            for eid in sec['switch_edges']:
                self.egraph.set_edge_state(eid, 'open')

    def _close_section_switches(self, section_name: str):
        """Close all switch edges for the given section (restoration)."""
        sec = self.network.SECTIONS.get(section_name)
        if sec:
            for eid in sec['switch_edges']:
                self.egraph.set_edge_state(eid, 'closed')

    def _section_has_active_faults(self, section_name: str) -> bool:
        """True if any active (unrepaired) fault lies within the section."""
        sec_nodes = self.network.SECTIONS.get(section_name, {}).get('nodes', set())
        for dp in self.faults.values():
            if dp.state == 'active':
                if dp.type == 'node' and dp.node in sec_nodes:
                    return True
                if dp.type == 'edge' and dp.edge:
                    if dp.edge[0] in sec_nodes or dp.edge[1] in sec_nodes:
                        return True
        return False

    def _get_section_for_node(self, node: str) -> str:
        """Return the section name containing this node, or None."""
        for sec_name, sec_data in self.network.SECTIONS.items():
            if node in sec_data['nodes']:
                return sec_name
        return None

    def _section_safe_for_mps(self, section_name: str) -> bool:
        """
        True if MPS is allowed to power this section.
        Requires no active faults AND confirmed fault-free:
          - all faults globally discovered (full knowledge, none active here), OR
          - all nodes in the section have been physically visited by an agent.
        """
        if self._section_has_active_faults(section_name):
            return False
        if all(dp.discovered for dp in self.faults.values()):
            return True
        sec_nodes = self.network.SECTIONS.get(section_name, {}).get('nodes', set())
        return sec_nodes.issubset(self.global_visited)

    def _recompute_outage_zones(self):
        """Set outage_zones to all EGraph nodes not reachable from Grid via closed edges."""
        powered = self.egraph.get_powered_nodes()
        self.outage_zones = set(self.egraph.nodes.keys()) - powered

    def _rc_at_fault(self, rc: RepairCrew, dp: DamagePoint) -> bool:
        if dp.type == 'node':
            return rc.position == dp.node
        if dp.type == 'edge' and dp.edge:
            # RC must have traversed the edge (on_edge set) to repair at midpoint
            return bool(rc.on_edge and set(rc.on_edge) == set(dp.edge))
        return False

    def _restore_fault(self, dp: DamagePoint):
        """Restore EGraph edges after fault repaired → loads turn ON."""
        dp.repaired_at_step = self.time
        self.egraph.restore_fault({'type': dp.type, 'node': dp.node, 'edge': dp.edge})
        # Close section switch if this section now has no remaining active faults
        for sec_name in self._fault_in_sections(dp):
            if not self._section_has_active_faults(sec_name):
                self._close_section_switches(sec_name)
                # If section still dark (parent feeder faulted), try tie-switch restoration
                self._attempt_tie_restoration(sec_name)
        self._recompute_outage_zones()
        self._update_loads()

    def _electrical_dist_to_grid(self, start: str) -> float:
        """Dijkstra through CLOSED electrical edges only. Returns km to nearest GRID, -1 if unreachable."""
        import heapq
        grid_nodes = {n for n, t in self.egraph.nodes.items() if t == 'GRID'}
        if start in grid_nodes:
            return 0.0
        km_lookup = {}
        for _eid, _fn, _tn, _km, _st in self.network.EDGES:
            km_lookup[(_fn, _tn)] = _km
            km_lookup[(_tn, _fn)] = _km
        dist = {start: 0.0}
        pq = [(0.0, start)]
        while pq:
            d, n = heapq.heappop(pq)
            if n in grid_nodes:
                return d
            if d > dist.get(n, float('inf')):
                continue
            for neighbor, eid in self.egraph.adjacency.get(n, []):
                edge = self.egraph.edges[eid]
                if edge['state'] != 'closed':
                    continue
                km = km_lookup.get((n, neighbor), 1.0)
                nd = d + km
                if nd < dist.get(neighbor, float('inf')):
                    dist[neighbor] = nd
                    heapq.heappush(pq, (nd, neighbor))
        return -1.0

    def _attempt_tie_restoration(self, section_name: str) -> str:
        """
        If section is still dark after its own switches re-close, try closing
        ONE open tie switch (the one whose other endpoint is closest to GRID
        through currently-live edges). Returns the closed edge_id, or None.
        Only one tie closed per section — avoids parallel loops.
        """
        sec = self.network.SECTIONS.get(section_name)
        if not sec:
            return None
        sec_nodes = sec['nodes']
        powered = self.egraph.get_powered_nodes()
        # If any section node already powered (via normal feeder), do nothing
        if any(n in powered for n in sec_nodes):
            return None
        own_switch_edges = set(sec.get('switch_edges', []))
        # Collect open switch edges that bridge this section to outside
        candidates = []  # (edge_id, outside_node, dist_to_grid)
        for eid, edge in self.egraph.edges.items():
            if edge['state'] != 'open':
                continue
            if eid in own_switch_edges:
                continue
            fn, tn = edge['from'], edge['to']
            if fn in sec_nodes and tn not in sec_nodes:
                outside = tn
            elif tn in sec_nodes and fn not in sec_nodes:
                outside = fn
            else:
                continue
            d = self._electrical_dist_to_grid(outside)
            if d >= 0:
                candidates.append((eid, outside, d))
        if not candidates:
            return None
        # Pick the candidate with shortest distance to grid (one tie only — no loops)
        candidates.sort(key=lambda c: c[2])
        best_eid, best_outside, best_dist = candidates[0]
        self.egraph.set_edge_state(best_eid, 'closed')
        return best_eid

    # ─────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────

    def open_switch(self, switch_id: str) -> dict:
        """Open a switch — sets all edges adjacent to this switch node to 'open'."""
        if self.egraph.nodes.get(switch_id) != 'SWITCH':
            return {'status': 'error', 'msg': f'{switch_id} is not a switch'}
        for eid, edge in self.egraph.edges.items():
            if edge['from'] == switch_id or edge['to'] == switch_id:
                self.egraph.set_edge_state(eid, 'open')
        self._recompute_outage_zones()
        self._update_loads()
        return {'status': 'ok', 'switch': switch_id, 'state': 'open'}

    def close_switch(self, switch_id: str) -> dict:
        """Close a switch — sets all edges adjacent to this switch node to 'closed'."""
        if self.egraph.nodes.get(switch_id) != 'SWITCH':
            return {'status': 'error', 'msg': f'{switch_id} is not a switch'}
        for eid, edge in self.egraph.edges.items():
            if edge['from'] == switch_id or edge['to'] == switch_id:
                self.egraph.set_edge_state(eid, 'closed')
        self._recompute_outage_zones()
        self._update_loads()
        return {'status': 'ok', 'switch': switch_id, 'state': 'closed'}

    def get_switch_states(self) -> dict:
        """Return {switch_id: 'open'|'closed'} — the only switch info policy should see."""
        result = {}
        for sw_id, sw_type in self.egraph.nodes.items():
            if sw_type != 'SWITCH':
                continue
            # A switch is 'closed' if ALL its adjacent edges are closed, else 'open'
            adj_edges = [e for e in self.egraph.edges.values()
                         if e['from'] == sw_id or e['to'] == sw_id]
            if adj_edges and all(e['state'] == 'closed' for e in adj_edges):
                result[sw_id] = 'closed'
            else:
                result[sw_id] = 'open'
        return result

    def get_policy_state(self) -> 'PolicyState':
        """
        Filtered state for the policy — hides undiscovered faults,
        shows switches as open/closed only, includes loads with P/Q.
        """
        return PolicyState(self)

    def move_rc(self, rc_id: str, target: str) -> dict:
        rc = self.rcs.get(rc_id)
        if not rc:
            return {'status': 'error', 'msg': f'{rc_id} not found'}
        path, dist = self.tgraph.shortest_path(rc.position, target)
        if not path:
            return {'status': 'error', 'msg': f'No path to {target}'}
        rc.move_to(path, dist)
        return {'status': 'ok', 'path': path, 'distance': dist}

    def move_scout(self, scout_id: str, target: str) -> dict:
        scout = self.scouts.get(scout_id)
        if not scout:
            return {'status': 'error', 'msg': f'{scout_id} not found'}
        path, dist = self.tgraph.shortest_path(scout.position, target)
        if not path:
            return {'status': 'error', 'msg': f'No path to {target}'}
        scout.move_to(path, dist)
        return {'status': 'ok', 'path': path, 'distance': dist}

    # ─────────────────────────────────────────
    # Power
    # ─────────────────────────────────────────

    def _update_loads(self):
        mps_sources = [m.position for m in self.mps.values() if m.state == 'connected']
        powered = self.egraph.get_powered_nodes(mps_sources=mps_sources)
        for load in self.loads.values():
            load.state = 'on' if load.node in powered else 'off'


    # ─────────────────────────────────────────
    # State / Reward
    # ─────────────────────────────────────────

    def get_reward(self) -> float:
        return sum(l.weighted_power for l in self.loads.values())

    def is_done(self) -> bool:
        return all(dp.state == 'repaired' for dp in self.faults.values())

    def get_state(self) -> dict:
        return {
            'time':              self.time,
            'rcs':               {k: v.get_state() for k, v in self.rcs.items()},
            'scouts':            {k: v.get_state() for k, v in self.scouts.items()},
            'mps':               {k: v.get_state() for k, v in self.mps.items()},
            'loads':             {k: v.get_state() for k, v in self.loads.items()},
            'faults_discovered': {k: v.get_state() for k, v in self.faults.items() if v.discovered},
            'faults_hidden':     len([v for v in self.faults.values() if not v.discovered]),
            'global_visited':    len(self.global_visited),
            'total_nodes':       len(self.tgraph.nodes),
            'reward':            self.get_reward(),
            'done':              self.is_done()
        }

    def get_full_state(self) -> dict:
        s = self.get_state()
        s['faults_all']   = {k: v.get_state() for k, v in self.faults.items()}
        s['egraph_edges'] = {k: v['state'] for k, v in self.egraph.edges.items()}
        return s


class PolicyState:
    """
    Filtered view of DSREnvironment passed to policy callbacks.

    Rules:
      - Undiscovered faults are hidden (policy only sees dark nodes/loads)
      - Switches exposed as open/closed only — no power state
      - Loads include P and Q demand
      - Full env available via .env for action calls (move_rc, open_switch etc.)
    """

    def __init__(self, env: 'DSREnvironment'):
        self.env = env  # for action calls: state.env.move_rc(...)
        self.time = env.time

        # Agents — positions, states, and exact in-transit positions
        switch_nodes = {n for n, t in env.egraph.nodes.items() if t == 'SWITCH'}
        self.rcs    = {rid: {**rc.get_state(),    'exact': rc.exact_position(env.tgraph, switch_nodes)}    for rid, rc in env.rcs.items()}
        self.scouts = {sid: {**sc.get_state(),    'exact': sc.exact_position(env.tgraph, switch_nodes)}    for sid, sc in env.scouts.items()}
        self.mps    = {mid: {**mp.get_state(),    'exact': mp.exact_position(env.tgraph, switch_nodes)}    for mid, mp in env.mps.items()}

        # Only discovered faults visible
        self.discovered_faults = {
            fid: dp.get_state()
            for fid, dp in env.faults.items()
            if dp.discovered
        }
        dark = env.outage_zones - switch_nodes
        load_nodes = {l.node for l in env.loads.values()}

        self.dark_nodes       = dark                        # all unpowered (legacy, keep for compat)
        self.load_nodes       = load_nodes                  # every node with a load attached
        self.dark_load_nodes  = dark & load_nodes           # unpowered AND has demand
        self.dark_topo_nodes  = dark - load_nodes           # unpowered, no load (pure topology)

        # Loads with P, Q demand
        self.loads = {
            lid: {
                'node':  l.node,
                'state': l.state,
                'P':     l.P,
                'Q':     l.Q,
                'W':     l.W,
            }
            for lid, l in env.loads.items()
        }

        # Switches — open/closed only
        self.switches = env.get_switch_states()

        # Search helpers (needed by greedy policy)
        self.global_visited   = env.global_visited

        self.globally_claimed = env.globally_claimed
        self.outage_zones     = self.dark_load_nodes | self.dark_topo_nodes  # full dark set for search
        self.rc_searching     = env.rc_searching
        self.tgraph           = env.tgraph
        self.egraph           = env.egraph
        self.network          = env.network

        if getattr(env, '_raw_mode', False):
            import json as _j
            print(f'\n[SIMULATOR -> POLICY]  t={self.time}')
            print(_j.dumps({
                'time': self.time,
                'rcs': self.rcs,
                'scouts': self.scouts,
                'mps': self.mps,
                'discovered_faults': self.discovered_faults,
                'load_nodes': sorted(self.load_nodes),
                'dark_load_nodes': sorted(self.dark_load_nodes),
                'dark_topo_nodes': sorted(self.dark_topo_nodes),
                'loads': self.loads,
                'switches': self.switches,
                'global_visited': sorted(self.global_visited),
                'globally_claimed': sorted(self.globally_claimed),
                'rc_searching': sorted(self.rc_searching),
            }, indent=2, default=str))
