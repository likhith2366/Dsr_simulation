# DSR LLM Agents — handoff notes

Two LLM agents that control the mobile units in the DSR (Distribution System
Restoration) reference simulator, communicating only through a shared
blackboard. Read this file first, then the module docstrings — every file
explains itself at the top.

---

## 1. What this does, in one paragraph

A power grid has 4 faults hidden in 3 unexplored regions. A **scout** agent
drives the patrol unit PAC1 to uncover them. A **controller** agent drives two
repair crews, RC1 and RC2, which also search and then repair. The agents are
separate processes that never call each other; they post facts to
`blackboard.json` and read each other's posts. A local LLM (qwen3:4b via
Ollama) makes the choices that are genuinely open; deterministic code handles
everything else.

**Status:** repair works end to end (4/4 faults repaired from far starting
positions, including one fault that needs both crews). **Score is still 0** —
see section 7.

---

## 2. Prerequisites

| Need | How |
|---|---|
| Python 3.11 with `requests`, plus the simulator's own deps (`fastapi`, `uvicorn`, `plotly`, `numpy`) | `pip install requests fastapi uvicorn plotly numpy` |
| Ollama | https://ollama.com — must be running (`ollama serve`) |
| The model | `ollama pull qwen3:4b` |
| Port 8050 free | the simulator binds it |

A GPU makes each LLM call ~3 s. On CPU expect much slower.

---

## 3. How to run

Two terminals, both in `reference_simulator/agents/`:

```powershell
# terminal 1 — --reset wipes the previous run's board
python scout_agent.py --reset

# terminal 2
python rc_agent.py
```

Whichever agent starts first boots the simulator and loads the scenario; the
other joins. Watch it live at **http://127.0.0.1:8050** (the page
auto-refreshes every 2 s).

Each agent prints every prompt, raw LLM reply, command sent, and blackboard
post, and dumps the whole blackboard when it exits.

**Before a new run:** kill any leftover simulator — it is started detached and
does not exit with the agents:

```powershell
Get-NetTCPConnection -LocalPort 8050 -State Listen | % { Stop-Process -Id $_.OwningProcess -Force }
```

If you skip `--reset`, a leftover `blackboard.json` from a finished run says
`over: true` and both agents exit immediately.

---

## 4. Files

| File | Role |
|---|---|
| `scout_agent.py` | SCOUT process. Drives PAC1. Decides which region to explore. |
| `rc_agent.py` | CONTROLLER process. Drives RC1 + RC2 in one LLM call. Contains the guards on LLM output. |
| `blackboard.py` | Shared file-backed board: lock, posts, round protocol, flush to simulator. |
| `sim_client.py` | All HTTP calls to the simulator + documented simulator quirks. |
| `llm_client.py` | Ollama call + the prefill trick + JSON extraction. |
| `blackboard.json` | *generated* — the board for the current/last run |
| `scout.log`, `ctrl.log` | *generated* — agent output if you redirect it (`*> scout.log`) |
| `sim_stderr.log` | *generated* — simulator server output |
| `run_output.log` | *stale* — from the removed single-process version; safe to delete |

---

## 5. Architecture

```
  scout_agent.py (PAC1)                    rc_agent.py (RC1, RC2)
        │  writes: discovered,                    │  writes: assigned,
        │  explored, scouting                     │  needs_both, repaired, explored
        ▼                                         ▼
  ┌──────────────────────── blackboard.json ────────────────────────┐
  │ round · booted · over · pending{agent: commands} · posts[]      │
  └───────────────────────────────┬─────────────────────────────────┘
                                  │ the submit that completes `pending`
                                  ▼ sends ONE merged batch
                     simulator  POST /api/text/execute   (1 time step)
```

**One round:**
1. Each agent reads the board and the simulator state.
2. `observe()` buffers posts about what changed.
3. `act()` picks its units' commands — asking the LLM only if there is a real choice.
4. `submit()` writes posts + commands under the lock.
5. The submit that completes the set calls the simulator once, advances `round`.
6. The other agent, waiting in `wait_for_next_round()`, sees the new round.

**Why one batched POST:** every `/execute` call advances the simulator clock.
Separate POSTs per agent would cost two time steps per round and put units on
different ticks.

**Why no orchestrator:** there used to be a `run_agents.py` main loop. It was
removed deliberately — the blackboard carries the turn-taking, so the agents
are genuinely independent.

**What the agents actually say to each other** — the text pasted into prompts:

```
controller reads (brief_for_controller):     scout reads (brief_for_scout):
  fault B at [-4, -4] (found round 3)          crews busy: RC1 on fault A, RC2 on fault C
  fault C at [0, -16] (found round 8)          faults closed: B
  regions swept: CentralBlock, EastCorridor    fault D needs BOTH crews (40 repair)
  scout heading to [0, -16]
```

---

## 6. Simulator facts you will trip over

These are all behaviours of `simulator_web_v23.py` / `simulator_core_v23.py`,
discovered by debugging. None are obvious from the API.

1. **The `case` field on `/api/load` is ignored.** Scenario files are always
   read from `cases/case1/`. To change the scenario, edit `case1`.
   (`cases/case2/` exists from an early attempt and is **never loaded**.)
2. **Hidden regions must be passed explicitly on load.** The unknown-region
   loader reads a root-level file that does not exist, so without this nothing
   is hidden. Symptom: `[MAP] 0 hidden regions`. Handled in
   `sim_client.case_unknown_regions`.
3. **Undiscovered faults are absent from `state["faults"]` entirely**, not
   flagged. Presence in the list = discovered.
4. **Busy units accept only `continue`.** Moving / Analyzing / Repairing.
   Units lock into Analyzing automatically when they come within range of an
   undiscovered fault, even mid-move.
5. **One illegal command rejects the whole batch (HTTP 400) and the clock does
   not advance.** Re-sending it deadlocks the run.
6. **A move to your own position is accepted as success** and silently wastes
   the step.
7. **Movement:** orthogonal grid steps. Cost per pixel is
   `1 / (move_speed × road_multiplier)`; level-2 road ×1.5, level-1 ×1.0,
   off-road = 1 pixel/step. Paths minimise *time*, so units detour onto
   highways. Units stop early when they discover a fault.
8. **Repair requires standing exactly on the fault** and spends crew resources
   one-for-one, capped per step by `repairable_faults[].maximum_amount`.
9. **There is no "Success" status.** Only Ready / Running / "Score locked at
   zero" / Completed. Completed = step limit reached = normal end.
10. **Score = sum of restored active power over every step**
    (`score += power`). If power ever *drops* below the previous step, the
    score is set to 0 and locked for the rest of the game.

---

## 7. Results and the open problem

Reference run (40-step limit, far starts, all faults hidden):

- All 4 faults found by round 8 — crews found A, B, D while travelling; the
  scout found C in the region no crew was heading to.
- All 4 repaired by round 20. Fault D (40) needed both crews: RC2 paid 24 and
  ran out, RC1 paid 16. Resources used 66 of 70; the scenario needs exactly 66.
- **Score: 0.0. Restored power: 0.0 kW for all 40 steps.**

**Why the score is zero:** repairing a fault clears it but does not re-energise
anything. Power only flows through closed switches. Switch **S1** sits on
**N1, the transmission source**, and is open — the grid has no supply. The
simulator accepts switch commands as a separate top-level key:

```json
{ "mobile_commands": { ... }, "switch_commands": { "S1": "closed" } }
```

`sim_client.execute()` never sends `switch_commands`. No agent operates
switches. **This is the next thing to build.**

### How much is the LLM actually deciding?

Reference run, 120 unit-commands over 40 rounds:

| | commands | chosen by LLM |
|---|---|---|
| RC1 + RC2 | 80 | 16 |
| PAC1 | 40 | 3 |
| **total** | **120** | **19 (16%)** |

The rest is code: "continue" while busy (the only legal command), "stay" when
nothing is left, 9 LLM answers discarded because that crew was busy, 1 no-op
move redirected. The LLM chooses where to search, which fault to take, and
when to repair.

---

## 8. Known issues and suggested next steps

In rough priority order:

1. **Switch agent (score is 0 without it).** A third blackboard participant.
   Needs no travel — switches are commanded remotely by name. Because any drop
   in power zeroes the score permanently, validate every plan with
   `POST /api/validate-switches` before committing it. Remember to add its name
   to `blackboard.EXPECTED`, or rounds will not wait for it.
2. **Half-wasted LLM calls.** When one crew is busy, the controller still asks
   the LLM for both and discards the busy crew's answer. Ask only about free
   crews.
3. **"explored" is approximate.** A region counts as explored once a unit
   stands inside it, not when all its pixels are inspected. Fine for the
   current small regions; revisit for large ones.
4. **`discovered` is always authored by SCOUT**, even when a crew found the
   fault, because the scout posts everything visible. Don't read authorship of
   that post kind as "who found it" — use unit positions in the logs.
5. **MPS1 (mobile power source) is unused.** It accepts
   `{"type": "supply", "p": ..., "q": ...}` and could restore power locally.
6. **Guards take decisions away from the LLM** (`clamp_repair`,
   `fix_noop_move`, pre-computed distances). Each was added because runs broke
   without it. If the research question is "what can the LLM decide", measure
   what breaks as you remove them.
7. **Blackboard robustness.** If one agent crashes, the other waits up to
   180 s then raises. A crashed holder of the lock is broken after 90 s.

---

## 9. Changes made outside `agents/`

`reference_simulator/` is **untracked in git**, so these originals cannot be
recovered from history. Recorded here.

### `cases/case1/Faults_v1.json`
| | original | now |
|---|---|---|
| A | [12, -8], 10 | [12, -8], 10 |
| B | [-4, -4], 8 | [-4, -4], 8 |
| C | — | [0, -16], 8 |
| D | — | [-4, -8], **40** (designed to need both crews) |

Faults must sit on a node or electrical-line pixel, or the simulator rejects
the scenario.

### `cases/case1/RepairCrews_v1.json` (positions only; speeds/resources unchanged)
| | original | now |
|---|---|---|
| RC1 | [6, 0] | [8, 16] |
| RC2 | [7, -16] | [12, 12] |
RC1: inspection 2, move 8, repair 5, resources 30. RC2: inspection 2, move 6, repair 8, resources 40.

### `cases/case1/UnknownState_v1.json`
Original:
```json
{ "event_id": 0, "default_inspected": true,
  "unknown_regions": [
    { "name": "InitialUnknownRegion", "lower_left": [-13, -17], "upper_right": [3, 3] },
    { "name": "V4UnknownSquare3x3",   "lower_left": [10, -18],  "upper_right": [12, -16] } ],
  "open_switches_in_unknown_regions": true,
  "open_switches_adjacent_to_unknown_areas": true }
```
Now: three regions — `EastCorridor` [8,-12]→[14,-4] (hides A),
`CentralBlock` [-8,-10]→[0,-2] (hides B, D), `SouthEnd` [-4,-18]→[4,-14]
(hides C) — and **both `open_switches_*` flags set to `false`**. Those flags
affect which switches start open, so check them when you build the switch
agent.

### `frontend/index_v23.html`
Added a `setInterval` at the end of the script (search `auto-refresh`) that
re-fetches `/api/state` every 2 s so the map updates without F5. It stops when
the game reports Completed.

### `cases/case2/`
Created early, before discovering the simulator ignores the case name. Unused.
Safe to delete.
