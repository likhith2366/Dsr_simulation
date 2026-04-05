"""
Dual Graph Model - Traffic Graph (TGraph) & Electrical Graph (EGraph)
======================================================================

The DSR simulator uses a "dual graph model" to separately model traffic routing
and electrical connectivity:

TGraph (Traffic Graph)
-----------------------
- Purpose: RC (Repair Crews) and MPS (Mobile Power Sources) move on this graph
- Structure: Undirected weighted graph, edge weight = distance (km)
- Core algorithm: Dijkstra shortest path
- Special operation: add_dp_to_edge() inserts a fault node on an edge (splits one edge into two for line faults)
- Nodes: TNode (is_fault flag indicates whether it is a fault point)
- Edges: TEdge (from_node, to_node, distance)

EGraph (Electrical Graph)
--------------------------
- Purpose: Determine electrical connectivity, island identification, cycle detection, power balance
- Structure: Undirected graph, edges have connectivity state (is_connected) and fault state (state)
- Node types (NodeType): GRID (grid) / MPS (mobile power source) / LOAD (load) / SWITCH (switch) / BUS (bus)
- Core functions:
  * identify_islands(): DFS to identify all electrical islands (connected components)
  * has_cycle() / detect_cycle_with_details(): DFS cycle detection
  * update_system_state(): Update load power supply state each step (Grid/MPS -> Load)
  * check_island_power_supply(): Verify island power balance

Power supply logic (update_system_state):
  1. Grid island: All loads fully restored (P_retained = P)
  2. MPS island: MPS output allocated proportionally to target_loads' remaining demand
  3. No-source island: All loads shed (switch_off)
  4. MPS depleted: Auto-disconnect, loads shed
"""

from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
import heapq
import math


class TNode:
    """Traffic node"""
    def __init__(self, node_id: str):
        self.id = node_id
        self.is_fault = False  # Reserved for DP use


class TEdge:
    """Traffic edge"""
    def __init__(self, edge_id: str, from_node: str, to_node: str, distance: int):
        """
        Args:
            edge_id: Unique edge identifier
            from_node: Start node ID
            to_node: End node ID
            distance: Distance (km)
        """
        self.id = edge_id
        self.from_node = from_node
        self.to_node = to_node
        self.distance = distance  # Integer km


class TGraph:
    """Traffic graph"""

    def __init__(self):
        self.nodes: Dict[str, TNode] = {}
        self.edges: Dict[str, TEdge] = {}

    def add_node(self, node_id: str) -> None:
        """Add node"""
        if node_id not in self.nodes:
            self.nodes[node_id] = TNode(node_id)

    def add_edge(self, edge_id: str, from_node: str, to_node: str, distance: int) -> None:
        """Add edge

        Args:
            edge_id: Unique edge identifier
            from_node: Start node ID
            to_node: End node ID
            distance: Distance (integer km)
        """
        # Ensure nodes exist
        self.add_node(from_node)
        self.add_node(to_node)

        # Add edge
        self.edges[edge_id] = TEdge(edge_id, from_node, to_node, distance)

    def get_edge(self, from_node: str, to_node: str) -> Optional[TEdge]:
        """Get edge by two nodes (undirected graph)"""
        for edge in self.edges.values():
            if (edge.from_node == from_node and edge.to_node == to_node) or \
               (edge.from_node == to_node and edge.to_node == from_node):
                return edge
        return None

    def get_node_edges(self, node_id: str) -> List[TEdge]:
        """Get all edges connected to a node"""
        edges = []
        for edge in self.edges.values():
            if edge.from_node == node_id or edge.to_node == node_id:
                edges.append(edge)
        return edges

    def find_shortest_path(self, start: str, end: str) -> Tuple[List[str], int]:
        """Find shortest path using Dijkstra's algorithm

        Args:
            start: Start node ID
            end: Target node ID

        Returns:
            (list of path nodes, total distance)
            If unreachable, returns ([], -1)
        """
        if start not in self.nodes or end not in self.nodes:
            return [], -1

        if start == end:
            return [start], 0

        # Initialize distances and predecessor nodes
        distances = {node: float('inf') for node in self.nodes}
        distances[start] = 0
        previous = {}

        # Priority queue: (distance, node)
        pq = [(0, start)]
        visited = set()

        while pq:
            current_dist, current = heapq.heappop(pq)

            if current in visited:
                continue

            visited.add(current)

            if current == end:
                # Reconstruct path
                path = []
                while current in previous:
                    path.append(current)
                    current = previous[current]
                path.append(start)
                path.reverse()
                return path, distances[end]

            # Check all neighbors
            for edge in self.get_node_edges(current):
                if edge.from_node == current:
                    neighbor = edge.to_node
                else:
                    neighbor = edge.from_node

                if neighbor in visited:
                    continue

                new_dist = distances[current] + edge.distance

                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current
                    heapq.heappush(pq, (new_dist, neighbor))

        # Unreachable
        return [], -1

    def get_path_distance(self, path: List[str]) -> int:
        """Calculate total distance of a path

        Args:
            path: List of node IDs

        Returns:
            Total distance, or -1 if path is invalid
        """
        if len(path) < 2:
            return 0

        total_distance = 0
        for i in range(len(path) - 1):
            edge = self.get_edge(path[i], path[i+1])
            if edge is None:
                return -1
            total_distance += edge.distance

        return total_distance

    # Legacy compatibility
    def find_path(self, start: str, end: str) -> Optional[List[str]]:
        """Find shortest path between nodes using Dijkstra's algorithm"""
        path, _ = self.find_shortest_path(start, end)
        return path if path else None

    def get_neighbors(self, node_id: str) -> List[str]:
        """Get neighboring nodes"""
        neighbors = []
        for edge in self.get_node_edges(node_id):
            if edge.from_node == node_id:
                neighbors.append(edge.to_node)
            else:
                neighbors.append(edge.from_node)
        return neighbors

    def get_shortest_path(self, start: str, end: str) -> Tuple[List[str], int]:
        """Compatibility method: get shortest path (alias)"""
        return self.find_shortest_path(start, end)

    def add_dp_to_edge(self, edge_id: str, dp_id: str, distance_from_start: int) -> Tuple[str, str]:
        """Add DP (damage point) on an edge

        Args:
            edge_id: Edge ID to add DP on
            dp_id: Unique DP identifier
            distance_from_start: Distance from the start node to DP (km)

        Returns:
            IDs of the two new edges after splitting
        """
        if edge_id not in self.edges:
            raise ValueError(f"Edge {edge_id} not found")

        edge = self.edges[edge_id]

        # 1. Create DP node
        self.add_node(dp_id)
        self.nodes[dp_id].is_fault = True

        # 2. Create two new edges
        edge1_id = f"{edge_id}_1_{dp_id}"
        edge2_id = f"{edge_id}_2_{dp_id}"

        # First edge: from original start to DP
        self.add_edge(edge1_id, edge.from_node, dp_id, distance_from_start)

        # Second edge: from DP to original end
        remaining_distance = edge.distance - distance_from_start
        self.add_edge(edge2_id, dp_id, edge.to_node, remaining_distance)

        # 3. Delete original edge
        del self.edges[edge_id]

        return edge1_id, edge2_id

    def add_dp_to_node(self, node_id: str, dp_id: str) -> None:
        """Add DP (damage point) on a node

        Args:
            node_id: Node ID to add DP on
            dp_id: Unique DP identifier (mainly used for recording)
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")

        # Mark node as fault node
        self.nodes[node_id].is_fault = True

    def __str__(self) -> str:
        """String representation"""
        return f"TGraph: {len(self.nodes)} nodes, {len(self.edges)} edges"


class NodeType(Enum):
    """Electrical node type"""
    GRID = "grid"      # Grid supply node
    MPS = "mps"        # Mobile power source
    LOAD = "load"      # Load node
    SWITCH = "switch"  # Switch node
    BUS = "bus"        # No-load node (pure connection point)

    # Legacy name compatibility
    SUBSTATION = "grid"
    JUNCTION = "bus"
    GENERATION = "mps"


class ENode:
    """Electrical node"""
    def __init__(self, node_id: str, node_type: NodeType):
        self.id = node_id
        self.type = node_type


class EEdge:
    """Electrical edge"""
    def __init__(self, edge_id: str, from_node: str, to_node: str, is_connected: bool = True):
        """
        Args:
            edge_id: Unique edge identifier
            from_node: Start node ID
            to_node: End node ID
            is_connected: Whether connected (True=connected, False=disconnected)
        """
        self.id = edge_id
        self.from_node = from_node
        self.to_node = to_node
        self.is_connected = is_connected
        self.state = 'operational'  # Edge state: 'operational' or 'faulted'


class EGraph:
    """Electrical graph"""

    def __init__(self):
        self.nodes: Dict[str, ENode] = {}
        self.edges: Dict[str, EEdge] = {}
        self.dp_system = None  # DP system reference, injected during initialization
        self.agent_manager = None  # AgentManager reference, injected during initialization (new version)

    def add_node(self, node_id: str, node_type: NodeType) -> None:
        """Add electrical node

        Args:
            node_id: Unique node identifier
            node_type: Node type
        """
        if node_id not in self.nodes:
            self.nodes[node_id] = ENode(node_id, node_type)

    def add_edge(self, edge_id: str, from_node: str, to_node: str, is_connected: bool = True) -> None:
        """Add electrical edge

        Args:
            edge_id: Unique edge identifier
            from_node: Start node ID
            to_node: End node ID
            is_connected: Initial connectivity state
        """
        if from_node not in self.nodes:
            raise ValueError(f"Node {from_node} does not exist")
        if to_node not in self.nodes:
            raise ValueError(f"Node {to_node} does not exist")

        self.edges[edge_id] = EEdge(edge_id, from_node, to_node, is_connected)

    def remove_edge(self, edge_id: str) -> bool:
        """Remove edge from electrical graph"""
        if edge_id not in self.edges:
            return False
        del self.edges[edge_id]
        return True

    def set_edge_connection(self, edge_id: str, is_connected: bool) -> None:
        """Set edge connectivity state

        Args:
            edge_id: Unique edge identifier
            is_connected: Connectivity state (True=connected, False=disconnected)
        """
        if edge_id in self.edges:
            self.edges[edge_id].is_connected = is_connected

    def is_edge_connected(self, edge_id: str) -> bool:
        """Check if edge is connected (considering faults and switches)

        Args:
            edge_id: Edge ID

        Returns:
            True if edge is connected
        """
        edge = self.edges.get(edge_id)
        if not edge:
            return False

        # First check the edge's own connectivity state (switch effect)
        if not edge.is_connected:
            return False

        # ⭐ CRITICAL FIX: Check edge.state directly instead of DP.check_edge_affected()
        # Reason: DP.check_edge_affected() relies on class variable cls.faults which is
        # empty in parallel training (class variables removed for multi-worker support)
        if hasattr(edge, 'state') and edge.state == 'faulted':
            return False

        return True

    def get_connected_neighbors(self, node_id: str) -> List[str]:
        """Get all connected neighbors of a node (considering faults)

        Args:
            node_id: Node ID

        Returns:
            List of connected neighbor node IDs
        """
        neighbors = []
        for edge_id, edge in self.edges.items():
            # Use the new connectivity check
            if not self.is_edge_connected(edge_id):
                continue

            if edge.from_node == node_id:
                neighbors.append(edge.to_node)
            elif edge.to_node == node_id:
                neighbors.append(edge.from_node)

        return neighbors

    def identify_islands(self) -> List[Set[str]]:
        """Identify all electrical islands (connected components)

        Returns:
            List of islands, each island is a set of node IDs
        """
        visited = set()
        islands = []

        for node_id in self.nodes:
            if node_id not in visited:
                # DFS to find a connected component
                island = self._dfs_connected_component(node_id, visited)
                islands.append(island)

        return islands

    def _dfs_connected_component(self, start_node: str, visited: Set[str]) -> Set[str]:
        """Find the connected component containing start_node using DFS

        Args:
            start_node: Start node
            visited: Set of visited nodes (will be updated)

        Returns:
            All node IDs in the connected component
        """
        stack = [start_node]
        component = set()

        while stack:
            node = stack.pop()
            if node in visited:
                continue

            visited.add(node)
            component.add(node)

            # Only expand through connected edges
            neighbors = self.get_connected_neighbors(node)
            for neighbor in neighbors:
                if neighbor not in visited:
                    stack.append(neighbor)

        return component

    def has_cycle(self) -> bool:
        """Detect whether the graph contains a cycle

        Returns:
            True if a cycle exists, False otherwise
        """
        visited = set()

        for node_id in self.nodes:
            if node_id not in visited:
                # Check each connected component for cycles
                if self._has_cycle_dfs(node_id, None, visited, set()):
                    return True

        return False

    def detect_cycle_with_details(self) -> Optional[Dict[str, any]]:
        """Detect cycle and return detailed information (for LLM learning)

        Returns:
            If cycle exists, returns dict containing:
                - cycle_path: List[str] cycle node sequence
                - switches_in_cycle: List[str] switch IDs participating in the cycle
            If no cycle, returns None
        """
        visited = set()
        parent_map = {}

        for node_id in self.nodes:
            if node_id not in visited:
                # Try to find a cycle in this connected component
                cycle_info = self._detect_cycle_dfs_with_path(
                    node_id, None, visited, set(), parent_map
                )
                if cycle_info:
                    # Found cycle, extract detailed information
                    cycle_path = cycle_info['path']

                    # Find switches participating in the cycle
                    switches_in_cycle = []
                    if self.agent_manager:
                        for switch_id, switch in self.agent_manager.switches.items():
                            # Check if edges controlled by switch are in the cycle
                            if switch.state == 'close':
                                for edge_id in switch.connected_edges:
                                    if edge_id in self.edges:
                                        edge = self.edges[edge_id]
                                        # Check if both endpoints of the edge are in the cycle
                                        if edge.from_node in cycle_path and edge.to_node in cycle_path:
                                            # Check if connected (participating in cycle)
                                            if edge.is_connected:
                                                switches_in_cycle.append(switch_id)
                                                break

                    return {
                        'cycle_path': cycle_path,
                        'switches_in_cycle': switches_in_cycle
                    }

        return None

    def _detect_cycle_dfs_with_path(self, node: str, parent: Optional[str],
                                   visited: Set[str], rec_stack: Set[str],
                                   parent_map: Dict[str, str]) -> Optional[Dict[str, any]]:
        """Detect cycle using DFS and return path

        Args:
            node: Current node
            parent: Parent node
            visited: Global visited flag
            rec_stack: Current DFS path
            parent_map: Parent node mapping (for backtracking path)

        Returns:
            If cycle found, returns {'path': [node list]}, otherwise returns None
        """
        visited.add(node)
        rec_stack.add(node)

        neighbors = self.get_connected_neighbors(node)
        for neighbor in neighbors:
            if neighbor not in visited:
                parent_map[neighbor] = node
                result = self._detect_cycle_dfs_with_path(neighbor, node, visited, rec_stack, parent_map)
                if result:
                    return result
            elif neighbor != parent and neighbor in rec_stack:
                # Found cycle! Backtrack path
                cycle_path = [neighbor]
                current = node
                while current != neighbor:
                    cycle_path.append(current)
                    current = parent_map.get(current)
                    if current is None:
                        break
                cycle_path.append(neighbor)  # Close the cycle
                return {'path': cycle_path}

        rec_stack.remove(node)
        return None

    def _has_cycle_dfs(self, node: str, parent: Optional[str], visited: Set[str], rec_stack: Set[str]) -> bool:
        """Detect cycle using DFS

        Args:
            node: Current node
            parent: Parent node (for undirected graph)
            visited: Global visited flag
            rec_stack: Current DFS path

        Returns:
            Whether a cycle was detected
        """
        visited.add(node)
        rec_stack.add(node)

        # Check all connected neighbors
        neighbors = self.get_connected_neighbors(node)
        for neighbor in neighbors:
            if neighbor not in visited:
                if self._has_cycle_dfs(neighbor, node, visited, rec_stack):
                    return True
            elif neighbor != parent and neighbor in rec_stack:
                # Found cycle (not the case of returning to parent node)
                return True

        rec_stack.remove(node)
        return False


    def check_island_power_supply(self, island: Set[str]) -> bool:
        """Check if island can successfully supply power (verify power balance)

        Calculates total demand of all loads in the island (potential demand),
        verifies whether MPS output meets the demand.
        If power balanced (sum_P_mps ~ sum_P_load, sum_Q_mps ~ sum_Q_load), loads can be turned on/kept on.
        If power imbalanced, loads will be turned off (load shedding).

        Args:
            island: Set of island node IDs

        Returns:
            True if island can successfully supply power (power balanced), False if insufficient or imbalanced
        """
        # 1. Check power sources in the island
        has_grid = False
        mps_nodes = []

        for node_id in island:
            node = self.nodes[node_id]
            if node.type == NodeType.GRID:
                has_grid = True
                break  # Grid has unlimited capacity, return True directly
            elif node.type == NodeType.MPS:
                mps_nodes.append(node_id)

        # If Grid present, return True directly (unlimited capacity)
        if has_grid:
            return True

        # If no power source, return False
        if not mps_nodes:
            return False

        if not self.agent_manager:
            raise RuntimeError("EGraph.agent_manager not set. Use IndependentDSREnvironment instead of DSREnvironment.")

        # 2. Calculate total load demand (based on MPS target_loads)
        total_p_load = 0
        total_q_load = 0

        # Collect all MPS target loads
        all_target_loads = set()
        has_mps_with_targets = False

        for mps_id in mps_nodes:
            mps = self.agent_manager.get_mobile_power_source(mps_id)
            if mps and mps.state == "connected":
                if mps.target_loads:
                    # MPS has specified target_loads
                    all_target_loads.update(mps.target_loads)
                    has_mps_with_targets = True

        # Calculate total demand of target loads
        if has_mps_with_targets and all_target_loads:
            # Only calculate MPS-specified target_loads (must be in current island)
            for load_id in all_target_loads:
                load = self.agent_manager.get_load(load_id)
                if load and load.node_id in island:
                    # Only calculate target_loads in current island
                    total_p_load += load.P
                    total_q_load += load.Q
        else:
            # No MPS has specified target_loads -> return False (no power supply)
            return False

        # 3. Calculate total output of all MPS
        total_p_mps = 0
        total_q_mps = 0
        has_connected_mps = False

        for mps_id in mps_nodes:
            mps = self.agent_manager.get_mobile_power_source(mps_id)
            if mps and mps.state == "connected" and mps.energy > 0:
                has_connected_mps = True
                total_p_mps += mps.Pout
                total_q_mps += mps.Qout

        # If no connected MPS, return False
        if not has_connected_mps:
            return False

        # 4. Verify power balance: sum_P_mps = sum_P_load, sum_Q_mps = sum_Q_load
        # Use 5% relative tolerance to avoid numerical precision issues
        tolerance = 0.05  # 5% tolerance

        # Calculate relative error for P and Q
        if total_p_load > 0:
            p_error = abs(total_p_mps - total_p_load) / total_p_load
        else:
            # Both P values near zero → balanced; otherwise check absolute difference
            p_error = 0.0 if abs(total_p_mps) < 1.0 else 1.0

        if total_q_load > 0:
            q_error = abs(total_q_mps - total_q_load) / total_q_load
        else:
            # Both Q values near zero → balanced; otherwise check absolute difference
            q_error = 0.0 if abs(total_q_mps) < 1.0 else 1.0

        # Power balance check
        power_balanced = (p_error <= tolerance) and (q_error <= tolerance)

        # DEBUG info (optional)
        # if not power_balanced:
        #     print(f"[POWER BALANCE] Island power imbalance detected:")
        #     print(f"  P: MPS={total_p_mps:.1f}kW, Load={total_p_load:.1f}kW, Error={p_error*100:.1f}%")
        #     print(f"  Q: MPS={total_q_mps:.1f}kVar, Load={total_q_load:.1f}kVar, Error={q_error*100:.1f}%")

        return power_balanced

    def update_system_state(self) -> None:
        """Update system state - called once per time step

        Power supply model:
        - Each load has P_retained (current power supply received)
        - Grid supply: load directly gets full P_retained = P
        - MPS supply: MPS output allocated proportionally to target_loads' remaining demand (P - P_retained)
        - No source (MPS depleted/disconnected/fault isolated): load loses power, P_retained = 0, state = "off"
        - Multiple MPS can stack supply, only need to cover the deficit
        """
        if not self.agent_manager:
            raise RuntimeError("EGraph.agent_manager not set. Use IndependentDSREnvironment instead of DSREnvironment.")

        # Reset all load power retention before recalculating from scratch
        for load in self.agent_manager.loads.values():
            load.P_retained = 0.0
            load.Q_retained = 0.0

        islands = self.identify_islands()
        self._power_loss_events = []

        for island in islands:
            # Check if island has any loads
            has_load = False
            for node_id in island:
                loads = self.agent_manager.get_loads_at_node(node_id)
                if loads:
                    has_load = True
                    break
            if not has_load:
                continue

            # Allocate power source output
            self._allocate_power_supply_with_manager(island)

            # Check power source types in the island
            has_grid = False
            mps_in_island = []
            mps_nodes_in_island = []
            for node_id in island:
                node = self.nodes.get(node_id)
                if node and node.type == NodeType.GRID:
                    has_grid = True
                elif node and node.type == NodeType.MPS:
                    mps_nodes_in_island.append(node_id)
                    mps = self.agent_manager.get_mobile_power_source(node_id)
                    if mps and mps.state == "connected" and mps.energy > 0:
                        mps_in_island.append(mps)

            if has_grid:
                # Grid supply -> all loads fully restored
                for node_id in island:
                    loads = self.agent_manager.get_loads_at_node(node_id)
                    for load in loads:
                        load.P_retained = float(load.P)
                        load.Q_retained = float(load.Q)
                        if load.state == "off":
                            load.switch_on()

            elif mps_in_island:
                # MPS supply -> allocate MPS output to target_loads' remaining demand
                # Does not rely on can_supply gating, allocate whatever is available

                # 1) Collect total output and target_loads from all MPS
                total_mps_P = 0.0
                target_loads_set = set()
                for mps in mps_in_island:
                    total_mps_P += mps.Pout
                    if mps.target_loads:
                        target_loads_set.update(mps.target_loads)

                loads_in_island = []
                for node_id in island:
                    loads = self.agent_manager.get_loads_at_node(node_id)
                    if loads:
                        loads_in_island.extend(loads)

                if not target_loads_set or total_mps_P <= 0:
                    loads_to_shed = []
                    if target_loads_set:
                        for load_id in target_loads_set:
                            load = self.agent_manager.get_load(load_id)
                            if load and load.node_id in island:
                                loads_to_shed.append(load)
                    else:
                        loads_to_shed = loads_in_island

                    if loads_to_shed:
                        shed_ids = []
                        for load in loads_to_shed:
                            load.P_retained = 0.0
                            load.Q_retained = 0.0
                            load.switch_off(force_system=True)
                            shed_ids.append(load.id)
                        self._power_loss_events.append({
                            "type": "mps_power_insufficient",
                            "mps_ids": [mps.id for mps in mps_in_island],
                            "load_ids": shed_ids,
                            "reason": "no_output"
                        })
                    continue

                # 2) Calculate remaining demand of target_loads (P - P_retained)
                if target_loads_set and total_mps_P > 0:
                    total_remaining_demand = 0.0
                    loads_with_deficit = []
                    for load_id in target_loads_set:
                        load = self.agent_manager.get_load(load_id)
                        if load and load.node_id in island:
                            deficit = max(0.0, float(load.P) - load.P_retained)
                            if deficit > 0:
                                loads_with_deficit.append((load, deficit))
                                total_remaining_demand += deficit
                            # Fully supplied loads also need to be switched on
                            if load.P_retained > 0 and load.state == "off":
                                load.switch_on()

                    if total_remaining_demand > 0 and total_mps_P < total_remaining_demand:
                        # Partial supply: generate informational event (not harsh penalty)
                        self._power_loss_events.append({
                            "type": "mps_partial_supply",
                            "mps_ids": [mps.id for mps in mps_in_island],
                            "available_kw": total_mps_P,
                            "demand_kw": total_remaining_demand,
                            "reason": "partial_power"
                        })

                    # 3) Allocate MPS output proportionally to remaining demand (handles both sufficient and insufficient cases)
                    for load, deficit in loads_with_deficit:
                        if total_remaining_demand > 0:
                            share = deficit / total_remaining_demand
                            allocated = min(deficit, share * total_mps_P)
                        else:
                            allocated = 0.0
                        load.P_retained = min(float(load.P), load.P_retained + allocated)
                        if load.P > 0:
                            load.Q_retained = load.P_retained / float(load.P) * float(load.Q)
                        if load.state == "off":
                            load.switch_on()

                    # Clean up orphaned loads: loads in this island not targeted by any MPS
                    # These loads have no power source and should be turned off
                    for node_id in island:
                        loads_at_node = self.agent_manager.get_loads_at_node(node_id)
                        for load in loads_at_node:
                            if load.id not in target_loads_set and load.state == "on":
                                load.P_retained = 0.0
                                load.Q_retained = 0.0
                                load.switch_off(force_system=True)

            else:
                # No Grid, no connected MPS — shed all powered loads in this island
                loads_to_shed = []
                for node_id in island:
                    loads = self.agent_manager.get_loads_at_node(node_id)
                    for load in loads:
                        if load.state == "on":
                            loads_to_shed.append(load)
                if loads_to_shed:
                    shed_ids = []
                    for load in loads_to_shed:
                        load.P_retained = 0.0
                        load.Q_retained = 0.0
                        load.switch_off(force_system=True)
                        shed_ids.append(load.id)
                    reason = "mps_depleted" if mps_nodes_in_island else "no_power_source"
                    self._power_loss_events.append({
                        "type": "mps_power_insufficient",
                        "mps_ids": mps_nodes_in_island,
                        "load_ids": shed_ids,
                        "reason": reason
                    })

    def _allocate_power_supply_with_manager(self, island: Set[str]) -> None:
        """Handle island power source state (using agent_manager)

        Note: This method no longer auto-allocates power. MPS output power is explicitly
        controlled by LLM through set_output().
        This method only resets MPS output to 0 when the island contains Grid.

        Args:
            island: Set of island node IDs
        """
        if not self.agent_manager:
            return

        # Check if Grid is present
        has_grid = any(self.nodes[n].type == NodeType.GRID for n in island if n in self.nodes)

        # If Grid is present, set all MPS output to 0 and disconnect (Grid provides unlimited capacity)
        if has_grid:
            disconnected_mps = []
            for node_id in island:
                if node_id in self.nodes and self.nodes[node_id].type == NodeType.MPS:
                    mps = self.agent_manager.get_mobile_power_source(node_id)
                    if mps and mps.state == "connected":
                        # Grid has taken over island, MPS task completed, auto-disconnect
                        mps.disconnect(self)
                        disconnected_mps.append(mps.id)

            # Return list of disconnected MPS (for event notification)
            if disconnected_mps and hasattr(self, '_grid_restored_mps'):
                self._grid_restored_mps.extend(disconnected_mps)
            return

        # If no Grid, MPS output remains unchanged (controlled by LLM through set_output())
        # No longer auto-allocates power

    # Compatibility method
    def _recompute_power(self) -> None:
        """Compatibility method: recalculate power balance"""
        self.update_system_state()

    def __str__(self) -> str:
        """String representation"""
        return f"EGraph: {len(self.nodes)} nodes, {len(self.edges)} edges"


# Utility functions
def create_ieee13_topology() -> Tuple[TGraph, EGraph]:
    """Create IEEE 13-node test topology"""
    tgraph = TGraph()
    egraph = EGraph()

    # Define nodes
    nodes = ['N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9', 'N10', 'N11', 'N12', 'N13']

    # Add nodes to both graphs
    for node_id in nodes:
        tgraph.add_node(node_id)
        if node_id == 'N1':
            egraph.add_node(node_id, NodeType.GRID)
        else:
            egraph.add_node(node_id, NodeType.LOAD)

    # Define edges (simplified IEEE 13-node)
    edges = [
        ('E1', 'N1', 'N2', 1),
        ('E2', 'N2', 'N3', 1),
        ('E3', 'N2', 'N4', 1),
        ('E4', 'N4', 'N5', 1),
        ('E5', 'N4', 'N6', 1),
        ('E6', 'N6', 'N7', 1),
        ('E7', 'N6', 'N8', 1),
        ('E8', 'N8', 'N9', 1),
        ('E9', 'N8', 'N10', 1),
        ('E10', 'N10', 'N11', 1),
        ('E11', 'N10', 'N12', 1),
        ('E12', 'N12', 'N13', 1)
    ]

    # Add edges to both graphs
    for edge_id, from_node, to_node, distance in edges:
        tgraph.add_edge(edge_id, from_node, to_node, distance)
        egraph.add_edge(edge_id, from_node, to_node, is_connected=True)

    return tgraph, egraph
