import re
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation
    from ..doctrine import CDoctrine

from .base import CActiveUnit
from ..situ_interpret import CGroupDict
from mozi_ai_x.utils.validator import validate_literal_args, validate_uuid4_args


class CGroup(CActiveUnit):
    """
    编组类
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
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
        # 是否在作战中
        self.operating = False
        # 停靠的单元GUID集合
        self.docked_units = ""
        # 实体的停靠设施(部件)
        # 集合
        self.dock_facilities_component = ""
        # 停靠的飞机的GUID集合
        self.dock_aircrafts = ""
        # 实体的航空设施(部件)
        # 集合
        self.air_facilities_component = ""
        # 实体的通信设备及数据链（部件）
        self.comm_devices = ""
        # 单元搭载武器
        self.unit_weapons = ""
        # 状态
        self.active_unit_status = ""
        # 训练水平
        self.proficiency_level = ""
        # 是否是护卫角色
        self.escort_role = False
        # 当前油门
        self.current_throttle = ""
        # 通讯设备是否断开
        self.comms_online = False
        # 是否视图隔离
        self.isolated_pov_object = False
        # 是否地形跟随
        self.terrain_following = False
        # 是否是领队
        self.regroup_needed = False
        # 是否保持阵位
        self.holding_position = False
        # 是否可自动探测
        self.auto_detectable = False
        # 燃油百分比，作战单元燃油栏第一个进度条的值
        self.fuel_percentage = False
        # 单元的通讯链集合
        self.comm_link = ""
        # 传感器GUID集合
        self.none_mcm_sensors = ""
        # 显示“干扰”或“被干扰”
        self.disturb_state = 0
        # 单元所属多个任务数量
        self.multiple_mission_count = 0
        # 单元所属多个任务guid集合
        self.multiple_mission_guids = ""
        # 弹药库GUID集合
        self.magazines = ""
        # 编组类型
        self.group_type = ""
        # 编组中心点
        self.group_center = ""
        # 编组领队
        self.group_lead = ""
        # 编组所有单元
        self.units_in_group = ""
        # 航路点名称
        self.way_point_name = ""
        # 航路点描述
        self.way_point_description = ""
        # 航路点剩余航行距离描述
        self.way_point_dtg_description = ""
        # 航路点剩余航行时间描述
        self.way_point_ttg_description = ""
        # 航路点需要燃油数描述
        self.way_point_fuel_description = ""
        # 发送队形方案选择的索引
        self.formation_selected_index = ""
        # 发送队形方案详情
        self.formation_formula = ""
        # 载机按钮的文本描述
        self.dock_aircraft = ""
        # 载艇按钮的文本描述
        self.dock_ship = ""

        self.var_map = CGroupDict.var_map

    @property
    def way_point_dtg(self) -> float:
        """航路点剩余航行距离，单位：公里"""
        numbers = re.findall(r"\d+\.?\d*", self.way_point_dtg_description)
        return float(numbers[0]) if numbers else 0.0

    @property
    def way_point_ttg(self) -> int:
        """航路点剩余航行时间，单位：秒"""
        description = self.way_point_ttg_description
        if not description:
            return 0

        total_seconds = 0
        # 尝试匹配小时
        hour_match = re.search(r"(\d+)\s*时", description)
        if hour_match:
            total_seconds += int(hour_match.group(1)) * 3600

        # 尝试匹配分钟
        minute_match = re.search(r"(\d+)\s*分", description)
        if minute_match:
            total_seconds += int(minute_match.group(1)) * 60

        # 尝试匹配秒
        second_match = re.search(r"(\d+)\s*秒", description)
        if second_match:
            total_seconds += int(second_match.group(1))

        # 如果没有找到任何时间单位，尝试将整个字符串作为秒数解析
        if total_seconds == 0:
            numbers = re.findall(r"\d+", description)
            if numbers:
                total_seconds = int(numbers[0])

        return total_seconds

    @property
    def way_point_fuel(self) -> float:
        """航路点需要燃油数，单位：公斤"""
        numbers = re.findall(r"\d+\.?\d*", self.way_point_fuel_description)
        return float(numbers[0]) if numbers else 0.0

    def get_units(self):
        """
        获取编组下单元

        Returns:
            dict: 格式 {unit_guid1:unit_obj_1, unit_guid2:unit_obj_2, ...}
        """
        units_guid = self.units_in_group.split("@")
        units_group = {}
        for guid in units_guid:
            units_group[guid] = self.situation.get_obj_by_guid(guid)
        return units_group

    def get_doctrine(self) -> "CDoctrine | None":
        """
        获取条令

        Returns:
            CDoctrine 对象
        """
        if self.doctrine in self.situation.doctrine_dict:
            doctrine = self.situation.doctrine_dict[self.doctrine]
            doctrine.category = "Group"  # 需求来源：20200331-2/2:Xy
            return doctrine
        return None

    @validate_uuid4_args(["unit_guid"])
    async def add_unit(self, unit_guid: str) -> bool:
        """
        编队添加一个单元

        Args:
            unit_guid(str): 单元guid

        Returns:
            bool, 是否成功
        """
        lua_script = f"ScenEdit_SetUnit({{group='{self.guid}',guid='{unit_guid}'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @validate_uuid4_args(["unit_guid"])
    async def remove_unit(self, unit_guid: str) -> bool:
        """
        将单元移除编组

        Args:
            unit_guid(str): 单元guid

        Returns:
            bool, 是否成功
        """
        response = await self.mozi_server.send_and_recv(f"Hs_RemoveUnitFromGroup('{unit_guid}')")
        return response.lua_success

    async def set_formation_group_lead(self, unit_name: str) -> bool:
        """
        设置编队领队

        Args:
            unit_name(str): 所设领队的单元名称

        Returns:
            bool, 是否成功
        """
        lua_script = f"ScenEdit_SetFormation({{NAME='{unit_name}',SETTOGROUPLEAD='Yes'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @validate_literal_args
    async def set_formation_group_member(
        self, unit_name: str, area_type: Literal["FIXED", "Rotating"], bearing: int, distance: int
    ) -> bool:
        """
        设置编队队形

        Args:
            unit_name(str): 单元名称
            area_type(str): 与领队的空间相对关系的维持模式
            bearing(int): 与领队的相对方位
            distance(int): 与领队的距离 单位海里

        Returns:
            bool, 是否成功
        """
        lua_script = (
            f"ScenEdit_SetFormation({{NAME='{unit_name}', TYPE='{area_type}', BEARING={bearing}, "
            f"DISTANCE={distance}}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @validate_uuid4_args(["unit_guid"])
    async def set_unit_sprint_and_drift(self, unit_guid: str, sprint_and_drift: bool) -> bool:
        """
        控制编队内非领队单元相对于编队是否进行高低速交替航行。

        Args:
            unit_guid(str): 单元guid
            sprint_and_drift(bool): 是否交替航行的状态标识符 'true'-是，'false'-否

        Returns:
            bool, 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_SetUnitSprintAndDrift('{unit_guid}',{str(sprint_and_drift).lower()})"
        )
        return response.lua_success
