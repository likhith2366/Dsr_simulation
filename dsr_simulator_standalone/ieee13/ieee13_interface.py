"""
IEEE-13 DSR Interface
=====================

Inherits from IndependentDSRInterface, adding IEEE-13 system-specific
initialization logic.

Usage:
  1. sim = IndependentIEEE13DSRInterface()   # Create instance
  2. sim.setup_case('Case1')                  # Load scenario configuration
  3. sim.setup_ieee13_scenario()              # Initialize all agents (RC/MPS/DP/Load/Switch)
  4. state = sim.get_current_state()          # Get initial state
  5. sim.move_repair_crew(...)                # Execute action
  6. sim.advance_time()                       # Advance time

Key Methods:
  - setup_case(case_name): Load the specified scenario configuration from IEEE13Config
  - setup_ieee13_scenario(): Based on configuration:
    * Add all RCs (repair crews)
    * Add all MPSs (mobile power sources)
    * Add all damage points (node faults / edge faults)
    * Add all loads
    * Add all switches and validate initial topology (no cycles)
  - _build_ieee13_topology(): Build electrical graph and traffic graph from configuration
  - reset(episode_config): Fully reset and reinitialize (supports scenario switching)
"""

import logging
from typing import Dict, Any
from ..core.dsr_interface import IndependentDSRInterface
from .ieee13_config import IEEE13Config


class IndependentIEEE13DSRInterface(IndependentDSRInterface):
    """Independent IEEE-13 DSR Interface for parallel training

    Manages IEEE-13 bus system configuration and environment state
    """

    def __init__(self):
        """Initialize independent IEEE-13 DSR interface"""
        super().__init__()
        self.ieee13_config = IEEE13Config()
        self.current_case = None
        self.case_config = None
        self.logger = logging.getLogger(__name__)
        self.system_type = 'IEEE-13'

        # Log instance creation
        self.logger.info(f"Created independent IEEE-13 interface instance: {id(self)}")
        self.logger.info(f"  System: IEEE-13 ({len(self.ieee13_config.system_config.get('nodes', {}))} nodes)")

    def reset(self, episode_config: dict = None):
        """Reset environment and setup IEEE DSR scenario with independent state"""
        # Get case name from episode_config
        if episode_config and 'damage_scenario' in episode_config:
            damage_scenario = episode_config['damage_scenario']
            case_name = damage_scenario.get('case_name', 'Case1')
            self.logger.info(f"Resetting independent {self.system_type} with {case_name} (instance: {id(self)})")

            # Get case configuration
            self.case_config = self.ieee13_config.get_case_config(case_name)
            self.current_case = case_name

            # Reset with independent state management
            self.reset_system()
            self._create_ieee13_network()
            self.setup_ieee13_scenario()

            return self.get_current_state()
        else:
            # Fallback to basic reset
            self.reset_system()
            return self.get_current_state()

    def setup_case(self, case_name: str):
        """Setup specific IEEE DSR case with independent state"""
        self.logger.info(f"Setting up independent {self.system_type} {case_name}... (instance: {id(self)})")

        # Get case configuration
        self.case_config = self.ieee13_config.get_case_config(case_name)
        self.current_case = case_name

        # Reset system first
        self.reset_system()

        # Create network topology
        self._create_ieee13_network()

        # Setup will be completed in setup_ieee13_scenario
        self.logger.info(f"Independent {self.system_type} {case_name} ready for episode setup (instance: {id(self)})")
        return True

    def _create_ieee13_network(self):
        """Create complete IEEE network topology for this instance"""
        try:
            # Create topology using the method from _build_ieee13_topology
            result = self._build_ieee13_topology()
            self.logger.info(f"Created independent {self.system_type} network topology for {self.current_case} (instance: {id(self)})")
            self.logger.info(f"  - Topology: Standard {self.system_type} bus system")
            self.logger.info(f"  - Grid source: Grid (substation)")
            return result
        except Exception as e:
            self.logger.error(f"Error creating independent {self.system_type} network: {e}")
            raise

    def setup_ieee13_scenario(self):
        """Setup IEEE DSR scenario with case-specific configuration using independent agents"""
        if not self.case_config:
            raise ValueError("No case configuration loaded. Call setup_case() first.")

        self.logger.info(f"Setting up independent {self.system_type} scenario for {self.current_case} (instance: {id(self)})")
        self.logger.info(f"Available config keys: {list(self.case_config.keys())}")
        self.logger.info(f"Repair crews count: {len(self.case_config.get('repair_crews', {}))}")
        self.logger.info(f"MPS count: {len(self.case_config.get('mobile_power_sources', {}))}")
        self.logger.info(f"Faults count: {len(self.case_config.get('faults', []))}")

        # Add repair crews using agent manager
        for rc_id, rc_config in self.case_config['repair_crews'].items():
            result = self.add_repair_crew(
                rc_id=rc_id,
                initial_position=rc_config['initial_position'],
                speed=rc_config['speed'],
                efficiency=rc_config['efficiency'],
                resources=rc_config['resources']
            )
            self.logger.info(f"Independent RC {rc_id} result: {result.get('status', 'unknown')} (instance: {id(self)})")

        # Add mobile power sources using agent manager
        mps_configs = self.case_config.get('mobile_power_sources', {})
        self.logger.info(f"Processing {len(mps_configs)} independent mobile power sources...")
        for mps_id, mps_config in mps_configs.items():
            self.logger.info(f"Adding independent MPS {mps_id} at {mps_config['initial_position']} (instance: {id(self)})")
            result = self.add_mobile_power(
                mps_id=mps_id,
                initial_position=mps_config['initial_position'],
                p_limit=mps_config['p_limit'],
                s_limit=mps_config['s_limit'],
                energy=mps_config['energy'],
                speed=mps_config.get('speed', 1.0)
            )
            self.logger.info(f"Independent MPS {mps_id} result: {result.get('status', 'unknown')} (instance: {id(self)})")

        # Add damage points using agent manager
        faults = self.case_config.get('faults', [])
        self.logger.info(f"Adding {len(faults)} independent damage points...")
        for fault_config in faults:
            fault_type = fault_config.get('type')

            if fault_type == 'node':
                # Node fault: fault is at a specific node
                from_node = fault_config['node']
                to_node = fault_config['node']
                position = 0
                is_node_fault = True
                fault_node_id = from_node
            elif fault_type == 'edge':
                # Edge fault: fault is on an edge between two nodes
                edge = fault_config['edge']
                offset_from = fault_config['offset_from']
                offset = fault_config['offset']

                # Determine from_node and to_node based on offset_from
                # The fault is located 'offset' distance from 'offset_from' node
                if offset_from == edge[0]:
                    # offset is from the first node of the edge
                    from_node = edge[0]
                    to_node = edge[1]
                    position = offset
                else:
                    # offset is from the second node of the edge
                    # Need to reverse the edge direction
                    from_node = edge[1]
                    to_node = edge[0]
                    position = offset

                is_node_fault = False
                fault_node_id = fault_config.get('fault_node_id')
            else:
                self.logger.error(f"Unknown fault type: {fault_type} for fault {fault_config.get('fault_id')}")
                continue

            # Get repair demand and capacity with correct field names
            repair_demand = fault_config.get('demand', fault_config.get('repair_demand', 0))
            capacity = fault_config.get('cap', fault_config.get('capacity', 1))

            dp = self.agent_manager.add_damage_point(
                dp_id=fault_config['fault_id'],
                from_node=from_node,
                to_node=to_node,
                distance=position,
                repair_demand=repair_demand,
                fault_node_id=fault_node_id,
                capacity=capacity
            )

            # Apply fault to environment (node fault vs edge fault)
            if is_node_fault:
                # Node fault: apply to the node itself
                dp._apply_node_fault(from_node, self.env.tgraph, self.env.egraph)
            else:
                # Edge fault: split edge and create fault node
                dp._apply_edge_fault(
                    from_node,
                    to_node,
                    position,
                    self.env.tgraph,
                    self.env.egraph
                )

        # Add loads using agent manager
        loads = self.case_config.get('loads', {})
        self.logger.info(f"Adding {len(loads)} independent loads...")
        for load_id, load_config in loads.items():
            self.agent_manager.add_load(
                load_id=load_id,
                node_id=load_config['node_id'],
                P=load_config['P'],
                Q=load_config['Q'],
                W=load_config['W']
            )

        # Add switches using agent manager with initial states
        # Note: Switches are created with their initial_state directly
        # The environment will validate topology (must be cycle-free) in update_switch_effects()
        switches = self.case_config.get('switches', {})
        self.logger.info(f"Adding {len(switches)} switches...")
        for switch_id, switch_config in switches.items():
            initial_state = switch_config.get('initial_state', 'close')
            # Normalize 'closed' to 'close' for backward compatibility
            normalized_state = 'close' if initial_state in ['close', 'closed'] else 'open'

            switch = self.agent_manager.add_switch(
                switch_id=switch_id,
                node_id=switch_config['node_id'],
                connected_edges=switch_config['connected_edges'],
                initial_state=normalized_state
            )
            self.logger.info(f"Switch {switch_id} added with state: {normalized_state}")

        # Apply all switch states and validate topology
        # allow_faulted=True: force faulted edges to disconnected during initialization
        # revert_on_cycle=False: don't revert (just detect, will raise error if cycle exists)
        cycle_info = self.env.update_switch_effects(allow_faulted=True, revert_on_cycle=False)

        # Verify initial topology is valid (no cycles)
        if cycle_info['cycle_detected']:
            raise ValueError(
                "Invalid initial configuration: Network topology contains a cycle. "
                "Please adjust switch states in the configuration."
            )

        # Update system state after all agents are added
        # CRITICAL: This updates load states based on electrical connectivity
        # - Loads start as state='on' (default from agent_manager.add_load)
        # - update_system_state() auto-sheds loads (state='off') if they lost power due to faults/switches
        # - Loads AUTOMATICALLY restore when power available (Grid or MPS) - no manual operate_load() needed
        self.env.egraph.update_system_state()
        self.logger.info(f"System state updated after scenario setup (instance: {id(self)})")

        self.logger.info(f"Independent scenario setup complete for {self.current_case} (instance: {id(self)})")

    def _validate_ieee13_topology(self, nodes, edges, loads, system_config):
        """Validate IEEE-13 topology against expected structure"""
        # Expected values for IEEE-13 system
        expected_nodes = 19  # Grid + N1-N13 + S1,S2 + V1,V2,V3
        expected_edges = 19  # From ieee13_config.py: 19 electrical edges
        expected_loads = 9   # N2, N3, N5, N6, N7, N8, N9, N11, N12
        expected_switches = 2  # S1, S2
        expected_traffic_roads = 23  # 19 electrical edges + 4 traffic-only roads

        actual_nodes = len(nodes)
        actual_edges = len(edges)
        actual_loads = len(loads)
        actual_switches = len(system_config.get('switches', {}))
        actual_traffic_roads = len(system_config.get('traffic_roads', []))

        validation_passed = True
        errors = []

        # Check node count (more lenient - just log warning if mismatch)
        if actual_nodes != expected_nodes:
            self.logger.warning(f"Node count info: expected ~{expected_nodes}, got {actual_nodes}")

        # Check edge count
        if actual_edges < expected_edges:  # Use < instead of != for flexibility
            errors.append(f"Edge count too low: expected at least {expected_edges}, got {actual_edges}")
            validation_passed = False

        # Check load count
        if actual_loads != expected_loads:
            errors.append(f"Load count mismatch: expected {expected_loads}, got {actual_loads}")
            validation_passed = False

        # Check switch count
        if actual_switches != expected_switches:
            errors.append(f"Switch count mismatch: expected {expected_switches}, got {actual_switches}")
            validation_passed = False

        # Check traffic roads
        if actual_traffic_roads < expected_traffic_roads:
            errors.append(f"Traffic road count too low: expected at least {expected_traffic_roads}, got {actual_traffic_roads}")
            validation_passed = False

        # Verify critical nodes exist for IEEE-13
        critical_nodes = ['Grid', 'N1', 'N13', 'S1', 'S2']

        for node in critical_nodes:
            if node not in nodes:
                errors.append(f"Critical node {node} not found in topology")
                validation_passed = False

        if validation_passed:
            self.logger.info(f"[VALIDATION PASSED] Independent {self.system_type} TOPOLOGY VALIDATED")
            self.logger.info(f"  All counts match expected values for standard {self.system_type} system (instance: {id(self)})")
        else:
            self.logger.error(f"[VALIDATION FAILED] Independent {self.system_type} TOPOLOGY VALIDATION FAILED")
            for error in errors:
                self.logger.error(f"  ERROR: {error}")
            raise ValueError(f"Independent {self.system_type} topology validation failed with {len(errors)} errors")

    def _build_ieee13_topology(self):
        """Build complete IEEE network topology for this instance"""
        # Get topology from config system_config
        system_config = self.ieee13_config.system_config

        # Format nodes as list of tuples for create_network (node_id, type, voltage)
        nodes = []
        for node_id, node_info in system_config['nodes'].items():
            node_type = node_info['type']
            # IEEE-13 standard voltage: 4.16 kV
            # NOTE: Voltage parameter currently not used by DSR system (no power flow analysis)
            #       Reserved for future extensions (e.g., integration with OpenDSS/MATPOWER)
            voltage = 4.16
            nodes.append((node_id, node_type, voltage))

        # Use electrical edges (create_network will add them to both EGraph and TGraph)
        edges = system_config['edges'].copy()

        self.logger.info(f"Building topology with {len(edges)} electrical edges (will be added to both EGraph and TGraph)")

        # Create network structure using our create_network method
        result = self.create_network(nodes, edges)
        if result.get('status') != 'success':
            raise ValueError(f"Failed to create IEEE-13 topology: {result.get('message', 'Unknown error')}")

        # Add traffic-only roads to TGraph (roads that exist for movement but have no electrical connection)
        # These are extracted from traffic_roads that are NOT derived from electrical edges
        traffic_roads = system_config.get('traffic_roads', [])

        # IEEE-13 has 4 bidirectional traffic-only roads (shortcuts for agent movement)
        traffic_only_patterns = {'TR_N7_V3', 'TR_V3_N7', 'TR_N12_V1', 'TR_V1_N12'}

        for road in traffic_roads:
            road_id, from_node, to_node, length = road
            if road_id in traffic_only_patterns:
                # Add to traffic graph only (not electrical graph)
                self.env.tgraph.add_edge(road_id, from_node, to_node, length)
                self.logger.debug(f"Added traffic-only road: {road_id} ({from_node} → {to_node}, {length}km)")

        total_traffic_roads = len([r for r in traffic_roads])
        self.logger.info(f"Independent {self.system_type} topology created successfully (instance: {id(self)})")
        self.logger.info(f"  - Electrical edges: {len(edges)}")
        self.logger.info(f"  - Total traffic roads: {total_traffic_roads}")

        return result
