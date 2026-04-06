"""
Fault Discovery Manager
=======================
Tracks which faults are hidden vs discovered.

At episode start:
  - All faults are HIDDEN (not visible in state)

When Scout or RC visits a node/edge:
  - System checks if any hidden fault is there
  - If yes → fault becomes DISCOVERED
  - Discovered faults appear in state
  - RCs can now be assigned to them

RC decision logic when discovering a fault:
  - Has enough resources AND at fault location → repair immediately
  - Not enough resources OR busy → report only, Scout/system decides next
"""

from typing import Dict, List, Optional, Set


class FaultDiscoveryManager:
    """
    Manages the hidden/discovered state of all faults.
    Acts as the ground truth for fault locations.
    """

    def __init__(self):
        self.hidden_faults: Dict[str, Dict] = {}       # fault_id → fault info (not visible to agents)
        self.discovered_faults: Dict[str, Dict] = {}   # fault_id → fault info (visible to agents)
        self.visited_nodes: Set[str] = set()           # all nodes visited by any agent
        self.visited_edges: Set[str] = set()           # all edges traversed by any agent
        self.discovery_log: List[Dict] = []            # history of discoveries

    def load_faults(self, faults: List[Dict]):
        """
        Load all faults at episode start and HIDE them.
        faults = list of fault dicts from ieee13/ieee33 config
        """
        self.hidden_faults = {}
        self.discovered_faults = {}
        self.visited_nodes = set()
        self.visited_edges = set()
        self.discovery_log = []

        for fault in faults:
            fault_id = fault['fault_id']
            self.hidden_faults[fault_id] = {
                'fault_id': fault_id,
                'type': fault['type'],                          # 'node' or 'edge'
                'node': fault.get('node'),                      # for node faults
                'edge': fault.get('edge'),                      # for edge faults (tuple)
                'offset_from': fault.get('offset_from'),
                'offset': fault.get('offset'),
                'demand': fault['demand'],
                'cap': fault['cap'],
                'discovered': False
            }

    def visit_node(self, node_id: str, agent_id: str, agent_type: str) -> List[Dict]:
        """
        Called when any agent (Scout or RC) arrives at a node.
        Checks if any hidden fault is at this node.
        Returns list of newly discovered faults.
        """
        self.visited_nodes.add(node_id)
        newly_discovered = []

        for fault_id, fault in list(self.hidden_faults.items()):
            if fault['type'] == 'node' and fault['node'] == node_id:
                # Found a hidden node fault
                discovered = self._discover_fault(fault_id, agent_id, agent_type, node_id)
                newly_discovered.append(discovered)

        return newly_discovered

    def visit_edge(self, from_node: str, to_node: str, agent_id: str, agent_type: str) -> List[Dict]:
        """
        Called when any agent travels along an edge.
        Checks if any hidden fault is on this edge.
        Returns list of newly discovered faults.
        """
        edge_key = tuple(sorted([from_node, to_node]))
        self.visited_edges.add(str(edge_key))
        newly_discovered = []

        for fault_id, fault in list(self.hidden_faults.items()):
            if fault['type'] == 'edge':
                fault_edge = tuple(sorted(fault['edge']))
                if fault_edge == edge_key:
                    # Found a hidden edge fault
                    discovered = self._discover_fault(fault_id, agent_id, agent_type, f"{from_node}-{to_node}")
                    newly_discovered.append(discovered)

        return newly_discovered

    def _discover_fault(self, fault_id: str, agent_id: str, agent_type: str, location: str) -> Dict:
        """Move fault from hidden to discovered."""
        fault = self.hidden_faults.pop(fault_id)
        fault['discovered'] = True
        fault['discovered_by'] = agent_id
        fault['discovered_by_type'] = agent_type   # 'scout' or 'rc'
        fault['discovered_at'] = location

        self.discovered_faults[fault_id] = fault

        log_entry = {
            'fault_id': fault_id,
            'discovered_by': agent_id,
            'agent_type': agent_type,
            'location': location,
            'fault_type': fault['type']
        }
        self.discovery_log.append(log_entry)

        print(f"  [DISCOVERY] {agent_type} {agent_id} found {fault_id} at {location}!")
        return fault

    def check_rc_can_repair(self, rc_state: Dict, fault_id: str) -> bool:
        """
        Check if an RC is capable of repairing a discovered fault.
        RC is capable if:
          - Fault is discovered
          - RC has remaining resources > 0
          - RC is at the fault location
        """
        if fault_id not in self.discovered_faults:
            return False

        fault = self.discovered_faults[fault_id]
        rc_resources = rc_state.get('remaining_resources', 0)
        rc_position = rc_state.get('current_position', '')

        # Check resources
        if rc_resources <= 0:
            return False

        # Check if RC is at fault location
        if fault['type'] == 'node':
            return rc_position == fault['node']
        else:
            # Edge fault - RC must be at the fault node position
            return rc_position == fault.get('offset_from') or rc_position in fault.get('edge', ())

    def get_unvisited_nodes(self, all_nodes: List[str]) -> List[str]:
        """Return nodes that haven't been visited yet."""
        return [n for n in all_nodes if n not in self.visited_nodes]

    def get_observable_faults(self) -> Dict:
        """Return only discovered faults (what agents can see)."""
        return dict(self.discovered_faults)

    def all_faults_discovered(self) -> bool:
        """True when all faults have been found."""
        return len(self.hidden_faults) == 0

    def get_summary(self) -> Dict:
        """Summary of discovery state."""
        return {
            'total_faults': len(self.hidden_faults) + len(self.discovered_faults),
            'hidden': len(self.hidden_faults),
            'discovered': len(self.discovered_faults),
            'visited_nodes': len(self.visited_nodes),
            'discovery_log': self.discovery_log
        }

    def __repr__(self):
        return (f"FaultDiscovery(hidden={len(self.hidden_faults)}, "
                f"discovered={len(self.discovered_faults)}, "
                f"visited_nodes={len(self.visited_nodes)})")
