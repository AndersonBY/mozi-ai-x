from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CTrigger
from ..situ_interpret import CTriggerRegularTimeDict


class CTriggerRegularTime(CTrigger):
    """
    规则时间
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        # 事件触发器描述
        self.description = ""
        # 事件触发器类型
        self.event_trigger_type = 0
        # 触发器每几秒将会触发
        self.interval = 0

        self.var_map = CTriggerRegularTimeDict.var_map
