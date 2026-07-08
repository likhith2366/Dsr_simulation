"""
Manual / Interactive DSR Simulator
====================================
YOU are the policy. The simulator asks you what to do at every decision point.

Run:
    cd a:\dsr_simulator_standalone
    python training_model/manual_sim.py
    python training_model/manual_sim.py --case Case2
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training_model.core.environment import DSREnvironment, PolicyState
from training_model.core.agents import RepairCrew, MPS
from training_model.config.ieee13new_cases import IEEE13NewCases, IEEE13NewNetwork


# ─────────────────────────────────────────────────
# Terminal helpers
# ─────────────────────────────────────────────────

SEP  = '-' * 60
SEP2 = '=' * 60

def hdr(title):
    print(f'\n{SEP2}')
    print(f'  {title}')
    print(SEP2)

def section(title):
    print(f'\n  {SEP[:40]}')
    print(f'  {title}')
    print(f'  {SEP[:40]}')

def ask(prompt, valid=None, allow_skip=True):
    """Prompt the user. Returns stripped input. Empty = skip (if allow_skip)."""
    hint = ''
    if valid:
        hint = f'  [{"/".join(valid)}]'
    while True:
        try:
            ans = input(f'  > {prompt}{hint}: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\n\n  [Interrupted — goodbye]')
            sys.exit(0)
        if allow_skip and ans == '':
            return None
        if valid and ans not in valid:
            print(f'    Invalid — choose from: {", ".join(valid)}')
            continue
        return ans


# ─────────────────────────────────────────────────
# Print current state (what the simulator tells you)
# ─────────────────────────────────────────────────

def print_state(state: PolicyState, trigger: str, extra: str = ''):
    hdr(f'SIMULATOR -> YOU   [{trigger}]   t = {state.time} h')
    if extra:
        print(f'  {extra}')

    # Agents
    section('AGENTS')
    for aid, a in state.rcs.items():
        ex   = a.get('exact', {})
        loc  = ex.get('at', a['position'])
        left = a.get('remaining_distance', 0)
        tgt  = a.get('target', '—')
        st   = a['state']
        rep  = a.get('repair_target')
        line = f'  {aid:6s}  pos={a["position"]:5s}  state={st}'
        if st == 'moving':
            line += f'  →{tgt}  ({left:.1f}km left, at {loc})'
        if rep:
            line += f'  REPAIRING={rep}'
        print(line)

    for sid, s in state.scouts.items():
        ex   = s.get('exact', {})
        loc  = ex.get('at', s['position'])
        left = s.get('remaining_distance', 0)
        tgt  = s.get('target', '—')
        st   = s['state']
        line = f'  {sid:8s}  pos={s["position"]:5s}  state={st}'
        if st == 'moving':
            line += f'  →{tgt}  ({left:.1f}km left, at {loc})'
        print(line)

    for mid, m in state.mps.items():
        ex   = m.get('exact', {})
        loc  = ex.get('at', m['position'])
        left = m.get('remaining_distance', 0)
        tgt  = m.get('target', '—')
        st   = m['state']
        nrg  = m.get('energy', 0)
        line = f'  {mid:6s}  pos={m["position"]:5s}  state={st}  energy={nrg:.0f}kWh'
        if st == 'moving':
            line += f'  →{tgt}  ({left:.1f}km left, at {loc})'
        print(line)

    # Discovered faults
    section('KNOWN FAULTS')
    if state.discovered_faults:
        for fid, f in state.discovered_faults.items():
            prog = f.get('progress', 0)
            print(f'  {fid}  @ {f["location"]}  state={f["state"]}  progress={prog:.0f}%')
    else:
        print('  (none discovered yet - send scouts to find them)')

    # Dark nodes
    section('DARK NODES (no power)')
    print(f'  Load nodes (customers dark) : {sorted(state.dark_load_nodes) or "none"}')
    print(f'  Topo nodes (junctions dark) : {sorted(state.dark_topo_nodes) or "none"}')

    # Loads
    section('LOADS')
    on_count  = sum(1 for l in state.loads.values() if l['state'] == 'on')
    off_count = sum(1 for l in state.loads.values() if l['state'] == 'off')
    print(f'  ON: {on_count}   OFF: {off_count}   Total: {len(state.loads)}')
    for lid, l in sorted(state.loads.items()):
        sym = 'ON ' if l['state'] == 'on' else 'OFF'
        print(f'    {sym} {lid:8s}  node={l["node"]:5s}  P={l["P"]:4d}kW  W={l["W"]}')

    # Switches
    section('SWITCHES')
    for sw, st in sorted(state.switches.items()):
        sym = '[X]' if st == 'closed' else '[ ]'
        print(f'  {sym} {sw} = {st}')

    # Visited / claimed
    section('SEARCH PROGRESS')
    print(f'  Visited : {sorted(state.global_visited)}')
    print(f'  Claimed : {sorted(state.globally_claimed)}')


# ─────────────────────────────────────────────────
# Ask human for commands
# ─────────────────────────────────────────────────

def ask_rc_actions(state: PolicyState, env: DSREnvironment):
    """Ask the human what to do with each RC."""
    actions = []
    print('\n  ── REPAIR CREW COMMANDS ────────────────────────')
    for rid, rc_data in state.rcs.items():
        rc  = env.rcs[rid]
        st  = rc_data['state']
        pos = rc_data['position']

        # If already repairing, show progress and skip
        if st == 'repairing':
            rep = rc_data.get('repair_target')
            print(f'\n  {rid} is REPAIRING {rep} at {pos} — no input needed')
            continue

        # If moving, offer option to redirect or leave alone
        if st == 'moving':
            tgt  = rc_data.get('target', '?')
            left = rc_data.get('remaining_distance', 0)
            print(f'\n  {rid} is moving → {tgt} ({left:.1f}km left)')
            redirect = ask(f'Redirect {rid}? Enter new node or press Enter to leave as-is')
            if redirect:
                result = env.move_rc(rid, redirect)
                if result['status'] == 'ok':
                    actions.append(f'move_rc({rid}, {redirect})')
                    print(f'    ✓ {rid} redirected → {redirect}')
                else:
                    print(f'    ✗ Error: {result["msg"]}')
            continue

        # RC is idle — ask what to do
        print(f'\n  {rid} is IDLE at {pos}')

        # Show nearby discovered faults
        discovered = list(state.discovered_faults.keys())
        if discovered:
            print(f'    Known faults: {discovered}')

        print(f'    Options:')
        print(f'      • Type a node name to move there (e.g. N3, N10, V2)')
        print(f'      • Type a fault ID to repair it (e.g. DP1, DP2) — only if RC is at the fault node')
        print(f'      • Press Enter to skip (RC stays idle)')

        cmd = ask(f'Command for {rid}')
        if cmd is None:
            print(f'    {rid} stays idle')
            continue

        # Check if it's a fault repair command
        if cmd in env.faults and env.faults[cmd].discovered:
            dp = env.faults[cmd]
            if env._rc_at_fault(rc, dp):
                rc.start_repair(cmd)
                actions.append(f'{rid}.start_repair({cmd})')
                print(f'    ✓ {rid} started repair of {cmd}')
            else:
                print(f'    ✗ {rid} is not at fault location — move there first')
        else:
            # Treat as a node move
            result = env.move_rc(rid, cmd)
            if result['status'] == 'ok':
                dist = result['distance']
                actions.append(f'move_rc({rid}, {cmd})')
                print(f'    ✓ {rid} → {cmd}  ({dist:.1f}km)')
            else:
                print(f'    ✗ Error: {result["msg"]}')

    return actions


def ask_scout_actions(state: PolicyState, env: DSREnvironment):
    """Ask the human what to do with each Scout."""
    actions = []
    print('\n  ── SCOUT COMMANDS ──────────────────────────────')
    for sid, sc_data in state.scouts.items():
        st  = sc_data['state']
        pos = sc_data['position']

        if st == 'moving':
            tgt  = sc_data.get('target', '?')
            left = sc_data.get('remaining_distance', 0)
            print(f'\n  {sid} is moving → {tgt} ({left:.1f}km left)')
            redirect = ask(f'Redirect {sid}? Enter new node or press Enter to leave as-is')
            if redirect:
                result = env.move_scout(sid, redirect)
                if result['status'] == 'ok':
                    actions.append(f'move_scout({sid}, {redirect})')
                    print(f'    ✓ {sid} redirected → {redirect}')
                else:
                    print(f'    ✗ Error: {result["msg"]}')
            continue

        print(f'\n  {sid} is IDLE at {pos}')
        unvisited = sorted(n for n in env.tgraph.nodes
                           if n not in state.global_visited
                           and env.egraph.nodes.get(n) != 'SWITCH')
        if unvisited:
            print(f'    Unvisited nodes: {unvisited}')
        cmd = ask(f'Send {sid} to node')
        if cmd:
            result = env.move_scout(sid, cmd)
            if result['status'] == 'ok':
                dist = result['distance']
                actions.append(f'move_scout({sid}, {cmd})')
                print(f'    ✓ {sid} → {cmd}  ({dist:.1f}km)')
            else:
                print(f'    ✗ Error: {result["msg"]}')
        else:
            print(f'    {sid} stays idle')

    return actions


def ask_mps_actions(state: PolicyState, env: DSREnvironment):
    """Ask the human what to do with each MPS."""
    actions = []
    if not env.mps:
        return actions
    print('\n  ── MPS COMMANDS ────────────────────────────────')
    for mid, mp_data in state.mps.items():
        mps = env.mps[mid]
        st  = mp_data['state']
        pos = mp_data['position']
        nrg = mp_data.get('energy', 0)

        if st == 'connected':
            print(f'\n  {mid} is CONNECTED at {pos} (energy={nrg:.0f}kWh)')
            disc = ask(f'Disconnect {mid}? (y/n)', valid=['y', 'n'])
            if disc == 'y':
                mps.disconnect()
                actions.append(f'{mid}.disconnect()')
                print(f'    ✓ {mid} disconnected')
            continue

        if st == 'moving':
            tgt  = mp_data.get('target', '?')
            left = mp_data.get('remaining_distance', 0)
            print(f'\n  {mid} is moving → {tgt} ({left:.1f}km left)')
            # No redirect for MPS in this version — just show status
            print(f'    (leave it moving — it will ask again when it arrives)')
            continue

        print(f'\n  {mid} is IDLE at {pos} (energy={nrg:.0f}kWh)')
        print(f'    Options:')
        print(f'      • Type "connect" to connect MPS here')
        print(f'      • Type a node name to move MPS there')
        print(f'      • Press Enter to leave idle')
        cmd = ask(f'Command for {mid}')
        if cmd == 'connect':
            sec = env._get_section_for_node(pos)
            if sec and not env._section_safe_for_mps(sec):
                print(f'    ✗ Section {sec} not clear — faults still active or unvisited')
            else:
                mps.connect()
                actions.append(f'{mid}.connect()')
                print(f'    ✓ {mid} connected at {pos}')
        elif cmd:
            path, dist = env.tgraph.shortest_path(pos, cmd)
            if path:
                mps.move_to(path, dist)
                actions.append(f'{mid}.move_to({cmd})')
                print(f'    ✓ {mid} → {cmd}  ({dist:.1f}km)')
            else:
                print(f'    ✗ No path to {cmd}')
        else:
            print(f'    {mid} stays idle')

    return actions


# ─────────────────────────────────────────────────
# Manual Policy class — plugs into the simulator
# ─────────────────────────────────────────────────

class ManualPolicy:
    """Human-driven policy. Every callback prints state and asks for input."""

    def on_setup(self, state: PolicyState, known_faults: bool):
        state_ = state
        env    = state.env
        print_state(state, 'on_setup', f'known_faults={known_faults}')
        print('\n  Initial setup - assign all agents:')
        all_actions = []
        all_actions += ask_scout_actions(state_, env)
        all_actions += ask_rc_actions(state_, env)
        all_actions += ask_mps_actions(state_, env)
        _show_actions(all_actions)

    def on_scout_arrived(self, state: PolicyState, scout_id: str, node: str):
        env = state.env
        print_state(state, 'on_scout_arrived', f'{scout_id} arrived at {node}')
        actions = ask_scout_actions(state, env)
        _show_actions(actions)

    def on_mps_arrived(self, state: PolicyState, mps: MPS, node: str, events: list):
        env = state.env
        print_state(state, 'on_mps_arrived', f'{mps.id} arrived at {node}')
        actions = ask_mps_actions(state, env)
        _show_actions(actions)

    def on_mps_idle(self, state: PolicyState, mps: MPS, events: list):
        env = state.env
        print_state(state, 'on_mps_idle', f'{mps.id} idle at {mps.position}')
        actions = ask_mps_actions(state, env)
        _show_actions(actions)

    def on_fault_discovered(self, state: PolicyState, events: list):
        # Only prompt if there are newly discovered faults and idle/moving RCs to redirect
        env = state.env
        has_new = any(dp.discovered and dp.state == 'active'
                      for dp in env.faults.values())
        moving_rcs = [rc for rc in env.rcs.values() if rc.state == 'moving']
        if has_new and moving_rcs:
            print_state(state, 'on_fault_discovered')
            print('\n  A fault was just discovered — you can redirect moving RCs:')
            actions = ask_rc_actions(state, env)
            _show_actions(actions)

    def on_rc_idle(self, state: PolicyState, rc: RepairCrew, events: list):
        env = state.env
        print_state(state, 'on_rc_idle', f'{rc.id} idle at {rc.position}')
        actions = ask_rc_actions(state, env)
        _show_actions(actions)


def _show_actions(actions):
    print(f'\n  YOU → SIMULATOR  [commands sent]')
    if actions:
        for a in actions:
            print(f'    {a}')
    else:
        print('    (none)')


# ─────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Interactive DSR Simulator — you are the policy')
    parser.add_argument('--case', default='Case1',
                        choices=IEEE13NewCases.all_cases(),
                        help='Which case to run (default: Case1)')
    parser.add_argument('--scouts', type=int, default=1,
                        help='Number of scouts (default: 1)')
    args = parser.parse_args()

    hdr(f'DSR Manual Simulator -- {args.case}')
    print(f'  You are the policy. The simulator tells you what is happening')
    print(f'  and ask what to do. Press Enter to skip / leave an agent as-is.')
    print(f'  Ctrl+C to quit at any time.')

    env = DSREnvironment(policy=ManualPolicy())
    env.setup(args.case, num_scouts=args.scouts, known_faults=False,
              network_cls=IEEE13NewNetwork, cases_cls=IEEE13NewCases)

    print(f'\n  Simulation running... (max 50 steps)')
    for step in range(50):
        input(f'\n  [Press Enter to advance to t = {env.time + 1}h]')

        result = env.step()

        # Print events from this step
        if result['events']:
            print(f'\n  ── Events at t={result["time"]}h ──────────────────')
            for ev in result['events']:
                print(f'    • {ev}')

        reward = result['reward']
        max_rew = sum(l.W * l.P for l in env.loads.values())
        print(f'\n  Reward: {reward:.0f} / {max_rew:.0f}   '
              f'Loads ON: {sum(1 for l in env.loads.values() if l.state=="on")}/{len(env.loads)}')

        if result['done']:
            hdr(f'ALL FAULTS REPAIRED at t = {result["time"]}h')
            print(f'  Final reward: {reward:.0f} / {max_rew:.0f}')
            print(f'\n  Fault timeline:')
            for dp in env.faults.values():
                d = f't={dp.discovered_at_step}h' if dp.discovered_at_step is not None else '—'
                r = f't={dp.repaired_at_step}h'   if dp.repaired_at_step   is not None else '—'
                print(f'    {dp.id}  discovered={d}  repaired={r}  by={dp.discovered_by or "none"}')
            break
    else:
        hdr('Max steps reached — simulation ended')
        print(f'  Final reward: {env.get_reward():.0f}')


if __name__ == '__main__':
    main()
