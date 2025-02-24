from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CTrigger
from ..situ_interpret import CTriggerUnitDestroyedDict


class CTriggerUnitDestroyed(CTrigger):
    """
    单元被摧毁
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        # 事件触发器描述CTriggerUnitDetected
        self.description = ""
        # 事件触发器类型
        self.event_trigger_type = ""
        # 目标推演方GUID
        self.target_side = ""
        # 目标类型
        self.target_type = ""
        # 目标子类型
        self.target_subtype = ""
        # 目标等级
        self.specific_unit_class = ""
        # 特殊单元GUID
        self.specific_unit = ""

        self.var_map = CTriggerUnitDestroyedDict.var_map
