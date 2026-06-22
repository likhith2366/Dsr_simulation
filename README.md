# DSR Simulator — Multi-Agent Distribution System Restoration

A simulation framework for **Distribution System Restoration (DSR)** using multi-agent coordination on the IEEE-13 New Network. Agents discover unknown faults, restore power, and coordinate repairs under realistic constraints.

---

## Quickstart

```bash
# Clone the repo
git clone https://github.com/likhith2366/Dsr_simulation.git
cd Dsr_simulation

# Install dependencies
pip install matplotlib networkx

# Run all 5 cases — human-readable simulator ↔ policy communication
python training_model/run_cases.py

# Run all 5 cases — raw JSON (exact Python object simulator sends to policy)
python training_model/run_cases.py --raw

# Save outputs to file
python training_model/run_cases.py > training_model/output/full_run_output.txt
python training_model/run_cases.py --raw > training_model/output/full_run_raw.txt
```

---

## What the Command Prints

Every time the simulator sends a message to the policy and every action the policy sends back is printed in real time. This is the actual communication between simulator and policy — not a summary.

```
SIMULATOR -> POLICY  [on_scout_arrived]  t=1
  Scout1 arrived at N3
  rcs:
    [RC1]
      position     : N2
      state        : moving
      target       : N10
      repair_target: None
      resources    : 15
      km_left      : 6.0
      exact.at     : N2->N3
      exact.km_done: 4.0
    [RC2]
      position     : N11
      state        : repairing
      repair_target: DP2
      km_left      : 0.0
      exact.at     : N11
  scouts:
    [Scout1]
      position     : N3
      state        : idle
      km_left      : 0.0
      exact.at     : N3
  mps:
    [MPS1]
      position     : N4
      state        : moving
      energy       : 5000 kWh
      km_left      : 10.0
      exact.at     : N4->N8
  switches: {S1: closed, S2: closed, S3: open, S4: open, S5: closed, S6: open, S7: open, S8: open}
  dark (load nodes) : [N10, N11, N12, N13, N3, N8, V2]
  dark (topo only)  : [N9, V1, V3, V4]
  faults  : [DP1, DP2]

POLICY -> SIMULATOR  [actions]
  env.move_scout('Scout1', 'N8')
  env.move_rc('RC1', fault=DP1)
```

---

## Network — IEEE-13 New Network

8 switches (S1–S8), 4 tie nodes (V1–V4), 11 load nodes, **5 protected areas**.

```
Grid (N1)
  └── S1 ──► N2 ──► N6 ──► N7          [Area 1 — protected by S1]
               └──► S2 ──► N4 ──► N5   [Area 2 — protected by S2]
               └──► S3 ──► N3           [Area 4 — protected by S3]
                            └──► N10 ──► N11, N12
                            └──► S4 ──► N8 ──► N9   [Area 3 — protected by S4]
                            └──► S5 ──► N13          [Area 5 — protected by S5]
                                         └──► V3, V2, V1

Tie switches (normally open):
  S6: V1 ↔ N1       S7: N13 ↔ V4       S8: N5 ↔ N9
```

| Area | Nodes | Protected by | Fault effect |
|---|---|---|---|
| Area 1 | N2, N6, N7 | S1 (main breaker) | Total blackout |
| Area 2 | N4, N5 | S2 | Area 2 dark only |
| Area 3 | N8, N9 | S4 | Area 3 dark only |
| Area 4 | N3, N10, N11, N12 | S3 | Areas 3, 4, 5 dark |
| Area 5 | N13, V1, V2, V3 | S5 | Area 5 dark only |

Tie switches S6/S7/S8 close automatically once all faults in a section are repaired.

---

## Agent Types

| Agent | Role | Speed |
|---|---|---|
| **RC** (Repair Crew) | Travels to fault location and repairs it | 2 km/h |
| **Scout** | Fast searcher, physically discovers hidden faults | 10 km/h |
| **MPS** (Mobile Power Source) | Connects to unpowered node, restores load temporarily | 6 km/h |

---

## How It Works — Simulator and Policy

The simulator and policy are **fully separated**. The simulator handles all physics. The policy handles all decisions. They communicate through a structured object called `PolicyState`.

### Simulator (environment.py)

Runs the physics every timestep:
1. Moves each agent one hour along their assigned path
2. Checks if any agent physically arrived at a hidden fault — if yes, reveals it
3. Applies repair progress to active faults
4. Recomputes power flow (BFS on electrical graph)
5. Updates load on/off states
6. Closes tie switches if a section is now clear

At every event, the simulator builds a fresh `PolicyState` and calls the relevant policy callback.

### Policy (policy.py)

Receives `PolicyState` and makes all decisions:
- Where to send scouts and repair crews
- Which fault to repair next
- When and where to connect MPS
- Redirects agents when a new fault is discovered

The policy only sees what a real operator would know — hidden faults are invisible until an agent physically arrives there.

### PolicyState — What Simulator Sends to Policy

At every callback the simulator builds and sends this exact Python object:

```python
PolicyState {
    time = 0,

    rcs = {
        "RC1": {
            "id":                 "RC1",
            "position":           "N2",
            "state":              "moving",       # idle / moving / repairing
            "target":             "N10",
            "repair_target":      null,
            "resources":          15,
            "remaining_distance": 10.0,
            "exact": {
                "at":      "N2->N3",              # switch nodes hidden in label
                "segment": ["N2", "S3"],           # raw edge including switch nodes
                "km_done": 0.0,
                "km_left": 10.0
            },
            "stats": {
                "total_km": 0.0, "hours_moving": 0,
                "hours_repairing": 0, "hours_idle": 0, "faults_repaired": []
            }
        }
    },

    scouts = {
        "Scout1": {
            "id": "Scout1", "position": "N2", "state": "moving",
            "target": "N3", "remaining_distance": 8.0,
            "exact": { "at": "N2->N3", "segment": ["N2","S3"], "km_done": 0.0, "km_left": 8.0 },
            "stats": {
                "total_km": 0.0, "hours_moving": 0, "hours_idle": 0,
                "nodes_visited": 1, "faults_found": 0, "discovery_log": []
            }
        }
    },

    mps = {
        "MPS1": {
            "id": "MPS1", "position": "N4", "state": "moving",   # idle/moving/connected
            "target": "N10", "remaining_distance": 10.01,
            "energy": 5000,    # kWh remaining
            "p_limit": 600,    # kW max output
            "exact": { "at": "N4->N8", "segment": ["N4","N8"], "km_done": 0.0, "km_left": 10.01 },
            "stats": { "total_km": 0.0, "hours_moving": 0, "hours_connected": 0, "hours_idle": 0 }
        }
    },

    # Hidden faults are NOT present — only faults physically found by an agent appear here
    discovered_faults = {
        "DP1": {
            "id": "DP1", "type": "node", "location": "N3",
            "state": "active", "progress": 0.0, "demand": 5,
            "discovered_by": "Scout1", "discovered_at_step": 1, "repaired_at_step": null
        }
    },

    load_nodes      = {"N3","N4","N5","N6","N7","N8","N10","N11","N12","N13","V2"},
    dark_load_nodes = {"N3","N8","N10","N11","N12","N13","V2"},  # unpowered WITH demand
    dark_topo_nodes = {"N9","V1","V3","V4"},                     # unpowered, no load

    loads = {
        "L_N7":  { "node":"N7",  "state":"on",  "P":40,  "Q":15,  "W":5  },
        "L_N11": { "node":"N11", "state":"off", "P":200, "Q":80,  "W":10 },
        # ... all 11 loads
    },

    switches = { "S1":"closed", "S2":"closed", "S3":"open", "S4":"open",
                 "S5":"closed", "S6":"open", "S7":"open", "S8":"open" },

    global_visited   = {"N2", "N11"},
    globally_claimed = {"N2", "N11", "N10", "N3"},
    rc_searching     = {"RC1"},

    env    = <DSREnvironment>   # policy calls actions here: state.env.move_rc(...)
    tgraph = <TGraph>           # policy queries paths here: state.tgraph.shortest_path(...)
}
```

### Policy Callbacks — When Simulator Calls Policy

| Callback | Trigger |
|---|---|
| `on_setup` | Simulation start — assign all agents |
| `on_scout_arrived` | Scout reaches a node — send to next unvisited |
| `on_rc_idle` | RC has nothing to do — start repair or assign target |
| `on_fault_discovered` | Agent physically finds a hidden fault — redirect RCs |
| `on_mps_arrived` | MPS reaches a node — connect or wait |
| `on_mps_idle` | MPS finishes session — reconnect or reassign |

### Policy Actions — What Policy Sends Back

```python
state.env.move_rc(rc_id, target_node)
state.env.move_scout(scout_id, target_node)
mps.move_to(path, distance)
rc.start_repair(fault_id)
mps.connect()
mps.disconnect()
state.env.open_switch(switch_id)
state.env.close_switch(switch_id)
```

### Node ≠ Load

Topology nodes (junctions) and load nodes (with P/Q demand) are explicitly separated. `dark_load_nodes` are the high-priority search targets — nodes where customers are without power. `dark_topo_nodes` are pure junction points with no load. The policy searches load nodes first.

---

## Project Structure

```
training_model/
├── core/
│   ├── environment.py        # Simulator — physics, step logic, PolicyState
│   ├── policy.py             # Policy — all decisions, 6 callbacks
│   ├── agents.py             # RC, Scout, MPS, DamagePoint, Load
│   └── graphs.py             # TGraph (travel), EGraph (electrical)
├── config/
│   └── ieee13new_cases.py    # Network topology + 5 training cases
├── visualizer.py             # Network visualization (PNG per step)
├── run_cases.py              # Main runner — all 5 cases
└── output/                   # Generated PNGs + full_run_output.txt
```

---

## Results

All 5 cases — unknown fault mode, 11/11 loads restored, reward 11800/11800.

| Case | Time (h) | Faults | Scenario |
|---|---|---|---|
| Case 1 | 7  | 3 × Area 4 | Full section search |
| Case 2 | 11 | Area 4 + Area 3 + Area 1 | Mixed outage |
| Case 3 | 11 | 3 × Area 1 | No section switch trips |
| Case 4 | 15 | Main feeder + Area 4 + Area 3 | 3-stage restoration |
| Case 5 | 18 | Main feeder + Area 4 + Area 1 | Complex multi-stage |
