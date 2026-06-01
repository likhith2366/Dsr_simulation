"""
IEEE-13 Network Configuration + 5 Training Cases
=================================================
Self-contained. No external imports.

Section-based fault protection
-------------------------------
Section A (Grid side): Grid, N1, N2, N4, N5, N6, N7, V2, V3
  - No isolating switch. A fault here cascades downstream.
  - Dead-end branches: N4-N5, N6-N7 (only the dead-end node goes dark)

Section B (N3 side, behind switch S1): S1, N3, N8, N9, N10, N11, N12, N13, V1
  - S1 is the only feed into Section B.
  - ANY fault in Section B -> protection opens S1 -> entire Section B loses power.
  - Tie switch S2 (normally open) can restore Section B from V3 side.

Outage zones are AUTO-COMPUTED by the environment from the EGraph
after applying faults + opening the section switch. Not hardcoded here.
"""


class IEEE13Network:
    """Static IEEE-13 network topology."""

    # Nodes
    NODES = {
        'Grid': 'GRID',
        'N1':   'BUS',
        'N2':   'BUS',
        'N4':   'BUS',
        'N10':  'BUS',
        'N13':  'BUS',
        'V1':   'BUS',
        'V2':   'BUS',
        'V3':   'BUS',
        'S1':   'SWITCH',
        'S2':   'SWITCH',
        'N3':   'LOAD',
        'N5':   'LOAD',
        'N6':   'LOAD',
        'N7':   'LOAD',
        'N8':   'LOAD',
        'N9':   'LOAD',
        'N11':  'LOAD',
        'N12':  'LOAD',
    }

    # Loads (P=kW, Q=kVar, W=priority)
    LOADS = {
        'L_N3':  {'node': 'N3',  'P': 400, 'Q': 300, 'W': 6.0},
        'L_N5':  {'node': 'N5',  'P': 500, 'Q': 300, 'W': 5.0},
        'L_N6':  {'node': 'N6',  'P': 10,  'Q': 5,   'W': 4.0},
        'L_N7':  {'node': 'N7',  'P': 40,  'Q': 15,  'W': 5.0},
        'L_N8':  {'node': 'N8',  'P': 150, 'Q': 70,  'W': 2.0},
        'L_N9':  {'node': 'N9',  'P': 500, 'Q': 200, 'W': 4.0},
        'L_N11': {'node': 'N11', 'P': 200, 'Q': 80,  'W': 10.0},
        'L_N12': {'node': 'N12', 'P': 150, 'Q': -80, 'W': 5.0},
    }

    # Electrical edges (id, from, to, km, state)
    # 'closed' = live, 'open' = normally open
    EDGES = [
        ('E_Grid_N1', 'Grid', 'N1',  2,  'closed'),
        ('E_N1_N2',   'N1',  'N2',   2,  'closed'),
        ('E_N2_N4',   'N2',  'N4',   4,  'closed'),
        ('E_N4_N5',   'N4',  'N5',   2,  'closed'),
        ('E_N2_N6',   'N2',  'N6',   4,  'closed'),
        ('E_N6_N7',   'N6',  'N7',   2,  'closed'),
        ('E_N2_S1',   'N2',  'S1',   8,  'closed'),
        ('E_S1_N3',   'S1',  'N3',   8,  'closed'),
        ('E_N3_N8',   'N3',  'N8',   2,  'closed'),
        ('E_N8_N9',   'N8',  'N9',   4,  'closed'),
        ('E_N3_N10',  'N3',  'N10',  2,  'closed'),
        ('E_N10_N12', 'N10', 'N12',  2,  'closed'),
        ('E_N10_N11', 'N10', 'N11',  4,  'closed'),
        ('E_N3_N13',  'N3',  'N13',  8,  'closed'),
        ('E_N13_V1',  'N13', 'V1',   4,  'closed'),
        ('E_V1_S2',   'V1',  'S2',   4,  'closed'),
        ('E_S2_V3',   'S2',  'V3',   2,  'open'),    # S2 normally open (tie switch)
        ('E_V3_V2',   'V3',  'V2',   2,  'closed'),
        ('E_V2_N1',   'V2',  'N1',   8,  'closed'),
    ]

    # Switches
    SWITCHES = {
        'S1': {'edges': ['E_N2_S1', 'E_S1_N3'], 'state': 'closed'},
        'S2': {'edges': ['E_V1_S2', 'E_S2_V3'], 'state': 'open'},
    }

    # Sections: areas separated by switches
    # Section A has no isolating switch; faults there cascade downstream only.
    # Section B is protected by S1; any fault there trips S1, blacking out all of B.
    SECTIONS = {
        'A': {
            'nodes': {'Grid', 'N1', 'N2', 'N4', 'N5', 'N6', 'N7', 'V2', 'V3'},
            # E_Grid_N1 acts as the main substation breaker.
            # Any fault in Section A causes fault current → breaker trips → all of A (and B) lose power.
            'switch_edges': ['E_Grid_N1'],
        },
        'B': {
            'nodes': {'S1', 'N3', 'N8', 'N9', 'N10', 'N11', 'N12', 'N13', 'V1'},
            'switch_edges': ['E_N2_S1', 'E_S1_N3'],
        },
    }

    # Traffic roads (id, from, to, km)
    ROADS = [
        ('R_Grid_N1', 'Grid', 'N1',  2),
        ('R_N1_N2',   'N1',  'N2',   2),
        ('R_N2_N4',   'N2',  'N4',   4),
        ('R_N4_N5',   'N4',  'N5',   2),
        ('R_N2_N6',   'N2',  'N6',   4),
        ('R_N6_N7',   'N6',  'N7',   2),
        ('R_N2_S1',   'N2',  'S1',   8),
        ('R_S1_N3',   'S1',  'N3',   8),
        ('R_N3_N8',   'N3',  'N8',   2),
        ('R_N8_N9',   'N8',  'N9',   4),
        ('R_N3_N10',  'N3',  'N10',  2),
        ('R_N10_N12', 'N10', 'N12',  2),
        ('R_N10_N11', 'N10', 'N11',  4),
        ('R_N3_N13',  'N3',  'N13',  8),
        ('R_N13_V1',  'N13', 'V1',   4),
        ('R_V1_S2',   'V1',  'S2',   4),
        ('R_S2_V3',   'S2',  'V3',   2),
        ('R_V3_V2',   'V3',  'V2',   2),
        ('R_V2_N1',   'V2',  'N1',   8),
        # Shortcuts (road only, no electrical line)
        ('R_N7_V3',   'N7',  'V3',   2),
        ('R_V3_N7',   'V3',  'N7',   2),
        ('R_N12_V1',  'N12', 'V1',   4),
        ('R_V1_N12',  'V1',  'N12',  4),
    ]

    # Node positions for visualization
    NODE_POS = {
        'Grid': (0, 4),
        'N1':   (2, 4),
        'N2':   (4, 4),
        'N4':   (4, 6),
        'N5':   (4, 8),
        'N6':   (4, 2),
        'N7':   (4, 0),
        'S1':   (6, 4),
        'N3':   (8, 4),
        'N8':   (8, 6),
        'N9':   (8, 8),
        'N10':  (10, 4),
        'N11':  (12, 6),
        'N12':  (12, 2),
        'N13':  (10, 2),
        'V1':   (12, 0),
        'S2':   (10, 0),
        'V3':   (8, 0),
        'V2':   (6, 0),
    }


class IEEE13Cases:
    """
    5 training cases — each with exactly 3 faults.

    Outage zone rules (auto-computed from EGraph):
      Any fault in Section B  -> S1 opens -> all of Section B dark
      Fault on N1-N2 (feeder) -> cascading outage: N2 + all downstream dark
      Fault on dead-end       -> only that branch goes dark

    No outage_zones field — environment auto-computes from EGraph BFS.
    """

    CASES = {
        # ── Case 1: 3 faults spread across Section B ─────────────────────
        # S1 opens -> entire Section B dark.
        # Faults are scattered: entry, mid-section, and deep end.
        # Agents must search all of Section B to find all 3.
        'Case1': {
            'repair_crews': {
                'RC1': {'position': 'N2',  'speed': 4, 'efficiency': 3, 'resources': 15},
                'RC2': {'position': 'N11', 'speed': 5, 'efficiency': 3, 'resources': 15},
            },
            'mobile_power': {
                'MPS1': {'position': 'N4', 'speed': 8, 'p_limit': 600, 'energy': 4000},
            },
            'faults': [
                {'id': 'DP1', 'type': 'edge', 'edge': ('N3', 'N8'),  'demand': 4, 'cap': 1},
                {'id': 'DP2', 'type': 'node', 'node': 'N10',         'demand': 5, 'cap': 1},
                {'id': 'DP3', 'type': 'edge', 'edge': ('N13', 'V1'), 'demand': 4, 'cap': 1},
            ],
        },

        # ── Case 2: 2 Section B faults + 1 Section A dead-end ────────────
        # S1 opens (B faults) -> Section B dark; also N7 dark (dead-end A fault).
        # Mixed outage: agents split between Section B search and A dead-end.
        'Case2': {
            'repair_crews': {
                'RC1': {'position': 'N2', 'speed': 4, 'efficiency': 3, 'resources': 15},
                'RC2': {'position': 'N9', 'speed': 5, 'efficiency': 3, 'resources': 15},
            },
            'mobile_power': {
                'MPS1': {'position': 'N11', 'speed': 8, 'p_limit': 600, 'energy': 3500},
            },
            'faults': [
                {'id': 'DP1', 'type': 'edge', 'edge': ('N8', 'N9'),  'demand': 5, 'cap': 1},
                {'id': 'DP2', 'type': 'node', 'node': 'N13',         'demand': 6, 'cap': 1},
                {'id': 'DP3', 'type': 'edge', 'edge': ('N6', 'N7'),  'demand': 3, 'cap': 1},
            ],
        },

        # ── Case 3: 3 Section A faults — no section switch trips ──────────
        # S1 stays closed. Only {N5, N6, N7} lose power.
        # DP3 (N2-N6) cuts the whole N6 branch; DP2 also faults N6-N7.
        # Repairing DP3 restores N6; both DP2+DP3 repaired to restore N7.
        'Case3': {
            'repair_crews': {
                'RC1': {'position': 'N1', 'speed': 5, 'efficiency': 4, 'resources': 12},
                'RC2': {'position': 'V2', 'speed': 4, 'efficiency': 3, 'resources': 12},
            },
            'mobile_power': {
                'MPS1': {'position': 'N2', 'speed': 8, 'p_limit': 400, 'energy': 2500},
            },
            'faults': [
                {'id': 'DP1', 'type': 'edge', 'edge': ('N4', 'N5'), 'demand': 5, 'cap': 1},
                {'id': 'DP2', 'type': 'edge', 'edge': ('N6', 'N7'), 'demand': 4, 'cap': 1},
                {'id': 'DP3', 'type': 'edge', 'edge': ('N2', 'N6'), 'demand': 4, 'cap': 1},
            ],
        },

        # ── Case 4: Main feeder cut + 2 Section B faults (3-stage) ───────
        # S1 opens (B faults). N1-N2 cut cascades entire downstream.
        # Powered only: Grid, N1, V2, V3.
        # Stage 1: fix N1-N2 -> Section A recovers; Section B still dark.
        # Stage 2: fix both B faults -> S1 closes, full restoration.
        'Case4': {
            'repair_crews': {
                'RC1': {'position': 'N4', 'speed': 3, 'efficiency': 4, 'resources': 15},
                'RC2': {'position': 'N8', 'speed': 2, 'efficiency': 3, 'resources': 13},
            },
            'mobile_power': {
                'MPS1': {'position': 'V1', 'speed': 6, 'p_limit': 450, 'energy': 4000},
            },
            'faults': [
                {'id': 'DP1', 'type': 'edge', 'edge': ('N1', 'N2'), 'demand': 10, 'cap': 2},
                {'id': 'DP2', 'type': 'edge', 'edge': ('N8', 'N9'), 'demand': 5,  'cap': 1},
                {'id': 'DP3', 'type': 'node', 'node': 'N10',        'demand': 5,  'cap': 1},
            ],
        },

        # ── Case 5: Main feeder + Section B + Section A dead-end ─────────
        # S1 opens (B fault). N1-N2 cut cascades everything.
        # Stage 1: fix N1-N2 -> Section A recovers (except N5 still dark).
        # Stage 2: fix DP3 -> N5 restored.
        # Stage 3: fix DP2 (N13) -> S1 closes, Section B fully restored.
        'Case5': {
            'repair_crews': {
                'RC1': {'position': 'N8', 'speed': 3, 'efficiency': 4, 'resources': 15},
                'RC2': {'position': 'N2', 'speed': 2, 'efficiency': 3, 'resources': 18},
            },
            'mobile_power': {
                'MPS1': {'position': 'V1', 'speed': 6, 'p_limit': 450, 'energy': 4000},
            },
            'faults': [
                {'id': 'DP1', 'type': 'edge', 'edge': ('N1', 'N2'), 'demand': 10, 'cap': 2},
                {'id': 'DP2', 'type': 'node', 'node': 'N13',        'demand': 6,  'cap': 1},
                {'id': 'DP3', 'type': 'edge', 'edge': ('N4', 'N5'), 'demand': 5,  'cap': 1},
            ],
        },
    }

    @classmethod
    def get(cls, case_name: str) -> dict:
        if case_name not in cls.CASES:
            raise ValueError(f"Unknown case: {case_name}. Available: {list(cls.CASES.keys())}")
        return cls.CASES[case_name]

    @classmethod
    def all_cases(cls):
        return list(cls.CASES.keys())
