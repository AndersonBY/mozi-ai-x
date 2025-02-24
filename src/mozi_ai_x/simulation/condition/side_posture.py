from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CCondition
from ..situ_interpret import CConditionSidePostureDict


class CConditionSidePosture(CCondition):
    """
    判定推演方立场的事件条件
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        # 事件条件描述
        self.description = ""
        # 事件条件类型
        self.event_condition_type = 0
        # 反选
        self.modifier = False
        # 推演方GUID
        self.observer_side_guid = ""
        # 考虑推演方GUID
        self.target_side_guid = ""
        # 推演方关系
        self.target_posture = 0

        self.var_map = CConditionSidePostureDict.var_map
