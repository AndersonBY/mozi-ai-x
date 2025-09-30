from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CActiveUnit
from ..situ_interpret import CShipDict


class CShip(CActiveUnit):
    """
    水面舰艇
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        """飞机"""
        super().__init__(guid, mozi_server, situation)
        # 方位类型
        self.bearing_type = 0
        # 方位
        self.bearing = 0
        # 距离（转换为千米）
        self.distance = 0
        # 高低速交替航行
        self.sprint_and_drift = False
        # 以下为 CShip 的属性
        # 类别
        self.category = 0
        # 指挥部
        self.command_post = ""
        # 船舵
        self.rudder = 0
        # 获取作战单元燃油信息
        # 显示燃油信息
        self.fuel_state = ""
        self.type = 0  #
        # 空泡
        self.cavitation = 0
        # 悬停
        self.hover_speed = 0.0
        # 低速
        self.low_speed = 0.0
        # 巡航
        self.cruise_speed = 0.0
        # 军力
        self.military_speed = 0.0
        # 加速
        self.add_force_speed = 0.0
        # 载艇-信息
        # 毁伤
        self.damage_info = 0
        # 武器
        self.weapon_info = 0
        # 弹药库
        self.magazines_info = 0
        # 燃料
        self.fuel_info = 0
        # 状态
        self.status_info = 0
        # 就绪时间
        self.time_to_ready_info = 0
        # 货物类型
        self.cargo_type = None
        # 油门高度-航路点信息
        # 航路点名称至少一个航速指令为0公里/小时,不能估计剩余航行距离/时间/燃油量
        self.way_point_name = 0
        self.can_refuel_or_unrep = 0
        # 补给队列header
        self.show_tanker_header = 0
        # 补给队列明显
        self.show_tanker = 0

        self.dock_aircraft = ""  # 停靠飞机信息
        self.dock_ship = ""  # 停靠舰船信息

        self.var_map = CShipDict.var_map
