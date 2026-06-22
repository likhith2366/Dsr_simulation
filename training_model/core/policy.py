"""
Decision-Making Policy
======================
Separated from the simulator (environment.py).

Interface — simulator passes a PolicyState (filtered view) to each callback:
  policy.on_setup(state, known)              # initial agent assignments
  policy.on_scout_arrived(state, sid, node)  # scout arrived at node
  policy.on_mps_arrived(state, mps, node)    # mps arrived at node
  policy.on_mps_idle(state, mps)             # mps standing by
  policy.on_fault_discovered(state)          # new fault found — redirect RCs
  policy.on_rc_idle(state, rc)               # RC has nothing to do

PolicyState exposes (reads):
  state.rcs, state.scouts, state.mps         — agent positions/states
  state.discovered_faults                    — only discovered faults
  state.dark_nodes                           — unpowered non-switch nodes
  state.loads                                — loads with P, Q demand
  state.switches                             — {switch_id: open|closed} only

Actions (writes via state.env):
  state.env.move_rc(rc_id, node)
  state.env.move_scout(scout_id, node)
  state.env.open_switch(switch_id)
  state.env.close_switch(switch_id)
  rc.start_repair(fault_id)
  mps.connect()
  mps.move_to(path, dist)
"""

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .environment import PolicyState
    from .agents import RepairCrew, MPS


def _agent_loc(a: dict) -> str:
    """Show exact in-transit position if moving, else just node."""
    if a.get('state') == 'moving':
        ex = a.get('exact', {})
        seg = ex.get('at', a['position'])
        km_left = ex.get('km_left', a.get('remaining_distance', 0))
        return f"{seg} ({km_left:.1f}km left -> {a.get('target','')})"
    return a['position']


def _print_agent(label, agents):
    print(f'  {label}:')
    for aid, a in agents.items():
        ex = a.get('exact', {})
        print(f'    [{aid}]')
        print(f'      position     : {a["position"]}')
        print(f'      state        : {a["state"]}')
        print(f'      target       : {a.get("target")}')
        if 'repair_target' in a:
            print(f'      repair_target: {a["repair_target"]}')
        if 'resources' in a:
            print(f'      resources    : {a["resources"]}')
        if 'energy' in a:
            print(f'      energy       : {a["energy"]} kWh')
        print(f'      km_left      : {a.get("remaining_distance", 0)}')
        print(f'      exact.at     : {ex.get("at", a["position"])}')
        print(f'      exact.km_done: {ex.get("km_done", 0)}')


def _print_state(label, state, extra=None):
    print(f'\nSIMULATOR -> POLICY  [{label}]  t={state.time}')
    if extra:
        for line in extra: print(f'  {line}')
    _print_agent('rcs',    state.rcs)
    _print_agent('scouts', state.scouts)
    _print_agent('mps',    state.mps)
    print(f'  switches: {state.switches}')
    print(f'  dark (load nodes) : {sorted(state.dark_load_nodes)}')
    print(f'  dark (topo only)  : {sorted(state.dark_topo_nodes)}')
    print(f'  faults  : {list(state.discovered_faults.keys())}')


def _print_actions(actions):
    print(f'POLICY -> SIMULATOR  [actions]')
    for a in actions: print(f'  {a}')
    if not actions: print('  (none)')


class GreedyPolicy:
    """
    Greedy nearest-neighbour policy (current baseline).
    Reads only from PolicyState. Actions via state.env.
    """

    # ── Initial assignments ─────────────────────────────────────────────

    def on_setup(self, state: 'PolicyState', known_faults: bool):
        env = state.env
        actions = []

        if known_faults:
            for dp in env.faults.values():
                dp.discovered = True
                dp.discovered_by = 'known'
                dp.discovered_at_step = 0
            for rid, rc in env.rcs.items():
                started = self._try_auto_repair(state, rc)
                if started:
                    actions.append(f'{rc.id}.start_repair({rc.repair_target!r})')
                else:
                    assigned = self._assign_rc_to_fault(state, rc)
                    if assigned:
                        actions.append(f'env.move_rc({rc.id!r}, fault={assigned})')
            for sid in state.scouts:
                self._send_to_next_unvisited(state, sid, 'scout', actions)
        else:
            # Check discovery at starting positions
            for rid, rc in env.rcs.items():
                env._check_discovery(rc.position, rid, 'RC')
            for sid in state.scouts:
                sc_pos = state.scouts[sid]['position']
                env._check_discovery(sc_pos, sid, 'Scout')

            # Assign scouts
            for sid in state.scouts:
                self._send_to_next_unvisited(state, sid, 'scout', actions)
            # Assign RCs
            for rid, rc in env.rcs.items():
                started = self._try_auto_repair(state, rc)
                if not started:
                    assigned = self._assign_rc_to_fault(state, rc)
                    if not assigned:
                        self._send_to_next_unvisited(state, rid, 'rc', actions)

        for mid, mps in env.mps.items():
            self._assign_mps(state, mps, actions)

        _print_state('on_setup', state, [f'known_faults={known_faults}'])
        _print_actions(actions)

    # ── Per-step callbacks ──────────────────────────────────────────────

    def on_scout_arrived(self, state: 'PolicyState', scout_id: str, node: str):
        actions = []
        self._send_to_next_unvisited(state, scout_id, 'scout', actions)
        _print_state('on_scout_arrived', state, [f'{scout_id} arrived at {node}'])
        _print_actions(actions)

    def on_mps_arrived(self, state: 'PolicyState', mps: 'MPS', node: str, events: list):
        env = state.env
        actions = []
        sec = env._get_section_for_node(node)
        if sec is None or env._section_safe_for_mps(sec):
            mps.connect()
            msg = f'{mps.id}.connect() at {node}'
            events.append(f'{mps.id} connected at {node} -- restoring power')
            actions.append(msg)
        else:
            events.append(f'{mps.id} standing by at {node} -- awaiting section clearance')
        _print_state('on_mps_arrived', state, [f'{mps.id} arrived at {node}'])
        _print_actions(actions)

    def on_mps_idle(self, state: 'PolicyState', mps: 'MPS', events: list):
        env = state.env
        actions = []
        sec = env._get_section_for_node(mps.position)
        other_sources = [m.position for m in env.mps.values()
                         if m.state == 'connected' and m.id != mps.id]
        grid_powered = env.egraph.get_powered_nodes(mps_sources=other_sources)
        if mps.position not in grid_powered and (sec is None or env._section_safe_for_mps(sec)):
            mps.connect()
            msg = f'{mps.id}.connect() at {mps.position}'
            events.append(f'{mps.id} connected at {mps.position} -- section cleared')
            actions.append(msg)
        else:
            self._assign_mps(state, mps, actions)
            events.extend(actions)
        _print_state('on_mps_idle', state, [f'{mps.id} pos={mps.position}'])
        _print_actions(actions)

    def on_fault_discovered(self, state: 'PolicyState', events: list):
        env = state.env
        actions = []
        for rc in env.rcs.values():
            if rc.state == 'moving':
                old_target = rc.target
                assigned = self._assign_rc_to_fault(state, rc)
                if assigned and rc.target != old_target:
                    if old_target and rc.id in env.rc_searching:
                        env.globally_claimed.discard(old_target)
                    env.rc_searching.discard(rc.id)
                    msg = f'env.move_rc({rc.id!r}, fault={assigned})'
                    events.append(f'{rc.id} redirected to fault {assigned}')
                    actions.append(msg)
        _print_state('on_fault_discovered', state)
        _print_actions(actions)

    def on_rc_idle(self, state: 'PolicyState', rc: 'RepairCrew', events: list):
        env = state.env
        actions = []
        repaired = False

        # Edge fault: RC at one endpoint → traverse to other end
        for dp in env.faults.values():
            if (dp.discovered and dp.state == 'active' and dp.type == 'edge'
                    and dp.edge and rc.position in dp.edge and rc.on_edge is None):
                other = dp.edge[1] if rc.position == dp.edge[0] else dp.edge[0]
                path, dist = env.tgraph.shortest_path(rc.position, other)
                if path:
                    rc.move_to(path, dist)
                    msg = f'{rc.id}.move_to({other!r})  [traverse fault edge]'
                    events.append(f'{rc.id} traversing fault edge to {other}')
                    actions.append(msg)
                    repaired = True
                break

        if not repaired:
            for dp in env.faults.values():
                if dp.discovered and dp.state == 'active' and env._rc_at_fault(rc, dp):
                    currently = sum(1 for r in env.rcs.values() if r.repair_target == dp.id)
                    if currently < dp.cap:
                        rc.start_repair(dp.id)
                        msg = f'{rc.id}.start_repair({dp.id!r})'
                        events.append(f'{rc.id} auto-started repair of {dp.id}')
                        actions.append(msg)
                        repaired = True
                        break

        if not repaired and rc.resources > 0:
            assigned = self._assign_rc_to_fault(state, rc)
            if assigned:
                env.rc_searching.discard(rc.id)
                msg = f'env.move_rc({rc.id!r}, {rc.target!r})'
                events.append(f'{rc.id} moving to discovered fault {assigned}')
                actions.append(msg)
            else:
                self._send_to_next_unvisited(state, rc.id, 'rc', actions)

        _print_state('on_rc_idle', state, [f'{rc.id}: pos={rc.position} repair_target={rc.repair_target}'])
        _print_actions(actions)

    # ── Internal helpers ────────────────────────────────────────────────

    def _send_to_next_unvisited(self, state: 'PolicyState', agent_id: str,
                                agent_type: str, actions: list = None):
        env = state.env
        if agent_type == 'scout':
            agent = env.scouts.get(agent_id)
        else:
            agent = env.rcs.get(agent_id)

        if not agent or agent.state != 'idle':
            return

        switch_nodes = {n for n, t in env.egraph.nodes.items() if t == 'SWITCH'}
        all_nodes = sorted(env.tgraph.nodes)
        zone = env.outage_zones if env.outage_zones else set(all_nodes)
        search_pool = [
            n for n in all_nodes
            if n in zone
            and n not in env.global_visited
            and n not in env.globally_claimed
            and n not in switch_nodes
        ]

        if not search_pool:
            return

        # Prefer load nodes (have demand) over pure topology nodes
        best_node, best_dist, best_score = None, float('inf'), -1
        for node in search_pool:
            _, d = env.tgraph.shortest_path(agent.position, node)
            if d <= 0:
                continue
            score = 1 if node in state.load_nodes else 0
            if score > best_score or (score == best_score and d < best_dist):
                best_score = score
                best_dist  = d
                best_node  = node

        if best_node:
            env.globally_claimed.add(best_node)
            if agent_type == 'scout':
                env.move_scout(agent_id, best_node)
                if actions is not None:
                    actions.append(f'env.move_scout({agent_id!r}, {best_node!r})')
            else:
                env.rc_searching.add(agent_id)
                env.move_rc(agent_id, best_node)
                if actions is not None:
                    actions.append(f'env.move_rc({agent_id!r}, {best_node!r})')

    def _try_auto_repair(self, state: 'PolicyState', rc: 'RepairCrew') -> bool:
        env = state.env
        for dp in env.faults.values():
            if dp.discovered and dp.state == 'active' and env._rc_at_fault(rc, dp):
                currently = sum(1 for r in env.rcs.values() if r.repair_target == dp.id)
                if currently < dp.cap:
                    rc.start_repair(dp.id)
                    return True
        return False

    def _assign_rc_to_fault(self, state: 'PolicyState', rc: 'RepairCrew') -> str:
        env = state.env
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

    def _assign_mps(self, state: 'PolicyState', mps: 'MPS', actions: list):
        env = state.env
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
            actions.append(f'{mps.id}.move_to({best_node!r})  [restores {best_score} loads]')
        elif best_node == mps.position:
            sec = env._get_section_for_node(mps.position)
            if sec is None or env._section_safe_for_mps(sec):
                mps.connect()
                actions.append(f'{mps.id}.connect() at {mps.position}')
            else:
                actions.append(f'{mps.id} standing by at {mps.position}')
