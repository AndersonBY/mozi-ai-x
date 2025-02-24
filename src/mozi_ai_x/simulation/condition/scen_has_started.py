from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CCondition
from ..situ_interpret import CConditionScenHasStartedDict


class CConditionScenHasStarted(CCondition):
    """
    判定想定启动的事件条件
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.name = ""
        self.description = ""
        self.event_condition_type = 0
        self.modifier = False

        self.var_map = CConditionScenHasStartedDict.var_map
