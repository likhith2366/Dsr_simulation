"""
IEEE-33 Bus System Module
=========================

Provides IEEE-33 node test system configuration and interface:
- ieee33_config.py:    System topology, load data, and 10 training cases
- ieee33_interface.py: IEEE-33 specific wrapper around DSR core interface
- core/:               IEEE-33 specific core engine

System Overview:
- 45 nodes: 1 Grid + 3 BUS + 31 LOAD + 10 SWITCH
- 39 normally-closed electrical edges + 10 normally-open tie lines
- 31 loads with priority weights (W): L_N3 to L_N33
- 10 switches: S1-S5 (normally closed), S6-S10 (normally open)
- 10 training cases (Case1 ~ Case10) with varying fault scenarios

Key differences from IEEE-13:
- Larger scale (45 nodes vs 19 nodes, 31 loads vs 9 loads)
- 10 switches (vs 2), more complex network reconfiguration options
- Monotonic load restoration semantics (once restored, loads will not be de-energized)
"""

from .ieee33_config import IEEE33Config
from .ieee33_interface import IndependentIEEE33DSRInterface

__all__ = ['IEEE33Config', 'IndependentIEEE33DSRInterface']
