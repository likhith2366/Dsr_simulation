"""
Unknown Fault Environment
=========================
Wraps the existing DSRSimulator to support unknown fault scenarios.

Key differences from original simulator:
  1. Fault locations are HIDDEN at episode start
  2. New Scout agent added - searches network for faults
  3. RCs also discover faults when passing through nodes/edges
  4. When fault found:
       - RC at fault + has resources → repair immediately
       - RC at fault + no resources → report only
       - Scout at fault → report only, keep searching
  5. get_observable_state() hides fault locations until discovered

Flow:
  Episode starts
      ↓
  Scout + RCs start moving (no one knows where faults are)
      ↓
  Scout visits node N5 → "DP1 found here!"
  RC2 passes through edge N2-S1 → "DP3 found here!"
      ↓
  System now knows DP1 and DP3 locations
  RC1 gets assigned to DP1 (capable, has resources)
  RC2 already at DP3 → repair immediately
      ↓
  Scout continues searching for remaining hidden faults
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional, Any
from dsr_simulator_standalone import DSRSimulator13, DSRSimulator33
from .scout_agent import ScoutAgent
from .fault_discovery import FaultDiscoveryManager


class UnknownFaultEnvironment:
    """
    Wraps DSRSimulator with unknown fault discovery mechanics.
    Adds Scout agent and hides fault locations until discovered.
    """

    def __init__(self, system: str = 'ieee13'):
        """
        Args:
            system: 'ieee13' or 'ieee33'
        """
        self.system = system

        # Create base simulator
        if system == 'ieee13':
            self.sim = DSRSimulator13()
        else:
            self.sim = DSRSimulator33()

        # Discovery manager - tracks hidden vs known faults
        self.discovery_manager = FaultDiscoveryManager()

        # Scout agents (added on top of base simulator)
        self.scouts: Dict[str, ScoutAgent] = {}

        # Track all network nodes (for scout search planning)
        self.all_nodes: List[str] = []

        # Current case info
        self.current_case = None
        self._raw_faults = []     # original fault configs (ground truth)

        # Step counter
        self.current_time = 0

    # ─────────────────────────────────────────
    # Setup
    # ─────────────────────────────────────────

    def setup(self, case_name: str, num_scouts: int = 1):
        """
        Setup the environment for an episode.

        Args:
            case_name: 'Case1' through 'Case10'
            num_scouts: how many scout agents to add (default 1)
        """
        self.current_case = case_name
        self.current_time = 0
        self.scouts = {}

        # Setup base simulator (this loads faults into the sim)
        self.sim.setup_case(case_name)

        if self.system == 'ieee13':
            self.sim.setup_ieee13_scenario()
        else:
            self.sim.setup_ieee33_scenario()

        # Get raw fault config BEFORE hiding
        state = self.sim.get_current_state()
        self._raw_faults = self._extract_fault_configs(case_name)

        # Load faults into discovery manager (hides them)
        self.discovery_manager.load_faults(self._raw_faults)

        # Get all network nodes for scout planning
        self.all_nodes = list(state.get('nodes', {}).keys()) if 'nodes' in state else []

        # Add scouts at strategic starting positions
        scout_positions = self._get_scout_start_positions(state, num_scouts)
        for i, pos in enumerate(scout_positions):
            scout_id = f'Scout{i+1}'
            self.scouts[scout_id] = ScoutAgent(scout_id, pos, speed=10.0)
            print(f"  Scout {scout_id} added at {pos}")

        print(f"\n  [ENV] {case_name} loaded — {len(self._raw_faults)} faults HIDDEN")
        print(f"  [ENV] {len(self.scouts)} scout(s) deployed")

        return self.get_observable_state()

    def _get_scout_start_positions(self, state: Dict, num_scouts: int) -> List[str]:
        """Place scouts at RC positions (they start together, then split)."""
        rc_positions = [rc['current_position'] for rc in state['repair_crews'].values()]
        positions = []
        for i in range(num_scouts):
            # Cycle through RC positions if more scouts than RCs
            positions.append(rc_positions[i % len(rc_positions)])
        return positions

    def _extract_fault_configs(self, case_name: str) -> List[Dict]:
        """Extract raw fault config from the case."""
        if self.system == 'ieee13':
            from dsr_simulator_standalone import IEEE13Config
            config = IEEE13Config()
        else:
            from dsr_simulator_standalone import IEEE33Config
            config = IEEE33Config()

        case_config = config.get_case_config(case_name)
        return case_config.get('faults', [])

    # ─────────────────────────────────────────
    # State (observable - hides unknown faults)
    # ─────────────────────────────────────────

    def get_observable_state(self) -> Dict:
        """
        Returns state with fault locations HIDDEN until discovered.
        This is what the LLM/agent sees.
        """
        base_state = self.sim.get_current_state()

        # Replace damage_points with only DISCOVERED faults
        discovered = self.discovery_manager.get_observable_faults()
        observable_damage_points = {}

        for fault_id, fault_info in discovered.items():
            # Find matching DP in base simulator state
            if fault_id in base_state.get('damage_points', {}):
                dp = base_state['damage_points'][fault_id]
                dp['discovered_by'] = fault_info.get('discovered_by', 'unknown')
                observable_damage_points[fault_id] = dp

        # Build observable state
        observable_state = {
            'time': self.current_time,
            'repair_crews': base_state.get('repair_crews', {}),
            'mobile_power': base_state.get('mobile_power', {}),
            'loads': base_state.get('loads', {}),
            'switches': base_state.get('switches', {}),
            'scouts': {sid: s.get_state() for sid, s in self.scouts.items()},

            # Only show DISCOVERED faults
            'damage_points': observable_damage_points,

            # Discovery progress info
            'discovery_status': {
                'faults_discovered': len(discovered),
                'faults_still_hidden': len(self.discovery_manager.hidden_faults),
                'total_faults': len(self._raw_faults),
                'nodes_visited': len(self.discovery_manager.visited_nodes),
                'total_nodes': len(self.all_nodes)
            }
        }

        return observable_state

    # ─────────────────────────────────────────
    # Scout Actions
    # ─────────────────────────────────────────

    def move_scout(self, scout_id: str, target_node: str) -> Dict:
        """
        Move a scout to a target node.
        Uses base simulator's TGraph for pathfinding.
        """
        if scout_id not in self.scouts:
            return {'status': 'error', 'message': f'{scout_id} not found'}

        scout = self.scouts[scout_id]

        # Use base sim's TGraph for pathfinding
        tgraph = self.sim.env.tgraph
        path, distance = tgraph.find_shortest_path(scout.current_position, target_node)

        if not path:
            return {'status': 'error', 'message': f'No path from {scout.current_position} to {target_node}'}

        scout.assign_search_path(path, distance)
        print(f"  Scout {scout_id} moving from {scout.current_position} to {target_node} ({distance}km)")

        return {'status': 'success', 'path': path, 'distance': distance}

    def auto_assign_scout(self, scout_id: str) -> Dict:
        """
        Automatically send scout to the nearest unvisited node.
        Simple greedy search strategy.
        """
        if scout_id not in self.scouts:
            return {'status': 'error', 'message': f'{scout_id} not found'}

        scout = self.scouts[scout_id]
        tgraph = self.sim.env.tgraph

        # Find nearest unvisited node
        unvisited = self.discovery_manager.get_unvisited_nodes(self.all_nodes)
        if not unvisited:
            return {'status': 'done', 'message': 'All nodes visited'}

        # Find closest unvisited
        best_node = None
        best_dist = float('inf')

        for node in unvisited:
            _, dist = tgraph.find_shortest_path(scout.current_position, node)
            if dist != -1 and dist < best_dist:
                best_dist = dist
                best_node = node

        if best_node:
            return self.move_scout(scout_id, best_node)

        return {'status': 'error', 'message': 'No reachable unvisited nodes'}

    # ─────────────────────────────────────────
    # Time Step
    # ─────────────────────────────────────────

    def advance_time(self) -> Dict:
        """
        Advance one time step.
        1. Advance base simulator (moves RCs, MPSs)
        2. Move scouts
        3. Check all agent positions for fault discovery
        4. If RC discovers fault and is capable → auto repair
        """
        self.current_time += 1
        events = []

        # 1. Advance base simulator
        base_result = self.sim.advance_time()
        events.extend(base_result.get('events', []))

        # 2. Move scouts
        for scout in self.scouts.values():
            prev_position = scout.current_position
            scout.update_position()

            # If scout moved to new node → check for faults
            if scout.current_position != prev_position:
                new_discoveries = self.discovery_manager.visit_node(
                    scout.current_position, scout.id, 'scout'
                )
                for fault in new_discoveries:
                    events.append({
                        'type': 'fault_discovered',
                        'fault_id': fault['fault_id'],
                        'location': fault.get('node') or str(fault.get('edge')),
                        'discovered_by': scout.id,
                        'agent_type': 'scout',
                        'time': self.current_time
                    })
                    # Scout is back to idle after reporting
                    scout.state = 'idle'

        # 3. Check RC positions for fault discovery
        base_state = self.sim.get_current_state()
        for rc_id, rc in base_state['repair_crews'].items():
            rc_position = rc['current_position']

            # Check if RC is at a hidden fault node
            new_discoveries = self.discovery_manager.visit_node(
                rc_position, rc_id, 'rc'
            )
            for fault in new_discoveries:
                events.append({
                    'type': 'fault_discovered',
                    'fault_id': fault['fault_id'],
                    'location': fault.get('node') or str(fault.get('edge')),
                    'discovered_by': rc_id,
                    'agent_type': 'rc',
                    'time': self.current_time
                })

                # RC decision: capable → repair immediately
                if self.discovery_manager.check_rc_can_repair(rc, fault['fault_id']):
                    repair_result = self.sim.repair_fault(rc_id, fault['fault_id'], auto_repair=True)
                    events.append({
                        'type': 'rc_auto_repair_started',
                        'rc_id': rc_id,
                        'fault_id': fault['fault_id'],
                        'message': f'{rc_id} discovered and started repairing {fault["fault_id"]} immediately',
                        'time': self.current_time
                    })
                    print(f"  [AUTO] {rc_id} discovered {fault['fault_id']} and started repair immediately!")
                else:
                    print(f"  [REPORT] {rc_id} found {fault['fault_id']} but cannot repair (insufficient resources or busy)")

        # 4. Auto assign idle scouts to unvisited nodes
        for scout_id, scout in self.scouts.items():
            if scout.state == 'idle' and not self.discovery_manager.all_faults_discovered():
                self.auto_assign_scout(scout_id)

        return {
            'status': 'success',
            'time': self.current_time,
            'events': events,
            'discovery_summary': self.discovery_manager.get_summary()
        }

    # ─────────────────────────────────────────
    # Pass-through to base simulator
    # ─────────────────────────────────────────

    def move_repair_crew(self, rc_id: str, target: str) -> Dict:
        """Move RC - only valid for DISCOVERED fault locations."""
        return self.sim.move_repair_crew(rc_id, target)

    def repair_fault(self, rc_id: str, fault_id: str, auto_repair: bool = True) -> Dict:
        """Repair a fault - only valid if fault is discovered."""
        if fault_id not in self.discovery_manager.discovered_faults:
            return {
                'status': 'error',
                'message': f'{fault_id} not yet discovered. Scout must find it first.'
            }
        return self.sim.repair_fault(rc_id, fault_id, auto_repair)

    def move_mps(self, mps_id: str, target_node: str) -> Dict:
        return self.sim.move_mps(mps_id, target_node)

    def set_mps_output(self, mps_id: str, P: float, Q: float, target_loads: List[str]) -> Dict:
        return self.sim.set_mps_output(mps_id, P, Q, target_loads)

    def operate_switches(self, switch_ops: List[Dict]) -> Dict:
        return self.sim.operate_switches(switch_ops)

    def is_done(self) -> bool:
        """Episode done when all faults discovered AND repaired."""
        base_state = self.sim.get_current_state()
        all_repaired = all(
            dp.get('state') == 'repaired'
            for dp in base_state.get('damage_points', {}).values()
        )
        return all_repaired

    def get_reward(self) -> float:
        """Weighted power restored - same reward signal as base simulator."""
        state = self.sim.get_current_state()
        loads = state.get('loads', {})
        return sum(l['W'] * l['P'] for l in loads.values() if l.get('state') == 'on')

    def print_status(self):
        """Print current episode status."""
        state = self.get_observable_state()
        disc = state['discovery_status']

        print(f"\n  --- Time={self.current_time} ---")
        print(f"  Faults: {disc['faults_discovered']}/{disc['total_faults']} discovered, "
              f"{disc['faults_still_hidden']} still hidden")
        print(f"  Nodes explored: {disc['nodes_visited']}/{disc['total_nodes']}")
        print(f"  Loads: {sum(1 for l in state['loads'].values() if l.get('state')=='on')}/{len(state['loads'])} ON")
        print(f"  Reward: {self.get_reward():.0f}")

        for scout_id, scout_state in state['scouts'].items():
            print(f"  {scout_id}: {scout_state['state']} @ {scout_state['current_position']} "
                  f"(visited {scout_state['visited_count']} nodes)")

        for rc_id, rc in state['repair_crews'].items():
            print(f"  {rc_id}: {rc['state']} @ {rc['current_position']} "
                  f"(resources: {rc['remaining_resources']}/{rc['total_resources']})")
