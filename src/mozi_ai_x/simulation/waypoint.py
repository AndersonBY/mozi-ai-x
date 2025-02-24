from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import MoziServer
    from .situation import CSituation

from .base import Base
from .situ_interpret import CWayPointDict


class CWayPoint(Base):
    """
    航路点
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 对象名
        self.name = ""
        # 经度
        self.longitude = 0.0
        # 纬度
        self.latitude = 0.0
        # 高度
        self.altitude = 0.0
        # 上一级单元guid
        self.active_unit = ""
        # 路径点类型
        self.waypoint_type = 0
        # 枚举类-进气道压力
        self.throttle_preset = 0
        # 高空压力
        self.altitude_preset = 0
        # 深潜压力
        self.depth_preset = 0
        # 是否采用地形跟随
        self.terrain_following = False
        # 作战条令
        self.doctrine = ""
        # 雷达状态
        self.radar_state = 0
        # 声纳状态
        self.sonar_state = 0
        # 电磁干扰状态
        self.ecm_state = 0
        # 航路点描述
        self.description = ""
        # 航路点剩余航行距离
        self.waypoint_dtg = ""
        # 航路点剩余航行时间
        self.waypoint_ttg = ""
        # 航路点需要燃油数
        self.waypoint_fuel = ""
        # 航路点名称
        self.waypoint_name = ""
        # 预期速度
        self.desired_speed = 0.0
        # 预期高度
        self.desired_altitude = 0.0
        # 温跃层上
        self.thermocline_up_depth = 0
        # 温跃层下
        self.thermocline_down_depth = 0

        self.var_map = CWayPointDict.var_map
