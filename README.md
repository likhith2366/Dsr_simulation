# DSR Simulator — Multi-Agent Distribution System Restoration

A simulation framework for **Distribution System Restoration (DSR)** using multi-agent coordination on an IEEE-13 inspired power network. Agents discover unknown faults, restore power, and coordinate repairs under realistic constraints.

---

## Overview

When a fault occurs in a power distribution network, the system operator may not know exactly where it is. This simulator models that real-world scenario:

- **Known mode** — fault locations are given upfront; agents go directly to repair
- **Unknown mode** — fault locations are hidden; Scout agents search the outage zone while Repair Crews follow behind

The overhead between the two modes quantifies the cost of uncertainty — a key metric for evaluating search and coordination strategies.

---

## Network

The network is an IEEE-13 inspired 19-node distribution feeder:

```
Section A (always connected to Grid):
  Grid → N1 → N2 → N4 → N5
                 → N6 → N7
                 → S1 (switch)

Section B (behind switch S1):
  S1 → N3 → N8 → N9
          → N10 → N11
               → N12
          → N13 → V1 → S2 (tie switch, normally open)

Tie path: S2 → V3 → V2 → N1
```

**Protection logic:**  
Any fault in Section B trips S1 open → entire Section B loses power. Tie switch S2 can restore partial power from the V3 side while repairs are underway.

---

## Agent Types

| Agent | Role | Speed |
|-------|------|-------|
| **RC** (Repair Crew) | Travels to fault, repairs it | 2–5 km/h |
| **Scout** | Fast searcher, discovers hidden faults | 10 km/h |
| **MPS** (Mobile Power Source) | Connects to unpowered node, restores load temporarily | 6–8 km/h |

---

## Training Cases

5 training cases, each with exactly 3 faults:

| Case | Fault Locations | Scenario |
|------|----------------|---------|
| Case 1 | 3 × Section B | Full section search |
| Case 2 | 2 × Section B + 1 × Section A dead-end | Mixed outage |
| Case 3 | 3 × Section A | No section switch trips |
| Case 4 | Main feeder + 2 × Section B | 3-stage restoration |
| Case 5 | Main feeder + Section B + Section A dead-end | Complex multi-stage |

### Results Summary

| Case | Known (h) | Unknown (h) | Overhead |
|------|-----------|-------------|----------|
| Case 1 | 7 | 8 | +1h |
| Case 2 | 8 | 12 | +4h |
| Case 3 | 5 | 7 | +2h |
| Case 4 | 6 | 6 | +0h |
| Case 5 | 8 | 11 | +3h |

---

## Project Structure

```
training_model/
├── config/
│   └── ieee13_cases.py       # Network topology + 5 training cases
├── core/
│   ├── agents.py             # RC, Scout, MPS, DamagePoint, Load
│   ├── environment.py        # DSR environment, step logic, section protection
│   └── graphs.py             # TGraph (road), EGraph (electrical)
├── visualizer.py             # Step-by-step network visualization
├── run_cases.py              # Run all 5 cases (known + unknown)
└── output/                   # Generated step images
```

---

## Quickstart

```bash
# Install dependencies
pip install matplotlib networkx

# Run all 5 cases
python -m training_model.run_cases
```

Output images saved to `training_model/output/` — one PNG per simulation step showing:
- Node power status (blue = ON, red = OFF)
- Edge states (live / faulted / open switch)
- Road-only shortcuts (dashed grey)
- Distance labels on every edge
- Agent positions and travel paths
- Fault markers (? hidden, ✗ discovered, ✓ repaired)

---

## Key Concepts

**Outage zone** — nodes not reachable from Grid through closed edges (computed by BFS). Agents only search within this zone.

**Section protection** — fault in Section B → S1 trips → BFS from Grid can no longer reach Section B → all Section B nodes enter outage zone.

**Two-stage restoration** — when the main feeder (N1–N2) is also faulted, Section A recovers first after that repair; Section B recovers separately when its own faults are fixed and S1 closes.

**Scout strategy** — greedy nearest-unvisited coverage within the outage zone. Each node is claimed immediately to prevent duplicate visits across agents.

---

## License

See [LICENSE](LICENSE).
