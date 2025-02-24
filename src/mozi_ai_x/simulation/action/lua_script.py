from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CAction
from ..situ_interpret import CActionLuaScriptDict


class CActionLuaScript(CAction):
    """
    运行lua脚本的事件动作类
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.name = ""
        self.description = ""
        self.lua_script = ""

        self.var_map = CActionLuaScriptDict.var_map
