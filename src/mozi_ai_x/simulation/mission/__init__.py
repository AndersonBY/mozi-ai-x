from typing import Union

from .patrol import CPatrolMission
from .strike import CStrikeMission
from .support import CSupportMission
from .cargo import CCargoMission
from .ferry import CFerryMission
from .mining import CMiningMission
from .mine_clearing import CMineClearingMission


MissionTypes = Union[
    CPatrolMission, CStrikeMission, CSupportMission, CCargoMission, CFerryMission, CMiningMission, CMineClearingMission
]


__all__ = [
    "MissionTypes",
    "CPatrolMission",
    "CStrikeMission",
    "CSupportMission",
    "CCargoMission",
    "CFerryMission",
    "CMiningMission",
    "CMineClearingMission",
]
