from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CAction
from ..situ_interpret import CActionChangeMissionStatusDict


class CActionChangeMissionStatus(CAction):
    """
    改变任务状态的事件动作类
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.name = ""
        self.description = ""
        self.side_guid = ""  # 推演方GUID
        self.mission_id = ""  # 任务GUID
        self.new_mission_status = 0  # 是否启动

        self.var_map = CActionChangeMissionStatusDict.var_map
