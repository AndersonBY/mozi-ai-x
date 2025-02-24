from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import MoziServer
    from .situation import CSituation

from .base import Base
from .situ_interpret import CWeaponImpactDict


class CWeaponImpact(Base):
    """
    武器碰撞
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        # 爆炸经度
        self.latitude = 0.0
        # 爆炸纬度
        self.longitude = 0.0
        # 海拔高度
        self.altitude_asl = 0.0
        # 碰撞类型
        self.impact_type = 0

        self.var_map = CWeaponImpactDict.var_map
