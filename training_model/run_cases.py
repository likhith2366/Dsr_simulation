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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training_model.core.environment import DSREnvironment
from training_model.visualizer import draw_network
from training_model.config.ieee13_cases import IEEE13Cases

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_STEPS = 50


def run_case(case_name: str):
    print(f"\n{'='*60}")
    print(f"  Case: {case_name}")
    print(f"{'='*60}")

    env = DSREnvironment()
    env.setup(case_name, num_scouts=1)

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

    # Save initial graph
    draw_network(env,
                 title=f'{case_name} — Initial State (faults hidden)',
                 save_path=os.path.join(OUTPUT_DIR, f'{case_name}_step0.png'),
                 show=False)

    # Simulation loop
    for step in range(MAX_STEPS):
        result = env.step()

        # Print events
        for event in result['events']:
            print(f"  [t={result['time']:02d}] {event}")

        # Every 10 steps save a graph
        if result['time'] % 10 == 0:
            draw_network(env,
                         title=f'{case_name} — Step {result["time"]}',
                         save_path=os.path.join(OUTPUT_DIR, f'{case_name}_step{result["time"]}.png'),
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
    print(f"\n  Summary:")
    print(f"    Steps taken : {env.time}")
    print(f"    Final reward: {env.get_reward():.0f} / {sum(l.W*l.P for l in env.loads.values()):.0f}")
    print(f"    Loads ON    : {sum(1 for l in env.loads.values() if l.state=='on')}/{len(env.loads)}")
    for dp in env.faults.values():
        disc = f"by {dp.discovered_by}" if dp.discovered else "NOT FOUND"
        print(f"    {dp.id}: {dp.state} (discovered {disc})")

    return {
        'case': case_name,
        'steps': env.time,
        'reward': env.get_reward(),
        'done': env.is_done()
    }


if __name__ == '__main__':
    results = []
    for case in IEEE13Cases.all_cases():
        r = run_case(case)
        results.append(r)

    print(f"\n{'='*60}")
    print("  All Cases Summary")
    print(f"{'='*60}")
    print(f"  {'Case':<10} {'Steps':>6} {'Reward':>10} {'Done':>6}")
    print(f"  {'-'*36}")
    for r in results:
        print(f"  {r['case']:<10} {r['steps']:>6} {r['reward']:>10.0f} {str(r['done']):>6}")

    print(f"\n  Graph images saved to: {OUTPUT_DIR}/")
