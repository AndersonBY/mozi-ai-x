from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CActiveUnit
from ..situ_interpret import CFacilityDict


class CFacility(CActiveUnit):
    """地面设施"""

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 方位类型
        self.bearing_type = 0
        # 方位
        self.bearing = 0.0
        # 距离（千米）
        self.distance = 0.0
        # 是否高速交替航行
        self.sprint_and_drift = False
        # 载机按钮的文本描述
        self.dock_aircraft = ""
        # 类别
        self.category = 0
        # 悬停
        self.hover_speed = 0.0
        # 低速
        self.low_speed = 0.0
        # 巡航
        self.cruise_speed = 0.0
        # 军力
        self.military_speed = 0.0
        # 载艇按钮的文本描述
        self.dock_ship = ""
        self.command_post = ""
        # 加油队列明细
        self.show_tanker = ""

        self.var_map = CFacilityDict.var_map

    def get_summary_info(self):
        """
        获取精简信息, 提炼信息进行决策

        Returns:
            dict: 精简信息
        """
        info_dict = {
            "guid": self.guid,
            "db_id": self.db_id,
            "subtype": str(self.category),
            "facility_type_id": "",
            "name": self.name,
            "side": self.side,
            "proficiency": self.proficiency_level,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude_agl,
            "altitude_asl": self.altitude_asl,
            "course": self.get_way_points_info(),
            "heading": self.current_heading,
            "speed": self.current_speed,
            "throttle": self.current_throttle,
            "autodetectable": self.auto_detectable,
            "unitstate": self.active_unit_status,
            "fuelstate": "",
            "weaponstate": -1,
            "mounts": self.get_mounts(),
            "type": "Facility",
            "fuel": 0,
            "damage": self.damage_state,
            "sensors": self.get_sensors(),
            "weapons_valid": self.get_weapon_infos(),
        }
        return info_dict
