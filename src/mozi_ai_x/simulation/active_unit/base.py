from typing import TYPE_CHECKING, Literal, Any, Iterable

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation
    from ..contact import CContact
    from ..side import CSide
    from .group import CGroup
    from .submarine import CSubmarine
    from .ship import CShip
    from .facility import CFacility
    from .aircraft import CAircraft
    from .satellite import CSatellite
    from ..doctrine import CDoctrine
    from ..mount import CMount
    from ..loadout import CLoadout
    from ..magazine import CMagazine
    from ..sensor import CSensor

from ..base import Base
from ...utils.log import mprint_with_name
from mozi_ai_x.utils.validator import validate_literal_args, validate_uuid4_args


mprint = mprint_with_name("ActiveUnit")


class CActiveUnit(Base):
    """
    活动单元（潜艇、水面舰艇、地面兵力及设施、飞机、卫星、离开平台射向目标的武器，不包含目标、传感器等）的父类
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 活动单元传感器列表
        self.sensors = {}
        # 活动单元挂架
        self._mounts = {}
        # 活动单元挂载
        self.loadout = {}
        # 挂载方案的GUid
        self.loadout_guid = ""
        # 活动单元弹药库
        self._magazines = {}
        # 航路点
        self.way_points = {}
        # 名称
        self.name = ""
        # 地理高度
        self.altitude_agl = 0.0
        # 海拔高度
        self.altitude_asl = 0
        # 所在推演方ID
        self.side = ""
        # 单元类别
        self.unit_class = ""
        # 当前纬度
        self.latitude = 0.0
        # 当前经度
        self.longitude = 0.0
        # 当前高度
        self.altitude = 0.0
        # 当前朝向
        self.current_heading = 0.0
        # 当前速度
        self.current_speed = 0.0
        # 当前海拔高度
        self.current_altitude_asl = 0.0
        # 倾斜角
        self.pitch = 0.0
        # 翻转角
        self.roll = 0.0
        # 获取期望速度
        self.desired_speed = 0.0
        # 获取最大油门
        self.max_throttle = 0
        # 最大速度
        self.max_speed = 0.0
        # 最小速度
        self.min_speed = 0.0
        # 最大高度
        self.max_altitude = 0.0
        # 最小高度
        self.min_altitude = 0.0
        # 军标ID
        self.icon_type = ""
        # 普通军标
        self.common_icon = ""
        # 数据库ID
        self.db_id = 0
        # 作战中
        self.operating = False
        # 编组ID
        self.parent_group = ""
        # 停靠的设施的ID(关系)
        self.docked_units = ""
        # 单元的停靠设施(部件)
        self.dock_facilities_component = ""
        # 停靠的飞机的ID(关系)
        self.dock_aircrafts = ""
        # 单元的航空设施(部件)
        self.air_facilities_component = ""
        # 单元的通信设备及数据链(部件)
        self.comm_devices = ""
        # 单元的引擎(部件)
        self.engines = ""
        # 传感器，需要构建对象类,所以只传ID
        self.sensor_guids = ""
        # 挂架
        self.mounts = ""
        # 毁伤状态
        self.damage_state = ""
        # 失火
        self.fire_intensity_level = 0
        # 进水
        self.flooding_intensity_level = 0
        # 分配的任务
        self.assigned_mission = ""
        # 作战条令
        self.doctrine: "CDoctrine | None" = None
        # 系统右栏->对象信息->作战单元武器
        self.unit_weapons = ""
        # 路径点
        self._way_points = ""
        # 训练水平
        self.proficiency_level = 0
        # 是否是护卫角色
        self.escort_role = False
        # 当前油门
        self.current_throttle = 0
        # 通讯设备是否断开
        self.comms_on_line = False
        self.isolated_pov_object = False
        # 地形跟随
        self.terrain_following = False
        self.regroup_needed = False
        # 保持阵位
        self.holding_position = False
        # 是否可自动探测
        self.auto_detectable = False
        # 当前货物
        self.cargo = ""
        # 燃油百分比，作战单元燃油栏第一个进度条的值
        self.fuel_percentage = 0.0
        # 获取AI对象的目标集合# 获取活动单元AI对象的每个目标对应显示不同的颜色集合
        self.ai_targets = ""
        # 获取活动单元AI对象的每个目标对应显示不同的颜色集合
        self.ai_targets_can_fire_target_by_wcs_and_weapon_qty = ""
        # 获取单元的通讯链集合
        self.comm_link = ""
        # 获取传感器
        self.none_mcm_sensors = ""
        # 获取显示"干扰"或"被干扰"
        self.disturb_state = 0
        # 单元所属多个任务数量
        self.multiple_mission_count = 0
        # 单元所属多个任务guid拼接
        self.multiple_mission_guids = ""
        # 是否遵守电磁管控
        self.obeys_emcon = False
        # 武器预设的打击航线
        self.contact_weapon_way_guid = ""
        # 停靠参数是否包含码头
        self.cocking_ops_has_pier = False
        # 弹药库
        self.magazines = ""
        # 被摧毁
        self.pb_components_destroyed_width = 0.0
        # 轻度
        self.pb_components_light_damage_width = 0.0
        # 中度
        self.pb_components_medium_damage_width = 0.0
        # 重度
        self.pb_components_heavy_damage_width = 0.0
        # 正常
        self.pb_components_ok_width = 0.0
        # 配属基地
        self.host_active_unit = ""
        # 状态
        self.active_unit_status = ""

        self.type = ""
        self.subtype = ""
        self.guid = ""
        self.fuel_state = ""
        self.weaponstate = ""

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    def get_assigned_mission(self):
        """
        获取分配的任务

        Returns:
            - 任务对象
        """
        if not self.assigned_mission:
            return None
        return self.situation.get_obj_by_guid(self.assigned_mission)

    def get_original_detector_side(self) -> "CSide":
        """获取单元所在方"""
        return self.situation.side_dict[self.side]

    def get_par_group(self) -> "CGroup":
        """获取父级编组"""
        return self.situation.group_dict[self.parent_group]

    def get_docked_units(self) -> dict[str, "CSubmarine | CShip | CFacility | CAircraft | CSatellite"]:
        """
        获取停靠单元

        Returns:
            - dict: 单元字典
                - 格式: {guid1: unit_obj1, guid2: unit_obj2, ...}
        """
        docked_units = {}
        docked_units_guid = self.docked_units.split("@")
        for guid in docked_units_guid:
            if guid in self.situation.submarine_dict:
                docked_units[guid] = self.situation.submarine_dict[guid]
            elif guid in self.situation.ship_dict:
                docked_units[guid] = self.situation.ship_dict[guid]
            elif guid in self.situation.facility_dict:
                docked_units[guid] = self.situation.facility_dict[guid]
            elif guid in self.situation.aircraft_dict:
                docked_units[guid] = self.situation.aircraft_dict[guid]
            elif guid in self.situation.satellite_dict:
                docked_units[guid] = self.situation.satellite_dict[guid]
        return docked_units

    def get_doctrine(self) -> "CDoctrine | None":
        """获取单元条令"""
        if self.doctrine in self.situation.doctrine_dict:
            doctrine = self.situation.doctrine_dict[self.doctrine]
            doctrine.category = "Unit"  # 需求来源：20200331-2/2:Xy
            return doctrine
        return None

    def get_weapon_db_guids(self) -> list[str]:
        """
        获取编组内所有武器的数据库guid

        Returns:
            - list: 编组内所有武器的guid组成的列表
        """
        weapon_record = self.unit_weapons
        lst1 = []
        if weapon_record:
            lst = weapon_record.split("@")
            lst1 = [k.split("$")[1] for k in lst]
        return lst1

    def get_weapon_infos(self) -> list[list[str]]:
        """
        获取编组内所有武器的名称及数据库guid

        Returns:
            - list: 编组内所有武器的名称及dbid组成的列表
        """
        kinds = ["CWeapon", "CUnguidedWeapon", "CWeaponImpact"]
        if self.class_name in kinds:
            raise ValueError("本身是武器实体")
        weapon_record = self.unit_weapons
        lst = weapon_record.split("@")
        lst1 = [k.split("$") for k in lst]
        return [x for x in lst1 if x != [""]]

    def get_mounts(self) -> dict[str, "CMount"]:
        """
        获取挂架信息

        Returns:
            - dict: 挂架字典
                - 格式: {mount_guid1: mount_obj1, mount_guid2: mount_obj2, ...}
        """
        mounts_guid = self.mounts.split("@")
        mounts_dic = {}
        for guid in mounts_guid:
            if guid in self.situation.mount_dict:
                mounts_dic[guid] = self.situation.mount_dict[guid]
        return mounts_dic

    def get_loadouts(self) -> dict[str, "CLoadout"]:
        """
        获取挂载

        Returns:
            - 挂载字典，格式{loadout_guid1: loadout_obj1, loadout_guid2: loadout_obj2, ...}
        """
        loadout_dic = {}
        loadout_guid = self.loadout_guid.split("@")
        for guid in loadout_guid:
            if guid in self.situation.loadout_dict:
                loadout_dic[guid] = self.situation.loadout_dict[guid]
        return loadout_dic

    def get_magazines(self) -> dict[str, "CMagazine"]:
        """
        获取弹药库

        Returns:
            - dict: 弹药库字典
                - 格式: {magazine_guid1: magazine_obj1, magazine_guid2: magazine_obj2, ...}
        """
        magazines_dic = {}
        magazines_guid = self.magazines.split("@")
        for guid in magazines_guid:
            if guid in self.situation.magazine_dict:
                magazines_dic[guid] = self.situation.magazine_dict[guid]
        return magazines_dic

    def get_sensors(self) -> dict[str, "CSensor"]:
        """
        获取传感器

        Returns:
            - dict: 传感器字典
                - 格式: {sensor_guid1: sensor_obj1, sensor_guid2: sensor_obj2, ...}
        """
        sensors_guid = self.none_mcm_sensors.split("@")
        sensors_dic = {}
        for guid in sensors_guid:
            if guid in self.situation.sensor_dict:
                sensors_dic[guid] = self.situation.sensor_dict[guid]
        return sensors_dic

    @validate_uuid4_args(["contact_guid"])
    async def get_range_to_contact(self, contact_guid: str) -> float:
        """
        获取单元与目标的距离（单位海里）

        Returns:
            float: 单位海里
        """
        cmd = f"print(Tool_Range('{self.guid}','{contact_guid}'))"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return float(response.raw_data)

    async def plot_course(self, course_list: list[tuple[float, float]]) -> bool:
        """
        规划单元航线

        Args:
            - course_list: 航路点列表，每个点为(纬度,经度)元组
                例子：[(40, 39.0), (41, 39.0)]

        Returns:
            - bool: 是否成功

        Raises:
            - TypeError: 当输入参数类型错误时
            - ValueError: 当航路点坐标值无效时
        """
        # 参数检查
        if not isinstance(course_list, list):
            raise TypeError("course_list must be a list")
        if not course_list:
            return False

        # 检查并格式化航路点
        waypoints = []
        for point in course_list:
            if not isinstance(point, Iterable) or len(point) != 2:
                raise TypeError("Each point must be a tuple of (latitude, longitude)")
            lat, lon = point
            if not (isinstance(lat, (int, float)) and isinstance(lon, (int, float))):
                raise TypeError("Coordinates must be numbers")
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError("Invalid coordinates")
            waypoints.append(f"{{latitude={lat},longitude={lon}}}")

        # 构建lua脚本
        course_para = ",".join(waypoints)
        lua_script = f"HS_LUA_SetUnit({{side='{self.side}',guid='{self.guid}',course={{{course_para}}}}})"

        # 发送命令并获取响应
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    def get_way_points_info(self) -> list[dict[str, float | str]]:
        """
        获取本单元航路点信息

        Returns:
            - list[dict]: 单元航路点列表
                - 例子: [{'latitude': 26.0728267704942, 'longitude': 125.582813973341, 'Description': ' '},
                    {'latitude': 26.410343165174, 'longitude': 125.857575579442, 'Description': ' '}]
        """
        way_points = []
        if self._way_points != "":
            guid_list = self._way_points.split("@")
            for guid in guid_list:
                point_obj = self.situation.waypoint_dict[guid]
                way_points.append(
                    {
                        "latitude": point_obj.latitude,
                        "longitude": point_obj.longitude,
                        "Description": point_obj.description,
                    }
                )
        return way_points

    def get_ai_targets(self) -> dict[str, "CContact"]:
        """
        获取活动单元的 AI 目标集合

        Returns:
            - dict: AI目标字典
                - 格式: {guid1: contact_obj, guid2: contact_obj}
                - 例子: {'801ea534-a57c-4d3b-ba5d-0f77e909506c': <.contact.CContact object at 0x000002C27BFCBCF8>,
                    '781cc773-30e3-440d-8750-1b5cddb90249': <.contact.CContact object at 0x000002C27BFEDB00>}
        """
        contacts_dic = {}
        tar_guid_list = self.ai_targets.split("@")
        for tar_guid in tar_guid_list:
            if tar_guid in self.situation.contact_dict:
                contacts_dic[tar_guid] = self.situation.contact_dict[tar_guid]
        return contacts_dic

    async def unit_obeys_emcon(self, obey: bool) -> bool:
        """
        单元传感器面板， 单元是否遵循电磁管控条令

        Args:
            - obey: 是否遵守

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(f"Hs_UnitObeysEMCON('{self.guid}', {str(obey).lower()})")
        return response.lua_success

    async def allocate_weapon_to_target(
        self, target: str | tuple[float, float], weapon_db_guid: str, weapon_count: int
    ) -> bool:
        """
        单元手动攻击(打击情报目标), 或者纯方位攻击(打击一个位置)

        Args:
            - target: 情报目标 guid 或 坐标
            - weapon_db_guid: 武器型号数据库 guid，通常为一个整数字符串
            - weapon_count: 分配数量

        Returns:
            - bool: 是否成功
        """
        if isinstance(target, str):
            table = "{TargetGUID ='" + target + "'}"
        elif isinstance(target, tuple):
            table = "{TargetLatitude =" + str(target[0]) + ", TargetLongitude = " + str(target[1]) + "}"
        else:
            raise Exception("target 参数错误")
        cmd = f"Hs_ScenEdit_AllocateWeaponToTarget('{self.guid}',{table},'{weapon_db_guid}',{weapon_count})"
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    @validate_uuid4_args(["contact_guid"])
    async def unit_drop_target_contact(self, contact_guid: str) -> bool:
        """
        放弃对指定目标进行攻击。

        Args:
            - contact_guid: 目标 guid

        Returns:
            - bool: 是否成功
        """
        cmd = f"Hs_UnitDropTargetContact('{self.side}','{self.guid}','{contact_guid}')"
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def unit_drop_target_all_contact(self) -> bool:
        """
        放弃对所有目标进行攻击。

        Returns:
            - bool: 是否成功
        """
        cmd = f"Hs_UnitDropTargetAllContact('{self.guid}')"
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def ignore_plotted_course_when_attacking(self, ignore_plotted: bool) -> bool:
        """
        指定单元攻击时是否忽略计划航线。

        Args:
            - ignore_plotted: 是否忽略

        Returns:
            - bool: 是否成功
        """
        cmd = f"Hs_LPCWAttackSUnit('{self.side}','{self.guid}',{str(ignore_plotted).lower()})"
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def follow_terrain(self, is_followed: bool) -> bool:
        """
        设置当前单元（飞机）的飞行高度跟随地形

        Args:
            - is_followed: 是否跟随

        Returns:
            - bool: 是否成功
        """
        cmd = f"ScenEdit_SetUnit({{guid='{self.guid}',TEEEAINFOLLOWING={str(is_followed).lower()}}})"
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def delete_coursed_point(self, point_index: int | list[int], clear: bool = False) -> bool:
        """
        单元删除航路点

        Args:
            - point_index: 航路点index
                - int: 航路点index, 删除航路点的序号, 从0开始, 0代表离单元最近的航路点
                - list[int]: 删除航路点的序号列表

            - clear: 是否清空所有航路点
                - True: 清空所有航路点
                - False: 按 point_index 删除航路点

        Returns:
            - bool: 是否成功
        """
        lua_script = ""
        if clear:
            if self._way_points != "":
                point_count = len(self._way_points.split("@"))
                for point in range(point_count - 1, -1, -1):
                    lua_script += f'Hs_UnitOperateCourse("{self.guid}",{point},0.0,0.0,"Delete")'
        else:
            if isinstance(point_index, list):
                if len(point_index) > 1 and point_index[-1] > point_index[0]:
                    point_index.reverse()
                for point in point_index:
                    lua_script += f'Hs_UnitOperateCourse("{self.guid}",{point},0.0,0.0,"Delete")'
            elif isinstance(point_index, int):
                lua_script = f"Hs_UnitOperateCourse('{self.guid}',{point_index},0.0,0.0,'Delete')"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def return_to_base(self) -> bool:
        """单元返航"""
        response = await self.mozi_server.send_and_recv(f"HS_ReturnToBase('{self.guid}')")
        return response.lua_success

    @validate_uuid4_args(["base_guid"])
    async def select_new_base(self, base_guid: str) -> bool:
        """
        单元选择新基地/新港口

        Args:
            - base_guid: 新基地的guid

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(f"ScenEdit_SetUnit({{guid='{self.guid}',base='{base_guid}'}})")
        return response.lua_success

    async def hold_position(self, hold: bool) -> bool:
        """
        命令面上指定单元设置是否保持阵位。 该接口暂不可用

        Args:
            - hold: 是否保持阵位
                - True: 是
                - False: 否

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_HoldPositonSelectedUnit('{self.guid}',{str(hold).lower()})"
        )
        return response.lua_success

    async def leave_dock_alone(self) -> bool:
        """单独出航"""
        cmd = f"Hs_ScenEdit_DockingOpsGroupOut({{{self.guid}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def assign_unit_to_mission(self, mission_name: str) -> bool:
        """
        分配加入到任务中

        Args:
            - mission_name: 任务名称

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_AssignUnitToMission('{self.guid}','{mission_name}')"
        )
        return response.lua_success

    async def assign_unit_to_mission_escort(self, mission_name: str) -> bool:
        """
        将单元分配为某打击任务的护航任务

        Args:
            - mission_name: 任务名称

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_AssignUnitToMission('{self.guid}','{mission_name}',true)"
        )
        return response.lua_success

    async def cancel_assign_unit_to_mission(self) -> bool:
        """
        将单元取消分配任务

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(f"ScenEdit_AssignUnitToMission('{self.guid}','none')")
        return response.lua_success

    async def set_unit_heading(self, heading: int) -> bool:
        """
        设置朝向

        Args:
            - heading: 朝向

        Returns:
            - bool: 是否成功
        example: set_unit_heading('016b72ba-2ab2-464a-a340-3cfbfb133ed1',30)
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_SetUnit({{guid ='{self.guid}' ,heading = {heading}}})"
        )
        return response.lua_success

    @validate_uuid4_args(["contact_guid"])
    async def auto_attack(self, contact_guid: str) -> bool:
        """
        自动攻击目标

        Args:
            - contact_guid: 目标guid

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_AttackContact('{self.guid}', '{contact_guid}', {{mode=0}})"
        )
        return response.lua_success

    async def set_desired_speed(self, desired_speed: int | float) -> bool:
        """
        设置单元的期望速度

        Args:
            - desired_speed: 单元期望速度，单位千米/小时

        Returns:
            - bool: 是否成功
        """
        if isinstance(desired_speed, int) or isinstance(desired_speed, float):
            response = await self.mozi_server.send_and_recv(
                f"ScenEdit_SetUnit({{guid='{self.guid}', manualSpeed={desired_speed / 1.852}}})"
            )
            return response.lua_success
        else:
            mprint.warning("desired_speed 参数类型错误")
            return False

    @validate_literal_args
    async def set_throttle(self, enum_throttle: Literal[1, 2, 3, 4]) -> bool:
        """
        设置单元油门

        Args:
            - enum_throttle: 油门
                - 1: 低速
                - 2: 巡航
                - 3: 全速
                - 4: 军用

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_SetUnit({{guid='{self.guid}', throttle={enum_throttle}}})"
        )
        return response.lua_success

    async def set_radar_on(self, on: bool) -> bool:
        """
        设置雷达开关机

        Args:
            - on: 开机或关机
                - True: 开机
                - False: 关机

        Returns:
            - bool: 是否成功
        """
        lua_script = f"Hs_ScenEdit_SetUnitSensorSwitch({{guid ='{self.guid}',rader={str(on).lower()}}})"  # TODO: 这里是服务端设计的时候就写错单词了？
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def set_sonar_on(self, on: bool) -> bool:
        """
        设置声纳开关机

        Args:
            - on: 开机或关机
                - True: 开机
                - False: 关机

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_ScenEdit_SetUnitSensorSwitch({{guid ='{self.guid}',SONAR={str(on).lower()}}})"
        )
        return response.lua_success

    async def set_oecm_on(self, on: bool) -> bool:
        """
        设置干扰机开关机

        Args:
            - on: 开机或关机
                - True: 开机
                - False: 关机

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_ScenEdit_SetUnitSensorSwitch({{guid ='{self.guid}',OECM={str(on).lower()}}})"
        )
        return response.lua_success

    async def manual_attack(self, target_guid: str, weapon_db_guid: str, weapon_num: int) -> bool:
        """
        手动开火函数

        Args:
            - target_guid: 目标guid
            - weapon_db_guid: 武器的数据库guid，通常为一个整数字符串
            - weapon_num: 武器数量

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_ScenEdit_AllocateWeaponToTarget('{self.guid}',{{TargetGUID='{target_guid}'}}, '{weapon_db_guid}',{weapon_num})"
        )
        return response.lua_success

    async def set_single_out(self) -> bool:
        """
        设置飞机在基地内单机出动

        Returns:
            - bool: 是否成功
        """
        if self.class_name == "CAircraft":
            response = await self.mozi_server.send_and_recv(f"Hs_ScenEdit_AirOpsSingleOut({{{self.guid}}})")
            return response.lua_success
        else:
            mprint.warning("不是飞机")
            return False

    @validate_literal_args
    async def drop_active_sonobuoy(self, deep_or_shallow: Literal["deep", "shallow"]) -> bool:
        """
        投放主动声呐

        Args:
            - deep_or_shallow: 深浅
                - "deep": 深-温跃层之下
                - "shallow": 浅-温跃层之上

        Returns:
            - bool: 是否成功
        """
        side = self.situation.side_dict[self.side]
        cmd = f"Hs_DropActiveSonobuoy('{side.name}','{self.guid}','{deep_or_shallow}')"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    @validate_literal_args
    async def drop_passive_sonobuoy(self, deep_or_shallow: Literal["deep", "shallow"]) -> bool:
        """
        投放被动声呐

        Args:
            - deep_or_shallow: 深浅
                - "deep": 深-温跃层之下
                - "shallow": 浅-温跃层之上

        Returns:
            - bool: 是否成功
        """
        side = self.situation.side_dict[self.side]
        cmd = f"Hs_DropPassiveSonobuoy('{side.name}','{self.guid}','{deep_or_shallow}')"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    @validate_literal_args
    async def drop_sonobuoy(
        self, deep_or_shallow: Literal["deep", "shallow"], passive_or_active: Literal["active", "passive"]
    ) -> bool:
        """
        投放声呐,目前只能飞机投放声纳

        Args:
            - deep_or_shallow: 深浅
                - "deep": 深-温跃层之下
                - "shallow": 浅-温跃层之上
            - passive_or_active: 主动或被动
                - "active": 主动声呐
                - "passive": 被动声呐
        返回：'lua执行成功' 或 '脚本执行出错'
        """
        side = self.situation.side_dict[self.side]
        response = await self.mozi_server.send_and_recv(
            f"Hs_DropSonobuoy('{side.name}','{self.guid}','{deep_or_shallow}','{passive_or_active}')"
        )
        return response.lua_success

    @validate_uuid4_args(["weapon_record_guid"])
    async def set_weapon_reload_priority(self, weapon_record_guid: str, priority: bool) -> bool:
        """
        设置武器重新装载优先级

        Args:
            - weapon_record_guid: 武器记录guid
            - priority: 优先级
                - True: 优先
                - False: 不优先

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_ScenEdit_SetWeaponReloadPriority({{guid='{self.guid}',WPNREC_GUID='{weapon_record_guid}',IsReloadPriority={str(priority).lower()}}})"
        )
        return response.lua_success

    @validate_uuid4_args(["mag_guid"])
    async def add_weapon_to_unit_magazine(self, mag_guid: str, weapon_db_id: int, number: int) -> bool:
        """
        往弹药库内添加武器

        Args:
            - mag_guid: 弹药库 guid
            - weapon_db_id: 武器 db_id
            - number: 武器数量

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_AddWeaponToUnitMagazine({{side='{self.side}',guid='{self.guid}',mag_guid='{mag_guid}',wpn_dbid={weapon_db_id},number={number}}})"
        )
        return response.lua_success

    async def switch_sensor(self, radar: bool, sonar: bool, oecm: bool) -> bool:
        """
        同时设置单元上多种类型传感器的开关状态。

        Args:
            - radar: 雷达
                - True: 开
                - False: 关
            - sonar: 声呐
                - True: 开
                - False: 关
            - oecm: 攻击性电子对抗手段
                - True: 开
                - False: 关

        Returns:
            - bool: 是否成功
        """
        lua = f"Hs_ScenEdit_SetUnitSensorSwitch({{guid='{self.guid}', RADER={str(radar).lower()},SONAR={str(sonar).lower()},OECM={str(oecm).lower()}}})"
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success

    @validate_literal_args
    async def wcsf_contact_types_unit(self, attack_status: Literal["Hold", "Tight", "Free", "Inherited"]) -> bool:
        """
        控制指定单元对所有目标类型的攻击状态。

        Args:
            - attack_status: 禁止、限制、自由、按上级条令执行
                - "Hold": 禁止
                - "Tight": 限制
                - "Free": 自由
                - "Inherited": 按上级条令执行

        Returns:
            - bool: 是否成功
        """
        lua = f"Hs_WCSFAContactTypesSUnit('{self.side}','{self.guid}','{attack_status}')"
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success

    @validate_uuid4_args(["target_guid"])
    async def allocate_all_weapons_to_target(self, target_guid: str, weapon_db_id: int) -> bool:
        """
        为手动交战分配同类型所有武器。

        Args:
            - target_guid: 目标guid
            - weapon_db_id: 武器dbid

        Returns:
            - bool: 是否成功
        """
        lua = f"Hs_ScenEdit_AllocateAllWeaponsToTarget('{self.guid}',{{TargetGUID='{target_guid}'}},{weapon_db_id})"
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success

    @validate_uuid4_args(["weapon_salvo_guid"])
    async def remove_salvo_target(self, weapon_salvo_guid: str) -> bool:
        """
        取消手动交战时齐射攻击目标。

        Args:
            - weapon_salvo_guid: 武器齐射 GUID

        Returns:
            - bool: 是否成功
        """
        lua = f"Hs_ScenEdit_RemoveWeapons_Target('{self.guid}','{weapon_salvo_guid}')"
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success

    async def set_salvo_timeout(self, salvo_timeout: bool = False) -> bool:
        """
        设置超时自动取消齐射

        Args:
            - salvo_timeout: 是否超时自动取消齐射
                - True: 是
                - False: 否

        Returns:
            - bool: 是否成功
        """
        lua = f"Hs_ScenEdit_SetSalvoTimeout({str(salvo_timeout).lower()}) "
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success

    async def allocate_salvo_to_target(self, target: str | tuple, weapon_db_id: int) -> bool:
        """
        单元手动分配一次齐射攻击(打击情报目标), 或者纯方位攻击(打击一个位置)

        Args:
            - target: 情报目标guid 或 (lat, lon) 例：(40.90,30.0)
            - weapon_db_id: 武器型号数据库id

        Returns:
            - bool: 是否成功
        """
        if isinstance(target, str):
            table = "{TargetGUID ='" + target + "'}"
        elif isinstance(target, tuple):
            table = "{TargetLatitude =" + str(target[0]) + ", TargetLongitude = " + str(target[1]) + "}"
        else:
            raise Exception("target 参数错误")
        lua_script = f"Hs_ScenEdit_AllocateSalvoToTarget('{self.guid}',{table},{weapon_db_id})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def allocate_weapon_auto_targeted(self, target_guids: list[str], weapon_db_id: int, num: int) -> bool:
        """
        为自动交战进行弹目匹配。此时自动交战意义在于不用指定对多个目标的攻击顺序。

        Args:
            - target_guids: 目标guid列表
            - weapon_db_id: 武器型号数据库id
            - num: 武器发射数量 对单个目标的数量

        Returns:
            - bool: 是否成功
        """
        targets = None
        for target_guid in target_guids:
            if targets:
                targets += f",'{target_guid}'"
            else:
                targets = f"'{target_guid}'"
        lua = f"Hs_AllocateWeaponAutoTargeteds('{self.guid}',{{{targets}}},{weapon_db_id},{num})"
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success

    async def auto_target(self, contacts_guid_list: list[str]) -> bool:
        """
        让单元自动进行弹目匹配并攻击目标。

        Args:
            - contacts_guid_list: 目标guid列表

        Returns:
            - bool: 是否成功
        """
        targets = None
        for target_guid in contacts_guid_list:
            if targets:
                targets += f",'{target_guid}'"
            else:
                targets = f"'{target_guid}'"
        cmd = f"Hs_AutoTargeted('{self.guid}',{{{targets}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def self_update(self, options: dict[str, Any]) -> tuple[int, "CActiveUnit"]:
        response = await self.mozi_server.send_and_recv(f"ReturnObj(scenEdit_UpdateUnit({options}))")
        active_unit = CActiveUnit(self.guid, self.mozi_server, self.situation)
        if response.raw_data[:4] == "unit":
            # 处理接收的数据
            result_split = response.raw_data[6:-1].replace("'", "")
            result_join = ""
            result_join = result_join.join([one for one in result_split.split("\n")])
            lst = result_join.split(",")
            for keyValue in lst:
                keyValue_list = keyValue.split("=")
                if len(keyValue_list) == 2:
                    attr = keyValue_list[0].strip()
                    value = keyValue_list[1].strip()
                    if attr == "name":
                        active_unit.name = value
                    elif attr == "side":
                        active_unit.side = value
                    elif attr == "type":
                        active_unit.type = value
                    elif attr == "subtype":
                        active_unit.subtype = value
                    elif attr == "guid":
                        active_unit.guid = value
                    elif attr == "proficiency":
                        active_unit.proficiency_level = value
                    elif attr == "latitude":
                        active_unit.latitude = float(value)
                    elif attr == "longitude":
                        active_unit.longitude = float(value)
                    elif attr == "altitude":
                        active_unit.altitude = float(value)
                    elif attr == "heading":
                        active_unit.current_heading = float(value)
                    elif attr == "speed":
                        active_unit.current_speed = float(value)
                    elif attr == "throttle":
                        active_unit.current_throttle = value
                    elif attr == "autodetectable":
                        active_unit.auto_detectable = bool(value)
                    elif attr == "mounts":
                        active_unit._mounts = int(value)
                    elif attr == "magazines":
                        active_unit._magazines = int(value)
                    elif attr == "unitstate":
                        active_unit.active_unit_status = value
                    elif attr == "fuelstate":
                        active_unit.fuel_state = value
                    elif attr == "weaponstate":
                        active_unit.weaponstate = value
            code = 200
        else:
            code = 500
        return code, active_unit

    async def update_way_point(self, way_point_index: int, lat: float, lon: float) -> bool:
        """
        更新单元航路点的具体信息,必须首先有一个航路点

        Args:
            - way_point_index: 航路点序号，从0开始，0表示第1个
            - lat: 纬度
            - lon: 经度

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f'Hs_UpdateWayPoint("{self.guid}",{way_point_index},{{"latitude":{lat},"longitude":{lon}}})'
        )
        return response.lua_success

    async def set_way_point_sensor(self, way_point_index: int, sensor: str, sensor_status: str) -> bool:
        """
        设置航路点传感器的开关状态

        Args:
            - way_point_index: 航路点序号，从0开始
            - sensor: 传感器类型
                - 'CB_Sonar': 声呐
                - 'CB_radar': 雷达
                - 'CB_ECM': 干扰机
            - sensor_status: 传感器状态
                - 'Unchecked': 未开机
                - 'Checked': 开机

        Returns:
            - bool: 是否成功
        """
        lua_script = f"Hs_UpdateWayPointSensorStatus('{self.guid}',{way_point_index},'{sensor}','{sensor_status}')"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def set_desired_height(self, desired_height: float | int, move_to: bool = False) -> bool:
        """
        设置单元的期望高度
        限制：专项赛限制使用，禁止设置moveto='true'

        Args:
            - desired_height: 期望高度值
            - move_to: 是否瞬间到达该高度
                - True: 是
                - False: 否

        Returns:
            - bool: 是否成功
        """
        moveto_str = str(move_to).lower()
        if isinstance(desired_height, int) or isinstance(desired_height, float):
            lua_script = (
                "ScenEdit_SetUnit({guid='"
                + str(self.guid)
                + "',  altitude ='"
                + str(desired_height)
                + "', moveto='"
                + moveto_str
                + "'}) "
            )
            response = await self.mozi_server.send_and_recv(lua_script)
            return response.lua_success
        else:
            raise Exception("desired_height 参数类型错误，应为 float 或 int")

    async def unit_auto_detectable(self, auto_detectable: bool) -> bool:
        """
        设置单元是否可以被自动探测到

        Args:
            - auto_detectable: 是否自动探测到
                - True: 是
                - False: 否

        Returns:
            - bool: 是否成功
        """
        auto_detectable_str = str(auto_detectable).lower()
        lua_script = f"ScenEdit_SetUnit({{{self.guid},autodetectable={auto_detectable_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def set_fuel_quantity(self, remaining_fuel: float) -> bool:
        """
        设置单元燃油量

        Args:
            - remaining_fuel: 剩余燃油的公斤数

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv("Hs_SetFuelQty('{}','{}')".format(self.guid, remaining_fuel))
        return response.lua_success

    async def set_own_side(self, new_side: str) -> bool:
        """
        改变单元所属阵营

        Args:
            - new_side: 新的方名称

        Returns:
            - bool: 是否成功
        """
        side = self.situation.side_dict[self.side]
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_SetUnitSide({{side='{side.name}',name='{self.name}',newside='{new_side}'}})"
        )
        return response.lua_success

    async def set_loadout(
        self, loadout_id: str, time_to_ready_minutes: int, ignore_magazines: bool, exclude_optional_weapons: bool
    ) -> bool:
        """
        设置挂载方案

        Args:
            - loadout_id: 挂载方案ID, 0表示使用当前挂载方案
            - time_to_ready_minutes: 载荷准备时间（分钟）
            - ignore_magazines:
                - True: 忽略弹药库
                - False: 不忽略弹药库
            - exclude_optional_weapons:
                - True: 不包含可选武器
                - False: 包含可选武器

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_SetLoadout ({{UnitName='{self.name}',LoadoutID='{loadout_id}',TimeToReady_Minutes='{time_to_ready_minutes}',IgnoreMagazines={str(ignore_magazines).lower()},"
            f"ExcludeOptionalWeapons={str(exclude_optional_weapons).lower()}}})"
        )
        return response.lua_success

    async def reload_weapon(self, weapon_db_id: int, number: int, fillout: bool = False) -> bool:
        """
        让指定单元重新装载武器

        Args:
            - weapon_db_id: 武器数据库guid
            - number: 要添加的数量
            - fillout:
                - True: 装满
                - False: 不装满

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_AddReloadsToUnit({{{self.guid},wpn_dbguid={weapon_db_id},number={number},fillout={str(fillout).lower()}}})"
        )
        return response.lua_success

    async def load_cargo(self, cargo_db_id: int) -> bool:
        """
        添加货物

        Args:
            - cargo_db_id: 货物数据库guid

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(f"Hs_AddCargoToUnit('{self.guid}',{cargo_db_id})")
        return response.lua_success

    async def remove_cargo(self, cargo_db_id: int) -> bool:
        """
        删除货物

        Args:
            - cargo_db_id: 货物数据库guid

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(f"Hs_RemoveCargoToUnit('{self.guid}',{cargo_db_id})")
        return response.lua_success

    @validate_uuid4_args(["weapon_rec_guid"])
    async def set_magazine_weapon_current_load(self, weapon_rec_guid: str, current_load: int) -> bool:
        """
        设置弹药库武器数量

        Args:
            - weapon_rec_guid: 武器记录guid
            - current_load: 当前武器装载数量

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_ScenEdit_SetMagazineWeaponCurrentLoad({{{self.guid},WPNREC_GUID='{weapon_rec_guid}',currentLoad={current_load}}})"
        )
        return response.lua_success

    @validate_uuid4_args(["magazine_guid"])
    async def remove_magazine(self, magazine_guid: str) -> bool:
        """
        删除弹药库

        Args:
            - magazine_guid: 弹药库guid

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_ScenEdit_RemoveMagazine({{{self.guid},magazine_guid='{magazine_guid}'}})"
        )
        return response.lua_success

    @validate_uuid4_args(["magazine_guid"])
    @validate_literal_args
    async def set_magazine_state(
        self, magazine_guid: str, state: Literal["正常运转", "轻度毁伤", "中度毁伤", "重度毁伤", "摧毁"]
    ) -> bool:
        """
        设置弹药库状态

        Args:
            - magazine_guid: 弹药库guid
            - state: 状态

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_ScenEdit_SetMagazineState({{{self.guid},magazine_guid='{magazine_guid}',state='{state}'}})"
        )
        return response.lua_success

    @validate_uuid4_args(["weapon_rec_guid"])
    async def set_weapon_current_load(self, weapon_rec_guid: str, number: int) -> bool:
        """
        设置挂架武器数量

        Args:
            - weapon_rec_guid: 武器guid
            - number: 数量

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_ScenEdit_SetWeaponCurrentLoad({{{self.guid},WPNREC_GUID='{weapon_rec_guid}',CURRENTLOAD={number}}})"
        )
        return response.lua_success

    @validate_uuid4_args(["base_guid"])
    async def add_to_host(self, base_guid: str) -> bool:
        """
        将单元部署进基地

        Args:
            - base_guid: 基地的guid

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_HostUnitToParent({{{self.guid},SelectedHostNameOrID='{base_guid}'}})"
        )
        return response.lua_success

    async def add_mount(self, mount_db_id: int, heading_code_dict: dict[str, bool]) -> bool:
        """
        为单元添加武器挂架

        Args:
            - mount_db_id (int): 挂架dbid
            - heading_code_dict (dict):
                - key(str)'-枚举值，
                    - 'PS1'-左弦尾1
                    - 'PMA1'-左弦中后1
                    - 'PMF1'-左弦中前1
                    - 'PB1'-左弦首1
                    - 'SS1'-右弦尾1
                    - 'SMA1'-右弦中后1
                    - 'SMF1'-右弦中前1
                    - 'SB1'-右弦首1
                    - 'PS2'-左弦尾2
                    - 'PMA2'-左弦中后2
                    - 'PMF2'-左弦中前2
                    - 'PB2'-左弦首2
                    - 'SS2'-右弦尾2
                    - 'SMA2'-右弦中后2
                    - 'SMF2'-右弦中前2
                    - 'SB2'-右弦首2
                    - '360'-全覆盖
                - value(bool): True or False}
                - example: {'PS1':True, 'PB1':True}
                - 不设置时，默认为False

        Returns:
            - bool: 是否成功
        """
        heading_code = ""
        for key, value in heading_code_dict.items():
            value_str = str(value).lower()
            if heading_code:
                heading_code += f",{key}={value_str}"
            else:
                heading_code = f"{key}={value_str}"
        lua_script = f"Hs_ScenEdit_AddMount({{unitname='{self.name}',mount_dbid={mount_db_id},{heading_code}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @validate_uuid4_args(["mount_guid"])
    async def remove_mount(self, mount_guid: str) -> bool:
        """
        删除单元中指定的武器挂架

        Args:
            - mount_guid: 武器挂架的GUID

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_ScenEdit_RemoveMount({{{self.name},mount_guid='{mount_guid}'}})"
        )
        return response.lua_success

    @validate_uuid4_args(["mount_guid"])
    async def add_weapon(self, weapon_db_id: int, mount_guid: str) -> bool:
        """
        给单元挂架中添加武器

        Args:
            - weapon_db_id: 武器DBID
            - mount_guid: 挂架guid

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_ScenEdit_AddWeapon({{{self.guid},wpn_dbid={weapon_db_id},MOUNT_GUID='{mount_guid}',IsTenThousand=true}})"
        )
        return response.lua_success

    @validate_uuid4_args(["weapon_rec_guid"])
    async def remove_weapon(self, weapon_rec_guid: str) -> bool:
        """
        通过武器属性删除单元的武器

        Args:
            - weapon_rec_guid: 武器记录guid

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_ScenEdit_RemoveWeapon({{unitname='{self.name}', WPNREC_GUID='{weapon_rec_guid}'}})"
        )
        return response.lua_success

    @validate_uuid4_args(["component_guid"])
    @validate_literal_args
    async def set_unit_damage(self, overall_damage: float, component_guid: str, level: Literal[0, 1, 2, 3, 4]) -> bool:
        """
        设置单元总体毁伤和单元各组件的毁伤值
        限制：专项赛禁用

        Args:
            - overalldamage: 总体毁伤值
            - comp_guid: 组件guid
            - level: 毁伤等级
                - 0-正常工作
                - 1-轻度毁伤
                - 2-中度毁伤
                - 3-重度毁伤
                - 4-被摧毁

        Returns:
            - bool: 是否成功
        """
        lua_script = (
            f"HS_SetUnitDamage({{guid='{self.guid}',OVERALLDEMAGE={overall_damage},"
            f"components={{'{component_guid}','{level}'}}}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def set_magazine_weapon_number(self, magazine_guid: str, weapon_db_guid: str, number: int) -> bool:
        """
        往单元的弹药库中添加指定数量的武器
        限制：专项赛禁用

        Args:
            - magazine_guid: 弹药库guid
            - weapon_db_guid: 武器数据库guid
            - number: 武器数量

        Returns:
            - bool: 是否成功
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_AddWeaponToUnitMagazine({{guid='{self.guid}',mag_guid='{magazine_guid}',wpn_dbguid='{weapon_db_guid}',number={number}}})"
        )
        return response.lua_success

    @validate_literal_args
    async def set_proficiency(self, proficiency: Literal["Novice", "Cadet", "Regular", "Veteran", "Ace"]) -> bool:
        """
        设置单元训练水平
        限制：专项赛禁用

        Args:
            - proficiency: 训练水平
                - Novice-新手
                - Cadet-初级
                - Regular-普通
                - Veteran-老手
                - Ace-顶级
        """
        side = self.situation.side_dict[self.side]
        lua_script = (
            f"ScenEdit_SetSideOptions({{side='{side.name}', guid='{self.guid}', proficiency='{proficiency}'}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success
