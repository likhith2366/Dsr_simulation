"""
Independent DSR Interface - Instance-based environment management
Inspired by 2048's independent game state design
Complete replacement for deprecated DSRInterface with instance-based agent management
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from .agent_manager import AgentManager
from .environment import IndependentDSREnvironment
from .graphs import NodeType


class IndependentDSRInterface:
    """
    DSR Interface with independent agent state management.
    Each instance has its own agent state, enabling parallel training.

    This class replaces the deprecated DSRInterface which used class-level
    agent storage (RC.repair_crews, MPS.mps_units, etc.) that caused conflicts
    in parallel training scenarios.
    """

    def __init__(self):
        """Initialize independent DSR interface"""
        # Initialize independent agent manager first
        self.agent_manager = AgentManager(logging.getLogger(__name__))

        # Initialize independent environment with agent manager reference
        self.env = IndependentDSREnvironment(self.agent_manager)
        self.action_history = []
        self.logger = logging.getLogger(__name__)

        # Track initialization
        self._initialized = False

    def setup_case(self, case_name: str) -> Dict[str, Any]:
        """Setup a specific case configuration"""
        try:
            if case_name == 'Case1':
                # Setup Case1 configuration
                result = self.create_test_network()
                if result.get('status') == 'success':
                    self._initialized = True
                    return {"status": "success", "message": f"Case {case_name} setup successfully"}
                else:
                    return {"status": "error", "message": f"Failed to setup case {case_name}: {result.get('message', 'unknown error')}"}
            else:
                return {"status": "error", "message": f"Unknown case: {case_name}"}
        except Exception as e:
            return {"status": "error", "message": f"Error setting up case {case_name}: {str(e)}"}

    def reset(self, episode_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Reset environment for new episode with optional configuration (RL interface)"""
        # Clear system state
        self.reset_system()

        # If episode_config provided, setup scenario
        if episode_config:
            damage_scenario = episode_config.get('damage_scenario', {})
            num_rc = episode_config.get('num_rc', 2)
            num_mps = episode_config.get('num_mps', 1)
            self.logger.info(f"Reset with config: {num_rc} RC, {num_mps} MPS, {len(damage_scenario.get('damage_edges', []))} damages")

        return self.get_current_state()

    def reset_system(self):
        """Clear environment state using instance-based approach"""
        # Clear environment graphs and time
        self.env.reset()
        self.action_history = []

        # Clear instance-specific agent state
        self.agent_manager.clear_all()

        self._initialized = False

    def create_network(self, nodes: List[Tuple], edges: List[Tuple]) -> Dict[str, Any]:
        """
        Create a network structure with given nodes and edges

        Args:
            nodes: List of tuples (node_id, node_type, voltage)
                   NOTE: voltage parameter currently not used (reserved for future power flow analysis)
            edges: List of tuples (edge_id, from_node, to_node, length)

        Returns:
            Result dictionary with status and message
        """
        try:
            # Add nodes to both graphs
            for node_info in nodes:
                node_id = node_info[0]
                node_type = node_info[1]
                # Read voltage if provided (currently not used, default: 4.16 kV)
                voltage = node_info[2] if len(node_info) > 2 else 4.16

                # Convert string type to NodeType enum if needed
                if isinstance(node_type, str):
                    try:
                        node_type = getattr(NodeType, node_type.upper())
                    except AttributeError:
                        raise ValueError(f"Invalid node type '{node_type}' for node '{node_id}'. "
                                       f"Valid types: {[t.name for t in NodeType]}")

                # Add node to electrical graph
                self.env.egraph.add_node(node_id, node_type)
                # Add node to traffic graph
                self.env.tgraph.add_node(node_id)

            # Add edges to both graphs
            for edge_info in edges:
                edge_id = edge_info[0]
                from_node = edge_info[1]
                to_node = edge_info[2]
                length = int(edge_info[3]) if len(edge_info) > 3 else 1  # Convert to int

                # Handle status field (string 'Closed'/'Opened' or boolean)
                if len(edge_info) > 4:
                    status = edge_info[4]
                    # Convert string status to boolean: 'Closed' -> True, 'Opened' -> False
                    if isinstance(status, str):
                        is_connected = status.lower() == 'closed'
                    else:
                        is_connected = bool(status)
                else:
                    is_connected = True  # Default: connected

                # Add edge to electrical graph with status
                self.env.egraph.add_edge(edge_id, from_node, to_node, is_connected)
                # Add edge to traffic graph (distance must be int)
                self.env.tgraph.add_edge(edge_id, from_node, to_node, length)

            # Update system state
            self.env.egraph.update_system_state()

            return {
                'status': 'success',
                'message': f'Network created with {len(nodes)} nodes and {len(edges)} edges',
                'nodes_count': len(nodes),
                'edges_count': len(edges)
            }

        except Exception as e:
            self.logger.error(f"Error creating network: {e}")
            return {
                'status': 'error',
                'message': f'Failed to create network: {str(e)}'
            }

    def create_test_network(self) -> Dict[str, Any]:
        """Create DSR test network matching DSRSimulator.ipynb (19 nodes, 21 edges)"""
        try:
            # Create complete node set matching notebook (19 nodes total)
            # NOTE: Voltage values (4.16 kV) provided but not used by DSR system
            nodes = []
            nodes.append(('Grid', 'GRID', 4.16))  # Main grid source
            nodes.append(('S1', 'BUS', 4.16))     # Switch node 1
            nodes.append(('S2', 'BUS', 4.16))     # Switch node 2
            nodes.append(('V1', 'BUS', 4.16))     # Virtual node 1
            nodes.append(('V2', 'BUS', 4.16))     # Virtual node 2
            nodes.append(('V3', 'BUS', 4.16))     # Virtual node 3
            nodes.append(('N1', 'BUS', 4.16))     # Junction node
            nodes.append(('N2', 'BUS', 4.16))     # Main junction
            # Load nodes
            for i in range(3, 14):
                nodes.append((f'N{i}', 'LOAD', 4.16))

            # Create 21 edges matching notebook topology
            edges = [
                ('E_Grid_N1', 'Grid', 'N1', 2),
                ('E_N1_N2', 'N1', 'N2', 3),
                ('E_N2_S1', 'N2', 'S1', 1),
                ('E_S1_V1', 'S1', 'V1', 1),
                ('E_V1_N3', 'V1', 'N3', 3),
                ('E_N3_N4', 'N3', 'N4', 4),
                ('E_N4_N5', 'N4', 'N5', 6),
                ('E_N5_N6', 'N5', 'N6', 5),
                ('E_N6_N7', 'N6', 'N7', 8),
                ('E_N2_S2', 'N2', 'S2', 1),
                ('E_S2_V2', 'S2', 'V2', 1),
                ('E_V2_N8', 'V2', 'N8', 4),
                ('E_N8_N9', 'N8', 'N9', 3),
                ('E_N9_N10', 'N9', 'N10', 5),
                ('E_N10_N11', 'N10', 'N11', 6),
                ('E_N2_V3', 'N2', 'V3', 4),
                ('E_V3_N12', 'V3', 'N12', 2),
                ('E_N12_N13', 'N12', 'N13', 4),
                # Normally-open reconfiguration lines
                ('E_N7_N13', 'N7', 'N13', 10),
                ('E_N5_N10', 'N5', 'N10', 10),
                ('E_N11_N13', 'N11', 'N13', 8),
            ]

            # Create network using our create_network method
            result = self.create_network(nodes, edges)

            if result.get('status') != 'success':
                return result

            # Add switches using agent manager with initial states
            # Add switches with initial states
            switch1 = self.agent_manager.add_switch('S1', 'S1', ['E_N2_S1', 'E_S1_V1'], 'close')
            switch2 = self.agent_manager.add_switch('S2', 'S2', ['E_N2_S2', 'E_S2_V2'], 'close')

            # Apply initial switch states
            # allow_faulted=True: force faulted edges to disconnected
            # revert_on_cycle=False: don't revert (config should be valid)
            cycle_info = self.env.update_switch_effects(allow_faulted=True, revert_on_cycle=False)

            # Verify initial topology is valid (no cycles)
            if cycle_info['cycle_detected']:
                raise ValueError(
                    "Invalid initial configuration: Network topology contains a cycle. "
                    "Please adjust switch states in the configuration."
                )

            # Update system state after switch configuration
            self.env.egraph.update_system_state()

            # Add loads using agent manager
            # IMPORTANT: Use L_N format to match envs.py regex and prompt examples
            for i in range(3, 14):
                self.agent_manager.add_load(f'L_N{i}', f'N{i}', P=200.0, Q=100.0, W=1.0)

            self.logger.info(f"Test network created with 19 nodes, 21 edges, 2 switches, 11 loads")

            return {
                "status": "success",
                "message": "Test network created successfully"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create test network: {str(e)}"
            }

    def add_repair_crew(self, rc_id: str, initial_position: str, speed: int = 3,
                       efficiency: float = 4.0, resources: float = 10.0) -> Dict[str, Any]:
        """Add repair crew using agent manager"""
        try:
            # Note: parameter name difference - resources vs total_resources
            rc = self.agent_manager.add_repair_crew(rc_id, initial_position, speed, efficiency, resources)
            self.action_history.append({
                "time": self.env.current_time,
                "action": "add_repair_crew",
                "params": {"rc_id": rc_id, "position": initial_position}
            })
            return {
                "status": "success",
                "message": f"Repair crew {rc_id} added at {initial_position}",
                "rc_id": rc_id
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to add repair crew: {str(e)}"
            }

    def add_mobile_power(self, mps_id: str, initial_position: str, p_limit: int = 1000,
                        s_limit: int = 1200, energy: int = 5000, speed: int = 1) -> Dict[str, Any]:
        """Add mobile power source using agent manager"""
        try:
            mps = self.agent_manager.add_mobile_power_source(mps_id, initial_position,
                                                            float(p_limit), float(s_limit),
                                                            float(energy), speed)

            # Create MPS node in EGraph (always present, even when disconnected)
            self.env.egraph.add_node(mps_id, NodeType.MPS)

            self.action_history.append({
                "time": self.env.current_time,
                "action": "add_mobile_power",
                "params": {"mps_id": mps_id, "position": initial_position}
            })
            return {
                "status": "success",
                "message": f"Mobile power source {mps_id} added at {initial_position}",
                "mps_id": mps_id
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to add mobile power source: {str(e)}"
            }

    def add_fault(self, fault_id: str, location: str, repair_demand: float = 5.0,
                 distance: float = 0.0, capacity: int = 1) -> Dict[str, Any]:
        """Add fault to system using agent manager

        Args:
            fault_id: Unique fault identifier
            location: Fault location (node or edge like "N1-N2")
            repair_demand: Required repair work
            distance: For edge faults, distance from the starting node (km)
            capacity: Maximum number of crews that can work simultaneously (default=1)
        """
        try:
            if "-" in location:
                # Edge fault
                from_node, to_node = location.split("-")
                dp = self.agent_manager.add_damage_point(
                    fault_id, from_node, to_node, distance, repair_demand,
                    fault_node_id=fault_id,  # Use fault_id directly (e.g., "Fault5")
                    capacity=capacity
                )
                # Apply edge fault to graphs
                dp._apply_edge_fault(from_node, to_node, int(distance),
                                    self.env.tgraph, self.env.egraph)
            else:
                # Node fault
                dp = self.agent_manager.add_damage_point(
                    fault_id, location, location, 0, repair_demand,
                    fault_node_id=location,
                    capacity=capacity
                )
                # Apply node fault to graphs
                dp._apply_node_fault(location, self.env.tgraph, self.env.egraph)

            # Recompute power after adding fault
            self.env.egraph.update_system_state()

            self.action_history.append({
                "time": self.env.current_time,
                "action": "add_fault",
                "params": {"fault_id": fault_id, "location": location, "repair_demand": repair_demand}
            })

            return {
                "status": "success",
                "message": f"Fault {fault_id} added at {location}",
                "fault_id": fault_id
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to add fault: {str(e)}"
            }

    def move_repair_crew(self, rc_id: str, target: str) -> Dict[str, Any]:
        """Move repair crew to target location (supports DP auto-conversion)"""
        original_target = target

        # Auto-convert DP format to node location
        if target.upper().startswith('DP'):
            dp = self.agent_manager.get_damage_point(target.upper())
            if dp:
                # For node faults (from_node == to_node), use that node
                if dp.from_node == dp.to_node:
                    target = dp.from_node
                    self.logger.info(f"Auto-converted {original_target} to node {target} (node fault location)")
                else:
                    # For edge faults, use fault_node_id (the exact fault position in traffic graph)
                    # CRITICAL: RC must move to the fault node itself, not just the endpoint!
                    # Edge faults create a fault node in traffic graph (e.g., 'DP2' node on edge N10-N12)
                    if hasattr(dp, 'fault_node_id') and dp.fault_node_id:
                        target = dp.fault_node_id
                        self.logger.info(f"Auto-converted {original_target} to fault node {target} (edge fault location)")
                    else:
                        # Fallback to from_node (shouldn't happen with properly configured edge faults)
                        self.logger.warning(f"Edge fault {original_target} has no fault_node_id, using from_node {dp.from_node}")
                        target = dp.from_node
            else:
                return {
                    "status": "error",
                    "message": f"Damage point {target} not found. Available DPs: {list(self.agent_manager.damage_points.keys())}"
                }

        return self._move_actor("repair_crew", rc_id, target, self.env.tgraph)

    def repair_fault(self, rc_id: str, fault_id: str, auto_repair: bool = False) -> Dict[str, Any]:
        """Repair fault using agent manager"""
        return self._repair_fault(rc_id, fault_id, auto_repair)

    def advance_time(self, force_power_balance: bool = False) -> Dict[str, Any]:
        """Advance simulation time and return events"""
        try:
            # Environment's step() advances time and updates all agents
            env_result = self.env.step()

            events = env_result.get("events", [])

            # NOTE: Repair-induced cycles are now auto-resolved in independent_environment.py step().
            # The event type is 'cycle_auto_resolved_after_repair' (no penalty).

            # Check power balance if requested
            if force_power_balance:
                balance = self.env.check_power_balance()
                if not balance.get('balanced', False):
                    self.logger.warning(f"Power imbalance: {balance}")

            self.action_history.append({
                "time": self.env.current_time,
                "action": "advance_time"
            })

            return {
                "status": "success",
                "time": self.env.current_time,
                "message": f"Time advanced to {self.env.current_time}",
                "events": events
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to advance time: {str(e)}"
            }

    def _get_instantaneous_supply_snapshot(self, refresh: bool = True) -> Dict[str, Dict[str, Any]]:
        """Get per-load instantaneous supply snapshot from electrical topology."""
        snapshot: Dict[str, Dict[str, Any]] = {}

        if hasattr(self.env, 'egraph') and self.env.egraph:
            if refresh and hasattr(self.env.egraph, 'build_supply_snapshot'):
                try:
                    snapshot = self.env.egraph.build_supply_snapshot()
                    self.env.egraph.last_supply_snapshot = snapshot
                except Exception as e:
                    self.logger.debug(f"Failed to rebuild supply snapshot, fallback to cached: {e}")

            if not snapshot:
                snapshot = getattr(self.env.egraph, 'last_supply_snapshot', {}) or {}

        # Ensure all loads are covered (defensive default)
        for load_id in self.agent_manager.loads.keys():
            snapshot.setdefault(load_id, {
                'served_grid_kw': 0.0,
                'served_mps_kw': 0.0,
                'currently_served': False,
                'reason': 'unknown',
            })

        return snapshot

    def get_current_state(self) -> Dict[str, Any]:
        """Get current system state from instance-specific agents"""
        try:
            # Collect repair crew states from agent manager
            repair_crews = {}
            for rc_id, rc in self.agent_manager.repair_crews.items():
                # Calculate ETA based on remaining distance and speed
                eta = rc.remaining_distance / max(rc.speed, 0.1) if rc.remaining_distance > 0 else 0.0

                # Calculate remaining work time (if assigned to a fault)
                remaining_work_time = 0.0
                if rc.auto_repair and rc.last_repair_target:
                    fault = self.agent_manager.get_damage_point(rc.last_repair_target)
                    if fault and fault.state == "active":
                        remaining_work = max(0, fault.repair_demand - fault.repair_progress)
                        remaining_work_time = remaining_work / max(rc.efficiency, 0.1)

                # Get target fault info for reward calculation
                target_fault_id = getattr(rc, 'target_fault', None) or rc.last_repair_target

                repair_crews[rc_id] = {
                    'current_position': rc.current_position,
                    'state': rc.state,
                    'speed': rc.speed,
                    'efficiency': rc.efficiency,
                    'total_resources': rc.total_resources,
                    'remaining_resources': rc.remaining_resources,
                    'target_position': rc.target_position,
                    'remaining_distance': rc.remaining_distance,
                    'eta': eta,
                    'auto_repair': rc.auto_repair,
                    'last_repair_target': rc.last_repair_target,
                    'remaining_work_time': remaining_work_time,
                    'target_fault_id': target_fault_id,  # For reward: _calculate_individual_contribution()
                    'current_fault_id': target_fault_id,  # Alias for compatibility
                    'work_units_contributed': rc.efficiency * 1.0 if rc.state == 'repairing' else 0.0  # Estimate for reward
                }

            # Collect mobile power states from agent manager
            mobile_power = {}
            for mps_id, mps in self.agent_manager.mobile_power_sources.items():
                # Calculate remaining distance for MPS movement
                remaining_distance = getattr(mps, 'remaining_distance', 0.0)

                # Calculate ETA based on remaining distance and speed
                eta = remaining_distance / max(mps.speed, 0.1) if remaining_distance > 0 else 0.0

                mobile_power[mps_id] = {
                    'current_position': mps.current_position,
                    'state': mps.state,
                    'p_limit': mps.p_limit,
                    's_limit': mps.s_limit,
                    'energy': mps.energy,
                    'max_energy': getattr(mps, 'initial_energy', mps.p_limit * 8.0),  # ⭐ v5.0: For grace period calc (assume 8h runtime if not set)
                    'initial_energy': getattr(mps, 'initial_energy', mps.p_limit * 8.0),  # ⭐ v5.0: Backup field
                    'speed': mps.speed,
                    'Pout': mps.Pout,
                    'Qout': mps.Qout,
                    'connected_node': mps.connected_node,  # Node ID where MPS is connected (None if not connected)
                    'target_position': mps.target_position,  # Target node for movement
                    'remaining_distance': remaining_distance,  # Add for reward phi_mps
                    'eta': eta,  # Estimated time of arrival (hours)
                    'target_loads': mps.target_loads,  # List of load IDs this MPS is serving
                    # ⭐ v5.8.1: Add requested power for ratio-based power sharing visibility
                    'P_requested': getattr(mps, 'P_requested', mps.Pout),  # Original LLM request (before projection)
                    'Q_requested': getattr(mps, 'Q_requested', mps.Qout),
                }

            # Collect damage point states from agent manager
            damage_points = {}
            for dp_id, dp in self.agent_manager.damage_points.items():
                damage_points[dp_id] = {
                    'from_node': dp.from_node,
                    'to_node': dp.to_node,
                    'distance': dp.distance,
                    'repair_demand': dp.repair_demand,
                    'repair_progress': dp.repair_progress,
                    'state': dp.state,
                    'fault_node_id': getattr(dp, 'fault_node_id', None),
                    'affected_edge_id': getattr(dp, 'affected_edge_id', None),
                    'capacity': getattr(dp, 'capacity', 1),  # CRITICAL: For parallel repair reward calculation
                    'active_crews': list(getattr(dp, 'active_crews', set())),  # CRITICAL: Show which RCs are currently working
                    'num_active_crews': len(getattr(dp, 'active_crews', set()))  # CRITICAL: Quick count for capacity check
                }

            # Build instantaneous supply map from current topology + source outputs.
            # This keeps observation/reward semantics aligned with the physical simulator.
            supply_snapshot = self._get_instantaneous_supply_snapshot(refresh=True)

            # Collect load states
            loads = {}
            for load_id, load in self.agent_manager.loads.items():
                supply_info = supply_snapshot.get(load_id, {})
                served_grid_kw = max(0.0, float(supply_info.get('served_grid_kw', 0.0) or 0.0))
                served_mps_kw = max(0.0, float(supply_info.get('served_mps_kw', 0.0) or 0.0))

                # Clamp to physical demand
                served_grid_kw = min(float(load.P), served_grid_kw)
                served_mps_kw = min(float(load.P), served_mps_kw)

                instant_served = bool(supply_info.get('currently_served', False))
                if not instant_served:
                    instant_served = (served_grid_kw + served_mps_kw) > 1e-6

                # Monotonic restoration semantics:
                # once restored/powered in this episode, load stays "on" and should not
                # appear as dropped in observation/reward state.
                restored = bool(self.agent_manager.is_load_restored(load_id) or load.state == 'on')
                currently_served = instant_served

                loads[load_id] = {
                    'node_id': load.node_id,
                    'P': load.P,
                    'Q': load.Q,
                    'W': load.W,
                    # Expose monotonic restoration state externally.
                    'state': 'on' if restored else 'off',
                    'restored': restored,
                    'served_grid_kw': served_grid_kw,  # Explicit grid power
                    'served_mps_kw': served_mps_kw,
                    'currently_served': currently_served,
                    'instantly_served': instant_served,  # Physical instantaneous supply
                    'supply_reason': supply_info.get('reason', 'unknown'),
                }

            # Collect switch states
            switches = {}
            for switch_id, switch in self.agent_manager.switches.items():
                switches[switch_id] = {
                    'node_id': switch.node_id,
                    'state': switch.state,
                    'controlled_edges': switch.connected_edges
                }

            # Calculate connectivity information
            islands_count = self.env.count_islands() if hasattr(self.env, 'count_islands') else 0

            # ⭐ v5.1: Add islands_list for MPS coordination reward detection
            # Each island is a set of node IDs that are electrically connected
            islands_list = []
            if hasattr(self.env.egraph, 'identify_islands'):
                islands = self.env.egraph.identify_islands()
                # Convert sets to lists for JSON serialization
                islands_list = [list(island) for island in islands]

            # Collect nodes status for connectivity visualization
            nodes = {}
            if hasattr(self.env, 'egraph') and hasattr(self.env.egraph, 'nodes'):
                for nid, node in self.env.egraph.nodes.items():
                    # Check if node has currently served loads (instantaneous power)
                    has_powered_load = any(
                        load_info.get('node_id') == nid and load_info.get('currently_served', False)
                        for load_info in loads.values()
                    )
                    nodes[nid] = {
                        'type': node.type.name if hasattr(node.type, 'name') else str(node.type),
                        'has_powered_load': has_powered_load  # Whether node has currently served loads
                    }

            # Collect edges status
            # ⭐ v5.9: Include both switch state (is_connected) and fault state (state)
            edges = {}
            if hasattr(self.env, 'egraph') and hasattr(self.env.egraph, 'edges'):
                for eid, edge in self.env.egraph.edges.items():
                    # Determine edge status considering both switch and fault state
                    edge_state = getattr(edge, 'state', 'operational')
                    if edge_state == 'faulted':
                        status = 'faulted'
                    elif not edge.is_connected:
                        status = 'open'  # Switch is open
                    else:
                        status = 'operational'

                    edges[eid] = {
                        'from_node': edge.from_node,
                        'to_node': edge.to_node,
                        'is_connected': edge.is_connected,  # Switch state (True=closed, False=open)
                        'state': edge_state,  # Fault state ('operational' or 'faulted')
                        'status': status  # Combined status for display
                    }

            # Calculate active faults count for grid info
            faults_active = sum(1 for dp in damage_points.values() if dp.get('state') == 'active')

            # Check if topology has a cycle (for time-integrated penalty)
            has_cycle = self.env.egraph.has_cycle() if hasattr(self.env.egraph, 'has_cycle') else False

            # Build grid info with fields needed by reward calculator
            grid_info = self.env.get_system_summary() if hasattr(self.env, 'get_system_summary') else {}
            grid_info.update({
                'faults_active': faults_active,  # Add for reward calculation
                'islands': islands_count,  # Add for reward calculation (duplicated from top level)
                'islands_list': islands_list,  # ⭐ v5.1: List of islands (each island = list of node IDs) for MPS coordination detection
                'violations_count': 0,  # Add placeholder for reward calculation
                'has_cycle': has_cycle,  # Add for cycle existence penalty (time-integrated)
                'supply_failures': getattr(self.env.egraph, 'last_supply_failures', [])  # under-supply diagnostics
            })

            # Count loads currently served (instantaneous power, not monotonic restoration flag)
            serving_count = sum(1 for load_info in loads.values() if load_info.get('currently_served', False))

            # DEBUG: Log serving loads and served power summary
            total_grid_served = sum(load.get('served_grid_kw', 0) for load in loads.values())
            total_mps_served = sum(load.get('served_mps_kw', 0) for load in loads.values())
            connected_mps = [mps_id for mps_id, mps in self.agent_manager.mobile_power_sources.items() if mps.state == 'connected']

            # if self.env.current_time % 5 == 0:  # Log every 5 hours to avoid spam
            #     print(f"[POWER DEBUG] Time={self.env.current_time}h: Serving={serving_count}/{len(loads)} loads, "
            #           f"Grid={total_grid_served:.1f}kW, MPS={total_mps_served:.1f}kW, "
            #           f"Connected_MPS={connected_mps}")

            # Calculate weighted instantaneous serving ratio for observation
            total_weighted_demand = sum(
                float(load_info.get('W', 0.0)) * float(load_info.get('P', 0.0))
                for load_info in loads.values()
            )
            total_weighted_served = sum(
                float(load_info.get('W', 0.0)) * float(load_info.get('P', 0.0))
                for load_info in loads.values()
                if load_info.get('currently_served', False)
            )
            # Ratio [0.0, 1.0] representing priority-weighted restoration progress
            weighted_restoration = (
                total_weighted_served / total_weighted_demand
                if total_weighted_demand > 1e-6 else 0.0
            )

            return {
                'time': self.env.current_time,
                'repair_crews': repair_crews,
                'mobile_power': mobile_power,
                'damage_points': damage_points,
                'loads': loads,
                'switches': switches,
                'islands': islands_count,
                'powered_loads': serving_count,  # Count of instantaneously served loads (legacy field name)
                'total_loads': len(loads),
                'nodes': nodes,  # Add nodes for connectivity visualization
                'edges': edges,  # Add edges for connectivity visualization
                'grid': grid_info,  # Enhanced grid info with reward fields
                'restoration_summary': {  # Add restoration summary for observation
                    'energized_loads': serving_count,  # Same as powered_loads (instantaneous serving count)
                    'total_loads': len(loads),
                    'weighted_restoration': weighted_restoration
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting current state: {e}")
            return {
                'time': self.env.current_time,
                'repair_crews': {},
                'mobile_power': {},
                'damage_points': {},
                'loads': {},
                'switches': {},
                'islands': 0,
                'powered_loads': 0,
                'total_loads': 0,
                'grid': {},
                'restoration_summary': {
                    'energized_loads': 0,
                    'total_loads': 0,
                    'weighted_restoration': 0.0
                },
                'error': str(e)
            }

    # ⚠️ REMOVED in v5.2: connect_mps and disconnect_mps are deprecated
    # Use set_mps_output() for all MPS operations
    # MPS auto-connects when set_mps_output() is called
    # MPS auto-disconnects when energy depletes or grid is restored

    def _validate_mps_projection_dry_run(self, mps_id: str, P_out: float, Q_out: float,
                                         target_loads: List[str], target_island: set) -> Dict[str, Any]:
        """Validate MPS projection without modifying any state (dry-run mode)

        This method performs all validation checks that _project_mps_outputs does,
        but WITHOUT modifying the MPS object's target_loads field.

        Args:
            mps_id: MPS identifier
            P_out: Requested active power
            Q_out: Requested reactive power
            target_loads: List of load IDs to serve
            target_island: Set of node IDs in the target island

        Returns:
            Dictionary with:
            - status: "valid" if all checks pass, "invalid" otherwise
            - P_out_projected: Projected active power (if valid)
            - Q_out_projected: Projected reactive power (if valid)
            - projection_info: Details about projection
            - reason: Failure reason (if invalid)
            - message: Human-readable message
        """
        try:
            # Get MPS object
            mps = self.agent_manager.get_mobile_power_source(mps_id)
            supply_snapshot = self._get_instantaneous_supply_snapshot(refresh=True)

            # Build target_loads_by_mps dict for projection logic
            target_loads_by_mps = {mps_id: set(target_loads)}
            all_target_loads = set(target_loads)

            # ===== v5.8: REMOVED coordination constraint =====
            # Old rule: All MPS in same island MUST use identical target_loads
            # New rule: Each MPS can serve different loads in the same island
            # This enables flexible multi-MPS coordination where each MPS serves different loads
            # Power sharing/renegotiation still works for MPS serving the SAME loads

            # ===== VALIDATION 1: Check if Grid is present in island =====
            # If Grid is in island, MPS is not needed (Grid provides unlimited power)
            has_grid_in_island = False
            for node_id in target_island:
                node = self.env.egraph.nodes.get(node_id)
                if node and node.type == NodeType.GRID:
                    has_grid_in_island = True
                    break

            # ===== VALIDATION 2: Check target_loads relationship with existing MPS =====
            # Collect existing MPS in island
            existing_mps_in_island = {}  # {mps_id: target_loads_set}
            for node_id in target_island:
                node = self.env.egraph.nodes.get(node_id)
                if node and node.type == NodeType.MPS:
                    existing_mps = self.agent_manager.get_mobile_power_source(node_id)
                    if existing_mps and existing_mps.id != mps_id and existing_mps.state == "connected":
                        if existing_mps.target_loads:
                            existing_mps_in_island[existing_mps.id] = set(existing_mps.target_loads)

            # ===== v5.8.1: Validate target_loads relationship =====
            # Rule: IDENTICAL or COMPLETELY DISJOINT, NO partial overlap
            new_tl_set = set(target_loads)
            for existing_id, existing_tl_set in existing_mps_in_island.items():
                if new_tl_set == existing_tl_set:
                    pass  # IDENTICAL - OK (power sharing)
                elif new_tl_set.isdisjoint(existing_tl_set):
                    pass  # DISJOINT - OK (independent)
                else:
                    # PARTIAL OVERLAP - INVALID
                    overlap = new_tl_set & existing_tl_set
                    only_new = new_tl_set - existing_tl_set
                    only_existing = existing_tl_set - new_tl_set
                    return {
                        "status": "invalid",
                        "reason": "partial_overlap_target_loads",
                        "message": f"MPS {mps_id} target_loads partially overlaps with {existing_id}. "
                                  f"Overlap: {list(overlap)}, Only in {mps_id}: {list(only_new)}, Only in {existing_id}: {list(only_existing)}. "
                                  f"Must use IDENTICAL or COMPLETELY DIFFERENT target_loads."
                    }

            # ===== VALIDATION 3: Check load reachability =====
            unreachable_loads = []
            grid_served_loads = []  # Loads served by Grid (not MPS)
            mps_served_loads = []   # Loads already served by other MPS
            total_p_load = 0.0
            total_q_load = 0.0

            # Collect all loads currently served by other MPS in this island
            other_mps_target_loads = set()
            for existing_tl_set in existing_mps_in_island.values():
                other_mps_target_loads.update(existing_tl_set)

            for load_id in target_loads:
                load = self.agent_manager.get_load(load_id)
                if not load:
                    return {
                        "status": "invalid",
                        "reason": "invalid_load_id",
                        "message": f"Load {load_id} not found in target_loads"
                    }

                # Check if load is in the same island
                if load.node_id in target_island:
                    # ⭐ v5.8: Distinguish between Grid-served and MPS-served loads
                    supply_info = supply_snapshot.get(load_id, {})
                    load_currently_served = bool(supply_info.get('currently_served', False))
                    load_grid_served = float(supply_info.get('served_grid_kw', 0.0) or 0.0) > 1e-6

                    if load_currently_served:
                        if load_grid_served:
                            # Load is powered by Grid
                            grid_served_loads.append(load_id)
                        elif load_id in other_mps_target_loads:
                            # Load is already served by another MPS
                            # ⭐ v5.8: Allow this MPS to also serve this load (power sharing)
                            # Count it as a load to serve (will share power with existing MPS)
                            total_p_load += load.P
                            total_q_load += load.Q
                            mps_served_loads.append(load_id)
                        else:
                            # Load is currently served but not in any other MPS target_loads.
                            # Treat as available demand for this MPS setting.
                            total_p_load += load.P
                            total_q_load += load.Q
                        continue

                    # Offline load - count demand
                    total_p_load += load.P
                    total_q_load += load.Q
                else:
                    # Load not reachable
                    unreachable_loads.append(load_id)

            # Reject if any loads unreachable
            if unreachable_loads:
                return {
                    "status": "invalid",
                    "reason": "loads_not_reachable",
                    "message": f"MPS {mps_id} cannot reach loads {unreachable_loads}. "
                              f"These loads are not in the same electrical island. "
                              f"MPS can only serve loads reachable through closed switches and repaired lines."
                }

            # ⭐ v5.8: Only reject if Grid is serving these loads (MPS truly not needed)
            # If loads are served by other MPS, allow power sharing
            if total_p_load == 0 and total_q_load == 0:
                if grid_served_loads:
                    return {
                        "status": "invalid",
                        "reason": "all_loads_grid_served",
                        "message": f"All target loads {grid_served_loads} are already served by Grid. MPS not needed."
                    }

            # ===== VALIDATION 3: Calculate projection (v5.8.1 Ratio-Based Power Sharing) =====
            # ⭐ v5.8.1: Project based on REQUESTED POWER RATIO
            # When multiple MPS target the same loads, they share based on their requested P ratio
            # Example: MPS1 requests 700kW, MPS2 requests 300kW for same loads
            #          -> MPS1 gets 70% of demand, MPS2 gets 30%
            import math

            # Build info for all MPS (existing + this one): {mps_id: (target_loads_set, P_requested)}
            all_mps_info = {}  # {mps_id: (target_loads_set, P_requested, Q_requested)}
            for existing_id, existing_tl_set in existing_mps_in_island.items():
                # Get existing MPS's requested power
                existing_mps_obj = self.agent_manager.get_mobile_power_source(existing_id)
                if existing_mps_obj:
                    p_req = getattr(existing_mps_obj, 'P_requested', existing_mps_obj.Pout)
                    q_req = getattr(existing_mps_obj, 'Q_requested', existing_mps_obj.Qout)
                    all_mps_info[existing_id] = (existing_tl_set, p_req, q_req)
            # Add this MPS being set
            all_mps_info[mps_id] = (set(target_loads), P_out, Q_out)

            num_mps_total = len(all_mps_info)

            # Calculate per-load demand
            load_demands = {}  # {load_id: (P, Q)}
            for load_id in target_loads:
                if load_id in grid_served_loads:
                    continue  # Skip Grid-served loads
                load = self.agent_manager.get_load(load_id)
                if load and load.node_id in target_island:
                    load_demands[load_id] = (load.P, load.Q)

            # For each load, calculate total requested P from all MPS serving it
            # Then this MPS's share = (this_mps_P_requested / total_P_requested) * load_demand
            my_p_demand = 0.0
            my_q_demand = 0.0

            for load_id in target_loads:
                if load_id not in load_demands:
                    continue
                p_load, q_load = load_demands[load_id]

                # Find all MPS serving this load and sum their requested P
                total_p_requested_for_load = 0.0
                total_q_requested_for_load = 0.0
                for other_mps_id, (other_tl_set, other_p_req, other_q_req) in all_mps_info.items():
                    if load_id in other_tl_set:
                        total_p_requested_for_load += other_p_req
                        total_q_requested_for_load += other_q_req

                # This MPS's share based on its requested P ratio
                if total_p_requested_for_load > 0:
                    my_p_ratio_for_load = P_out / total_p_requested_for_load
                else:
                    my_p_ratio_for_load = 1.0  # Only MPS serving this load

                if total_q_requested_for_load > 0:
                    my_q_ratio_for_load = Q_out / total_q_requested_for_load
                else:
                    my_q_ratio_for_load = 1.0

                my_p_demand += p_load * my_p_ratio_for_load
                my_q_demand += q_load * my_q_ratio_for_load

            # Project output to match this MPS's share of demand
            P_out_projected_raw = my_p_demand
            Q_out_projected_raw = my_q_demand

            # Calculate overall ratio for logging
            p_ratio = my_p_demand / total_p_load if total_p_load > 0 else 0
            q_ratio = my_q_demand / total_q_load if total_q_load > 0 else 0

            # Sum of all requested power (for logging)
            sum_p_requested = sum(p_req for _, p_req, _ in all_mps_info.values())
            sum_q_requested = sum(q_req for _, _, q_req in all_mps_info.values())

            # ⭐ v5.4.1: NEW - Clip to MPS capacity limits
            # Ensure projected output does not exceed physical MPS capacity
            P_out_projected = min(P_out_projected_raw, float(mps.p_limit))

            # Check S_limit (apparent power constraint)
            S_out_projected = math.sqrt(P_out_projected**2 + Q_out_projected_raw**2)
            if S_out_projected > mps.s_limit:
                # Scale down both P and Q proportionally to satisfy S_limit
                scale_factor = float(mps.s_limit) / S_out_projected
                P_out_projected = P_out_projected * scale_factor
                Q_out_projected = Q_out_projected_raw * scale_factor
            else:
                Q_out_projected = Q_out_projected_raw

            # Log if clipping occurred
            clipped = (P_out_projected < P_out_projected_raw - 0.1) or (S_out_projected > mps.s_limit)
            if clipped:
                S_final = math.sqrt(P_out_projected**2 + Q_out_projected**2)
                self.logger.info(
                    f"MPS {mps_id} output will be clipped to capacity: "
                    f"P {P_out_projected_raw:.1f}→{P_out_projected:.1f}kW (limit {mps.p_limit}kW), "
                    f"S {S_out_projected:.1f}→{S_final:.1f}kVA (limit {mps.s_limit}kVA)"
                )

            return {
                "status": "valid",
                "P_out_projected": P_out_projected,
                "Q_out_projected": Q_out_projected,
                "projection_info": {
                    "projected": True,
                    "island_demand": {"P": total_p_load, "Q": total_q_load},
                    "num_mps_total": num_mps_total,
                    "llm_requested_sum": {"P": sum_p_requested, "Q": sum_q_requested},
                    "this_mps_ratio": {"P": p_ratio, "Q": q_ratio},
                    "P_requested": P_out,
                    "Q_requested": Q_out,
                    "clipped_to_capacity": clipped,  # ⭐ v5.4.1
                    "mps_capacity": {"P": float(mps.p_limit), "S": float(mps.s_limit)}  # ⭐ v5.4.1
                }
            }

        except Exception as e:
            self.logger.error(f"Exception in _validate_mps_projection_dry_run: {str(e)}")
            return {
                "status": "invalid",
                "reason": "exception",
                "message": f"Validation exception: {str(e)}"
            }

    def _project_mps_outputs(self, mps_outputs: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Project MPS outputs to satisfy island power balance automatically (v5.5 Renegotiation Mode)

        ⭐ v5.5 RENEGOTIATION MODE:
        - When new MPS joins island, ALL existing MPS re-project proportionally
        - Uses P_requested/Q_requested (not Pout) to preserve LLM's intended ratios
        - Ensures consistent behavior for sync (same step) and async (different steps) operations

        This method calculates the island's total load demand and projects ALL MPS
        (existing + being set) proportionally to match the exact demand. This guarantees
        feasible solutions and simplifies learning.

        Args:
            mps_outputs: List of MPS output requests with mps_id, P_out, Q_out

        Returns:
            Tuple of (projected_outputs, projection_info):
            - projected_outputs: List of projected MPS outputs with actual P/Q values
            - projection_info: Dict with projection details (ratios, demand, renegotiated MPS, etc.)
        """
        try:
            # Get all MPS objects and determine which island they belong to
            mps_objects = {}
            mps_nodes = set()
            supply_snapshot = self._get_instantaneous_supply_snapshot(refresh=True)

            for item in mps_outputs:
                mps_id = item["mps_id"]
                mps = self.agent_manager.get_mobile_power_source(mps_id)
                if not mps or mps.state != "connected":
                    # Cannot project if MPS not connected
                    return mps_outputs, {"projected": False, "reason": "mps_not_connected"}

                mps_objects[mps_id] = mps
                mps_nodes.add(mps.connected_node)  # Use connected_node (not current_position)

            # Find the island containing these MPS
            # IMPORTANT: All MPS must be in the same island for projection to work
            islands = self.env.egraph.identify_islands()
            target_island = None

            for island in islands:
                if all(node in island for node in mps_nodes):
                    # All MPS nodes are in this island
                    target_island = island
                    break

            if not target_island:
                # MPS are in different islands or island not found
                # Cannot project across islands - use original values
                return mps_outputs, {"projected": False, "reason": "mps_in_different_islands"}

            # Calculate total load demand based on MPS target_loads
            total_p_load = 0.0
            total_q_load = 0.0

            # Collect all target loads from MPS being set
            all_target_loads = set()
            target_loads_by_mps = {}  # Track each MPS's target_loads for coordination check

            for item in mps_outputs:
                mps_id = item["mps_id"]
                mps = mps_objects[mps_id]

                if mps.target_loads:
                    # MPS has specified target loads
                    all_target_loads.update(mps.target_loads)
                    target_loads_by_mps[mps_id] = set(mps.target_loads)
                else:
                    # MPS has no target_loads specified -> error
                    return mps_outputs, {
                        "projected": False,
                        "reason": f"mps_{mps_id}_no_target_loads",
                        "message": f"MPS {mps_id} has no target_loads specified. Must specify target_loads when connecting."
                    }

            # ===== v5.8.1: COORDINATION CONSTRAINT - Same Island MPS Rules =====
            # Rule: MPS in same island must have either:
            #   1. IDENTICAL target_loads (power sharing mode)
            #   2. COMPLETELY DISJOINT target_loads (independent mode)
            # Partial overlap is INVALID (too complex, confusing for LLM)

            # Check if Grid is in island (if yes, MPS not needed)
            has_grid_in_island = False
            for node_id in target_island:
                node = self.env.egraph.nodes.get(node_id)
                if node and node.type == NodeType.GRID:
                    has_grid_in_island = True
                    break

            # Collect all existing connected MPS in island (not being modified)
            mps_ids_being_set = {item["mps_id"] for item in mps_outputs}
            existing_mps_in_island = {}  # {mps_id: (mps_object, target_loads_set)}

            for node_id in target_island:
                node = self.env.egraph.nodes.get(node_id)
                if node and node.type == NodeType.MPS:
                    existing_mps = self.agent_manager.get_mobile_power_source(node_id)
                    if existing_mps and existing_mps.state == "connected" and existing_mps.id not in mps_ids_being_set:
                        if existing_mps.target_loads:
                            existing_mps_in_island[existing_mps.id] = (existing_mps, set(existing_mps.target_loads))

            # ===== v5.8.1: Validate target_loads relationship =====
            # Check new MPS against existing MPS in same island
            for new_mps_id, new_tl_set in target_loads_by_mps.items():
                for existing_id, (existing_mps, existing_tl_set) in existing_mps_in_island.items():
                    # Check relationship: identical, disjoint, or partial overlap
                    if new_tl_set == existing_tl_set:
                        # IDENTICAL - OK (power sharing)
                        pass
                    elif new_tl_set.isdisjoint(existing_tl_set):
                        # DISJOINT - OK (independent)
                        pass
                    else:
                        # PARTIAL OVERLAP - INVALID
                        overlap = new_tl_set & existing_tl_set
                        only_new = new_tl_set - existing_tl_set
                        only_existing = existing_tl_set - new_tl_set
                        return mps_outputs, {
                            "projected": False,
                            "reason": "partial_overlap_target_loads",
                            "message": f"MPS {new_mps_id} target_loads partially overlaps with {existing_id}. "
                                      f"Overlap: {overlap}, Only in {new_mps_id}: {only_new}, Only in {existing_id}: {only_existing}. "
                                      f"Must use IDENTICAL or COMPLETELY DIFFERENT target_loads."
                        }

            # Also check among new MPS being set together
            new_mps_list = list(target_loads_by_mps.items())
            for i in range(len(new_mps_list)):
                for j in range(i + 1, len(new_mps_list)):
                    mps_id_1, tl_set_1 = new_mps_list[i]
                    mps_id_2, tl_set_2 = new_mps_list[j]
                    if tl_set_1 == tl_set_2:
                        pass  # IDENTICAL - OK
                    elif tl_set_1.isdisjoint(tl_set_2):
                        pass  # DISJOINT - OK
                    else:
                        # PARTIAL OVERLAP - INVALID
                        overlap = tl_set_1 & tl_set_2
                        return mps_outputs, {
                            "projected": False,
                            "reason": "partial_overlap_target_loads",
                            "message": f"MPS {mps_id_1} and {mps_id_2} have partially overlapping target_loads. "
                                      f"Overlap: {overlap}. Must use IDENTICAL or COMPLETELY DIFFERENT target_loads."
                        }

            # Validate each MPS's target_loads individually
            unreachable_loads = []
            grid_served_loads = []

            for load_id in all_target_loads:
                load = self.agent_manager.get_load(load_id)
                if not load:
                    return mps_outputs, {
                        "projected": False,
                        "reason": "invalid_load_id",
                        "message": f"Load {load_id} not found in target_loads"
                    }

                if load.node_id in target_island:
                    # Check if Grid is serving this load (Grid takes priority)
                    load_grid_served = float(supply_snapshot.get(load_id, {}).get('served_grid_kw', 0.0) or 0.0) > 1e-6
                    if has_grid_in_island and load_grid_served:
                        grid_served_loads.append(load_id)
                else:
                    unreachable_loads.append(load_id)

            if unreachable_loads:
                first_mps_id = list(target_loads_by_mps.keys())[0]
                mps = mps_objects[first_mps_id]
                return mps_outputs, {
                    "projected": False,
                    "reason": "loads_not_reachable",
                    "message": f"MPS {first_mps_id} at node {mps.connected_node} cannot reach loads {unreachable_loads}. "
                              f"These loads are not in the same electrical island."
                }

            # ⭐ v5.8: Calculate demand PER LOAD (for individual MPS projection)
            load_demands = {}  # {load_id: (P, Q)}
            for load_id in all_target_loads:
                if load_id in grid_served_loads:
                    continue  # Skip Grid-served loads
                load = self.agent_manager.get_load(load_id)
                if load and load.node_id in target_island:
                    # For loads already MPS-served, still count full demand for sharing/renegotiation
                    load_demands[load_id] = (load.P, load.Q)

            # Calculate total load demand across all target_loads
            total_p_load = sum(p for p, q in load_demands.values())
            total_q_load = sum(q for p, q in load_demands.values())

            if total_p_load == 0 and total_q_load == 0:
                if grid_served_loads:
                    return mps_outputs, {
                        "projected": False,
                        "reason": "all_loads_grid_served",
                        "message": f"All target loads {grid_served_loads} are already served by Grid. MPS not needed."
                    }
                else:
                    return mps_outputs, {"projected": False, "reason": "no_load"}

            # ===== v5.8.2: Ratio-based power sharing (aligned with dry-run + renegotiation) =====
            # Build unified mapping for ALL MPS in island (existing + new being set)
            all_target_loads_by_mps = {}
            all_requested_by_mps = {}  # {mps_id: (P_requested, Q_requested)}

            for existing_id, (existing_mps, existing_tl_set) in existing_mps_in_island.items():
                all_target_loads_by_mps[existing_id] = set(existing_tl_set)
                all_requested_by_mps[existing_id] = (
                    max(0.0, float(getattr(existing_mps, 'P_requested', existing_mps.Pout) or 0.0)),
                    max(0.0, float(getattr(existing_mps, 'Q_requested', existing_mps.Qout) or 0.0)),
                )

            for item in mps_outputs:
                mps_id = item["mps_id"]
                all_target_loads_by_mps[mps_id] = set(target_loads_by_mps.get(mps_id, set()))
                all_requested_by_mps[mps_id] = (
                    max(0.0, float(item.get("P_requested", item["P_out"]) or 0.0)),
                    max(0.0, float(item.get("Q_requested", item["Q_out"]) or 0.0)),
                )

            all_mps_in_island = list(all_requested_by_mps.items())

            # ===== v5.8.2: Per-MPS Projection based on requested-power ratio =====
            # For each load, share demand by P_requested/Q_requested ratio among MPS targeting that load

            import math
            num_mps_total = len(all_mps_in_island)
            projected_outputs = []
            projection_ratios = {}

            for item in mps_outputs:
                mps_id = item["mps_id"]
                p_requested, q_requested = all_requested_by_mps.get(mps_id, (0.0, 0.0))
                mps = mps_objects[mps_id]
                my_target_loads = target_loads_by_mps.get(mps_id, set())

                # Calculate this MPS's share of demand based on its target_loads
                my_p_demand = 0.0
                my_q_demand = 0.0

                for load_id in my_target_loads:
                    if load_id in load_demands:
                        p_load, q_load = load_demands[load_id]

                        serving_mps_ids = [mid for mid, tl_set in all_target_loads_by_mps.items() if load_id in tl_set]
                        total_p_requested_for_load = sum(all_requested_by_mps[mid][0] for mid in serving_mps_ids)
                        total_q_requested_for_load = sum(all_requested_by_mps[mid][1] for mid in serving_mps_ids)
                        num_serving = max(len(serving_mps_ids), 1)

                        if total_p_requested_for_load > 1e-6:
                            my_p_ratio = p_requested / total_p_requested_for_load
                        else:
                            my_p_ratio = 1.0 / num_serving

                        if total_q_requested_for_load > 1e-6:
                            my_q_ratio = q_requested / total_q_requested_for_load
                        else:
                            my_q_ratio = 1.0 / num_serving

                        my_p_demand += p_load * my_p_ratio
                        my_q_demand += q_load * my_q_ratio

                # Project output to match this MPS's share of demand
                # Use the requested ratio to scale if multiple MPS share loads
                if my_p_demand == 0:
                    p_projected_raw = 0.0
                else:
                    p_projected_raw = my_p_demand

                if my_q_demand == 0:
                    q_projected_raw = 0.0
                else:
                    q_projected_raw = my_q_demand

                # ⭐ v5.4.1: Clip to MPS capacity limits
                p_projected = min(p_projected_raw, float(mps.p_limit))

                # Clip S to s_limit (apparent power constraint)
                s_projected = math.sqrt(p_projected**2 + q_projected_raw**2)
                if s_projected > mps.s_limit:
                    scale_factor = float(mps.s_limit) / s_projected
                    p_projected = p_projected * scale_factor
                    q_projected = q_projected_raw * scale_factor
                else:
                    q_projected = q_projected_raw

                # Log if clipping occurred
                clipped = (p_projected < p_projected_raw - 0.1) or (s_projected > mps.s_limit)
                if clipped:
                    s_final = math.sqrt(p_projected**2 + q_projected**2)
                    self.logger.info(
                        f"MPS {mps_id} output clipped to capacity: "
                        f"P {p_projected_raw:.1f}→{p_projected:.1f}kW (limit {mps.p_limit}kW), "
                        f"S {s_projected:.1f}→{s_final:.1f}kVA (limit {mps.s_limit}kVA)"
                    )

                projected_outputs.append({
                    "mps_id": mps_id,
                    "P_out": p_projected,
                    "Q_out": q_projected,
                    "P_requested": p_requested,
                    "Q_requested": q_requested,
                    "clipped": clipped,
                    "my_target_loads": list(my_target_loads),
                    "my_demand": {"P": my_p_demand, "Q": my_q_demand}
                })

                # Calculate ratio for logging
                p_ratio = my_p_demand / total_p_load if total_p_load > 0 else 0
                q_ratio = my_q_demand / total_q_load if total_q_load > 0 else 0
                projection_ratios[mps_id] = {"P_ratio": p_ratio, "Q_ratio": q_ratio}

            # ⭐ v5.8: RENEGOTIATION - Update existing connected MPS in the same island
            # When new MPS joins, existing MPS are re-projected based on their OWN target_loads
            # Each MPS serves its own target_loads, sharing demand for overlapping loads
            renegotiated_mps = []
            sum_p_requested = 0.0  # For logging only
            sum_q_requested = 0.0  # For logging only

            for item in mps_outputs:
                sum_p_requested += item.get("P_requested", item["P_out"])
                sum_q_requested += item.get("Q_requested", item["Q_out"])

            for node_id in target_island:
                node = self.env.egraph.nodes.get(node_id)
                if node and node.type == NodeType.MPS:
                    existing_mps = self.agent_manager.get_mobile_power_source(node_id)
                    if existing_mps and existing_mps.state == "connected" and existing_mps.id not in mps_ids_being_set:
                        # This MPS is already connected and not being set in this call
                        # ⭐ v5.8: Re-project based on its OWN target_loads
                        existing_target_loads = set(getattr(existing_mps, 'target_loads', []) or [])

                        # Calculate existing MPS's share of demand
                        existing_p_demand = 0.0
                        existing_q_demand = 0.0

                        for load_id in existing_target_loads:
                            if load_id in load_demands:
                                p_load, q_load = load_demands[load_id]

                                serving_mps_ids = [mid for mid, tl_set in all_target_loads_by_mps.items() if load_id in tl_set]
                                total_p_requested_for_load = sum(all_requested_by_mps[mid][0] for mid in serving_mps_ids)
                                total_q_requested_for_load = sum(all_requested_by_mps[mid][1] for mid in serving_mps_ids)
                                num_serving = max(len(serving_mps_ids), 1)

                                my_p_req = all_requested_by_mps.get(existing_mps.id, (0.0, 0.0))[0]
                                my_q_req = all_requested_by_mps.get(existing_mps.id, (0.0, 0.0))[1]

                                if total_p_requested_for_load > 1e-6:
                                    p_ratio_existing_load = my_p_req / total_p_requested_for_load
                                else:
                                    p_ratio_existing_load = 1.0 / num_serving

                                if total_q_requested_for_load > 1e-6:
                                    q_ratio_existing_load = my_q_req / total_q_requested_for_load
                                else:
                                    q_ratio_existing_load = 1.0 / num_serving

                                existing_p_demand += p_load * p_ratio_existing_load
                                existing_q_demand += q_load * q_ratio_existing_load

                        # Project to match this MPS's share of demand
                        p_projected_existing_raw = existing_p_demand
                        q_projected_existing_raw = existing_q_demand

                        # Clip to capacity
                        p_projected_existing = min(p_projected_existing_raw, float(existing_mps.p_limit))
                        s_projected_existing = math.sqrt(p_projected_existing**2 + q_projected_existing_raw**2)
                        if s_projected_existing > existing_mps.s_limit:
                            scale_factor = float(existing_mps.s_limit) / s_projected_existing
                            p_projected_existing = p_projected_existing * scale_factor
                            q_projected_existing = q_projected_existing_raw * scale_factor
                        else:
                            q_projected_existing = q_projected_existing_raw

                        # Update existing MPS output (renegotiation)
                        existing_mps.Pout = p_projected_existing
                        existing_mps.Qout = q_projected_existing

                        # Log renegotiation
                        renegotiated_mps.append(existing_mps.id)
                        p_ratio_existing = existing_p_demand / total_p_load if total_p_load > 0 else 0
                        self.logger.info(
                            f"Renegotiation: {existing_mps.id} re-projected to "
                            f"P={p_projected_existing:.1f}kW, Q={q_projected_existing:.1f}kVar "
                            f"(own demand: P={existing_p_demand:.1f}kW, ratio: {p_ratio_existing:.1%})"
                        )

                        # Add to sum for logging
                        sum_p_requested += getattr(existing_mps, 'P_requested', existing_mps.Pout)
                        sum_q_requested += getattr(existing_mps, 'Q_requested', existing_mps.Qout)

            projection_info = {
                "projected": True,
                "island_demand": {"P": total_p_load, "Q": total_q_load},
                "num_mps_total": num_mps_total,
                "num_mps_being_set": len(mps_outputs),
                "num_mps_renegotiated": len(renegotiated_mps),
                "renegotiated_mps": renegotiated_mps,
                "llm_requested_sum": {"P": sum_p_requested, "Q": sum_q_requested},
                "projection_ratios": projection_ratios
            }

            return projected_outputs, projection_info

        except Exception as e:
            self.logger.warning(f"Projection failed: {e}, using original outputs")
            return mps_outputs, {"projected": False, "reason": f"exception: {str(e)}"}

    def set_mps_output(self, mps_id: str, P_out: float, Q_out: float, target_loads: List[str]) -> Dict[str, Any]:
        """Set MPS output with auto-connect and target loads (LLM action) - v5.2 Fixed

        ⭐ v5.2 CRITICAL FIX:
        - All validations (coordination, reachability, projection) happen BEFORE any state modification
        - No rollback logic needed - operations are atomic (validate-then-execute)
        - Fixed bug where failed operations left MPS in inconsistent state

        ⭐ v5.1 SIMPLIFICATION:
        - If MPS is idle, automatically connects to current position
        - target_loads parameter is REQUIRED (no more separate connect_mps action)
        - Can change target_loads at any time by calling this function

        AUTOMATIC PROJECTION: The P/Q values are automatically projected to satisfy power balance.
        - Single MPS: Projected to match 100% of island load
        - Multiple MPS: Projected proportionally based on the ratio you specify
        This simplifies learning by guaranteeing feasible solutions.

        Workflow:
        1. Move MPS to target location: move_mps(mps_id, node_id)
        2. Set output (auto-connects + sets target_loads + sets power):
           set_mps_output(mps_id, P, Q, target_loads=[...])

        To change which loads an MPS serves, simply call this function again with new target_loads.

        Args:
            mps_id: MPS identifier (e.g., "MPS1")
            P_out: Active power output in kW (ratio indicator, will be projected)
            Q_out: Reactive power output in kVar (ratio indicator, will be projected)
            target_loads: List of load IDs to serve (e.g., ['L_N3', 'L_N4']) - REQUIRED

        Returns:
            Dictionary with:
            - status: "success" if constraints satisfied, "invalid" if violated, "error" if MPS not found
            - message: Detailed explanation
            - P_out_projected: Actual P value after projection
            - Q_out_projected: Actual Q value after projection
            - projection_info: Details about projection (if applied)
            - reason: Specific constraint violation code (if invalid)

        Example:
            # 2-step workflow: move + set_output (auto-connects)
            interface.move_mps("MPS1", "N15")
            interface.set_mps_output("MPS1", P_out=100, Q_out=60, target_loads=['L_N15', 'L_N16'])

            # Change which loads MPS1 serves (1-step, no disconnect needed)
            interface.set_mps_output("MPS1", P_out=80, Q_out=48, target_loads=['L_N3', 'L_N4'])
        """
        try:
            # Get MPS from agent manager
            mps = self.agent_manager.get_mobile_power_source(mps_id)

            if not mps:
                return {
                    "status": "error",
                    "message": f"MPS {mps_id} not found"
                }

            # ===== PHASE 1: PRE-VALIDATION (NO STATE MODIFICATION) =====

            # 1.1 Determine target island without modifying state
            if mps.state == "idle":
                # MPS will connect to current position
                connection_node = mps.current_position
            elif mps.state == "connected":
                # MPS already connected
                connection_node = mps.connected_node
            else:
                # MPS is moving or out of service
                return {
                    "status": "invalid",
                    "message": f"MPS {mps_id} must be idle or connected to set output (current state: {mps.state})",
                    "reason": "invalid_state",
                    "mps_id": mps_id
                }

            # Validate connection node exists
            if connection_node not in self.env.egraph.nodes:
                return {
                    "status": "invalid",
                    "message": f"Connection node {connection_node} not found in electrical graph",
                    "reason": "invalid_node",
                    "mps_id": mps_id
                }

            # MILP alignment: MPS cannot connect on switch nodes
            connection_node_obj = self.env.egraph.nodes.get(connection_node)
            if connection_node_obj and connection_node_obj.type == NodeType.SWITCH:
                return {
                    "status": "invalid",
                    "message": f"MPS {mps_id} cannot connect to switch node {connection_node}. "
                               f"Move to a non-switch node and call set_mps_output again.",
                    "reason": "switch_node_forbidden",
                    "mps_id": mps_id,
                    "node_id": connection_node
                }

            # MILP alignment: MPS cannot connect on unrepaired node-fault nodes
            for dp in self.agent_manager.damage_points.values():
                if dp.from_node == connection_node and dp.to_node == connection_node and dp.state != 'repaired':
                    return {
                        "status": "invalid",
                        "message": f"MPS {mps_id} cannot connect to node {connection_node}: "
                                   f"node fault {dp.id} is still active.",
                        "reason": "fault_node_unrepaired",
                        "mps_id": mps_id,
                        "node_id": connection_node,
                        "fault_id": dp.id
                    }

            # Get island for this connection point
            # Use _dfs_connected_component to find the island containing connection_node
            target_island = self.env.egraph._dfs_connected_component(connection_node, set())

            # 1.2 Validate target_loads parameter
            if not target_loads or len(target_loads) == 0:
                return {
                    "status": "invalid",
                    "message": f"MPS {mps_id} requires target_loads to be specified. "
                              f"Example: set_mps_output('{mps_id}', {P_out}, {Q_out}, target_loads=['L_N3', 'L_N4'])",
                    "reason": "no_target_loads",
                    "mps_id": mps_id
                }

            # Physical sanity check: negative active power request is invalid
            # (kept consistent with MPS.set_output P>=0 constraint and MILP pS >= 0)
            if float(P_out) < 0:
                return {
                    "status": "invalid",
                    "message": f"MPS {mps_id}: P_out={P_out} violates constraint P >= 0",
                    "reason": "p_negative",
                    "mps_id": mps_id,
                    "P_out": P_out
                }

            # 1.3 Pre-validate projection (dry-run mode without state modification)
            # Call projection with simulated target_loads
            validation_result = self._validate_mps_projection_dry_run(
                mps_id=mps_id,
                P_out=P_out,
                Q_out=Q_out,
                target_loads=target_loads,
                target_island=target_island
            )

            # If validation failed, return immediately (no state was modified)
            if validation_result["status"] != "valid":
                return {
                    "status": "invalid",
                    "message": validation_result.get("message", "Projection validation failed"),
                    "reason": validation_result.get("reason", "projection_failed"),
                    "mps_id": mps_id,
                    "projection_info": validation_result.get("projection_info", {})
                }

            # Extract validated projection results
            P_out_final = validation_result["P_out_projected"]
            Q_out_final = validation_result["Q_out_projected"]
            projection_info = validation_result["projection_info"]

            # ===== PHASE 2: ATOMIC EXECUTION (ALL VALIDATIONS PASSED) =====

            # 2.1 Connect MPS if needed (now safe to modify state)
            if mps.state == "idle":
                success = mps.connect(self.env.egraph, target_loads=target_loads)
                if not success:
                    # This should not happen since we validated above, but handle defensively
                    return {
                        "status": "error",
                        "message": f"MPS {mps_id} failed to connect at {mps.current_position} (unexpected error after validation)",
                        "reason": "connect_failed",
                        "mps_id": mps_id
                    }
                self.logger.info(f"MPS {mps_id} auto-connected to {mps.current_position}")

            # 2.2 Set output power and target loads
            result = mps.set_output(P_out_final, Q_out_final, target_loads=target_loads, egraph=self.env.egraph)

            # ⭐ v5.8.1: Store ORIGINAL requested values (before projection) for ratio-based renegotiation
            # This ensures that when new MPS joins, power is shared based on LLM's original requests
            mps.P_requested = P_out  # Original LLM request, not projected value
            mps.Q_requested = Q_out

            # Add projection info to result
            result["P_out_projected"] = P_out_final
            result["Q_out_projected"] = Q_out_final
            result["projection_info"] = projection_info

            # 2.3 If successful, update system state and record action
            if result["status"] == "success":
                # ⭐ v5.8.1: Renegotiate other MPS in same island
                # Re-calculate island AFTER connection (MPS node is now in the graph)
                updated_island = self.env.egraph._dfs_connected_component(connection_node, set())
                self._renegotiate_island_mps(mps_id, updated_island, target_loads)

                # Update system state to reflect new power output
                self.env.egraph.update_system_state()

                # Record action in history
                self.action_history.append({
                    "time": self.env.current_time,
                    "action": "set_mps_output",
                    "params": {
                        "mps_id": mps_id,
                        "P_out": P_out,
                        "Q_out": Q_out,
                        "P_out_projected": P_out_final,
                        "Q_out_projected": Q_out_final,
                        "target_loads": target_loads
                    }
                })

            return result

        except Exception as e:
            self.logger.error(f"Exception in set_mps_output: {str(e)}")
            return {"status": "error", "message": f"Exception in set_mps_output: {str(e)}"}

    def _renegotiate_island_mps(self, new_mps_id: str, target_island: set, new_target_loads: List[str]) -> None:
        """Renegotiate power output for all MPS in the same island when a new MPS joins.

        v5.8.1: When a new MPS sets output, existing MPS in the same island need to
        re-project their output based on the new power sharing arrangement.
        Power is shared based on REQUESTED POWER RATIO, not equally.

        Args:
            new_mps_id: ID of the MPS that just set its output
            target_island: Set of node IDs in the target island
            new_target_loads: Target loads of the new MPS (unused but kept for API compatibility)
        """
        import math

        # Collect all connected MPS in island: {mps_id: (mps_object, target_loads_set, P_requested)}
        all_mps_info = {}

        for node_id in target_island:
            node = self.env.egraph.nodes.get(node_id)
            if node and node.type == NodeType.MPS:
                mps = self.agent_manager.get_mobile_power_source(node_id)
                if mps and mps.state == "connected" and mps.target_loads:
                    p_req = getattr(mps, 'P_requested', mps.Pout)
                    q_req = getattr(mps, 'Q_requested', mps.Qout)
                    all_mps_info[mps.id] = (mps, set(mps.target_loads), p_req, q_req)

        # If only one MPS, no renegotiation needed
        if len(all_mps_info) <= 1:
            return

        # Calculate load demand for each load
        load_demands = {}  # {load_id: (P, Q)}
        all_target_loads_set = set()
        for mps_id, (mps, tl_set, _, _) in all_mps_info.items():
            all_target_loads_set.update(tl_set)

        for load_id in all_target_loads_set:
            load = self.agent_manager.get_load(load_id)
            if load and load.node_id in target_island:
                load_demands[load_id] = (load.P, load.Q)

        # Re-project each MPS (except the new one which was just projected)
        for mps_id, (mps, my_target_loads, my_p_req, my_q_req) in all_mps_info.items():
            if mps_id == new_mps_id:
                continue  # Skip the new MPS, it was just projected

            # Calculate this MPS's share of demand based on REQUESTED POWER RATIO
            my_p_demand = 0.0
            my_q_demand = 0.0

            for load_id in my_target_loads:
                if load_id not in load_demands:
                    continue
                p_load, q_load = load_demands[load_id]

                # Sum requested P from all MPS serving this load
                total_p_requested_for_load = 0.0
                total_q_requested_for_load = 0.0
                for other_id, (_, other_tl_set, other_p_req, other_q_req) in all_mps_info.items():
                    if load_id in other_tl_set:
                        total_p_requested_for_load += other_p_req
                        total_q_requested_for_load += other_q_req

                # This MPS's share based on its requested P ratio
                if total_p_requested_for_load > 0:
                    my_p_ratio = my_p_req / total_p_requested_for_load
                else:
                    my_p_ratio = 1.0

                if total_q_requested_for_load > 0:
                    my_q_ratio = my_q_req / total_q_requested_for_load
                else:
                    my_q_ratio = 1.0

                my_p_demand += p_load * my_p_ratio
                my_q_demand += q_load * my_q_ratio

            # Clip to capacity
            p_projected = min(my_p_demand, float(mps.p_limit))
            s_projected = math.sqrt(p_projected**2 + my_q_demand**2)
            if s_projected > mps.s_limit:
                scale_factor = float(mps.s_limit) / s_projected
                p_projected = p_projected * scale_factor
                q_projected = my_q_demand * scale_factor
            else:
                q_projected = my_q_demand

            # Update MPS output
            old_pout = mps.Pout
            mps.Pout = p_projected
            mps.Qout = q_projected

            self.logger.info(
                f"Renegotiation: {mps_id} re-projected from P={old_pout:.1f}kW to "
                f"P={p_projected:.1f}kW, Q={q_projected:.1f}kVar (ratio-based share: {my_p_demand:.1f}kW)"
            )

    def move_mps(self, mps_id: str, target_node: str) -> Dict[str, Any]:
        """Move MPS using agent manager"""
        return self._move_actor("mobile_power", mps_id, target_node, self.env.tgraph)

    def operate_switches(self, switch_operations: List[Dict[str, str]]) -> Dict[str, Any]:
        """Operate multiple switches atomically with cycle auto-break

        Behavior:
        - All switches are updated atomically
        - If resulting topology has a cycle, system auto-opens the best switch to break it
        - One-time penalty applied for cycle creation (via cycle_detected flag)
        - LLM learns to avoid cycles by doing paired switch ops (close + open)

        Args:
            switch_operations: List of dicts, each containing:
                - switch_id: str (e.g., "S1")
                - operation: str ("open" or "close")

        Example:
            operate_switches([{"switch_id": "S1", "operation": "close"}])
            operate_switches([
                {"switch_id": "S1", "operation": "close"},
                {"switch_id": "S2", "operation": "open"}
            ])

        Returns:
            Result dict with:
                - status: "success" or "error"
                - cycle_detected: bool
                - message: str
                - switch_operations: original operations
                - final_states: dict of {switch_id: final_state}
        """
        try:
            # Step 1: Validate all operations first
            validated_ops = []
            for op in switch_operations:
                switch_id = op.get('switch_id')
                operation = op.get('operation')

                # Validate switch exists
                switch = self.agent_manager.get_switch(switch_id)
                if not switch:
                    return {
                        "status": "error",
                        "message": f"Switch {switch_id} not found",
                        "invalid_switch": switch_id
                    }

                # Validate operation
                if operation not in ["open", "close"]:
                    return {
                        "status": "error",
                        "message": f"Invalid operation '{operation}' for switch {switch_id}. Must be 'open' or 'close'",
                        "invalid_operation": operation
                    }

                # Check if switch node has a fault
                switch_node_faulted = False
                for dp_id, dp in self.agent_manager.damage_points.items():
                    if dp.from_node == switch.node_id and dp.to_node == switch.node_id and dp.state != 'repaired':
                        switch_node_faulted = True
                        break

                if switch_node_faulted:
                    return {
                        "status": "invalid",
                        "message": f"Switch {switch_id} cannot be operated: switch node has an active fault",
                        "switch_id": switch_id,
                        "reason": "switch_node_faulted"
                    }

                validated_ops.append((switch, operation))

            # Step 2: Save initial states
            initial_states = {}
            for switch, _ in validated_ops:
                initial_states[switch.id] = switch.state

            # Step 3: Apply all operations
            for switch, operation in validated_ops:
                switch.state = operation

            # Step 4: Update switch effects (do NOT revert on cycle)
            cycle_info = self.env.update_switch_effects(allow_faulted=False, revert_on_cycle=False)

            # Step 5: Update system state
            self.env.egraph.update_system_state()

            # Step 6: Check for cycle and auto-break if needed
            cycle_detected = cycle_info.get('cycle_detected', False)
            auto_break_result = None

            if cycle_detected:
                # Determine which switches the LLM just closed (exclude from auto-break)
                just_closed = set()
                for op in switch_operations:
                    if op.get('operation') == 'close':
                        just_closed.add(op.get('switch_id'))

                # Auto-break the cycle by opening the best switch
                auto_break_result = self._auto_break_cycle(exclude_switches=just_closed)
                self.logger.info(f"Cycle auto-break: {auto_break_result}")

            # Step 7: Record action
            self.action_history.append({
                "time": self.env.current_time,
                "action": "operate_switches",
                "params": {"switch_operations": switch_operations}
            })

            # Step 8: Build result
            weighted_power = self.env._calculate_weighted_power()
            final_states_dict = {sw.id: sw.state for sw, _ in validated_ops}

            if cycle_detected and auto_break_result:
                # Cycle was created and auto-resolved
                operations_desc = ', '.join([f"{op['switch_id']}->{op['operation']}" for op in switch_operations])
                opened_switches = auto_break_result.get('opened_switches', [])

                # Include auto-opened switches in final states
                for sw_id in opened_switches:
                    final_states_dict[sw_id] = 'open'

                resolved = auto_break_result.get('resolved', False)
                if opened_switches:
                    opened_str = ', '.join(opened_switches)
                    message = (
                        f"Switch operation applied [{operations_desc}], but created a cycle. "
                        f"System auto-opened {opened_str} to maintain radial topology. "
                        f"Penalty applied for cycle creation."
                    )
                else:
                    message = (
                        f"Switch operation applied [{operations_desc}], but created a cycle. "
                        f"Could not auto-resolve. Penalty applied for cycle creation."
                    )

                return {
                    "status": "success",  # Action was applied (not reverted)
                    "message": message,
                    "cycle_detected": True,  # Still True for reward penalty
                    "cycle_auto_resolved": resolved,
                    "auto_opened_switches": opened_switches,
                    "switch_operations": switch_operations,
                    "final_states": final_states_dict,
                    "weighted_power": weighted_power,
                    "reason": "cycle_auto_resolved"
                }
            else:
                return {
                    "status": "success",
                    "message": f"Successfully operated {len(switch_operations)} switch(es)",
                    "cycle_detected": False,
                    "switch_operations": switch_operations,
                    "final_states": {sw.id: sw.state for sw, _ in validated_ops},
                    "weighted_power": weighted_power
                }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _auto_break_cycle(self, exclude_switches: set = None) -> Dict[str, Any]:
        """Auto-break all cycles by opening the best switch(es).

        When a cycle is detected (from switch operation or repair), this method
        finds and opens the optimal switch to restore radial topology, maximizing
        weighted power delivery.

        Args:
            exclude_switches: Set of switch IDs to avoid opening (e.g., switches
                            just closed by LLM - we want to keep the LLM's intent)

        Returns:
            Dict with:
                - resolved: bool - whether all cycles were broken
                - opened_switches: List[str] - switches auto-opened
                - message: str - human-readable description
        """
        if exclude_switches is None:
            exclude_switches = set()

        opened_switches = []
        max_iterations = 10  # Safety limit for nested cycles

        for _ in range(max_iterations):
            if not self.env.egraph.has_cycle():
                break

            cycle_details = self.env.egraph.detect_cycle_with_details() if hasattr(self.env.egraph, 'detect_cycle_with_details') else None
            if not cycle_details:
                # Fallback: cycle exists but can't get details
                break

            switches_in_cycle = cycle_details.get('switches_in_cycle', [])

            # Prefer opening switches NOT in exclude set (keep LLM's intended closures)
            candidates = [s for s in switches_in_cycle if s not in exclude_switches and s not in opened_switches]
            if not candidates:
                # If all switches in cycle are excluded, allow any switch
                candidates = [s for s in switches_in_cycle if s not in opened_switches]
            if not candidates:
                break

            # Find best switch to open: the one that breaks the cycle with maximum power delivery
            best_switch = None
            best_power = -float('inf')

            for switch_id in candidates:
                switch = self.agent_manager.get_switch(switch_id)
                if not switch or switch.state != 'close':
                    continue

                # Temporarily open this switch
                switch.state = 'open'
                self.env.update_switch_effects(allow_faulted=False, revert_on_cycle=False)

                no_cycle = not self.env.egraph.has_cycle()
                if no_cycle:
                    self.env.egraph.update_system_state()
                    power = self.env._calculate_weighted_power()
                    if power > best_power:
                        best_power = power
                        best_switch = switch_id

                # Restore
                switch.state = 'close'
                self.env.update_switch_effects(allow_faulted=False, revert_on_cycle=False)

            if best_switch is None:
                # Fallback: just open the first closed candidate
                for s in candidates:
                    sw = self.agent_manager.get_switch(s)
                    if sw and sw.state == 'close':
                        best_switch = s
                        break

            if best_switch is None:
                break

            # Apply the opening
            switch = self.agent_manager.get_switch(best_switch)
            switch.state = 'open'
            opened_switches.append(best_switch)
            self.logger.info(f"Auto-break cycle: opened {best_switch}")

        # Final update after all openings
        if opened_switches:
            self.env.update_switch_effects(allow_faulted=False, revert_on_cycle=False)
            self.env.egraph.update_system_state()

        resolved = not self.env.egraph.has_cycle()

        if opened_switches:
            switches_str = ', '.join(opened_switches)
            message = f"Cycle auto-resolved: system opened {switches_str} to maintain radial topology. Penalty applied."
        else:
            message = "No cycle to resolve"

        return {
            "resolved": resolved,
            "opened_switches": opened_switches,
            "message": message
        }

    def operate_switch(self, switch_id: str, operation: str) -> Dict[str, Any]:
        """Operate single switch (backward compatibility wrapper)

        This method wraps operate_switches() to support legacy code that calls
        operate_switch() with single switch operations.

        Args:
            switch_id: Switch identifier (e.g., "S1")
            operation: "open" or "close"

        Returns:
            Result dict from operate_switches()
        """
        # Convert single operation to batch format
        switch_operations = [{"switch_id": switch_id, "operation": operation}]
        return self.operate_switches(switch_operations)

    def operate_load(self, load_id: str, action: str) -> Dict[str, Any]:
        """Operate load (on/off) using agent manager

        Note: This interface exists for backward compatibility and testing.
        In GRPO training, load restoration is AUTOMATIC (graphs.py:update_system_state).
        LLM cannot use this action (removed from projection.py valid actions).
        """
        try:
            load = self.agent_manager.get_load(load_id)

            if not load:
                return {
                    "status": "error",
                    "message": f"Load {load_id} not found"
                }

            valid_actions = ["on", "off"]
            if action not in valid_actions:
                return {
                    "status": "error",
                    "message": f"Invalid action '{action}'. Valid actions: {valid_actions}"
                }

            # Perform load operation
            if action == "on":
                load.switch_on()
            elif action == "off":
                load.switch_off()

            # Update system state after load operation
            self.env.egraph.update_system_state()

            self.action_history.append({
                "time": self.env.current_time,
                "action": "operate_load",
                "params": {"load_id": load_id, "action": action}
            })

            return {
                "status": "success",
                "message": f"Load {load_id} {action}",
                "load_id": load_id,
                "action": action,
                "new_state": load.state
            }

        except Exception as e:
            return {"status": "error", "message": f"Failed to operate load: {str(e)}"}

    def stop_repair(self, rc_id: str) -> Dict[str, Any]:
        """Stop repair operation using agent manager"""
        try:
            rc = self.agent_manager.get_repair_crew(rc_id)

            if not rc:
                return {"status": "error", "message": f"Repair crew {rc_id} not found"}

            if rc.state != "repairing":
                return {"status": "error", "message": f"Repair crew {rc_id} is not repairing (state: {rc.state})"}

            # Stop repair and free up the crew
            rc.stop_repair()  # Call RC instance method for proper encapsulation

            self.action_history.append({
                "time": self.env.current_time,
                "action": "stop_repair",
                "params": {"rc_id": rc_id}
            })

            return {
                "status": "success",
                "message": f"Repair crew {rc_id} stopped repair operation",
                "rc_id": rc_id
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def snapshot(self) -> Dict[str, Any]:
        """Create state snapshot for rollback"""
        return {
            'time': self.env.current_time,
            'agent_state': self.agent_manager.export_state(),
            'environment_state': self.env.export_state() if hasattr(self.env, 'export_state') else {}
        }

    def restore(self, snap: Dict[str, Any]) -> None:
        """Restore state from snapshot"""
        try:
            # Restore environment time
            if 'time' in snap:
                self.env.current_time = snap['time']

            # Restore agent state
            if 'agent_state' in snap:
                self.agent_manager.import_state(snap['agent_state'])

            # Restore environment state if available
            if 'environment_state' in snap and hasattr(self.env, 'import_state'):
                self.env.import_state(snap['environment_state'])

        except Exception as e:
            self.logger.error(f"Error restoring state: {e}")

    def step(self, action: Dict[str, Any], advance_time: bool = True) -> tuple[Dict[str, Any], Dict[str, Any], bool, Dict[str, Any]]:
        """Step the environment with action using agent manager"""
        initial_state = {}  # Safe default in case get_current_state() fails
        try:
            # Store initial state for comparison
            initial_state = self.get_current_state()

            # Process action
            action_result = self._execute_action(action)

            # Advance time if requested and get events
            if advance_time:
                env_step_result = self.env.step()  # This advances time and updates all agents
            else:
                env_step_result = {"events": [], "time": self.env.current_time}

            # Get new state after time advancement
            new_state = self.get_current_state()

            # Calculate basic reward info
            reward_info = {
                'action_success': action_result.get('status') == 'success',
                'action_result': action_result,
                'violations': [],
                'events': env_step_result.get('events', [])
            }

            # Check for any constraint violations
            if hasattr(self.env, 'check_violations'):
                violations = self.env.check_violations()
                reward_info['violations'] = violations

            # Check done condition using instance damage points
            done = self._check_episode_done()

            return new_state, reward_info, done, {'step_info': env_step_result}

        except Exception as e:
            self.logger.error(f"Error in step: {e}")
            return initial_state, {'error': str(e)}, False, {}

    def _check_episode_done(self) -> bool:
        """Check if episode is complete using instance damage points"""
        if not self.agent_manager:
            return False

        damage_points = self.agent_manager.damage_points
        if not damage_points:
            return True  # No damage points means episode is done

        # Check if all damage points are repaired
        all_repaired = all(dp.state == "repaired" for dp in damage_points.values())

        if all_repaired:
            self.logger.info("Episode complete: all damage points repaired")
            return True

        # Additional completion criteria can be added here
        # e.g., time limits, resource depletion, etc.

        return False

    # Helper methods
    def _move_actor(self, actor_type: str, actor_id: str, target: str, graph) -> Dict[str, Any]:
        """Helper function for moving actors (RC/MPS) to reduce code duplication"""
        try:
            # Get the appropriate actor from agent manager
            if actor_type == "repair_crew":
                actor = self.agent_manager.get_repair_crew(actor_id)
                # Allow "repairing" state - RC can interrupt current repair to move to new target
                valid_states = ["idle", "repairing"]
                state_error_msg = f"Repair crew {actor_id} is busy (state: {actor.state if actor else 'unknown'})"
            elif actor_type == "mobile_power":
                actor = self.agent_manager.get_mobile_power_source(actor_id)
                valid_states = ["idle"]
                state_error_msg = f"Mobile power source {actor_id} must be idle to move (state: {actor.state if actor else 'unknown'})"
            else:
                return {"status": "error", "message": f"Unknown actor type: {actor_type}"}

            if not actor:
                return {
                    "status": "error",
                    "message": f"{actor_type.replace('_', ' ').title()} {actor_id} not found"
                }

            if actor.state not in valid_states:
                # Provide clearer error message for specific MPS states
                if actor_type == "mobile_power":
                    if actor.state == 'connected':
                        # MPS is connected, need to disconnect first
                        current_node = actor.current_position if hasattr(actor, 'current_position') else 'unknown'
                        state_error_msg = f"MPS {actor_id} connected at {current_node}. Disconnect first or wait until disconnected."
                        reason = "mps_connected"
                    elif actor.state == 'out_of_service':
                        state_error_msg = (
                            f"MPS {actor_id} is permanently out of service (energy exhausted). "
                            f"Cannot move or use this MPS."
                        )
                        reason = "mps_out_of_service"
                    else:
                        # Other states (moving, etc.)
                        state_error_msg = f"MPS {actor_id} must be idle to move (state: {actor.state})"
                        reason = "agent_busy"
                elif actor_type == "repair_crew":
                    if actor.state == 'out_of_service':
                        state_error_msg = (
                            f"RC {actor_id} is out of service (resources depleted). "
                            f"Cannot use this RC for further repairs."
                        )
                        reason = "rc_out_of_service"
                    else:
                        state_error_msg = f"RC {actor_id} is busy (state: {actor.state})"
                        reason = "agent_busy"

                return {"status": "invalid", "message": state_error_msg, "reason": reason}

            # Check if already at target position
            if hasattr(actor, 'current_position') and actor.current_position == target:
                return {
                    "status": "no_op",
                    "message": f"{actor_type.replace('_', ' ').title()} {actor_id} already at target position {target}",
                    "reason": "already_at_target"
                }

            # For MPS, check if target is a fault node
            if actor_type == "mobile_power" and target in graph.nodes:
                if graph.nodes[target].is_fault:
                    return {
                        "status": "invalid",
                        "message": f"Cannot move MPS {actor_id} to fault node {target}. "
                                   f"Fault nodes are damaged locations. Choose a different node.",
                        "reason": "target_is_fault_node"
                    }

            # Check if target node exists in graph before attempting move
            if target not in graph.nodes:
                # Provide detailed error with available nodes
                available_nodes = sorted(list(graph.nodes.keys()))

                # Show first 15 nodes + count of remaining
                if len(available_nodes) > 15:
                    nodes_sample = available_nodes[:15]
                    remaining_count = len(available_nodes) - 15
                    nodes_display = ', '.join(nodes_sample) + f', ... (+{remaining_count} more)'
                else:
                    nodes_display = ', '.join(available_nodes)

                # Get list of damage points for helpful tip
                dp_list = sorted(list(self.agent_manager.damage_points.keys()))
                dp_display = ', '.join(dp_list) if dp_list else 'None'

                return {
                    "status": "error",
                    "message": f"ERROR: Target '{target}' not found. Valid nodes: {nodes_display[:50]}... Valid DPs: {dp_display[:30]}..."
                }

            # Use TGraph interface
            success = actor.move(target, graph)
            if not success:
                # Target exists but move failed for other reasons (e.g., no path)
                return {
                    "status": "error",
                    "message": f"{actor_type.replace('_', ' ').title()} {actor_id} could not move to {target}. "
                               f"Possible reasons: no valid path exists, or target is unreachable."
                }

            self.action_history.append({
                "time": self.env.current_time,
                "action": f"move_{actor_type}",
                "params": {f"{actor_type}_id": actor_id, "target": target}
            })

            return {
                "status": "success",
                "message": f"{actor_type.replace('_', ' ').title()} {actor_id} moving to {target}",
                f"{actor_type}_id": actor_id,
                "target": target,
                "distance": getattr(actor, 'remaining_distance', 0)
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to move {actor_type.replace('_', ' ')}: {str(e)}"
            }

    def _do_and_update(self, action_name: str, operation_func, *args, **kwargs) -> Dict[str, Any]:
        """Helper function for operations that need system state update"""
        try:
            result = operation_func(*args, **kwargs)

            # Update system state after operation
            self.env.egraph.update_system_state()

            return result

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to {action_name}: {str(e)}"
            }

    def _move_repair_crew(self, rc_id: str, target: str) -> Dict[str, Any]:
        """Move repair crew using agent manager (private helper)"""
        return self._move_actor("repair_crew", rc_id, target, self.env.tgraph)

    def _repair_fault(self, rc_id: str, fault_id: str, auto_repair: bool = False) -> Dict[str, Any]:
        """Repair fault using agent manager (private helper)"""
        try:
            rc = self.agent_manager.get_repair_crew(rc_id)
            dp = self.agent_manager.get_damage_point(fault_id)

            if not rc:
                return {
                    "status": "error",
                    "message": f"Repair crew {rc_id} not found"
                }

            if not dp:
                return {
                    "status": "error",
                    "message": f"Fault {fault_id} not found"
                }

            if rc.state != "idle":
                return {
                    "status": "invalid",
                    "message": f"RC {rc_id} is busy (state: {rc.state})",
                    "reason": "agent_busy"
                }

            if dp.state == "repaired":
                return {"status": "no_op", "message": f"Fault {fault_id} already repaired", "reason": "already_completed"}

            # Check if RC is at fault location
            if not rc._at_fault_location(dp):
                # Get precise fault location info
                fault_location = dp.fault_node_id if hasattr(dp, 'fault_node_id') and dp.fault_node_id else f"{dp.from_node}-{dp.to_node}"

                # Provide detailed position information
                rc_pos = rc.current_position
                rc_state = rc.state

                # Determine the correct target for move command
                # For node faults: target is the node itself (fault_node_id == from_node)
                # For edge faults: target is the fault_id (which becomes a node in traffic graph)
                move_target = fault_location

                # Check if fault has capacity constraint (multiple crews required)
                capacity_hint = ""
                if hasattr(dp, 'capacity') and dp.capacity > 1:
                    capacity_hint = f"\nIMPORTANT: Fault {fault_id} requires {dp.capacity} crews working TOGETHER.\n" \
                                  f"   ALL {dp.capacity} crews must execute repair_fault in the SAME turn!"

                return {
                    "status": "invalid",
                    "message": f"RC {rc_id} at {rc_pos}, cannot repair {fault_id} at {fault_location}. Move to fault location first.",
                    "reason": "position_mismatch"
                }

            # CRITICAL: Check DP capacity constraint before attempting repair
            if hasattr(dp, 'active_crews') and hasattr(dp, 'capacity'):
                if rc_id not in dp.active_crews:
                    if len(dp.active_crews) >= dp.capacity:
                        # Capacity limit reached - provide detailed error with actionable information
                        return {
                            "status": "invalid",
                            "message": f"RC {rc_id} cannot repair {fault_id}: DP capacity limit reached ({len(dp.active_crews)}/{dp.capacity}). "
                                      f"Active crews: {list(dp.active_crews)}. Wait for one crew to finish.",
                            "reason": "capacity_limit",
                            "capacity": dp.capacity,
                            "active_crews": list(dp.active_crews),
                            "num_active_crews": len(dp.active_crews)
                        }

            # Start repair
            repair_amount = rc.repair(fault_id, auto_repair=auto_repair,
                                    tgraph=self.env.tgraph, egraph=self.env.egraph)

            if repair_amount > 0:
                self.action_history.append({
                    "time": self.env.current_time,
                    "action": "repair_fault",
                    "params": {"rc_id": rc_id, "fault_id": fault_id, "amount": repair_amount}
                })

                return {
                    "status": "success",
                    "message": f"Repair crew {rc_id} repairing fault {fault_id}",
                    "rc_id": rc_id,
                    "fault_id": fault_id,
                    "repair_amount": repair_amount,
                    "auto_repair": auto_repair
                }
            else:
                return {
                    "status": "error",
                    "message": f"Repair crew {rc_id} could not start repair"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action using agent manager"""
        action_type = action.get('type', '')

        # RC actions
        if action_type == 'move_repair_crew':
            for k in ('crew_id', 'target'):
                if k not in action:
                    return {'status': 'error', 'message': f'move_repair_crew requires {k}'}
            return self.move_repair_crew(action['crew_id'], action['target'])
        elif action_type == 'repair_fault':
            for k in ('crew_id', 'fault_id'):
                if k not in action:
                    return {'status': 'error', 'message': f'repair_fault requires {k}'}
            return self.repair_fault(action['crew_id'], action['fault_id'], action.get('auto_repair', False))
        elif action_type == 'stop_repair':
            if 'crew_id' not in action:
                return {'status': 'error', 'message': 'stop_repair requires crew_id'}
            return self.stop_repair(action['crew_id'])

        # MPS actions
        elif action_type == 'move_mps':
            for k in ('mps_id', 'target_node'):
                if k not in action:
                    return {'status': 'error', 'message': f'move_mps requires {k}'}
            return self.move_mps(action['mps_id'], action['target_node'])
        elif action_type == 'connect_mps':
            return {
                'status': 'error',
                'message': 'connect_mps is deprecated in v5.2. Use set_mps_output() instead.'
            }
        elif action_type == 'disconnect_mps':
            return {
                'status': 'error',
                'message': 'disconnect_mps is not available. MPS auto-disconnects when energy depletes.'
            }
        elif action_type == 'set_mps_output':
            for k in ('mps_id', 'P_out', 'Q_out'):
                if k not in action:
                    return {'status': 'error', 'message': f'set_mps_output requires {k}'}
            return self.set_mps_output(action['mps_id'], action['P_out'], action['Q_out'], action.get('target_loads', []))
        elif action_type == 'set_multiple_mps_outputs':
            if 'mps_outputs' not in action:
                return {'status': 'error', 'message': 'set_multiple_mps_outputs requires mps_outputs'}
            return self.set_multiple_mps_outputs(action['mps_outputs'])

        # Switch actions
        elif action_type == 'operate_switch':
            for k in ('switch_id', 'operation'):
                if k not in action:
                    return {'status': 'error', 'message': f'operate_switch requires {k}'}
            return self.operate_switch(action['switch_id'], action['operation'])

        # General actions
        elif action_type == 'wait':
            return {'status': 'success', 'message': 'Waiting'}

        else:
            return {'status': 'error', 'message': f'Unknown action type: {action_type}'}


    def _is_connected(self, node1: str, node2: str, egraph) -> bool:
        """Check if two nodes are electrically connected

        Uses _dfs_connected_component to determine if two nodes are in the same island
        """
        try:
            # Check if nodes exist
            if node1 not in egraph.nodes or node2 not in egraph.nodes:
                return False

            # Same node is always connected to itself
            if node1 == node2:
                return True

            # Use _dfs_connected_component to find the island containing node1
            # Then check if node2 is in the same island
            island = egraph._dfs_connected_component(node1, set())
            return node2 in island

        except Exception as e:
            self.logger.error(f"Error checking connectivity: {e}")
            return False
