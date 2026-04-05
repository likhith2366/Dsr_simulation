"""
IEEE-13 Bus System Module
=========================

Provides IEEE-13 node test system configuration and interface:
- ieee13_config.py:    System topology, load data, and 10 training cases
- ieee13_interface.py: IEEE-13 specific wrapper around DSR core interface

System Overview:
- 19 nodes: 1 Grid + 7 BUS + 9 LOAD + 2 SWITCH
- 19 electrical edges + 4 traffic-only roads
- 9 loads with priority weights (W): L_N2 to L_N12
- 2 switches: S1 (normally closed), S2 (normally open)
- 10 training cases (Case1 ~ Case10) with varying fault scenarios
"""

from .ieee13_config import IEEE13Config
from .ieee13_interface import IndependentIEEE13DSRInterface

__all__ = ['IEEE13Config', 'IndependentIEEE13DSRInterface']
