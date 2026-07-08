# How to Play the Manual DSR Simulator

You act as the policy. The simulator tells you what is happening and asks you what to do. Your goal: restore power to all 11 customers as fast as possible.

---

## Run It

```bash
cd a:\dsr_simulator_standalone
python training_model/manual_sim.py
```

Pick a case (default is Case1):

```bash
python training_model/manual_sim.py --case Case1
python training_model/manual_sim.py --case Case2
python training_model/manual_sim.py --case Case3
python training_model/manual_sim.py --case Case4
python training_model/manual_sim.py --case Case5
```

---

## The Network

```
Grid (N1)
  └── [S1] ── N2 ── N6 ── N7          Area 1 (S1 closed)
               ├── [S2] ── N4 ── N5   Area 2 (S2 closed)
               └── [S3] ── N3          Area 4 (S3 open if faulted)
                           ├── N10 ── N11, N12
                           ├── [S4] ── N8 ── N9    Area 3 (S4 open if faulted)
                           └── [S5] ── N13          Area 5 (S5 closed)
                                        └── V3, V2, V1

Tie switches (normally open):
  S6: V1 <-> N1     S7: N13 <-> V4     S8: N5 <-> N9
```

### Agent starting positions

| Agent | Starts at | Role |
|---|---|---|
| RC1 | N2 | Repair Crew — travel to fault and fix it |
| RC2 | N11 | Repair Crew |
| Scout1 | N2 | Fast searcher (10 km/h) — discovers hidden faults |
| MPS1 | N4 | Mobile Power Source — temporarily powers a dark area |

### Speeds

| Agent | Speed |
|---|---|
| RC | 2 km/h |
| Scout | 10 km/h |
| MPS | 6 km/h |

---

## The 5 Cases

| Case | Faults hidden where | What makes it hard |
|---|---|---|
| Case1 | 3 faults in Area 4 (N3, N10, N11) | Must search whole section |
| Case2 | Area 4 + Area 3 + Area 1 | Mixed outage, 2 RCs split work |
| Case3 | 3 faults in Area 1 | Blackout at main breaker S1 |
| Case4 | Main feeder + Area 4 + Area 3 | 3-stage restoration needed |
| Case5 | Main feeder + Area 4 + Area 1 | Most complex |

Faults are **hidden** — you do not know where they are. Send Scout to discover them.

---

## Each Turn

Every hour the simulator asks you what to do. You will see:

```
============================================================
  SIMULATOR -> YOU   [on_rc_idle]   t = 2 h
============================================================

  AGENTS
  RC1     pos=N3    state=idle
  RC2     pos=N11   state=moving  ->N10  (4.0km left, at N11->N10)
  Scout1  pos=N3    state=idle

  KNOWN FAULTS
  DP1  @ N3  state=active  progress=0%

  DARK NODES (no power)
  Load nodes (customers dark) : ['N10', 'N11', 'N12']
  Topo nodes (junctions dark) : ['N9']

  LOADS
  ON: 8   OFF: 3   Total: 11
    OFF L_N10   node=N10   P= 150kW  W=2
    ...

  SWITCHES
  [X] S1 = closed
  [ ] S3 = open
  ...
```

Then it asks:

```
  > Command for RC1 (press Enter to skip):
  > Send Scout1 to node (press Enter to skip):
```

---

## Commands You Can Type

The simulator asks separately for each agent. Here is exactly what each prompt accepts.

---

### RC (Repair Crew)

**When RC is IDLE:**

The prompt shows:
```
  RC1 is IDLE at N3
    Known faults: ['DP1']
    Options:
      * Type a node name to move there (e.g. N3, N10, V2)
      * Type a fault ID to repair it (e.g. DP1, DP2) -- only if RC is at the fault node
      * Press Enter to skip (RC stays idle)
  > Command for RC1:
```

| What you type | What happens |
|---|---|
| `N10` | RC moves to node N10 |
| `DP1` | RC starts repairing fault DP1 (only works if RC is already at that fault's node) |
| *(Enter)* | RC stays idle, nothing happens |

**When RC is MOVING:**

```
  RC1 is moving -> N10 (4.0km left)
  > Redirect RC1? Enter new node or press Enter to leave as-is:
```

| What you type | What happens |
|---|---|
| `N12` | RC changes destination to N12 |
| *(Enter)* | RC keeps going to its current target |

**When RC is REPAIRING:**

```
  RC1 is REPAIRING DP1 at N3 -- no input needed
```

No prompt — RC repairs automatically until done.

---

### Scout

**When Scout is IDLE:**

```
  Scout1 is IDLE at N3
    Unvisited nodes: ['N8', 'N10', 'N12', 'N13', 'V1', 'V2', 'V3']
  > Send Scout1 to node:
```

| What you type | What happens |
|---|---|
| `N10` | Scout moves to N10 (will discover any fault there) |
| *(Enter)* | Scout stays idle |

**When Scout is MOVING:**

```
  Scout1 is moving -> N10 (8.0km left)
  > Redirect Scout1? Enter new node or press Enter to leave as-is:
```

| What you type | What happens |
|---|---|
| `N12` | Scout changes destination to N12 |
| *(Enter)* | Scout keeps going to current target |

---

### MPS (Mobile Power Source)

**When MPS is IDLE:**

```
  MPS1 is IDLE at N8 (energy=5000kWh)
    Options:
      * Type "connect" to connect MPS here
      * Type a node name to move MPS there
      * Press Enter to leave idle
  > Command for MPS1:
```

| What you type | What happens |
|---|---|
| `connect` | MPS connects at current node, restoring power to that area |
| `N13` | MPS moves to node N13 |
| *(Enter)* | MPS stays idle |

> Note: `connect` only works if the section is safe — no active faults and all nodes in that area have been visited. If not safe, the simulator prints an error and skips.

**When MPS is CONNECTED:**

```
  MPS1 is CONNECTED at N8 (energy=4800kWh)
  > Disconnect MPS1? (y/n):
```

| What you type | What happens |
|---|---|
| `y` | MPS disconnects |
| `n` | MPS stays connected |

**When MPS is MOVING:**

```
  MPS1 is moving -> N8 (6.0km left)
    (leave it moving -- it will ask again when it arrives)
```

No input — MPS cannot be redirected mid-travel. It will ask you again when it arrives.

---

### Valid Node Names

These are the nodes you can send agents to:

| Area | Nodes |
|---|---|
| Area 1 (main feeder) | `N2`, `N6`, `N7` |
| Area 2 | `N4`, `N5` |
| Area 3 | `N8`, `N9` |
| Area 4 | `N3`, `N10`, `N11`, `N12` |
| Area 5 | `N13`, `V1`, `V2`, `V3` |
| Tie nodes | `V4` |

Switch nodes (`S1`–`S8`) are internal — do not send agents there.

### Valid Fault IDs

Fault IDs are shown in the **KNOWN FAULTS** section once a Scout discovers them. Typical IDs: `DP1`, `DP2`, `DP3`. Only use these with an idle RC that is already standing at the fault node.

### Skip / do nothing
Press **Enter** at any prompt to leave that agent as-is.

---

## Strategy Tips

### Step 1 — Setup (t=0)
- Send Scout to the dark area (e.g. `N3`, `N10`) to find faults fast
- Send RC1 toward the dark section to be nearby when Scout finds a fault
- Send MPS toward a node that can restore the most customers

### Step 2 — When Scout finds a fault
- The simulator will tell you: `*** Scout1 DISCOVERED DP1 at N3 ***`
- Send an RC directly to that fault node (e.g. `N3`)
- Keep Scout moving to the next unvisited node

### Step 3 — Repair
- When RC arrives at the fault node, type the fault ID (e.g. `DP1`) to start repair
- Repair takes a few hours — RC stays there automatically
- Send the other RC to search for remaining faults

### Step 4 — MPS (optional but speeds up score)
- MPS can power a dark section while waiting for repairs
- Only connect MPS if the section is safe (no active faults, or all nodes visited)
- The simulator will warn you if a section is not safe to connect

### Step 5 — Watch switches
- When a fault is repaired, the section switch closes automatically
- Tie switches (S6, S7, S8) also close automatically if an alternate path is available
- You do not need to manage switches manually in most cases

---

## Example Walkthrough — Case1

```
t=0  Setup:
       Send Scout1 -> N3  (it will sweep N3, N10, N11, N12)
       Send RC1    -> N3  (move toward the dark area)
       RC2 is at N11 — leave it, it will search from there
       Send MPS1   -> N8  (can restore Area 3 loads)

t=1  Scout1 arrives at N3, discovers DP1 @ N3
       Send Scout1 -> N10  (keep searching)
       Send RC1    -> N3   (already heading there — skip or confirm)

t=2  RC1 at N3 — type DP1 to start repair

t=3  Scout1 finds DP2 @ N10
       Send Scout1 -> N11
       Send RC2    -> N10

t=5  DP1 repaired by RC1, DP2 repaired by RC2
     Scout finds DP3 @ N11
       RC1 -> N11 to repair

t=7  DP3 repaired — all faults done, S3 closes, power restored
```

---

## Advancing Time

After you enter all commands, press **Enter** when prompted:

```
  [Press Enter to advance to t = 3h]
```

The simulator runs one hour of physics, prints what happened, then asks again.

---

## Ending

The simulator ends automatically when all faults are repaired:

```
============================================================
  ALL FAULTS REPAIRED at t = 7h
============================================================
  Final reward: 11800 / 11800
```

Or after 50 hours if not done.
