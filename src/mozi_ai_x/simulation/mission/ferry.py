from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CMission
from ..situ_interpret import CFerryMissionDict


class CFerryMission(CMission):
    """
    转场任务
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 转场任务行为
        self.ferry_mission_behavior = ""
        # 转场飞机数量
        self.flight_size = ""

        self.var_map = CFerryMissionDict.var_map
