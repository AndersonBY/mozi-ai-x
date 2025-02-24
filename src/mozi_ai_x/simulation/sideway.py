from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import MoziServer
    from .situation import CSituation

from .base import Base
from .situ_interpret import CSideWayDict


class CSideWay(Base):
    """
    预设航线类
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        # 推演方的GUID
        self.side = ""
        # 是否显示航线
        self.show = False
        # 航线类型
        self.side_way_type = 0
        # 所有航路点的集合
        self.way_points = ""

        self.var_map = CSideWayDict.var_map
