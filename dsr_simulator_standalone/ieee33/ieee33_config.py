"""
IEEE-33 Bus Distribution System Configuration
==============================================

This module defines the complete configuration for the IEEE-33 bus distribution system.

System structure (45 nodes):
  - 1 Grid node (main grid power source)
  - 3 BUS nodes (G1, N1, N2 - pure connection points)
  - 31 LOAD nodes (N3~N33)
  - 10 SWITCH nodes (S1~S10)

Electrical edges (49):
  - 39 normally-closed edges (normal operating topology)
  - 10 normally-open tie lines (controlled by S6~S10, used for network reconfiguration)

Switches (10):
  - S1~S5: normally closed (sectionalizing switches)
  - S6~S10: normally open (tie switches, used for network reconfiguration during fault recovery)

Loads (31):
  - Total active power: ~3,535 kW
  - Maximum load: L_N25, L_N26 (420kW)
  - Priority weights W: 1~10

Training cases (10):
  - Case1~Case10, with different RC/MPS configurations and fault layouts
  - Each case has 5~8 fault points

Correspondence with IEEE-13 configuration:
  - Same interface: get_case_config(case_name), get_all_cases()
  - Same structure: nodes, loads, edges, switches, traffic_roads, repair_crews, mobile_power_sources, faults

Dependencies: None (pure Python standard library)
"""

from typing import Dict, List, Any, Tuple, Optional
import json
import copy


class IEEE33Config:
    """Configuration for IEEE-33 node system"""

    def __init__(self):
        self.system_config = self._build_system_config()
        self.training_cases = self._build_training_cases()

    # -------------------------
    # System (static) blueprint
    # -------------------------
    def _build_system_config(self) -> Dict[str, Any]:
        """
        Build the IEEE-33 system configuration.
        Notes:
        - Node types:
            GRID: external grid connection (Grid)
            LOAD: node with load (N3-N33, 31 nodes)
            BUS: transit/bus node without load (G1, N1, N2)
            SWITCH: sectionalizing/reconfiguration switch node (S1-S10)
        - Length units: km
        - Switch initial states: S1-S5 closed, S6-S10 open
        - Network includes normally-open edges for network reconfiguration
        """

        # Node configuration
        nodes = {
            'Grid': {'type': 'GRID'},
            'G1': {'type': 'BUS'},  # Grid connection point

            # Switches (S1-S10)
            'S1': {'type': 'SWITCH'},
            'S2': {'type': 'SWITCH'},
            'S3': {'type': 'SWITCH'},
            'S4': {'type': 'SWITCH'},
            'S5': {'type': 'SWITCH'},
            'S6': {'type': 'SWITCH'},
            'S7': {'type': 'SWITCH'},
            'S8': {'type': 'SWITCH'},
            'S9': {'type': 'SWITCH'},
            'S10': {'type': 'SWITCH'},

            # Bus nodes (no load)
            'N1': {'type': 'BUS'},
            'N2': {'type': 'BUS'},

            # Load nodes (N3-N33)
            'N3': {'type': 'LOAD'},   # (100, 60, 1)
            'N4': {'type': 'LOAD'},   # (90, 40, 1)
            'N5': {'type': 'LOAD'},   # (120, 80, 1)
            'N6': {'type': 'LOAD'},   # (60, 30, 1)
            'N7': {'type': 'LOAD'},   # (60, 20, 1)
            'N8': {'type': 'LOAD'},   # (200, 100, 2)
            'N9': {'type': 'LOAD'},   # (200, 100, 2)
            'N10': {'type': 'LOAD'},  # (60, 20, 1)
            'N11': {'type': 'LOAD'},  # (60, 20, 1)
            'N12': {'type': 'LOAD'},  # (45, 30, 1)
            'N13': {'type': 'LOAD'},  # (60, 35, 10)
            'N14': {'type': 'LOAD'},  # (60, 35, 8)
            'N15': {'type': 'LOAD'},  # (120, 80, 4)
            'N16': {'type': 'LOAD'},  # (60, 10, 2)
            'N17': {'type': 'LOAD'},  # (60, 20, 2)
            'N18': {'type': 'LOAD'},  # (60, 20, 8)
            'N19': {'type': 'LOAD'},  # (90, 40, 1)
            'N20': {'type': 'LOAD'},  # (90, 40, 6)
            'N21': {'type': 'LOAD'},  # (90, 40, 5)
            'N22': {'type': 'LOAD'},  # (90, 40, 1)
            'N23': {'type': 'LOAD'},  # (90, 40, 1)
            'N24': {'type': 'LOAD'},  # (90, 50, 1)
            'N25': {'type': 'LOAD'},  # (420, 200, 5)
            'N26': {'type': 'LOAD'},  # (420, 200, 3)
            'N27': {'type': 'LOAD'},  # (60, 25, 2)
            'N28': {'type': 'LOAD'},  # (60, 25, 10)
            'N29': {'type': 'LOAD'},  # (60, 20, 2)
            'N30': {'type': 'LOAD'},  # (120, 70, 3)
            'N31': {'type': 'LOAD'},  # (200, 600, 5)
            'N32': {'type': 'LOAD'},  # (150, 70, 2)
            'N33': {'type': 'LOAD'},  # (210, 100, 2)
        }

        # Load configuration: (P, Q, W) - 31 load nodes
        # IMPORTANT: Load IDs must match format expected by LLM and envs.py regex (L_N\d+)
        loads = {
            'L_N3':  {'node_id': 'N3',  'P': 100, 'Q': 60,  'W': 1.0},
            'L_N4':  {'node_id': 'N4',  'P': 90,  'Q': 40,  'W': 1.0},
            'L_N5':  {'node_id': 'N5',  'P': 120, 'Q': 80,  'W': 1.0},
            'L_N6':  {'node_id': 'N6',  'P': 60,  'Q': 30,  'W': 1.0},
            'L_N7':  {'node_id': 'N7',  'P': 60,  'Q': 20,  'W': 1.0},
            'L_N8':  {'node_id': 'N8',  'P': 200, 'Q': 100, 'W': 2.0},
            'L_N9':  {'node_id': 'N9',  'P': 200, 'Q': 100, 'W': 2.0},
            'L_N10': {'node_id': 'N10', 'P': 60,  'Q': 20,  'W': 1.0},
            'L_N11': {'node_id': 'N11', 'P': 60,  'Q': 20,  'W': 1.0},
            'L_N12': {'node_id': 'N12', 'P': 45,  'Q': 30,  'W': 1.0},
            'L_N13': {'node_id': 'N13', 'P': 60,  'Q': 35,  'W': 10.0},
            'L_N14': {'node_id': 'N14', 'P': 60,  'Q': 35,  'W': 8.0},
            'L_N15': {'node_id': 'N15', 'P': 120, 'Q': 80,  'W': 4.0},
            'L_N16': {'node_id': 'N16', 'P': 60,  'Q': 10,  'W': 2.0},
            'L_N17': {'node_id': 'N17', 'P': 60,  'Q': 20,  'W': 2.0},
            'L_N18': {'node_id': 'N18', 'P': 60,  'Q': 20,  'W': 8.0},
            'L_N19': {'node_id': 'N19', 'P': 90,  'Q': 40,  'W': 1.0},
            'L_N20': {'node_id': 'N20', 'P': 90,  'Q': 40,  'W': 6.0},
            'L_N21': {'node_id': 'N21', 'P': 90,  'Q': 40,  'W': 5.0},
            'L_N22': {'node_id': 'N22', 'P': 90,  'Q': 40,  'W': 1.0},
            'L_N23': {'node_id': 'N23', 'P': 90,  'Q': 40,  'W': 1.0},
            'L_N24': {'node_id': 'N24', 'P': 90,  'Q': 50,  'W': 1.0},
            'L_N25': {'node_id': 'N25', 'P': 420, 'Q': 200, 'W': 5.0},
            'L_N26': {'node_id': 'N26', 'P': 420, 'Q': 200, 'W': 3.0},
            'L_N27': {'node_id': 'N27', 'P': 60,  'Q': 25,  'W': 2.0},
            'L_N28': {'node_id': 'N28', 'P': 60,  'Q': 25,  'W': 10.0},
            'L_N29': {'node_id': 'N29', 'P': 60,  'Q': 20,  'W': 2.0},
            'L_N30': {'node_id': 'N30', 'P': 120, 'Q': 70,  'W': 3.0},
            'L_N31': {'node_id': 'N31', 'P': 200, 'Q': 600, 'W': 5.0},
            'L_N32': {'node_id': 'N32', 'P': 150, 'Q': 70,  'W': 2.0},
            'L_N33': {'node_id': 'N33', 'P': 210, 'Q': 100, 'W': 2.0},
        }

        # Electrical edges - Format: (edge_id, from_node, to_node, length_km, status)
        # Status: 'Closed' (normally-closed) or 'Opened' (normally-open for reconfiguration)
        edges = [
            # Main feeder
            ('E_Grid_G1',  'Grid', 'G1', 1, 'Closed'),
            ('E_G1_N1',    'G1',   'N1', 2, 'Closed'),
            ('E_N1_N2',    'N1',   'N2', 2, 'Closed'),

            # Branch 1: N2->N3->...->N18
            ('E_N2_N3',    'N2',   'N3', 8, 'Closed'),
            ('E_N3_N4',    'N3',   'N4', 6, 'Closed'),
            ('E_N4_N5',    'N4',   'N5', 6, 'Closed'),
            ('E_N5_N6',    'N5',   'N6', 16, 'Closed'),
            ('E_N6_N7',    'N6',   'N7', 2, 'Closed'),
            ('E_N7_S2',    'N7',   'S2', 1, 'Closed'),
            ('E_S2_N8',    'S2',   'N8', 33, 'Closed'),
            ('E_N8_N9',    'N8',   'N9', 20, 'Closed'),
            ('E_N9_S5',    'N9',   'S5', 1, 'Closed'),
            ('E_S5_N10',   'S5',   'N10', 19, 'Closed'),
            ('E_N10_N11',  'N10',  'N11', 4, 'Closed'),
            ('E_N11_N12',  'N11',  'N12', 6, 'Closed'),
            ('E_N12_N13',  'N12',  'N13', 28, 'Closed'),
            ('E_N13_N14',  'N13',  'N14', 10, 'Closed'),
            ('E_N14_N15',  'N14',  'N15', 10, 'Closed'),
            ('E_N15_N16',  'N15',  'N16', 14, 'Closed'),
            ('E_N16_N17',  'N16',  'N17', 24, 'Closed'),
            ('E_N17_N18',  'N17',  'N18', 14, 'Closed'),

            # Branch 2: N2->N19->S1->N20->N21->N22
            ('E_N2_N19',   'N2',   'N19', 2, 'Closed'),
            ('E_N19_S1',   'N19',  'S1', 1, 'Closed'),
            ('E_S1_N20',   'S1',   'N20', 29, 'Closed'),
            ('E_N20_N21',  'N20',  'N21', 8, 'Closed'),
            ('E_N21_N22',  'N21',  'N22', 14, 'Closed'),

            # Branch 3: N3->N23->S4->N24->N25
            ('E_N3_N23',   'N3',   'N23', 8, 'Closed'),
            ('E_N23_S4',   'N23',  'S4', 1, 'Closed'),
            ('E_S4_N24',   'S4',   'N24', 17, 'Closed'),
            ('E_N24_N25',  'N24',  'N25', 18, 'Closed'),

            # Branch 4: N6->N26->N27->S3->N28->N29->N30->N31->N32->N33
            ('E_N6_N26',   'N6',   'N26', 4, 'Closed'),
            ('E_N26_N27',  'N26',  'N27', 6, 'Closed'),
            ('E_N27_S3',   'N27',  'S3', 1, 'Closed'),
            ('E_S3_N28',   'S3',   'N28', 19, 'Closed'),
            ('E_N28_N29',  'N28',  'N29', 16, 'Closed'),
            ('E_N29_N30',  'N29',  'N30', 10, 'Closed'),
            ('E_N30_N31',  'N30',  'N31', 18, 'Closed'),
            ('E_N31_N32',  'N31',  'N32', 6, 'Closed'),
            ('E_N32_N33',  'N32',  'N33', 6, 'Closed'),

            # Normally-open tie lines (S6-S10 for network reconfiguration)
            ('E_N8_S6',    'N8',   'S6', 1, 'Opened'),
            ('E_S6_N21',   'S6',   'N21', 9, 'Opened'),
            ('E_N29_S7',   'N29',  'S7', 1, 'Opened'),
            ('E_S7_N25',   'S7',   'N25', 14, 'Opened'),
            ('E_N12_S8',   'N12',  'S8', 1, 'Opened'),
            ('E_S8_N22',   'S8',   'N22', 29, 'Opened'),
            ('E_N15_S9',   'N15',  'S9', 1, 'Opened'),
            ('E_S9_N9',    'S9',   'N9', 34, 'Opened'),
            ('E_N18_S10',  'N18',  'S10', 1, 'Opened'),
            ('E_S10_N33',  'S10',  'N33', 19, 'Opened'),
        ]

        # Switch configuration: control edges at each switch node
        # Initial states: S1-S5 closed (1), S6-S10 open (0)
        switches = {
            'S1': {
                'node_id': 'S1',
                'connected_edges': ['E_N19_S1', 'E_S1_N20'],
                'initial_state': 'close'
            },
            'S2': {
                'node_id': 'S2',
                'connected_edges': ['E_N7_S2', 'E_S2_N8'],
                'initial_state': 'close'
            },
            'S3': {
                'node_id': 'S3',
                'connected_edges': ['E_N27_S3', 'E_S3_N28'],
                'initial_state': 'close'
            },
            'S4': {
                'node_id': 'S4',
                'connected_edges': ['E_N23_S4', 'E_S4_N24'],
                'initial_state': 'close'
            },
            'S5': {
                'node_id': 'S5',
                'connected_edges': ['E_N9_S5', 'E_S5_N10'],
                'initial_state': 'close'
            },
            'S6': {
                'node_id': 'S6',
                'connected_edges': ['E_N8_S6', 'E_S6_N21'],
                'initial_state': 'open'
            },
            'S7': {
                'node_id': 'S7',
                'connected_edges': ['E_N29_S7', 'E_S7_N25'],
                'initial_state': 'open'
            },
            'S8': {
                'node_id': 'S8',
                'connected_edges': ['E_N12_S8', 'E_S8_N22'],
                'initial_state': 'open'
            },
            'S9': {
                'node_id': 'S9',
                'connected_edges': ['E_N15_S9', 'E_S9_N9'],
                'initial_state': 'open'
            },
            'S10': {
                'node_id': 'S10',
                'connected_edges': ['E_N18_S10', 'E_S10_N33'],
                'initial_state': 'open'
            },
        }

        # Traffic roads derived from electrical edges (agents travel on these)
        traffic_roads = [
            (f"TR_{eid[2:]}" if eid.startswith('E_') else f"TR_{frm}_{to}", frm, to, length)
            for (eid, frm, to, length, status) in edges
        ]

        # Add traffic-only roads (for RC/MPS movement, not electrical connections)
        # These are additional routes that don't have electrical lines
        traffic_only_roads = [
            ('TR_N4_N20',   'N4',  'N20', 2),
            ('TR_N20_N4',   'N20', 'N4',  2),
            ('TR_N20_N6',   'N20', 'N6',  8),
            ('TR_N6_N20',   'N6',  'N20', 8),
            ('TR_N5_N24',   'N5',  'N24', 6),
            ('TR_N24_N5',   'N24', 'N5',  6),
            ('TR_N24_N26',  'N24', 'N26', 4),
            ('TR_N26_N24',  'N26', 'N24', 4),
            ('TR_N7_N27',   'N7',  'N27', 2),
            ('TR_N27_N7',   'N27', 'N7',  2),
            ('TR_N27_N25',  'N27', 'N25', 4),
            ('TR_N25_N27',  'N25', 'N27', 4),
            ('TR_N25_N28',  'N25', 'N28', 4),
            ('TR_N28_N25',  'N28', 'N25', 4),
            ('TR_N28_N8',   'N28', 'N8',  4),
            ('TR_N8_N28',   'N8',  'N28', 4),
            ('TR_N22_N9',   'N22', 'N9',  10),
            ('TR_N9_N22',   'N9',  'N22', 10),
            ('TR_N9_N29',   'N9',  'N29', 4),
            ('TR_N29_N9',   'N29', 'N9',  4),
            ('TR_N10_N30',  'N10', 'N30', 4),
            ('TR_N30_N10',  'N30', 'N10', 4),
            ('TR_N11_N31',  'N11', 'N31', 4),
            ('TR_N31_N11',  'N31', 'N11', 4),
            ('TR_N13_N32',  'N13', 'N32', 6),
            ('TR_N32_N13',  'N32', 'N13', 6),
            ('TR_N13_N16',  'N13', 'N16', 16),
            ('TR_N16_N13',  'N16', 'N13', 16),
            ('TR_N17_N33',  'N17', 'N33', 10),
            ('TR_N33_N17',  'N33', 'N17', 10),
        ]
        traffic_roads.extend(traffic_only_roads)

        return {
            'nodes': nodes,
            'loads': loads,
            'edges': edges,
            'traffic_roads': traffic_roads,
            'switches': switches
        }

    # -------------------------
    # Training cases (RC, MPS, and faults)
    # -------------------------
    def _build_training_cases(self) -> Dict[str, Dict[str, Any]]:
        """
        Build training cases for IEEE-33 system.
        Each case includes:
            - repair_crews: dict with RC configurations (initial_position, speed, resources, efficiency)
            - mobile_power_sources: dict with MPS configuration (initial_position, speed, p_limit, s_limit, energy)
            - faults: list of damage points (type, node/edge, offset_from, offset, demand, cap)

        Note: RC and MPS configurations are the same across all cases, only faults differ.
              RC1: N7, speed=6, efficiency=6, resources=30
              RC2: N12, speed=8, efficiency=4, resources=24
              MPS1: N16, speed=8, p_limit=1000, s_limit=1100, energy=10000
              MPS2: N25, speed=8, p_limit=600, s_limit=800, energy=6000
        """

        # Standard RC configuration for all cases
        standard_rcs = {
            'RC1': {'initial_position': 'N7', 'speed': 6, 'efficiency': 6, 'resources': 30},
            'RC2': {'initial_position': 'N12', 'speed': 8, 'efficiency': 4, 'resources': 24}
        }

        # Standard MPS configuration for all cases (INTEGER VALUES for simplified LLM reasoning)
        standard_mps = {
            'MPS1': {'initial_position': 'N16', 'speed': 8, 'p_limit': 1000, 's_limit': 1100, 'energy': 10000},
            'MPS2': {'initial_position': 'N25', 'speed': 8, 'p_limit': 600, 's_limit': 800, 'energy': 6000}
        }

        cases = {
            'Case1': {
                'repair_crews': standard_rcs,
                'mobile_power_sources': standard_mps,
                'faults': [
                    {'fault_id': 'DP1', 'type': 'edge', 'edge': ('N1', 'N2'), 'offset_from': 'N1', 'offset': 1, 'demand': 10, 'cap': 2},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('N2', 'N3'), 'offset_from': 'N2', 'offset': 4, 'demand': 6, 'cap': 1},
                    {'fault_id': 'DP3', 'type': 'node', 'node': 'S1', 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP4', 'type': 'edge', 'edge': ('N28', 'N29'), 'offset_from': 'N28', 'offset': 10, 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP5', 'type': 'edge', 'edge': ('N12', 'N13'), 'offset_from': 'N12', 'offset': 12, 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP6', 'type': 'edge', 'edge': ('N8', 'N9'), 'offset_from': 'N8', 'offset': 2, 'demand': 14, 'cap': 2},
                ],
            },
            'Case2': {
                'repair_crews': standard_rcs,
                'mobile_power_sources': standard_mps,
                'faults': [
                    {'fault_id': 'DP1', 'type': 'edge', 'edge': ('G1', 'N1'), 'offset_from': 'G1', 'offset': 1, 'demand': 32, 'cap': 2},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('N20', 'N21'), 'offset_from': 'N20', 'offset': 4, 'demand': 6, 'cap': 1},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('S4', 'N24'), 'offset_from': 'S4', 'offset': 4, 'demand': 6, 'cap': 1},
                    {'fault_id': 'DP4', 'type': 'node', 'node': 'S3', 'demand': 2, 'cap': 1},
                    {'fault_id': 'DP5', 'type': 'edge', 'edge': ('N13', 'N14'), 'offset_from': 'N13', 'offset': 4, 'demand': 6, 'cap': 1},
                    {'fault_id': 'DP6', 'type': 'edge', 'edge': ('N16', 'N17'), 'offset_from': 'N16', 'offset': 22, 'demand': 2, 'cap': 1},
                ],
            },
            'Case3': {
                'repair_crews': standard_rcs,
                'mobile_power_sources': standard_mps,
                'faults': [
                    {'fault_id': 'DP1', 'type': 'edge', 'edge': ('S1', 'N20'), 'offset_from': 'S1', 'offset': 18, 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('N5', 'N6'), 'offset_from': 'N5', 'offset': 6, 'demand': 10, 'cap': 2},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('N24', 'N25'), 'offset_from': 'N24', 'offset': 8, 'demand': 14, 'cap': 2},
                    {'fault_id': 'DP4', 'type': 'edge', 'edge': ('N22', 'S8'), 'offset_from': 'N22', 'offset': 12, 'demand': 6, 'cap': 1},
                    {'fault_id': 'DP5', 'type': 'edge', 'edge': ('N21', 'S6'), 'offset_from': 'N21', 'offset': 4, 'demand': 4, 'cap': 1},
                    {'fault_id': 'DP6', 'type': 'edge', 'edge': ('N10', 'N11'), 'offset_from': 'N10', 'offset': 2, 'demand': 2, 'cap': 1},
                    {'fault_id': 'DP7', 'type': 'edge', 'edge': ('N14', 'N15'), 'offset_from': 'N14', 'offset': 4, 'demand': 4, 'cap': 1},
                    {'fault_id': 'DP8', 'type': 'edge', 'edge': ('N28', 'N29'), 'offset_from': 'N28', 'offset': 8, 'demand': 6, 'cap': 1},
                ],
            },
            'Case4': {
                'repair_crews': standard_rcs,
                'mobile_power_sources': standard_mps,
                'faults': [
                    {'fault_id': 'DP1', 'type': 'edge', 'edge': ('N2', 'N3'), 'offset_from': 'N2', 'offset': 2, 'demand': 14, 'cap': 2},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('S1', 'N20'), 'offset_from': 'S1', 'offset': 4, 'demand': 12, 'cap': 2},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('N3', 'N23'), 'offset_from': 'N3', 'offset': 4, 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP4', 'type': 'edge', 'edge': ('N30', 'N31'), 'offset_from': 'N30', 'offset': 8, 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP5', 'type': 'node', 'node': 'S2', 'demand': 12, 'cap': 2},
                ],
            },
            'Case5': {
                'repair_crews': standard_rcs,
                'mobile_power_sources': standard_mps,
                'faults': [
                    {'fault_id': 'DP1', 'type': 'edge', 'edge': ('N5', 'N6'), 'offset_from': 'N5', 'offset': 8, 'demand': 18, 'cap': 2},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('N22', 'S8'), 'offset_from': 'N22', 'offset': 18, 'demand': 10, 'cap': 2},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('N21', 'S6'), 'offset_from': 'N21', 'offset': 4, 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP4', 'type': 'edge', 'edge': ('N24', 'N25'), 'offset_from': 'N24', 'offset': 10, 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP5', 'type': 'edge', 'edge': ('N12', 'N13'), 'offset_from': 'N12', 'offset': 24, 'demand': 6, 'cap': 1},
                    {'fault_id': 'DP6', 'type': 'edge', 'edge': ('N30', 'N31'), 'offset_from': 'N30', 'offset': 10, 'demand': 4, 'cap': 1},
                ],
            },
            'Case6': {
                'repair_crews': standard_rcs,
                'mobile_power_sources': standard_mps,
                'faults': [
                    {'fault_id': 'DP1', 'type': 'edge', 'edge': ('N1', 'N2'), 'offset_from': 'N1', 'offset': 1, 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('N3', 'N23'), 'offset_from': 'N3', 'offset': 5, 'demand': 10, 'cap': 2},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('N25', 'S7'), 'offset_from': 'N25', 'offset': 10, 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP4', 'type': 'edge', 'edge': ('N32', 'N33'), 'offset_from': 'N32', 'offset': 2, 'demand': 10, 'cap': 2},
                    {'fault_id': 'DP5', 'type': 'node', 'node': 'S9', 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP6', 'type': 'node', 'node': 'N12', 'demand': 10, 'cap': 2},
                ],
            },
            'Case7': {
                'repair_crews': standard_rcs,
                'mobile_power_sources': standard_mps,
                'faults': [
                    {'fault_id': 'DP1', 'type': 'node', 'node': 'N1', 'demand': 12, 'cap': 2},
                    {'fault_id': 'DP2', 'type': 'node', 'node': 'N19', 'demand': 10, 'cap': 2},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('N4', 'N5'), 'offset_from': 'N4', 'offset': 4, 'demand': 12, 'cap': 2},
                    {'fault_id': 'DP4', 'type': 'node', 'node': 'N8', 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP5', 'type': 'edge', 'edge': ('N28', 'N29'), 'offset_from': 'N28', 'offset': 8, 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP6', 'type': 'edge', 'edge': ('N30', 'N31'), 'offset_from': 'N30', 'offset': 8, 'demand': 4, 'cap': 1},
                ],
            },
            'Case8': {
                'repair_crews': standard_rcs,
                'mobile_power_sources': standard_mps,
                'faults': [
                    {'fault_id': 'DP1', 'type': 'node', 'node': 'N2', 'demand': 20, 'cap': 2},
                    {'fault_id': 'DP2', 'type': 'node', 'node': 'N21', 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('S2', 'N8'), 'offset_from': 'S2', 'offset': 17, 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP4', 'type': 'node', 'node': 'S7', 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP5', 'type': 'node', 'node': 'N15', 'demand': 6, 'cap': 1},
                    {'fault_id': 'DP6', 'type': 'edge', 'edge': ('N30', 'N31'), 'offset_from': 'N30', 'offset': 8, 'demand': 4, 'cap': 1},
                ],
            },
            'Case9': {
                'repair_crews': standard_rcs,
                'mobile_power_sources': standard_mps,
                'faults': [
                    {'fault_id': 'DP1', 'type': 'edge', 'edge': ('G1', 'N1'), 'offset_from': 'G1', 'offset': 1, 'demand': 6, 'cap': 1},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('N2', 'N19'), 'offset_from': 'N2', 'offset': 1, 'demand': 6, 'cap': 1},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('N5', 'N6'), 'offset_from': 'N5', 'offset': 8, 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP4', 'type': 'node', 'node': 'N8', 'demand': 10, 'cap': 2},
                    {'fault_id': 'DP5', 'type': 'edge', 'edge': ('N28', 'N29'), 'offset_from': 'N28', 'offset': 6, 'demand': 6, 'cap': 1},
                    {'fault_id': 'DP6', 'type': 'node', 'node': 'N12', 'demand': 10, 'cap': 2},
                    {'fault_id': 'DP7', 'type': 'edge', 'edge': ('N25', 'S7'), 'offset_from': 'N25', 'offset': 4, 'demand': 4, 'cap': 1},
                    {'fault_id': 'DP8', 'type': 'edge', 'edge': ('N33', 'S10'), 'offset_from': 'N33', 'offset': 3, 'demand': 4, 'cap': 1},
                ],
            },
            'Case10': {
                'repair_crews': standard_rcs,
                'mobile_power_sources': standard_mps,
                'faults': [
                    {'fault_id': 'DP1', 'type': 'node', 'node': 'N2', 'demand': 6, 'cap': 1},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('N3', 'N23'), 'offset_from': 'N3', 'offset': 4, 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('N28', 'N29'), 'offset_from': 'N28', 'offset': 8, 'demand': 8, 'cap': 1},
                    {'fault_id': 'DP4', 'type': 'node', 'node': 'N9', 'demand': 16, 'cap': 2},
                    {'fault_id': 'DP5', 'type': 'edge', 'edge': ('N12', 'N13'), 'offset_from': 'N12', 'offset': 26, 'demand': 10, 'cap': 2},
                    {'fault_id': 'DP6', 'type': 'edge', 'edge': ('N16', 'N17'), 'offset_from': 'N16', 'offset': 22, 'demand': 6, 'cap': 1},
                ],
            },
        }
        return cases

    def _clean_fault_data(self, faults: List[Dict]) -> List[Dict]:
        """Normalize and drop invalid entries."""
        cleaned: List[Dict] = []
        for f in faults:
            if not f.get('fault_id'):
                continue
            # Validate based on fault type
            fault_type = f.get('type')
            if fault_type == 'node':
                # Node faults must have 'node' field
                if not f.get('node') or str(f.get('node', '')).lower() == 'nan':
                    continue
            elif fault_type == 'edge':
                # Edge faults must have 'edge', 'offset_from', and 'offset' fields
                edge = f.get('edge')
                if not edge or not isinstance(edge, tuple) or len(edge) != 2:
                    continue
                if not f.get('offset_from') or not isinstance(f.get('offset'), (int, float)):
                    continue
            else:
                # Unknown fault type
                continue
            cleaned.append(f)
        return cleaned

    def get_case_config(self, case_name: str) -> Dict[str, Any]:
        """Get complete configuration for a specific case (deep-copied)."""
        if case_name not in self.training_cases:
            raise ValueError(f"Case {case_name} not found. Available cases: {list(self.training_cases.keys())}")

        config = copy.deepcopy(self.system_config)
        case_data = self.training_cases[case_name]

        # Add case-specific RC and MPS configurations
        config['repair_crews'] = case_data['repair_crews']
        config['mobile_power_sources'] = case_data['mobile_power_sources']
        config['faults'] = self._clean_fault_data(case_data['faults'])
        config['case_name'] = case_name

        return config

    def get_all_cases(self) -> List[str]:
        """Get list of all available case names."""
        return list(self.training_cases.keys())

    def get_all_case_names(self) -> List[str]:
        """Alias for get_all_cases() for compatibility."""
        return self.get_all_cases()

    def export_config(self, case_name: str, filepath: Optional[str] = None) -> None:
        """Export configuration for a specific case to JSON file."""
        cfg = self.get_case_config(case_name)
        if filepath is None:
            filepath = f"ieee33_{case_name.lower()}_config.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        print(f"Configuration for {case_name} exported to {filepath}")

    def validate_configuration(self) -> Dict[str, Any]:
        """Validation of configuration structure."""
        res = {
            'nodes': {'total': len(self.system_config['nodes'])},
            'loads': {'total': len(self.system_config['loads'])},
            'edges': {'total': len(self.system_config['edges'])},
            'switches': {'total': len(self.system_config['switches'])},
            'traffic_roads': {'total': len(self.system_config['traffic_roads'])},
            'cases': {'total': len(self.training_cases)},
            'warnings': []
        }

        # Sanity check for switches' connected edges
        all_edge_ids = {e[0] for e in self.system_config['edges']}
        for sid, scfg in self.system_config['switches'].items():
            for eid in scfg.get('connected_edges', []):
                if eid not in all_edge_ids:
                    res['warnings'].append(f"Switch {sid} references missing edge {eid}")

        # Check load node consistency
        load_nodes_in_loads = {ld['node_id'] for ld in self.system_config['loads'].values()}
        load_nodes_in_nodes = {nid for nid, n in self.system_config['nodes'].items() if n['type'] == 'LOAD'}
        if load_nodes_in_loads != load_nodes_in_nodes:
            missing_in_loads = load_nodes_in_nodes - load_nodes_in_loads
            missing_in_nodes = load_nodes_in_loads - load_nodes_in_nodes
            if missing_in_loads:
                res['warnings'].append(f"Nodes marked as LOAD but missing load data: {missing_in_loads}")
            if missing_in_nodes:
                res['warnings'].append(f"Load data for non-LOAD nodes: {missing_in_nodes}")

        return res


if __name__ == "__main__":
    cfg = IEEE33Config()
    print("=== IEEE-33 System Configuration ===")
    print(f"Cases: {cfg.get_all_cases()}")

    val = cfg.validate_configuration()
    print(f"\nValidation Results:")
    print(f"  Nodes: {val['nodes']['total']}")
    print(f"  Loads: {val['loads']['total']}")
    print(f"  Edges: {val['edges']['total']}")
    print(f"  Switches: {val['switches']['total']}")
    print(f"  Traffic Roads: {val['traffic_roads']['total']}")
    print(f"  Cases: {val['cases']['total']}")

    if val['warnings']:
        print(f"\n  Warnings:")
        for w in val['warnings']:
            print(f"    - {w}")
    else:
        print(f"  [OK] No warnings")

    # Export one case to check
    print(f"\nExporting Case1 configuration...")
    cfg.export_config("Case1")
    print("Done!")
