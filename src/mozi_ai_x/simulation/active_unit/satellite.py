from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CActiveUnit
from ..situ_interpret import CSatelliteDict


class CSatellite(CActiveUnit):
    """
    卫星类
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 卫星类别
        self.satellite_category = None
        # 卫星航迹线 航迹是根据卫星算法得出的
        self.tracks_points = ""

        self.var_map = CSatelliteDict.var_map
