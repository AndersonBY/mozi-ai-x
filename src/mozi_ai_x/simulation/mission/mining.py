from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CMission
from ..situ_interpret import CMiningMissionDict


class CMiningMission(CMission):
    """
    布雷任务
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.var_map = CMiningMissionDict.var_map
