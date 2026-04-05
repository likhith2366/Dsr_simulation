"""
DSR Environment - Simulation Environment State Management and Time Stepping
============================================================================

This module manages the simulation environment's global state and time advancement logic.

Core responsibilities:
- Holds TGraph (traffic graph) and EGraph (electrical graph) instances
- Manages simulation time (current_time)
- step(): Core loop for each time step:
  1. Update all RC states (movement / auto-repair)
  2. Update all MPS states (movement / energy consumption)
  3. Detect newly completed fault repairs -> may trigger loops -> auto-open switch to break loop
  4. Detect MPS energy depletion -> auto-disconnect
  5. Call egraph.update_system_state() to update all load power supply states
  6. Collect events and return them to the caller

Event types:
- fault_repaired: Fault repair completed
- mps_depleted: MPS energy depleted
- mps_grid_restored: MPS auto-disconnected after Grid reconnection
- cycle_auto_resolved_after_repair: Repair-induced loop resolved by auto-opening a switch

Key design:
- update_switch_effects(): Apply all switch states to electrical graph, detect loops
- _apply_switch_state(): Map a single switch state to its controlled electrical edges
- _auto_resolve_repair_cycle(): If a loop forms after fault repair, auto-open a switch to break it
- _calculate_weighted_power(): Calculate current weighted power supply sum(W*P)
"""

from typing import Dict, List, Optional, Set, Any
import math
import logging
from .graphs import TGraph, EGraph, NodeType


class IndependentDSREnvironment:
    """Independent DSR Environment using AgentManager for parallel training

    This class provides true instance isolation for parallel training,
    replacing the deprecated DSREnvironment which used class-level storage.
    """

    def __init__(self, agent_manager=None):
        """Initialize independent DSR environment"""
        # Initialize base graphs and time
        self.tgraph = TGraph()
        self.egraph = EGraph()
        self.current_time = 0
        self.simulation_state = "initialized"

        # Event deduplication tracking (instance-specific)
        self._emitted_fault_repaired: Set[str] = set()
        self._emitted_mps_depleted: Set[str] = set()

        # Agent manager reference (injected by IndependentDSRInterface)
        self.agent_manager = agent_manager

        # Inject agent_manager into egraph for MPS/Load access
        self.egraph.agent_manager = agent_manager

    def reset(self, preserve_graphs: bool = False) -> None:
        """Reset environment using agent manager - COMPLETE reset for new episode/epoch"""
        # Clear instance-specific agent state
        self.agent_manager.clear_all()

        # Reset time and simulation state (CRITICAL: prevents state leakage across epochs)
        self.current_time = 0
        self.simulation_state = "reset"

        # Clear event tracking (CRITICAL: allows events to fire again in new epoch)
        self._emitted_fault_repaired.clear()
        self._emitted_mps_depleted.clear()

        # Reset graphs if needed (for complete environment reset)
        if not preserve_graphs:
            self.tgraph = TGraph()
            self.egraph = EGraph()
            # Re-inject agent_manager into new egraph
            self.egraph.agent_manager = self.agent_manager

    def reset_episode(self, preserve_graphs: bool = True) -> None:
        """Reset for new episode using agent manager"""
        # Reset restoration state for instance
        self.agent_manager.reset_restoration_state()

        # Reset time and simulation state
        self.current_time = 0
        self.simulation_state = "reset"

        # Clear event tracking
        self._emitted_fault_repaired.clear()
        self._emitted_mps_depleted.clear()

        # Reset graphs unless we want to preserve underlying topology
        if not preserve_graphs:
            self.tgraph = TGraph()
            self.egraph = EGraph()
            # Re-inject agent_manager into new egraph
            self.egraph.agent_manager = self.agent_manager

    def update_switch_effects(self, allow_faulted: bool = False, revert_on_cycle: bool = True, original_states: Dict[str, str] = None) -> Dict[str, Any]:
        """Update edge connectivity and detect cycles

        Args:
            allow_faulted: If True, force faulted edges to disconnected (initialization).
                          If False, skip faulted edges (runtime).
            revert_on_cycle: If True, revert switches when cycle detected (for LLM actions).
                           If False, keep state even with cycle (for damage repair).

        Returns:
            Dict with cycle info:
                - cycle_detected: bool
                - weighted_power: float
        """
        import logging
        logger = logging.getLogger(__name__)

        switches = self.agent_manager.switches

        # Record initial switch states
        if original_states is not None:
            initial_states = dict(original_states)  # Use caller-provided original states
        else:
            initial_states = {sid: s.state for sid, s in switches.items()}

        # Apply all switch states
        for switch_id, switch in switches.items():
            # Standardize state to "open"/"close"
            if switch.state == "closed":
                switch.state = "close"

            self._apply_switch_state(switch, allow_faulted=allow_faulted)
            logger.debug(f"Applied switch {switch_id} state: {switch.state}")

        # Check for cycles with detailed information
        cycle_detected = self.egraph.has_cycle()
        cycle_details = None

        if cycle_detected:
            # Get detailed cycle information for LLM feedback
            if hasattr(self.egraph, 'detect_cycle_with_details'):
                try:
                    cycle_details = self.egraph.detect_cycle_with_details()
                except:
                    cycle_details = None

            if revert_on_cycle:
                # Revert switches (for LLM invalid actions)
                logger.warning("Cycle detected - INVALID ACTION - reverting switches")
                for switch_id, switch in switches.items():
                    switch.state = initial_states[switch_id]
                    self._apply_switch_state(switch, allow_faulted=allow_faulted)
                logger.info("Reverted all switches to initial states")
            else:
                # Allow cycle to exist (for damage repair - LLM must fix it)
                logger.warning("Cycle detected after damage repair - LLM must resolve")
        else:
            logger.debug("No cycles detected, topology is radial")

        # Calculate final weighted power
        weighted_power = self._calculate_weighted_power()

        result = {
            'cycle_detected': cycle_detected,
            'weighted_power': weighted_power
        }

        # Include cycle details if available
        if cycle_details:
            result['cycle_details'] = cycle_details

        return result

    def step(self) -> Dict:
        """Advance simulation by one time step using agent manager"""
        self.current_time += 1

        # Update repair crews
        for rc in self.agent_manager.repair_crews.values():
            rc.update(self.tgraph, self.egraph)

        # Update mobile power sources
        for mps in self.agent_manager.mobile_power_sources.values():
            # Allow out_of_service MPS to update position (they can still move)
            # Only skip energy updates for out_of_service
            mps.update_position()  # Update movement (works for all states including out_of_service)
            mps.update_energy()    # Handle energy consumption (update_energy checks state internally)

        # Check for newly completed faults FIRST (to determine if cycle check is needed)
        newly_completed_faults = []
        for dp in self.agent_manager.damage_points.values():
            if dp.state == "repaired" and dp.id not in self._emitted_fault_repaired:
                self._emitted_fault_repaired.add(dp.id)
                newly_completed_faults.append(dp.id)

        # Check for cycles after damage repair (topology changes)
        # - DP repair: edge changes from 'faulted' to 'healthy' → topology MAY form cycles
        # - Must update switch effects first to reconnect repaired edges
        # - Auto-resolve: open a switch in the cycle to break it (no penalty for repair-induced cycles)
        cycle_auto_resolved = False
        auto_resolved_switch = None
        if newly_completed_faults:
            # Update switch effects to reconnect repaired edges based on current switch states
            # allow_faulted=False: skip remaining faulted edges
            # revert_on_cycle=False: don't revert, just detect
            cycle_info = self.update_switch_effects(allow_faulted=False, revert_on_cycle=False)
            if cycle_info.get('cycle_detected', False):
                # Auto-resolve: find a closed switch in the cycle and open it
                auto_resolved_switch = self._auto_resolve_repair_cycle()
                cycle_auto_resolved = auto_resolved_switch is not None

        # Collect events for this step
        events = []

        # Notify LLM that cycle was auto-resolved (informational, no penalty)
        if cycle_auto_resolved:
            events.append({
                "type": "cycle_auto_resolved_after_repair",
                "repaired_faults": newly_completed_faults,
                "opened_switch": auto_resolved_switch,
                "message": f"Repair created loop → system auto-opened {auto_resolved_switch} to maintain radial topology.",
                "time": self.current_time
            })

        # Fault repaired event
        if newly_completed_faults:
            events.append({
                "type": "fault_repaired",  # Match reward calculator expectation (singular)
                "fault_ids": newly_completed_faults,
                "time": self.current_time
            })

        # Check for newly depleted MPS units
        newly_depleted_mps = []
        depleted_load_ids = []
        for mps in self.agent_manager.mobile_power_sources.values():
            if mps.energy <= 0 and mps.id not in self._emitted_mps_depleted:
                self._emitted_mps_depleted.add(mps.id)
                newly_depleted_mps.append(mps.id)
                # Capture target_loads before disconnect clears them
                if hasattr(mps, 'target_loads') and mps.target_loads:
                    depleted_load_ids.extend(list(mps.target_loads))
                if hasattr(mps, 'disconnect'):
                    mps.disconnect(self.egraph)

        # Initialize tracking list for Grid-restored MPS before update_system_state
        self.egraph._grid_restored_mps = []

        # Update system state after time step to recalculate MPS power allocation
        # This ensures Pout reflects current energy levels and load states
        # During this call, if Grid reconnects to an island, MPS will be auto-disconnected
        self.egraph.update_system_state()

        # Emit mps_depleted event AFTER update_system_state for accurate load reporting
        if newly_depleted_mps:
            # Filter to loads that actually lost power
            actual_lost_load_ids = []
            for load_id in depleted_load_ids:
                load = self.agent_manager.loads.get(load_id)
                if load and load.state == "off":
                    actual_lost_load_ids.append(load_id)
            events.append({
                "type": "mps_depleted",
                "mps_ids": newly_depleted_mps,
                "load_ids": actual_lost_load_ids,
                "time": self.current_time
            })

        if hasattr(self.egraph, "_power_loss_events") and self.egraph._power_loss_events:
            for event in self.egraph._power_loss_events:
                event["time"] = self.current_time
                events.append(event)
            self.egraph._power_loss_events = []

        # Check for MPS disconnected due to Grid restoration
        if hasattr(self.egraph, '_grid_restored_mps') and self.egraph._grid_restored_mps:
            grid_restored_mps = self.egraph._grid_restored_mps
            events.append({
                "type": "mps_grid_restored",
                "mps_ids": grid_restored_mps,
                "message": "Grid reconnected to island, MPS disconnected (task completed)",
                "time": self.current_time
            })
            # Clear the list
            self.egraph._grid_restored_mps = []

        return {"events": events, "time": self.current_time}

    def get_state(self) -> Dict:
        """Get current system state using agent manager"""
        return {
            'time': self.current_time,
            'loads': len(self.agent_manager.loads),
            'mps_units': len(self.agent_manager.mobile_power_sources),
            'repair_crews': len(self.agent_manager.repair_crews),
            'damage_points': len(self.agent_manager.damage_points),
            'switches': len(self.agent_manager.switches)
        }

    def check_power_balance(self) -> Dict:
        """Check MPS-side power balance while excluding Grid-served load."""
        try:
            mps_sources = self.agent_manager.mobile_power_sources
            loads = self.agent_manager.loads

            total_mps_generation = sum(
                float(mps.Pout)
                for mps in mps_sources.values()
                if mps.state == 'connected'
            )

            # Grid supply is exogenous in this simulator, so only compare MPS generation
            # against the portion of served load that is actually being carried by MPS.
            grid_reachable = set()
            for node_id, node in self.egraph.nodes.items():
                if getattr(node, 'type', None) == NodeType.GRID:
                    grid_reachable.update(self.egraph._dfs_connected_component(node_id, set()))

            total_grid_served = 0.0
            total_mps_served = 0.0
            for load in loads.values():
                if load.state != "on":
                    continue

                if load.node_id in grid_reachable:
                    total_grid_served += float(load.P)
                else:
                    total_mps_served += min(
                        float(load.P),
                        max(0.0, float(getattr(load, 'P_retained', 0.0) or 0.0)),
                    )

            balance = total_mps_generation - total_mps_served
            tolerance = max(1e-3, 0.01 * max(total_mps_generation, total_mps_served, 1.0))

            return {
                'total_generation': total_mps_generation,
                'total_demand': total_mps_served,
                'balance': balance,
                'balanced': abs(balance) <= tolerance,
                'tolerance': tolerance,
                'scope': 'mps_only',
                'grid_served_demand': total_grid_served,
                'mps_served_demand': total_mps_served,
            }

        except Exception as e:
            return {
                'error': str(e),
                'balanced': False
            }

    def count_islands(self) -> int:
        """Count electrical islands"""
        if not self.egraph:
            return 0
        try:
            islands = self.egraph.identify_islands()
            return len(islands)
        except Exception as e:
            logging.getLogger(__name__).warning(f"Failed to count islands: {e}")
            return 0

    def export_state(self) -> Dict[str, Any]:
        """Export complete environment state using agent manager"""
        return {
            'time': self.current_time,
            'simulation_state': self.simulation_state,
            'agent_state': self.agent_manager.export_state(),
            'emitted_events': {
                'fault_repaired': list(self._emitted_fault_repaired),
                'mps_depleted': list(self._emitted_mps_depleted)
            }
        }

    def import_state(self, snap: Dict[str, Any]) -> None:
        """Import environment state using agent manager"""
        # Restore time and simulation state
        self.current_time = snap.get('time', 0)
        self.simulation_state = snap.get('simulation_state', 'initialized')

        # Restore agent state through agent manager
        if 'agent_state' in snap:
            self.agent_manager.import_state(snap['agent_state'])

        # Restore event tracking
        events = snap.get('emitted_events', {})
        self._emitted_fault_repaired = set(events.get('fault_repaired', []))
        self._emitted_mps_depleted = set(events.get('mps_depleted', []))

    def advance_time(self):
        """Advance time (alias for step for compatibility)"""
        return self.step()

    def get_system_summary(self) -> Dict[str, Any]:
        """Get system summary using agent manager"""
        return {
            'total_agents': (
                len(self.agent_manager.repair_crews) +
                len(self.agent_manager.mobile_power_sources) +
                len(self.agent_manager.damage_points) +
                len(self.agent_manager.switches) +
                len(self.agent_manager.loads)
            ),
            'agent_breakdown': {
                'repair_crews': len(self.agent_manager.repair_crews),
                'mobile_power_sources': len(self.agent_manager.mobile_power_sources),
                'damage_points': len(self.agent_manager.damage_points),
                'switches': len(self.agent_manager.switches),
                'loads': len(self.agent_manager.loads)
            }
        }

    # ========== Helper Methods ==========

    def _auto_resolve_repair_cycle(self) -> Optional[str]:
        """Auto-resolve a cycle created by fault repair by opening a switch in the cycle.

        Strategy: Find closed switches participating in the cycle, open the one that
        breaks the cycle. This is a system-level auto-resolution — no penalty.

        Returns:
            Switch ID that was opened, or None if resolution failed.
        """
        import logging
        logger = logging.getLogger(__name__)

        if not self.egraph.has_cycle():
            return None

        cycle_details = None
        if hasattr(self.egraph, 'detect_cycle_with_details'):
            try:
                cycle_details = self.egraph.detect_cycle_with_details()
            except Exception:
                pass

        if not cycle_details or not cycle_details.get('switches_in_cycle'):
            candidates = [
                sid for sid, sw in self.agent_manager.switches.items()
                if sw.state == 'close'
            ]
        else:
            candidates = cycle_details['switches_in_cycle']

        for switch_id in candidates:
            switch = self.agent_manager.switches.get(switch_id)
            if not switch or switch.state != 'close':
                continue

            old_state = switch.state
            switch.state = 'open'
            self._apply_switch_state(switch, allow_faulted=False)

            if not self.egraph.has_cycle():
                logger.info(f"Auto-resolved repair-induced cycle by opening switch {switch_id}")
                return switch_id

            switch.state = old_state
            self._apply_switch_state(switch, allow_faulted=False)

        logger.warning("Failed to auto-resolve repair-induced cycle — no single switch break found")
        return None

    def _calculate_weighted_power(self) -> float:
        """Calculate total weighted power of energized loads

        Returns sum of (W * P) for all loads with state='on'
        Note: Does NOT call update_system_state() to avoid side effects.
        The caller (step()) is responsible for updating system state separately.

        Returns:
            Total weighted power (sum of w_i * P_i)
        """
        total_weighted_power = 0.0
        for load_id, load in self.agent_manager.loads.items():
            if load.state == "on":  # Load is energized
                total_weighted_power += load.W * load.P

        return total_weighted_power


    def _apply_switch_state(self, switch, force_state: Optional[str] = None, allow_faulted: bool = False) -> None:
        """Apply switch state to electrical graph edges

        Directly sets edge connectivity without cycle detection.
        Used internally for applying switch configurations.

        Args:
            switch: Switch object to apply
            force_state: If provided, use this state instead of switch.state
            allow_faulted: If True, process faulted edges (for initialization/cycle resolution).
                          If False, skip faulted edges (for runtime LLM operations).

        CRITICAL - Physical Correctness (aligned with MILP Part 4.25):
        - Faulted edges MUST remain disconnected regardless of switch state
        - This matches MILP: b[e,t] <= b_healthy[e,t] (faulted edge -> b_healthy=0 -> b=0)
        - allow_faulted=True means "don't skip faulted edges in the loop",
          but faulted edges are still forced to is_connected=False
        """
        logger = logging.getLogger(__name__)
        state = force_state if force_state else switch.state

        for edge_id in switch.connected_edges:
            if edge_id in self.egraph.edges:
                edge = self.egraph.edges[edge_id]

                # Check if edge is faulted
                is_faulted = hasattr(edge, 'state') and edge.state == 'faulted'

                if is_faulted:
                    if not allow_faulted:
                        # Runtime: Skip faulted edges (LLM cannot operate switches controlling faulted edges)
                        logger.debug(f"Skipping faulted edge {edge_id} in switch {switch.id} operation (edge must be repaired first)")
                        continue
                    else:
                        # Initialization/Cycle Resolution: Faulted edges MUST remain disconnected
                        # This ensures physical correctness: damaged edges cannot conduct electricity
                        # regardless of switch state (matches MILP physical layer constraint)
                        self.egraph.set_edge_connection(edge_id, False)
                        logger.debug(f"Faulted edge {edge_id} forced to disconnected (physical constraint)")
                else:
                    # Healthy edges: Apply switch state normally
                    if state == "open":
                        self.egraph.set_edge_connection(edge_id, False)
                    elif state == "close":
                        self.egraph.set_edge_connection(edge_id, True)
