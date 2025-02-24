from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CCondition
from ..situ_interpret import CConditionLuaScriptDict


class CConditionLuaScript(CCondition):
    """
    运行lua脚本的事件条件
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.name = ""
        self.description = ""
        self.event_condition_type = 0
        self.lua_script = ""

        self.var_map = CConditionLuaScriptDict.var_map
