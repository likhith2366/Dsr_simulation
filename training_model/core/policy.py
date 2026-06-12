"""
Decision-Making Policy
======================
Separated from the simulator (environment.py).

Interface:
  state  = env.get_state()          # simulator exposes state
  policy.on_setup(env, known)       # initial agent assignments
  policy.on_scout_arrived(env, sid, node)   # scout arrived at node
  policy.on_mps_arrived(env, mps, node)     # mps arrived at node
  policy.on_mps_idle(env, mps)              # mps standing by
  policy.on_fault_discovered(env)           # new fault found — redirect RCs
  policy.on_rc_idle(env, rc)               # RC has nothing to do

Swap this class for an LLMPolicy (or RLPolicy) to change the decision maker
without touching the simulator.
"""

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .environment import DSREnvironment
    from .agents import RepairCrew, MPS


class GreedyPolicy:
    """
    Greedy nearest-neighbour policy (current baseline).
    All strategy logic lives here — the simulator only does physics.
    """

    # ── Initial assignments ─────────────────────────────────────────────

    def on_setup(self, env: 'DSREnvironment', known_faults: bool):
        """Called once after the environment is initialised."""
        if known_faults:
            for dp in env.faults.values():
                dp.discovered = True
                dp.discovered_by = 'known'
                dp.discovered_at_step = 0
            for rc in env.rcs.values():
                started = self._try_auto_repair(env, rc)
                if not started:
                    self._assign_rc_to_fault(env, rc)
        else:
            for rc in env.rcs.values():
                env._check_discovery(rc.position, rc.id, 'RC')
            for scout in env.scouts.values():
                env._check_discovery(scout.position, scout.id, 'Scout')

            for scout_id in env.scouts:
                self._send_to_next_unvisited(env, scout_id, 'scout')
            for rc_id, rc in env.rcs.items():
                started = self._try_auto_repair(env, rc)
                if not started:
                    assigned = self._assign_rc_to_fault(env, rc)
                    if not assigned:
                        self._send_to_next_unvisited(env, rc_id, 'rc')

        for mps in env.mps.values():
            self._assign_mps(env, mps, [])

    # ── Per-step callbacks ──────────────────────────────────────────────

    def on_scout_arrived(self, env: 'DSREnvironment', scout_id: str, node: str):
        """Scout reached a node — send it to the next unvisited dark node."""
        self._send_to_next_unvisited(env, scout_id, 'scout')

    def on_mps_arrived(self, env: 'DSREnvironment', mps: 'MPS', node: str, events: list):
        """MPS reached its target — connect if section is safe, else stand by."""
        sec = env._get_section_for_node(node)
        if sec is None or env._section_safe_for_mps(sec):
            mps.connect()
            events.append(f'{mps.id} connected at {node} — restoring power')
        else:
            events.append(f'{mps.id} standing by at {node} — awaiting section clearance')

    def on_mps_idle(self, env: 'DSREnvironment', mps: 'MPS', events: list):
        """MPS is idle (standing by) — connect if section cleared, else reassign."""
        sec = env._get_section_for_node(mps.position)
        other_sources = [m.position for m in env.mps.values()
                         if m.state == 'connected' and m.id != mps.id]
        grid_powered = env.egraph.get_powered_nodes(mps_sources=other_sources)
        if mps.position not in grid_powered and (sec is None or env._section_safe_for_mps(sec)):
            mps.connect()
            events.append(f'{mps.id} connected at {mps.position} — section cleared')
        else:
            self._assign_mps(env, mps, events)

    def on_fault_discovered(self, env: 'DSREnvironment', events: list):
        """A new fault was just discovered — redirect any moving RCs if needed."""
        for rc in env.rcs.values():
            if rc.state == 'moving':
                old_target = rc.target
                assigned = self._assign_rc_to_fault(env, rc)
                if assigned and rc.target != old_target:
                    if old_target and rc.id in env.rc_searching:
                        env.globally_claimed.discard(old_target)
                    env.rc_searching.discard(rc.id)
                    events.append(f'{rc.id} redirected to fault {assigned}')

    def on_rc_idle(self, env: 'DSREnvironment', rc: 'RepairCrew', events: list):
        """RC has nothing to do — try repair, move to fault, or search."""
        repaired = False

        # Edge fault: RC at one endpoint but hasn't traversed → go to other end
        for dp in env.faults.values():
            if (dp.discovered and dp.state == 'active' and dp.type == 'edge'
                    and dp.edge and rc.position in dp.edge and rc.on_edge is None):
                other = dp.edge[1] if rc.position == dp.edge[0] else dp.edge[0]
                path, dist = env.tgraph.shortest_path(rc.position, other)
                if path:
                    rc.move_to(path, dist)
                    events.append(f'{rc.id} traversing fault edge to {other}')
                    repaired = True
                break

        if not repaired:
            for dp in env.faults.values():
                if dp.discovered and dp.state == 'active' and env._rc_at_fault(rc, dp):
                    currently = sum(1 for r in env.rcs.values() if r.repair_target == dp.id)
                    if currently < dp.cap:
                        rc.start_repair(dp.id)
                        events.append(f'{rc.id} auto-started repair of {dp.id}')
                        repaired = True
                        break

        if not repaired and rc.resources > 0:
            assigned = self._assign_rc_to_fault(env, rc)
            if assigned:
                env.rc_searching.discard(rc.id)
                events.append(f'{rc.id} moving to discovered fault {assigned}')
            else:
                self._send_to_next_unvisited(env, rc.id, 'rc')

    # ── Internal helpers ────────────────────────────────────────────────

    def _send_to_next_unvisited(self, env: 'DSREnvironment', agent_id: str, agent_type: str):
        """Send agent to nearest unvisited dark node. Search continues until full restoration."""
        if agent_type == 'scout':
            agent = env.scouts.get(agent_id)
        else:
            agent = env.rcs.get(agent_id)

        if not agent or agent.state != 'idle':
            return

        all_nodes = sorted(env.tgraph.nodes)
        zone = env.outage_zones if env.outage_zones else set(all_nodes)
        search_pool = [
            n for n in all_nodes
            if n in zone
            and n not in env.global_visited
            and n not in env.globally_claimed
        ]

        if not search_pool:
            return

        best_node, best_dist = None, float('inf')
        for node in search_pool:
            _, d = env.tgraph.shortest_path(agent.position, node)
            if 0 < d < best_dist:
                best_dist = d
                best_node = node

        if best_node:
            env.globally_claimed.add(best_node)
            if agent_type == 'scout':
                env.move_scout(agent_id, best_node)
            else:
                env.rc_searching.add(agent_id)
                env.move_rc(agent_id, best_node)

    def _try_auto_repair(self, env: 'DSREnvironment', rc: 'RepairCrew') -> bool:
        """Start repair if RC is already on a discovered active fault."""
        for dp in env.faults.values():
            if dp.discovered and dp.state == 'active' and env._rc_at_fault(rc, dp):
                currently = sum(1 for r in env.rcs.values() if r.repair_target == dp.id)
                if currently < dp.cap:
                    rc.start_repair(dp.id)
                    return True
        return False

    def _assign_rc_to_fault(self, env: 'DSREnvironment', rc: 'RepairCrew') -> str:
        """Send RC to the closest discovered active fault that still has capacity."""
        active = [dp for dp in env.faults.values() if dp.discovered and dp.state == 'active']

        rcs_per_fault = {}
        for other in env.rcs.values():
            if other.id == rc.id:
                continue
            if other.repair_target:
                rcs_per_fault[other.repair_target] = rcs_per_fault.get(other.repair_target, 0) + 1
            if other.resources > 0:
                for dp in active:
                    if env._rc_at_fault(other, dp):
                        rcs_per_fault[dp.id] = rcs_per_fault.get(dp.id, 0) + 1
            if other.target and not other.repair_target and other.state == 'moving' and other.resources > 0:
                for dp in active:
                    if dp.type == 'node' and other.target == dp.node:
                        rcs_per_fault[dp.id] = rcs_per_fault.get(dp.id, 0) + 1
                    elif dp.type == 'edge' and dp.edge and other.target in dp.edge:
                        rcs_per_fault[dp.id] = rcs_per_fault.get(dp.id, 0) + 1

        best_dp, best_dist = None, float('inf')
        for dp in active:
            if rcs_per_fault.get(dp.id, 0) >= dp.cap:
                continue
            if dp.type == 'node':
                fault_loc = dp.node
            elif dp.type == 'edge' and dp.edge:
                e0, e1 = dp.edge
                fault_loc = e1 if rc.position == e0 else e0
            else:
                fault_loc = None
            if fault_loc:
                _, d = env.tgraph.shortest_path(rc.position, fault_loc)
                if 0 < d < best_dist:
                    best_dist = d
                    best_dp = dp

        if best_dp:
            if best_dp.type == 'node':
                fault_loc = best_dp.node
            elif best_dp.type == 'edge' and best_dp.edge:
                e0, e1 = best_dp.edge
                fault_loc = e1 if rc.position == e0 else e0
            else:
                return None
            if fault_loc == rc.target:
                return None
            env.move_rc(rc.id, fault_loc)
            return best_dp.id

        return None

    def _assign_mps(self, env: 'DSREnvironment', mps: 'MPS', events: list):
        """Move MPS to the unpowered node that would restore the most loads."""
        other_mps = [m.position for m in env.mps.values()
                     if m.state == 'connected' and m.id != mps.id]
        grid_powered = env.egraph.get_powered_nodes(mps_sources=other_mps)

        best_node, best_score, best_dist = None, 0, float('inf')
        for node in env.tgraph.nodes:
            if node in grid_powered:
                continue
            score = env.egraph.count_loads_if_source(node)
            if score == 0:
                continue
            _, d = env.tgraph.shortest_path(mps.position, node)
            if d < 0:
                continue
            if score > best_score or (score == best_score and d < best_dist):
                best_score = score
                best_dist  = d
                best_node  = node

        if best_node and best_node != mps.position:
            path, dist = env.tgraph.shortest_path(mps.position, best_node)
            mps.move_to(path, dist)
            events.append(f'{mps.id} moving to {best_node} (restores {best_score} loads)')
        elif best_node == mps.position:
            sec = env._get_section_for_node(mps.position)
            if sec is None or env._section_safe_for_mps(sec):
                mps.connect()
                events.append(f'{mps.id} connected at {mps.position} — restoring power')
            else:
                events.append(f'{mps.id} standing by at {mps.position} — awaiting section clearance')
