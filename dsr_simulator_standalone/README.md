# DSR Simulator - Distribution System Restoration Simulator

> Distribution System Restoration (DSR) Simulator for IEEE-13 Bus System

## Overview

This simulator is designed for Distribution System Restoration (DSR) simulation. Based on the IEEE-13 bus distribution system, it simulates the post-disaster restoration process involving **repair crew dispatching**, **mobile power source deployment**, and **network reconfiguration** decisions.

### Core Objective
After a distribution network suffers multiple faults, coordinate the following resources to maximize weighted load restoration (sum of W_i x P_i):
- **RC (Repair Crew)** - Repair crews: move to fault locations to perform repairs
- **MPS (Mobile Power Source)** - Mobile power sources: temporarily supply power to de-energized areas
- **Switch** - Switch operations: restore power supply through network reconfiguration

---

## System Architecture

```
dsr_simulator_standalone/
├── __init__.py              # Package entry point, exports DSRSimulator and IEEE13Config
├── README.md                # This file
├── demo.py                  # Complete usage examples
│
├── core/                    # Core simulation engine
│   ├── __init__.py
│   ├── agents.py            # Agent entity classes (RC, MPS, DP, Load, Switch)
│   ├── agent_manager.py     # Instance-based agent manager (supports parallel training)
│   ├── graphs.py            # Dual graph model (Traffic graph TGraph + Electrical graph EGraph)
│   ├── environment.py       # Environment state management and simulation stepping
│   └── dsr_interface.py     # DSR main interface (coordinates all operations)
│
└── ieee13/                  # IEEE-13 system configuration
    ├── __init__.py
    ├── ieee13_config.py     # System topology, load data, 10 training scenarios
    └── ieee13_interface.py  # IEEE-13 wrapper interface
```

---

## Core Concepts

### 1. Dual Graph Model

The simulator uses two graphs to model the distribution system:

| Graph Type | Purpose | Description |
|------------|---------|-------------|
| **TGraph** (Traffic Graph) | RC/MPS movement path planning | Undirected weighted graph, edge weight = distance (km), Dijkstra shortest path |
| **EGraph** (Electrical Graph) | Electrical connectivity analysis | Undirected graph, edges can be connected/disconnected/faulted, supports island detection and cycle detection |

```
                    TGraph (Traffic Graph)                    EGraph (Electrical Graph)
            RC/MPS move on this graph                  Power flows on this graph

     Grid ──2km── N1 ──2km── N2                Grid ── N1 ── N2 ── S1 ── N3
                               │                              │         │
                          4km  │                              N4        N8
                               │                              │         │
                               N4 ──2km── N5                  N5        N9
```

### 2. Agents

#### RC (Repair Crew)
```
States: idle → moving → idle → repairing → idle → out_of_service
Attributes: position, speed(km/h), efficiency(p.u./step), resources(p.u.)
Actions: move(target_node), repair(fault_id)
```
- Movement consumes time (distance/speed), does not consume resources
- Repair consumes resources, repairs up to `efficiency` p.u. per step
- Becomes `out_of_service` when resources are depleted

#### MPS (Mobile Power Source)
```
States: idle → moving → idle → connected → out_of_service
Attributes: position, speed(km/h), p_limit(kW), s_limit(kVA), energy(kWh)
Actions: move(target_node), set_output(P, Q, target_loads)
```
- After connecting to a node, supplies power to specified `target_loads`
- Consumes `Pout` kWh of energy per step
- Automatically disconnects when energy is depleted, becomes `out_of_service`
- Supports multi-MPS coordinated power supply (proportional allocation for same target_loads)

#### DP (Damage Point)
```
Types: node fault / edge fault
Attributes: repair_demand, repair_progress, capacity (max parallel repair count)
States: active → repaired
```
- Node fault: affects all electrical edges connected to that node
- Edge fault: affects a specific edge, inserts a fault node in the traffic graph

#### Load
```
Attributes: P (kW active power), Q (kVar reactive power), W (weight/priority)
States: on (energized) / off (de-energized)
Auto-managed: automatically turns on when power is restored, turns off when power is lost
```

#### Switch
```
Types: S1 (normally closed), S2 (normally open, for network reconfiguration)
States: open / close
Constraint: loops are not allowed (radial topology must be maintained)
```

### 3. IEEE-13 Bus System

```
Topology:
                                Grid (Utility)
                                  │
                                  N1 ─── V2 ─── V3 ─── S2 ─── V1 ─── N13
                                  │                     │              │
                                  N2                    (normally open) N3
                                / | \                                /  |  \
                              N4  N6  S1 ────── N3 ────── N10       N8
                              │   │                        │ \       │
                              N5  N7                      N11 N12   N9

Load Data (9 load nodes):
┌────────┬────────┬─────────┬──────────┬──────────────────────────┐
│ Load   │ P (kW) │ Q (kVar)│ W (weight)│ Description             │
├────────┼────────┼─────────┼──────────┼──────────────────────────┤
│ L_N2   │  250   │   120   │   1.0    │ Low priority             │
│ L_N3   │  400   │   300   │   6.0    │ High priority            │
│ L_N5   │  500   │   300   │   5.0    │ Large load               │
│ L_N6   │   10   │     5   │   4.0    │ Small load               │
│ L_N7   │   40   │    15   │   5.0    │                          │
│ L_N8   │  150   │    70   │   2.0    │                          │
│ L_N9   │  500   │   200   │   4.0    │ Large load               │
│ L_N11  │  200   │    80   │  10.0    │ Highest priority         │
│ L_N12  │  150   │   -80   │   5.0    │ Capacitive load (Q < 0)  │
└────────┴────────┴─────────┴──────────┴──────────────────────────┘
Total active power: ~2,200 kW | Total weighted power: ~10,440 (sum of W*P)
```

---

## Quick Start

### Dependencies
- Python 3.9+
- No external dependencies (pure Python standard library)

### Basic Usage

```python
import sys
sys.path.append('/path/to/parent/of/dsr_simulator_standalone')

from dsr_simulator_standalone import DSRSimulator

# 1. Create simulator instance
sim = DSRSimulator()

# 2. Set up scenario (Case1 ~ Case10)
sim.setup_case('Case1')
sim.setup_ieee13_scenario()

# 3. View initial state
state = sim.get_current_state()
print(f"Time: {state['time']}")
print(f"Damage points: {list(state['damage_points'].keys())}")
print(f"Repair crews: {list(state['repair_crews'].keys())}")
print(f"Mobile power sources: {list(state['mobile_power'].keys())}")

# 4. Execute actions
# Move repair crew to fault point
sim.move_repair_crew('RC1', 'DP1')

# Advance time
result = sim.advance_time()

# Repair fault
sim.repair_fault('RC1', 'DP1', auto_repair=True)

# Move MPS and supply power
sim.move_mps('MPS1', 'N8')
result = sim.advance_time()  # Wait for arrival
sim.set_mps_output('MPS1', P_out=500, Q_out=200, target_loads=['L_N8', 'L_N9'])

# Operate switches
sim.operate_switches([{'switch_id': 'S1', 'operation': 'open'}])

# 5. View updated state
state = sim.get_current_state()
```

For more detailed examples, run `demo.py`.

---

## Training Scenarios (Training Cases)

There are 10 training scenarios, each with different RC/MPS configurations and fault locations:

| Case | RC Count | MPS Count | Fault Count | Fault Types | Difficulty Description |
|------|----------|-----------|-------------|-------------|----------------------|
| Case1 | 2 | 2 | 3 | 2 node + 1 edge | Medium, requires RC and MPS coordination |
| Case2 | 2 | 2 | 5 | All edge faults | Hard, 5 fault points, includes trunk line fault |
| Case3 | 2 | 2 | 4 | 1 node + 3 edge | Medium, includes switch area fault |
| Case4 | 2 | 2 | 5 | 2 node + 3 edge | Hard, includes reconfiguration path fault |
| Case5 | 2 | 2 | 5 | Same as Case4 | Case4 variant |
| Case6 | 2 | 2 | 3 | All edge faults | Medium, includes high repair demand fault |
| Case7 | 2 | 2 | 2 | 1 node + 1 edge | Easy, but high repair demand (cap=2) |
| Case8 | 2 | 2 | 4 | 1 node + 3 edge | Medium, limited RC resources |
| Case9 | 2 | 2 | 3 | 1 node + 2 edge | Medium |
| Case10| 2 | 2 | 4 | All edge faults | Hard, 4 edge faults |

---

## Key Design Decisions

### Instance-based Architecture
Each environment instance has its own independent `AgentManager`, without using class variables, supporting multi-process parallel training.

### Automatic Load Management
Load states (on/off) are automatically managed by the system:
- Power restored (Grid reconnection / MPS power supply) -> automatically `switch_on`
- Power lost (fault / MPS depleted) -> automatically `switch_off`

### Cycle Detection
Distribution systems must maintain a radial topology (no cycles). Cycle detection is performed automatically before switch operations, and violating operations are rolled back.

### MPS Power Projection
MPS output is automatically projected to actual load demand, ensuring power balance (sum of P_MPS = sum of P_load).

---

## API Reference

### DSRSimulator (IndependentIEEE13DSRInterface)

#### Initialization and Reset
| Method | Description |
|--------|-------------|
| `setup_case(case_name)` | Set up training scenario |
| `setup_ieee13_scenario()` | Initialize scenario (add RC/MPS/DP/Load/Switch) |
| `reset(episode_config)` | Reset for a new episode |
| `get_current_state()` | Get complete system state |

#### RC Operations
| Method | Description |
|--------|-------------|
| `move_repair_crew(rc_id, target)` | Move RC to target position (supports automatic DP conversion) |
| `repair_fault(rc_id, fault_id, auto_repair=False)` | Execute repair (auto_repair=True for automatic continuous repair) |

#### MPS Operations
| Method | Description |
|--------|-------------|
| `move_mps(mps_id, target)` | Move MPS to target node |
| `set_mps_output(mps_id, P_out, Q_out, target_loads)` | Set MPS output power and target loads |

#### Switch Operations
| Method | Description |
|--------|-------------|
| `operate_switches(switch_ops)` | Batch switch operations, format: `[{'switch_id': 'S1', 'operation': 'open'}]` |

#### Time Advancement
| Method | Description |
|--------|-------------|
| `advance_time()` | Advance one time step, returns event list |

### State Dictionary Structure (get_current_state() return value)

```python
{
    'time': int,                    # Current simulation time step
    'repair_crews': {               # Repair crew states
        'RC1': {
            'current_position': str,   # Current position
            'state': str,              # idle/moving/repairing/out_of_service
            'remaining_resources': float,
            'remaining_distance': float,
            ...
        }
    },
    'mobile_power': {               # Mobile power source states
        'MPS1': {
            'current_position': str,
            'state': str,              # idle/moving/connected/out_of_service
            'energy': float,           # Remaining energy (kWh)
            'Pout': float,             # Current active power output (kW)
            'target_loads': list,      # List of served loads
            ...
        }
    },
    'damage_points': {              # Damage point states
        'DP1': {
            'state': str,              # active/repaired
            'repair_progress': float,
            'repair_demand': float,
            ...
        }
    },
    'loads': {                      # Load states
        'L_N3': {
            'P': float, 'Q': float, 'W': float,
            'state': str,              # on/off
            'served_grid_kw': float,   # Grid-supplied power
            'served_mps_kw': float,    # MPS-supplied power
            ...
        }
    },
    'switches': {                   # Switch states
        'S1': {'state': str},       # open/close
        'S2': {'state': str},
    },
    'grid': {                       # System global information
        'faults_active': int,
        'has_cycle': bool,
        'islands_list': list,       # Electrical island list
    }
}
```

---

## File Descriptions

### core/agents.py (~1,670 lines)
Defines 5 agent entity classes:
- `Switch`: Switch device, controls electrical edge connection/disconnection
- `RC`: Repair crew, supports movement (`move`) and repair (`repair`)
- `Load`: Load, automatically manages on/off state
- `MPS`: Mobile power source, supports movement, connection, and output power setting
- `DP`: Damage point, supports node faults and edge faults

### core/agent_manager.py (~350 lines)
Instance-based management of all agents, replaces class variable approach, supports parallel training.
Provides `export_state()`/`import_state()` for state snapshots.

### core/graphs.py (~915 lines)
- `TGraph`: Traffic graph (Dijkstra shortest path, edge splitting)
- `EGraph`: Electrical graph (island detection, cycle detection, power balance, automatic load management)

### core/environment.py (~480 lines)
Environment state management, contains `step()` method (advance time, update RC/MPS, detect events).

### core/dsr_interface.py (~1,300+ lines)
Main interface class, provides all user-callable APIs (move RC/MPS, repair faults, set MPS output, etc.).

### ieee13/ieee13_config.py (~445 lines)
Complete configuration for the IEEE-13 system (19 nodes, 19 electrical edges, 4 traffic-only roads, 9 loads, 2 switches, 10 training scenarios).

### ieee13/ieee13_interface.py (~345 lines)
Dedicated wrapper for the IEEE-13 system, inherits from `IndependentDSRInterface`, responsible for reading configuration and initializing the system.
