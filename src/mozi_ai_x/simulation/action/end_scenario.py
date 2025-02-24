from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CAction
from ..situ_interpret import CActionEndScenarioDict


class CActionEndScenario(CAction):
    """
    终止想定的事件动作类
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.name = ""
        self.description = ""
        self.var_map = CActionEndScenarioDict.var_map
