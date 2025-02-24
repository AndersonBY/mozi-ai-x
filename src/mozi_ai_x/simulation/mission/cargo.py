from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CMission
from ..situ_interpret import CCargoMissionDict


class CCargoMission(CMission):
    """
    投送任务
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 母舰平台
        self.motherships = ""
        # 要卸载的货物
        self.mounts_to_unload = ""

        self.var_map = CCargoMissionDict.var_map
