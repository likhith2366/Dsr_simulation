"""
TGraph + EGraph
===============
TGraph : road network for RC/Scout/MPS movement (Dijkstra)
EGraph : electrical network for power flow (island detection)
"""

import heapq
from typing import Dict, List, Tuple, Set, Optional


# ─────────────────────────────────────────────────────────────
# TGraph — Traffic / Road Graph
# ─────────────────────────────────────────────────────────────

class TGraph:
    """Road network. Agents move on this using Dijkstra shortest path."""

    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: Dict[str, dict] = {}          # edge_id → {from, to, distance}
        self.adjacency: Dict[str, List] = {}      # node → list of (neighbor, distance, edge_id)

    def add_node(self, node_id: str):
        self.nodes.add(node_id)
        if node_id not in self.adjacency:
            self.adjacency[node_id] = []

    def add_edge(self, edge_id: str, from_node: str, to_node: str, distance: float):
        self.add_node(from_node)
        self.add_node(to_node)
        self.edges[edge_id] = {'from': from_node, 'to': to_node, 'distance': distance}
        # Undirected
        self.adjacency[from_node].append((to_node, distance, edge_id))
        self.adjacency[to_node].append((from_node, distance, edge_id))

    def shortest_path(self, start: str, end: str) -> Tuple[List[str], float]:
        """Dijkstra. Returns (path, total_distance). Empty path if unreachable."""
        if start == end:
            return [start], 0.0
        if start not in self.nodes or end not in self.nodes:
            return [], -1

        dist = {n: float('inf') for n in self.nodes}
        dist[start] = 0
        prev = {}
        pq = [(0, start)]
        visited = set()

        while pq:
            d, node = heapq.heappop(pq)
            if node in visited:
                continue
            visited.add(node)
            if node == end:
                path = []
                cur = end
                while cur in prev:
                    path.append(cur)
                    cur = prev[cur]
                path.append(start)
                path.reverse()
                return path, dist[end]
            for neighbor, weight, _ in self.adjacency.get(node, []):
                nd = d + weight
                if nd < dist[neighbor]:
                    dist[neighbor] = nd
                    prev[neighbor] = node
                    heapq.heappush(pq, (nd, neighbor))

        return [], -1


# ─────────────────────────────────────────────────────────────
# EGraph — Electrical Graph
# ─────────────────────────────────────────────────────────────

class EGraph:
    """
    Electrical network.
    Tracks which edges are live/faulted/open.
    Determines which loads get power (island detection).
    """

    def __init__(self):
        self.nodes: Dict[str, str] = {}           # node_id → type (GRID/BUS/LOAD/SWITCH)
        self.edges: Dict[str, dict] = {}          # edge_id → {from, to, state}
        self.adjacency: Dict[str, List] = {}      # node → [(neighbor, edge_id)]

    def add_node(self, node_id: str, node_type: str):
        self.nodes[node_id] = node_type
        if node_id not in self.adjacency:
            self.adjacency[node_id] = []

    def add_edge(self, edge_id: str, from_node: str, to_node: str, state: str = 'closed'):
        """state: 'closed' (live), 'open' (switched off), 'faulted' (broken)"""
        self.edges[edge_id] = {'from': from_node, 'to': to_node, 'state': state}
        self.adjacency[from_node].append((to_node, edge_id))
        self.adjacency[to_node].append((from_node, edge_id))

    def set_edge_state(self, edge_id: str, state: str):
        if edge_id in self.edges:
            self.edges[edge_id]['state'] = state

    def get_powered_nodes(self) -> Set[str]:
        """
        BFS from GRID node through live edges.
        Returns all nodes reachable from grid (have power).
        """
        grid_nodes = [n for n, t in self.nodes.items() if t == 'GRID']
        if not grid_nodes:
            return set()

        powered = set()
        queue = list(grid_nodes)
        powered.update(grid_nodes)

        while queue:
            node = queue.pop(0)
            for neighbor, edge_id in self.adjacency.get(node, []):
                edge = self.edges[edge_id]
                if edge['state'] == 'closed' and neighbor not in powered:
                    powered.add(neighbor)
                    queue.append(neighbor)

        return powered

    def apply_fault(self, fault: dict):
        """Mark edges as faulted based on fault config."""
        if fault['type'] == 'node':
            # All edges connected to the faulted node become faulted
            node = fault['node']
            for edge_id, edge in self.edges.items():
                if edge['from'] == node or edge['to'] == node:
                    self.set_edge_state(edge_id, 'faulted')

        elif fault['type'] == 'edge':
            # Find and fault the matching edge
            fn, tn = fault['edge']
            for edge_id, edge in self.edges.items():
                if (edge['from'] == fn and edge['to'] == tn) or \
                   (edge['from'] == tn and edge['to'] == fn):
                    self.set_edge_state(edge_id, 'faulted')

    def restore_fault(self, fault: dict):
        """Restore edges after fault is repaired."""
        if fault['type'] == 'node':
            node = fault['node']
            for edge_id, edge in self.edges.items():
                if edge['from'] == node or edge['to'] == node:
                    if edge['state'] == 'faulted':
                        self.set_edge_state(edge_id, 'closed')

        elif fault['type'] == 'edge':
            fn, tn = fault['edge']
            for edge_id, edge in self.edges.items():
                if (edge['from'] == fn and edge['to'] == tn) or \
                   (edge['from'] == tn and edge['to'] == fn):
                    if edge['state'] == 'faulted':
                        self.set_edge_state(edge_id, 'closed')
