"""
Mozi AI X - Asynchronous SDK for Mozi Simulation Platform

Provides asynchronous Python API for interacting with Mozi simulation platform.
"""

__version__ = "0.3.5"

# Core service classes
from .simulation.server import MoziServer, ServerResponse

# Distributed support
from .simulation.server.distributed import MoziProxyServer, MoziProxyClient

# Scenario and situation
from .simulation.scenario import CScenario
from .simulation.situation import CSituation

# Side
from .simulation.side import CSide

# Active units
from .simulation.active_unit import (
    CActiveUnit,
    CAircraft,
    CShip,
    CSubmarine,
    CFacility,
    CSatellite,
    CGroup,
)

# Missions
from .simulation.mission import (
    CPatrolMission,
    CStrikeMission,
    CSupportMission,
    CCargoMission,
    CFerryMission,
    CMiningMission,
    CMineClearingMission,
)

# Zones
from .simulation.zone import CNoNavZone, CExclusionZone

# Reference point
from .simulation.reference_point import CReferencePoint

# Contact
from .simulation.contact import CContact

# Doctrine
from .simulation.doctrine import CDoctrine

# Weather
from .simulation.weather import CWeather

__all__ = [
    # Version
    "__version__",
    # Core services
    "MoziServer",
    "ServerResponse",
    # Distributed
    "MoziProxyServer",
    "MoziProxyClient",
    # Scenario
    "CScenario",
    "CSituation",
    # Side
    "CSide",
    # Active units
    "CActiveUnit",
    "CAircraft",
    "CShip",
    "CSubmarine",
    "CFacility",
    "CSatellite",
    "CGroup",
    # Missions
    "CPatrolMission",
    "CStrikeMission",
    "CSupportMission",
    "CCargoMission",
    "CFerryMission",
    "CMiningMission",
    "CMineClearingMission",
    # Zones
    "CNoNavZone",
    "CExclusionZone",
    # Others
    "CReferencePoint",
    "CContact",
    "CDoctrine",
    "CWeather",
]
