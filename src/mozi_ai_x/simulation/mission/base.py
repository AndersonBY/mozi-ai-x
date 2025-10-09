from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation
    from ..args import Throttle
    from ..doctrine import CDoctrine
    from ..side import CSide
    from ..active_unit import CActiveUnit

from mozi_ai_x.utils.validator import validate_literal_args, validate_uuid4_args

from ..base import Base


class CMission(Base):
    """任务"""

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        # 推演方
        self.side = ""
        # 推演方名称
        self.side_name = ""
        # 任务类别
        self.category = 0
        # 任务类型
        self.mission_class = 0
        # 任务状态
        self.mission_status = 0
        # 飞机设置-编队规模
        self.flight_size = 0
        # 空中加油任务设置-任务执行设置 -加油机遵循受油机的飞行计划是否选中
        self.tanker_follows_receivers = False
        # 任务描述
        self.description = ""
        # 空中加油任务设置-任务规划设置 加油机没到位的情况下启动任务
        self.launch_mission_without_tankers_in_place = False
        # 水面舰艇/潜艇设置-水面舰艇/潜艇树低于编队规模要求,不能出击(根据基地编组)
        self.use_group_size_hard_limit = False
        # 已分配单元的集合
        self.assigned_units = ""
        # 空中加油任务设置-任务执行设置 - 每架加油机允许加油队列最大长度
        self.max_receivers_in_queue_per_tanker_airborne = ""
        # 水面舰艇/潜艇设置-编队规模
        self.group_size = 0
        # 空中加油-  点击配置  显示如下两个选项： 返回选中的值1.使用优良充足的最近加油机加油2.使用已分配特定任务的加油机加油
        self.tanker_usage = 0
        # 条令
        self.doctrine = ""
        # 空中加油任务设置-任务规划设置 阵位上加油机最小数量
        self.tanker_min_number_station = ""
        # 未分配单元的集合
        self.unassigned_units = ""
        # 单元航线
        self.side_way_guid = ""
        # 空中加油任务设置-任务执行设置 -受油机寻找加油机的时机条件
        self.fuel_qty_to_start_looking_for_tanker_airborne = ""
        # 空中加油选项是否与上级保持一致
        self.use_refuel = False
        # 飞机数低于编队规模要求,不能起飞
        self.use_flight_size_hard_limit = False
        # 飞机设置-空中加油
        self.refuel = 0
        # 行动预案
        self.use_action_plan = False
        # 空中加油任务设置-任务规划设置 留空的加油机最小数量
        self.tanker_min_number_airborne = ""
        # 空中加油任务设置-任务规划设置1.需要加油机的最小数量
        self.tanker_min_number_total = ""
        self.transit_throttle_airecraft = ""  # 飞机航速与高度-出航油门
        self.station_throttle_aircraft = ""  # 飞机航速与高度-阵位油门
        self.transit_altitude_aircraft = ""  # 飞机航速与高度-出航高度
        self.station_altitude_aircraft = ""  # 飞机航速与高度-阵位高度
        self.transit_throttle_submarine = ""  # 潜艇航速与潜深-出航油门
        self.station_throttle_submarine = ""  # 潜艇航速与潜深-阵位油门
        self.transit_depth_submarine = ""  # 潜艇航速与潜深-出航潜深
        self.station_depth_submarine = ""  # 潜艇航速与潜深-阵位潜深
        self.transit_throttle_ship = ""  # 水面舰艇航速-出航油门
        self.station_throttle_ship = ""  # 水面舰艇航速-阵位油门

    def get_assigned_units(self) -> dict:
        """
        获取已分配任务的单元

        Returns:
            dict: key为单元guid, value为单元对象
        """
        guid_list = self.assigned_units.split("@")
        units = {}
        for guid in guid_list:
            units[guid] = self.situation.get_obj_by_guid(guid)
        return units

    def get_unassigned_units(self) -> dict:
        """
        获取未分配任务的单元

        Returns:
            dict: key为单元guid, value为单元对象
        """
        guid_list = self.unassigned_units.split("@")
        units = {}
        for guid in guid_list:
            units[guid] = self.situation.get_obj_by_guid(guid)
        return units

    def get_doctrine(self) -> "CDoctrine | None":
        """
        获取条令

        Returns:
            CDoctrine | None
        """
        if self.doctrine in self.situation.doctrine_dict:
            doctrine = self.situation.doctrine_dict[self.doctrine]
            doctrine.category = "Mission"  # 需求来源：20200331-2/2:Xy
            return doctrine
        return None

    def get_weapon_db_guids(self) -> list[str]:
        """
        获取编组内所有武器的数据库 GUID

        Returns:
            编组内所有武器的guid组成的列表
        """
        side = self.situation.side_dict[self.side]
        unit_guids = self.assigned_units.split("@")
        # 考虑了编组作为执行单位时的情况。
        groups = self.situation.side_dict[self.side].groups
        assigned_groups = {k: v for k, v in groups.items() if k in unit_guids}
        result = []
        if len(assigned_groups) > 0:
            gg = [k.get_weapon_db_guids() for k in assigned_groups.values()]
            for n in gg:
                result.extend(n)
        assigned_units_guids = [k for k in unit_guids if k not in groups.keys()]
        weapon_record = []
        lst02 = []
        if len(assigned_units_guids) > 0:
            weapon_record.extend(list({v.unit_weapons: k for k, v in side.submarines.items() if k in assigned_units_guids}))
            weapon_record.extend(list({v.unit_weapons: k for k, v in side.ships.items() if k in assigned_units_guids}))
            weapon_record.extend(list({v.unit_weapons: k for k, v in side.facilities.items() if k in assigned_units_guids}))
            weapon_record.extend(list({v.unit_weapons: k for k, v in side.aircrafts.items() if k in assigned_units_guids}))
            weapon_record.extend(list({v.unit_weapons: k for k, v in side.satellites.items() if k in assigned_units_guids}))
            for unit_weapon_record in weapon_record:
                if unit_weapon_record:
                    lst01 = unit_weapon_record.split("@")
                    lst02.extend([k.split("$")[1] for k in lst01])
        result.extend(lst02)
        return result

    def get_weapon_infos(self) -> list[str]:
        """
        获取编组内所有武器的名称及 GUID

        Returns:
            编组内所有武器的名称及 GUID 组成的列表
        """
        side = self.situation.side_dict[self.side]
        unit_guids = self.assigned_units.split("@")
        # 考虑了编组作为执行单位时的情况。
        groups = self.situation.side_dict[self.side].groups
        assigned_groups = {k: v for k, v in groups.items() if k in unit_guids}
        result = []
        if len(assigned_groups) > 0:
            gg = [k.get_weapon_infos() for k in assigned_groups.values()]
            for n in gg:
                result.extend(n)
        assigned_units_guids = [k for k in unit_guids if k not in groups.keys()]
        weapon_record = []
        lst04 = []
        if len(assigned_units_guids) > 0:
            weapon_record.extend(list({v.unit_weapons: k for k, v in side.submarines.items() if k in assigned_units_guids}))
            weapon_record.extend(list({v.unit_weapons: k for k, v in side.ships.items() if k in assigned_units_guids}))
            weapon_record.extend(list({v.unit_weapons: k for k, v in side.facilities.items() if k in assigned_units_guids}))
            weapon_record.extend(list({v.unit_weapons: k for k, v in side.aircrafts.items() if k in assigned_units_guids}))
            weapon_record.extend(list({v.unit_weapons: k for k, v in side.satellites.items() if k in assigned_units_guids}))
            for unit_weapon_record in weapon_record:
                if unit_weapon_record:
                    lst01 = unit_weapon_record.split("@")
                    lst04.extend([k.split("$") for k in lst01])
        result.extend(lst04)
        return result

    def get_side(self) -> "CSide":
        """
        获取任务所在方

        Returns:
            任务所在方对象
        """
        return self.situation.side_dict[self.side]

    async def set_is_active(self, active: bool) -> bool:
        """
        设置是否启用任务

        Args:
            active (bool): 是否启用

        Returns:
            bool
        """
        lua = f"ScenEdit_SetMission('{self.side}','{self.name}',{{isactive='{str(active).lower()}'}})"
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success

    async def set_start_time(self, start_time: str) -> bool:
        """
        设置任务开始时间

        Args:
            start_time (str): 格式 '2020-04-16 22:10:00'

        Returns:
            bool
        """
        cmd_str = f"ScenEdit_SetMission('{self.side}','{self.name}',{{starttime='{start_time}'}})"
        response = await self.mozi_server.send_and_recv(cmd_str)
        return response.lua_success

    async def set_end_time(self, end_time: str) -> bool:
        """
        设置任务结束时间

        Args:
            end_time (str): 格式 '2020-04-16 22:10:00'

        Returns:
            bool
        """
        cmd_str = f"ScenEdit_SetMission('{self.side}','{self.name}',{{endtime='{end_time}'}})"
        response = await self.mozi_server.send_and_recv(cmd_str)
        return response.lua_success

    async def set_one_third_rule(self, one_third: bool) -> bool:
        """
        设置任务是否遵循1/3原则

        Args:
            one_third (bool): 是否遵循1/3原则

        Returns:
            bool
        """

        cmd = f'ScenEdit_SetMission("{self.side}","{self.name}", {{oneThirdRule={str(one_third).lower()}}})'
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def switch_radar(self, switch_on: bool) -> bool:
        """
        设置任务雷达是否打开

        Args:
            switch_on (bool): 雷达打开或者静默

        Returns:
            bool
        """
        if switch_on:
            set_str = "Radar=Active"
        else:
            set_str = "Radar=Passive"
        return await self.situation.side_dict[self.side].set_ecom_status("Mission", self.name, set_str)

    @validate_uuid4_args(["unit_guid"])
    async def assign_unit(self, unit_guid: str, escort: bool = False) -> bool:
        """
        分配单元

        Args:
            unit_guid (str): 单元guid
            escort (bool): 是否护航任务

        Returns:
            bool
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_AssignUnitToMission('{unit_guid}', '{self.name}', {str(escort).lower()})"
        )
        return response.lua_success

    async def assign_units(self, units: list["CActiveUnit | str"]) -> list[bool]:
        """
        分配多个单元

        Args:
            units (list[CActiveUnit | str]): 单元对象或单元guid

        Returns:
            list[bool]: 返回分配执行结果
        """
        results = []
        for v in units:
            cmd = f"ScenEdit_AssignUnitToMission('{v.guid if isinstance(v, CActiveUnit) else v}', '{self.name}')"
            self.mozi_server.throw_into_pool(cmd)
            response = await self.mozi_server.send_and_recv(cmd)
            results.append(response.lua_success)
        return results

    async def is_area_valid(self) -> bool:
        """
        验证区域角点连线是否存在交叉现象

        Returns:
            bool: 验证结果状态标识
                True: 正常
                False: 异常
        """
        lua_script = f"print(Hs_IsValidArea('{self.name}'))"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.raw_data.lower() == "yes"

    async def unassign_unit(self, active_unit_name_guid: str) -> bool:
        """
        单元从任务中移除

        Args:
            active_unit_name_guid (str): 活动单元guid或名称

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_UnAssignUnitFromMission('{active_unit_name_guid}','{self.name}')"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @validate_literal_args
    async def set_throttle(
        self,
        throttle_type: Literal[
            "transitThrottleAircraft",  # 飞机出航油门
            "stationThrottleAircraft",  # 飞机阵位油门
            "attackThrottleAircraft",  # 飞机攻击油门
            "transitThrottleShip",  # 水面舰艇出航油门
            "stationThrottleShip",  # 水面舰艇阵位油门
            "attackThrottleShip",  # 水面舰艇攻击油门
            "transitThrottleSubmarine",  # 潜艇出航油门
            "stationThrottleSubmarine",  # 潜艇阵位油门
        ],
        throttle: "Throttle",
    ) -> bool:
        """
        设置任务油门类型及值

        Args:
            - throttle_type (str): 油门类型
                - "transitThrottleAircraft": 飞机出航油门
                - "stationThrottleAircraft": 飞机阵位油门
                - "attackThrottleAircraft": 飞机攻击油门
                - "transitThrottleShip": 水面舰艇出航油门
                - "stationThrottleShip": 水面舰艇阵位油门
                - "attackThrottleShip": 水面舰艇攻击油门
                - "transitThrottleSubmarine": 潜艇出航油门
                - "stationThrottleSubmarine": 潜艇阵位油门
            - throttle (Throttle): 油门

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.guid}', {{'{throttle_type}' = '{throttle.value}'}}) "
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    @validate_literal_args
    async def set_altitude(
        self,
        altitude_type: Literal["transitAltitudeAircraft", "stationAltitudeAircraft", "attackAltitudeAircraft"],
        altitude: float,
    ) -> bool:
        """
        设置任务高度类型及值

        Args:
            - altitude_type (str): 高度类型
                - "transitAltitudeAircraft": 出航高度
                - "stationAltitudeAircraft": 阵位高度
                - "attackAltitudeAircraft": 攻击高度
            - altitude (float): 高度值，单位：米
                - 会被格式化为最多6位字符的字符串，例：99999.9， 888888  # TODO: 这个格式化规则是否正确？

        Returns:
            bool: 执行结果
        """

        def format_altitude(alt: float) -> str:
            if alt.is_integer():
                return str(int(alt))
            s = f"{alt:.1f}"
            return str(round(alt)) if len(s) > 6 else s

        cmd = f"ScenEdit_SetMission('{self.side}','{self.guid}', {{{altitude_type}={format_altitude(altitude)}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    @validate_literal_args
    async def add_plan_way_to_mission(self, way_type: Literal[0, 1, 2, 3], way_name_or_id: str) -> bool:
        """
        为任务分配预设航线

        Args:
            - way_type (int): 航线类型
                - 0: 单元出航航线
                - 1: 武器航线
                - 2: 返航航线
                - 3: 巡逻航线
            - way_name_or_id (str): 航线名称或guid

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(f"Hs_AddPlanWayToMission('{self.name}',{way_type},'{way_name_or_id}')")
        return response.lua_success

    async def add_plan_way_to_target(self, way_name_or_id: str, target_name_or_id: str) -> bool:
        """
        武器打击目标预设航线

        Args:
            - way_name_or_id (str): 武器航线名称或guid
            - target_name_or_id (str): 目标名称或guid

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_AddPlanWayToMissionTarget('{self.name}','{way_name_or_id}','{target_name_or_id}')"
        )
        return response.lua_success

    @validate_literal_args
    async def set_use_refuel_unrep(self, use_refuel_unrep: Literal[0, 1, 2]) -> bool:
        """
        设置空中加油

        Args:
            - use_refuel_unrep (int)
                - 0: 允许但不允许给加油机加油
                - 1: 不允许
                - 2: 允许

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.guid}', {{use_refuel_unrep={use_refuel_unrep}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    @validate_literal_args
    async def set_submarine_depth(
        self, depth_type: Literal["transitDepthSubmarine", "stationDepthSubmarine"], depth: float
    ) -> bool:
        """
        设置潜艇潜深 - 仅支持扫雷、布雷、支援和巡逻任务

        Args:
            - depth_type (str): 深度类型
                - "transitDepthSubmarine": 出航潜深
                - "stationDepthSubmarine": 阵位潜深
            - depth (float): 深度 单位米

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.guid}', {{'{depth_type}' = {depth}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def export_mission(self) -> bool:
        """
        将相应的任务导出到 Defaults 文件夹中

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(f"ScenEdit_ExportMission('{self.side}','{self.guid}')")
        return response.lua_success
