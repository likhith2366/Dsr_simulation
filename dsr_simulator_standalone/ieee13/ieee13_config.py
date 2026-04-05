"""
IEEE-13 Node Distribution System Configuration
================================================

This module defines the complete configuration of the IEEE-13 node
distribution system, including:

System Structure (19 nodes):
  - 1 Grid node (main power source, infinite capacity)
  - 7 BUS nodes (N1, N4, N10, N13, V1, V2, V3 - pure connection points, no load)
  - 9 LOAD nodes (N2, N3, N5, N6, N7, N8, N9, N11, N12)
  - 2 SWITCH nodes (S1: normally closed, S2: normally open)

Electrical Edges (19):
  - Main feeder: Grid->N1->N2
  - Branch 1: N2->N4->N5
  - Branch 2: N2->N6->N7
  - Branch 3: N2->S1->N3->N8->N9
  - Branch 4: N3->N10->{N11, N12}
  - Branch 5 (reconfiguration path): N3->N13->V1->S2->V3->V2->N1
  - S2 normally open, used for network reconfiguration during faults

Traffic Roads (23):
  - 19 parallel to electrical edges (agents can travel along electrical lines)
  - 4 traffic-only shortcuts (N7<->V3, N12<->V1, for fast agent movement)

Load Data (9 loads):
  - Total active power: ~2,200 kW
  - Total weighted power: ~10,440 (sum of W*P)
  - Highest priority: L_N11 (W=10.0)
  - Largest loads: L_N5, L_N9 (P=500kW)
  - Capacitive load: L_N12 (Q=-80kVar)

Training Scenarios (10):
  - Case1~Case10, each with different RC/MPS configurations and fault layouts
  - Supports node faults and edge faults
  - Fault capacity (cap): maximum number of concurrent repair crews
"""

from typing import Dict, List, Any, Tuple
import json
import copy


class IEEE13Config:
    """Configuration for IEEE-13 node system"""

    def __init__(self):
        self.system_config = self._build_system_config()
        self.training_cases = self._build_training_cases()

    # -------------------------
    # System (static) blueprint
    # -------------------------
    def _build_system_config(self) -> Dict[str, Any]:
        """
        Build the IEEE-13 system configuration.
        Notes:
        - Node types:
            GRID: external grid connection (Grid)
            LOAD: node with load (N2, N3, N5, N6, N7, N8, N9, N11, N12)
            BUS: transit/bus node without load (N1, N4, N10, N13, V1, V2, V3)
            SWITCH: sectionalizing/reconfiguration switch node (S1, S2)
        - Length units: km
        - Switch initial states: S1 closed, S2 open
        - Network includes normally-open edges for network reconfiguration
        """

        # Node configuration (19 nodes total)
        nodes = {
            'Grid': {'type': 'GRID'},

            # Bus nodes (no load)
            'N1': {'type': 'BUS'},
            'N4': {'type': 'BUS'},
            'N10': {'type': 'BUS'},
            'N13': {'type': 'BUS'},
            'V1': {'type': 'BUS'},
            'V2': {'type': 'BUS'},
            'V3': {'type': 'BUS'},

            # Switches (S1-S2)
            'S1': {'type': 'SWITCH'},
            'S2': {'type': 'SWITCH'},

            # Load nodes (9 nodes with loads)
            'N2': {'type': 'LOAD'},   # (250, 120, 1)
            'N3': {'type': 'LOAD'},   # (400, 300, 6)
            'N5': {'type': 'LOAD'},   # (500, 300, 5)
            'N6': {'type': 'LOAD'},   # (10, 5, 4)
            'N7': {'type': 'LOAD'},   # (40, 15, 5)
            'N8': {'type': 'LOAD'},   # (150, 70, 2)
            'N9': {'type': 'LOAD'},   # (500, 200, 4)
            'N11': {'type': 'LOAD'},  # (200, 80, 10)
            'N12': {'type': 'LOAD'},  # (150, -80, 5) - capacitive load
        }

        # Load configuration: (P, Q, W) - 9 load nodes
        # IMPORTANT: Load IDs must match format expected by LLM and envs.py regex (L_N\d+)
        loads = {
            'L_N2':  {'node_id': 'N2',  'P': 250, 'Q': 120, 'W': 1.0},
            'L_N3':  {'node_id': 'N3',  'P': 400, 'Q': 300, 'W': 6.0},
            'L_N5':  {'node_id': 'N5',  'P': 500, 'Q': 300, 'W': 5.0},
            'L_N6':  {'node_id': 'N6',  'P': 10,  'Q': 5,   'W': 4.0},
            'L_N7':  {'node_id': 'N7',  'P': 40,  'Q': 15,  'W': 5.0},
            'L_N8':  {'node_id': 'N8',  'P': 150, 'Q': 70,  'W': 2.0},
            'L_N9':  {'node_id': 'N9',  'P': 500, 'Q': 200, 'W': 4.0},
            'L_N11': {'node_id': 'N11', 'P': 200, 'Q': 80,  'W': 10.0},
            'L_N12': {'node_id': 'N12', 'P': 150, 'Q': -80, 'W': 5.0},  # Capacitive load (negative Q)
        }

        # Electrical edges - Format: (edge_id, from_node, to_node, length_km, status)
        # Status: 'Closed' (normally-closed) or 'Opened' (normally-open for reconfiguration)
        edges = [
            # Main feeder from Grid
            ('E_Grid_N1',  'Grid', 'N1', 2, 'Closed'),
            ('E_N1_N2',    'N1',   'N2', 2, 'Closed'),

            # Branch 1: N2->N4->N5
            ('E_N2_N4',    'N2',   'N4', 4, 'Closed'),
            ('E_N4_N5',    'N4',   'N5', 2, 'Closed'),

            # Branch 2: N2->N6->N7
            ('E_N2_N6',    'N2',   'N6', 4, 'Closed'),
            ('E_N6_N7',    'N6',   'N7', 2, 'Closed'),

            # Branch 3: N2->S1->N3->N8->N9
            ('E_N2_S1',    'N2',   'S1', 8, 'Closed'),
            ('E_S1_N3',    'S1',   'N3', 8, 'Closed'),
            ('E_N3_N8',    'N3',   'N8', 2, 'Closed'),
            ('E_N8_N9',    'N8',   'N9', 4, 'Closed'),

            # Branch 4: N3->N10->N12 and N10->N11
            ('E_N3_N10',   'N3',   'N10', 2, 'Closed'),
            ('E_N10_N12',  'N10',  'N12', 2, 'Closed'),
            ('E_N10_N11',  'N10',  'N11', 4, 'Closed'),

            # Branch 5: N3->N13->V1->S2->V3->V2->N1 (reconfiguration path, S2 initially open)
            ('E_N3_N13',   'N3',   'N13', 8, 'Closed'),
            ('E_N13_V1',   'N13',  'V1',  4, 'Closed'),
            ('E_V1_S2',    'V1',   'S2',  4, 'Closed'),
            ('E_S2_V3',    'S2',   'V3',  2, 'Opened'),  # S2 initially open
            ('E_V3_V2',    'V3',   'V2',  2, 'Closed'),
            ('E_V2_N1',    'V2',   'N1',  8, 'Closed'),
        ]

        # Switch configuration: control edges at each switch node
        # Initial states: S1 closed (1), S2 open (0)
        switches = {
            'S1': {
                'node_id': 'S1',
                'connected_edges': ['E_N2_S1', 'E_S1_N3'],
                'initial_state': 'close'
            },
            'S2': {
                'node_id': 'S2',
                'connected_edges': ['E_V1_S2', 'E_S2_V3'],
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
            # Shortcuts for agent movement
            ('TR_N7_V3',   'N7',  'V3', 2),
            ('TR_V3_N7',   'V3',  'N7', 2),
            ('TR_N12_V1',  'N12', 'V1', 4),
            ('TR_V1_N12',  'V1',  'N12', 4),
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
        Build training cases for IEEE-13 system.
        Each case includes:
            - repair_crews: dict with RC configurations (initial_position, speed, resources, efficiency)
            - mobile_power_sources: dict with MPS configuration (initial_position, speed, p_limit, s_limit, energy)
            - faults: list of damage points (type, node/edge, offset_from, offset, demand, cap)

        Note: RC and MPS configurations vary across cases - each case has unique settings.
        """

        cases = {
            'Case1': {
                'repair_crews': {
                    'RC1': {'initial_position': 'N9', 'speed': 3, 'efficiency': 2, 'resources': 12},
                    'RC2': {'initial_position': 'N2', 'speed': 5, 'efficiency': 3, 'resources': 12}
                },
                'mobile_power_sources': {
                    'MPS1': {'initial_position': 'N12', 'speed': 8, 'p_limit': 750.0, 's_limit': 800.0, 'energy': 3500.0},
                    'MPS2': {'initial_position': 'V3', 'speed': 8, 'p_limit': 750.0, 's_limit': 800.0, 'energy': 4000.0}
                },
                'faults': [
                    {'fault_id': 'DP1', 'type': 'node', 'node': 'N5', 'demand': 10, 'cap': 2},
                    {'fault_id': 'DP2', 'type': 'node', 'node': 'S2', 'demand': 4, 'cap': 1},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('N2', 'S1'), 'offset_from': 'S1', 'offset': 3, 'demand': 10, 'cap': 2},
                ],
            },
            'Case2': {
                'repair_crews': {
                    'RC1': {'initial_position': 'N9', 'speed': 2, 'efficiency': 2, 'resources': 10},
                    'RC2': {'initial_position': 'N10', 'speed': 5, 'efficiency': 4, 'resources': 9}
                },
                'mobile_power_sources': {
                    'MPS1': {'initial_position': 'N10', 'speed': 3, 'p_limit': 600.0, 's_limit': 700.0, 'energy': 4000.0},
                    'MPS2': {'initial_position': 'N4', 'speed': 7, 'p_limit': 450.0, 's_limit': 550.0, 'energy': 3000.0}
                },
                'faults': [
                    {'fault_id': 'DP1', 'type': 'edge', 'edge': ('N3', 'S1'), 'offset_from': 'N3', 'offset': 1, 'demand': 3, 'cap': 1},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('N2', 'S1'), 'offset_from': 'N2', 'offset': 6, 'demand': 5, 'cap': 1},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('N1', 'N2'), 'offset_from': 'N2', 'offset': 1, 'demand': 3, 'cap': 1},
                    {'fault_id': 'DP4', 'type': 'edge', 'edge': ('N1', 'V2'), 'offset_from': 'V2', 'offset': 5, 'demand': 4, 'cap': 1},
                    {'fault_id': 'DP5', 'type': 'edge', 'edge': ('N13', 'V1'), 'offset_from': 'N13', 'offset': 2, 'demand': 3, 'cap': 1},
                ],
            },
            'Case3': {
                'repair_crews': {
                    'RC1': {'initial_position': 'N7', 'speed': 5, 'efficiency': 3, 'resources': 12},
                    'RC2': {'initial_position': 'N11', 'speed': 4, 'efficiency': 4, 'resources': 11}
                },
                'mobile_power_sources': {
                    'MPS1': {'initial_position': 'N11', 'speed': 6, 'p_limit': 600.0, 's_limit': 700.0, 'energy': 3500.0},
                    'MPS2': {'initial_position': 'N10', 'speed': 7, 'p_limit': 600.0, 's_limit': 700.0, 'energy': 3500.0}
                },
                'faults': [
                    {'fault_id': 'DP1', 'type': 'node', 'node': 'N12', 'demand': 4, 'cap': 1},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('N2', 'S1'), 'offset_from': 'S1', 'offset': 2, 'demand': 4, 'cap': 1},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('N3', 'S1'), 'offset_from': 'S1', 'offset': 5, 'demand': 5, 'cap': 1},
                    {'fault_id': 'DP4', 'type': 'edge', 'edge': ('N13', 'V1'), 'offset_from': 'N13', 'offset': 3, 'demand': 3, 'cap': 1},
                ],
            },
            'Case4': {
                'repair_crews': {
                    'RC1': {'initial_position': 'N9', 'speed': 2, 'efficiency': 4, 'resources': 10},
                    'RC2': {'initial_position': 'N8', 'speed': 6, 'efficiency': 2, 'resources': 11}
                },
                'mobile_power_sources': {
                    'MPS1': {'initial_position': 'N13', 'speed': 4, 'p_limit': 600.0, 's_limit': 700.0, 'energy': 4000.0},
                    'MPS2': {'initial_position': 'N11', 'speed': 8, 'p_limit': 450.0, 's_limit': 550.0, 'energy': 3000.0}
                },
                'faults': [
                    {'fault_id': 'DP1', 'type': 'node', 'node': 'V3', 'demand': 4, 'cap': 1},
                    {'fault_id': 'DP2', 'type': 'node', 'node': 'N9', 'demand': 3, 'cap': 1},
                    {'fault_id': 'DP3', 'type': 'node', 'node': 'S2', 'demand': 3, 'cap': 1},
                    {'fault_id': 'DP4', 'type': 'edge', 'edge': ('V2', 'V3'), 'offset_from': 'V3', 'offset': 1, 'demand': 4, 'cap': 1},
                    {'fault_id': 'DP5', 'type': 'edge', 'edge': ('N3', 'S1'), 'offset_from': 'S1', 'offset': 5, 'demand': 7, 'cap': 1},
                ],
            },
            'Case5': {
                'repair_crews': {
                    'RC1': {'initial_position': 'N9', 'speed': 2, 'efficiency': 4, 'resources': 10},
                    'RC2': {'initial_position': 'N8', 'speed': 6, 'efficiency': 2, 'resources': 11}
                },
                'mobile_power_sources': {
                    'MPS1': {'initial_position': 'N13', 'speed': 4, 'p_limit': 600.0, 's_limit': 700.0, 'energy': 4000.0},
                    'MPS2': {'initial_position': 'N11', 'speed': 8, 'p_limit': 450.0, 's_limit': 550.0, 'energy': 3000.0}
                },
                'faults': [
                    {'fault_id': 'DP1', 'type': 'node', 'node': 'V3', 'demand': 4, 'cap': 1},
                    {'fault_id': 'DP2', 'type': 'node', 'node': 'N9', 'demand': 3, 'cap': 1},
                    {'fault_id': 'DP3', 'type': 'node', 'node': 'S2', 'demand': 3, 'cap': 1},
                    {'fault_id': 'DP4', 'type': 'edge', 'edge': ('V2', 'V3'), 'offset_from': 'V3', 'offset': 1, 'demand': 4, 'cap': 1},
                    {'fault_id': 'DP5', 'type': 'edge', 'edge': ('N3', 'S1'), 'offset_from': 'S1', 'offset': 5, 'demand': 7, 'cap': 1},
                ],
            },
            'Case6': {
                'repair_crews': {
                    'RC1': {'initial_position': 'N8', 'speed': 3, 'efficiency': 4, 'resources': 13},
                    'RC2': {'initial_position': 'N4', 'speed': 2, 'efficiency': 3, 'resources': 11}
                },
                'mobile_power_sources': {
                    'MPS1': {'initial_position': 'V1', 'speed': 6, 'p_limit': 450.0, 's_limit': 550.0, 'energy': 3500.0},
                    'MPS2': {'initial_position': 'N10', 'speed': 8, 'p_limit': 450.0, 's_limit': 550.0, 'energy': 4000.0}
                },
                'faults': [
                    {'fault_id': 'DP1', 'type': 'edge', 'edge': ('N2', 'S1'), 'offset_from': 'S1', 'offset': 3, 'demand': 5, 'cap': 1},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('N3', 'N8'), 'offset_from': 'N8', 'offset': 1, 'demand': 4, 'cap': 1},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('N1', 'N2'), 'offset_from': 'N2', 'offset': 1, 'demand': 8, 'cap': 2},
                ],
            },
            'Case7': {
                'repair_crews': {
                    'RC1': {'initial_position': 'V3', 'speed': 4, 'efficiency': 4, 'resources': 13},
                    'RC2': {'initial_position': 'N5', 'speed': 4, 'efficiency': 3, 'resources': 10}
                },
                'mobile_power_sources': {
                    'MPS1': {'initial_position': 'N8', 'speed': 7, 'p_limit': 750.0, 's_limit': 800.0, 'energy': 3500.0},
                    'MPS2': {'initial_position': 'N1', 'speed': 8, 'p_limit': 600.0, 's_limit': 700.0, 'energy': 3000.0}
                },
                'faults': [
                    {'fault_id': 'DP1', 'type': 'node', 'node': 'S2', 'demand': 10, 'cap': 2},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('V2', 'V3'), 'offset_from': 'V3', 'offset': 1, 'demand': 10, 'cap': 2},
                ],
            },
            'Case8': {
                'repair_crews': {
                    'RC1': {'initial_position': 'N3', 'speed': 3, 'efficiency': 3, 'resources': 8},
                    'RC2': {'initial_position': 'V3', 'speed': 3, 'efficiency': 2, 'resources': 9}
                },
                'mobile_power_sources': {
                    'MPS1': {'initial_position': 'N4', 'speed': 7, 'p_limit': 450.0, 's_limit': 550.0, 'energy': 3000.0},
                    'MPS2': {'initial_position': 'N1', 'speed': 6, 'p_limit': 750.0, 's_limit': 800.0, 'energy': 3500.0}
                },
                'faults': [
                    {'fault_id': 'DP1', 'type': 'node', 'node': 'S1', 'demand': 4, 'cap': 1},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('N6', 'N7'), 'offset_from': 'N6', 'offset': 1, 'demand': 5, 'cap': 1},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('V2', 'V3'), 'offset_from': 'V3', 'offset': 1, 'demand': 5, 'cap': 1},
                    {'fault_id': 'DP4', 'type': 'edge', 'edge': ('S2', 'V3'), 'offset_from': 'S2', 'offset': 1, 'demand': 3, 'cap': 1},
                ],
            },
            'Case9': {
                'repair_crews': {
                    'RC1': {'initial_position': 'N12', 'speed': 4, 'efficiency': 2, 'resources': 8},
                    'RC2': {'initial_position': 'N2', 'speed': 6, 'efficiency': 2, 'resources': 8}
                },
                'mobile_power_sources': {
                    'MPS1': {'initial_position': 'N3', 'speed': 8, 'p_limit': 600.0, 's_limit': 700.0, 'energy': 3000.0},
                    'MPS2': {'initial_position': 'N2', 'speed': 6, 'p_limit': 750.0, 's_limit': 800.0, 'energy': 3000.0}
                },
                'faults': [
                    {'fault_id': 'DP1', 'type': 'node', 'node': 'V1', 'demand': 5, 'cap': 1},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('N2', 'N4'), 'offset_from': 'N2', 'offset': 2, 'demand': 5, 'cap': 1},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('N3', 'S1'), 'offset_from': 'S1', 'offset': 6, 'demand': 6, 'cap': 1},
                ],
            },
            'Case10': {
                'repair_crews': {
                    'RC1': {'initial_position': 'N13', 'speed': 5, 'efficiency': 3, 'resources': 9},
                    'RC2': {'initial_position': 'V1', 'speed': 4, 'efficiency': 3, 'resources': 12}
                },
                'mobile_power_sources': {
                    'MPS1': {'initial_position': 'N9', 'speed': 6, 'p_limit': 750.0, 's_limit': 800.0, 'energy': 4000.0},
                    'MPS2': {'initial_position': 'N11', 'speed': 6, 'p_limit': 600.0, 's_limit': 700.0, 'energy': 4000.0}
                },
                'faults': [
                    {'fault_id': 'DP1', 'type': 'edge', 'edge': ('N4', 'N5'), 'offset_from': 'N5', 'offset': 1, 'demand': 6, 'cap': 1},
                    {'fault_id': 'DP2', 'type': 'edge', 'edge': ('S2', 'V3'), 'offset_from': 'S2', 'offset': 1, 'demand': 4, 'cap': 1},
                    {'fault_id': 'DP3', 'type': 'edge', 'edge': ('N13', 'V1'), 'offset_from': 'V1', 'offset': 1, 'demand': 6, 'cap': 1},
                    {'fault_id': 'DP4', 'type': 'edge', 'edge': ('S2', 'V1'), 'offset_from': 'V1', 'offset': 1, 'demand': 4, 'cap': 1},
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

    def export_config(self, case_name: str, filepath: str | None = None) -> None:
        """Export configuration for a specific case to JSON file."""
        cfg = self.get_case_config(case_name)
        if filepath is None:
            filepath = f"ieee13_{case_name.lower()}_config.json"
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
    cfg = IEEE13Config()
    print("=== IEEE-13 System Configuration ===")
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
