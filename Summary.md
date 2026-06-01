# DSR Simulation — Agent Journey Summaries
## IEEE-13 New Network · Unknown-Fault Mode

Each case starts with a brief scenario overview, then follows each agent step by step in plain English.

---

## Case 1 — South and East Hit Hard
**Completion: 11 hours**

**Scenario:** Three faults knock out Areas 3, 4, and 5. One fault (DP2 at N11) is already known from the start — a lineman reported it. The other two are hidden. Areas 1 and 2 stay powered. Two repair crews (RC1, RC2), one Scout, and one MPS are deployed.

| Agent | Start | Faults handled |
|-------|-------|----------------|
| RC1   | N2    | DP3 (N8–N9) |
| RC2   | N11   | DP2 (N11), DP1 (N3–N10) |
| Scout1 | N2   | Discovers DP3 |
| MPS1  | N4    | Never connects |

---

### RC1
- Starts at **N2**. Moves toward tie switch S6, arrives at t=1.
- Crosses S6 into Area 5, reaches V1 at t=3.
- At t=3, DP1 is discovered — RC1 is first sent toward N3 (DP1 location).
- At t=4, Scout discovers DP3 at N9 — RC1 gets redirected to DP3 instead.
- Travels from V1 all the way to **N8** (arrives t=8), then pushes on to **N9** (arrives t=9).
- Starts repairing DP3 (edge N8–N9) immediately.
- **Repairs DP3 at t=11.** Full restoration — simulation ends.

### RC2
- Starts at **N11**, right next to the pre-known fault DP2.
- Begins repairing immediately. **Repairs DP2 at t=2.** Area 4 partly restored.
- Moves north to **N10** (arrives t=3). Discovers hidden fault DP1 (edge N3–N10).
- Crosses the fault edge to reach **N3**, starts repairing from that end.
- **Repairs DP1 at t=6.** Area 4 and Area 5 come back online (10/11 loads on).
- Nothing left to do — idles at N3 for the rest of the simulation.

### Scout1
- Starts at **N2**, heads south through S3 and S8.
- Arrives at **N9** at t=3. Discovers hidden fault DP3 (edge N8–N9). Reports to RC1.
- No more dark zones to search — idles at N9 for the remainder.

### MPS1
- Starts at **N4**, moves toward the outage zone targeting N10.
- Arrives N10 at t=2 — but Area 4 is still dark, so it waits for section clearance.
- At t=6, when DP1 is repaired and Area 4 restores, MPS1 moves to N8 to stage for Area 3.
- Arrives N8 at t=7 — but Area 3 (N8, N9, V4) is still dark. Keeps waiting.
- RC1 repairs the fault before MPS1 can connect. **Never connects.** Ends idle at N8.

---

## Case 2 — Total Blackout, Faults in Three Areas
**Completion: 15 hours**

**Scenario:** Full blackout — all 5 areas dark. Three hidden faults are spread across Area 1 (DP3), Area 4 (DP1), and Area 5 (DP2).

| Agent | Start | Faults handled |
|-------|-------|----------------|
| RC1   | N2    | DP3 (N6–N7), DP2 (N13) |
| RC2   | N9    | DP1 (N10–N12) |
| Scout1 | N2   | Discovers DP3, DP2 |
| MPS1  | N11   | Never connects |

---

### RC1
- Starts at **N2**, heads west through S3 → S6 → V1, arriving in Area 5 at t=3.
- Continues into Area 1 via V1 → N6 → **N7** (arrives t=6). Scout already flagged DP3 here.
- Starts repairing DP3 (edge N6–N7). **Repairs DP3 at t=7.** Areas 1, 2, 4 restore (9/11 loads).
- Pivots back east — travels N7 → V1 → V2 → V3 → **N13** (long 18km journey, arrives t=13).
- Scout had already discovered DP2 at N13 at t=8, so RC1 goes straight there.
- Starts repairing DP2 at t=13. **Repairs DP2 at t=15.** Area 5 restores — simulation ends.

### RC2
- Starts at **N9**, heads north: N9 → N8 → through S4 → **N3**.
- Continues east to **N10** (arrives t=4). Discovers hidden fault DP1 (edge N10–N12).
- Crosses fault edge to N12, starts repairing. **Repairs DP1 at t=7.** Area 4 restores.
- Moves to **S5** — nothing more in range. Idles the rest of the simulation.

### Scout1
- Starts at **N2**, heads northwest: S2 → **S1** → **N6** (arrives t=3).
- Discovers DP3 (edge N6–N7) at t=3. Reports to RC1.
- Continues: N6 → N7 → **V1** → **V2** → **V3** → **N13** (arrives t=8).
- Discovers DP2 at **N13** at t=8. Reports to RC1 (who is already heading there).
- All faults found — idles at N13.

### MPS1
- Starts at **N11**, waits while the section is dark (no connectivity to grid).
- Begins moving to **N13** at t=7 (after DP1 and DP3 are repaired, Area 4 is live).
- Arrives N13 at t=9 — but Area 5 (N13, V1, V2, V3) is still dark. Waits for section clearance.
- RC1 eventually repairs DP2 at N13, restoring Area 5 through the grid.
- **Never connects.** Ends idle at N13.

---

## Case 3 — Three Faults, RC1 Burns Out
**Completion: 15 hours**

**Scenario:** Full blackout — three faults in Area 1 (DP2, DP3) and Area 2 (DP1). RC1 handles the first two faults efficiently but runs out of repair resources before finishing DP1. RC2 completes the job. MPS1 successfully connects and powers one load.

| Agent | Start | Faults handled |
|-------|-------|----------------|
| RC1   | N1    | DP3 (N2–N6), DP2 (N6–N7), DP1 partial |
| RC2   | V2    | DP1 (N4–N5) final repair |
| Scout1 | N1   | Discovers DP3, searches Area 3/5 |
| MPS1  | N2    | **Connects at N5 (t=7), powers 1 load** |

---

### RC1
- Starts at **N1**, moves through S6 → S2 → **N2** (arrives t=3).
- Reaches **N6** (t=4) — discovers hidden fault DP2 (edge N6–N7).
- Also: Scout had already flagged DP3 (edge N2–N6) at t=2, so RC1 is already heading for it.
- **Repairs DP3 at t=5.** Immediately starts on DP2 (N6–N7).
- **Repairs DP2 at t=7.** Area 1 restores. Discovers DP1 at N4 (t=10) while moving through.
- Arrives **N5** (t=11), starts repairing DP1 (edge N4–N5, demand 5).
- At **t=12, runs out of resources** — only 4 of 5 units of DP1 done. Stops.
- Idles at N5 for the final 3 hours while RC2 finishes the job.

### RC2
- Starts at **V2**, takes the long road south: V2 → N12 → N10 → N3 → through S4.
- Continues: N3 → N6 (t=8) → **N4** (t=13) → **N5** (t=14).
- Finds DP1 partially repaired by RC1. Picks up from 4/5 progress.
- **Repairs DP1 at t=15.** Area 2 restores — simulation ends.

### Scout1
- Starts at **N1**, goes through S1 to **N2** (t=2). Discovers DP3 (edge N2–N6) at t=2. Reports to RC1.
- Continues east: S3 → N6 → N7 → V1 → V3 → S7 → V4 → S8.
- Thorough sweep of Area 3 and Area 5 tie nodes — no more faults there.
- Idles at S8 after completing the search loop.

### MPS1
- Starts at **N2**, waits while the section is dark.
- Moves to **N5** at t=7 (after Area 1 restores, MPS can reach Area 2).
- **Connects at N5 at t=7** — restores 1 load in Area 2 while DP1 is still being repaired.
- Stays connected at N5 for the rest of the simulation.
- RC2 repairs DP1 at t=15, restoring Area 2 through the grid. MPS1 had bridged the gap for 8 hours.

---

## Case 4 — The Big Fault Needs Two Crews (MPS Saves the Day)
**Completion: 19 hours**

**Scenario:** Full blackout. DP1 (edge N2–N6) has severity level 10 and requires 2 crews simultaneously. DP2 (N8–N9) was pre-discovered at start. RC1 and RC2 handle their individual tasks first, then converge. MPS1 connects and powers 9 loads for 9 hours while the grid is dark.

| Agent | Start | Faults handled |
|-------|-------|----------------|
| RC1   | N4    | DP2 (N8–N9), then DP1 with RC2 |
| RC2   | N8    | DP3 (N10), then DP1 with RC1 |
| Scout1 | N4   | Discovers DP1 |
| MPS1  | V3    | **Connects at V1 (t=10), powers 9 loads** |

---

### RC1
- Starts at **N4**, moves southeast to N8 (t=2) then **N9** (t=4).
- DP2 (edge N8–N9) was pre-discovered — RC1 starts repairing immediately on arrival.
- **Repairs DP2 at t=6.** Area 3 partially restores.
- Long journey north: N9 → **N11** (t=11) → **N2** (t=16) → **N6** (t=18).
- Joins RC2 at N6 to work the level-10 fault DP1 together.
- **DP1 repaired at t=19 (joint effort).** Full restoration — simulation ends.

### RC2
- Starts at **N8**, heads through S4 → N3 → **N10** (arrives t=3).
- Discovers hidden fault DP3 at **N10** (node fault). Begins repairing immediately.
- **Repairs DP3 at t=5.** Area 4 restores.
- Long return journey: N10 → N12 → V2 → V1 → S6 → **N2** (t=15) → **N6** (t=17).
- Works with RC1 on the massive DP1 fault. **DP1 repaired at t=19.**

### Scout1
- Starts at **N4**, sweeps south and east: N5 → S8 → N9 → **V4** (t=4) → S7 → **V3** (t=8) → **N7** (t=10).
- Arrives **N6** at t=11 — discovers hidden fault DP1 (edge N2–N6). Reports to both RCs.
- Both crews were already converging. Scout locks in the target.
- Idles at N6.

### MPS1
- Starts at **V3**, moves to **N7** (arrives t=2). Waits for section clearance — Area 5 is dark.
- Eventually repositions to **V1**. Connects at **t=10**.
- **Powers 9 loads** across the dark area for 9 hours while repairs continue.
- Disconnects at **t=19** when RC1 and RC2 repair DP1 and grid power is restored.

---

## Case 5 — The Hardest Case (29 Hours)
**Completion: 29 hours**

**Scenario:** Full blackout. DP1 (edge N2–N6, level 10) was pre-discovered before the simulation starts. RC2 repairs DP1 alone. Scout makes the longest search across nearly the entire network. MPS1 reaches N13 but never connects.

| Agent | Start | Faults handled |
|-------|-------|----------------|
| RC1   | N8    | DP1 (arrives as RC2 finishes), DP3 (N4–N5) |
| RC2   | N2    | DP1 (N2–N6) alone, then DP2 (N13) |
| Scout1 | N8   | Discovers DP2, DP3 |
| MPS1  | V3    | Never connects |

---

### RC1
- Starts at **N8**, heads northwest to **N2** (arrives t=4) then **N6** (arrives t=6).
- DP1 is already finished by RC2 at t=6 — RC1 arrives just as it's done.
- Redirected: first moves toward N13 (DP2), but at t=13 Scout discovers DP3 at N5, so RC1 is sent there instead.
- Long route: N6 → V1 → ... → **N4** (t=16) → **N5** (t=17). Starts repairing DP3.
- **Repairs DP3 at t=19.** Area 2 restores. Only DP2 remains.

### RC2
- Starts at **N2**, moves directly to **N6** (arrives t=2).
- DP1 was pre-discovered — RC2 starts repairing alone (demand 10, efficiency 3 → ~4 steps).
- **Repairs DP1 solo at t=6.** Area 1 restores.
- Immediately heads east: N6 → S2 (t=9) → S6 (t=11) → into Area 5 via V1 → V2 → V3 → N13.
- A very long journey — arrives **N13** at t=27. Starts repairing DP2.
- **Repairs DP2 at t=29.** Area 5 restores — simulation ends.

### Scout1
- Starts at **N8**, sweeps the outage zone methodically: S4 → N3 → N10 → N12 → V2 → V3 → **N13** (t=7).
- Discovers DP2 at **N13** at t=7. Reports to RC2.
- Continues the loop: S5 → S7 → V4 → S8 → **N5** (t=13).
- Discovers DP3 (edge N4–N5) at **N5** at t=13. Reports to RC1.
- All three faults found. Scout idles at N5 — a complete cross-network search.

### MPS1
- Starts at **V3**, moves to **N12** then repositions to **N13** (arrives around t=6).
- Waits at N13 for section clearance — Area 5 (N13, V1, V2, V3) is dark throughout.
- RC2 takes until t=29 to reach and repair DP2. MPS1 sits idle the entire time.
- **Never connects.** Ends at N13, fully charged but unused.

---

## Quick Reference — All Cases

| Case | Faults | Completion | MPS Status | Key Challenge |
|------|--------|------------|-----------|---------------|
| 1    | 3      | 11 h       | Never connects | Scout finds Area 3 fault, RC1 long reroute |
| 2    | 3      | 15 h       | Never connects | Total blackout, faults spread across 3 areas |
| 3    | 3      | 15 h       | **Connects at N5 (t=7)** | RC1 runs out of resources mid-repair |
| 4    | 3      | 19 h       | **Connects at V1 (t=10), 9 loads, 9h** | DP1 level 10 needs 2 RCs |
| 5    | 3      | 29 h       | Never connects | DP1 pre-discovered, RC2 solo repairs DP1 then long journey to N13 |
