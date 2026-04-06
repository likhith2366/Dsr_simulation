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
from .agents import RepairCrew, Scout, DamagePoint, Load
from ..config.ieee13_cases import IEEE13Network, IEEE13Cases


class DSREnvironment:

    def __init__(self):
        self.tgraph  = TGraph()
        self.egraph  = EGraph()
        self.rcs:    Dict[str, RepairCrew]  = {}
        self.scouts: Dict[str, Scout]       = {}
        self.faults: Dict[str, DamagePoint] = {}
        self.loads:  Dict[str, Load]        = {}
        self.time    = 0
        self.case_name = None

        # ── Shared visited set (all agents contribute) ──────
        self.global_visited: Set[str] = set()

    # ─────────────────────────────────────────
    # Setup
    # ─────────────────────────────────────────

    def setup(self, case_name: str, num_scouts: int = 1):
        self.time = 0
        self.case_name = case_name
        self.rcs = {}
        self.scouts = {}
        self.faults = {}
        self.loads = {}
        self.tgraph = TGraph()
        self.egraph = EGraph()
        self.global_visited = set()

        net  = IEEE13Network
        case = IEEE13Cases.get(case_name)

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

        # RCs
        for rc_id, rdata in case['repair_crews'].items():
            rc = RepairCrew(rc_id, rdata['position'], rdata['speed'],
                            rdata['efficiency'], rdata['resources'])
            self.rcs[rc_id] = rc
            # Mark starting position as visited
            self.global_visited.add(rc.position)

        # Scouts — start at different positions from RCs to maximize coverage
        rc_positions = list({r.position for r in self.rcs.values()})
        for i in range(num_scouts):
            sid = f'Scout{i+1}'
            pos = rc_positions[i % len(rc_positions)]
            scout = Scout(sid, pos, speed=10.0)
            self.scouts[sid] = scout
            self.global_visited.add(pos)

        self._update_loads()

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

            rc_events = rc.step(self.faults)
            events.extend(rc_events)

            # If RC arrived at new node → mark visited + check discovery
            if rc.position != prev_pos or rc.state == 'idle':
                self.global_visited.add(rc.position)
                events.extend(self._check_discovery(rc.position, rc.id, 'RC'))

            # Restore EGraph for any newly repaired faults
            for dp_id, dp in self.faults.items():
                if before[dp_id] == 'active' and dp.state == 'repaired':
                    self._restore_fault(dp)

        # ── 2. Move Scouts ───────────────────────────────────
        for scout in self.scouts.values():
            arrived_at = scout.step()
            if arrived_at:
                self.global_visited.add(arrived_at)
                events.append(f'Scout {scout.id} arrived at {arrived_at}')
                events.extend(self._check_discovery(arrived_at, scout.id, 'Scout'))
                # Immediately assign next unvisited node
                self._send_to_next_unvisited(scout.id, 'scout')

        # ── 3. RC: auto-repair if at discovered fault ────────
        for rc in self.rcs.values():
            if rc.state == 'idle' and rc.repair_target is None:
                repaired = False
                for dp in self.faults.values():
                    if dp.discovered and dp.state == 'active' and self._rc_at_fault(rc, dp):
                        rc.start_repair(dp.id)
                        events.append(f'{rc.id} auto-started repair of {dp.id}')
                        repaired = True
                        break

                # ── RC: search if no repair task ─────────────
                if not repaired:
                    # Check if any discovered fault needs an RC to travel to it
                    assigned = self._assign_rc_to_discovered_fault(rc)
                    if assigned:
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
        Send agent to nearest GLOBALLY unvisited node.
        Marks the target as 'claimed' immediately so other agents
        don't go to the same node.
        """
        all_nodes = list(self.tgraph.nodes)
        unvisited = [n for n in all_nodes if n not in self.global_visited]

        if not unvisited:
            return  # All nodes visited

        # Get agent current position
        if agent_type == 'scout':
            agent = self.scouts.get(agent_id)
        else:
            agent = self.rcs.get(agent_id)

        if not agent or agent.state != 'idle':
            return

        # Find nearest unvisited node
        best_node, best_dist = None, float('inf')
        for node in unvisited:
            _, d = self.tgraph.shortest_path(agent.position, node)
            if 0 < d < best_dist:
                best_dist = d
                best_node = node

        if best_node:
            # Claim it immediately so no other agent targets same node
            self.global_visited.add(best_node)

            if agent_type == 'scout':
                self.move_scout(agent_id, best_node)
            else:
                self.move_rc(agent_id, best_node)

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

        # Check which ones already have an RC assigned or moving toward them
        rcs_targeting = set()
        for other_rc in self.rcs.values():
            if other_rc.id != rc.id and other_rc.repair_target:
                rcs_targeting.add(other_rc.repair_target)
            if other_rc.id != rc.id and other_rc.target:
                # RC moving to a fault location
                for dp in active_discovered:
                    fault_loc = dp.node if dp.type == 'node' else (dp.edge[0] if dp.edge else None)
                    if other_rc.target == fault_loc:
                        rcs_targeting.add(dp.id)

        # Find unassigned fault closest to this RC
        best_dp, best_dist = None, float('inf')
        for dp in active_discovered:
            if dp.id in rcs_targeting:
                continue
            fault_loc = dp.node if dp.type == 'node' else (dp.edge[0] if dp.edge else None)
            if fault_loc:
                _, d = self.tgraph.shortest_path(rc.position, fault_loc)
                if 0 < d < best_dist:
                    best_dist = d
                    best_dp = dp

        if best_dp:
            fault_loc = best_dp.node if best_dp.type == 'node' else best_dp.edge[0]
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
                events.append(f'*** {agent_type} {agent_id} DISCOVERED {dp.id} at {position}! ***')
        return events

    def _rc_at_fault(self, rc: RepairCrew, dp: DamagePoint) -> bool:
        if dp.type == 'node':
            return rc.position == dp.node
        return bool(dp.edge and rc.position in dp.edge)

    def _restore_fault(self, dp: DamagePoint):
        """Restore EGraph edges after fault repaired → loads turn ON."""
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
        powered = self.egraph.get_powered_nodes()
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
