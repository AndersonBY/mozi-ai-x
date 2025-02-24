from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import MoziServer
    from .situation import CSituation

from .base import Base
from .situ_interpret import CReferencePointDict


class CReferencePoint(Base):
    """
    参考点
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.name = ""
        # 方
        self.side = ""
        # 经度
        self.longitude = 0.0
        # 纬度
        self.latitude = 0.0
        # 高度
        self.altitude = 0.0
        # 相对单元guid
        self.relative_to_unit = ""
        # 相对方位角
        self.relative_bearing = 0.0
        # 相对距离
        self.relative_distance = 0.0
        # 方向类型
        # 0 固定的，不随领队朝向变化而变化
        # 1 旋转的，随领队朝向改变旋转
        self.bearing_type = 0
        # 是否锁定
        self.locked = False

        self.var_map = CReferencePointDict.var_map

    async def set_reference_point(self, new_coord: tuple[float, float]) -> bool:
        """
        设置参考点的位置

        Args:
            new_coord (tuple[float, float]): 新的经纬度位置 (lat, lon)

        Returns:
            bool: 执行结果
        """
        set_str = f"ScenEdit_SetReferencePoint({{side='{self.side}',guid='{self.guid}', lat={new_coord[0]}, lon={new_coord[1]}}})"
        response = await self.mozi_server.send_and_recv(set_str)
        return response.lua_success
