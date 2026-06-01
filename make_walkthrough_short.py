"""
Generate simulation_walkthrough_short.md — compact one-table-per-step format.

Each step = one small markdown table covering faults, RCs, Scout, MPS, switches, sections.
Goal: scannable in seconds. ~50–80 lines per case instead of 500+.
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from training_model.core.environment import DSREnvironment
from training_model.config.ieee13new_cases import IEEE13NewCases, IEEE13NewNetwork

MAX_STEPS = 50
OUT_PATH  = os.path.join(os.path.dirname(__file__), 'simulation_walkthrough_short.md')


def fault_short(dp):
    loc = dp.node if dp.type == 'node' else f"{dp.edge[0]}-{dp.edge[1]}"
    if dp.state == 'repaired':
        tag = '✓ repaired'
    elif dp.discovered:
        tag = f'⚡ {dp.progress:.0f}/{dp.demand:.0f}'
    else:
        tag = '? hidden'
    return f"{dp.id}@{loc} lv{dp.demand:.0f} {tag}"


def rc_short(rc):
    if rc.state == 'moving':
        act = f"→{rc.target}({rc.remaining_distance:.0f}km)"
    elif rc.state == 'repairing':
        act = f"REPAIR {rc.repair_target}"
    else:
        act = 'idle'
    return f"{rc.id}@{rc.position} v{rc.speed} r{rc.resources:.0f} {act}"


def scout_short(s):
    if s.state == 'moving':
        act = f"→{s.target}"
    else:
        act = 'idle'
    return f"{s.id}@{s.position} v{s.speed:.0f} {act}"


def mps_short(m):
    if m.state == 'moving':
        act = f"→{m.target}"
    elif m.state == 'connected':
        act = 'CONNECTED'
    else:
        act = 'idle'
    return f"{m.id}@{m.position} {m.p_limit}kW e{m.energy:.0f} {act}"


def switch_states(env):
    closed, open_, faulted = [], [], []
    for sid in [n for n, t in env.network.NODES.items() if t == 'SWITCH']:
        sw_edges = env.network.SWITCHES.get(sid, {}).get('edges', [])
        states = [env.egraph.edges[e]['state'] for e in sw_edges if e in env.egraph.edges]
        if 'faulted' in states:
            faulted.append(sid)
        elif 'open' in states:
            open_.append(sid)
        else:
            closed.append(sid)
    return sorted(closed), sorted(open_), sorted(faulted)


def section_summary(env):
    powered = env.egraph.get_powered_nodes(
        mps_sources=[m.position for m in env.mps.values() if m.state == 'connected']
    )
    out = []
    for name, sec in env.network.SECTIONS.items():
        nodes = sec['nodes']
        dark = sorted(n for n in nodes if n not in powered)
        if not dark:
            out.append(f"{name}=LIVE")
        elif len(dark) == len(nodes):
            out.append(f"{name}=DARK[{','.join(dark)}]")
        else:
            out.append(f"{name}=PARTIAL[{','.join(dark)}]")
    return ' · '.join(out)


def step_block(env, header, events=None):
    out = [f"#### {header}"]
    if events:
        out.append("> " + '; '.join(events))
    loads_on = sum(1 for l in env.loads.values() if l.state == 'on')
    closed, open_, faulted = switch_states(env)
    sw_line = f"closed: {','.join(closed) or '—'}  ·  open: {','.join(open_) or '—'}"
    if faulted:
        sw_line += f"  ·  **faulted: {','.join(faulted)}**"

    out.append("")
    out.append("| | |")
    out.append("|---|---|")
    out.append(f"| Loads     | {loads_on}/{len(env.loads)} on · reward {env.get_reward():.0f} |")
    out.append(f"| Faults    | {' · '.join(fault_short(d) for d in env.faults.values())} |")
    out.append(f"| RC        | {' · '.join(rc_short(r) for r in env.rcs.values())} |")
    out.append(f"| Scout     | {' · '.join(scout_short(s) for s in env.scouts.values())} |")
    if env.mps:
        out.append(f"| MPS       | {' · '.join(mps_short(m) for m in env.mps.values())} |")
    out.append(f"| Switches  | {sw_line} |")
    out.append(f"| Sections  | {section_summary(env)} |")
    out.append("")
    return out


def run_case(case_name: str, buf: list):
    env = DSREnvironment()
    env.setup(case_name, num_scouts=1, known_faults=False,
              network_cls=IEEE13NewNetwork, cases_cls=IEEE13NewCases)

    cdata = IEEE13NewCases.get(case_name)
    buf.append(f"\n---\n\n## {case_name}")
    buf.append(f"_{len(cdata['faults'])} hidden faults · {len(cdata['repair_crews'])} RC · "
               f"{len(cdata.get('mobile_power', {}))} MPS · 1 Scout_\n")

    buf.extend(step_block(env, "Initial (t=0h)"))

    final_t = 0
    for _ in range(MAX_STEPS):
        result = env.step()
        final_t = result['time']
        buf.extend(step_block(env, f"Step {final_t} (t={final_t}h)",
                              events=result['events']))
        if result['done']:
            buf.append(f"**✓ All faults repaired at t={final_t}h.**\n")
            break


def main():
    buf = []
    buf.append("# Simulation Walkthrough — Short Version\n")
    buf.append("One compact table per step. Same data as the detailed walkthrough, "
               "but scannable in seconds.\n")
    buf.append("**Legend**")
    buf.append("- **Faults** — `ID@location` `lv`demand · `?`hidden / `⚡`progress / `✓`repaired")
    buf.append("- **RC** — `ID@pos` `v`speed `r`resources · action")
    buf.append("- **MPS** — `ID@pos` kW-limit `e`nergy-kWh · state")
    buf.append("- **Sections** — LIVE / PARTIAL[dark nodes] / DARK[all nodes]\n")
    buf.append("> V-tie nodes can carry load. V2 has `L_V2` (120 kW, weight 8). "
               "V1, V3, V4 are tie-only.\n")

    for case in IEEE13NewCases.all_cases():
        run_case(case, buf)

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(buf) + '\n')

    # report line count
    with open(OUT_PATH, encoding='utf-8') as f:
        n = sum(1 for _ in f)
    print(f"Wrote {OUT_PATH}  ({n} lines)")


if __name__ == '__main__':
    main()
