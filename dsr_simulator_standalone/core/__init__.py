"""
DSR Core Module - Core Simulation Logic
========================================

Core components of the DSR simulator:
- agents.py:         Agent entity classes (RC, MPS, DP, Load, Switch)
                     Agent entity classes (Repair Crew, Mobile Power Source, Damage Point, Load, Switch)
- agent_manager.py:  Instance-based agent state management
                     Instance-based agent state manager
- graphs.py:         Dual graph model (TGraph for routing, EGraph for power flow)
                     Dual graph model (Traffic graph for routing, Electrical graph for power flow/connectivity analysis)
- environment.py:    Environment state management and simulation stepping
                     Environment state management and simulation advancement
- dsr_interface.py:  Main DSR interface orchestrating all operations
                     Main DSR interface, orchestrating all operations
"""

from .agents import RC, MPS, DP, Load, Switch
from .agent_manager import AgentManager
from .graphs import TGraph, EGraph, NodeType
from .environment import IndependentDSREnvironment
from .dsr_interface import IndependentDSRInterface

__all__ = [
    'RC', 'MPS', 'DP', 'Load', 'Switch',
    'AgentManager',
    'TGraph', 'EGraph', 'NodeType',
    'IndependentDSREnvironment',
    'IndependentDSRInterface',
]
