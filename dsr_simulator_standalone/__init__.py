"""
DSR Simulator (Distribution System Restoration Simulator)
Distribution System Restoration Simulator - Standalone Package

This package provides DSR simulation environments for two distribution systems:
- IEEE-13 Bus System: 19 nodes, 9 loads, 2 switches (small-scale, fast testing)
- IEEE-33 Bus System: 45 nodes, 31 loads, 10 switches (standard-scale, with power flow calculation)

Modeled entities:
- Repair Crews (RC): Repair crews that move to fault locations to perform repairs
- Mobile Power Sources (MPS): Mobile power sources that temporarily supply power to de-energized loads
- Damage Points (DP): Fault locations that require RC to repair
- Loads: Load nodes with active power / reactive power / priority weight
- Switches: Switches used for network reconfiguration

Usage (IEEE-13):
    from dsr_simulator_standalone import DSRSimulator13, IEEE13Config
    sim = DSRSimulator13()
    sim.setup_case('Case1')
    sim.setup_ieee13_scenario()
    state = sim.get_current_state()

Usage (IEEE-33):
    from dsr_simulator_standalone import DSRSimulator33, IEEE33Config
    sim = DSRSimulator33()
    sim.setup_case('Case1')
    sim.setup_ieee33_scenario()
    state = sim.get_current_state()
"""

# IEEE-13 System
from .ieee13.ieee13_interface import IndependentIEEE13DSRInterface as DSRSimulator13
from .ieee13.ieee13_config import IEEE13Config

# IEEE-33 System
from .ieee33.ieee33_interface import IndependentIEEE33DSRInterface as DSRSimulator33
from .ieee33.ieee33_config import IEEE33Config

# Backward compatibility: DSRSimulator defaults to IEEE-13
DSRSimulator = DSRSimulator13

__all__ = [
    'DSRSimulator',     # Default IEEE-13 (backward compatible)
    'DSRSimulator13',   # IEEE-13 System
    'DSRSimulator33',   # IEEE-33 System
    'IEEE13Config',
    'IEEE33Config',
]
