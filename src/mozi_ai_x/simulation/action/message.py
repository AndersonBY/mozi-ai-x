from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CAction
from ..situ_interpret import CActionMessageDict


class CActionMessage(CAction):
    """
    发布消息的事件动作类
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.name = ""
        self.description = ""
        self.side_guid = ""
        self.message_text = ""

        self.var_map = CActionMessageDict.var_map
