from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CTrigger
from ..situ_interpret import CTriggerRandomTimeDict


class CTriggerRandomTime(CTrigger):
    """
    随机时间
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        # 事件触发器描述
        self.description = ""
        # 事件触发器类型
        self.event_trigger_type = 0
        # 当前设置最早最晚时间
        self.current_setting = ""
        # 最早时间的时间戳
        self.earliest_time = None
        # 最晚时间的时间戳
        self.latest_time = None

        self.var_map = CTriggerRandomTimeDict.var_map
