"""
IEEE-13 Network Configuration + 5 Training Cases
=================================================
Self-contained. No external imports.

Network: 19 nodes, 9 loads, 2 switches, 23 roads
Cases:   5 scenarios with different fault locations, RC/MPS positions
"""


class IEEE13Network:
    """Static IEEE-13 network topology."""

    # ── Nodes ──────────────────────────────────────────────
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

    # ── Loads (P=kW, Q=kVar, W=priority) ───────────────────
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

    # ── Electrical edges (id, from, to, km, state) ─────────
    # state: 'closed' = live, 'open' = normally open (reconfiguration)
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
        ('E_S2_V3',   'S2',  'V3',   2,  'open'),    # S2 normally open
        ('E_V3_V2',   'V3',  'V2',   2,  'closed'),
        ('E_V2_N1',   'V2',  'N1',   8,  'closed'),
    ]

    # ── Switches ────────────────────────────────────────────
    SWITCHES = {
        'S1': {'edges': ['E_N2_S1', 'E_S1_N3'], 'state': 'closed'},
        'S2': {'edges': ['E_V1_S2', 'E_S2_V3'], 'state': 'open'},
    }

    # ── Traffic roads (id, from, to, km) ────────────────────
    # Roads follow electrical lines + 4 shortcuts
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
        # Shortcuts (roads only, no electrical line)
        ('R_N7_V3',   'N7',  'V3',   2),
        ('R_V3_N7',   'V3',  'N7',   2),
        ('R_N12_V1',  'N12', 'V1',   4),
        ('R_V1_N12',  'V1',  'N12',  4),
    ]

    # ── Node positions for visualization (x, y) ─────────────
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
    """5 training cases for unknown fault discovery."""

    CASES = {
        'Case1': {
            'repair_crews': {
                'RC1': {'position': 'N9',  'speed': 3, 'efficiency': 2, 'resources': 12},
                'RC2': {'position': 'N2',  'speed': 5, 'efficiency': 3, 'resources': 12},
            },
            'mobile_power': {
                'MPS1': {'position': 'N12', 'speed': 8, 'p_limit': 750, 'energy': 3500},
                'MPS2': {'position': 'V3',  'speed': 8, 'p_limit': 750, 'energy': 4000},
            },
            'faults': [
                {'id': 'DP1', 'type': 'node', 'node': 'N5',  'demand': 10, 'cap': 2},
                {'id': 'DP2', 'type': 'node', 'node': 'S2',  'demand': 4,  'cap': 1},
                {'id': 'DP3', 'type': 'edge', 'edge': ('N2', 'S1'), 'demand': 10, 'cap': 2},
            ],
        },

        'Case2': {
            'repair_crews': {
                'RC1': {'position': 'N9',  'speed': 2, 'efficiency': 2, 'resources': 10},
                'RC2': {'position': 'N10', 'speed': 5, 'efficiency': 4, 'resources': 9},
            },
            'mobile_power': {
                'MPS1': {'position': 'N10', 'speed': 3, 'p_limit': 600, 'energy': 4000},
                'MPS2': {'position': 'N4',  'speed': 7, 'p_limit': 450, 'energy': 3000},
            },
            'faults': [
                {'id': 'DP1', 'type': 'edge', 'edge': ('N3', 'S1'),  'demand': 3,  'cap': 1},
                {'id': 'DP2', 'type': 'edge', 'edge': ('N2', 'S1'),  'demand': 5,  'cap': 1},
                {'id': 'DP3', 'type': 'edge', 'edge': ('N1', 'N2'),  'demand': 3,  'cap': 1},
                {'id': 'DP4', 'type': 'edge', 'edge': ('N13', 'V1'), 'demand': 3,  'cap': 1},
            ],
        },

        'Case3': {
            'repair_crews': {
                'RC1': {'position': 'N7',  'speed': 5, 'efficiency': 3, 'resources': 12},
                'RC2': {'position': 'N11', 'speed': 4, 'efficiency': 4, 'resources': 11},
            },
            'mobile_power': {
                'MPS1': {'position': 'N11', 'speed': 6, 'p_limit': 600, 'energy': 3500},
                'MPS2': {'position': 'N10', 'speed': 7, 'p_limit': 600, 'energy': 3500},
            },
            'faults': [
                {'id': 'DP1', 'type': 'node', 'node': 'N12', 'demand': 4, 'cap': 1},
                {'id': 'DP2', 'type': 'edge', 'edge': ('N2', 'S1'),  'demand': 4, 'cap': 1},
                {'id': 'DP3', 'type': 'edge', 'edge': ('N13', 'V1'), 'demand': 3, 'cap': 1},
            ],
        },

        'Case4': {
            'repair_crews': {
                'RC1': {'position': 'N9', 'speed': 2, 'efficiency': 4, 'resources': 10},
                'RC2': {'position': 'N8', 'speed': 6, 'efficiency': 2, 'resources': 11},
            },
            'mobile_power': {
                'MPS1': {'position': 'N13', 'speed': 4, 'p_limit': 600, 'energy': 4000},
                'MPS2': {'position': 'N11', 'speed': 8, 'p_limit': 450, 'energy': 3000},
            },
            'faults': [
                {'id': 'DP1', 'type': 'node', 'node': 'V3', 'demand': 4, 'cap': 1},
                {'id': 'DP2', 'type': 'node', 'node': 'N9', 'demand': 3, 'cap': 1},
                {'id': 'DP3', 'type': 'edge', 'edge': ('N3', 'S1'), 'demand': 7, 'cap': 1},
            ],
        },

        'Case5': {
            'repair_crews': {
                'RC1': {'position': 'N8', 'speed': 3, 'efficiency': 4, 'resources': 13},
                'RC2': {'position': 'N4', 'speed': 2, 'efficiency': 3, 'resources': 11},
            },
            'mobile_power': {
                'MPS1': {'position': 'V1',  'speed': 6, 'p_limit': 450, 'energy': 3500},
                'MPS2': {'position': 'N10', 'speed': 8, 'p_limit': 450, 'energy': 4000},
            },
            'faults': [
                {'id': 'DP1', 'type': 'edge', 'edge': ('N2', 'S1'),  'demand': 5, 'cap': 1},
                {'id': 'DP2', 'type': 'edge', 'edge': ('N3', 'N8'),  'demand': 4, 'cap': 1},
                {'id': 'DP3', 'type': 'edge', 'edge': ('N1', 'N2'),  'demand': 8, 'cap': 2},
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
