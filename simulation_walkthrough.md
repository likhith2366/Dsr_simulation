# Simulation Walkthrough — IEEE-13 New Network

Detailed per-step state for all 5 cases under **UNKNOWN-fault** mode (Scout searches, RCs repair). Each step records:

- Fault positions, levels (demand), and status (hidden / discovered / repaired)
- RC and Scout positions, speed, remaining resources, current action
- MPS position, speed, limit, remaining energy, connection state
- Switch / breaker states (CLOSED / OPEN / FAULTED)
- Section status (LIVE / PARTIAL / DARK with dark-node list)
- Loads ON/OFF count (V2 has a load — V-tie nodes can carry load)

> Note: in the newest network, V-nodes can have loads. V2 has `L_V2` (120 kW, weight 8). V1, V3, V4 are tie nodes without loads.


---

## Case1

**Scenario:** 3 hidden faults  ·  2 RC  ·  1 MPS  ·  1 Scout

### Initial State  (t = 0 h)

- Loads ON: **4/11**  ·  Reward: **2990** / 11800

**Faults**
  - **DP1** at `N3–N10` (edge)  ·  level 4  ·  cap 1  ·  HIDDEN
  - **DP2** at `N11` (node)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)
  - **DP3** at `N8–N9` (edge)  ·  level 4  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N2`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `S6` (2.0km left)
  - **RC2** @ `N11`  ·  speed 5km/h  ·  resources 15.0  ·  repairing on `DP2`

**Scouts**
  - **Scout1** @ `N2`  ·  speed 10.0km/h  ·  moving → `S3` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N4`  ·  speed 8km/h  ·  limit 600kW  ·  energy 5000kWh  ·  moving → `N10` (10.0km left)

**Switches / Breakers**
  - CLOSED: S1, S2, S5
  - OPEN  : S3, S4, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 1  (t = 1 h)

**Events**
  - RC1 arrived at S6 (t=1, total=2.0km)
  - Scout Scout1 arrived at S3

### State after step 1

- Loads ON: **4/11**  ·  Reward: **2990** / 11800

**Faults**
  - **DP1** at `N3–N10` (edge)  ·  level 4  ·  cap 1  ·  HIDDEN
  - **DP2** at `N11` (node)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 3/5)
  - **DP3** at `N8–N9` (edge)  ·  level 4  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `S6`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `V1` (6.0km left)
  - **RC2** @ `N11`  ·  speed 5km/h  ·  resources 12.0  ·  repairing on `DP2`

**Scouts**
  - **Scout1** @ `S3`  ·  speed 10.0km/h  ·  moving → `S8` (6.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N4`  ·  speed 8km/h  ·  limit 600kW  ·  energy 5000kWh  ·  moving → `N10` (2.0km left)

**Switches / Breakers**
  - CLOSED: S1, S2, S5
  - OPEN  : S3, S4, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 2  (t = 2 h)

**Events**
  - RC2 repaired DP2 at t=2
  - Scout Scout1 arrived at S8
  - MPS1 arrived at N10
  - MPS1 standing by at N10 — awaiting section clearance
  - MPS1 standing by at N10 — awaiting section clearance

### State after step 2

- Loads ON: **4/11**  ·  Reward: **2990** / 11800

**Faults**
  - **DP1** at `N3–N10` (edge)  ·  level 4  ·  cap 1  ·  HIDDEN
  - **DP2** at `N11` (node)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N8–N9` (edge)  ·  level 4  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `S6`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `V1` (2.0km left)
  - **RC2** @ `N11`  ·  speed 5km/h  ·  resources 10.0  ·  moving → `N10` (4.0km left)

**Scouts**
  - **Scout1** @ `S8`  ·  speed 10.0km/h  ·  moving → `N9` (6.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N10`  ·  speed 8km/h  ·  limit 600kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S5
  - OPEN  : S3, S4, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 3  (t = 3 h)

**Events**
  - RC1 arrived at V1 (t=3, total=8.0km)
  - RC2 arrived at N10 (t=3, total=4.0km)
  - *** RC RC2 DISCOVERED DP1 at N10 (t=3h) ***
  - Scout Scout1 arrived at N9
  - *** Scout Scout1 DISCOVERED DP3 at N9 (t=3h) ***
  - MPS1 standing by at N10 — awaiting section clearance
  - RC1 moving to discovered fault DP1
  - RC2 traversing fault edge to N3

### State after step 3

- Loads ON: **4/11**  ·  Reward: **2990** / 11800

**Faults**
  - **DP1** at `N3–N10` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)
  - **DP2** at `N11` (node)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N8–N9` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)

**Repair Crews**
  - **RC1** @ `V1`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `N3` (12.0km left)
  - **RC2** @ `N10`  ·  speed 5km/h  ·  resources 10.0  ·  moving → `N3` (2.0km left)

**Scouts**
  - **Scout1** @ `N9`  ·  speed 10.0km/h  ·  moving → `N8` (4.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N10`  ·  speed 8km/h  ·  limit 600kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S5
  - OPEN  : S3, S4, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 4  (t = 4 h)

**Events**
  - RC2 arrived at N3 (t=4, total=6.0km)
  - Scout Scout1 arrived at N8
  - MPS1 standing by at N10 — awaiting section clearance
  - RC1 redirected to fault DP3
  - RC2 auto-started repair of DP1

### State after step 4

- Loads ON: **4/11**  ·  Reward: **2990** / 11800

**Faults**
  - **DP1** at `N3–N10` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)
  - **DP2** at `N11` (node)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N8–N9` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)

**Repair Crews**
  - **RC1** @ `V1`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `N8` (14.0km left)
  - **RC2** @ `N3`  ·  speed 5km/h  ·  resources 10.0  ·  repairing on `DP1`

**Scouts**
  - **Scout1** @ `N8`  ·  speed 10.0km/h  ·  moving → `S4` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N10`  ·  speed 8km/h  ·  limit 600kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S5
  - OPEN  : S3, S4, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 5  (t = 5 h)

**Events**
  - Scout Scout1 arrived at S4
  - MPS1 standing by at N10 — awaiting section clearance

### State after step 5

- Loads ON: **4/11**  ·  Reward: **2990** / 11800

**Faults**
  - **DP1** at `N3–N10` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 3/4)
  - **DP2** at `N11` (node)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N8–N9` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)

**Repair Crews**
  - **RC1** @ `V1`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `N8` (10.0km left)
  - **RC2** @ `N3`  ·  speed 5km/h  ·  resources 7.0  ·  repairing on `DP1`

**Scouts**
  - **Scout1** @ `S4`  ·  speed 10.0km/h  ·  moving → `N12` (4.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N10`  ·  speed 8km/h  ·  limit 600kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S5
  - OPEN  : S3, S4, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 6  (t = 6 h)

**Events**
  - RC2 repaired DP1 at t=6
  - Scout Scout1 arrived at N12
  - MPS1 moving to N8 (restores 1 loads)

### State after step 6

- Loads ON: **10/11**  ·  Reward: **9800** / 11800

**Faults**
  - **DP1** at `N3–N10` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP2** at `N11` (node)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N8–N9` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)

**Repair Crews**
  - **RC1** @ `V1`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `N8` (6.0km left)
  - **RC2** @ `N3`  ·  speed 5km/h  ·  resources 6.0  ·  moving → `V4` (12.0km left)

**Scouts**
  - **Scout1** @ `N12`  ·  speed 10.0km/h  ·  moving → `S7` (12.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N10`  ·  speed 8km/h  ·  limit 600kW  ·  energy 5000kWh  ·  moving → `N8` (4.0km left)

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S5
  - OPEN  : S4, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 7  (t = 7 h)

**Events**
  - MPS1 arrived at N8
  - MPS1 standing by at N8 — awaiting section clearance
  - MPS1 standing by at N8 — awaiting section clearance

### State after step 7

- Loads ON: **10/11**  ·  Reward: **9800** / 11800

**Faults**
  - **DP1** at `N3–N10` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP2** at `N11` (node)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N8–N9` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)

**Repair Crews**
  - **RC1** @ `V1`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `N8` (2.0km left)
  - **RC2** @ `N3`  ·  speed 5km/h  ·  resources 6.0  ·  moving → `V4` (7.0km left)

**Scouts**
  - **Scout1** @ `N12`  ·  speed 10.0km/h  ·  moving → `S7` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N8`  ·  speed 8km/h  ·  limit 600kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S5
  - OPEN  : S4, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 8  (t = 8 h)

**Events**
  - RC1 arrived at N8 (t=8, total=26.0km)
  - Scout Scout1 arrived at S7
  - MPS1 standing by at N8 — awaiting section clearance
  - RC2 redirected to fault DP3
  - RC1 traversing fault edge to N9

### State after step 8

- Loads ON: **10/11**  ·  Reward: **9800** / 11800

**Faults**
  - **DP1** at `N3–N10` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP2** at `N11` (node)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N8–N9` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)

**Repair Crews**
  - **RC1** @ `N8`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `N9` (4.0km left)
  - **RC2** @ `N3`  ·  speed 5km/h  ·  resources 6.0  ·  moving → `N8` (2.0km left)

**Scouts**
  - **Scout1** @ `S7`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N8`  ·  speed 8km/h  ·  limit 600kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S5
  - OPEN  : S4, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 9  (t = 9 h)

**Events**
  - RC1 arrived at N9 (t=9, total=30.0km)
  - RC2 arrived at N8 (t=9, total=18.0km)
  - MPS1 standing by at N8 — awaiting section clearance
  - RC1 auto-started repair of DP3
  - RC2 traversing fault edge to N9

### State after step 9

- Loads ON: **10/11**  ·  Reward: **9800** / 11800

**Faults**
  - **DP1** at `N3–N10` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP2** at `N11` (node)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N8–N9` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)

**Repair Crews**
  - **RC1** @ `N9`  ·  speed 4km/h  ·  resources 15.0  ·  repairing on `DP3`
  - **RC2** @ `N8`  ·  speed 5km/h  ·  resources 6.0  ·  moving → `N9` (4.0km left)

**Scouts**
  - **Scout1** @ `S7`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N8`  ·  speed 8km/h  ·  limit 600kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S5
  - OPEN  : S4, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 10  (t = 10 h)

**Events**
  - RC2 arrived at N9 (t=10, total=22.0km)
  - MPS1 standing by at N8 — awaiting section clearance

### State after step 10

- Loads ON: **10/11**  ·  Reward: **9800** / 11800

**Faults**
  - **DP1** at `N3–N10` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP2** at `N11` (node)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N8–N9` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 3/4)

**Repair Crews**
  - **RC1** @ `N9`  ·  speed 4km/h  ·  resources 12.0  ·  repairing on `DP3`
  - **RC2** @ `N9`  ·  speed 5km/h  ·  resources 6.0  ·  moving → `V4` (6.0km left)

**Scouts**
  - **Scout1** @ `S7`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N8`  ·  speed 8km/h  ·  limit 600kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S5
  - OPEN  : S4, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 11  (t = 11 h)

**Events**
  - RC1 repaired DP3 at t=11

### State after step 11

- Loads ON: **11/11**  ·  Reward: **11800** / 11800

**Faults**
  - **DP1** at `N3–N10` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP2** at `N11` (node)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N8–N9` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N9`  ·  speed 4km/h  ·  resources 11.0  ·  idle
  - **RC2** @ `N9`  ·  speed 5km/h  ·  resources 6.0  ·  moving → `V4` (1.0km left)

**Scouts**
  - **Scout1** @ `S7`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N8`  ·  speed 8km/h  ·  limit 600kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4, S5
  - OPEN  : S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


**All faults repaired at step 11.**

---

## Case2

**Scenario:** 3 hidden faults  ·  2 RC  ·  1 MPS  ·  1 Scout

### Initial State  (t = 0 h)

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N2`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `S3` (0.0km left)
  - **RC2** @ `N9`  ·  speed 5km/h  ·  resources 15.0  ·  moving → `N8` (4.0km left)

**Scouts**
  - **Scout1** @ `N2`  ·  speed 10.0km/h  ·  moving → `S2` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N11`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S2, S4
  - OPEN  : S1, S3, S5, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 1  (t = 1 h)

**Events**
  - RC1 arrived at S3 (t=1, total=0.0km)
  - RC2 arrived at N8 (t=1, total=4.0km)
  - Scout Scout1 arrived at S2
  - MPS1 standing by at N11 — awaiting section clearance

### State after step 1

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `S3`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `S6` (2.0km left)
  - **RC2** @ `N8`  ·  speed 5km/h  ·  resources 15.0  ·  moving → `S4` (2.0km left)

**Scouts**
  - **Scout1** @ `S2`  ·  speed 10.0km/h  ·  moving → `S1` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N11`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S2, S4
  - OPEN  : S1, S3, S5, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 2  (t = 2 h)

**Events**
  - RC1 arrived at S6 (t=2, total=2.0km)
  - RC2 arrived at S4 (t=2, total=6.0km)
  - Scout Scout1 arrived at S1
  - MPS1 standing by at N11 — awaiting section clearance

### State after step 2

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `S6`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `V1` (6.0km left)
  - **RC2** @ `S4`  ·  speed 5km/h  ·  resources 15.0  ·  moving → `N3` (0.0km left)

**Scouts**
  - **Scout1** @ `S1`  ·  speed 10.0km/h  ·  moving → `N6` (6.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N11`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S2, S4
  - OPEN  : S1, S3, S5, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 3  (t = 3 h)

**Events**
  - RC2 arrived at N3 (t=3, total=6.0km)
  - Scout Scout1 arrived at N6
  - *** Scout Scout1 DISCOVERED DP3 at N6 (t=3h) ***
  - MPS1 standing by at N11 — awaiting section clearance
  - RC1 redirected to fault DP3

### State after step 3

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  DISCOVERED  (progress 0/3)

**Repair Crews**
  - **RC1** @ `S6`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `N6` (6.0km left)
  - **RC2** @ `N3`  ·  speed 5km/h  ·  resources 15.0  ·  moving → `N10` (2.0km left)

**Scouts**
  - **Scout1** @ `N6`  ·  speed 10.0km/h  ·  moving → `N7` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N11`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S2, S4
  - OPEN  : S1, S3, S5, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 4  (t = 4 h)

**Events**
  - RC2 arrived at N10 (t=4, total=8.0km)
  - *** RC RC2 DISCOVERED DP1 at N10 (t=4h) ***
  - Scout Scout1 arrived at N7
  - MPS1 standing by at N11 — awaiting section clearance
  - RC2 traversing fault edge to N12

### State after step 4

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  DISCOVERED  (progress 0/3)

**Repair Crews**
  - **RC1** @ `S6`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `N6` (2.0km left)
  - **RC2** @ `N10`  ·  speed 5km/h  ·  resources 15.0  ·  moving → `N12` (2.0km left)

**Scouts**
  - **Scout1** @ `N7`  ·  speed 10.0km/h  ·  moving → `V1` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N11`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S2, S4
  - OPEN  : S1, S3, S5, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 5  (t = 5 h)

**Events**
  - RC1 arrived at N6 (t=5, total=12.0km)
  - RC2 arrived at N12 (t=5, total=10.0km)
  - Scout Scout1 arrived at V1
  - MPS1 standing by at N11 — awaiting section clearance
  - RC1 traversing fault edge to N7
  - RC2 auto-started repair of DP1

### State after step 5

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  DISCOVERED  (progress 0/3)

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 4km/h  ·  resources 15.0  ·  moving → `N7` (2.0km left)
  - **RC2** @ `N12`  ·  speed 5km/h  ·  resources 15.0  ·  repairing on `DP1`

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  moving → `V2` (6.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N11`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S2, S4
  - OPEN  : S1, S3, S5, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 6  (t = 6 h)

**Events**
  - RC1 arrived at N7 (t=6, total=14.0km)
  - Scout Scout1 arrived at V2
  - MPS1 standing by at N11 — awaiting section clearance
  - RC1 auto-started repair of DP3

### State after step 6

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 3/5)
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  DISCOVERED  (progress 0/3)

**Repair Crews**
  - **RC1** @ `N7`  ·  speed 4km/h  ·  resources 15.0  ·  repairing on `DP3`
  - **RC2** @ `N12`  ·  speed 5km/h  ·  resources 12.0  ·  repairing on `DP1`

**Scouts**
  - **Scout1** @ `V2`  ·  speed 10.0km/h  ·  moving → `V3` (4.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N11`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S2, S4
  - OPEN  : S1, S3, S5, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 7  (t = 7 h)

**Events**
  - RC1 repaired DP3 at t=7
  - RC2 repaired DP1 at t=7
  - Scout Scout1 arrived at V3
  - MPS1 moving to N13 (restores 1 loads)

### State after step 7

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N7`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `S8` (12.0km left)
  - **RC2** @ `N12`  ·  speed 5km/h  ·  resources 10.0  ·  moving → `S5` (12.0km left)

**Scouts**
  - **Scout1** @ `V3`  ·  speed 10.0km/h  ·  moving → `N13` (6.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N11`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  moving → `N13` (14.0km left)

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 8  (t = 8 h)

**Events**
  - Scout Scout1 arrived at N13
  - *** Scout Scout1 DISCOVERED DP2 at N13 (t=8h) ***
  - RC1 redirected to fault DP2

### State after step 8

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N7`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N13` (18.0km left)
  - **RC2** @ `N12`  ·  speed 5km/h  ·  resources 10.0  ·  moving → `S5` (7.0km left)

**Scouts**
  - **Scout1** @ `N13`  ·  speed 10.0km/h  ·  moving → `S7` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N11`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  moving → `N13` (6.0km left)

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 9  (t = 9 h)

**Events**
  - Scout Scout1 arrived at S7
  - MPS1 arrived at N13
  - MPS1 standing by at N13 — awaiting section clearance
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 9

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N7`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N13` (14.0km left)
  - **RC2** @ `N12`  ·  speed 5km/h  ·  resources 10.0  ·  moving → `S5` (2.0km left)

**Scouts**
  - **Scout1** @ `S7`  ·  speed 10.0km/h  ·  moving → `V4` (5.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 10  (t = 10 h)

**Events**
  - RC2 arrived at S5 (t=10, total=22.0km)
  - Scout Scout1 arrived at V4
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 10

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N7`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N13` (10.0km left)
  - **RC2** @ `S5`  ·  speed 5km/h  ·  resources 10.0  ·  idle

**Scouts**
  - **Scout1** @ `V4`  ·  speed 10.0km/h  ·  moving → `S8` (12.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 11  (t = 11 h)

**Events**
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 11

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N7`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N13` (6.0km left)
  - **RC2** @ `S5`  ·  speed 5km/h  ·  resources 10.0  ·  idle

**Scouts**
  - **Scout1** @ `V4`  ·  speed 10.0km/h  ·  moving → `S8` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 12  (t = 12 h)

**Events**
  - Scout Scout1 arrived at S8
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 12

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N7`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N13` (2.0km left)
  - **RC2** @ `S5`  ·  speed 5km/h  ·  resources 10.0  ·  idle

**Scouts**
  - **Scout1** @ `S8`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 13  (t = 13 h)

**Events**
  - RC1 arrived at N13 (t=13, total=36.0km)
  - MPS1 standing by at N13 — awaiting section clearance
  - RC1 auto-started repair of DP2

### State after step 13

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N13`  ·  speed 4km/h  ·  resources 12.0  ·  repairing on `DP2`
  - **RC2** @ `S5`  ·  speed 5km/h  ·  resources 10.0  ·  idle

**Scouts**
  - **Scout1** @ `S8`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 14  (t = 14 h)

**Events**
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 14

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 3/6)
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N13`  ·  speed 4km/h  ·  resources 9.0  ·  repairing on `DP2`
  - **RC2** @ `S5`  ·  speed 5km/h  ·  resources 10.0  ·  idle

**Scouts**
  - **Scout1** @ `S8`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 15  (t = 15 h)

**Events**
  - RC1 repaired DP2 at t=15

### State after step 15

- Loads ON: **11/11**  ·  Reward: **11800** / 11800

**Faults**
  - **DP1** at `N10–N12` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  REPAIRED
  - **DP3** at `N6–N7` (edge)  ·  level 3  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N13`  ·  speed 4km/h  ·  resources 6.0  ·  idle
  - **RC2** @ `S5`  ·  speed 5km/h  ·  resources 10.0  ·  idle

**Scouts**
  - **Scout1** @ `S8`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 8km/h  ·  limit 600kW  ·  energy 4000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4, S5
  - OPEN  : S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


**All faults repaired at step 15.**

---

## Case3

**Scenario:** 3 hidden faults  ·  2 RC  ·  1 MPS  ·  1 Scout

### Initial State  (t = 0 h)

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  HIDDEN
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N1`  ·  speed 5km/h  ·  resources 12.0  ·  moving → `S6` (0.0km left)
  - **RC2** @ `V2`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N12` (2.0km left)

**Scouts**
  - **Scout1** @ `N1`  ·  speed 10.0km/h  ·  moving → `S1` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N2`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S3, S4, S5
  - OPEN  : S1, S2, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 1  (t = 1 h)

**Events**
  - RC1 arrived at S6 (t=1, total=0.0km)
  - RC2 arrived at N12 (t=1, total=2.0km)
  - Scout Scout1 arrived at S1
  - MPS1 standing by at N2 — awaiting section clearance

### State after step 1

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  HIDDEN
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `S6`  ·  speed 5km/h  ·  resources 12.0  ·  moving → `S2` (2.0km left)
  - **RC2** @ `N12`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N10` (2.0km left)

**Scouts**
  - **Scout1** @ `S1`  ·  speed 10.0km/h  ·  moving → `N2` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N2`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S3, S4, S5
  - OPEN  : S1, S2, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 2  (t = 2 h)

**Events**
  - RC1 arrived at S2 (t=2, total=2.0km)
  - RC2 arrived at N10 (t=2, total=4.0km)
  - Scout Scout1 arrived at N2
  - *** Scout Scout1 DISCOVERED DP3 at N2 (t=2h) ***
  - MPS1 standing by at N2 — awaiting section clearance
  - RC1 moving to discovered fault DP3

### State after step 2

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  HIDDEN
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)

**Repair Crews**
  - **RC1** @ `S2`  ·  speed 5km/h  ·  resources 12.0  ·  moving → `N2` (0.0km left)
  - **RC2** @ `N10`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N3` (2.0km left)

**Scouts**
  - **Scout1** @ `N2`  ·  speed 10.0km/h  ·  moving → `S3` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N2`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S3, S4, S5
  - OPEN  : S1, S2, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 3  (t = 3 h)

**Events**
  - RC1 arrived at N2 (t=3, total=2.0km)
  - RC2 arrived at N3 (t=3, total=6.0km)
  - Scout Scout1 arrived at S3
  - MPS1 standing by at N2 — awaiting section clearance
  - RC1 traversing fault edge to N6

### State after step 3

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  HIDDEN
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)

**Repair Crews**
  - **RC1** @ `N2`  ·  speed 5km/h  ·  resources 12.0  ·  moving → `N6` (4.0km left)
  - **RC2** @ `N3`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `S4` (0.0km left)

**Scouts**
  - **Scout1** @ `S3`  ·  speed 10.0km/h  ·  moving → `N6` (4.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N2`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S3, S4, S5
  - OPEN  : S1, S2, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 4  (t = 4 h)

**Events**
  - RC1 arrived at N6 (t=4, total=6.0km)
  - *** RC RC1 DISCOVERED DP2 at N6 (t=4h) ***
  - RC2 arrived at S4 (t=4, total=6.0km)
  - Scout Scout1 arrived at N6
  - MPS1 standing by at N2 — awaiting section clearance
  - RC1 auto-started repair of DP3
  - RC2 moving to discovered fault DP2

### State after step 4

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 5km/h  ·  resources 12.0  ·  repairing on `DP3`
  - **RC2** @ `S4`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N6` (12.0km left)

**Scouts**
  - **Scout1** @ `N6`  ·  speed 10.0km/h  ·  moving → `N7` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N2`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S3, S4, S5
  - OPEN  : S1, S2, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 5  (t = 5 h)

**Events**
  - RC1 repaired DP3 at t=5
  - Scout Scout1 arrived at N7
  - MPS1 standing by at N2 — awaiting section clearance
  - RC1 traversing fault edge to N7

### State after step 5

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 5km/h  ·  resources 8.0  ·  moving → `N7` (2.0km left)
  - **RC2** @ `S4`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N6` (8.0km left)

**Scouts**
  - **Scout1** @ `N7`  ·  speed 10.0km/h  ·  moving → `V1` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N2`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S3, S4, S5
  - OPEN  : S1, S2, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 6  (t = 6 h)

**Events**
  - RC1 arrived at N7 (t=6, total=8.0km)
  - Scout Scout1 arrived at V1
  - MPS1 standing by at N2 — awaiting section clearance
  - RC1 auto-started repair of DP2

### State after step 6

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  DISCOVERED  (progress 0/4)
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N7`  ·  speed 5km/h  ·  resources 8.0  ·  repairing on `DP2`
  - **RC2** @ `S4`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N6` (4.0km left)

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  moving → `V3` (10.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N2`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S3, S4, S5
  - OPEN  : S1, S2, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 7  (t = 7 h)

**Events**
  - RC1 repaired DP2 at t=7
  - Scout Scout1 arrived at V3
  - MPS1 moving to N5 (restores 1 loads)

### State after step 7

- Loads ON: **9/11**  ·  Reward: **9050** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N7`  ·  speed 5km/h  ·  resources 4.0  ·  moving → `N4` (10.0km left)
  - **RC2** @ `S4`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N6` (0.0km left)

**Scouts**
  - **Scout1** @ `V3`  ·  speed 10.0km/h  ·  moving → `S7` (6.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N2`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  moving → `N5` (6.0km left)

**Switches / Breakers**
  - CLOSED: S1, S3, S4, S5
  - OPEN  : S2, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 8  (t = 8 h)

**Events**
  - RC2 arrived at N6 (t=8, total=18.0km)
  - Scout Scout1 arrived at S7
  - MPS1 arrived at N5
  - MPS1 standing by at N5 — awaiting section clearance
  - MPS1 standing by at N5 — awaiting section clearance

### State after step 8

- Loads ON: **9/11**  ·  Reward: **9050** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N7`  ·  speed 5km/h  ·  resources 4.0  ·  moving → `N4` (5.0km left)
  - **RC2** @ `N6`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N5` (10.0km left)

**Scouts**
  - **Scout1** @ `S7`  ·  speed 10.0km/h  ·  moving → `V4` (5.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N5`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4, S5
  - OPEN  : S2, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 9  (t = 9 h)

**Events**
  - Scout Scout1 arrived at V4
  - MPS1 standing by at N5 — awaiting section clearance

### State after step 9

- Loads ON: **9/11**  ·  Reward: **9050** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N7`  ·  speed 5km/h  ·  resources 4.0  ·  moving → `N4` (0.0km left)
  - **RC2** @ `N6`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N5` (6.0km left)

**Scouts**
  - **Scout1** @ `V4`  ·  speed 10.0km/h  ·  moving → `S8` (12.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N5`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4, S5
  - OPEN  : S2, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 10  (t = 10 h)

**Events**
  - RC1 arrived at N4 (t=10, total=18.0km)
  - *** RC RC1 DISCOVERED DP1 at N4 (t=10h) ***
  - MPS1 standing by at N5 — awaiting section clearance
  - RC2 redirected to fault DP1
  - RC1 traversing fault edge to N5

### State after step 10

- Loads ON: **9/11**  ·  Reward: **9050** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N4`  ·  speed 5km/h  ·  resources 4.0  ·  moving → `N5` (2.0km left)
  - **RC2** @ `N6`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N4` (8.0km left)

**Scouts**
  - **Scout1** @ `V4`  ·  speed 10.0km/h  ·  moving → `S8` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N5`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4, S5
  - OPEN  : S2, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 11  (t = 11 h)

**Events**
  - RC1 arrived at N5 (t=11, total=20.0km)
  - Scout Scout1 arrived at S8
  - MPS1 standing by at N5 — awaiting section clearance
  - RC1 auto-started repair of DP1

### State after step 11

- Loads ON: **9/11**  ·  Reward: **9050** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 5km/h  ·  resources 4.0  ·  repairing on `DP1`
  - **RC2** @ `N6`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N4` (4.0km left)

**Scouts**
  - **Scout1** @ `S8`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N5`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4, S5
  - OPEN  : S2, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 12  (t = 12 h)

**Events**
  - RC1 out of resources at t=12
  - MPS1 standing by at N5 — awaiting section clearance

### State after step 12

- Loads ON: **9/11**  ·  Reward: **9050** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 4/5)
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 5km/h  ·  resources 0.0  ·  idle
  - **RC2** @ `N6`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N4` (0.0km left)

**Scouts**
  - **Scout1** @ `S8`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N5`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4, S5
  - OPEN  : S2, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 13  (t = 13 h)

**Events**
  - RC2 arrived at N4 (t=13, total=34.0km)
  - MPS1 standing by at N5 — awaiting section clearance
  - RC2 traversing fault edge to N5

### State after step 13

- Loads ON: **9/11**  ·  Reward: **9050** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 4/5)
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 5km/h  ·  resources 0.0  ·  idle
  - **RC2** @ `N4`  ·  speed 4km/h  ·  resources 12.0  ·  moving → `N5` (2.0km left)

**Scouts**
  - **Scout1** @ `S8`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N5`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4, S5
  - OPEN  : S2, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 14  (t = 14 h)

**Events**
  - RC2 arrived at N5 (t=14, total=36.0km)
  - MPS1 standing by at N5 — awaiting section clearance
  - RC2 auto-started repair of DP1

### State after step 14

- Loads ON: **9/11**  ·  Reward: **9050** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 4/5)
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 5km/h  ·  resources 0.0  ·  idle
  - **RC2** @ `N5`  ·  speed 4km/h  ·  resources 12.0  ·  repairing on `DP1`

**Scouts**
  - **Scout1** @ `S8`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N5`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4, S5
  - OPEN  : S2, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 15  (t = 15 h)

**Events**
  - RC2 repaired DP1 at t=15

### State after step 15

- Loads ON: **11/11**  ·  Reward: **11800** / 11800

**Faults**
  - **DP1** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP2** at `N6–N7` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED
  - **DP3** at `N2–N6` (edge)  ·  level 4  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 5km/h  ·  resources 0.0  ·  idle
  - **RC2** @ `N5`  ·  speed 4km/h  ·  resources 11.0  ·  idle

**Scouts**
  - **Scout1** @ `S8`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N5`  ·  speed 8km/h  ·  limit 400kW  ·  energy 3000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4, S5
  - OPEN  : S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


**All faults repaired at step 15.**

---

## Case4

**Scenario:** 3 hidden faults  ·  2 RC  ·  1 MPS  ·  1 Scout

### Initial State  (t = 0 h)

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  HIDDEN
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N4`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N8` (6.0km left)
  - **RC2** @ `N8`  ·  speed 2km/h  ·  resources 13.0  ·  moving → `S4` (2.0km left)

**Scouts**
  - **Scout1** @ `N4`  ·  speed 10.0km/h  ·  moving → `N5` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `V3`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  moving → `N7` (12.0km left)

**Switches / Breakers**
  - CLOSED: S2, S5
  - OPEN  : S1, S3, S4, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 1  (t = 1 h)

**Events**
  - RC2 arrived at S4 (t=1, total=2.0km)
  - Scout Scout1 arrived at N5

### State after step 1

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  HIDDEN
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N4`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N8` (3.0km left)
  - **RC2** @ `S4`  ·  speed 2km/h  ·  resources 13.0  ·  moving → `N3` (0.0km left)

**Scouts**
  - **Scout1** @ `N5`  ·  speed 10.0km/h  ·  moving → `S8` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `V3`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  moving → `N7` (6.0km left)

**Switches / Breakers**
  - CLOSED: S2, S5
  - OPEN  : S1, S3, S4, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 2  (t = 2 h)

**Events**
  - RC1 arrived at N8 (t=2, total=6.0km)
  - RC2 arrived at N3 (t=2, total=2.0km)
  - Scout Scout1 arrived at S8
  - MPS1 arrived at N7
  - MPS1 standing by at N7 — awaiting section clearance
  - MPS1 standing by at N7 — awaiting section clearance
  - RC1 traversing fault edge to N9

### State after step 2

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  HIDDEN
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N8`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N9` (4.0km left)
  - **RC2** @ `N3`  ·  speed 2km/h  ·  resources 13.0  ·  moving → `N10` (2.0km left)

**Scouts**
  - **Scout1** @ `S8`  ·  speed 10.0km/h  ·  moving → `N9` (6.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N7`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S2, S5
  - OPEN  : S1, S3, S4, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 3  (t = 3 h)

**Events**
  - RC2 arrived at N10 (t=3, total=4.0km)
  - *** RC RC2 DISCOVERED DP3 at N10 (t=3h) ***
  - Scout Scout1 arrived at N9
  - MPS1 standing by at N7 — awaiting section clearance
  - RC2 auto-started repair of DP3

### State after step 3

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  HIDDEN
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)

**Repair Crews**
  - **RC1** @ `N8`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N9` (1.0km left)
  - **RC2** @ `N10`  ·  speed 2km/h  ·  resources 13.0  ·  repairing on `DP3`

**Scouts**
  - **Scout1** @ `N9`  ·  speed 10.0km/h  ·  moving → `V4` (6.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N7`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S2, S5
  - OPEN  : S1, S3, S4, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 4  (t = 4 h)

**Events**
  - RC1 arrived at N9 (t=4, total=10.0km)
  - Scout Scout1 arrived at V4
  - MPS1 standing by at N7 — awaiting section clearance
  - RC1 auto-started repair of DP2

### State after step 4

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  HIDDEN
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 3/5)

**Repair Crews**
  - **RC1** @ `N9`  ·  speed 3km/h  ·  resources 15.0  ·  repairing on `DP2`
  - **RC2** @ `N10`  ·  speed 2km/h  ·  resources 10.0  ·  repairing on `DP3`

**Scouts**
  - **Scout1** @ `V4`  ·  speed 10.0km/h  ·  moving → `S7` (5.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N7`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S2, S5
  - OPEN  : S1, S3, S4, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 5  (t = 5 h)

**Events**
  - RC2 repaired DP3 at t=5
  - Scout Scout1 arrived at S7
  - MPS1 moving to V1 (restores 5 loads)

### State after step 5

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  HIDDEN
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 4/5)
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N9`  ·  speed 3km/h  ·  resources 11.0  ·  repairing on `DP2`
  - **RC2** @ `N10`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N12` (2.0km left)

**Scouts**
  - **Scout1** @ `S7`  ·  speed 10.0km/h  ·  moving → `N13` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N7`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  moving → `V1` (2.0km left)

**Switches / Breakers**
  - CLOSED: S2, S3, S5
  - OPEN  : S1, S4, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 6  (t = 6 h)

**Events**
  - RC1 repaired DP2 at t=6
  - RC2 arrived at N12 (t=6, total=6.0km)
  - Scout Scout1 arrived at N13
  - MPS1 arrived at V1
  - MPS1 standing by at V1 — awaiting section clearance
  - MPS1 standing by at V1 — awaiting section clearance

### State after step 6

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  HIDDEN
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N9`  ·  speed 3km/h  ·  resources 10.0  ·  moving → `N11` (12.0km left)
  - **RC2** @ `N12`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `V2` (2.0km left)

**Scouts**
  - **Scout1** @ `N13`  ·  speed 10.0km/h  ·  moving → `S5` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `V1`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S2, S3, S4, S5
  - OPEN  : S1, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 7  (t = 7 h)

**Events**
  - RC2 arrived at V2 (t=7, total=8.0km)
  - Scout Scout1 arrived at S5
  - MPS1 standing by at V1 — awaiting section clearance

### State after step 7

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  HIDDEN
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N9`  ·  speed 3km/h  ·  resources 10.0  ·  moving → `N11` (9.0km left)
  - **RC2** @ `V2`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `V1` (6.0km left)

**Scouts**
  - **Scout1** @ `S5`  ·  speed 10.0km/h  ·  moving → `V3` (6.0km left)

**Mobile Power Sources**
  - **MPS1** @ `V1`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S2, S3, S4, S5
  - OPEN  : S1, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 8  (t = 8 h)

**Events**
  - Scout Scout1 arrived at V3
  - MPS1 standing by at V1 — awaiting section clearance

### State after step 8

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  HIDDEN
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N9`  ·  speed 3km/h  ·  resources 10.0  ·  moving → `N11` (6.0km left)
  - **RC2** @ `V2`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `V1` (4.0km left)

**Scouts**
  - **Scout1** @ `V3`  ·  speed 10.0km/h  ·  moving → `N7` (12.0km left)

**Mobile Power Sources**
  - **MPS1** @ `V1`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S2, S3, S4, S5
  - OPEN  : S1, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 9  (t = 9 h)

**Events**
  - MPS1 standing by at V1 — awaiting section clearance

### State after step 9

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  HIDDEN
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N9`  ·  speed 3km/h  ·  resources 10.0  ·  moving → `N11` (3.0km left)
  - **RC2** @ `V2`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `V1` (2.0km left)

**Scouts**
  - **Scout1** @ `V3`  ·  speed 10.0km/h  ·  moving → `N7` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `V1`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S2, S3, S4, S5
  - OPEN  : S1, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 10  (t = 10 h)

**Events**
  - RC2 arrived at V1 (t=10, total=14.0km)
  - Scout Scout1 arrived at N7
  - MPS1 connected at V1 — section cleared

### State after step 10

- Loads ON: **9/11**  ·  Reward: **11560** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  HIDDEN
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N9`  ·  speed 3km/h  ·  resources 10.0  ·  moving → `N11` (0.0km left)
  - **RC2** @ `V1`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `S6` (6.0km left)

**Scouts**
  - **Scout1** @ `N7`  ·  speed 10.0km/h  ·  moving → `N6` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `V1`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  connected (feeding power)

**Switches / Breakers**
  - CLOSED: S2, S3, S4, S5
  - OPEN  : S1, S6, S7, S8

**Sections**
  - Section Area1: ⚠ **PARTIAL** — dark nodes: `N6, N7`
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 11  (t = 11 h)

**Events**
  - RC1 arrived at N11 (t=11, total=22.0km)
  - Scout Scout1 arrived at N6
  - *** Scout Scout1 DISCOVERED DP1 at N6 (t=11h) ***
  - RC2 redirected to fault DP1
  - RC1 moving to discovered fault DP1

### State after step 11

- Loads ON: **9/11**  ·  Reward: **11560** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  DISCOVERED  (progress 0/10)
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N11`  ·  speed 3km/h  ·  resources 10.0  ·  moving → `N2` (14.0km left)
  - **RC2** @ `V1`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N2` (8.0km left)

**Scouts**
  - **Scout1** @ `N6`  ·  speed 10.0km/h  ·  moving → `N2` (4.0km left)

**Mobile Power Sources**
  - **MPS1** @ `V1`  ·  speed 6km/h  ·  limit 450kW  ·  energy 4550kWh  ·  connected (feeding power)

**Switches / Breakers**
  - CLOSED: S2, S3, S4, S5
  - OPEN  : S1, S6, S7, S8

**Sections**
  - Section Area1: ⚠ **PARTIAL** — dark nodes: `N6, N7`
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 12  (t = 12 h)

**Events**
  - Scout Scout1 arrived at N2

### State after step 12

- Loads ON: **9/11**  ·  Reward: **11560** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  DISCOVERED  (progress 0/10)
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N11`  ·  speed 3km/h  ·  resources 10.0  ·  moving → `N2` (11.0km left)
  - **RC2** @ `V1`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N2` (6.0km left)

**Scouts**
  - **Scout1** @ `N2`  ·  speed 10.0km/h  ·  moving → `S2` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `V1`  ·  speed 6km/h  ·  limit 450kW  ·  energy 4100kWh  ·  connected (feeding power)

**Switches / Breakers**
  - CLOSED: S2, S3, S4, S5
  - OPEN  : S1, S6, S7, S8

**Sections**
  - Section Area1: ⚠ **PARTIAL** — dark nodes: `N6, N7`
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 13  (t = 13 h)

**Events**
  - Scout Scout1 arrived at S2

### State after step 13

- Loads ON: **9/11**  ·  Reward: **11560** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  DISCOVERED  (progress 0/10)
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N11`  ·  speed 3km/h  ·  resources 10.0  ·  moving → `N2` (8.0km left)
  - **RC2** @ `V1`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N2` (4.0km left)

**Scouts**
  - **Scout1** @ `S2`  ·  speed 10.0km/h  ·  moving → `S3` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `V1`  ·  speed 6km/h  ·  limit 450kW  ·  energy 3650kWh  ·  connected (feeding power)

**Switches / Breakers**
  - CLOSED: S2, S3, S4, S5
  - OPEN  : S1, S6, S7, S8

**Sections**
  - Section Area1: ⚠ **PARTIAL** — dark nodes: `N6, N7`
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 14  (t = 14 h)

**Events**
  - Scout Scout1 arrived at S3

### State after step 14

- Loads ON: **9/11**  ·  Reward: **11560** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  DISCOVERED  (progress 0/10)
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N11`  ·  speed 3km/h  ·  resources 10.0  ·  moving → `N2` (5.0km left)
  - **RC2** @ `V1`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N2` (2.0km left)

**Scouts**
  - **Scout1** @ `S3`  ·  speed 10.0km/h  ·  moving → `S1` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `V1`  ·  speed 6km/h  ·  limit 450kW  ·  energy 3200kWh  ·  connected (feeding power)

**Switches / Breakers**
  - CLOSED: S2, S3, S4, S5
  - OPEN  : S1, S6, S7, S8

**Sections**
  - Section Area1: ⚠ **PARTIAL** — dark nodes: `N6, N7`
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 15  (t = 15 h)

**Events**
  - RC2 arrived at N2 (t=15, total=24.0km)
  - Scout Scout1 arrived at S1
  - RC2 traversing fault edge to N6

### State after step 15

- Loads ON: **9/11**  ·  Reward: **11560** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  DISCOVERED  (progress 0/10)
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N11`  ·  speed 3km/h  ·  resources 10.0  ·  moving → `N2` (2.0km left)
  - **RC2** @ `N2`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N6` (4.0km left)

**Scouts**
  - **Scout1** @ `S1`  ·  speed 10.0km/h  ·  moving → `S6` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `V1`  ·  speed 6km/h  ·  limit 450kW  ·  energy 2750kWh  ·  connected (feeding power)

**Switches / Breakers**
  - CLOSED: S2, S3, S4, S5
  - OPEN  : S1, S6, S7, S8

**Sections**
  - Section Area1: ⚠ **PARTIAL** — dark nodes: `N6, N7`
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 16  (t = 16 h)

**Events**
  - RC1 arrived at N2 (t=16, total=36.0km)
  - Scout Scout1 arrived at S6
  - RC1 traversing fault edge to N6

### State after step 16

- Loads ON: **9/11**  ·  Reward: **11560** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  DISCOVERED  (progress 0/10)
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N2`  ·  speed 3km/h  ·  resources 10.0  ·  moving → `N6` (4.0km left)
  - **RC2** @ `N2`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N6` (2.0km left)

**Scouts**
  - **Scout1** @ `S6`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `V1`  ·  speed 6km/h  ·  limit 450kW  ·  energy 2300kWh  ·  connected (feeding power)

**Switches / Breakers**
  - CLOSED: S2, S3, S4, S5
  - OPEN  : S1, S6, S7, S8

**Sections**
  - Section Area1: ⚠ **PARTIAL** — dark nodes: `N6, N7`
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 17  (t = 17 h)

**Events**
  - RC2 arrived at N6 (t=17, total=28.0km)
  - RC2 auto-started repair of DP1

### State after step 17

- Loads ON: **9/11**  ·  Reward: **11560** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  DISCOVERED  (progress 0/10)
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N2`  ·  speed 3km/h  ·  resources 10.0  ·  moving → `N6` (1.0km left)
  - **RC2** @ `N6`  ·  speed 2km/h  ·  resources 8.0  ·  repairing on `DP1`

**Scouts**
  - **Scout1** @ `S6`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `V1`  ·  speed 6km/h  ·  limit 450kW  ·  energy 1850kWh  ·  connected (feeding power)

**Switches / Breakers**
  - CLOSED: S2, S3, S4, S5
  - OPEN  : S1, S6, S7, S8

**Sections**
  - Section Area1: ⚠ **PARTIAL** — dark nodes: `N6, N7`
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 18  (t = 18 h)

**Events**
  - RC1 arrived at N6 (t=18, total=40.0km)
  - RC1 auto-started repair of DP1

### State after step 18

- Loads ON: **9/11**  ·  Reward: **11560** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  DISCOVERED  (progress 3/10)
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 3km/h  ·  resources 10.0  ·  repairing on `DP1`
  - **RC2** @ `N6`  ·  speed 2km/h  ·  resources 5.0  ·  repairing on `DP1`

**Scouts**
  - **Scout1** @ `S6`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `V1`  ·  speed 6km/h  ·  limit 450kW  ·  energy 1400kWh  ·  connected (feeding power)

**Switches / Breakers**
  - CLOSED: S2, S3, S4, S5
  - OPEN  : S1, S6, S7, S8

**Sections**
  - Section Area1: ⚠ **PARTIAL** — dark nodes: `N6, N7`
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


#### Step 19  (t = 19 h)

**Events**
  - RC2 repaired DP1 at t=19
  - MPS1 disconnected at V1 (grid restored)

### State after step 19

- Loads ON: **11/11**  ·  Reward: **11800** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N8–N9` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED
  - **DP3** at `N10` (node)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 3km/h  ·  resources 6.0  ·  repairing on `DP1`
  - **RC2** @ `N6`  ·  speed 2km/h  ·  resources 2.0  ·  idle

**Scouts**
  - **Scout1** @ `S6`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `V1`  ·  speed 6km/h  ·  limit 450kW  ·  energy 950kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4, S5
  - OPEN  : S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


**All faults repaired at step 19.**

---

## Case5

**Scenario:** 3 hidden faults  ·  2 RC  ·  1 MPS  ·  1 Scout

### Initial State  (t = 0 h)

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  DISCOVERED  (progress 0/10)
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N8`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N2` (10.0km left)
  - **RC2** @ `N2`  ·  speed 2km/h  ·  resources 18.0  ·  moving → `N6` (4.0km left)

**Scouts**
  - **Scout1** @ `N8`  ·  speed 10.0km/h  ·  moving → `S4` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `V3`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  moving → `N12` (6.0km left)

**Switches / Breakers**
  - CLOSED: S3, S4
  - OPEN  : S1, S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 1  (t = 1 h)

**Events**
  - Scout Scout1 arrived at S4
  - MPS1 arrived at N12
  - MPS1 standing by at N12 — awaiting section clearance
  - MPS1 standing by at N12 — awaiting section clearance

### State after step 1

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  DISCOVERED  (progress 0/10)
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N8`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N2` (7.0km left)
  - **RC2** @ `N2`  ·  speed 2km/h  ·  resources 18.0  ·  moving → `N6` (2.0km left)

**Scouts**
  - **Scout1** @ `S4`  ·  speed 10.0km/h  ·  moving → `N3` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N12`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S3, S4
  - OPEN  : S1, S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 2  (t = 2 h)

**Events**
  - RC2 arrived at N6 (t=2, total=4.0km)
  - Scout Scout1 arrived at N3
  - MPS1 standing by at N12 — awaiting section clearance
  - RC2 auto-started repair of DP1

### State after step 2

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  DISCOVERED  (progress 0/10)
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N8`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N2` (4.0km left)
  - **RC2** @ `N6`  ·  speed 2km/h  ·  resources 18.0  ·  repairing on `DP1`

**Scouts**
  - **Scout1** @ `N3`  ·  speed 10.0km/h  ·  moving → `N10` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N12`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S3, S4
  - OPEN  : S1, S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 3  (t = 3 h)

**Events**
  - Scout Scout1 arrived at N10
  - MPS1 standing by at N12 — awaiting section clearance

### State after step 3

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  DISCOVERED  (progress 3/10)
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N8`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N2` (1.0km left)
  - **RC2** @ `N6`  ·  speed 2km/h  ·  resources 15.0  ·  repairing on `DP1`

**Scouts**
  - **Scout1** @ `N10`  ·  speed 10.0km/h  ·  moving → `N12` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N12`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S3, S4
  - OPEN  : S1, S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 4  (t = 4 h)

**Events**
  - RC1 arrived at N2 (t=4, total=10.0km)
  - Scout Scout1 arrived at N12
  - MPS1 standing by at N12 — awaiting section clearance
  - RC1 traversing fault edge to N6

### State after step 4

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  DISCOVERED  (progress 6/10)
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N2`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N6` (4.0km left)
  - **RC2** @ `N6`  ·  speed 2km/h  ·  resources 12.0  ·  repairing on `DP1`

**Scouts**
  - **Scout1** @ `N12`  ·  speed 10.0km/h  ·  moving → `V2` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N12`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S3, S4
  - OPEN  : S1, S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 5  (t = 5 h)

**Events**
  - Scout Scout1 arrived at V2
  - MPS1 standing by at N12 — awaiting section clearance

### State after step 5

- Loads ON: **0/11**  ·  Reward: **0** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  DISCOVERED  (progress 9/10)
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N2`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N6` (1.0km left)
  - **RC2** @ `N6`  ·  speed 2km/h  ·  resources 9.0  ·  repairing on `DP1`

**Scouts**
  - **Scout1** @ `V2`  ·  speed 10.0km/h  ·  moving → `V3` (4.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N12`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S3, S4
  - OPEN  : S1, S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✗ **DARK** — dark nodes: `N2, N6, N7`
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✗ **DARK** — dark nodes: `N8, N9`
  - Section Area4: ✗ **DARK** — dark nodes: `N10, N11, N12, N3`
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 6  (t = 6 h)

**Events**
  - RC1 arrived at N6 (t=6, total=14.0km)
  - RC2 repaired DP1 at t=6
  - Scout Scout1 arrived at V3
  - MPS1 moving to N13 (restores 1 loads)

### State after step 6

- Loads ON: **7/11**  ·  Reward: **7690** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  HIDDEN
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `V1` (4.0km left)
  - **RC2** @ `N6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `S2` (4.0km left)

**Scouts**
  - **Scout1** @ `V3`  ·  speed 10.0km/h  ·  moving → `N13` (6.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N12`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  moving → `N13` (12.0km left)

**Switches / Breakers**
  - CLOSED: S1, S3, S4
  - OPEN  : S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 7  (t = 7 h)

**Events**
  - Scout Scout1 arrived at N13
  - *** Scout Scout1 DISCOVERED DP2 at N13 (t=7h) ***
  - RC1 redirected to fault DP2

### State after step 7

- Loads ON: **7/11**  ·  Reward: **7690** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N13` (20.0km left)
  - **RC2** @ `N6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `S2` (2.0km left)

**Scouts**
  - **Scout1** @ `N13`  ·  speed 10.0km/h  ·  moving → `S5` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N12`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  moving → `N13` (6.0km left)

**Switches / Breakers**
  - CLOSED: S1, S3, S4
  - OPEN  : S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 8  (t = 8 h)

**Events**
  - Scout Scout1 arrived at S5
  - MPS1 arrived at N13
  - MPS1 standing by at N13 — awaiting section clearance
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 8

- Loads ON: **7/11**  ·  Reward: **7690** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N13` (17.0km left)
  - **RC2** @ `N6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `S2` (0.0km left)

**Scouts**
  - **Scout1** @ `S5`  ·  speed 10.0km/h  ·  moving → `S7` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4
  - OPEN  : S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 9  (t = 9 h)

**Events**
  - RC2 arrived at S2 (t=9, total=8.0km)
  - Scout Scout1 arrived at S7
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 9

- Loads ON: **7/11**  ·  Reward: **7690** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N13` (14.0km left)
  - **RC2** @ `S2`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `S6` (2.0km left)

**Scouts**
  - **Scout1** @ `S7`  ·  speed 10.0km/h  ·  moving → `V4` (5.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4
  - OPEN  : S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 10  (t = 10 h)

**Events**
  - Scout Scout1 arrived at V4
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 10

- Loads ON: **7/11**  ·  Reward: **7690** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N13` (11.0km left)
  - **RC2** @ `S2`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `S6` (0.0km left)

**Scouts**
  - **Scout1** @ `V4`  ·  speed 10.0km/h  ·  moving → `S8` (12.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4
  - OPEN  : S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 11  (t = 11 h)

**Events**
  - RC2 arrived at S6 (t=11, total=10.0km)
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 11

- Loads ON: **7/11**  ·  Reward: **7690** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N13` (8.0km left)
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `V1` (6.0km left)

**Scouts**
  - **Scout1** @ `V4`  ·  speed 10.0km/h  ·  moving → `S8` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4
  - OPEN  : S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 12  (t = 12 h)

**Events**
  - Scout Scout1 arrived at S8
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 12

- Loads ON: **7/11**  ·  Reward: **7690** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  HIDDEN

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N13` (5.0km left)
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `V1` (4.0km left)

**Scouts**
  - **Scout1** @ `S8`  ·  speed 10.0km/h  ·  moving → `N5` (0.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4
  - OPEN  : S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 13  (t = 13 h)

**Events**
  - Scout Scout1 arrived at N5
  - *** Scout Scout1 DISCOVERED DP3 at N5 (t=13h) ***
  - MPS1 standing by at N13 — awaiting section clearance
  - RC1 redirected to fault DP3
  - RC2 redirected to fault DP2

### State after step 13

- Loads ON: **7/11**  ·  Reward: **7690** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N4` (8.0km left)
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N13` (18.0km left)

**Scouts**
  - **Scout1** @ `N5`  ·  speed 10.0km/h  ·  moving → `N4` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4
  - OPEN  : S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 14  (t = 14 h)

**Events**
  - Scout Scout1 arrived at N4
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 14

- Loads ON: **7/11**  ·  Reward: **7690** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N4` (5.0km left)
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N13` (16.0km left)

**Scouts**
  - **Scout1** @ `N4`  ·  speed 10.0km/h  ·  moving → `V1` (12.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4
  - OPEN  : S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 15  (t = 15 h)

**Events**
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 15

- Loads ON: **7/11**  ·  Reward: **7690** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)

**Repair Crews**
  - **RC1** @ `N6`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N4` (2.0km left)
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N13` (14.0km left)

**Scouts**
  - **Scout1** @ `N4`  ·  speed 10.0km/h  ·  moving → `V1` (2.0km left)

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4
  - OPEN  : S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 16  (t = 16 h)

**Events**
  - RC1 arrived at N4 (t=16, total=43.0km)
  - Scout Scout1 arrived at V1
  - MPS1 standing by at N13 — awaiting section clearance
  - RC2 redirected to fault DP3
  - RC1 traversing fault edge to N5

### State after step 16

- Loads ON: **7/11**  ·  Reward: **7690** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)

**Repair Crews**
  - **RC1** @ `N4`  ·  speed 3km/h  ·  resources 15.0  ·  moving → `N5` (2.0km left)
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N4` (6.0km left)

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4
  - OPEN  : S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 17  (t = 17 h)

**Events**
  - RC1 arrived at N5 (t=17, total=45.0km)
  - MPS1 standing by at N13 — awaiting section clearance
  - RC2 redirected to fault DP2
  - RC1 auto-started repair of DP3

### State after step 17

- Loads ON: **7/11**  ·  Reward: **7690** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 0/5)

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 3km/h  ·  resources 15.0  ·  repairing on `DP3`
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N13` (18.0km left)

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4
  - OPEN  : S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 18  (t = 18 h)

**Events**
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 18

- Loads ON: **7/11**  ·  Reward: **7690** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  DISCOVERED  (progress 4/5)

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 3km/h  ·  resources 11.0  ·  repairing on `DP3`
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N13` (16.0km left)

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S3, S4
  - OPEN  : S2, S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✗ **DARK** — dark nodes: `N4, N5`
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 19  (t = 19 h)

**Events**
  - RC1 repaired DP3 at t=19
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 19

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 3km/h  ·  resources 10.0  ·  idle
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N13` (14.0km left)

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 20  (t = 20 h)

**Events**
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 20

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 3km/h  ·  resources 10.0  ·  idle
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N13` (12.0km left)

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 21  (t = 21 h)

**Events**
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 21

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 3km/h  ·  resources 10.0  ·  idle
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N13` (10.0km left)

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 22  (t = 22 h)

**Events**
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 22

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 3km/h  ·  resources 10.0  ·  idle
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N13` (8.0km left)

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 23  (t = 23 h)

**Events**
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 23

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 3km/h  ·  resources 10.0  ·  idle
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N13` (6.0km left)

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 24  (t = 24 h)

**Events**
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 24

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 3km/h  ·  resources 10.0  ·  idle
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N13` (4.0km left)

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 25  (t = 25 h)

**Events**
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 25

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 3km/h  ·  resources 10.0  ·  idle
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N13` (2.0km left)

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 26  (t = 26 h)

**Events**
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 26

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 3km/h  ·  resources 10.0  ·  idle
  - **RC2** @ `S6`  ·  speed 2km/h  ·  resources 8.0  ·  moving → `N13` (0.0km left)

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 27  (t = 27 h)

**Events**
  - RC2 arrived at N13 (t=27, total=40.1km)
  - MPS1 standing by at N13 — awaiting section clearance
  - RC2 auto-started repair of DP2

### State after step 27

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 0/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 3km/h  ·  resources 10.0  ·  idle
  - **RC2** @ `N13`  ·  speed 2km/h  ·  resources 8.0  ·  repairing on `DP2`

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 28  (t = 28 h)

**Events**
  - MPS1 standing by at N13 — awaiting section clearance

### State after step 28

- Loads ON: **9/11**  ·  Reward: **10440** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  DISCOVERED  (progress 3/6)
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 3km/h  ·  resources 10.0  ·  idle
  - **RC2** @ `N13`  ·  speed 2km/h  ·  resources 5.0  ·  repairing on `DP2`

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4
  - OPEN  : S5, S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✗ **DARK** — dark nodes: `N13, V1, V2, V3`


#### Step 29  (t = 29 h)

**Events**
  - RC2 repaired DP2 at t=29

### State after step 29

- Loads ON: **11/11**  ·  Reward: **11800** / 11800

**Faults**
  - **DP1** at `N2–N6` (edge)  ·  level 10  ·  cap 2  ·  REPAIRED
  - **DP2** at `N13` (node)  ·  level 6  ·  cap 1  ·  REPAIRED
  - **DP3** at `N4–N5` (edge)  ·  level 5  ·  cap 1  ·  REPAIRED

**Repair Crews**
  - **RC1** @ `N5`  ·  speed 3km/h  ·  resources 10.0  ·  idle
  - **RC2** @ `N13`  ·  speed 2km/h  ·  resources 2.0  ·  idle

**Scouts**
  - **Scout1** @ `V1`  ·  speed 10.0km/h  ·  idle

**Mobile Power Sources**
  - **MPS1** @ `N13`  ·  speed 6km/h  ·  limit 450kW  ·  energy 5000kWh  ·  idle

**Switches / Breakers**
  - CLOSED: S1, S2, S3, S4, S5
  - OPEN  : S6, S7, S8

**Sections**
  - Section Area1: ✓ **LIVE**
  - Section Area2: ✓ **LIVE**
  - Section Area3: ✓ **LIVE**
  - Section Area4: ✓ **LIVE**
  - Section Area5: ✓ **LIVE**


**All faults repaired at step 29.**
