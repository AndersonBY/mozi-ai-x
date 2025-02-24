from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CTrigger
from ..situ_interpret import CTriggerUnitDetectedDict


class CTriggerUnitDetected(CTrigger):
    """
    单元被探测到
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        # 事件触发器描述
        self.description = ""
        # 事件触发器类型
        self.event_trigger_type = 0
        # 目标推演方GUID
        self.target_side = ""
        # 目标类型
        self.target_type = 0
        # 目标子类型
        self.target_sub_type = 0
        # 目标等级
        self.specific_unit_class = 0
        # 特殊单元GUID
        self.specific_unit = ""
        # 探测器推演方GUID
        self.detector_side_id = ""
        # 最小等级分类
        self.identification_status = 0

        self.var_map = CTriggerUnitDetectedDict.var_map
