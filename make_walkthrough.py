"""
Generate simulation_walkthrough.md with detailed per-step state.

Captures for every step:
  - Fault states (position, level/demand, progress, discovered/repaired)
  - RC states (position, speed, resources, action, target)
  - MPS states (position, speed, energy, p_limit, connection)
  - Section / breaker states (which switches open or closed)
  - Loads ON/OFF (V nodes included — V2 has a load)
  - Outage zones (which nodes have no power)
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from training_model.core.environment import DSREnvironment
from training_model.config.ieee13new_cases import IEEE13NewCases, IEEE13NewNetwork

MAX_STEPS = 50
OUT_PATH  = os.path.join(os.path.dirname(__file__), 'simulation_walkthrough.md')


def fmt_fault(dp):
    loc = dp.node if dp.type == 'node' else f"{dp.edge[0]}–{dp.edge[1]}"
    if dp.state == 'repaired':
        status = 'REPAIRED'
    elif dp.discovered:
        status = f'DISCOVERED  (progress {dp.progress:.0f}/{dp.demand:.0f})'
    else:
        status = 'HIDDEN'
    return f"  - **{dp.id}** at `{loc}` ({dp.type})  ·  level {dp.demand:.0f}  ·  cap {dp.cap}  ·  {status}"


def fmt_rc(rc):
    act = rc.state
    detail = ''
    if rc.state == 'moving' and rc.target:
        detail = f" → `{rc.target}` ({rc.remaining_distance:.1f}km left)"
    elif rc.state == 'repairing' and rc.repair_target:
        detail = f" on `{rc.repair_target}`"
    return (f"  - **{rc.id}** @ `{rc.position}`  ·  speed {rc.speed}km/h  ·  "
            f"resources {rc.resources:.1f}  ·  {act}{detail}")


def fmt_scout(s):
    detail = ''
    if s.state == 'moving' and s.target:
        detail = f" → `{s.target}` ({s.remaining_distance:.1f}km left)"
    return (f"  - **{s.id}** @ `{s.position}`  ·  speed {s.speed}km/h  ·  "
            f"{s.state}{detail}")


def fmt_mps(m):
    detail = ''
    if m.state == 'moving' and m.target:
        detail = f" → `{m.target}` ({m.remaining_distance:.1f}km left)"
    elif m.state == 'connected':
        detail = ' (feeding power)'
    return (f"  - **{m.id}** @ `{m.position}`  ·  speed {m.speed}km/h  ·  "
            f"limit {m.p_limit}kW  ·  energy {m.energy:.0f}kWh  ·  {m.state}{detail}")


def fmt_switches(env):
    """Return dict {switch_id: state} based on EGraph edge states."""
    switches = {}
    for sid in [n for n, t in env.network.NODES.items() if t == 'SWITCH']:
        sw_edges = env.network.SWITCHES.get(sid, {}).get('edges', [])
        states = [env.egraph.edges[e]['state'] for e in sw_edges if e in env.egraph.edges]
        if 'faulted' in states:
            switches[sid] = 'FAULTED'
        elif 'open' in states:
            switches[sid] = 'OPEN'
        else:
            switches[sid] = 'CLOSED'
    return switches


def fmt_section_status(env):
    """Return list of (section_name, status, dark_nodes)."""
    powered = env.egraph.get_powered_nodes(
        mps_sources=[m.position for m in env.mps.values() if m.state == 'connected']
    )
    out = []
    for name, sec in env.network.SECTIONS.items():
        nodes = sec['nodes']
        dark = [n for n in nodes if n not in powered]
        status = 'LIVE' if not dark else ('PARTIAL' if dark != list(nodes) else 'DARK')
        out.append((name, status, dark))
    return out


def write_state(buf, env, header):
    buf.append(f"### {header}\n")
    # totals
    loads_on = sum(1 for l in env.loads.values() if l.state == 'on')
    loads_tot = len(env.loads)
    buf.append(f"- Loads ON: **{loads_on}/{loads_tot}**  ·  Reward: **{env.get_reward():.0f}** / "
               f"{sum(l.W * l.P for l in env.loads.values()):.0f}")
    # faults
    buf.append("\n**Faults**")
    for dp in env.faults.values():
        buf.append(fmt_fault(dp))
    # RCs
    buf.append("\n**Repair Crews**")
    for rc in env.rcs.values():
        buf.append(fmt_rc(rc))
    # Scouts
    buf.append("\n**Scouts**")
    for s in env.scouts.values():
        buf.append(fmt_scout(s))
    # MPSs
    buf.append("\n**Mobile Power Sources**")
    for m in env.mps.values():
        buf.append(fmt_mps(m))
    # Switches
    buf.append("\n**Switches / Breakers**")
    sw_states = fmt_switches(env)
    closed = [s for s, st in sw_states.items() if st == 'CLOSED']
    open_  = [s for s, st in sw_states.items() if st == 'OPEN']
    faulted = [s for s, st in sw_states.items() if st == 'FAULTED']
    buf.append(f"  - CLOSED: {', '.join(sorted(closed)) if closed else '—'}")
    buf.append(f"  - OPEN  : {', '.join(sorted(open_))  if open_  else '—'}")
    if faulted:
        buf.append(f"  - FAULTED: {', '.join(sorted(faulted))}")
    # Sections
    buf.append("\n**Sections**")
    for name, status, dark in fmt_section_status(env):
        tag = {'LIVE':'✓','PARTIAL':'⚠','DARK':'✗'}[status]
        dark_str = f" — dark nodes: `{', '.join(sorted(dark))}`" if dark else ''
        buf.append(f"  - Section {name}: {tag} **{status}**{dark_str}")
    buf.append("")


def run_case(case_name: str, buf: list):
    env = DSREnvironment()
    env.setup(case_name, num_scouts=1, known_faults=False,
              network_cls=IEEE13NewNetwork, cases_cls=IEEE13NewCases)

    buf.append(f"\n---\n\n## {case_name}\n")
    cdata = IEEE13NewCases.get(case_name)
    buf.append(f"**Scenario:** {len(cdata['faults'])} hidden faults  ·  "
               f"{len(cdata['repair_crews'])} RC  ·  "
               f"{len(cdata.get('mobile_power', {}))} MPS  ·  1 Scout\n")

    write_state(buf, env, f"Initial State  (t = 0 h)")

    # Run steps
    for _ in range(MAX_STEPS):
        result = env.step()
        events = result['events']
        buf.append(f"\n#### Step {result['time']}  (t = {result['time']} h)\n")
        if events:
            buf.append("**Events**")
            for ev in events:
                buf.append(f"  - {ev}")
            buf.append("")
        write_state(buf, env, f"State after step {result['time']}")
        if result['done']:
            buf.append(f"\n**All faults repaired at step {result['time']}.**")
            break


def main():
    cases = IEEE13NewCases.all_cases()
    buf = []
    buf.append("# Simulation Walkthrough — IEEE-13 New Network\n")
    buf.append("Detailed per-step state for all 5 cases under **UNKNOWN-fault** mode "
               "(Scout searches, RCs repair). Each step records:\n")
    buf.append("- Fault positions, levels (demand), and status (hidden / discovered / repaired)")
    buf.append("- RC and Scout positions, speed, remaining resources, current action")
    buf.append("- MPS position, speed, limit, remaining energy, connection state")
    buf.append("- Switch / breaker states (CLOSED / OPEN / FAULTED)")
    buf.append("- Section status (LIVE / PARTIAL / DARK with dark-node list)")
    buf.append("- Loads ON/OFF count (V2 has a load — V-tie nodes can carry load)\n")
    buf.append("> Note: in the newest network, V-nodes can have loads. V2 has `L_V2` (120 kW, weight 8). "
               "V1, V3, V4 are tie nodes without loads.\n")

    for case in cases:
        run_case(case, buf)

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(buf) + '\n')
    print(f"Wrote {OUT_PATH}")


if __name__ == '__main__':
    main()
