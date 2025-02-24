from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CTrigger
from ..situ_interpret import CTriggerPointsDict


class CTriggerPoints(CTrigger):
    """
    推演方得分
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        # 事件触发器描述
        self.description = ""
        # 事件触发器类型
        self.event_trigger_type = 0
        # 推演方的GUID
        self.side_guid = ""
        # 得分类型
        self.reach_direction = 0
        # 得分
        self.point_value = 0

        self.var_map = CTriggerPointsDict.var_map
