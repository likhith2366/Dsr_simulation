"""
Scout Agent
===========
A new agent type that searches the network to discover hidden faults.

Unlike RC:
  - Scout does NOT repair
  - Scout moves fast, covers more ground
  - Scout reports discovered faults to FaultDiscoveryManager
  - Scout uses DFS-based search strategy (visits unvisited nodes first)

States:
  idle      → waiting for search assignment
  searching → moving to next unvisited node
  reporting → fault found, notifying system
"""

import heapq
from typing import List, Optional, Dict, Set, Tuple


class ScoutAgent:
    """
    Scout agent that explores the network to find hidden faults.
    Moves on TGraph just like RC/MPS.
    """

    def __init__(self, scout_id: str, initial_position: str, speed: float = 10.0):
        """
        Args:
            scout_id: Unique identifier (e.g. 'Scout1')
            initial_position: Starting node
            speed: km/h - scouts are fast (default 10km/h)
        """
        self.id = scout_id
        self.current_position = initial_position
        self.speed = speed
        self.state = 'idle'                    # idle / searching / reporting

        # Movement tracking
        self.path = []                         # planned path to next target
        self.remaining_distance = 0.0          # km left to travel
        self.target_node = None                # current movement target

        # Discovery tracking
        self.visited_nodes: Set[str] = {initial_position}   # nodes already visited
        self.discovered_faults: List[Dict] = []              # faults found so far
        self.search_queue: List[str] = []                    # nodes to visit next

    def assign_search_path(self, path: List[str], distance: float):
        """Assign a path for the scout to travel."""
        self.path = path
        self.remaining_distance = distance
        self.target_node = path[-1] if path else None
        self.state = 'searching'

    def update_position(self):
        """Move scout along its path by one step."""
        if self.state != 'searching' or not self.path:
            return

        move_amount = self.speed

        if move_amount >= self.remaining_distance:
            # Arrived at target
            self.current_position = self.target_node
            self.visited_nodes.add(self.current_position)
            self.remaining_distance = 0.0
            self.path = []
            self.state = 'idle'
        else:
            self.remaining_distance -= move_amount

    def report_fault(self, fault_id: str, location: str, fault_type: str):
        """Called when scout discovers a fault at current position."""
        discovery = {
            'fault_id': fault_id,
            'location': location,
            'type': fault_type,
            'discovered_by': self.id,
            'discovered_at_position': self.current_position
        }
        self.discovered_faults.append(discovery)
        self.state = 'reporting'
        return discovery

    def get_unvisited_neighbors(self, tgraph) -> List[Tuple[str, float]]:
        """
        Get neighboring nodes not yet visited, sorted by distance (closest first).
        Used to decide where to search next.
        """
        neighbors = []
        for edge in tgraph.get_node_edges(self.current_position):
            neighbor = edge.to_node if edge.from_node == self.current_position else edge.from_node
            if neighbor not in self.visited_nodes:
                neighbors.append((neighbor, edge.distance))

        # Sort by distance - visit closest unvisited first
        neighbors.sort(key=lambda x: x[1])
        return neighbors

    def get_state(self) -> Dict:
        """Return current scout state for observation."""
        return {
            'id': self.id,
            'current_position': self.current_position,
            'state': self.state,
            'visited_nodes': list(self.visited_nodes),
            'visited_count': len(self.visited_nodes),
            'discovered_faults': self.discovered_faults,
            'remaining_distance': self.remaining_distance,
            'target_node': self.target_node
        }

    def __repr__(self):
        return (f"Scout({self.id} @ {self.current_position}, "
                f"state={self.state}, visited={len(self.visited_nodes)} nodes, "
                f"found={len(self.discovered_faults)} faults)")
