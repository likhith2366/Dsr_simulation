"""
Agents
======
RepairCrew  — moves on TGraph, repairs faults
Scout       — moves on TGraph, discovers hidden faults
DamagePoint — a fault (hidden until discovered)
Load        — power consumer (ON if grid reaches it)

Time model:
  1 step = 1 hour
  speed  = km/hour
  distance tracked in km (fractional movement, no snap errors)
  Stats tracked per agent: km traveled, hours moving/repairing/idle
"""

from typing import List, Dict, Optional, Set


# ─────────────────────────────────────────────────────────────
class RepairCrew:

    def __init__(self, rc_id: str, position: str, speed: float,
                 efficiency: float, resources: float):
        self.id          = rc_id
        self.position    = position
        self.speed       = speed            # km/hour
        self.efficiency  = efficiency       # repair units/hour
        self.resources   = resources        # total repair resource pool
        self.state       = 'idle'           # idle / moving / repairing
        self.path        = []
        self.remaining_distance = 0.0       # km left to target
        self.distance_covered   = 0.0       # km already covered on current leg
        self.target      = None
        self.repair_target: Optional[str] = None
        self.on_edge: Optional[tuple] = None  # (from_node, to_node) when stopped on edge fault

        # ── Stats ──────────────────────────────────────────
        self.stats = {
            'total_km':        0.0,   # total distance traveled
            'hours_moving':    0,     # steps spent moving
            'hours_repairing': 0,     # steps spent repairing
            'hours_idle':      0,     # steps spent idle
            'faults_repaired': [],    # list of fault ids repaired
            'discovery_log':   [],    # [(step, fault_id, position)]
        }

    def move_to(self, path: List[str], distance: float):
        self.path = path
        self.remaining_distance = distance
        self.distance_covered   = 0.0
        self.target = path[-1] if path else None
        self.state  = 'moving'
        self.on_edge = None  # clear edge position when moving to a new target

    def step(self, damage_points: dict, current_time: int = 0) -> List[str]:
        """
        Advance one hour (1 step).
        Returns list of event strings.
        """
        events = []

        if self.state == 'moving':
            move = min(self.speed, self.remaining_distance)
            self.remaining_distance -= move
            self.distance_covered   += move
            self.stats['total_km']  += move
            self.stats['hours_moving'] += 1

            if self.remaining_distance <= 0:
                self.position = self.target
                self.remaining_distance = 0.0
                self.state = 'idle'
                events.append(f'{self.id} arrived at {self.position} '
                               f'(t={current_time}, total={self.stats["total_km"]:.1f}km)')

        elif self.state == 'repairing' and self.repair_target:
            dp = damage_points.get(self.repair_target)
            if dp and dp.state == 'active':
                actual = min(self.efficiency, self.resources,
                             dp.demand - dp.progress)
                dp.progress          += actual
                self.resources       -= actual
                self.stats['hours_repairing'] += 1

                if dp.progress >= dp.demand:
                    dp.state = 'repaired'
                    self.state = 'idle'
                    self.stats['faults_repaired'].append(self.repair_target)
                    self.repair_target = None
                    events.append(f'{self.id} repaired {dp.id} at t={current_time}')

                if self.resources <= 0:
                    self.state = 'idle'
                    self.repair_target = None
                    events.append(f'{self.id} out of resources at t={current_time}')
            else:
                self.state = 'idle'

        else:
            self.stats['hours_idle'] += 1

        return events

    def start_repair(self, fault_id: str):
        self.repair_target = fault_id
        self.state = 'repairing'

    def log_discovery(self, fault_id: str, step: int):
        self.stats['discovery_log'].append((step, fault_id, self.position))

    def get_state(self) -> dict:
        return {
            'id':                 self.id,
            'position':           self.position,
            'state':              self.state,
            'resources':          round(self.resources, 2),
            'remaining_distance': round(self.remaining_distance, 2),
            'repair_target':      self.repair_target,
            'stats':              {
                'total_km':        round(self.stats['total_km'], 1),
                'hours_moving':    self.stats['hours_moving'],
                'hours_repairing': self.stats['hours_repairing'],
                'hours_idle':      self.stats['hours_idle'],
                'faults_repaired': self.stats['faults_repaired'],
            }
        }


# ─────────────────────────────────────────────────────────────
class Scout:

    def __init__(self, scout_id: str, position: str, speed: float = 10.0):
        self.id          = scout_id
        self.position    = position
        self.speed       = speed            # km/hour
        self.state       = 'idle'
        self.path        = []
        self.remaining_distance = 0.0
        self.target      = None
        self.on_edge: Optional[tuple] = None
        self.visited: Set[str] = {position}
        self.found_faults: List[str] = []

        # ── Stats ──────────────────────────────────────────
        self.stats = {
            'total_km':      0.0,
            'hours_moving':  0,
            'hours_idle':    0,
            'nodes_visited': 1,
            'discovery_log': [],   # [(step, fault_id, position)]
        }

    def move_to(self, path: List[str], distance: float):
        self.path = path
        self.remaining_distance = distance
        self.target = path[-1] if path else None
        self.state  = 'moving'
        self.on_edge = None  # clear edge position when Scout starts a new journey

    def step(self, current_time: int = 0) -> Optional[str]:
        """Move one hour. Returns new position if arrived, else None."""
        if self.state != 'moving':
            self.stats['hours_idle'] += 1
            return None

        move = min(self.speed, self.remaining_distance)
        self.remaining_distance -= move
        self.stats['total_km']  += move
        self.stats['hours_moving'] += 1

        if self.remaining_distance <= 0:
            self.position = self.target
            self.remaining_distance = 0.0
            self.state = 'idle'
            self.visited.add(self.position)
            self.stats['nodes_visited'] = len(self.visited)
            return self.position

        return None

    def log_discovery(self, fault_id: str, step: int):
        self.found_faults.append(fault_id)
        self.stats['discovery_log'].append((step, fault_id, self.position))

    def get_state(self) -> dict:
        return {
            'id':                 self.id,
            'position':           self.position,
            'state':              self.state,
            'remaining_distance': round(self.remaining_distance, 2),
            'target':             self.target,
            'stats': {
                'total_km':      round(self.stats['total_km'], 1),
                'hours_moving':  self.stats['hours_moving'],
                'hours_idle':    self.stats['hours_idle'],
                'nodes_visited': self.stats['nodes_visited'],
                'faults_found':  len(self.found_faults),
                'discovery_log': self.stats['discovery_log'],
            }
        }


# ─────────────────────────────────────────────────────────────
class MPS:
    """
    Mobile Power Source.
    Moves to an isolated (unpowered) node, connects, and restores
    power to that island until the fault is repaired or energy runs out.
    """

    def __init__(self, mps_id: str, position: str, speed: float,
                 p_limit: float, energy: float):
        self.id         = mps_id
        self.position   = position
        self.speed      = speed       # km/hour
        self.p_limit    = p_limit     # kW max output
        self.energy     = energy      # kWh total energy remaining
        self.state      = 'idle'      # idle / moving / connected
        self.path       = []
        self.remaining_distance = 0.0
        self.target     = None

        self.stats = {
            'total_km':       0.0,
            'hours_moving':   0,
            'hours_connected': 0,
            'hours_idle':     0,
        }

    def move_to(self, path: List[str], distance: float):
        self.path = path
        self.remaining_distance = distance
        self.target = path[-1] if path else None
        self.state  = 'moving'

    def step(self, current_time: int = 0) -> Optional[str]:
        """Move one hour. Returns new position if arrived, else None."""
        if self.state == 'moving':
            move = min(self.speed, self.remaining_distance)
            self.remaining_distance -= move
            self.stats['total_km']  += move
            self.stats['hours_moving'] += 1

            if self.remaining_distance <= 0:
                self.position = self.target
                self.remaining_distance = 0.0
                self.state = 'idle'
                return self.position

        elif self.state == 'connected':
            consumed = min(self.p_limit, self.energy)
            self.energy -= consumed
            self.stats['hours_connected'] += 1
            if self.energy <= 0:
                self.energy = 0
                self.state  = 'idle'

        else:
            self.stats['hours_idle'] += 1

        return None

    def connect(self):
        if self.state == 'idle' and self.energy > 0:
            self.state = 'connected'

    def disconnect(self):
        if self.state == 'connected':
            self.state = 'idle'

    def get_state(self) -> dict:
        return {
            'id':       self.id,
            'position': self.position,
            'state':    self.state,
            'energy':   round(self.energy, 1),
            'p_limit':  self.p_limit,
            'stats':    {
                'total_km':        round(self.stats['total_km'], 1),
                'hours_moving':    self.stats['hours_moving'],
                'hours_connected': self.stats['hours_connected'],
                'hours_idle':      self.stats['hours_idle'],
            }
        }


# ─────────────────────────────────────────────────────────────
class DamagePoint:

    def __init__(self, fault_id: str, fault_type: str, node: str = None,
                 edge: tuple = None, demand: float = 5.0, cap: int = 1):
        self.id           = fault_id
        self.type         = fault_type
        self.node         = node
        self.edge         = edge
        self.demand       = demand
        self.cap          = cap
        self.progress     = 0.0
        self.state        = 'active'
        self.discovered   = False
        self.discovered_by = None
        self.discovered_at_step = None
        self.repaired_at_step   = None

    @property
    def location_str(self) -> str:
        if self.type == 'node':
            return self.node
        return f"{self.edge[0]}-{self.edge[1]}"

    def get_state(self) -> dict:
        return {
            'id':                 self.id,
            'type':               self.type,
            'location':           self.location_str,
            'state':              self.state,
            'progress':           round(self.progress, 1),
            'demand':             self.demand,
            'discovered':         self.discovered,
            'discovered_by':      self.discovered_by,
            'discovered_at_step': self.discovered_at_step,
            'repaired_at_step':   self.repaired_at_step,
        }


# ─────────────────────────────────────────────────────────────
class Load:

    def __init__(self, load_id: str, node: str, P: float, Q: float, W: float):
        self.id    = load_id
        self.node  = node
        self.P     = P
        self.Q     = Q
        self.W     = W
        self.state = 'on'

    @property
    def weighted_power(self) -> float:
        return self.W * self.P if self.state == 'on' else 0.0

    def get_state(self) -> dict:
        return {
            'id': self.id, 'node': self.node,
            'P': self.P, 'W': self.W,
            'state': self.state,
            'weighted_power': self.weighted_power
        }
