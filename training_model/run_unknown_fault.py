"""
Run Unknown Fault Simulation
=============================
Test script - shows how the unknown fault environment works.

Run:
    cd a:\dsr_simulator_standalone
    python training_model/run_unknown_fault.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from training_model import UnknownFaultEnvironment


def run_episode(case_name: str = 'Case1', max_steps: int = 40):
    print("=" * 60)
    print(f"  Unknown Fault Simulation — {case_name}")
    print("=" * 60)

    # Create environment
    env = UnknownFaultEnvironment(system='ieee13')

    # Setup - faults are hidden, scout is added
    state = env.setup(case_name, num_scouts=1)

    print(f"\n  Initial State:")
    print(f"  Loads ON: {sum(1 for l in state['loads'].values() if l.get('state')=='on')}/{len(state['loads'])}")
    print(f"  Discovered faults: {state['discovery_status']['faults_discovered']}")
    print(f"  Hidden faults: {state['discovery_status']['faults_still_hidden']}")

    # Simulation loop
    for step in range(max_steps):

        # Auto assign scout to search
        for scout_id in env.scouts:
            if env.scouts[scout_id].state == 'idle':
                env.auto_assign_scout(scout_id)

        # Advance time - scout moves, RCs move, discoveries happen
        result = env.advance_time()

        # Print discoveries
        for event in result['events']:
            if event['type'] == 'fault_discovered':
                print(f"\n  *** FAULT FOUND at step {step+1}: "
                      f"{event['fault_id']} at {event['location']} "
                      f"by {event['agent_type']} {event['discovered_by']} ***")

            elif event['type'] == 'rc_auto_repair_started':
                print(f"  *** AUTO REPAIR: {event['message']} ***")

            elif event['type'] == 'fault_repaired':
                print(f"  *** REPAIRED: {event['fault_ids']} at step {step+1} ***")

        # Print status every 5 steps
        if (step + 1) % 5 == 0:
            env.print_status()

        # Check done
        if env.is_done():
            print(f"\n  All faults repaired at step {step+1}!")
            break

    # Final state
    print("\n" + "=" * 60)
    print("  Final State")
    print("=" * 60)
    env.print_status()
    disc_summary = env.discovery_manager.get_summary()
    print(f"\n  Discovery log:")
    for entry in disc_summary['discovery_log']:
        print(f"    {entry['fault_id']} found by {entry['agent_type']} "
              f"{entry['discovered_by']} at {entry['location']}")


if __name__ == '__main__':
    run_episode('Case1', max_steps=40)
