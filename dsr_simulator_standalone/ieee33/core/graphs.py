"""
Graph modules: Traffic Graph (TGraph) and Electrical Graph (EGraph)
For basic topology modeling in DSR simulation environment - Updated to match DSRSimulator.ipynb
"""

from typing import Dict, List, Tuple, Optional, Set, Any
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
        """Get edge by two node endpoints (undirected graph)"""
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
            distance_from_start: Distance from the start node to the DP (km)

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
    GRID = "grid"      # Grid power supply node
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
        self.dp_system = None  # DP system reference, injected at initialization
        self.agent_manager = None  # AgentManager reference, injected at initialization (new version)
        # Record under-supply/collapse info for each update_system_state call (does not change monotonic load restoration semantics)
        self.last_supply_failures: List[Dict[str, Any]] = []
        # Record instantaneous supply snapshot for each load (used uniformly by observation/reward)
        self.last_supply_snapshot: Dict[str, Dict[str, Any]] = {}

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
            is_connected: Initial connection state
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
        """Set edge connection state

        Args:
            edge_id: Unique edge identifier
            is_connected: Connection state (True=connected, False=disconnected)
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

        # First check edge's own connection state (affected by switches)
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
            # Use new connectivity check
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
        """Find connected component containing start_node using DFS

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
        """Detect whether a cycle exists in the graph

        Returns:
            True if a cycle exists, False otherwise
        """
        visited = set()

        for node_id in self.nodes:
            if node_id not in visited:
                # Check for cycles in each connected component
                if self._has_cycle_dfs(node_id, None, visited, set()):
                    return True

        return False

    def detect_cycle_with_details(self) -> Optional[Dict[str, any]]:
        """Detect cycle and return detailed information (for LLM learning)

        Returns:
            If cycle exists, returns dict containing:
                - cycle_path: List[str] cycle node sequence
                - switches_in_cycle: List[str] list of switch IDs participating in the cycle
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
                            # Check if switch-controlled edges are on the cycle
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
            visited: Global visited marker
            rec_stack: Current DFS path
            parent_map: Parent node mapping (for path backtracking)

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
            visited: Global visited marker
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
                # Found cycle (not the case of going back to parent)
                return True

        rec_stack.remove(node)
        return False


    def _evaluate_island_power_supply(self, island: Set[str]) -> Dict[str, Any]:
        """Evaluate island power feasibility and return diagnostics.

        Returns:
            Dict with fields:
            - can_supply: bool
            - reason: str
            - total_p_load/total_q_load: target load demand
            - total_p_mps/total_q_mps: available connected MPS output
            - p_error/q_error: relative undersupply (backward-compatible field names)
            - p_surplus/q_surplus: relative oversupply diagnostics
            - tolerance: allowed relative undersupply threshold
            - target_load_ids: effective loads considered in this island
        """
        diagnostics: Dict[str, Any] = {
            'can_supply': False,
            'reason': 'unknown',
            'has_grid': False,
            'mps_nodes': [],
            'target_load_ids': [],
            'total_p_load': 0.0,
            'total_q_load': 0.0,
            'total_p_mps': 0.0,
            'total_q_mps': 0.0,
            'p_error': 1.0,
            'q_error': 1.0,
            'p_surplus': 0.0,
            'q_surplus': 0.0,
            'tolerance': 0.05,
        }

        # 1. Check power source existence
        has_grid = False
        mps_nodes: List[str] = []

        for node_id in island:
            node = self.nodes[node_id]
            if node.type == NodeType.GRID:
                has_grid = True
                break
            if node.type == NodeType.MPS:
                mps_nodes.append(node_id)

        diagnostics['has_grid'] = has_grid
        diagnostics['mps_nodes'] = sorted(mps_nodes)

        # Grid has infinite capacity in this abstraction
        if has_grid:
            diagnostics.update({
                'can_supply': True,
                'reason': 'has_grid',
                'p_error': 0.0,
                'q_error': 0.0,
            })
            return diagnostics

        if not mps_nodes:
            diagnostics['reason'] = 'no_source'
            return diagnostics

        if not self.agent_manager:
            raise RuntimeError('EGraph.agent_manager not set. Use IndependentDSREnvironment instead of DSREnvironment.')

        # 2. Aggregate target-load demand in this island
        total_p_load = 0.0
        total_q_load = 0.0
        all_target_loads = set()
        has_mps_with_targets = False

        for mps_id in mps_nodes:
            mps = self.agent_manager.get_mobile_power_source(mps_id)
            if mps and mps.state == 'connected' and mps.target_loads:
                all_target_loads.update(mps.target_loads)
                has_mps_with_targets = True

        valid_target_load_ids: List[str] = []
        if has_mps_with_targets and all_target_loads:
            for load_id in all_target_loads:
                load = self.agent_manager.get_load(load_id)
                if load and load.node_id in island:
                    total_p_load += float(load.P)
                    total_q_load += float(load.Q)
                    valid_target_load_ids.append(load_id)

        diagnostics['target_load_ids'] = sorted(valid_target_load_ids)
        diagnostics['total_p_load'] = total_p_load
        diagnostics['total_q_load'] = total_q_load

        if not valid_target_load_ids:
            diagnostics['reason'] = 'no_target_loads'
            return diagnostics

        # 3. Aggregate available connected MPS output
        total_p_mps = 0.0
        total_q_mps = 0.0
        has_connected_mps = False

        for mps_id in mps_nodes:
            mps = self.agent_manager.get_mobile_power_source(mps_id)
            if mps and mps.state == 'connected' and mps.energy > 0:
                has_connected_mps = True
                total_p_mps += float(mps.Pout)
                total_q_mps += float(mps.Qout)

        diagnostics['total_p_mps'] = total_p_mps
        diagnostics['total_q_mps'] = total_q_mps

        if not has_connected_mps:
            diagnostics['reason'] = 'no_connected_mps'
            return diagnostics

        # 4. Supply adequacy check (undersupply must be within tolerance)
        # IMPORTANT:
        # - Oversupply is physically curtail-able in this abstraction and should not
        #   mark the island as unsupplied.
        # - Undersupply indicates unmet demand and should fail supply.
        tolerance = float(diagnostics['tolerance'])

        if total_p_load > 1e-6:
            p_undersupply = max(0.0, total_p_load - total_p_mps) / total_p_load
            p_surplus = max(0.0, total_p_mps - total_p_load) / total_p_load
        else:
            p_undersupply = 0.0
            p_surplus = abs(total_p_mps) / max(1.0, abs(total_p_mps))

        if total_q_load > 1e-6:
            q_undersupply = max(0.0, total_q_load - total_q_mps) / total_q_load
            q_surplus = max(0.0, total_q_mps - total_q_load) / total_q_load
        else:
            q_undersupply = 0.0
            q_surplus = abs(total_q_mps) / max(1.0, abs(total_q_mps))

        supply_adequate = (p_undersupply <= tolerance) and (q_undersupply <= tolerance)

        diagnostics.update({
            'can_supply': bool(supply_adequate),
            'reason': 'balanced' if supply_adequate else 'island_power_not_balanced',
            # Keep legacy names p_error/q_error for backward compatibility.
            'p_error': float(p_undersupply),
            'q_error': float(q_undersupply),
            'p_surplus': float(p_surplus),
            'q_surplus': float(q_surplus),
        })

        return diagnostics

    def _calculate_island_mps_served_kw(self, island: Set[str], target_load_ids: Optional[Set[str]] = None) -> Dict[str, float]:
        """Estimate per-load MPS served kW inside one island.

        The sharing rule mirrors projection/renegotiation:
        - Split each load by requested-power ratio among MPS that target it.
        - Enforce each MPS Pout limit by scaling its tentative allocations.
        """
        if not self.agent_manager:
            return {}

        connected_mps_info: Dict[str, Dict[str, Any]] = {}
        mps_serving_by_load: Dict[str, List[str]] = {}
        target_filter = set(target_load_ids) if target_load_ids is not None else None

        for node_id in island:
            node = self.nodes.get(node_id)
            if not node or node.type != NodeType.MPS:
                continue

            mps = self.agent_manager.get_mobile_power_source(node_id)
            if not mps or mps.state != 'connected' or mps.energy <= 0:
                continue

            raw_target_loads = list(getattr(mps, 'target_loads', []) or [])
            if not raw_target_loads:
                continue

            filtered_target_loads: List[str] = []
            for load_id in raw_target_loads:
                if target_filter is not None and load_id not in target_filter:
                    continue
                load = self.agent_manager.get_load(load_id)
                if load and load.node_id in island:
                    filtered_target_loads.append(load_id)

            if not filtered_target_loads:
                continue

            p_req = float(getattr(mps, 'P_requested', mps.Pout) or 0.0)
            q_req = float(getattr(mps, 'Q_requested', mps.Qout) or 0.0)
            connected_mps_info[mps.id] = {
                'target_loads': set(filtered_target_loads),
                'p_req': max(0.0, p_req),
                'q_req': max(0.0, q_req),
                'p_avail': max(0.0, float(mps.Pout or 0.0)),
                'q_avail': max(0.0, float(mps.Qout or 0.0)),
            }

            for load_id in filtered_target_loads:
                mps_serving_by_load.setdefault(load_id, []).append(mps.id)

        # Step 1: Tentative per-load shares by requested ratio
        tentative_mps_share: Dict[str, Dict[str, Dict[str, float]]] = {}
        for load_id, serving_mps_ids in mps_serving_by_load.items():
            load = self.agent_manager.get_load(load_id)
            if not load:
                continue

            total_p_req = sum(connected_mps_info[mid]['p_req'] for mid in serving_mps_ids)
            total_q_req = sum(connected_mps_info[mid]['q_req'] for mid in serving_mps_ids)
            num_serving = max(len(serving_mps_ids), 1)

            for mid in serving_mps_ids:
                if total_p_req > 1e-6:
                    p_ratio = connected_mps_info[mid]['p_req'] / total_p_req
                else:
                    p_ratio = 1.0 / num_serving

                if total_q_req > 1e-6:
                    q_ratio = connected_mps_info[mid]['q_req'] / total_q_req
                else:
                    q_ratio = 1.0 / num_serving

                tentative_mps_share.setdefault(mid, {})[load_id] = {
                    'p': float(load.P) * p_ratio,
                    'q': float(load.Q) * q_ratio,
                }

        # Step 2: Enforce each MPS output limit
        mps_scale: Dict[str, float] = {}
        for mid, mps_data in connected_mps_info.items():
            p_demand = sum(v['p'] for v in tentative_mps_share.get(mid, {}).values())
            if p_demand > 1e-6:
                mps_scale[mid] = min(1.0, mps_data['p_avail'] / p_demand)
            else:
                mps_scale[mid] = 1.0

        # Step 3: Aggregate to load-level served_mps_kw
        served_mps_kw_by_load: Dict[str, float] = {}
        for load_id, serving_mps_ids in mps_serving_by_load.items():
            served_kw = 0.0
            for mid in serving_mps_ids:
                per_load = tentative_mps_share.get(mid, {}).get(load_id)
                if not per_load:
                    continue
                served_kw += per_load['p'] * mps_scale.get(mid, 1.0)
            served_mps_kw_by_load[load_id] = max(0.0, float(served_kw))

        return served_mps_kw_by_load

    def build_supply_snapshot(self) -> Dict[str, Dict[str, Any]]:
        """Build instantaneous per-load supply snapshot from current topology + source outputs."""
        if not self.agent_manager:
            return {}

        snapshot: Dict[str, Dict[str, Any]] = {
            load_id: {
                'served_grid_kw': 0.0,
                'served_mps_kw': 0.0,
                'currently_served': False,
                'reason': 'unknown',
            }
            for load_id in self.agent_manager.loads.keys()
        }

        islands = self.identify_islands()
        for island in islands:
            island_loads = []
            for node_id in island:
                island_loads.extend(self.agent_manager.get_loads_at_node(node_id))

            if not island_loads:
                continue

            power_evaluation = self._evaluate_island_power_supply(island)
            can_supply = bool(power_evaluation.get('can_supply', False))
            has_grid = bool(power_evaluation.get('has_grid', False))
            reason = str(power_evaluation.get('reason', 'unknown'))

            if has_grid:
                for load in island_loads:
                    snapshot[load.id] = {
                        'served_grid_kw': float(load.P),
                        'served_mps_kw': 0.0,
                        'currently_served': True,
                        'reason': 'has_grid',
                    }
                continue

            if not can_supply:
                for load in island_loads:
                    snapshot[load.id]['reason'] = reason
                continue

            target_load_ids = set(power_evaluation.get('target_load_ids', []) or [])
            served_mps_kw_by_load = self._calculate_island_mps_served_kw(island, target_load_ids=target_load_ids)

            for load in island_loads:
                served_mps_kw = 0.0
                if load.id in target_load_ids:
                    served_mps_kw = min(float(load.P), float(served_mps_kw_by_load.get(load.id, 0.0) or 0.0))

                snapshot[load.id] = {
                    'served_grid_kw': 0.0,
                    'served_mps_kw': served_mps_kw,
                    'currently_served': served_mps_kw > 1e-6,
                    'reason': 'balanced' if load.id in target_load_ids else 'mps_not_targeted',
                }

        return snapshot

    def check_island_power_supply(self, island: Set[str]) -> bool:
        """Backward-compatible bool-only wrapper for island power evaluation."""
        evaluation = self._evaluate_island_power_supply(island)
        return bool(evaluation.get('can_supply', False))

    def update_system_state(self) -> None:
        """Update system state - called once per time step

        Update all load supply states based on current network topology and power source conditions
        """
        if not self.agent_manager:
            raise RuntimeError("EGraph.agent_manager not set. Use IndependentDSREnvironment instead of DSREnvironment.")

        # Reset per-step supply failure diagnostics
        self.last_supply_failures = []
        self.last_supply_snapshot = {}

        islands = self.identify_islands()

        for island in islands:
            # First check if the island has any loads
            has_load = False
            for node_id in island:
                loads = self.agent_manager.get_loads_at_node(node_id)
                if loads:  # If this node has loads
                    has_load = True
                    break

            # If the island has no loads, skip
            if not has_load:
                continue

            # First allocate power source output (set MPS Pout and Qout)
            self._allocate_power_supply_with_manager(island)

            # Check if this island can supply power (includes P/Q imbalance diagnostics)
            power_evaluation = self._evaluate_island_power_supply(island)
            can_supply = bool(power_evaluation.get('can_supply', False))

            if can_supply:
                # When power source is available, loads are automatically restored
                # Grid: Unlimited capacity, immediately restore all loads
                # MPS: Only restore loads specified in target_loads

                # Collect all MPS target_loads
                target_loads_to_restore = set()
                has_mps_with_targets = False
                has_grid = False

                # Check if Grid is present
                for node_id in island:
                    node = self.nodes.get(node_id)
                    if node and node.type == NodeType.GRID:
                        has_grid = True
                        break

                if has_grid:
                    # Has Grid -> restore all loads
                    for node_id in island:
                        loads = self.agent_manager.get_loads_at_node(node_id)
                        for load in loads:
                            if load.state == "off":
                                load.switch_on()
                else:
                    # Only MPS -> collect all MPS target_loads
                    for node_id in island:
                        node = self.nodes.get(node_id)
                        if node and node.type == NodeType.MPS:
                            mps = self.agent_manager.get_mobile_power_source(node_id)
                            if mps and mps.state == "connected":
                                if mps.target_loads:
                                    target_loads_to_restore.update(mps.target_loads)
                                    has_mps_with_targets = True

                    # Only restore loads in target_loads (and must be in current island)
                    if has_mps_with_targets and target_loads_to_restore:
                        for load_id in target_loads_to_restore:
                            load = self.agent_manager.get_load(load_id)
                            if load and load.node_id in island and load.state == "off":
                                load.switch_on()
            else:
                # Power does not satisfy supply conditions.
                # For cases with power source but imbalanced, record diagnostic information.
                # For cases without power source (MPS depleted/disconnected), force load shedding.
                failed_loads = []
                failed_load_ids = []
                island_pw = 0.0
                island_p_demand = 0.0
                island_q_demand = 0.0

                reason = power_evaluation.get("reason", "island_power_not_balanced")

                for node_id in island:
                    loads = self.agent_manager.get_loads_at_node(node_id)
                    for load in loads:
                        failed_load_ids.append(load.id)
                        island_p_demand += float(load.P)
                        island_q_demand += float(load.Q)
                        island_pw += float(load.P) * float(load.W)
                        failed_loads.append({
                            "load_id": load.id,
                            "node_id": load.node_id,
                            "state": load.state,
                            "P": load.P,
                            "Q": load.Q,
                            "W": load.W,
                            "restored": self.agent_manager.is_load_restored(load.id)
                        })

                # When there is NO power source at all (no Grid, no connected MPS),
                # force-shed loads so reward correctly reflects no power delivery.
                if reason in ('no_source', 'no_connected_mps', 'no_target_loads'):
                    for node_id in island:
                        loads_at_node = self.agent_manager.get_loads_at_node(node_id)
                        for load in loads_at_node:
                            if load.state == "on":
                                load.switch_off(force_system=True)

                self.last_supply_failures.append({
                    "island_nodes": sorted(list(island)),
                    "load_ids": sorted(failed_load_ids),
                    "loads": failed_loads,
                    "reason": reason,
                    "island_pw": island_pw,
                    "island_p_demand": island_p_demand,
                    "island_q_demand": island_q_demand,
                    "power_balance": {
                        "total_p_load": float(power_evaluation.get("total_p_load", 0.0) or 0.0),
                        "total_q_load": float(power_evaluation.get("total_q_load", 0.0) or 0.0),
                        "total_p_mps": float(power_evaluation.get("total_p_mps", 0.0) or 0.0),
                        "total_q_mps": float(power_evaluation.get("total_q_mps", 0.0) or 0.0),
                        "p_error": float(power_evaluation.get("p_error", 1.0) or 1.0),
                        "q_error": float(power_evaluation.get("q_error", 1.0) or 1.0),
                        "tolerance": float(power_evaluation.get("tolerance", 0.05) or 0.05),
                    },
                    "target_load_ids": list(power_evaluation.get("target_load_ids", [])),
                    "mps_nodes": list(power_evaluation.get("mps_nodes", [])),
                })

        # Refresh instantaneous supply snapshot for observation/reward consumers
        self.last_supply_snapshot = self.build_supply_snapshot()

    def _allocate_power_supply_with_manager(self, island: Set[str]) -> None:
        """Handle island power source state (using agent_manager)

        Note: This method no longer automatically allocates power. MPS output power is
        explicitly controlled by LLM through set_output().
        This method only resets MPS output to 0 when the island contains Grid.

        Args:
            island: Set of island nodes
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
        # No longer automatically allocates power

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
