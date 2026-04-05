#!/usr/bin/env python3
"""
DSR Simulator Demo - Distribution System Restoration Simulator Usage Example
=============================================================================

This script demonstrates the basic usage of the DSR simulator, including:
1. Creating a simulator and loading a scenario
2. Viewing system state
3. Moving repair crews and repairing faults
4. Deploying mobile power sources for temporary power supply
5. Operating switches for network reconfiguration

How to run:
    cd /path/to/parent/of/dsr_simulator_standalone
    python -m dsr_simulator_standalone.demo
    # or
    python dsr_simulator_standalone/demo.py
"""

import sys
import os

# Ensure this package can be imported
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from dsr_simulator_standalone import DSRSimulator, IEEE13Config


def print_separator(title: str):
    """Print a separator line."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_state_summary(state: dict):
    """Print a system state summary."""
    print(f"\n  --- System State (Time = {state['time']}) ---")

    # Damage point status
    print(f"  Damage Points:")
    for dp_id, dp in state.get('damage_points', {}).items():
        progress = dp.get('repair_progress', 0)
        demand = dp.get('repair_demand', 0)
        dp_state = dp.get('state', '?')
        print(f"    {dp_id}: {dp_state} (progress: {progress}/{demand})")

    # Repair crew status
    print(f"  Repair Crews:")
    for rc_id, rc in state.get('repair_crews', {}).items():
        pos = rc.get('current_position', '?')
        rc_state = rc.get('state', '?')
        res = rc.get('remaining_resources', 0)
        total = rc.get('total_resources', 0)
        print(f"    {rc_id}: {rc_state} @ {pos} (resources: {res}/{total})")

    # Mobile power source status
    print(f"  Mobile Power Sources (MPS):")
    for mps_id, mps in state.get('mobile_power', {}).items():
        pos = mps.get('current_position', '?')
        mps_state = mps.get('state', '?')
        energy = mps.get('energy', 0)
        pout = mps.get('Pout', 0)
        targets = mps.get('target_loads', [])
        print(f"    {mps_id}: {mps_state} @ {pos} (energy: {energy}kWh, output: {pout}kW, targets: {targets})")

    # Load status
    loads = state.get('loads', {})
    on_count = sum(1 for l in loads.values() if l.get('state') == 'on')
    total_count = len(loads)
    total_pw = sum(l.get('P', 0) * l.get('W', 0) for l in loads.values() if l.get('state') == 'on')
    max_pw = sum(l.get('P', 0) * l.get('W', 0) for l in loads.values())
    print(f"  Loads: {on_count}/{total_count} energized, weighted power: {total_pw:.0f}/{max_pw:.0f} (W*P)")

    # Switch status
    print(f"  Switches:")
    for sw_id, sw in state.get('switches', {}).items():
        print(f"    {sw_id}: {sw.get('state', '?')}")


def demo_basic_usage():
    """Basic usage example."""
    print_separator("Demo 1: Basic Usage - Create simulator and view state")

    # Create simulator
    sim = DSRSimulator()
    print("  [OK] Simulator created successfully")

    # View available scenarios
    config = IEEE13Config()
    cases = config.get_all_cases()
    print(f"  Available scenarios: {cases}")

    # Set up Case1
    sim.setup_case('Case1')
    sim.setup_ieee13_scenario()
    print("  [OK] Case1 scenario loaded successfully")

    # View initial state
    state = sim.get_current_state()
    print_state_summary(state)

    return sim


def demo_repair_crew(sim: DSRSimulator):
    """Repair crew operation example."""
    print_separator("Demo 2: Repair Crew Operations - Move to fault and repair")

    state = sim.get_current_state()

    # Get the first RC and the first DP
    rc_ids = list(state['repair_crews'].keys())
    dp_ids = list(state['damage_points'].keys())

    if not rc_ids or not dp_ids:
        print("  [SKIP] No available RC or DP")
        return

    rc_id = rc_ids[0]
    dp_id = dp_ids[0]
    dp_info = state['damage_points'][dp_id]

    print(f"\n  === Step 1: Move {rc_id} to fault point {dp_id} ===")
    print(f"  Fault location: {dp_info.get('from_node')}-{dp_info.get('to_node')}")

    result = sim.move_repair_crew(rc_id, dp_id)
    print(f"  Move result: {result.get('status', 'unknown')}")

    # Advance time until RC arrives
    for step in range(10):
        result = sim.advance_time()
        state = sim.get_current_state()
        rc_state = state['repair_crews'][rc_id]['state']
        rc_pos = state['repair_crews'][rc_id]['current_position']

        if rc_state != 'moving':
            print(f"  [Step {step+1}] {rc_id} has arrived at {rc_pos} (state: {rc_state})")
            break
        else:
            dist = state['repair_crews'][rc_id].get('remaining_distance', 0)
            print(f"  [Step {step+1}] {rc_id} moving... remaining distance: {dist}km")

    # Start repair
    print(f"\n  === Step 2: {rc_id} repairs {dp_id} (auto continuous repair) ===")
    result = sim.repair_fault(rc_id, dp_id, auto_repair=True)
    print(f"  Repair command result: {result.get('status', 'unknown')}")

    # Advance time until repair is complete
    for step in range(20):
        result = sim.advance_time()
        state = sim.get_current_state()
        dp_state = state['damage_points'][dp_id]['state']
        progress = state['damage_points'][dp_id].get('repair_progress', 0)
        demand = state['damage_points'][dp_id].get('repair_demand', 0)

        if dp_state == 'repaired':
            print(f"  [Step {step+1}] {dp_id} repair complete!")
            break
        else:
            print(f"  [Step {step+1}] Repair progress: {progress}/{demand}")

    print_state_summary(state)


def demo_mps_operation(sim: DSRSimulator):
    """Mobile power source operation example."""
    print_separator("Demo 3: MPS Operations - Deploy MPS for temporary power supply")

    state = sim.get_current_state()
    mps_ids = list(state['mobile_power'].keys())

    if not mps_ids:
        print("  [SKIP] No available MPS")
        return

    mps_id = mps_ids[0]
    mps_info = state['mobile_power'][mps_id]
    print(f"  Using {mps_id}, current position: {mps_info['current_position']}, state: {mps_info['state']}")

    # Find de-energized loads
    loads = state.get('loads', {})
    off_loads = [(lid, l) for lid, l in loads.items() if l.get('state') == 'off']
    if not off_loads:
        print("  [SKIP] All loads are energized, MPS not needed")
        return

    # Select a de-energized load node as MPS target
    target_load_id, target_load = off_loads[0]
    target_node = target_load['node_id']
    print(f"  Target: supply power to {target_load_id} (node {target_node})")
    print(f"  Load demand: P={target_load['P']}kW, Q={target_load['Q']}kVar, weight W={target_load['W']}")

    # Move MPS
    if mps_info['current_position'] != target_node:
        print(f"\n  === Step 1: Move {mps_id} to {target_node} ===")
        result = sim.move_mps(mps_id, target_node)
        print(f"  Move result: {result.get('status', 'unknown')}")

        # Wait for arrival
        for step in range(15):
            sim.advance_time()
            state = sim.get_current_state()
            if state['mobile_power'][mps_id]['state'] != 'moving':
                print(f"  [Step {step+1}] {mps_id} has arrived at {target_node}")
                break
    else:
        print(f"  {mps_id} is already at target position {target_node}")

    # Select loads to supply power to
    target_loads = [target_load_id]
    # Can add other de-energized loads within the same electrical island
    p_total = target_load['P']
    q_total = target_load['Q']

    print(f"\n  === Step 2: Set {mps_id} output ===")
    print(f"  P={p_total}kW, Q={q_total}kVar, target_loads={target_loads}")

    result = sim.set_mps_output(mps_id, p_total, q_total, target_loads=target_loads)
    print(f"  Setting result: {result.get('status', 'unknown')}")
    if result.get('status') != 'success':
        print(f"  Message: {result.get('message', '')}")

    # Advance one step to see the effect
    sim.advance_time()
    state = sim.get_current_state()
    print_state_summary(state)


def demo_switch_operation(sim: DSRSimulator):
    """Switch operation example."""
    print_separator("Demo 4: Switch Operations - Network Reconfiguration")

    state = sim.get_current_state()
    switches = state.get('switches', {})

    print(f"  Current switch states:")
    for sw_id, sw in switches.items():
        print(f"    {sw_id}: {sw.get('state', '?')}")

    # Try opening S1
    print(f"\n  === Operation: Open S1 ===")
    result = sim.operate_switches([{'switch_id': 'S1', 'operation': 'open'}])
    print(f"  Result: {result.get('status', 'unknown')}")

    state = sim.get_current_state()
    print(f"  S1 state after operation: {state['switches'].get('S1', {}).get('state', '?')}")
    print(f"  S2 state after operation: {state['switches'].get('S2', {}).get('state', '?')}")

    # Restore S1
    print(f"\n  === Operation: Close S1 ===")
    result = sim.operate_switches([{'switch_id': 'S1', 'operation': 'close'}])
    print(f"  Result: {result.get('status', 'unknown')}")


def demo_full_episode():
    """Full episode example."""
    print_separator("Demo 5: Full Episode Flow")

    sim = DSRSimulator()
    sim.setup_case('Case1')
    sim.setup_ieee13_scenario()

    state = sim.get_current_state()
    max_steps = 30

    print(f"  Starting simulation (max steps: {max_steps})")
    print_state_summary(state)

    # Simple strategy: send two RCs to repair two faults respectively
    rc_ids = list(state['repair_crews'].keys())
    dp_ids = list(state['damage_points'].keys())

    # Assign tasks
    assignments = {}
    for i, rc_id in enumerate(rc_ids):
        if i < len(dp_ids):
            assignments[rc_id] = dp_ids[i]

    print(f"\n  Task assignments: {assignments}")

    # Move all RCs to targets
    for rc_id, dp_id in assignments.items():
        sim.move_repair_crew(rc_id, dp_id)

    # Simulation loop
    for step in range(max_steps):
        result = sim.advance_time()
        state = sim.get_current_state()

        # Check if RC has arrived and needs to start repair
        for rc_id, dp_id in assignments.items():
            rc = state['repair_crews'][rc_id]
            dp = state['damage_points'][dp_id]
            if rc['state'] == 'idle' and dp['state'] == 'active':
                sim.repair_fault(rc_id, dp_id, auto_repair=True)

        # Check if all faults are repaired
        all_repaired = all(
            dp.get('state') == 'repaired'
            for dp in state['damage_points'].values()
        )

        if all_repaired:
            print(f"\n  [Step {step+1}] All faults have been repaired!")
            break

        # Print status every 5 steps
        if (step + 1) % 5 == 0:
            active_dps = sum(1 for dp in state['damage_points'].values() if dp['state'] == 'active')
            on_loads = sum(1 for l in state['loads'].values() if l['state'] == 'on')
            total_loads = len(state['loads'])
            print(f"  [Step {step+1}] Active faults: {active_dps}, Energized loads: {on_loads}/{total_loads}")

    print_state_summary(state)
    print(f"\n  Simulation ended (total steps: {state['time']})")


if __name__ == '__main__':
    print("=" * 60)
    print("  DSR Simulator Demo - Distribution System Restoration Simulator")
    print("=" * 60)

    # Demo 1: Basic usage
    sim = demo_basic_usage()

    # Demo 2: Repair crew operations
    demo_repair_crew(sim)

    # Demo 3: Mobile power source operations
    demo_mps_operation(sim)

    # Demo 4: Switch operations
    demo_switch_operation(sim)

    # Demo 5: Full episode
    demo_full_episode()

    print("\n" + "=" * 60)
    print("  All demos completed!")
    print("=" * 60)
