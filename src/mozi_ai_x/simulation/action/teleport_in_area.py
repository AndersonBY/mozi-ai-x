from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CAction
from ..situ_interpret import CActionTeleportInAreaDict


class CActionTeleportInArea(CAction):
    """
    瞬间移动的事件动作类
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.name = ""
        self.description = ""
        self.event_action_type = 0
        self.unit_ids = ""  # 要瞬间移动的目标
        self.reference_point = ""  # 区域

        self.var_map = CActionTeleportInAreaDict.var_map
