from mozi_ai_x.utils.validator import validate_literal_args, validate_uuid4_args
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .server import MoziServer
    from .weather import CWeather
    from .response import CResponse
    from .weapon_impact import CWeaponImpact
    from .sim_event import CSimEvent
    from .side import CSide
    from .active_unit import CActiveUnit

from .situation import CSituation
from .situ_interpret import CCurrentScenarioDict
from .base import BaseObject


class CScenario(BaseObject):
    """想定"""

    def __init__(self, mozi_server: "MoziServer"):
        self.mozi_server = mozi_server
        self.name = ""
        # GUID
        self.guid = ""
        # 标题
        self.title = ""
        # 想定文件名
        self.scene_file_name = ""
        # 描述
        self.description = ""
        # 当前时间
        self.time = ""
        # 是否是夏令时
        self.daylight_saving_time = False
        # 当前想定第一次启动的开始时间
        self.first_time_run_datetime = ""
        # 用不上
        self.first_time_last_processed = 0.0
        # 用不上
        self.grand_time_last_processed = 0.0
        # 夏令时开始时间（基本不用）
        self.daylight_saving_time_start = 0.0
        # 夏令结束时间（基本不用）
        self.daylight_saving_time_end = 0.0
        # 想定开始时间
        self.star_time = ""
        # 想定持续时间
        self.duration = ""
        # 想定精细度
        self.meat_complexity = 1
        # 想定困难度
        self.meta_difficulty = 1
        # 想定发生地
        self.meta_scene_setting = ""
        # 想定精细度的枚举类集合
        self.declared_features = ""
        # 想定的名称
        self.custom_file_name = ""
        # 编辑模式剩余时间
        self.edit_count_down = 0
        # 推演模式剩余时间
        self.start_count_down = 0
        # 暂停剩余时间
        self.suspend_count_down = 0
        # 获取推演的阶段模式
        self.current_stage = 0
        # 态势
        self.situation = CSituation(mozi_server)

        self.guid_str = ""  # GUID字符串形式 (映射到 strGuid)

        self.var_map = CCurrentScenarioDict.var_map

    @property
    def sides(self):
        return self.situation.side_dict

    def get_title(self) -> str:
        """
        获取想定标题

        Returns:
            str: 想定标题
        """
        return self.title

    def get_weather(self) -> "CWeather | None":
        """
        获取天气条件

        Returns:
            CWeather: 天气条件
        """
        return self.situation.weather

    @property
    def weather(self) -> "CWeather | None":
        """
        获取天气条件

        Returns:
            CWeather: 天气条件
        """
        return self.situation.weather

    def get_responses(self) -> dict:
        """
        获取仿真响应信息。

        Returns:
            dict: 仿真响应信息
                格式 {response_guid:response_obj,response_guid_2:response_obj_2, ...}
        """
        return self.situation.response_dict

    @property
    def responses(self) -> dict[str, "CResponse"]:
        """
        获取仿真响应信息。

        Returns:
            dict: 仿真响应信息
                格式 {response_guid:response_obj,response_guid_2:response_obj_2, ...}
        """
        return self.situation.response_dict

    def get_weapon_impacts(self) -> dict[str, "CWeaponImpact"]:
        """
        获取所有武器冲击。

        Returns:
            dict: 所有武器冲击
                格式 {weapon_impact_guid:weapon_impact_obj,weapon_impact_guid_2:weapon_impact_obj_2, ...}
        """
        return self.situation.weapon_impact_dict

    @property
    def weapon_impacts(self) -> dict[str, "CWeaponImpact"]:
        """
        获取所有武器冲击。

        Returns:
            dict: 所有武器冲击
                格式 {weapon_impact_guid:weapon_impact_obj,weapon_impact_guid_2:weapon_impact_obj_2, ...}
        """
        return self.situation.weapon_impact_dict

    def get_events(self):
        """
        获取所有事件。

        Returns:
            dict: 所有事件
                格式 {event_guid:event_obj,event_guid_2:event_obj_2, ...}
        """
        return self.situation.simevent_dict

    @property
    def events(self) -> dict[str, "CSimEvent"]:
        """
        获取所有事件。

        Returns:
            dict: 所有事件
                格式 {event_guid:event_obj,event_guid_2:event_obj_2, ...}
        """
        return self.situation.simevent_dict

    def get_side_by_name(self, name) -> "CSide | None":
        """
        根据名字获取推演方信息

        Returns:
            CSide: 推演方对象
        """
        for side in self.situation.side_dict.values():
            if side.name == name:
                return side

    async def get_current_time(self) -> int:
        """
        获取当前想定时间

        Returns:
            int: 当前时间戳 example: 1626657722
        """
        lua = "ReturnObj(ScenEdit_CurrentTime())"
        response = await self.mozi_server.send_and_recv(lua)
        return int(response.raw_data)

    async def get_player_name(self) -> str:
        """
        获取当前推演方的名称

        Returns:
            str: 当前推演方名称
        """
        response = await self.mozi_server.send_and_recv("ReturnObj(ScenEdit_PlayerSide())")
        return response.raw_data

    async def get_side_posture(self, side_a: str, side_b: str) -> Literal["F", "H", "N", "U"]:
        """
        获取一方side_a对另一方side_b的立场

        Args:
            side_a (str): 推演方名称
            side_b (str): 推演方名称

        Returns:
            Literal["F", "H", "N", "U"]: 立场编码
        """
        response = await self.mozi_server.send_and_recv(f"ReturnObj(ScenEdit_GetSidePosture('{side_a}','{side_b}'))")
        if response.raw_data in ["F", "H", "N", "U"]:
            return response.raw_data.upper()  # type: ignore
        else:
            raise ValueError(f"Invalid side posture: {response.raw_data}")

    def get_units_by_name(self, name: str) -> dict[str, "CActiveUnit"]:
        """
        从上帝视角用名称获取单元。
        限制：专项赛禁用

        Args:
            name (str): 单元名称

        Returns:
            活动单元字典 格式 {active_unit_guid:active_unit_obj,active_unit_guid_2:active_unit_obj_2...}
        """
        units = {}
        submarines = {k: v for k, v in self.situation.submarine_dict.items() if v.name == name}
        ships = {k: v for k, v in self.situation.ship_dict.items() if v.name == name}
        facilities = {k: v for k, v in self.situation.facility_dict.items() if v.name == name}
        aircrafts = {k: v for k, v in self.situation.aircraft_dict.items() if v.name == name}
        satellites = {k: v for k, v in self.situation.satellite_dict.items() if v.name == name}
        weapons = {k: v for k, v in self.situation.weapon_dict.items() if v.name == name}
        unguided_weapons = {k: v for k, v in self.situation.unguided_weapon_dict.items() if v.name == name}
        units.update(submarines)
        units.update(ships)
        units.update(facilities)
        units.update(aircrafts)
        units.update(satellites)
        units.update(weapons)
        units.update(unguided_weapons)
        return units

    @validate_uuid4_args(["guid"])
    def unit_is_alive(self, guid: str) -> bool:
        """
        从上帝视角用guid判断实体单元是否存在
        限制：专项赛禁用

        Args:
            guid (str): 单元guid

        Returns:
            bool: 是否存在
        """
        return guid in self.situation.all_guid

    async def add_side(self, side_name: str) -> bool:
        """
        添加方
        限制：专项赛禁用

        Args:
            side_name (str): 推演方名字

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(f"HS_LUA_AddSide({{side='{side_name}'}})")
        return response.lua_success

    async def remove_side(self, side: str) -> bool:
        """
        移除推演方
        限制：专项赛禁用

        Args:
            side (str): 推演方名字

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(f"ScenEdit_RemoveSide({{side='{side}'}})")
        return response.lua_success

    @validate_literal_args
    async def set_side_posture(self, side_a: str, side_b: str, relation: Literal["F", "H", "N", "U"]) -> bool:
        """
        设置一方对另一方的立场
        限制：专项赛禁用

        Args:
            side_a (str): 推演方名字
            side_b (str): 推演方名字
            relation (Literal["F", "H", "N", "U"]): 立场编码

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(f"ScenEdit_SetSidePosture('{side_a}','{side_b}','{relation}')")
        return response.lua_success

    async def reset_all_sides_scores(self) -> bool:
        """
        重置所有推演方分数
        限制：专项赛禁用

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv("Hs_ResetAllSideScores()")
        return response.lua_success

    async def reset_all_losses_expenditures(self) -> bool:
        """
        将各推演方所有战斗损失、战斗消耗、单元损伤等均清零。
        限制：专项赛禁用

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv("Hs_ResetAllLossesExpenditures()")
        return response.lua_success

    async def set_scenario_time(
        self,
        current_time: str | None = None,
        start_time: str | None = None,
        set_duration: str | None = None,
        complexity: Literal[1, 2, 3, 4, 5] | None = None,
        difficulty: Literal[1, 2, 3, 4, 5] | None = None,
        address_setting: str | None = None,
    ) -> bool:
        """
        设置当前想定的起始时间，当前时间，持续事时间、想定复杂度、想定难度，想定地点等
        限制：专项赛禁用

        Args:
            current_time (str | None): 想定当前时间 {str: 格式'2020/8/10 10:12:2'}
            start_time (str | None):   想定起始时间 {str: 格式'2020/8/10 10:12:2'} 开始时间不能晚于当前时间
            set_duration (str | None): 想定持续时间 {str: '1-10-16' 表示1天10小时16分钟}
            complexity (int | None): 想定复杂度 {int: 1-5 5个复杂等级}
            difficulty (int | None): 想定难度 {int: 1-5 5个难度等级}
            address_setting (str | None): 想定发生地点 {str: 想定发生地点}

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if current_time:
            update_str += f", ScenarioTime='{current_time}'"
        if start_time:
            update_str += f", ScenarioStartTime='{start_time}'"
        if set_duration:
            update_str += f", ScenarioSetDuration='{set_duration}'"
        if complexity:
            update_str += f", ScenarioComplexity={complexity}"
        if difficulty:
            update_str += f", ScenarioDifficulty={difficulty}"
        if address_setting:
            update_str += f", ScenarioScenSetting='{address_setting}'"
        if update_str:
            update_str = update_str[1:]
        lua_script = f"Hs_SetScenarioTime({{{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def change_unit_side(self, unit_name: str, side_a: str, side_b: str) -> bool:
        """
        改变单元的方
        限制：专项赛禁用

        Args:
            unit_name (str): 单元名称
            side_a (str): 推演方名称
            side_b (str): 推演方名称

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_SetUnitSide({{name='{unit_name}',side='{side_a}',newside='{side_b}'}})"
        )
        return response.lua_success

    async def dump_rules(self) -> bool:
        """
        向系统安装目录下想定默认文件夹以 xml 文件的方式导出事件、条件、触发器、动作、特殊动作。
        限制：专项赛禁用

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv("Tool_DumpEvents()")
        return response.lua_success

    async def set_description(self, scenario_title: str, description: str) -> bool:
        """
        设置想定标题和描述
        限制：专项赛禁用

        Args:
            scenario_title (str): 想定标题
            description (str): 想定描述

        Returns:
            bool: 执行结果
        """
        lua_script = f"Hs_SetScenarioDescribe({{ScenarioTitle='{scenario_title}',SetDescription='{description}'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def set_fineness(
        self,
        detailed_gun_fire_control: bool | None = None,
        unlimited_base_mags: bool | None = None,
        aircraft_damage: bool | None = None,
        comms_jamming: bool | None = None,
        comms_disruption: bool | None = None,
        ballistic_missile: bool | None = None,
    ) -> bool:
        """
        设置想定精细度
        限制：专项赛禁用

        Args:
            detailed_gun_fire_control (bool | None): 是否使用高精度火控算法
            unlimited_base_mags (bool | None): 是否海/空弹药库不受限
            aircraft_damage (bool | None): 是否使用飞机高精度毁伤模型
            comms_jamming (bool | None): 是否使用通信干扰
            comms_disruption (bool | None): 是否使用通信摧毁
            ballistic_missile (bool | None): 是否使用弹道导弹精细模型

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if detailed_gun_fire_control:
            update_str += f", DetailedGunFirControl={str(detailed_gun_fire_control).lower()}"
        if unlimited_base_mags:
            update_str += f", UnlimitedBaseMags={str(unlimited_base_mags).lower()}"
        if aircraft_damage:
            update_str += f", AircraftDamage={str(aircraft_damage).lower()}"
        if comms_jamming:
            update_str += f", CommsJamming={str(comms_jamming).lower()}"
        if comms_disruption:
            update_str += f", CommsDisruption={str(comms_disruption).lower()}"
        if ballistic_missile:
            update_str += f", BallisticMissile={str(ballistic_missile).lower()}"

        if update_str:
            update_str = update_str[1:]

        lua_script = f"Hs_FeaturesReakismSet({{{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def set_cur_side_and_dir_view(self, side_name_or_guid: str, open_or_close_dir_view: bool) -> bool:
        """
        设置服务端当前推演方,便于用户观察态势。
        限制：专项赛禁用

        Args:
            side_name_or_guid (str): 推演方名称或guid
            open_or_close_dir_view (bool): 是否开启导演视图
                True - 是
                False - 否

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_SetCurSideAndDirView('{side_name_or_guid}',{str(open_or_close_dir_view).lower()})"
        )
        return response.lua_success

    async def end_scenario(self) -> bool:
        """
        终止当前想定，进入参演方评估并给出评估结果
        限制：专项赛禁用

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv("ScenEdit_EndScenario()")
        return response.lua_success

    async def save_scenario(self) -> bool:
        """
        保存当前已经加载的想定
        限制：专项赛禁用

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv("Hs_ScenEdit_SaveScenario()")
        return response.lua_success

    async def save_as(self, scenario_name: str) -> bool:
        """
        另存当前已经加载的想定
        限制：专项赛禁用

        Args:
            scenario_name (str): 想定名称

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(f"Hs_ScenEdit_SaveAsScenario('{scenario_name}')")
        return response.lua_success

    async def set_weather(
        self, average_temperature: float, rainfall_rate: float, fraction_under_rain: float, sea_state: int
    ) -> bool:
        """
        设置当前天气条件
        限制：专项赛禁用

        Args:
            average_temperature (float): 平均气温 {float: -50 ~ 50}
            rainfall_rate (float): 降水量 {float: 0 ~ 50 无雨~暴雨}
            fraction_under_rain (float): 天空云量 {float: 0 ~ 1.0 晴朗~多云}
            sea_state (int): 风力/海况 {int: 0 ~ 9 无风~飓风}

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetWeather({average_temperature}, {rainfall_rate}, {fraction_under_rain}, {sea_state})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @staticmethod
    def __generate_target_filter_str(target_filter_dict: dict) -> str:
        """
        将target_filter_dict转换成target_filter_str

        Args:
            - target_filter_dict (dict): 目标过滤字典
                - example: {TARGETSIDE='红方',TARGETTYPE=3,TARGETSUBTYPE=3204,SPECIFICUNITCLASS=1573,
                SPECIFICUNIT='016b72ba-2ab2-464a-a340-3cfbfb133ed1'}

        Returns:
            str: 目标过滤字符串
            example: TARGETSIDE='红方',TARGETTYPE=3,TARGETSUBTYPE=3204,SPECIFICUNITCLASS=1573,
                SPECIFICUNIT='016b72ba-2ab2-464a-a340-3cfbfb133ed1'
        """
        target_filter_str = ""
        target_filter_list = []
        for k, v in target_filter_dict.items():
            if k in ["TARGETSIDE", "SPECIFICUNIT"]:
                target_filter_list.append(f"{k}='{v}'")
            if k in ["TARGETSUBTYPE", "SPECIFICUNITCLASS"]:
                target_filter_list.append(f"{k}={v}")
            if k in ["TARGETTYPE"]:
                if isinstance(v, int):
                    target_filter_list.append(f"{k}={v}")
                else:
                    target_filter_list.append(f"{k}='{v}'")
        if target_filter_list:
            target_filter_str = ",".join(target_filter_list)
        return target_filter_str

    async def add_trigger_unit_destroyed(self, name: str, target_filter_dict: dict) -> bool:
        """
        添加单元被摧毁触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - target_filter_dict (dict):
                - TARGETSIDE-str-推演方名称，
                - TARGETTYPE
                    - int: 类型ID
                        - 0 = NoneValue
                        - 1 = AircraftType
                        - 2 = ShipType
                        - 3 = SubmarineType
                        - 4 = FacilityType
                        - 5 = Aimpoint
                        - 6 = WeaponType
                        - 7 = SatelliteType
                    - str
                        - Aircraft: 飞机
                        - Ship: 水面舰艇
                        - Submarine: 潜艇
                        - Facility: 地面兵力与设施
                - TARGETSUBTYPE-int-数据库中的类型ID
                - SPECIFICUNITCLASS-目标数据库DBID
                - SPECIFICUNIT-实际单元名称或GUID}
                - example: `{'TARGETSIDE': '红方', 'TARGETTYPE': 1, 'TARGETSUBTYPE': 6002, 'SPECIFICUNITCLASS': 2802}`

        Returns:
            bool: 执行结果
        """
        target_filter_str = self.__generate_target_filter_str(target_filter_dict)
        if not target_filter_str:
            raise ValueError("target_filter_dict不合法")

        lua_script = (
            f"ScenEdit_SetTrigger({{name='{name}',Mode='add',Type='unitdestroyed',TargetFilter={{{target_filter_str}}}}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_trigger_unit_destroyed(
        self, name: str, rename: str | None = None, target_filter_dict: dict | None = None
    ) -> bool:
        """
        更新单元被摧毁触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - rename (str | None): 新的触发器名称
            - target_filter_dict (dict | None):
                - TARGETSIDE-str-推演方名称，
                - TARGETTYPE
                    - int: 类型ID
                        - 0 = NoneValue
                        - 1 = AircraftType
                        - 2 = ShipType
                        - 3 = SubmarineType
                        - 4 = FacilityType
                        - 5 = Aimpoint
                        - 6 = WeaponType
                        - 7 = SatelliteType
                    - str
                        - Aircraft: 飞机
                        - Ship: 水面舰艇
                        - Submarine: 潜艇
                        - Facility: 地面兵力与设施
                - TARGETSUBTYPE-int-数据库中的类型ID
                - SPECIFICUNITCLASS-目标数据库DBID
                - SPECIFICUNIT-实际单元名称或GUID
                - example: `{'TARGETSIDE': '红方', 'TARGETTYPE': 1, 'TARGETSUBTYPE': 6002, 'SPECIFICUNITCLASS': 2802}`

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if target_filter_dict:
            target_filter_str = self.__generate_target_filter_str(target_filter_dict)
            if not target_filter_str:
                raise ValueError("target_filter_dict 不合法")
            update_str += f", TargetFilter={{{target_filter_str}}}"
        if rename:
            update_str += f", rename='{rename}'"

        lua_script = f"ScenEdit_SetTrigger({{name='{name}',Mode='update',Type='unitdestroyed'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_trigger_unit_damaged(self, name: str, target_filter_dict: dict, damage_percent: int) -> bool:
        """
        添加单元被毁伤触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - target_filter_dict (dict):
                - TARGETSIDE-str-推演方名称
                - TARGETTYPE
                    - int: 类型ID
                        - 0 = NoneValue
                        - 1 = AircraftType
                        - 2 = ShipType
                        - 3 = SubmarineType
                        - 4 = FacilityType
                        - 5 = Aimpoint
                        - 6 = WeaponType
                        - 7 = SatelliteType
                    - str
                        - Aircraft: 飞机
                        - Ship: 水面舰艇
                        - Submarine: 潜艇
                        - Facility: 地面兵力与设施
                - TARGETSUBTYPE-int-数据库中的类型ID
                - SPECIFICUNITCLASS-目标数据库DBID
                - SPECIFICUNIT-实际单元名称或GUID
                - example: `{'TARGETSIDE': '红方', 'TARGETTYPE': 1, 'TARGETSUBTYPE': 6002, 'SPECIFICUNITCLASS': 2802}`
            - damage_percent (int): 毁伤百分比

        Returns:
            bool: 执行结果
        """
        target_filter_str = self.__generate_target_filter_str(target_filter_dict)
        if not target_filter_str:
            raise ValueError("target_filter_dict不合法")

        lua_script = (
            f"ScenEdit_SetTrigger({{name='{name}',Mode='add',Type='UnitDamaged',"
            f"TargetFilter={{{target_filter_str}}},DamagePercent={damage_percent}}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_trigger_unit_damaged(
        self,
        name: str,
        rename: str | None = None,
        target_filter_dict: dict | None = None,
        damage_percent: int | None = None,
    ) -> bool:
        """
        更新单元被毁伤触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - rename (str | None): 新的触发器名称
            - target_filter_dict (dict | None):
                - TARGETSIDE-str-推演方名称，
                - TARGETTYPE
                    - int: 类型ID
                        - 0 = NoneValue
                        - 1 = AircraftType
                        - 2 = ShipType
                        - 3 = SubmarineType
                        - 4 = FacilityType
                        - 5 = Aimpoint
                        - 6 = WeaponType
                        - 7 = SatelliteType
                    - str
                        - Aircraft: 飞机
                        - Ship: 水面舰艇
                        - Submarine: 潜艇
                        - Facility: 地面兵力与设施
                - TARGETSUBTYPE-int-数据库中的类型ID
                - SPECIFICUNITCLASS-目标数据库DBID
                - SPECIFICUNIT-实际单元名称或GUID
                - example: `{'TARGETSIDE': '红方', 'TARGETTYPE': 1, 'TARGETSUBTYPE': 6002, 'SPECIFICUNITCLASS': 2802}`
            - damage_percent (int | None): 毁伤百分比

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if target_filter_dict:
            target_filter_str = self.__generate_target_filter_str(target_filter_dict)
            if not target_filter_str:
                raise ValueError("target_filter_dict不合法")
            update_str += f", TargetFilter={{{target_filter_str}}}"
        if rename:
            update_str += f", rename='{rename}'"
        if damage_percent:
            update_str += f", DamagePercent={damage_percent}"

        lua_script = f"ScenEdit_SetTrigger({{name='{name}',Mode='update',Type='UnitDamaged'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @validate_literal_args
    async def add_trigger_points(self, name: str, side: str, point_value: int, reach_direction: Literal[0, 1, 2]) -> bool:
        """
        添加推演方得分触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - side (str): 推演方名称
            - point_value (int): 推演方分数
            - reach_direction (int):
                - 0: 超过
                - 1: 刚好达到
                - 2: 低于

        Returns:
            bool: 执行结果
        """
        lua_script = (
            f"ScenEdit_SetTrigger({{name='{name}',Mode='add',Type='Points',"
            f"SideID='{side}', PointValue={point_value}, ReachDirection={reach_direction}}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_trigger_points(
        self,
        name: str,
        rename: str | None = None,
        side: str | None = None,
        point_value: int | None = None,
        reach_direction: Literal[0, 1, 2] | None = None,
    ) -> bool:
        """
        编辑推演方得分触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - rename (str | None): 新的触发器名称
            - side (str | None): 推演方名称
            - point_value (int | None): 推演方分数
            - reach_direction (int | None):
                - 0: 超过
                - 1: 刚好达到
                - 2: 低于

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if rename:
            update_str += f", rename='{rename}'"
        if side:
            update_str += f", SideID='{side}'"
        if point_value:
            update_str += f", PointValue={point_value}"
        if reach_direction:
            update_str += f", ReachDirection={reach_direction}"
        lua_script = f"ScenEdit_SetTrigger({{name='{name}',Mode='update',Type='Points'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_trigger_time(self, name: str, time: str) -> bool:
        """
        添加时间触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - time (str): 格式 2019/8/10 10:1:21，实际设置的时间为设置时间+8小时

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetTrigger({{name='{name}',Mode='add',Type='time',Time='{time}'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_trigger_time(
        self,
        name: str,
        rename: str | None = None,
        time: str | None = None,
    ) -> bool:
        """
        更新时间触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - rename (str | None): 新的触发器名称
            - time (str | None): 格式 2019/8/10 10:1:21，实际设置的时间为设置时间

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if rename:
            update_str += f", rename='{rename}'"
        if time:
            update_str += f", Time='{time}'"

        lua_script = f"ScenEdit_SetTrigger({{name='{name}',Mode='update',Type='time'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_trigger_unit_remains_in_area(self, name: str, target_filter_dict: dict, area: list, stay_time: str) -> bool:
        """
        添加单元停留在区域内触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - target_filter_dict (dict):
                - TARGETSIDE-str-推演方名称，
                - TARGETTYPE
                    - int: 类型ID
                        - 0 = NoneValue
                        - 1 = AircraftType
                        - 2 = ShipType
                        - 3 = SubmarineType
                        - 4 = FacilityType
                        - 5 = Aimpoint
                        - 6 = WeaponType
                        - 7 = SatelliteType
                    - str
                        - Aircraft：飞机
                        - Ship：水面舰艇
                        - Submarine：潜艇
                        - Facility：地面兵力与设施
                - TARGETSUBTYPE-int-数据库中的类型ID
                - SPECIFICUNITCLASS-目标数据库DBID
                - SPECIFICUNIT-实际单元名称或GUID
                - example: `{'TARGETSIDE': '红方', 'TARGETTYPE': 1, 'TARGETSUBTYPE': 6002, 'SPECIFICUNITCLASS': 2802}`
            - area (list): 参考点名称列表
            - stay_time (str): 格式'1:2:3:4' （'天:小时:分:秒'）

        Returns:
            bool: 执行结果
        """
        target_filter_str = self.__generate_target_filter_str(target_filter_dict)
        if not target_filter_str:
            raise ValueError("target_filter_dict不合法")

        area_str = str(area).replace("[", "").replace("]", "")

        lua_script = (
            f"ScenEdit_SetTrigger({{name='{name}',Mode='add',Type='UnitRemainsInArea',"
            f"TargetFilter={{{target_filter_str}}}, Area={{{area_str}}}, TD='{stay_time}'}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_trigger_unit_remains_in_area(
        self,
        name: str,
        rename: str | None = None,
        target_filter_dict: dict | None = None,
        area: list[str] | None = None,
        stay_time: str | None = None,
    ) -> bool:
        """
        编辑单元停留在区域内触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - rename (str | None): 新的触发器名称
            - target_filter_dict (dict | None):
                - TARGETSIDE-str-推演方名称，
                - TARGETTYPE
                    - int: 类型ID
                        - 0 = NoneValue
                        - 1 = AircraftType
                        - 2 = ShipType
                        - 3 = SubmarineType
                        - 4 = FacilityType
                        - 5 = Aimpoint
                        - 6 = WeaponType
                        - 7 = SatelliteType
                    - str
                        - Aircraft：飞机
                        - Ship：水面舰艇
                        - Submarine：潜艇
                        - Facility：地面兵力与设施
                - TARGETSUBTYPE-int-数据库中的类型ID
                - SPECIFICUNITCLASS-目标数据库DBID
                - SPECIFICUNIT-实际单元名称或GUID
                - example: `{'TARGETSIDE': '红方', 'TARGETTYPE': 1, 'TARGETSUBTYPE': 6002, 'SPECIFICUNITCLASS': 2802}`
            - area (list | None): 参考点名称列表
            - stay_time (str | None): 格式'1:2:3:4' （'天:小时:分:秒'）

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if target_filter_dict:
            target_filter_str = self.__generate_target_filter_str(target_filter_dict)
            if not target_filter_str:
                raise ValueError("target_filter_dict不合法")
            update_str += f", TargetFilter={{{target_filter_str}}}"
        if rename:
            update_str += f", rename='{rename}'"
        if area:
            area_str = str(area).replace("[", "").replace("]", "")
            update_str += f", Area={{{area_str}}}"
        if stay_time:
            update_str += f", TD='{stay_time}'"

        lua_script = f"ScenEdit_SetTrigger({{name='{name}',Mode='update',Type='UnitRemainsInArea'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_trigger_unit_enters_area(
        self, name: str, target_filter_dict: dict, area: list[str], etoa: str, ltoa: str, trigger_if_not_in_area: bool
    ) -> bool:
        """
        添加单元进入区域触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - target_filter_dict (dict):
                - TARGETSIDE-str-推演方名称，
                - TARGETTYPE
                    - int: 类型ID
                        - 0 = NoneValue
                        - 1 = AircraftType
                        - 2 = ShipType
                        - 3 = SubmarineType
                        - 4 = FacilityType
                        - 5 = Aimpoint
                        - 6 = WeaponType
                        - 7 = SatelliteType
                    - str
                        - Aircraft: 飞机
                        - Ship: 水面舰艇
                        - Submarine: 潜艇
                        - Facility: 地面兵力与设施
                - TARGETSUBTYPE-int-数据库中的类型ID
                - SPECIFICUNITCLASS-目标数据库DBID
                - SPECIFICUNIT-实际单元名称或GUID
                - example: `{'TARGETSIDE': '红方', 'TARGETTYPE': 1, 'TARGETSUBTYPE': 6002, 'SPECIFICUNITCLASS': 2802}`
            - area (list): 参考点名称列表
            - etoa (str): 最早到达日期/时间 格式'2020/8/10 10:12:2'
            - ltoa (str): 最晚到达日期/时间 格式'2019/8/1 9:1:21'
            - trigger_if_not_in_area (bool): 'true'- 若单元不在区域内则触发, 'false'-若单元在区域内则触发

        Returns:
            bool: 执行结果
        """
        target_filter_str = self.__generate_target_filter_str(target_filter_dict)
        if not target_filter_str:
            raise ValueError("target_filter_dict不合法")

        area_str = str(area).replace("[", "").replace("]", "")

        lua_script = (
            f"ScenEdit_SetTrigger({{name='{name}',Mode='add',Type='unitentersarea',"
            f"TargetFilter={{{target_filter_str}}}, Area={{{area_str}}},"
            f"ETOA='{etoa}', LTOA='{ltoa}', NOT={trigger_if_not_in_area}}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_trigger_unit_enters_area(
        self,
        name: str,
        rename: str | None = None,
        target_filter_dict: dict | None = None,
        area: list[str] | None = None,
        etoa: str | None = None,
        ltoa: str | None = None,
        trigger_if_not_in_area: bool | None = None,
    ) -> bool:
        """
        更新单元进入区域触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - rename (str | None): 新的触发器名称
            - target_filter_dict (dict | None):
                - TARGETSIDE-str-推演方名称，
                - TARGETTYPE
                    - int: 类型ID
                        - 0 = NoneValue
                        - 1 = AircraftType
                        - 2 = ShipType
                        - 3 = SubmarineType
                        - 4 = FacilityType
                        - 5 = Aimpoint
                        - 6 = WeaponType
                        - 7 = SatelliteType
                    - str
                        - Aircraft：飞机
                        - Ship：水面舰艇
                        - Submarine：潜艇
                        - Facility：地面兵力与设施
                - TARGETSUBTYPE-int-数据库中的类型ID
                - SPECIFICUNITCLASS-目标数据库DBID
                - SPECIFICUNIT-实际单元名称或GUID
                - 例子：`{'TARGETSIDE': '红方', 'TARGETTYPE': 1, 'TARGETSUBTYPE': 6002, 'SPECIFICUNITCLASS': 2802}`
            - area (list): 参考点名称列表
            - etoa (str): 最早到达日期/时间 格式'2020/8/10 10:12:2'
            - ltoa (str): 最晚到达日期/时间 格式'2019/8/1 9:1:21'
            - trigger_when_not_in_area (str): 'true'- 若单元不在区域内则触发, 'false'-若单元在区域内则触发

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if target_filter_dict:
            target_filter_str = self.__generate_target_filter_str(target_filter_dict)
            if not target_filter_str:
                raise ValueError("target_filter_dict不合法")
            update_str += f", TargetFilter={{{target_filter_str}}}"
        if rename:
            update_str += f", rename='{rename}'"
        if area:
            area_str = str(area).replace("[", "").replace("]", "")
            update_str += f", Area={{{area_str}}}"
        if etoa:
            update_str += f", ETOA='{etoa}'"
        if ltoa:
            update_str += f", LTOA='{ltoa}'"
        if trigger_if_not_in_area:
            update_str += f", NOT={trigger_if_not_in_area}"

        lua_script = f"ScenEdit_SetTrigger({{name='{name}',Mode='update',Type='unitentersarea'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_trigger_random_time(self, name: str, earliest_time: str, latest_time: str) -> bool:
        """
        添加随机时间触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - earliest_time (str): 开始检查的最早日期/时间 格式'2019/8/2 9:31:21'
            - latest_time (str): 停止检查的最晚日期/时间 格式'2019/8/9 10:31:21'

        Returns:
            bool: 执行结果
        """
        lua_script = (
            f"ScenEdit_SetTrigger({{name='{name}',Mode='add',Type='RandomTime',"
            f"EarliestTime='{earliest_time}', LatestTime='{latest_time}'}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_trigger_random_time(
        self, name: str, rename: str | None = None, earliest_time: str | None = None, latest_time: str | None = None
    ) -> bool:
        """
        编辑随机时间触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - rename (str | None): 新的触发器名称
            - earliest_time (str | None): 开始检查的最早日期/时间 格式'2019/8/2 9:31:21'  # 显示时间-设置时间=4小时
            - latest_time (str | None): 停止检查的最晚日期/时间 格式'2019/8/9 10:31:21'  # 显示时间-设置时间=4小时

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if rename:
            update_str += f", rename='{rename}'"
        if earliest_time:
            update_str += f", EarliestTime='{earliest_time}'"
        if latest_time:
            update_str += f", LatestTime='{latest_time}'"

        lua_script = f"ScenEdit_SetTrigger({{name='{name}',Mode='update',Type='RandomTime'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_trigger_scen_loaded(self, name: str) -> bool:
        """
        添加想定被加载触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetTrigger({{name='{name}',Mode='add',Type='scenloaded'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_trigger_scen_loaded(self, old_name: str, new_name: str) -> bool:
        """
        编辑想定被加载触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - rename (str): 新的触发器名称

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetTrigger({{name='{old_name}',Mode='update',Type='scenloaded', rename='{new_name}'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @validate_literal_args
    async def add_trigger_regular_time(self, name: str, interval: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]) -> bool:
        """
        添加规律时间触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - interval (int): 秒
                - 0-1秒
                - 1-5秒
                - 2-15秒
                - 3-30秒
                - 4-1分钟
                - 5-5分钟
                - 6-15分钟
                - 7-30分钟
                - 8-1小时
                - 9-6小时
                - 10-6小时
                - 11-24小时
                - 12-0.1秒（高精度模式可用）
                - 13-0.5秒（高经度模式可用）

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetTrigger({{name='{name}',Mode='add',Type='regulartime',Interval={interval}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_trigger_regular_time(
        self,
        old_name: str,
        new_name: str | None = None,
        interval: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] | None = None,
    ) -> bool:
        """
        编辑规律时间触发器
        限制：专项赛禁用

        Args:
            - old_name (str): 触发器名称
            - new_name (str | None): 新的触发器名称
            - interval (int | None): 秒
                - 0-1秒
                - 1-5秒
                - 2-15秒
                - 3-30秒
                - 4-1分钟
                - 5-5分钟
                - 6-15分钟
                - 7-30分钟
                - 8-1小时
                - 9-6小时
                - 10-6小时
                - 11-24小时
                - 12-0.1秒（高精度模式可用）
                - 13-0.5秒（高经度模式可用）

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if new_name:
            update_str += f", rename='{new_name}'"
        if interval:
            update_str += f", Interval={interval}"

        lua_script = f"ScenEdit_SetTrigger({{name='{old_name}',Mode='update',Type='regulartime'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @validate_literal_args
    async def add_trigger_unit_detected(
        self, name: str, target_filter_dict: dict, detector_side: str, mcl: Literal[0, 1, 2, 3, 4]
    ) -> bool:
        """
        添加单元被探测到触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - target_filter_dict (dict):
                - TARGETSIDE (str): 推演方名称
                - TARGETTYPE (int | str): 类型ID
                    - 0 = NoneValue
                    - 1 = AircraftType
                    - 2 = ShipType
                    - 3 = SubmarineType
                    - 4 = FacilityType
                    - 5 = Aimpoint
                    - 6 = WeaponType
                    - 7 = SatelliteType
                    - Aircraft: 飞机
                    - Ship: 水面舰艇
                    - Submarine: 潜艇
                    - Facility: 地面兵力与设施
                - TARGETSUBTYPE (int): 数据库中的类型ID
                - SPECIFICUNITCLASS (int): 目标数据库DBID
                - SPECIFICUNIT (str): 实际单元名称或GUID
                例子：{'TARGETSIDE': '红方', 'TARGETTYPE': 1, 'TARGETSUBTYPE': 6002, 'SPECIFICUNITCLASS': 2802}
            - detector_side (str): 探测推演方
            - mcl (int): 最小分类级别
                - 0-不明
                - 1-知道领域(舰艇、飞机)
                - 2-知道类型（护卫舰，轰炸机）
                - 3-知道型号（F-16）
                - 4-具体ID

        Returns:
            bool: 执行结果
        """
        target_filter_str = self.__generate_target_filter_str(target_filter_dict)
        if not target_filter_str:
            raise ValueError("target_filter_dict不合法")

        lua_script = (
            f"ScenEdit_SetTrigger({{name='{name}',Mode='add',Type='UnitDetected',"
            f"TargetFilter={{{target_filter_str}}}, DetectorSideID='{detector_side}',"
            f"MCL={mcl}}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_trigger_unit_detected(
        self,
        old_name: str,
        new_name: str | None = None,
        target_filter_dict: dict | None = None,
        detector_side: str | None = None,
        mcl: Literal[0, 1, 2, 3, 4] | None = None,
    ) -> bool:
        """
        更新单元被探测到触发器
        限制：专项赛禁用

        Args:
            - old_name (str): 触发器名称
            - new_name (str | None): 新的触发器名称
            - target_filter_dict (dict | None):
                - TARGETSIDE (str): 推演方名称
                - TARGETTYPE (int | str): 类型ID
                    - 0 = NoneValue
                    - 1 = AircraftType
                    - 2 = ShipType
                    - 3 = SubmarineType
                    - 4 = FacilityType
                    - 5 = Aimpoint
                    - 6 = WeaponType
                    - 7 = SatelliteType
                    - Aircraft: 飞机
                    - Ship: 水面舰艇
                    - Submarine: 潜艇
                    - Facility: 地面兵力与设施
                - TARGETSUBTYPE (int): 数据库中的类型ID
                - SPECIFICUNITCLASS (int): 目标数据库DBID
                - SPECIFICUNIT (str): 实际单元名称或GUID
                例子：{'TARGETSIDE': '红方', 'TARGETTYPE': 1, 'TARGETSUBTYPE': 6002, 'SPECIFICUNITCLASS': 2802}
            - detector_side (str): 探测推演方
            - mcl (int): 最小分类级别
                - 0-不明
                - 1-知道领域(舰艇、飞机)
                - 2-知道类型（护卫舰，轰炸机）
                - 3-知道型号（F-16）
                - 4-具体ID
        """
        update_str = ""
        if target_filter_dict:
            target_filter_str = self.__generate_target_filter_str(target_filter_dict)
            if not target_filter_str:
                raise ValueError("target_filter_dict不合法")
            update_str += f", TargetFilter={{{target_filter_str}}}"
        if new_name:
            update_str += f", rename='{new_name}'"
        if detector_side:
            update_str += f", DetectorSideID='{detector_side}'"
        if mcl:
            update_str += f", MCL={mcl}"

        lua_script = f"ScenEdit_SetTrigger({{name='{old_name}',Mode='update',Type='UnitDetected'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def remove_trigger(self, name: str) -> bool:
        """
        删除触发器
        限制：专项赛禁用
        其他信息：如果触发器分配给了某事件，必须移除该事件才能移除该触发器

        Args:
            - name (str): 触发器名称

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetTrigger({{name='{name}',Mode='remove'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_action_points(self, name: str, side_name: str, point_change: int) -> bool:
        """
        添加推演方得分动作
        限制：专项赛禁用

        Args:
            - name (str): 动作名称
            - side_name (str): 推演方名称
            - point_change (int): 推演方得分变化

        Returns:
            bool: 执行结果
        """
        lua_script = (
            f"ScenEdit_SetAction({{name='{name}',Mode='add',Type='Points',SideID='{side_name}', PointChange={point_change}}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_action_points(
        self, name: str, rename: str | None = None, side_name: str | None = None, point_change: int | None = None
    ) -> bool:
        """
        编辑推演方得分动作
        限制：专项赛禁用

        Args:
            - name (str): 动作名称
            - rename (str | None): 新的动作名称
            - side_name (str | None): 推演方名称
            - point_change (int | None): 推演方得分变化

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if rename:
            update_str += f", rename='{rename}'"
        if side_name:
            update_str += f", SideID='{side_name}'"
        if point_change:
            update_str += f", PointChange={point_change}"
        lua_script = f"ScenEdit_SetAction({{name='{name}',Mode='update',Type='Points'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_action_end_scenario(self, name: str) -> bool:
        """
        添加终止想定动作
        限制：专项赛禁用

        Args:
            name:{str:动作名称}

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetAction({{name='{name}',Mode='add',Type='EndScenario'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_action_end_scenario(self, name: str, rename: str) -> bool:
        """
        编辑终止想定动作
        限制：专项赛禁用

        Args:
            - name (str): 动作名称
            - rename (str): 新的动作名称

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetAction({{name='{name}', rename='{rename}', Mode='update',Type='EndScenario'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_action_teleport_in_area(self, name: str, unit_list: list[str], area: list[str]) -> bool:
        """
        添加单元瞬时移动动作
        限制：专项赛禁用

        Args:
            - name (str): 动作名称
            - unit_list (list[str]): 单元名称或单元guid列表
            - area (list[str]): 参考点名称列表

        Returns:
            bool: 执行结果
        """
        area_str = str(area).replace("[", "").replace("]", "")
        unit_list_str = str(unit_list).replace("[", "").replace("]", "")
        lua_script = (
            f"ScenEdit_SetAction({{name='{name}',Mode='add',Type='TeleportInArea',"
            f"UnitIDs={{{unit_list_str}}}, Area={{{area_str}}}}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_action_teleport_in_area(
        self, name: str, rename: str | None = None, unit_list: list[str] | None = None, area: list[str] | None = None
    ) -> bool:
        """
        编辑单元瞬时移动动作
        限制：专项赛禁用

        Args:
            - name (str): 动作名称
            - rename (str | None): 新的动作名称
            - unit_list (list[str] | None): 单元名称或单元guid列表
            - area (list[str] | None): 参考点名称列表

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if rename:
            update_str += f", rename='{rename}'"
        if unit_list:
            unit_list_str = str(unit_list).replace("[", "").replace("]", "")
            update_str += f", UnitIDs={{{unit_list_str}}}"
        if area:
            area_str = str(area).replace("[", "").replace("]", "")
            update_str += f", Area={{{area_str}}}"

        lua_script = f"ScenEdit_SetAction({{name='{name}',Mode='update',Type='TeleportInArea'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_action_message(self, name: str, side: str, text: str) -> bool:
        """
        添加消息动作
        限制：专项赛禁用

        Args:
            - name (str): 动作名称
            - side (str): 推演方名称
            - text (str): 消息内容

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetAction({{name='{name}',Mode='add',Type='Message',SideID='{side}', text='{text}'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_action_message(
        self, name: str, rename: str | None = None, side: str | None = None, text: str | None = None
    ) -> bool:
        """
        编辑消息动作
        限制：专项赛禁用

        Args:
            - name (str): 动作名称
            - rename (str | None): 新的动作名称
            - side (str | None): 推演方名称
            - text (str | None): 消息内容

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if rename:
            update_str += f", rename='{rename}'"
        if side:
            update_str += f", SideID='{side}'"
        if text:
            update_str += f", text='{text}'"
        lua_script = f"ScenEdit_SetAction({{name='{name}',Mode='update',Type='Message'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_action_change_mission_status(self, name: str, side: str, mission: str, new_status: int) -> bool:
        """
        添加改变任务状态动作
        限制：专项赛禁用

        Args:
            - name (str): 动作名称
            - side (str): 推演方名称
            - mission (str): 任务名称
            - new_status (int): 0-激活，1-不激活

        Returns:
            bool: 执行结果
        """
        lua_script = (
            f"ScenEdit_SetAction({{name='{name}',Mode='add',Type='ChangeMissionStatus',"
            f"MissionID='{mission}', NewStatus={new_status}, SideID='{side}'}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_action_change_mission_status(
        self,
        name: str,
        rename: str | None = None,
        side: str | None = None,
        mission: str | None = None,
        new_status: int | None = None,
    ) -> bool:
        """
        编辑改变任务状态动作
        限制：专项赛禁用

        Args:
            - name (str): 动作名称
            - rename (str | None): 新的动作名称
            - side (str | None): 推演方名称
            - mission (str | None): 任务名称
            - new_status (int | None): 0-激活，1-不激活

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if rename:
            update_str += f", rename='{rename}'"
        if side:
            update_str += f", SideID='{side}'"
        if mission:
            update_str += f", MissionID='{mission}'"
        if new_status:
            update_str += f", NewStatus={new_status}"
        lua_script = f"ScenEdit_SetAction({{name='{name}',Mode='update',Type='ChangeMissionStatus'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_action_lua_script(self, name: str, script_text: str) -> bool:
        """
        添加执行lua脚本动作
        限制：专项赛禁用

        Args:
            - name (str): 动作名称
            - script_text (str): lua脚本

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetAction({{name='{name}',Mode='add',Type='LuaScript',ScriptText=\"{script_text}\"}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_action_lua_script(self, name: str, rename: str | None = None, script_text: str | None = None) -> bool:
        """
        编辑执行lua脚本动作
        限制：专项赛禁用

        Args:
            - name (str): 动作名称
            - rename (str | None): 新的动作名称
            - script_text (str | None): lua脚本

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if rename:
            update_str += f", rename='{rename}'"
        if script_text:
            update_str += f', ScriptText="{script_text}"'

        lua_script = f"ScenEdit_SetAction({{name='{name}',Mode='update',Type='LuaScript'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def remove_action(self, name: str) -> bool:
        """
        删除动作
        限制：专项赛禁用

        Args:
            - name (str): 动作名称

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetAction({{name='{name}',Mode='remove'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_event(self, name: str) -> bool:
        """
        添加事件
        限制：专项赛禁用

        Args:
            - name (str): 事件名称

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetEvent('{name}', {{Mode='add'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def remove_event(self, name: str) -> bool:
        """
        删除事件
        限制：专项赛禁用

        Args:
            - name (str): 事件名称

        Returns:
            bool: 执行结果
        返回：'lua执行成功' 或 '脚本执行出错'
        """
        lua_script = f"ScenEdit_SetEvent('{name}', {{Mode='remove'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def set_event_trigger(self, event_name: str, trigger_name: str) -> bool:
        """
        添加事件的触发器
        限制：专项赛禁用

        Args:
            - event_name (str): 事件名称
            - trigger_name (str): 触发器名称

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetEventTrigger('{event_name}', {{Mode='add', name='{trigger_name}'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def replace_event_trigger(self, event_name: str, trigger_name: str, new_trigger_name: str) -> bool:
        """
        替换事件的触发器
        限制：专项赛禁用

        Args:
            - event_name (str): 事件名称
            - trigger_name (str): 触发器名称
            - new_trigger_name (str): 新的触发器名称

        Returns:
            bool: 执行结果
        """
        lua_script = (
            f"ScenEdit_SetEventTrigger('{event_name}', {{Mode='replace', name='{trigger_name}', "
            f"replacedby='{new_trigger_name}'}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def set_event_action(self, event_name: str, action_name: str) -> bool:
        """
        添加事件的动作
        限制：专项赛禁用

        Args:
            - event_name (str): 事件名称
            - action_name (str): 动作名称

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetEventAction('{event_name}', {{Mode='add', name='{action_name}'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def replace_event_action(self, event_name: str, action_name: str, new_action_name: str) -> bool:
        """
        替换事件的动作
        限制：专项赛禁用

        Args:
            - event_name (str): 事件名称
            - action_name (str): 动作名称
            - new_action_name (str): 新的动作名称

        Returns:
            bool: 执行结果
        """
        lua_script = (
            f"ScenEdit_SetEventAction('{event_name}', {{Mode='replace', name='{action_name}', replacedby='{new_action_name}'}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def set_event_condition(self, event_name: str, condition_name: str) -> bool:
        """
        添加事件的条件
        限制：专项赛禁用

        Args:
            - event_name (str): 事件名称
            - condition_name (str): 条件名称

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetEventCondition('{event_name}', {{Mode='add', name='{condition_name}'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def replace_event_condition(self, event_name: str, condition_name: str, new_condition_name: str) -> bool:
        """
        替换事件的条件
        限制：专项赛禁用

        Args:
            - event_name (str): 事件名称
            - condition_name (str): 条件名称
            - new_condition_name (str): 新的条件名称

        返回：'lua执行成功' 或 '脚本执行出错'
        """
        lua_script = (
            f"ScenEdit_SetEventCondition('{event_name}', {{Mode='replace', name='{condition_name}', "
            f"replacedby='{new_condition_name}'}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_event_attribute(
        self,
        event_name: str,
        new_event_name: str | None = None,
        is_active: str | None = None,
        is_shown: str | None = None,
        is_repeatable: str | None = None,
        probability: int | None = None,
    ) -> bool:
        """
        更新事件的属性
        限制：专项赛禁用

        Args:
            - event_name (str): 事件名称
            - new_event_name (str | None): 新的事件名称
            - is_active (str | None): 是否启用
            - is_shown (str | None): 是否显示
            - is_repeatable (str | None): 是否可重复
            - probability (int | None): 发生概率

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if new_event_name:
            update_str += f", Description='{new_event_name}'"
        if is_active:
            update_str += f", IsActive='{is_active}'"
        if is_shown:
            update_str += f", IsShown={is_shown}"
        if is_repeatable:
            update_str += f", IsRepeatable={is_repeatable}"
        if probability:
            update_str += f", Probability={probability}"

        if update_str:
            update_str = update_str[1:]
        lua_script = f"ScenEdit_UpdateEvent('{event_name}', {{{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @validate_literal_args
    async def add_condition_side_posture(
        self,
        name: str,
        observer_side: str,
        target_side: str,
        target_posture: Literal[0, 1, 2, 3, 4],
        reverse: bool,
    ) -> bool:
        """
        添加推演方立场条件
        限制：专项赛禁用

        Args:
            - name (str): 条件名称
            - observer_side (str): 推演方名称
            - target_side (str): 考虑推演方名称
            - target_posture (int): observer_side视作target_side的关系:
                - 0-中立方
                - 1-友方
                - 2-非友方
                - 3-敌方
                - 4-不明
            - reverse (bool): 条件是否取反

        Returns:
            bool: 执行结果
        """
        lua_script = (
            f"ScenEdit_SetCondition({{name='{name}',Mode='add',Type='sideposture',"
            f"ObserverSideID='{observer_side}',TargetSideID='{target_side}',"
            f"TargetPosture='{target_posture}', NOT={str(reverse).lower()}}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_condition_side_posture(
        self,
        name: str,
        rename: str | None = None,
        observer_side: str | None = None,
        target_side: str | None = None,
        target_posture: Literal[0, 1, 2, 3, 4] | None = None,
        reverse: bool | None = None,
    ) -> bool:
        """
        编辑推演方立场条件
        限制：专项赛禁用

        Args:
            - name (str): 条件名称
            - rename (str | None): 新的条件名称
            - observer_side (str | None): 推演方名称
            - target_side (str | None): 考虑推演方名称
            - target_posture (int | None): observer_side视作target_side的关系:
                - 0-中立方
                - 1-友方
                - 2-非友方
                - 3-敌方
                - 4-不明
            - reverse (bool | None): 条件是否取反

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if rename:
            update_str += f", rename='{rename}'"
        if observer_side:
            update_str += f", ObserverSideID='{observer_side}'"
        if target_side:
            update_str += f", TargetSideID='{target_side}'"
        if target_posture:
            update_str += f", TargetPosture={target_posture}"
        if reverse:
            update_str += f", NOT={reverse}"

        lua_script = f"ScenEdit_SetCondition({{name='{name}',Mode='update',Type='sideposture'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_condition_scen_has_started(self, name: str, reverse: bool) -> bool:
        """
        添加想定已经开始条件
        限制：专项赛禁用

        Args:
            - name (str): 条件名称
            - reverse (bool): 条件是否取反

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetCondition({{name='{name}',Mode='add',Type='scenhasstarted', NOT={str(reverse).lower()}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_condition_scen_has_started(self, name: str, rename: str | None = None, reverse: bool | None = None) -> bool:
        """
        编辑想定已经开始条件
        限制：专项赛禁用

        Args:
            - name (str): 条件名称
            - rename (str | None): 新的条件名称
            - reverse (bool | None): 条件是否取反

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if rename:
            update_str += f", rename='{rename}'"
        if reverse:
            update_str += f", NOT={str(reverse).lower()}"
        lua_script = f"ScenEdit_SetCondition({{name='{name}',Mode='update',Type='scenhasstarted'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def add_condition_lua_script(self, name: str, script_text: str) -> bool:
        """
        添加lua脚本条件
        限制：专项赛禁用

        Args:
            - name (str): 条件名称
            - script_text (str): lua脚本

        Returns:
            bool: 执行结果
            name:{str:条件名称}
        """
        lua_script = f"ScenEdit_SetCondition({{name='{name}',Mode='add',Type='LuaScript', ScriptText=\"{script_text}\"}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def update_condition_lua_script(self, name: str, rename: str | None = None, script_text: str | None = None) -> bool:
        """
        编辑lua脚本条件
        限制：专项赛禁用

        Args:
            - name (str): 条件名称
            - rename (str | None): 新的条件名称
            - script_text (str | None): lua脚本

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if rename:
            update_str += f", rename='{rename}'"
        if script_text:
            update_str += f', ScriptText="{script_text}"'
        lua_script = f"ScenEdit_SetCondition({{name='{name}',Mode='update',Type='LuaScript'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def remove_condition(self, name: str) -> bool:
        """
        删除条件
        限制：专项赛禁用

        Args:
            - name (str): 条件名称

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetCondition({{name='{name}',Mode='remove'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @validate_uuid4_args(["side_guid"])
    async def add_trigger_aircraft_take_off(self, name: str, side_guid: str) -> bool:
        """
        添加飞机起飞触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - side_guid (str): 推演方guid

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetTrigger({{name='{name}',Mode='add',Type='AircraftTakeOff',DetectorSideID='{side_guid}'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @validate_uuid4_args(["side_guid"])
    async def add_trigger_aircraft_landing(self, name: str, side_guid: str) -> bool:
        """
        添加飞机降落触发器
        限制：专项赛禁用

        Args:
            - name (str): 触发器名称
            - side_guid (str): 推演方guid

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_SetTrigger({{name='{name}',Mode='add',Type='AircraftLanding',DetectorSideID='{side_guid}'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success
