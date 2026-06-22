"""
Run 5 IEEE-13 Cases with Unknown Fault Discovery
=================================================
Runs each case, scouts discover faults, RCs repair.
Saves a network graph image for each case.

Run:
    cd a:\dsr_simulator_standalone
    python training_model/run_cases.py
"""

import os
import sys
import argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training_model.core.environment import DSREnvironment
from training_model.visualizer import draw_network
from training_model.config.ieee13new_cases import IEEE13NewCases, IEEE13NewNetwork

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_STEPS = 50

# Set at runtime via --network flag
_NETWORK_CLS = None
_CASES_CLS   = None


def run_case(case_name: str, known_faults: bool = False, raw: bool = False):
    mode = 'KNOWN faults' if known_faults else 'UNKNOWN faults'
    print(f"\n{'='*60}")
    print(f"  Case: {case_name}  [{mode}]")
    print(f"{'='*60}")

    env = DSREnvironment()
    env._raw_mode = raw
    env.setup(case_name, num_scouts=1, known_faults=known_faults,
              network_cls=_NETWORK_CLS, cases_cls=_CASES_CLS)

    # Print initial state
    state = env.get_state()
    print(f"\n  Initial:")
    print(f"    Loads ON : {sum(1 for l in env.loads.values() if l.state=='on')}/{len(env.loads)}")
    print(f"    Reward   : {env.get_reward():.0f}")
    print(f"    Faults   : {len(env.faults)} hidden")
    for rc in env.rcs.values():
        print(f"    {rc.id} @ {rc.position}")
    for s in env.scouts.values():
        print(f"    {s.id} @ {s.position}")
    for m in env.mps.values():
        print(f"    {m.id} @ {m.position} (energy={m.energy:.0f}kWh)")

    # Save initial graph
    draw_network(env,
                 title=f'{case_name} — Initial State (faults hidden)',
                 save_path=os.path.join(OUTPUT_DIR, f'{case_name}_step0.png'),
                 show=False)

    # Simulation loop
    for _ in range(MAX_STEPS):
        result = env.step()

        # Print events
        for event in result['events']:
            print(f"  [t={result['time']:02d}] {event}")

        # Save graph every step
        draw_network(env,
                     title=f'{case_name} — Step {result["time"]}',
                     save_path=os.path.join(OUTPUT_DIR, f'{case_name}_step{result["time"]:02d}.png'),
                     show=False)

        if result['done']:
            print(f"\n  All faults repaired at step {result['time']}!")
            break

    # Final graph
    draw_network(env,
                 title=f'{case_name} — Final (step {env.time})',
                 save_path=os.path.join(OUTPUT_DIR, f'{case_name}_final.png'),
                 show=False)

    # Summary
    max_reward = sum(l.W * l.P for l in env.loads.values())
    print(f"\n  Summary:")
    print(f"    Total time   : {env.time} hours")
    print(f"    Final reward : {env.get_reward():.0f} / {max_reward:.0f} W*P")
    print(f"    Loads ON     : {sum(1 for l in env.loads.values() if l.state=='on')}/{len(env.loads)}")

    print(f"\n  Fault Timeline:")
    for dp in env.faults.values():
        disc_t   = f"t={dp.discovered_at_step}h" if dp.discovered_at_step is not None else "NOT FOUND"
        repair_t = f"t={dp.repaired_at_step}h"   if dp.repaired_at_step   is not None else "NOT REPAIRED"
        lag      = ((dp.repaired_at_step or 0) - (dp.discovered_at_step or 0)) if dp.discovered_at_step is not None else '-'
        print(f"    {dp.id:4s}: discovered={disc_t:8s}  repaired={repair_t:8s}  "
              f"repair_lag={lag}h  by={dp.discovered_by or 'none'}")

    print(f"\n  Agent Stats:")
    for rc in env.rcs.values():
        s = rc.stats
        print(f"    {rc.id}: {s['total_km']:.1f}km traveled | "
              f"{s['hours_moving']}h moving | "
              f"{s['hours_repairing']}h repairing | "
              f"{s['hours_idle']}h idle | "
              f"repaired={s['faults_repaired']}")

    for scout in env.scouts.values():
        s = scout.stats
        print(f"    {scout.id}: {s['total_km']:.1f}km traveled | "
              f"{s['hours_moving']}h moving | "
              f"{s['hours_idle']}h idle | "
              f"{s['nodes_visited']} nodes visited | "
              f"found={len(s['discovery_log'])} faults")

    for mps in env.mps.values():
        s = mps.stats
        print(f"    {mps.id}: {s['total_km']:.1f}km traveled | "
              f"{s['hours_moving']}h moving | "
              f"{s['hours_connected']}h connected | "
              f"{s['hours_idle']}h idle | "
              f"energy left={mps.energy:.0f}kWh")

    return {
        'case':   case_name,
        'steps':  env.time,
        'reward': env.get_reward(),
        'done':   env.is_done(),
        'mode':   'known' if known_faults else 'unknown'
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--network', choices=['old', 'new'], default='new',
                        help='Which IEEE-13 network to use (default: new)')
    parser.add_argument('--raw', action='store_true',
                        help='Print raw JSON PolicyState instead of human-readable log')
    args = parser.parse_args()

    if args.raw:
        import json as _json
        import training_model.core.policy as _pol
        _pol._print_state = lambda *a, **kw: None   # suppress human-readable state
        def _raw_actions(actions):
            print('[POLICY -> SIMULATOR]')
            print(_json.dumps({'actions': actions}, indent=2))
        _pol._print_actions = _raw_actions

    if args.network == 'new':
        _NETWORK_CLS = IEEE13NewNetwork
        _CASES_CLS   = IEEE13NewCases
        print("Using NEW IEEE-13 network (8 switches, V1-V4 tie nodes)")
    else:
        _NETWORK_CLS = IEEE13NewNetwork
        _CASES_CLS   = IEEE13NewCases
        print("Using NEW IEEE-13 network (old flag ignored, only new network supported)")

    import json, datetime

    unknown_results = []
    for case in _CASES_CLS.all_cases():
        unknown_results.append(run_case(case, known_faults=False, raw=args.raw))

    # Save summary JSON
    summary = {
        'generated': datetime.datetime.now().isoformat(timespec='seconds'),
        'network': args.network,
        'cases': [
            {
                'case':   r['case'],
                'hours':  r['steps'],
                'reward': r['reward'],
                'done':   r['done'],
            }
            for r in unknown_results
        ]
    }
    summary_path = os.path.join(OUTPUT_DIR, 'summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print("  Unknown Faults — Summary")
    print(f"{'='*60}")
    print(f"  {'Case':<10} {'Hours':>8} {'Reward':>10}")
    print(f"  {'-'*32}")
    for r in unknown_results:
        print(f"  {r['case']:<10} {r['steps']:>8} {r['reward']:>10.0f}")
    print(f"\n  Summary saved to: {summary_path}")
    print(f"  Graph images saved to: {OUTPUT_DIR}/")
