"""
Agents
======
RepairCrew  — moves on TGraph, repairs faults
Scout       — moves on TGraph, discovers hidden faults
DamagePoint — a fault (hidden until discovered)
Load        — power consumer (ON if grid reaches it)
"""

from typing import List, Dict, Optional, Set


# ─────────────────────────────────────────────────────────────
class RepairCrew:
    """RC: moves to fault, repairs it."""

    def __init__(self, rc_id: str, position: str, speed: float, efficiency: float, resources: float):
        self.id          = rc_id
        self.position    = position
        self.speed       = speed           # km per step
        self.efficiency  = efficiency      # repair units per step
        self.resources   = resources       # total resource pool
        self.state       = 'idle'          # idle / moving / repairing
        self.path        = []
        self.remaining_distance = 0.0
        self.target      = None            # target node
        self.repair_target: Optional[str] = None   # fault id being repaired

    def move_to(self, path: List[str], distance: float):
        self.path = path
        self.remaining_distance = distance
        self.target = path[-1] if path else None
        self.state = 'moving'

    def step(self, damage_points: dict) -> List[str]:
        """Advance one time step. Returns list of events."""
        events = []

        if self.state == 'moving':
            self.remaining_distance -= self.speed
            if self.remaining_distance <= 0:
                self.position = self.target
                self.remaining_distance = 0
                self.state = 'idle'
                events.append(f'{self.id} arrived at {self.position}')

        elif self.state == 'repairing' and self.repair_target:
            dp = damage_points.get(self.repair_target)
            if dp and dp.state == 'active':
                actual = min(self.efficiency, self.resources, dp.demand - dp.progress)
                dp.progress += actual
                self.resources -= actual
                if dp.progress >= dp.demand:
                    dp.state = 'repaired'
                    self.state = 'idle'
                    self.repair_target = None
                    events.append(f'{self.id} repaired {dp.id}')
                if self.resources <= 0:
                    self.state = 'idle'

        return events

    def start_repair(self, fault_id: str):
        self.repair_target = fault_id
        self.state = 'repairing'

    def get_state(self) -> dict:
        return {
            'id': self.id, 'position': self.position,
            'state': self.state, 'resources': round(self.resources, 2),
            'remaining_distance': round(self.remaining_distance, 1),
            'repair_target': self.repair_target
        }


# ─────────────────────────────────────────────────────────────
class Scout:
    """Scout: explores network to discover hidden faults."""

    def __init__(self, scout_id: str, position: str, speed: float = 10.0):
        self.id          = scout_id
        self.position    = position
        self.speed       = speed
        self.state       = 'idle'          # idle / moving
        self.path        = []
        self.remaining_distance = 0.0
        self.target      = None
        self.visited: Set[str] = {position}
        self.found_faults: List[str] = []

    def move_to(self, path: List[str], distance: float):
        self.path = path
        self.remaining_distance = distance
        self.target = path[-1] if path else None
        self.state = 'moving'

    def step(self) -> Optional[str]:
        """Move one step. Returns new position if arrived, else None."""
        if self.state != 'moving':
            return None

        self.remaining_distance -= self.speed
        if self.remaining_distance <= 0:
            self.position = self.target
            self.remaining_distance = 0
            self.state = 'idle'
            self.visited.add(self.position)
            return self.position

        return None

    def get_state(self) -> dict:
        return {
            'id': self.id, 'position': self.position,
            'state': self.state,
            'visited_count': len(self.visited),
            'found_faults': self.found_faults,
            'remaining_distance': round(self.remaining_distance, 1),
            'target': self.target
        }


# ─────────────────────────────────────────────────────────────
class DamagePoint:
    """A fault — hidden until a Scout or RC discovers it."""

    def __init__(self, fault_id: str, fault_type: str, node: str = None,
                 edge: tuple = None, demand: float = 5.0, cap: int = 1):
        self.id        = fault_id
        self.type      = fault_type       # 'node' or 'edge'
        self.node      = node             # for node faults
        self.edge      = edge             # for edge faults (from, to)
        self.demand    = demand
        self.cap       = cap
        self.progress  = 0.0
        self.state     = 'active'         # active / repaired
        self.discovered = False
        self.discovered_by = None

    @property
    def location_str(self) -> str:
        if self.type == 'node':
            return self.node
        return f"{self.edge[0]}-{self.edge[1]}"

    def get_state(self) -> dict:
        return {
            'id': self.id, 'type': self.type,
            'location': self.location_str,
            'state': self.state,
            'progress': round(self.progress, 1),
            'demand': self.demand,
            'discovered': self.discovered,
            'discovered_by': self.discovered_by
        }


# ─────────────────────────────────────────────────────────────
class Load:
    """Power consumer node."""

    def __init__(self, load_id: str, node: str, P: float, Q: float, W: float):
        self.id    = load_id
        self.node  = node
        self.P     = P
        self.Q     = Q
        self.W     = W
        self.state = 'on'     # on / off

    @property
    def weighted_power(self) -> float:
        return self.W * self.P if self.state == 'on' else 0.0

    def get_state(self) -> dict:
        return {
            'id': self.id, 'node': self.node,
            'P': self.P, 'W': self.W, 'state': self.state,
            'weighted_power': self.weighted_power
        }
