from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CActiveUnit
from ..situ_interpret import CSubmarineDict


class CSubmarine(CActiveUnit):
    """
    潜艇
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.bearing_type = {}  # 方位类型
        self.bearing = {}  # 方位
        self.distance = 0.0  # 距离（转换为千米）
        self.sprint_and_drift = False  # 高低速交替航行
        self.ai_targets = {}  # 获取AI对象的目标集合
        self.ai_targets_can_fire_the_target_by_wcs_and_weapon_qty = {}  # 获取活动单元AI对象的每个目标对应显示不同的颜色集合
        self.dock_aircraft = ""  # 载机按钮的文本描述
        self.dock_ship = ""  # 载艇按钮的文本描述
        # 以下为 CSubmarine 的属性
        self.category = {}  # 类型类别
        self.cic = {}  # 指挥部
        self.rudder = {}  # 船舵
        self.pressure_hull = {}  # 船身
        # 获取作战单元燃油信息
        self.fuel_state = ""  # 显示燃油状态
        # 柴油剩余百分比
        self.percentage_diesel = 0.0
        # 电池剩余百分比
        self.percentage_battery = 0.0
        # AIP剩余百分比
        self.percentage_aip = 0.0
        self.type = {}
        self.cavitation = ""
        self.hover_speed = 0.0  # 悬停
        self.low_speed = 0.0  # 低速
        self.cruise_speed = 0.0  # 巡航
        self.military_speed = 0.0  # 军力
        self.add_force_speed = 0.0  # 加速
        self.thermocline_up_depth = 0.0  # 温跃层上
        self.thermocline_down_depth = 0.0  # 温跃层下
        # 载艇-信息
        self.damage_info = ""  # 毁伤
        self.weapon_info = ""  # 武器
        self.magazines_info = ""  # 弹药库
        self.fuel_info = ""  # 燃料
        self.status_info = ""  # 状态
        self.time_to_ready_info = ""  # 就绪时间
        # 油门高度-航路点信息
        self.way_point_name = ""  # 航路点名称

        self.var_map = CSubmarineDict.var_map
