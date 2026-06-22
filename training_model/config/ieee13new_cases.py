"""
IEEE-13 New Network Configuration + 5 Training Cases
=====================================================
Based on the updated IEEE-13 diagram with 8 switches (S1-S8),
4 tie nodes (V1-V4), and 11 load nodes.

Switch colors in diagram:
  GREEN (S1-S5): normally CLOSED sectionalizers
  RED   (S6-S8): normally OPEN tie switches

Section protection:
  Section A: behind S1 (main breaker)
    Nodes: N1, S1, N2, N6, N7, S2, N4, N5
    Any Section A fault → S1 trips → total blackout

  Section B: behind S3
    Nodes: S3, N3, N10, N11, N12, V2, S4, N8, N9, N13, S5, V3
    Any Section B fault → S3 trips → Section B dark; Section A stays live

Tie switches for restoration:
  S6: V1 ↔ N1 (6km) — alternate top source
  S7: N13 ↔ V4 (5km) — alternate bottom source
  S8: N5 ↔ N9 (6km) — lateral tie
"""


class IEEE13NewNetwork:
    """Static IEEE-13 New network topology."""

    NODES = {
        'N1':  'GRID',
        'N2':  'BUS',
        'N3':  'BUS',
        'N4':  'BUS',
        'N9':  'BUS',
        'V1':  'BUS',
        'V2':  'BUS',
        'V3':  'BUS',
        'V4':  'BUS',
        'S1':  'SWITCH',
        'S2':  'SWITCH',
        'S3':  'SWITCH',
        'S4':  'SWITCH',
        'S5':  'SWITCH',
        'S6':  'SWITCH',
        'S7':  'SWITCH',
        'S8':  'SWITCH',
        'N5':  'LOAD',
        'N6':  'LOAD',
        'N7':  'LOAD',
        'N8':  'LOAD',
        'N10': 'LOAD',
        'N11': 'LOAD',
        'N12': 'LOAD',
        'N13': 'LOAD',
    }

    # Loads (P=kW, Q=kVar, W=priority)
    LOADS = {
        'L_N7':  {'node': 'N7',  'P': 40,  'Q': 15,  'W': 5},
        'L_N6':  {'node': 'N6',  'P': 10,  'Q': 5,   'W': 4},
        'L_N4':  {'node': 'N4',  'P': 250, 'Q': 120, 'W': 1},
        'L_N5':  {'node': 'N5',  'P': 500, 'Q': 300, 'W': 5},
        'L_V2':  {'node': 'V2',  'P': 120, 'Q': 60,  'W': 8},
        'L_N12': {'node': 'N12', 'P': 150, 'Q': -80, 'W': 5},
        'L_N10': {'node': 'N10', 'P': 150, 'Q': 70,  'W': 2},
        'L_N3':  {'node': 'N3',  'P': 400, 'Q': 300, 'W': 6},
        'L_N8':  {'node': 'N8',  'P': 500, 'Q': 200, 'W': 4},
        'L_N11': {'node': 'N11', 'P': 200, 'Q': 80,  'W': 10},
        'L_N13': {'node': 'N13', 'P': 200, 'Q': -100, 'W': 2},
    }

    # Electrical edges: (id, from, to, km, state)
    # Assumption: switch-to-node distance ≈ 0 (0.001 km) — switches sit AT the node.
    EDGES = [
        # ── Main section feeder (S1 = main breaker) ──────────────
        ('E_N1_S1',   'N1',  'S1',   0.01,  'closed'),
        ('E_S1_N2',   'S1',  'N2',   2,     'closed'),

        # ── West branch: N2 → N6 → N7 ────────────────────────────
        ('E_N2_N6',   'N2',  'N6',   4,     'closed'),
        ('E_N6_N7',   'N6',  'N7',   2,     'closed'),

        # ── East branch: N2 → S2 → N4 → N5 ──────────────────────
        ('E_N2_S2',   'N2',  'S2',   0.001, 'closed'),
        ('E_S2_N4',   'S2',  'N4',   4,     'closed'),
        ('E_N4_N5',   'N4',  'N5',   2,     'closed'),

        # ── South main feeder: N2 → S3 → N3 ─────────────────────
        ('E_N2_S3',   'N2',  'S3',   0.001, 'closed'),
        ('E_S3_N3',   'S3',  'N3',   8,     'closed'),

        # ── From N3: west branch to N10, N12, N11 ────────────────
        ('E_N3_N10',  'N3',  'N10',  2,     'closed'),
        ('E_N10_N12', 'N10', 'N12',  2,     'closed'),
        ('E_N10_N11', 'N10', 'N11',  4,     'closed'),

        # ── From N3: east branch via S4 to N8, N9 ────────────────
        ('E_N3_S4',   'N3',  'S4',   0.01,  'closed'),
        ('E_S4_N8',   'S4',  'N8',   2,     'closed'),
        ('E_N8_N9',   'N8',  'N9',   4,     'closed'),

        # ── From N3: south via S5 to N13, then V3 → V2 → V1 ────────
        ('E_N3_S5',   'N3',  'S5',   8,     'closed'),
        ('E_S5_N13',  'S5',  'N13',  0.01,  'closed'),
        ('E_N13_V3',  'N13', 'V3',   6,     'closed'),
        ('E_V3_V2',   'V3',  'V2',   4,     'closed'),
        ('E_V2_V1',   'V2',  'V1',   6,     'closed'),

        # ── Tie switches (normally OPEN) ──────────────────────────
        ('E_V1_S6',   'V1',  'S6',   6,     'open'),
        ('E_S6_N1',   'S6',  'N1',   0.01,  'open'),

        ('E_N5_S8',   'N5',  'S8',   0.01,  'open'),
        ('E_S8_N9',   'S8',  'N9',   6,     'open'),

        ('E_N13_S7',  'N13', 'S7',   0.01,  'open'),
        ('E_S7_V4',   'S7',  'V4',   5,     'open'),
    ]

    SWITCHES = {
        'S1': {'edges': ['E_N1_S1',  'E_S1_N2'],  'state': 'closed'},
        'S2': {'edges': ['E_N2_S2',  'E_S2_N4'],  'state': 'closed'},
        'S3': {'edges': ['E_N2_S3',  'E_S3_N3'],  'state': 'closed'},
        'S4': {'edges': ['E_N3_S4',  'E_S4_N8'],  'state': 'closed'},
        'S5': {'edges': ['E_N3_S5',  'E_S5_N13'], 'state': 'closed'},
        'S6': {'edges': ['E_V1_S6',  'E_S6_N1'],  'state': 'open'},
        'S7': {'edges': ['E_N13_S7', 'E_S7_V4'],  'state': 'open'},
        'S8': {'edges': ['E_N5_S8',  'E_S8_N9'],  'state': 'open'},
    }

    # Section protection — 5 areas (N1 is the transmission/grid, not in any area)
    # Assumption: switches are robust (no switch faults). Tie switches S6, S7, S8 start OPEN.
    SECTIONS = {
        'Area1': {
            # Protected by S1 (main substation breaker)
            'nodes': {'N2', 'N6', 'N7'},
            'switch_edges': ['E_N1_S1', 'E_S1_N2'],
        },
        'Area2': {
            # Protected by S2
            'nodes': {'N4', 'N5'},
            'switch_edges': ['E_N2_S2', 'E_S2_N4'],
        },
        'Area3': {
            # Protected by S4.
            'nodes': {'N8', 'N9'},
            'switch_edges': ['E_N3_S4', 'E_S4_N8'],
        },
        'Area4': {
            # Protected by S3
            'nodes': {'N3', 'N10', 'N11', 'N12'},
            'switch_edges': ['E_N2_S3', 'E_S3_N3'],
        },
        'Area5': {
            # Protected by S5 (for N13). V1, V2, V3 are tie / outer-ring nodes.
            'nodes': {'V1', 'V2', 'V3', 'N13'},
            'switch_edges': ['E_N3_S5', 'E_S5_N13'],
        },
    }

    # Traffic roads (id, from, to, km)
    # Same assumption: switch-to-node distance ≈ 0 (0.001 km).
    ROADS = [
        ('R_N1_S1',   'N1',  'S1',   0.01),
        ('R_S1_N2',   'S1',  'N2',   2),
        ('R_N2_N6',   'N2',  'N6',   4),
        ('R_N6_N7',   'N6',  'N7',   2),
        ('R_N2_S2',   'N2',  'S2',   0.001),
        ('R_S2_N4',   'S2',  'N4',   4),
        ('R_N4_N5',   'N4',  'N5',   2),
        ('R_N2_S3',   'N2',  'S3',   0.001),
        ('R_S3_N3',   'S3',  'N3',   8),
        ('R_N3_N10',  'N3',  'N10',  2),
        ('R_N10_N12', 'N10', 'N12',  2),
        ('R_N10_N11', 'N10', 'N11',  4),
        ('R_N3_S4',   'N3',  'S4',   0.01),
        ('R_S4_N8',   'S4',  'N8',   2),
        ('R_N8_N9',   'N8',  'N9',   4),
        ('R_N3_S5',   'N3',  'S5',   8),
        ('R_S5_N13',  'S5',  'N13',  0.01),
        ('R_N13_V3',  'N13', 'V3',   6),
        ('R_V3_N13',  'V3',  'N13',  6),
        ('R_V3_V2',   'V3',  'V2',   4),
        ('R_V2_V3',   'V2',  'V3',   4),
        ('R_V2_V1',   'V2',  'V1',   6),
        ('R_V1_V2',   'V1',  'V2',   6),
        ('R_V1_S6',   'V1',  'S6',   6),
        ('R_S6_N1',   'S6',  'N1',   0.01),
        ('R_N5_S8',   'N5',  'S8',   0.01),
        ('R_S8_N9',   'S8',  'N9',   6),
        ('R_N13_S7',  'N13', 'S7',   0.01),
        ('R_S7_V4',   'S7',  'V4',   5),
        # Shortcuts (road only — no power line, but agents can travel)
        ('R_N7_V1',   'N7',  'V1',   2),   # west branch ↔ top tie node (dotted)
        ('R_V1_N7',   'V1',  'N7',   2),
        ('R_N12_V2',  'N12', 'V2',   2),   # N12 ↔ V2 (dotted)
        ('R_V2_N12',  'V2',  'N12',  2),
        ('R_N4_N8',   'N4',  'N8',   6),   # east Section A ↔ east Section B (dotted)
        ('R_N8_N4',   'N8',  'N4',   6),
        ('R_N9_V4',   'N9',  'V4',   6),   # east bottom ↔ bottom-right tie (solid road)
        ('R_V4_N9',   'V4',  'N9',   6),
    ]

    # Node positions for visualization (x, y)
    NODE_POS = {
        'V1':  (-1.5, 8),  # external tie — offset left so V1→N7 and V1→V2 are diagonal, not overlapping
        'S6':  (3,  8),
        'N1':  (6,  8),
        'S1':  (6,  7),
        'N2':  (6,  6),
        'N7':  (0,  6),
        'N6':  (3,  6),
        'S2':  (8,  6),
        'N4':  (10, 6),
        'N5':  (12, 6),
        'S3':  (6,  5),
        'S8':  (12, 5),   # tie switch between N5(y=6) and N9(y=4)
        'V2':  (0,  4),
        'N12': (2,  4),
        'N10': (4,  4),
        'N3':  (6,  4),
        'S4':  (8,  4),
        'N8':  (10, 4),
        'N9':  (12, 4),
        'N11': (4,  2.5),
        'S5':  (6,  3),
        'N13': (6,  2),
        'S7':  (9,  2),
        'V3':  (0,  2),
        'V4':  (12, 2),
    }


class IEEE13NewCases:
    """
    5 training cases for the new IEEE-13 network.
    Each case has exactly 3 faults.

    Section rules:
      Section A fault → S1 trips → total blackout (both sections dark)
      Section B fault → S3 opens → Section B dark; Section A live
    """

    CASES = {
        # ── Case 1: 3 faults in Section B ────────────────────────────
        # S3 opens → Section B dark; Section A stays powered.
        # MPS can reach Section B while RCs search/repair.
        'Case1': {
            'repair_crews': {
                'RC1': {'position': 'N2',  'speed': 4, 'efficiency': 3, 'resources': 15},
                'RC2': {'position': 'N11', 'speed': 5, 'efficiency': 3, 'resources': 15},
            },
            'mobile_power': {
                'MPS1': {'position': 'N4', 'speed': 8, 'p_limit': 600, 'energy': 5000},
            },
            'faults': [
                {'id': 'DP1', 'type': 'edge', 'edge': ('N3',  'N10'), 'demand': 4, 'cap': 1},
                {'id': 'DP2', 'type': 'node', 'node': 'N11',          'demand': 5, 'cap': 1},
                {'id': 'DP3', 'type': 'edge', 'edge': ('N8',  'N9'),  'demand': 4, 'cap': 1},
            ],
        },

        # ── Case 2: 2 Section B + 1 Section A dead-end ───────────────
        # S3 opens (B faults) → Section B dark.
        # Section A stays live except N7 branch (dead-end fault).
        'Case2': {
            'repair_crews': {
                'RC1': {'position': 'N2',  'speed': 4, 'efficiency': 3, 'resources': 15},
                'RC2': {'position': 'N9',  'speed': 5, 'efficiency': 3, 'resources': 15},
            },
            'mobile_power': {
                'MPS1': {'position': 'N11', 'speed': 8, 'p_limit': 600, 'energy': 4000},
            },
            'faults': [
                {'id': 'DP1', 'type': 'edge', 'edge': ('N10', 'N12'), 'demand': 5, 'cap': 1},
                {'id': 'DP2', 'type': 'node', 'node': 'N13',          'demand': 6, 'cap': 1},
                {'id': 'DP3', 'type': 'edge', 'edge': ('N6',  'N7'),  'demand': 3, 'cap': 1},
            ],
        },

        # ── Case 3: 3 Area 1/2 faults — total blackout ───────────────
        # S1 trips (Area 1 fault) → entire grid dark.
        # Agents must search ALL nodes in outage zone.
        'Case3': {
            'repair_crews': {
                'RC1': {'position': 'N1',  'speed': 5, 'efficiency': 4, 'resources': 12},
                'RC2': {'position': 'V2',  'speed': 4, 'efficiency': 3, 'resources': 12},
            },
            'mobile_power': {
                'MPS1': {'position': 'N2', 'speed': 8, 'p_limit': 400, 'energy': 3000},
            },
            'faults': [
                {'id': 'DP1', 'type': 'edge', 'edge': ('N4',  'N5'),  'demand': 5, 'cap': 1},
                {'id': 'DP2', 'type': 'edge', 'edge': ('N6',  'N7'),  'demand': 4, 'cap': 1},
                {'id': 'DP3', 'type': 'edge', 'edge': ('N2',  'N6'),  'demand': 4, 'cap': 1},
            ],
        },

        # ── Case 4: Main feeder cut + 2 Section B faults ─────────────
        # Area 1 feeder cut: S1 trips → total blackout.
        # Stage 1: fix feeder → Area 1 recovers; Areas 3-5 still dark.
        # Stage 2: fix B faults → S3, S4 close, full restoration.
        'Case4': {
            'repair_crews': {
                'RC1': {'position': 'N4',  'speed': 3, 'efficiency': 4, 'resources': 15},
                'RC2': {'position': 'N8',  'speed': 2, 'efficiency': 3, 'resources': 13},
            },
            'mobile_power': {
                'MPS1': {'position': 'V3', 'speed': 6, 'p_limit': 450, 'energy': 5000},
            },
            'faults': [
                {'id': 'DP1', 'type': 'edge', 'edge': ('N2',  'N6'),  'demand': 10, 'cap': 2},
                {'id': 'DP2', 'type': 'edge', 'edge': ('N8',  'N9'),  'demand': 5,  'cap': 1},
                {'id': 'DP3', 'type': 'node', 'node': 'N10',          'demand': 5,  'cap': 1},
            ],
        },

        # ── Case 5: Main feeder + Section B + Section A dead-end ──────
        # Area 1 feeder cut: S1 trips → total blackout.
        # Stage 1: fix feeder → Area 1 recovers except Area 2 N5 dead-end fault.
        # Stage 2: fix DP3 → N5 restored.
        # Stage 3: fix DP2 → S5 closes, N13 restored.
        'Case5': {
            'repair_crews': {
                'RC1': {'position': 'N8',  'speed': 3, 'efficiency': 4, 'resources': 15},
                'RC2': {'position': 'N2',  'speed': 2, 'efficiency': 3, 'resources': 18},
            },
            'mobile_power': {
                'MPS1': {'position': 'V3', 'speed': 6, 'p_limit': 450, 'energy': 5000},
            },
            'faults': [
                {'id': 'DP1', 'type': 'edge', 'edge': ('N2',  'N6'),  'demand': 10, 'cap': 2},
                {'id': 'DP2', 'type': 'node', 'node': 'N13',          'demand': 6,  'cap': 1},
                {'id': 'DP3', 'type': 'edge', 'edge': ('N4',  'N5'),  'demand': 5,  'cap': 1},
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
