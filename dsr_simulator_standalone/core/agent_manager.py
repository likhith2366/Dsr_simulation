"""
AgentManager - Instance-based Agent State Manager
===================================================

Core design principles:
- Each simulation environment instance owns an independent AgentManager, avoiding class variables
- Supports multi-process parallel training (each worker has its own AgentManager instance)

Managed agent types:
- repair_crews (Dict[str, RC])     : Repair Crews
- mobile_power_sources (Dict[str, MPS]) : Mobile Power Sources
- damage_points (Dict[str, DP])    : Damage Points
- switches (Dict[str, Switch])     : Switches
- loads (Dict[str, Load])          : Loads

Key functions:
- add_xxx() / get_xxx() / get_all_xxx() : Add / Get / Get all
- export_state() / import_state()       : State snapshots (for rollback, checkpoints)
- get_loads_at_node()                   : Query all loads at a given node
- get_mps_connected_at_node()           : Query MPS connected at a given node
- _restored_loads                       : Monotonic flag for loads that have been restored (for reliability constraint)
"""

from typing import Dict, Optional, List, Tuple, Any
import logging
from .agents import RC, MPS, DP, Switch, Load


class AgentManager:
    """
    Manages independent agent state for each environment instance.
    Replaces global class variables with instance-based management.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize independent agent state"""
        self.logger = logger or logging.getLogger(__name__)

        # Instance-specific agent collections (replacing class variables)
        self.repair_crews: Dict[str, RC] = {}
        self.mobile_power_sources: Dict[str, MPS] = {}
        self.damage_points: Dict[str, DP] = {}
        self.switches: Dict[str, Switch] = {}
        self.loads: Dict[str, Load] = {}

        # Restoration tracking
        self._restored_loads: set[str] = set()

    def clear_all(self) -> None:
        """Clear all agents (equivalent to original class.clear_all())"""
        self.repair_crews.clear()
        self.mobile_power_sources.clear()
        self.damage_points.clear()
        self.switches.clear()
        self.loads.clear()
        self._restored_loads.clear()

    def reset_restoration_state(self) -> None:
        """Reset restoration state for new episode"""
        self._restored_loads.clear()

    # ===== RC Management =====
    def add_repair_crew(self, rc_id: str, initial_position: str, speed: int,
                       efficiency: float, total_resources: float) -> RC:
        """Add repair crew to this environment instance"""
        rc = RC(rc_id, initial_position, speed, efficiency, total_resources)
        # Override the RC's agent manager reference
        rc._agent_manager = self
        self.repair_crews[rc_id] = rc

        if self.logger:
            self.logger.info(f"RC {rc_id} added: pos={initial_position}, eff={efficiency}, res={total_resources}")

        return rc

    def get_repair_crew(self, rc_id: str) -> Optional[RC]:
        """Get repair crew by ID"""
        return self.repair_crews.get(rc_id)

    def get_all_repair_crews(self) -> Dict[str, RC]:
        """Get all repair crews"""
        return self.repair_crews.copy()

    # ===== MPS Management =====
    def add_mobile_power_source(self, mps_id: str, initial_position: str,
                                p_limit: float, s_limit: float, energy: float,
                                speed: float = 5.0) -> MPS:
        """Add mobile power source to this environment instance"""
        mps = MPS(mps_id, int(p_limit), int(s_limit), int(energy), initial_position, int(speed))
        mps._agent_manager = self
        self.mobile_power_sources[mps_id] = mps

        if self.logger:
            self.logger.info(f"MPS {mps_id} added: pos={initial_position}, p_limit={p_limit}kW, energy={energy}kWh")

        return mps

    def get_mobile_power_source(self, mps_id: str) -> Optional[MPS]:
        """Get mobile power source by ID"""
        return self.mobile_power_sources.get(mps_id)

    def get_all_mobile_power_sources(self) -> Dict[str, MPS]:
        """Get all mobile power sources"""
        return self.mobile_power_sources.copy()

    # ===== DP Management =====
    def add_damage_point(self, dp_id: str, from_node: str, to_node: str,
                        distance: float, repair_demand: float,
                        fault_node_id: str = None, capacity: int = 1) -> DP:
        """Add damage point to this environment instance"""
        dp = DP(dp_id, from_node, to_node, int(distance), int(repair_demand), capacity)
        dp._agent_manager = self
        if fault_node_id:
            dp.fault_node_id = fault_node_id
        self.damage_points[dp_id] = dp

        if self.logger:
            self.logger.info(f"Damage point {dp_id} added: {from_node}->{to_node}, demand={repair_demand}")

        return dp

    def get_damage_point(self, dp_id: str) -> Optional[DP]:
        """Get damage point by ID"""
        return self.damage_points.get(dp_id)

    def get_all_damage_points(self) -> Dict[str, DP]:
        """Get all damage points"""
        return self.damage_points.copy()

    # ===== Switch Management =====
    def add_switch(self, switch_id: str, node_id: str,
                  connected_edges: List[str], initial_state: str = "close") -> Switch:
        """Add switch to this environment instance"""
        switch = Switch(switch_id, node_id, connected_edges, initial_state)
        switch._agent_manager = self
        self.switches[switch_id] = switch

        return switch

    def get_switch(self, switch_id: str) -> Optional[Switch]:
        """Get switch by ID"""
        return self.switches.get(switch_id)

    def get_all_switches(self) -> Dict[str, Switch]:
        """Get all switches"""
        return self.switches.copy()

    # ===== Load Management =====
    def add_load(self, load_id: str, node_id: str, P: float, Q: float, W: float) -> Load:
        """Add load to this environment instance

        Note: Load.state represents load operational status:
        - state="on" means the load is serving customers (connected and powered)
        - state="off" means the load is offline (not serving, either disconnected or unpowered)

        Load state management (AUTOMATIC):
        - Loads start as "on" assuming initial power availability
        - System automatically sheds loads (switch_off) when power lost (graphs.py:update_system_state)
        - System AUTOMATICALLY restores loads when power available (Grid or MPS) (graphs.py:update_system_state)
        - LLM controls RC repair and MPS deployment; load restoration is fully automatic
        - The operate_load() interface still exists but is NOT exposed to LLM (removed from projection.py)
        """
        load = Load(load_id, node_id, P, Q, W, initial_state="on")
        load._agent_manager = self
        self.loads[load_id] = load

        return load

    def get_load(self, load_id: str) -> Optional[Load]:
        """Get load by ID"""
        return self.loads.get(load_id)

    def get_all_loads(self) -> Dict[str, Load]:
        """Get all loads"""
        return self.loads.copy()

    def get_loads_at_node(self, node_id: str) -> List[Load]:
        """Get all loads at a specific node"""
        return [load for load in self.loads.values() if load.node_id == node_id]

    def get_mps_connected_at_node(self, node_id: str) -> Optional[MPS]:
        """Get first MPS connected at a specific node (for backward compatibility)

        Note: v5.8 allows multiple MPS per node. Use get_all_mps_connected_at_node() for full list.
        """
        for mps in self.mobile_power_sources.values():
            if mps.state == 'connected' and mps.connected_node == node_id:
                return mps
        return None

    def get_all_mps_connected_at_node(self, node_id: str) -> List[MPS]:
        """Get all MPS connected at a specific node (v5.8: supports multiple MPS per node)"""
        return [mps for mps in self.mobile_power_sources.values()
                if mps.state == 'connected' and mps.connected_node == node_id]

    # ===== Restoration State Management =====
    # Note: This tracking mechanism was originally designed to prevent user from manually
    # disconnecting restored loads (user behavior constraint in Load.switch_off).
    # With automatic load restoration (graphs.py), all loads are restored by system, not user.
    # The constraint still exists but is effectively inactive since:
    # 1. LLM cannot use operate_load() (removed from projection.py valid actions)
    # 2. System uses force_system=True when shedding loads (bypasses constraint)
    # 3. All restoration is automatic (graphs.py:update_system_state)

    def is_load_restored(self, load_id: str) -> bool:
        """Check if load has been restored (marked when load.switch_on() called)"""
        return load_id in self._restored_loads

    def restore_load(self, load_id: str) -> None:
        """Mark load as restored (called by Load.switch_on())"""
        self._restored_loads.add(load_id)

    def get_restored_loads(self) -> set[str]:
        """Get all loads that have been restored"""
        return self._restored_loads.copy()

    # ===== State Export/Import =====
    def export_state(self) -> Dict[str, Any]:
        """Export complete agent state for snapshots"""
        return {
            'repair_crews': {rc_id: {
                'id': rc.id,
                'current_position': rc.current_position,
                'state': rc.state,
                'speed': rc.speed,
                'efficiency': rc.efficiency,
                'total_resources': rc.total_resources,
                'remaining_resources': rc.remaining_resources,
                'target_position': rc.target_position,
                'remaining_distance': rc.remaining_distance,
                'target_fault': getattr(rc, 'target_fault', None),
                'path': rc.path,  # Movement path
                'current_repair_amount': rc.current_repair_amount,
                'planned_efficiency': rc.planned_efficiency,
                'auto_repair': rc.auto_repair,
                'last_repair_target': rc.last_repair_target
            } for rc_id, rc in self.repair_crews.items()},

            'mobile_power_sources': {mps_id: {
                'id': mps.id,
                'current_position': mps.current_position,
                'state': mps.state,
                'p_limit': mps.p_limit,
                's_limit': mps.s_limit,
                'energy': mps.energy,
                'speed': mps.speed,
                'Pout': mps.Pout,
                'Qout': mps.Qout,
                'connected_node': mps.connected_node,  # CRITICAL: Connection state
                'edge_id': mps.edge_id,  # Edge in EGraph when connected
                'target_position': mps.target_position,  # Movement target
                'remaining_distance': mps.remaining_distance,
                'path': mps.path,  # Movement path
                'target_loads': mps.target_loads  # CRITICAL: Selective load recovery
            } for mps_id, mps in self.mobile_power_sources.items()},

            'damage_points': {dp_id: {
                'id': dp.id,
                'from_node': dp.from_node,
                'to_node': dp.to_node,
                'distance': dp.distance,
                'repair_demand': dp.repair_demand,
                'repair_progress': dp.repair_progress,
                'state': dp.state,
                'fault_node_id': dp.fault_node_id,
                'affected_edge_id': dp.affected_edge_id,
                'split_edges': dp.split_edges,
                'capacity': dp.capacity,  # CRITICAL: For parallel repair reward calculation
                'active_crews': list(dp.active_crews)  # CRITICAL: Track active RCs for capacity constraint
            } for dp_id, dp in self.damage_points.items()},

            'switches': {switch_id: {
                'id': switch.id,
                'node_id': switch.node_id,
                'state': switch.state,
                'connected_edges': switch.connected_edges
            } for switch_id, switch in self.switches.items()},

            'loads': {load_id: {
                'id': load.id,
                'node_id': load.node_id,
                'P': load.P,
                'Q': load.Q,
                'W': load.W,
                'state': load.state,  # CRITICAL: Must preserve on/off state for restore
            } for load_id, load in self.loads.items()},

            # Restoration tracking (separate from load state for clarity)
            'restored_loads': list(self._restored_loads)
        }

    def import_state(self, state: Dict[str, Any]) -> None:
        """Import agent state from snapshot"""
        # Clear current state
        self.clear_all()

        # Import repair crews
        for rc_id, rc_data in state.get('repair_crews', {}).items():
            rc = self.add_repair_crew(
                rc_id, rc_data['current_position'], rc_data['speed'],
                rc_data['efficiency'], rc_data['total_resources']
            )
            rc.state = rc_data['state']
            rc.remaining_resources = rc_data['remaining_resources']
            rc.target_position = rc_data.get('target_position')
            rc.remaining_distance = rc_data.get('remaining_distance', 0)
            if 'target_fault' in rc_data:
                rc.target_fault = rc_data['target_fault']
            # Restore additional RC state
            rc.path = rc_data.get('path', [])
            rc.current_repair_amount = rc_data.get('current_repair_amount', 0)
            rc.planned_efficiency = rc_data.get('planned_efficiency')
            rc.auto_repair = rc_data.get('auto_repair', False)
            rc.last_repair_target = rc_data.get('last_repair_target')

        # Import mobile power sources
        for mps_id, mps_data in state.get('mobile_power_sources', {}).items():
            mps = self.add_mobile_power_source(
                mps_id, mps_data['current_position'], mps_data['p_limit'],
                mps_data['s_limit'], mps_data['energy'], mps_data['speed']
            )
            mps.state = mps_data['state']
            mps.Pout = mps_data.get('Pout', 0)
            mps.Qout = mps_data.get('Qout', 0)
            # Restore connection state (critical for connected MPS)
            mps.connected_node = mps_data.get('connected_node')
            mps.edge_id = mps_data.get('edge_id')
            # Restore movement state
            mps.target_position = mps_data.get('target_position')
            mps.remaining_distance = mps_data.get('remaining_distance', 0)
            mps.path = mps_data.get('path', [])
            # Restore target loads (critical for selective load recovery)
            mps.target_loads = mps_data.get('target_loads', [])

        # Import damage points
        for dp_id, dp_data in state.get('damage_points', {}).items():
            dp = self.add_damage_point(
                dp_id, dp_data['from_node'], dp_data['to_node'],
                dp_data['distance'], dp_data['repair_demand'],
                dp_data.get('fault_node_id'),
                dp_data.get('capacity', 1)  # CRITICAL: Restore capacity for parallel repair
            )
            dp.repair_progress = dp_data.get('repair_progress', 0)
            dp.state = dp_data.get('state', 'active')
            # Restore graph-related fields
            dp.affected_edge_id = dp_data.get('affected_edge_id')
            dp.split_edges = dp_data.get('split_edges', [])
            # Restore active_crews for capacity constraint enforcement
            dp.active_crews = set(dp_data.get('active_crews', []))

        # Import switches
        for switch_id, switch_data in state.get('switches', {}).items():
            switch = self.add_switch(
                switch_id, switch_data['node_id'],
                switch_data['connected_edges'], switch_data['state']
            )

        # Import loads
        for load_id, load_data in state.get('loads', {}).items():
            load = self.add_load(
                load_id, load_data['node_id'],
                load_data['P'], load_data['Q'], load_data['W']
            )
            # Restore load state (on/off)
            if 'state' in load_data:
                load.state = load_data['state']

        # Import restoration state (restored_loads tracked separately from load state)
        self._restored_loads = set(state.get('restored_loads', []))