from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CAction
from ..situ_interpret import CActionPointsDict


class CActionPoints(CAction):
    """
    设置得分的事件动作类
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.name = ""
        self.description = ""
        self.side_guid = ""  # 推演方GUID
        self.point_change = 0  # 变化评分

        self.var_map = CActionPointsDict.var_map
