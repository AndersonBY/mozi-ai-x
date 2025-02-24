from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CZone
from ..situ_interpret import CExclusionZoneDict


class CExclusionZone(CZone):
    """
    封锁区
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        # 所属推演方GUID
        self.side = ""
        # 区域描述
        self.description = ""
        # 区域的参考点集
        self.area_ref_point_list = ""
        # 单元类型集合
        self.affected_unit_types = ""
        # 是否启用
        self.active = False
        # 推演方立场
        self.mark_violator_as = ""

        self.var_map = CExclusionZoneDict.var_map
