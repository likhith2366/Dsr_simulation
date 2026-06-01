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
from training_model.config.ieee13_cases import IEEE13Cases, IEEE13Network
from training_model.config.ieee13new_cases import IEEE13NewCases, IEEE13NewNetwork

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_STEPS = 50

# Set at runtime via --network flag
_NETWORK_CLS = None
_CASES_CLS   = None


def run_case(case_name: str, known_faults: bool = False):
    mode = 'KNOWN faults' if known_faults else 'UNKNOWN faults'
    print(f"\n{'='*60}")
    print(f"  Case: {case_name}  [{mode}]")
    print(f"{'='*60}")

    env = DSREnvironment()
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
        lag      = ((dp.repaired_at_step or 0) - (dp.discovered_at_step or 0)) if dp.discovered_at_step else '-'
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
    args = parser.parse_args()

    if args.network == 'new':
        _NETWORK_CLS = IEEE13NewNetwork
        _CASES_CLS   = IEEE13NewCases
        print("Using NEW IEEE-13 network (8 switches, V1-V4 tie nodes)")
    else:
        _NETWORK_CLS = IEEE13Network
        _CASES_CLS   = IEEE13Cases
        print("Using ORIGINAL IEEE-13 network")

    known_results   = []
    unknown_results = []

    for case in _CASES_CLS.all_cases():
        known_results.append(run_case(case, known_faults=True))
        unknown_results.append(run_case(case, known_faults=False))

    print(f"\n{'='*60}")
    print("  Comparison: Known vs Unknown Faults")
    print(f"{'='*60}")
    print(f"  {'Case':<10} {'Known Steps':>12} {'Unknown Steps':>14} {'Extra Hours':>12}")
    print(f"  {'-'*52}")
    for k, u in zip(known_results, unknown_results):
        extra = u['steps'] - k['steps']
        print(f"  {k['case']:<10} {k['steps']:>12} {u['steps']:>14} {extra:>+12}")

    print(f"\n  Graph images saved to: {OUTPUT_DIR}/")
