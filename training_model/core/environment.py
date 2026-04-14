"""
DSR Environment
===============
- Shared visited_nodes across ALL agents (Scout + RCs)
- Scout uses optimized coverage: always picks nearest GLOBALLY unvisited node
- RC searches when idle and no repair task
- No two agents visit the same node twice
"""

from typing import Dict, List, Set
from .graphs import TGraph, EGraph
from .agents import RepairCrew, Scout, MPS, DamagePoint, Load
from ..config.ieee13_cases import IEEE13Network, IEEE13Cases


class DSREnvironment:

    def __init__(self):
        self.tgraph  = TGraph()
        self.egraph  = EGraph()
        self.rcs:    Dict[str, RepairCrew]  = {}
        self.scouts: Dict[str, Scout]       = {}
        self.mps:    Dict[str, MPS]         = {}
        self.faults: Dict[str, DamagePoint] = {}
        self.loads:  Dict[str, Load]        = {}
        self.time    = 0
        self.case_name = None

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

    def setup(self, case_name: str, num_scouts: int = 1, known_faults: bool = False):
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

        net  = IEEE13Network
        case = IEEE13Cases.get(case_name)

        # Load operator-observable outage zones (defined in test case config)
        self.outage_zones = set(case.get('outage_zones', []))

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

        # Scouts — start at different positions from RCs to maximize coverage
        rc_positions = list({r.position for r in self.rcs.values()})
        for i in range(num_scouts):
            sid = f'Scout{i+1}'
            pos = rc_positions[i % len(rc_positions)]
            scout = Scout(sid, pos, speed=10.0)
            self.scouts[sid] = scout
            self.global_visited.add(pos)
            self.globally_claimed.add(pos)

        self._update_loads()

        # Kick MPS toward unpowered sections immediately
        for mps in self.mps.values():
            self._assign_mps(mps, [])

        if known_faults:
            # Pre-reveal all faults and immediately assign RCs
            for dp in self.faults.values():
                dp.discovered = True
                dp.discovered_by = 'known'
                dp.discovered_at_step = 0
            for rc in self.rcs.values():
                # If already standing on a fault, start repair immediately
                started = self._try_auto_repair(rc)
                if not started:
                    self._assign_rc_to_discovered_fault(rc)
        else:
            # Check if any agent is already standing on a fault at t=0
            for rc in self.rcs.values():
                self._check_discovery(rc.position, rc.id, 'RC')
            for scout in self.scouts.values():
                self._check_discovery(scout.position, scout.id, 'Scout')

            # Kick scouts and RCs toward outage zone nodes
            for scout_id in self.scouts:
                self._send_to_next_unvisited(scout_id, 'scout')
            for rc_id in self.rcs:
                rc = self.rcs[rc_id]
                # If already on a discovered fault, start repair immediately
                started = self._try_auto_repair(rc)
                if not started:
                    assigned = self._assign_rc_to_discovered_fault(rc)
                    if not assigned:
                        self._send_to_next_unvisited(rc_id, 'rc')

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
            # If RC became idle, clear search flag
            if rc.state == 'idle':
                self.rc_searching.discard(rc.id)

            # Restore EGraph for any newly repaired faults
            for dp_id, dp in self.faults.items():
                if before[dp_id] == 'active' and dp.state == 'repaired':
                    self._restore_fault(dp)

        # ── 2. Move Scouts ───────────────────────────────────
        for scout in self.scouts.values():
            arrived_at = scout.step(current_time=self.time)
            if arrived_at:
                self.global_visited.add(arrived_at)
                self.globally_claimed.add(arrived_at)
                events.append(f'Scout {scout.id} arrived at {arrived_at}')
                events.extend(self._check_discovery(arrived_at, scout.id, 'Scout'))
                # Immediately assign next unvisited node
                self._send_to_next_unvisited(scout.id, 'scout')

        # ── 2c. Step MPS (move + connect) ───────────────────────
        for mps in self.mps.values():
            arrived_at = mps.step(current_time=self.time)
            if arrived_at:
                events.append(f'{mps.id} arrived at {arrived_at}')
                mps.connect()
                events.append(f'{mps.id} connected at {arrived_at} — restoring power')
            # Auto-disconnect if grid now powers this node (fault repaired)
            if mps.state == 'connected':
                grid_powered = self.egraph.get_powered_nodes()
                if mps.position in grid_powered:
                    mps.disconnect()
                    events.append(f'{mps.id} disconnected at {mps.position} (grid restored)')
            # Auto-assign idle MPS to best unpowered node
            if mps.state == 'idle' and mps.energy > 0:
                self._assign_mps(mps, events)

        # ── 2b. Redirect ALL moving RCs to any newly discovered / uncovered faults ──
        for rc in self.rcs.values():
            if rc.state == 'moving':
                old_target = rc.target  # capture BEFORE redirect changes it
                assigned = self._assign_rc_to_discovered_fault(rc)
                if assigned and rc.target != old_target:
                    # Genuinely redirected to a different location
                    if old_target and rc.id in self.rc_searching:
                        self.globally_claimed.discard(old_target)
                    self.rc_searching.discard(rc.id)
                    events.append(f'{rc.id} redirected to fault {assigned}')

        # ── 3. RC: auto-repair if at discovered fault ────────
        for rc in self.rcs.values():
            if rc.state == 'idle' and rc.repair_target is None and rc.resources > 0:
                repaired = False
                for dp in self.faults.values():
                    if dp.discovered and dp.state == 'active' and self._rc_at_fault(rc, dp):
                        # Respect cap: count how many RCs are already repairing this fault
                        currently_repairing = sum(
                            1 for r in self.rcs.values() if r.repair_target == dp.id
                        )
                        if currently_repairing < dp.cap:
                            rc.start_repair(dp.id)
                            events.append(f'{rc.id} auto-started repair of {dp.id}')
                            repaired = True
                            break

                # ── RC: search if no repair task ─────────────
                if not repaired and rc.resources > 0:
                    # Check if any discovered fault needs an RC to travel to it
                    assigned = self._assign_rc_to_discovered_fault(rc)
                    if assigned:
                        self.rc_searching.discard(rc.id)
                        events.append(f'{rc.id} moving to discovered fault {assigned}')
                    else:
                        # No known faults → search unvisited nodes
                        self._send_to_next_unvisited(rc.id, 'rc')

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

    def _send_to_next_unvisited(self, agent_id: str, agent_type: str):
        """
        Send agent to nearest unvisited node in an unpowered section.
        The grid operator knows which sections have no electricity —
        agents only search there. Powered sections are fine, no need to visit.
        Marks the target as 'claimed' immediately so other agents
        don't go to the same node.
        """
        # No undiscovered faults left — no need to search any more nodes
        if not any(not dp.discovered for dp in self.faults.values()):
            return

        if agent_type == 'scout':
            agent = self.scouts.get(agent_id)
        else:
            agent = self.rcs.get(agent_id)

        if not agent or agent.state != 'idle':
            return

        # Search only within the outage zone, only nodes not yet physically visited
        # and not currently claimed as a target by another agent.
        all_nodes = list(self.tgraph.nodes)
        zone = self.outage_zones if self.outage_zones else set(all_nodes)
        search_pool = [
            n for n in all_nodes
            if n in zone
            and n not in self.global_visited    # not yet physically visited
            and n not in self.globally_claimed  # not currently targeted
        ]

        if not search_pool:
            return  # All outage zone nodes covered or claimed

        # Find nearest node in the search pool
        best_node, best_dist = None, float('inf')
        for node in search_pool:
            _, d = self.tgraph.shortest_path(agent.position, node)
            if 0 < d < best_dist:
                best_dist = d
                best_node = node

        if best_node:
            # Claim target so no other agent is sent to the same node
            self.globally_claimed.add(best_node)

            if agent_type == 'scout':
                self.move_scout(agent_id, best_node)
            else:
                self.rc_searching.add(agent_id)
                self.move_rc(agent_id, best_node)

    def _try_auto_repair(self, rc: RepairCrew) -> bool:
        """Start repair if RC is already standing on a discovered active fault. Returns True if started."""
        for dp in self.faults.values():
            if dp.discovered and dp.state == 'active' and self._rc_at_fault(rc, dp):
                currently_repairing = sum(
                    1 for r in self.rcs.values() if r.repair_target == dp.id
                )
                if currently_repairing < dp.cap:
                    rc.start_repair(dp.id)
                    return True
        return False

    def _assign_rc_to_discovered_fault(self, rc: RepairCrew) -> str:
        """
        If a fault is discovered but no RC is heading to it,
        send this idle RC toward it.
        Returns fault_id if assigned, else None.
        """
        # Collect faults that need an RC
        active_discovered = [
            dp for dp in self.faults.values()
            if dp.discovered and dp.state == 'active'
        ]

        # Count how many RCs are already assigned (repairing, travelling, or standing on fault)
        # Only count RCs that still have resources (exhausted RCs can't contribute)
        rcs_per_fault: Dict[str, int] = {}
        for other_rc in self.rcs.values():
            if other_rc.id == rc.id:
                continue
            if other_rc.repair_target:
                rcs_per_fault[other_rc.repair_target] = rcs_per_fault.get(other_rc.repair_target, 0) + 1
            # Count RCs physically standing on a fault location (only if they have resources)
            if other_rc.resources > 0:
                for dp in active_discovered:
                    if self._rc_at_fault(other_rc, dp):
                        rcs_per_fault[dp.id] = rcs_per_fault.get(dp.id, 0) + 1
            # Count RCs moving toward a fault (only if they have resources)
            if other_rc.target and not other_rc.repair_target and other_rc.state == 'moving' and other_rc.resources > 0:
                for dp in active_discovered:
                    fault_loc = dp.node if dp.type == 'node' else (dp.edge[0] if dp.edge else None)
                    if other_rc.target == fault_loc:
                        rcs_per_fault[dp.id] = rcs_per_fault.get(dp.id, 0) + 1

        # Find fault that still has capacity and is closest to this RC
        best_dp, best_dist = None, float('inf')
        for dp in active_discovered:
            if rcs_per_fault.get(dp.id, 0) >= dp.cap:
                continue  # fault already at capacity
            fault_loc = dp.node if dp.type == 'node' else (dp.edge[0] if dp.edge else None)
            if fault_loc:
                _, d = self.tgraph.shortest_path(rc.position, fault_loc)
                if 0 < d < best_dist:
                    best_dist = d
                    best_dp = dp

        if best_dp:
            fault_loc = best_dp.node if best_dp.type == 'node' else best_dp.edge[0]
            # Already heading to this exact location — no need to re-route
            if fault_loc == rc.target:
                return None
            self.move_rc(rc.id, fault_loc)
            return best_dp.id

        return None

    # ─────────────────────────────────────────
    # Discovery
    # ─────────────────────────────────────────

    def _check_discovery(self, position: str, agent_id: str, agent_type: str) -> List[str]:
        events = []
        for dp in self.faults.values():
            if dp.discovered:
                continue
            found = False
            if dp.type == 'node' and dp.node == position:
                found = True
            elif dp.type == 'edge' and dp.edge and position in dp.edge:
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

    def _rc_at_fault(self, rc: RepairCrew, dp: DamagePoint) -> bool:
        if dp.type == 'node':
            return rc.position == dp.node
        return bool(dp.edge and rc.position in dp.edge)

    def _restore_fault(self, dp: DamagePoint):
        """Restore EGraph edges after fault repaired → loads turn ON."""
        dp.repaired_at_step = self.time
        self.egraph.restore_fault({'type': dp.type, 'node': dp.node, 'edge': dp.edge})
        self._update_loads()

    # ─────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────

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

    def _assign_mps(self, mps: MPS, events: list):
        """Send idle MPS to the unpowered node that would restore the most loads."""
        # Current powered nodes (without this MPS)
        other_mps = [m.position for m in self.mps.values()
                     if m.state == 'connected' and m.id != mps.id]
        grid_powered = self.egraph.get_powered_nodes(mps_sources=other_mps)

        # Find unpowered nodes in TGraph, score by loads they'd restore
        best_node, best_score, best_dist = None, 0, float('inf')
        for node in self.tgraph.nodes:
            if node in grid_powered:
                continue
            score = self.egraph.count_loads_if_source(node)
            if score == 0:
                continue
            _, d = self.tgraph.shortest_path(mps.position, node)
            if d < 0:
                continue
            # Prefer more loads restored; break ties by distance
            if score > best_score or (score == best_score and d < best_dist):
                best_score = score
                best_dist  = d
                best_node  = node

        if best_node and best_node != mps.position:
            path, dist = self.tgraph.shortest_path(mps.position, best_node)
            mps.move_to(path, dist)
            events.append(f'{mps.id} moving to {best_node} (restores {best_score} loads)')
        elif best_node == mps.position:
            mps.connect()
            events.append(f'{mps.id} connected at {mps.position} — restoring power')

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
