"""
Agent classes: repair crews(RC), mobile power sources(MPS), damage points(DP), loads and switches
For various agent entities in DSR simulation environment - Cleaned version
"""

from typing import Dict, List, Optional, Tuple, Set, Any
import math
import logging

class Switch:
    """Switch class - manages all switch devices"""

    # Class variable, stores all switches
    switches: Dict[str, 'Switch'] = {}

    def __init__(self, switch_id: str, node_id: str, connected_edges: List[str], initial_state: str = "open"):
        """Initialize switch

        Args:
            switch_id: Unique switch identifier
            node_id: Electrical node ID where the switch is located
            connected_edges: List of edge IDs controlled by this switch
            initial_state: Initial state ("open" or "close")
        """
        self.id = switch_id
        self.node_id = node_id
        self.connected_edges = connected_edges  # List of edges controlled by this switch
        self.state = initial_state  # "open" or "close"

        # Agent manager reference (for new instance-based approach)
        self._agent_manager = None

        # Note: Class variable registration removed to support parallel training
        # All instances are now managed through AgentManager only

    @classmethod
    def add(cls, switch_id: str, node_id: str, connected_edges: List[str], initial_state: str = "open") -> 'Switch':
        """Add new switch (class method)

        Args:
            switch_id: Unique switch identifier
            node_id: Electrical node ID where the switch is located
            connected_edges: List of edge IDs controlled by this switch
            initial_state: Initial state

        Returns:
            Newly created switch object
        """
        if switch_id in cls.switches:
            raise ValueError(f"Switch {switch_id} already exists")

        return cls(switch_id, node_id, connected_edges, initial_state)

    def open(self, egraph: 'EGraph') -> None:
        """Open switch

        Args:
            egraph: Electrical graph object, used to update edge connection state
        """
        self.state = "open"
        # Disconnect all related edges
        for edge_id in self.connected_edges:
            egraph.set_edge_connection(edge_id, False)

    def close(self, egraph: 'EGraph') -> None:
        """Close switch

        Args:
            egraph: Electrical graph object, used to update edge connection state
        """
        self.state = "close"
        # Connect all related edges
        for edge_id in self.connected_edges:
            egraph.set_edge_connection(edge_id, True)

    @classmethod
    def operate(cls, switch_id: str, action: str, egraph: 'EGraph') -> None:
        """Operate switch (class method)

        Args:
            switch_id: Switch ID to operate
            action: Operation action ("open" or "close")
            egraph: Electrical graph object
        """
        if switch_id not in cls.switches:
            raise ValueError(f"Switch {switch_id} not found")

        switch = cls.switches[switch_id]

        if action == "open":
            switch.open(egraph)
        elif action == "close":
            # Check for cycles before closing switch
            if cls._would_create_cycle(switch, egraph):
                raise ValueError(f"Cannot close switch {switch_id}: would create cycle (violate radial topology)")
            switch.close(egraph)
        else:
            raise ValueError(f"Invalid action: {action}. Must be 'open' or 'close'")

    @classmethod
    def _would_create_cycle(cls, switch: 'Switch', egraph: 'EGraph') -> bool:
        """Check if closing switch would create a cycle

        Args:
            switch: Switch to close
            egraph: Electrical graph object

        Returns:
            True if closing switch would create cycle, False otherwise
        """
        # Temporarily close the switch edges to test for cycles
        original_states = {}

        # Store original states and temporarily close switch edges
        for edge_id in switch.connected_edges:
            if edge_id in egraph.edges:
                original_states[edge_id] = egraph.edges[edge_id].is_connected
                egraph.edges[edge_id].is_connected = True

        # Check for cycles
        has_cycle = egraph.has_cycle()

        # Restore original states
        for edge_id, original_state in original_states.items():
            if edge_id in egraph.edges:
                egraph.edges[edge_id].is_connected = original_state

        return has_cycle

    def operate(self, egraph: 'EGraph', action: str) -> Dict[str, str]:
        """Instance-level operate method with cycle prevention check

        Args:
            egraph: Electrical graph object
            action: Operation action ("open" or "close")

        Returns:
            Operation result dict containing result and reason fields
        """
        if action == "open":
            self.open(egraph)
            return {"result": "success", "reason": "Switch opened successfully"}
        elif action == "close":
            # Check for cycles before closing switch
            if Switch._would_create_cycle(self, egraph):
                return {
                    "result": "blocked",
                    "reason": "Cannot close switch: would create cycle (violate radial topology)"
                }
            self.close(egraph)
            return {"result": "success", "reason": "Switch closed successfully"}
        else:
            return {"result": "error", "reason": f"Invalid action: {action}. Must be 'open' or 'close'"}

    @classmethod
    def get_by_node(cls, node_id: str) -> List['Switch']:
        """Get all switches at a node

        Args:
            node_id: Node ID

        Returns:
            List of all switches at this node
        """
        return [switch for switch in cls.switches.values() if switch.node_id == node_id]

    @classmethod
    def get_switch(cls, switch_id: str) -> Optional['Switch']:
        """Get switch by ID

        Args:
            switch_id: Switch ID

        Returns:
            Switch object, or None if it does not exist
        """
        return cls.switches.get(switch_id)

    @staticmethod
    def get_switch_from_manager(agent_manager, switch_id: str) -> Optional['Switch']:
        """Get switch from AgentManager (for new approach)

        Args:
            agent_manager: AgentManager instance
            switch_id: Switch ID

        Returns:
            Switch object, or None if not found
        """
        if agent_manager is None:
            return None
        return agent_manager.get_switch(switch_id)

    @classmethod
    def get_all_switches(cls) -> Dict[str, 'Switch']:
        """Get all switches

        Returns:
            Dictionary of all switches
        """
        return cls.switches.copy()

    @classmethod
    def clear_all(cls) -> None:
        """Clear all switches (used for system reset)"""
        cls.switches.clear()

    def __str__(self) -> str:
        """String representation"""
        return f"Switch(id={self.id}, node={self.node_id}, state={self.state}, edges={self.connected_edges})"

    def __repr__(self) -> str:
        """Detailed representation"""
        return self.__str__()

class RC:
    """RC (Repair Crew) class"""

    # Class variables
    repair_crews: Dict[str, 'RC'] = {}
    _logger: Optional[logging.Logger] = None

    def __init__(self, rc_id: str, initial_position: str, speed: int,
                 efficiency: float, total_resources: float):
        """Initialize RC

        Args:
            rc_id: Unique RC identifier
            initial_position: Initial position (traffic graph node ID)
            speed: Movement speed (km/h)
            efficiency: Maximum repair efficiency per time step (p.u.)
            total_resources: Total resource capacity (p.u.)
        """
        self.id = rc_id
        self.current_position = initial_position
        self.speed = speed
        self.efficiency = efficiency
        self.total_resources = total_resources
        self.remaining_resources = total_resources

        # State management
        self.state = "idle"  # idle/moving/repairing/out_of_service

        # Movement related
        self.target_position = None
        self.remaining_distance = 0
        self.path = []

        # Repair related
        self.current_repair_amount = 0  # Actual repair amount this step
        self.planned_efficiency = None  # Planned efficiency to use
        self.auto_repair = False  # Whether to automatically continue repair
        self.last_repair_target = None  # Fault ID of last repair target

        # Agent manager reference (for new instance-based approach)
        self._agent_manager = None

        self._repaired_this_step = False

        # Note: Class variable registration removed to support parallel training
        # All instances are now managed through AgentManager only

    @classmethod
    def set_logger(cls, logger: logging.Logger):
        """Set class-level logger"""
        cls._logger = logger

    @classmethod
    def add(cls, rc_id: str, initial_position: str, speed: int,
            efficiency: float, total_resources: float) -> 'RC':
        """Add new RC

        Args:
            rc_id: Unique RC identifier
            initial_position: Initial position
            speed: Movement speed
            efficiency: Maximum repair efficiency
            total_resources: Total resource amount

        Returns:
            Newly created RC object
        """
        if rc_id in cls.repair_crews:
            # Silently return existing RC during restore operations
            return cls.repair_crews[rc_id]

        rc = cls(rc_id, initial_position, speed, efficiency, total_resources)
        # Only log during initial creation, not during restore
        if not hasattr(cls, '_restore_mode') or not cls._restore_mode:
            if cls._logger:
                cls._logger.info(f"RC {rc_id} added: pos={initial_position}, eff={efficiency}, res={total_resources}")
            else:
                print(f"RC {rc_id} added: pos={initial_position}, eff={efficiency}, res={total_resources}")
        return rc

    def move(self, target_node: str, tgraph: 'TGraph') -> bool:
        """Move to target node

        Args:
            target_node: Target node ID
            tgraph: Traffic graph object

        Returns:
            Whether movement started successfully
        """
        # Check state
        if self.state == "moving":
            print(f"RC {self.id} is moving, cannot accept new move command")
            return False

        if self.state == "repairing":
            # Allow interrupting repair - crew will stop current repair and move to new target
            # Cleanup of active_crews and auto_repair happens below (lines 348-355)
            print(f"RC {self.id} interrupting repair to move to {target_node}")

        # Allow out_of_service RC to move (to clear fault locations)
        # Movement does not consume resources, only repair does
        if self.remaining_resources <= 0 and self.state != "out_of_service":
            print(f"RC {self.id} resources exhausted, setting to out of service")
            self.state = "out_of_service"
            # Continue to allow movement

        # Check if already at target position - this should be successful (no-op)
        if self.current_position == target_node:
            if self._logger:
                self._logger.info(f"RC {self.id} already at target position {target_node}")
            else:
                print(f"RC {self.id} already at target position {target_node}")
            # Already at target - this is a successful no-op, not an error
            self.state = "idle"  # Ensure state is idle since we're at target
            return True

        # Use shortest path algorithm
        path, total_distance = tgraph.find_shortest_path(self.current_position, target_node)

        if not path or total_distance < 0:
            # Only print path errors during initial simulation, not during restore
            if not hasattr(self.__class__, '_restore_mode') or not self.__class__._restore_mode:
                if self._logger:
                    self._logger.warning(f"cannot find path from {self.current_position} to {target_node} path")
                else:
                    print(f"cannot find path from {self.current_position} to {target_node} path")
            return False

        # Set movement parameters
        self.target_position = target_node
        self.remaining_distance = total_distance
        self.path = path
        self.state = "moving"

        # Stop auto repair and clean up active_crews
        # CRITICAL: Remove from active_crews when moving away
        if self.last_repair_target and self._agent_manager:
            dp = self._agent_manager.get_damage_point(self.last_repair_target)
            if dp:
                dp.active_crews.discard(self.id)
        self.auto_repair = False
        self.last_repair_target = None

        if self._logger:
            self._logger.info(f"RC {self.id} moving from {self.current_position} to {target_node}")
            self._logger.info(f"  path: {' -> '.join(path)}")
            self._logger.info(f"  total distance: {total_distance} km")
        else:
            print(f"RC {self.id} moving from {self.current_position} to {target_node}")
            print(f"  path: {' -> '.join(path)}")
            print(f"  total distance: {total_distance} km")
        return True

    def repair(self, dp_id: str, repair_efficiency: Optional[float] = None,
               auto_repair: Optional[bool] = None,
               tgraph: 'TGraph' = None, egraph: 'EGraph' = None) -> float:
        """Execute repair command

        Args:
            dp_id: Fault ID
            repair_efficiency: Repair efficiency for this step (p.u./time step)
                             None means use maximum efficiency
            auto_repair: Whether to automatically continue repair
                        None means keep current setting
            tgraph: Traffic graph object
            egraph: Electrical graph object

        Returns:
            Actual resource amount consumed
        """
        # Check state
        if self.state == "moving":
            print(f"RC {self.id} is moving, cannot repair")
            return 0

        if self.remaining_resources <= 0:
            print(f"RC {self.id} resources exhausted, out of service")
            self.state = "out_of_service"  # Out of service after resources exhausted
            return 0

        # Get fault - Use agent_manager for instance-based approach
        if not self._agent_manager:
            print(f"ERROR: RC {self.id} has no agent_manager reference")
            return 0

        dp = self._agent_manager.get_damage_point(dp_id)

        if not dp:
            print(f"fault {dp_id} does not exist")
            return 0

        if dp.state == "repaired":
            print(f"fault {dp_id} already repaired")
            return 0

        # Check position match
        if not self._at_fault_location(dp):
            print(f"RC {self.id} not at fault {dp_id} location")
            return 0

        # CRITICAL: Check DP capacity constraint (MILP dp_cap constraint)
        # If this RC is not in active_crews, need to check if capacity is exceeded
        if self.id not in dp.active_crews:
            if len(dp.active_crews) >= dp.capacity:
                print(f"RC {self.id} cannot repair {dp_id}: capacity limit reached "
                      f"({len(dp.active_crews)}/{dp.capacity} crews already working)")
                return 0

        # If RC switched repair target, remove from old target's active_crews
        if self.last_repair_target and self.last_repair_target != dp_id and self._agent_manager:
            old_dp = self._agent_manager.get_damage_point(self.last_repair_target)
            if old_dp:
                old_dp.active_crews.discard(self.id)

        # Update auto repair setting
        if auto_repair is not None:
            self.auto_repair = auto_repair

        # Determine repair efficiency
        if repair_efficiency is None:
            repair_efficiency = self.efficiency  # Use maximum efficiency
        else:
            repair_efficiency = min(repair_efficiency, self.efficiency)  # Cannot exceed maximum

        # Save planned efficiency (for auto repair)
        self._repaired_this_step = True
        self.planned_efficiency = repair_efficiency

        # Consider resource limits
        actual_efficiency = min(repair_efficiency, self.remaining_resources)

        # Execute repair
        if tgraph and egraph:
            actual_consumed = dp.repair(actual_efficiency, tgraph, egraph)
        else:
            print("Warning: No tgraph and egraph provided, repair may not update graph state")
            return 0

        # Consume resources
        self.remaining_resources -= actual_consumed

        # Check if resources exhausted
        if self.remaining_resources <= 0:
            self.remaining_resources = 0
            # CRITICAL: Remove from active_crews before going out of service
            if self.last_repair_target and self._agent_manager:
                old_dp = self._agent_manager.get_damage_point(self.last_repair_target)
                if old_dp:
                    old_dp.active_crews.discard(self.id)
            self.state = "out_of_service"
            print(f"RC {self.id} resources exhausted after repair, out of service")
        elif dp.state == "repaired":
            # Fault completed with this repair; release the crew immediately.
            self.state = "idle"
            self.auto_repair = False
            self.last_repair_target = None
            print(f"RC {self.id} completed repair of {dp_id}, returning to idle")
        elif actual_consumed > 0:
            # Only set repairing state if actual work was done
            self.state = "repairing"
            self.current_repair_amount = actual_consumed
            self.last_repair_target = dp_id
            # Add this RC to DP's active_crews set
            dp.active_crews.add(self.id)
        else:
            # No work done (fault already repaired) - stop auto repair and return to idle
            self.state = "idle"
            self.auto_repair = False
            self.last_repair_target = None
            print(f"RC {self.id} stopped auto-repair: target {dp_id} already repaired")

        print(f"RC {self.id} repair {dp_id}: planned={repair_efficiency}, actual={actual_consumed}, "
              f"remaining={self.remaining_resources}/{self.total_resources}")

        return actual_consumed

    def stop_repair(self):
        """Stop auto repair"""
        # If currently repairing, remove from active_crews
        if self.last_repair_target and self._agent_manager:
            dp = self._agent_manager.get_damage_point(self.last_repair_target)
            if dp:
                dp.active_crews.discard(self.id)

        self.auto_repair = False
        self.last_repair_target = None
        self.planned_efficiency = None
        if self.state == "repairing":
            self.state = "idle"
        print(f"RC {self.id} stopped auto repair")

    def update_position(self) -> None:
        """Update position (called each time step)"""
        if self.state != "moving":
            return

        # Reduce remaining distance
        self.remaining_distance -= self.speed

        if self.remaining_distance <= 0:
            # Arrived at destination
            self.current_position = self.target_position
            self.target_position = None
            self.remaining_distance = 0
            self.path = []
            self.state = "idle"
            print(f"RC {self.id} arrived at {self.current_position}")
        else:
            print(f"RC {self.id} moving, remaining distance {self.remaining_distance} km")

    def set_out_of_service(self):
        """Manually set RC out of service"""
        # CRITICAL: Remove from active_crews before going out of service
        if self.last_repair_target and self._agent_manager:
            dp = self._agent_manager.get_damage_point(self.last_repair_target)
            if dp:
                dp.active_crews.discard(self.id)
        self.state = "out_of_service"
        self.auto_repair = False
        self.last_repair_target = None
        print(f"RC {self.id} set to out of service")

    def update(self, tgraph: 'TGraph' = None, egraph: 'EGraph' = None) -> None:
        """Update each time step (unified update entry point)

        Args:
            tgraph: Traffic graph object
            egraph: Electrical graph object
        """
        # Out of service state does not need updating
        if self.state == "out_of_service":
            return

        if self.state == "repairing":
            # Repair state only lasts one time step
            self.state = "idle"

            # Remove from previous repair target's active_crews
            if self.last_repair_target and self._agent_manager:
                dp = self._agent_manager.get_damage_point(self.last_repair_target)
                if dp:
                    dp.active_crews.discard(self.id)

            # If auto repair is enabled and has target, continue repair
            if self.auto_repair and self.last_repair_target and tgraph and egraph:
                if not self._repaired_this_step:
                    # Continue repair using saved efficiency
                    self.repair(self.last_repair_target,
                              repair_efficiency=self.planned_efficiency,
                              auto_repair=True,
                              tgraph=tgraph,
                              egraph=egraph)
                else:
                    # Explicit repair already consumed work in this step.
                    dp = self._agent_manager.get_damage_point(self.last_repair_target)
                    if dp and dp.state == "active":
                        self.state = "repairing"
                        dp.active_crews.add(self.id)
        elif self.state == "moving":
            # Update position
            self.update_position()

        self._repaired_this_step = False

    def _at_fault_location(self, dp: 'DP') -> bool:
        """Check if at fault location

        Args:
            dp: Fault object

        Returns:
            Whether at fault location
        """
        # Node fault
        if dp.from_node == dp.to_node and dp.distance == 0:
            return self.current_position == dp.from_node

        # Edge fault - RC must reach exact fault position (fault_node_id) to repair
        if hasattr(dp, 'from_node') and hasattr(dp, 'to_node'):
            # Only allow repair at the exact fault position (fault_node_id)
            if dp.fault_node_id and self.current_position == dp.fault_node_id:
                return True

            # For legacy compatibility: if no fault_node_id, fallback to endpoints
            # But this should not happen with properly configured edge faults
            if not dp.fault_node_id:
                print(f"WARNING: Edge fault {dp.id} has no fault_node_id, using endpoint fallback")
                return self.current_position in [dp.from_node, dp.to_node]

        return False

    @classmethod
    def update_all(cls, tgraph: 'TGraph' = None, egraph: 'EGraph' = None) -> None:
        """Update state of all RCs

        Args:
            tgraph: Traffic graph object
            egraph: Electrical graph object
        """
        for rc in cls.repair_crews.values():
            rc.update(tgraph, egraph)

    @classmethod
    def get_rc(cls, rc_id: str) -> Optional['RC']:
        """Get specified RC (class method for backward compatibility)

        Args:
            rc_id: RC ID

        Returns:
            RC object, or None if it does not exist
        """
        return cls.repair_crews.get(rc_id)

    @staticmethod
    def get_rc_from_manager(agent_manager, rc_id: str) -> Optional['RC']:
        """Get specified RC (from AgentManager for new approach)

        Args:
            agent_manager: AgentManager instance
            rc_id: RC ID

        Returns:
            RC object, or None if it does not exist
        """
        if agent_manager is None:
            return None
        return agent_manager.get_repair_crew(rc_id)

    @classmethod
    def get_all_rcs(cls) -> Dict[str, 'RC']:
        """Get all RCs"""
        return cls.repair_crews.copy()

    @classmethod
    def clear_all(cls):
        """Clear all RCs (used for system reset)"""
        cls.repair_crews.clear()

    def __str__(self) -> str:
        """String representation"""
        return (f"RC(id={self.id}, position={self.current_position}, state={self.state}, "
                f"speed={self.speed}km/h, efficiency={self.efficiency}p.u., "
                f"resources={self.remaining_resources}/{self.total_resources})")

    def __repr__(self) -> str:
        """Detailed representation"""
        return self.__str__()


class Load:
    """Load class - manages all load devices"""

    # Class variable, stores all loads
    loads: Dict[str, 'Load'] = {}

    def __init__(self, load_id: str, node_id: str, P: int, Q: int, W: int, initial_state: str = "off"):
        """Initialize load

        Args:
            load_id: Unique load identifier
            node_id: Electrical node ID where the load is located
            P: Active power demand (kW, integer)
            Q: Reactive power demand (kVar, integer)
            W: Weight (integer, priority)
            initial_state: Initial state ("on" or "off")
        """
        self.id = load_id
        self.node_id = node_id
        self.P = P  # Active power kW
        self.Q = Q  # Reactive power kVar
        self.W = W  # Weight/priority
        self.state = initial_state  # "on" or "off"

        # Agent manager reference (for new instance-based approach)
        self._agent_manager = None

        # Note: Class variable registration removed to support parallel training
        # All instances are now managed through AgentManager only

    @classmethod
    def add(cls, load_id: str, node_id: str, P: int, Q: int, W: int, initial_state: str = "off") -> 'Load':
        """Add new load (class method)

        Args:
            load_id: Unique load identifier
            node_id: Electrical node ID where the load is located
            P: Active power demand (kW, integer)
            Q: Reactive power demand (kVar, integer)
            W: Weight (integer)
            initial_state: Initial state

        Returns:
            Newly created load object
        """
        if load_id in cls.loads:
            raise ValueError(f"Load {load_id} already exists")

        return cls(load_id, node_id, P, Q, W, initial_state)

    def switch_on(self) -> None:
        """Switch load on"""
        old_state = self.state
        self.state = "on"

        # Mark as restored if switched from off to on (service restoration)
        if old_state == "off" and self._agent_manager:
            self._agent_manager.restore_load(self.id)

    def switch_off(self, force_system: bool = False) -> None:
        """Switch load off

        Args:
            force_system: True means system-forced shedding (load shedding), no user constraint check
                         False means manual user operation, needs constraint check

        Note:
            Reliability constraint applies to manual operations.
            force_system=True allows system-driven shedding (e.g. MPS depleted, no power source).
        """
        if self._agent_manager and self._agent_manager.is_load_restored(self.id):
            if not force_system:
                return

        self.state = "off"

    @classmethod
    def operate(cls, load_id: str, action: str) -> None:
        """Operate load (class method)

        Args:
            load_id: Load ID to operate
            action: Operation action ("on" or "off")
        """
        if load_id not in cls.loads:
            raise ValueError(f"Load {load_id} not found")

        load = cls.loads[load_id]

        if action == "on":
            load.switch_on()
        elif action == "off":
            load.switch_off()
        else:
            raise ValueError(f"Invalid action: {action}. Must be 'on' or 'off'")

    @classmethod
    def get_by_node(cls, node_id: str) -> List['Load']:
        """Get all loads at a node

        Args:
            node_id: Node ID

        Returns:
            List of all loads at this node
        """
        return [load for load in cls.loads.values() if load.node_id == node_id]

    @classmethod
    def clear_all(cls) -> None:
        """Clear all loads (used for system reset)"""
        cls.loads.clear()

    @staticmethod
    def get_load_from_manager(agent_manager, load_id: str) -> Optional['Load']:
        """Get load from AgentManager (for new approach)

        Args:
            agent_manager: AgentManager instance
            load_id: Load ID

        Returns:
            Load object, or None if not found
        """
        if agent_manager is None:
            return None
        return agent_manager.get_load(load_id)

    def __str__(self) -> str:
        """String representation"""
        return f"Load(id={self.id}, node={self.node_id}, P={self.P}kW, Q={self.Q}kVar, W={self.W}, state={self.state})"

    def __repr__(self) -> str:
        """Detailed representation"""
        return self.__str__()

class MPS:
    """Mobile Power Source (MPS) class"""

    # Class variables
    mps_units: Dict[str, 'MPS'] = {}
    _logger: Optional[logging.Logger] = None

    def __init__(self, mps_id: str, p_limit: int, s_limit: int, energy: int,
                 initial_position: str, speed: int = 4):
        """Initialize MPS

        Args:
            mps_id: Unique MPS identifier (e.g., "MPS1")
            p_limit: Active power output limit (kW)
            s_limit: Apparent power limit (kVA)
            energy: Initial energy (kWh)
            initial_position: Initial position (traffic graph node ID)
            speed: Movement speed (km/h, default 4)
        """
        self.id = mps_id

        # Capacity parameters
        self.p_limit = p_limit  # kW
        self.s_limit = s_limit  # kVA
        self.energy = energy    # kWh

        # Movement parameters
        self.speed = speed  # km/h - movement speed per MPS

        # Output parameters (calculated later)
        self.Pout = 0  # kW - Actual output after projection
        self.Qout = 0  # kVar - Actual output after projection

        # ⭐ v5.5: Store LLM's requested P/Q for renegotiation
        # When new MPS joins island, ALL MPS re-project based on their P_requested ratios
        self.P_requested = 0  # kW - LLM's requested P (before projection)
        self.Q_requested = 0  # kVar - LLM's requested Q (before projection)

        # Position and state
        self.current_position = initial_position
        self.state = "idle"  # idle/moving/connected/out_of_service

        # Movement related
        self.target_position = None
        self.remaining_distance = 0  # km
        self.path = []  # Movement path

        # Connection related
        self.connected_node = None  # Connected electrical node
        self.edge_id = None  # Edge ID in electrical graph

        # Target load list (selective power supply)
        self.target_loads = []  # List[str]: List of load IDs to serve
                                # Empty list means target_loads must be explicitly specified

        # Stay constraint counter (MILP: useMPS[s,t] <= stay[s,t])
        # MPS must stay at a node for at least 1 time step before connecting.
        # Initialized to 1 because MPS starts stationary at its initial position.
        self.steps_at_current_node = 1

        # Agent manager reference (for new instance-based approach)
        self._agent_manager = None

        # Note: Class variable registration removed to support parallel training
        # All instances are now managed through AgentManager only

    @classmethod
    def set_logger(cls, logger: logging.Logger):
        """Set class-level logger"""
        cls._logger = logger

    @classmethod
    def add(cls, mps_id: str, p_limit: int, s_limit: int, energy: int,
            initial_position: str, egraph: 'EGraph', speed: int = 4) -> 'MPS':
        """Add new MPS and create node in electrical graph

        Args:
            mps_id: Unique MPS identifier
            p_limit: Active power output limit (kW)
            s_limit: Apparent power limit (kVA)
            energy: Initial energy (kWh)
            initial_position: Initial position (traffic graph node ID)
            egraph: Electrical graph object
            speed: Movement speed (km/h, default 4)

        Returns:
            Newly created MPS object
        """
        if mps_id in cls.mps_units:
            # Silently return existing MPS during restore operations
            if hasattr(cls, '_restore_mode') and cls._restore_mode:
                return cls.mps_units[mps_id]
            raise ValueError(f"MPS {mps_id} already exists")

        # Create MPS instance (pass speed parameter)
        mps = cls(mps_id, p_limit, s_limit, energy, initial_position, speed)

        # Only log during initial creation, not during restore
        if not hasattr(cls, '_restore_mode') or not cls._restore_mode:
            message = f"MPS {mps_id} added: pos={initial_position}, p_limit={p_limit}kW, energy={energy}kWh"
            if cls._logger:
                cls._logger.info(message)
            else:
                print(message)

        # Add MPS node in electrical graph (always present, but initially not connected)
        try:
            from graphs import NodeType
            egraph.add_node(mps_id, NodeType.MPS)
        except ImportError:
            # If import fails, use string as fallback
            egraph.add_node(mps_id, 'MPS')

        return mps

    def move(self, target_node: str, tgraph: 'TGraph') -> bool:
        """Move to target node

        Args:
            target_node: Target node ID
            tgraph: Traffic graph object

        Returns:
            Whether movement started successfully
        """
        # Check state
        # Allow out_of_service MPS to move (to clear node locations)
        # Movement does not consume energy, only power supply does
        if self.state == "moving":
            print(f"MPS {self.id} is moving, cannot accept new move command")
            return False

        # If currently connected, cannot move
        if self.state == "connected":
            print(f"MPS {self.id} is connected and supplying power, cannot move")
            return False

        # Check if already at target position - this should be successful (no-op)
        if self.current_position == target_node:
            print(f"MPS {self.id} already at target position {target_node}")
            # Already at target - this is a successful no-op, not an error
            self.state = "idle"  # Ensure state is idle since we're at target
            return True

        # Use shortest path algorithm
        path, total_distance = tgraph.find_shortest_path(self.current_position, target_node)

        if not path or total_distance < 0:
            # Only print path errors during initial simulation, not during restore
            if not hasattr(self.__class__, '_restore_mode') or not self.__class__._restore_mode:
                if self._logger:
                    self._logger.warning(f"cannot find path from {self.current_position} to {target_node} path")
                else:
                    print(f"cannot find path from {self.current_position} to {target_node} path")
            return False

        # Set movement parameters
        self.target_position = target_node
        self.remaining_distance = total_distance
        self.path = path
        self.state = "moving"
        self.steps_at_current_node = 0  # Reset stay counter when departing

        print(f"MPS {self.id} moving from {self.current_position} to {target_node}")
        print(f"  path: {' -> '.join(path)}")
        print(f"  total distance: {total_distance} km")
        return True

    def update_position(self) -> None:
        """Update position (called each time step)

        Stay constraint (MILP alignment):
        - When not moving, increment steps_at_current_node each step.
        - When arriving at destination, reset to 0 (just arrived, hasn't stayed yet).
        - MPS can only connect() after steps_at_current_node >= 1.
        """
        if self.state != "moving":
            # MPS is stationary (idle/connected/out_of_service) — increment stay counter
            self.steps_at_current_node += 1
            return

        # Reduce remaining distance (using each MPS's own speed)
        self.remaining_distance -= self.speed

        if self.remaining_distance <= 0:
            # Arrived at destination
            self.current_position = self.target_position
            self.target_position = None
            self.remaining_distance = 0
            self.state = "idle"
            self.steps_at_current_node = 0  # Just arrived, reset counter
            print(f"MPS {self.id} arrived at {self.current_position}")
        else:
            print(f"MPS {self.id} moving, remaining distance {self.remaining_distance}km")

    def connect(self, egraph: 'EGraph', target_loads: List[str] = None) -> bool:
        """Connect to the electrical node at current position and specify loads to serve

        Args:
            egraph: Electrical graph object
            target_loads: List of load IDs to serve
                         Must be explicitly specified, e.g., ['L_N3', 'L_N4', 'L_N5']

        Returns:
            Whether connection was successful
        """
        # Check state - can only connect when idle (must be stationary and not connected)
        if self.state != "idle":
            print(f"MPS {self.id} current state is {self.state}, can only connect when idle")
            return False

        # Stay constraint (MILP: useMPS[s,t] <= stay[s,t])
        # MPS must stay at node for at least 1 time step before connecting
        if self.steps_at_current_node < 1:
            print(f"MPS {self.id} must stay at node for at least 1 time step before connecting "
                  f"(steps_at_current_node={self.steps_at_current_node})")
            return False

        if self.energy <= 0:
            print(f"MPS {self.id} out of energy, cannot connect")
            return False

        # Check if current position exists in electrical graph
        if self.current_position not in egraph.nodes:
            print(f"Current position {self.current_position} not in electrical graph")
            return False

        # Check for active node-type faults at current position
        # MILP constraint (Part 4.55): MPS cannot park at or connect to a node
        # that has an active (unrepaired) node-type fault
        if self._agent_manager:
            for dp in self._agent_manager.damage_points.values():
                if (dp.state == "active" and
                        dp.from_node == dp.to_node and dp.distance == 0 and
                        dp.from_node == self.current_position):
                    print(f"MPS {self.id} cannot connect at {self.current_position}: "
                          f"active node-type fault {dp.id}")
                    return False

        # Validate target load list (must be explicitly specified)
        # CRITICAL: Validate before modifying state to avoid partial success
        if target_loads is None or len(target_loads) == 0:
            print(f"ERROR: MPS {self.id} cannot connect without target_loads")
            print(f"  You must specify which loads this MPS should serve")
            print(f"  Example: mps.connect(egraph, target_loads=['L_N3', 'L_N4'])")
            return False  # Reject connection

        # First add MPS node to electrical graph (if not exists)
        from .graphs import NodeType
        if self.id not in egraph.nodes:
            egraph.add_node(self.id, NodeType.MPS)

        # Create connection edge
        self.edge_id = f"E_{self.current_position}_{self.id}"
        egraph.add_edge(self.edge_id, self.current_position, self.id, is_connected=True)

        # Update state
        self.connected_node = self.current_position
        self.state = "connected"

        # Set target load list
        self.target_loads = target_loads.copy()  # Copy list to avoid external modification

        # Initial output is 0, waiting for LLM to explicitly set via set_output()
        self.Pout = 0
        self.Qout = 0
        self.P_requested = 0  # v5.5: Reset requested values on connect
        self.Q_requested = 0

        # Connection successful, print info
        print(f"MPS {self.id} connected to node {self.current_position}")
        print(f"  Target loads: {self.target_loads} ({len(self.target_loads)} loads)")
        print(f"  Initial output: P=0kW, Q=0kVar (awaiting set_output command)")
        print(f"  Capacity: P_max={self.p_limit}kW, S_max={self.s_limit}kVA")

        return True

    def disconnect(self, egraph: 'EGraph') -> bool:
        """Disconnect

        Args:
            egraph: Electrical graph object

        Returns:
            Whether disconnection was successful
        """
        # Allow disconnect for both "connected" and "out_of_service" states
        # (out_of_service MPS may still have edge connection)
        if self.state not in ["connected", "out_of_service"]:
            print(f"MPS {self.id} not connected (state={self.state}), no need to disconnect")
            return False

        # If out_of_service but not actually connected, skip
        if self.state == "out_of_service" and not self.connected_node:
            print(f"MPS {self.id} already disconnected")
            return False

        # Delete connection edge
        if self.edge_id in egraph.edges:
            del egraph.edges[self.edge_id]
            print(f"removed edge {self.edge_id}")

        # Remove MPS node from egraph to avoid orphaned nodes
        if self.id in egraph.nodes:
            del egraph.nodes[self.id]

        # Reset connection-related attributes
        self.connected_node = None
        self.edge_id = None

        # Clear target load list
        self.target_loads = []

        # Preserve out_of_service state if MPS is depleted
        # Otherwise set to idle (normal disconnect)
        if self.state != "out_of_service":
            self.state = "idle"

        # Reset output
        self.Pout = 0
        self.Qout = 0
        self.P_requested = 0  # v5.5: Reset requested values on disconnect
        self.Q_requested = 0

        print(f"MPS {self.id} disconnected (state: {self.state})")
        return True

    def update_energy(self) -> None:
        """Update energy (called each time step)"""
        if self.state != "connected":
            return

        # Energy consumption = Pout * 1 hour
        self.energy -= self.Pout

        if self.energy <= 0:
            self.energy = 0
            # MPS depletes: transition to out_of_service
            # Note: egraph edge removal will be handled by environment calling disconnect()
            print(f"MPS {self.id} out of energy, transitioning to out_of_service")

            # Transition to out_of_service state
            # connected_node will be cleared when environment calls disconnect()
            self.state = "out_of_service"
            self.Pout = 0  # Stop power output
            self.Qout = 0
            self.P_requested = 0  # v5.5: Reset requested values on depletion
            self.Q_requested = 0
            print(f"MPS {self.id} now out_of_service (environment will handle disconnection)")

    def set_output(self, P_out: float, Q_out: float, target_loads: List[str], egraph: 'EGraph' = None) -> Dict[str, Any]:
        """Set MPS output power (LLM action) - v5.1 simplified version

        If MPS is not connected, will auto-connect to current position.
        Each call updates target_loads.

        Args:
            P_out: Active power output (kW)
            Q_out: Reactive power output (kVar)
            target_loads: List of load IDs to serve (required parameter)
            egraph: Electrical graph object (only needed for auto-connect)

        Returns:
            Result dict containing status, message and constraint info
        """
        import math

        # 0. Integer conversion - force output to integer, simplify LLM learning (avoid floating point precision issues)
        # Keep the sign of Q_out to match the MILP/action semantics.
        P_out = round(float(P_out))
        Q_out = round(float(Q_out))

        # Enforce MPS capacity limits
        if P_out > self.p_limit:
            P_out = self.p_limit
        # Check apparent power constraint using |S| = sqrt(P^2 + Q^2) <= S_limit.
        S_check = math.sqrt(P_out**2 + Q_out**2)
        if self.s_limit > 0 and S_check > self.s_limit:
            scale = self.s_limit / S_check
            P_out = round(P_out * scale)
            Q_out = round(Q_out * scale)

        # 0.5. Validate target_loads (must be provided)
        if not target_loads or len(target_loads) == 0:
            return {
                "status": "invalid",
                "message": f"MPS {self.id}: target_loads is required and cannot be empty. "
                          f"Example: set_mps_output('{self.id}', 100, 60, target_loads=['L_N3', 'L_N4'])",
                "reason": "target_loads_required",
                "mps_id": self.id
            }

        # 1. State check - if not connected, auto-connect
        if self.state != "connected":
            if self.state == "idle":
                # Stay constraint check (MILP: useMPS[s,t] <= stay[s,t])
                if self.steps_at_current_node < 1:
                    return {
                        "status": "invalid",
                        "message": f"MPS {self.id} must stay at node for at least 1 time step before "
                                  f"connecting (just arrived, steps_at_current_node={self.steps_at_current_node}). "
                                  f"Wait until next time step to set output.",
                        "reason": "stay_constraint",
                        "mps_id": self.id,
                        "steps_at_current_node": self.steps_at_current_node
                    }

                # Auto-connect to current position
                if egraph is None:
                    return {
                        "status": "invalid",
                        "message": f"MPS {self.id} not connected and egraph not provided for auto-connect",
                        "reason": "egraph_required",
                        "mps_id": self.id
                    }

                # Execute auto-connect
                success = self.connect(egraph, target_loads=target_loads)
                if not success:
                    return {
                        "status": "invalid",
                        "message": f"MPS {self.id} failed to auto-connect at {self.current_position}",
                        "reason": "auto_connect_failed",
                        "mps_id": self.id
                    }
                print(f"MPS {self.id} auto-connected to {self.current_position} with target_loads={target_loads}")
            else:
                return {
                    "status": "invalid",
                    "message": f"MPS {self.id} cannot set output: invalid state '{self.state}'. "
                              f"MPS must be idle or connected.",
                    "reason": "invalid_state",
                    "mps_id": self.id,
                    "current_state": self.state
                }
        else:
            # Already connected, update target_loads
            self.target_loads = target_loads.copy()
            print(f"MPS {self.id} target_loads updated: {target_loads}")

        # 2. Energy check - must have remaining energy
        if self.energy <= 0:
            return {
                "status": "invalid",
                "message": f"MPS {self.id} cannot set output: no energy remaining (energy={self.energy}kWh)",
                "reason": "no_energy",
                "mps_id": self.id,
                "energy": self.energy
            }

        # 3. Active power lower bound check - P >= 0 (negative power has no physical meaning)
        if P_out < 0:
            return {
                "status": "invalid",
                "message": f"MPS {self.id}: P_out={P_out:.1f}kW violates constraint P >= 0",
                "reason": "p_negative",
                "mps_id": self.id,
                "P_out": P_out,
                "P_max": self.p_limit
            }

        # Note: No P_max check here because P is a ratio indicator, not the final output.
        # Actual output is determined by projection based on island load demand.

        # 4. All constraints satisfied, apply output
        # Note: No S_max check here because P/Q are ratio indicators, not final outputs.
        # Actual outputs are determined by projection based on island load demand.
        S_out = math.sqrt(P_out**2 + Q_out**2)
        self.Pout = P_out
        self.Qout = Q_out

        # ⭐ v5.5: Store requested P/Q for renegotiation
        # These values are preserved even after projection, allowing consistent renegotiation
        # when new MPS joins the same island
        self.P_requested = P_out
        self.Q_requested = Q_out

        print(f"MPS {self.id} output set: P={P_out:.1f}kW, Q={Q_out:.1f}kVar, S={S_out:.1f}kVA")

        return {
            "status": "success",
            "message": f"MPS {self.id} output set to P={P_out:.1f}kW, Q={Q_out:.1f}kVar",
            "mps_id": self.id,
            "P_out": P_out,
            "Q_out": Q_out,
            "S_out": S_out,
            "P_max": self.p_limit,
            "S_max": self.s_limit
        }

    def calculate_output(self, island_loads: List) -> Tuple[int, int]:
        """Calculate actual MPS output (to be implemented)

        Args:
            island_loads: List of loads in the island

        Returns:
            (Pout, Qout)
        """
        # TODO: Implement specific calculation logic later
        # Temporarily return 0
        self.Pout = 0
        self.Qout = 0
        self.P_requested = 0  # v5.5: Reset requested values
        self.Q_requested = 0
        return self.Pout, self.Qout

    @classmethod
    def update_all(cls, tgraph: 'TGraph' = None) -> None:
        """Update state of all MPS (called each time step)

        Args:
            tgraph: Traffic graph object (for updating position)
        """
        for mps in cls.mps_units.values():
            # Allow out_of_service MPS to update position (they can still move)
            # Only skip energy updates for out_of_service

            # Update position (works for all states including out_of_service)
            mps.update_position()

            # Update energy (only for connected state, update_energy handles the check)
            mps.update_energy()

    @classmethod
    def get_mps(cls, mps_id: str) -> Optional['MPS']:
        """Get specified MPS (class method for backward compatibility)

        Args:
            mps_id: MPS ID

        Returns:
            MPS object, or None if it does not exist
        """
        return cls.mps_units.get(mps_id)

    @staticmethod
    def get_mps_from_manager(agent_manager, mps_id: str) -> Optional['MPS']:
        """Get specified MPS (from AgentManager for new approach)

        Args:
            agent_manager: AgentManager instance
            mps_id: MPS ID

        Returns:
            MPS object, or None if it does not exist
        """
        if agent_manager is None:
            return None
        return agent_manager.get_mobile_power_source(mps_id)

    @classmethod
    def get_all_mps(cls) -> Dict[str, 'MPS']:
        """Get all MPS"""
        return cls.mps_units.copy()

    @classmethod
    def clear_all(cls) -> None:
        """Clear all MPS (used for system reset)"""
        cls.mps_units.clear()

    def get_capacity(self) -> Tuple[int, int]:
        """Get MPS capacity

        Returns:
            (P_limit, S_limit)
        """
        if self.state == "out_of_service":
            return 0, 0
        return self.p_limit, self.s_limit

    def __str__(self) -> str:
        """String representation"""
        return (f"MPS(id={self.id}, position={self.current_position}, state={self.state}, "
                f"speed={self.speed}km/h, energy={self.energy}kWh, "
                f"P_limit={self.p_limit}kW, S_limit={self.s_limit}kVA)")

    def __repr__(self) -> str:
        """Detailed representation"""
        return self.__str__()

class DP:
    """Damage Point (DP) class"""

    # Class variable, stores all faults
    faults: Dict[str, 'DP'] = {}
    _logger: Optional[logging.Logger] = None

    def __init__(self, dp_id: str, from_node: str, to_node: str, distance: int, repair_demand: int, capacity: int = 1):
        """Initialize fault

        Args:
            dp_id: Unique fault identifier (e.g., "DP1")
            from_node: Start node
            to_node: End node (if equal to from_node, indicates node fault)
            distance: Distance from from_node (km)
            repair_demand: Repair demand (p.u.)
            capacity: Maximum number of crews working simultaneously (default=1)
        """
        self.id = dp_id
        self.from_node = from_node
        self.to_node = to_node
        self.distance = distance
        self.repair_demand = repair_demand
        self.repair_progress = 0.0  # Current repair progress
        self.state = "active"  # active/repaired
        self.capacity = capacity  # Maximum number of crews working simultaneously
        self.active_crews = set()  # Set of RC IDs currently working on this DP (for capacity constraint check)

        # Associated graph elements
        self.fault_node_id = None  # Node ID created in traffic graph (for edge faults)
        self.affected_edge_id = None  # Affected electrical edge ID
        self.split_edges = []  # List of edge IDs after splitting in traffic graph

        # Agent manager reference (for new instance-based approach)
        self._agent_manager = None

        # Note: Class variable registration removed to support parallel training
        # All instances are now managed through AgentManager only

    @classmethod
    def set_logger(cls, logger: logging.Logger):
        """Set class-level logger"""
        cls._logger = logger

    @classmethod
    def add(cls, dp_id: str, location: Tuple[str, str, int], repair_demand: int,
            tgraph: 'TGraph', egraph: 'EGraph') -> 'DP':
        """Add fault and update graph

        Args:
            dp_id: Unique fault identifier
            location: (from_node, to_node, distance) position tuple
            repair_demand: Repair demand (p.u.)
            tgraph: Traffic graph object
            egraph: Electrical graph object

        Returns:
            Newly created DP object
        """
        if dp_id in cls.faults:
            # Silently return existing DP during restore operations
            if not hasattr(cls, '_restore_mode') or not cls._restore_mode:
                print(f"Warning: DP {dp_id} already exists, skipping creation")
            return cls.faults[dp_id]

        from_node, to_node, distance = location

        # Create DP instance
        dp = cls(dp_id, from_node, to_node, distance, repair_demand)

        # Update traffic graph
        if from_node == to_node and distance == 0:
            # Node fault
            dp._apply_node_fault(from_node, tgraph, egraph)
        else:
            # Edge fault
            dp._apply_edge_fault(from_node, to_node, distance, tgraph, egraph)

        # Only log during initial creation, not during restore
        if not hasattr(cls, '_restore_mode') or not cls._restore_mode:
            message = f"fault {dp_id} added: pos=({from_node},{to_node},{distance}), repair_demand={repair_demand}"
            if cls._logger:
                cls._logger.info(message)
            else:
                print(message)
        return dp

    def _apply_node_fault(self, node_id: str, tgraph: 'TGraph', egraph: 'EGraph'):
        """Apply node fault

        Args:
            node_id: Fault node ID
            tgraph: Traffic graph
            egraph: Electrical graph
        """
        # Use TGraph method to mark node fault
        tgraph.add_dp_to_node(node_id, self.id)
        print(f"  traffic graph: node {node_id} marked as fault")

        # CRITICAL FIX: Mark all edges connected to faulted node as 'faulted'
        affected_edges = []
        for edge_id, edge in egraph.edges.items():
            if edge.from_node == node_id or edge.to_node == node_id:
                affected_edges.append(edge_id)
                edge.state = 'faulted'

        if affected_edges:
            self.affected_node_edges = affected_edges  # Store for repair completion
            print(f"  electrical graph: node fault affects edges {affected_edges}, all marked as 'faulted'")

    def _apply_edge_fault(self, from_node: str, to_node: str, distance: int,
                          tgraph: 'TGraph', egraph: 'EGraph'):
        """Apply edge fault

        Args:
            from_node: Start node
            to_node: End node
            distance: Distance from from_node
            tgraph: Traffic graph
            egraph: Electrical graph
        """
        # Insert fault node in traffic graph and split edge
        self.fault_node_id = self.id  # Use DP's ID as node ID

        # Find original edge
        original_edge = None
        for edge_id, edge in tgraph.edges.items():
            if ((edge.from_node == from_node and edge.to_node == to_node) or
                (edge.from_node == to_node and edge.to_node == from_node)):
                original_edge = edge
                original_edge_id = edge_id
                break

        if original_edge:
            # Calculate original edge length
            total_distance = original_edge.distance

            # Add fault node
            tgraph.add_node(self.fault_node_id)
            tgraph.nodes[self.fault_node_id].is_fault = True

            # Create two new edges
            if original_edge.from_node == from_node:
                # Forward direction
                edge1_id = f"{original_edge_id}_1_{self.id}"
                edge2_id = f"{original_edge_id}_2_{self.id}"
                tgraph.add_edge(edge1_id, from_node, self.fault_node_id, distance)
                tgraph.add_edge(edge2_id, self.fault_node_id, to_node, total_distance - distance)
            else:
                # Reverse direction
                edge1_id = f"{original_edge_id}_1_{self.id}"
                edge2_id = f"{original_edge_id}_2_{self.id}"
                tgraph.add_edge(edge1_id, to_node, self.fault_node_id, total_distance - distance)
                tgraph.add_edge(edge2_id, self.fault_node_id, from_node, distance)

            self.split_edges = [edge1_id, edge2_id]

            # Delete original edge
            del tgraph.edges[original_edge_id]

            message = f"  traffic graph: edge {original_edge_id} split into {edge1_id} and {edge2_id}"
            if self._logger:
                self._logger.info(message)
            else:
                print(message)

        # Record affected electrical edge and set state to faulted
        for edge_id, edge in egraph.edges.items():
            if ((edge.from_node == from_node and edge.to_node == to_node) or
                (edge.from_node == to_node and edge.to_node == from_node)):
                self.affected_edge_id = edge_id
                # CRITICAL FIX: Set edge state to 'faulted'
                edge.state = 'faulted'
                message = f"  electrical graph: edge {edge_id} affected by fault, state set to 'faulted'"
                if self._logger:
                    self._logger.info(message)
                else:
                    print(message)
                break

    def repair(self, amount: float, tgraph: 'TGraph', egraph: 'EGraph') -> float:
        """Accept repair

        Args:
            amount: Repair work amount provided by RC (p.u.)
            tgraph: Traffic graph object
            egraph: Electrical graph object

        Returns:
            Actual repair amount consumed
        """
        if self.state == "repaired":
            return 0.0

        # Calculate remaining demand
        remaining = self.repair_demand - self.repair_progress
        actual_repair = min(amount, remaining)

        # Update progress
        self.repair_progress += actual_repair

        # Check if completed
        if self.repair_progress >= self.repair_demand:
            self.state = "repaired"
            print(f"fault {self.id} repair completed")
            # Clear active_crews (all RCs leave after repair is completed)
            self.active_crews.clear()
            # Automatically update graph state
            self.complete_repair(tgraph, egraph)

        return actual_repair

    def complete_repair(self, tgraph: 'TGraph', egraph: 'EGraph'):
        """Post-repair completion handling

        Args:
            tgraph: Traffic graph
            egraph: Electrical graph
        """
        if self.state != "repaired":
            return

        # Update traffic graph
        if self.from_node == self.to_node and self.distance == 0:
            # Node fault repair
            if self.from_node in tgraph.nodes:
                tgraph.nodes[self.from_node].is_fault = False
                print(f"  traffic graph: node {self.from_node} fault cleared")
        elif self.fault_node_id:
            # Edge fault repair - fault node marked as non-fault (but node is kept)
            if self.fault_node_id in tgraph.nodes:
                tgraph.nodes[self.fault_node_id].is_fault = False
                print(f"  traffic graph: fault node {self.fault_node_id} marked as repaired")

        # CRITICAL FIX: Reset electrical edge state back to operational
        if hasattr(self, 'affected_edge_id') and self.affected_edge_id:
            if self.affected_edge_id in egraph.edges:
                egraph.edges[self.affected_edge_id].state = 'operational'
                print(f"  electrical graph: edge {self.affected_edge_id} state reset to 'operational'")

        # CRITICAL FIX: Reset all edges affected by node fault
        if hasattr(self, 'affected_node_edges') and self.affected_node_edges:
            for edge_id in self.affected_node_edges:
                if edge_id in egraph.edges:
                    egraph.edges[edge_id].state = 'operational'
                    print(f"  electrical graph: edge {edge_id} state reset to 'operational' (node fault repair)")

        # Electrical graph connectivity will be auto-updated via check_edge_connectivity
        print(f"  electrical graph: connectivity of related edges will auto-recover")

    @classmethod
    def check_edge_affected(cls, edge_id: str, egraph: 'EGraph') -> bool:
        """Check if electrical edge is affected by fault

        Args:
            edge_id: Electrical edge ID
            egraph: Electrical graph object

        Returns:
            True if affected by fault and cannot connect
        """
        edge = egraph.edges.get(edge_id)
        if not edge:
            return False

        # Check all active faults
        for dp in cls.faults.values():
            if dp.state == "active":
                # Check node fault
                if dp.from_node == dp.to_node and dp.distance == 0:
                    # Node fault affects all connected edges
                    if edge.from_node == dp.from_node or edge.to_node == dp.from_node:
                        return True
                # Check edge fault
                elif dp.affected_edge_id == edge_id:
                    return True

        return False

    @classmethod
    def get_all_faults(cls) -> Dict[str, 'DP']:
        """Get all faults"""
        return cls.faults.copy()

    @classmethod
    def get_active_faults(cls) -> List['DP']:
        """Get all active faults"""
        return [dp for dp in cls.faults.values() if dp.state == "active"]

    @classmethod
    def get_fault(cls, dp_id: str) -> Optional['DP']:
        """Get specified fault (class method for backward compatibility)"""
        return cls.faults.get(dp_id)

    @staticmethod
    def get_fault_from_manager(agent_manager, dp_id: str) -> Optional['DP']:
        """Get specified fault (from AgentManager for new approach)

        Args:
            agent_manager: AgentManager instance
            dp_id: Fault ID

        Returns:
            DP object, or None if it does not exist
        """
        if agent_manager is None:
            return None
        return agent_manager.get_damage_point(dp_id)

    @classmethod
    def clear_all(cls):
        """Clear all faults (used for system reset)"""
        cls.faults.clear()

    def __str__(self) -> str:
        """String representation"""
        location = f"({self.from_node},{self.to_node},{self.distance})"
        return (f"DP(id={self.id}, location={location}, "
                f"state={self.state}, progress={self.repair_progress}/{self.repair_demand})")

    def __repr__(self) -> str:
        """Detailed representation"""
        return self.__str__()
