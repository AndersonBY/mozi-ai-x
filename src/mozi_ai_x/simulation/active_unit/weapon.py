from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .base import CActiveUnit
from ..situ_interpret import CWeaponDict
from mozi_ai_x.utils.validator import validate_uuid4_args


class CWeapon(CActiveUnit):
    """武器"""

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 提供数据链的活动单元
        self.data_link_parent_guid = ""
        # 主要目标
        self.primary_target_guid = ""
        # 反潜模式使用时最小作用距离
        self.range_asw_min = 0.0
        # 反潜模式使用时最大作用距离
        self.rage_asw_max = 0.0
        # 最小射程
        self.range_land_min = 0.0
        # 最大射程
        self.range_land_max = 0.0
        # 反舰模式使用时最小距离
        self.range_asuw_min = 0.0
        # 反舰模式使用时最大距离
        self.range_asuw_max = 0.0
        # 防空作战最小大作用距离
        self.range_aaw_min = 0.0
        # 防空作战最大作用距离
        self.range_aaw_max = 0.0
        # 武器类型
        self.weapon_type = 0
        # 打击的目标类型
        self.weapon_target_type = ""
        # 是否是空射制导武器
        self.is_of_air_launched_guided_weapon = False
        # 是否是主动声纳
        self.sonobuoy_active = False
        # 发射单元GUID
        self.firing_unit_guid = ""
        # 父挂架
        self.parent_mount = ""
        # 父弹药库
        self.parent_magazine = ""
        # 声呐深度设置
        self.sonobuoy_depth_setting = 0
        # 如果是声纳浮标则发送它的剩余时间
        self.sonobuoy_remaining_time = ""

        self.var_map = CWeaponDict.var_map

    def delete_sub_object(self):
        """
        删除时删除子对象

        Returns:
            list: 删除的子对象列表
        """
        del_list = []
        if self.doctrine is not None:
            del_list.append(self.doctrine.guid)
            del self.doctrine

        del_list.extend(self.way_points.keys())
        del self.way_points
        del_list.extend(list(self.sensors.keys()))
        del self.sensors
        return del_list

    def get_summary_info(self) -> dict:
        """
        获取精简信息, 提炼信息进行决策

        Returns:
            dict
        """
        info_dict = {
            "guid": self.guid,
            "db_id": self.db_id,
            "subtype": "0",
            "facility_type_id": "",
            "name": self.name,
            "side": self.name,
            "proficiency": "",
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude_agl,
            "course": self.get_way_points_info(),
            "heading": self.current_heading,
            "speed": self.current_speed,
            "throttle": self.current_throttle,
            "autodetectable": self.auto_detectable,
            "unitstate": self.active_unit_status,
            "fuelstate": "",
            "weaponstate": -1,
            "mounts": self.get_mounts(),
            "target": self.primary_target_guid,
            "shooter": self.firing_unit_guid,
            "type": "Weapon",
            "fuel": -1,
            "damage": -1,
            "sensors": self.get_sensor(),
            "weapons_valid": self.get_weapon_infos(),
        }
        return info_dict

    @validate_uuid4_args(["target_guid"])
    async def unit_target_sim_break_off(self, type: str, side: str, target_guid: str, distance: float) -> bool:
        """
        武器距离目标多少公里后暂停

        Args:
            type(str): 类型
            side(str): 推演方
            target_guid(str): 目标guid
            distance(float): 距离（公里） complate

        Returns:
            bool
        """
        lua_script = (
            f"Hs_WeaponTargetSimBreakOff('{type}', {{SIDE = '{side}', CONTACTGUID = '{target_guid}', "
            f"ACTIVEUNITGUID = '{self.guid}', DISTANCE = {distance}}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @validate_uuid4_args(["active_unit_guid"])
    async def clear_weapon_way(self, active_unit_guid: str) -> bool:
        """
        清空手动攻击时武器的航路点。

        Args:
            active_unit_guid(str): GUID

        Returns:
            bool
        """
        response = await self.mozi_server.send_and_recv(f"Hs_ClearWeaponWay('{active_unit_guid}','{self.guid}')")
        return response.lua_success

    @validate_uuid4_args(["active_unit_guid", "contact_guid"])
    async def set_weapon_way(
        self, active_unit_guid: str, contact_guid: str, latitude: float, longitude: float
    ) -> bool:
        """
        对可设置航路的武器在手动攻击时绘制武器的航线。

        Args:
            active_unit_guid(str): 单元 GUID
            contact_guid(str): 目标 GUID
            latitude(float): 纬度
            longitude(float): 经度

        Returns:
            bool
        """
        lua_script = f"Hs_SetWeaponWay('{active_unit_guid}','{self.guid}','{contact_guid}',{longitude},{latitude})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success
