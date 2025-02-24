from typing import TYPE_CHECKING, Optional

from .base import CMission
from ..situ_interpret import CStrikeMissionDict

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation
    from ..args import StrikeMinimumTrigger, FlightSize, StrikeMinAircraftReq, StrikeRadarUsage, StrikeFuelAmmo
    from ..doctrine import CDoctrine
    from ..contact import CContact


class CStrikeMission(CMission):
    """
    打击任务
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.use_flight_size_hard_limit_escort: Optional[bool] = None
        self.use_group_size_hard_limit_escort: Optional[bool] = None
        self.one_time_only: Optional[bool] = None
        self.pre_planned_only: Optional[bool] = None
        self.use_auto_planner: Optional[bool] = None
        self.use_flight_size_hard_limit: Optional[bool] = None
        self.use_group_size_hard_limit: Optional[bool] = None
        self.empty_slots: Optional[int] = None
        self.escort_response_radius: Optional[int] = None
        self.min_response_radius: Optional[int] = None
        self.max_response_radius: Optional[int] = None
        self.bingo: Optional[float] = None
        self.doctrine_escorts: Optional["CDoctrine"] = None
        self.start_time: Optional[str] = None
        self.end_time: Optional[str] = None
        self.escort_flight_size: Optional[int] = None
        self.escort_flight_size_no: Optional[int] = None
        self.escort_group_size: Optional[int] = None
        self.max_aircraft_to_fly_escort: Optional[int] = None
        self.max_aircraft_to_fly_escort_no: Optional[int] = None
        self.min_aircraft_req_escorts: Optional[int] = None
        self.min_aircraft_req_escorts_no: Optional[int] = None
        self.min_aircraft_req_strikers: Optional[int] = None
        self.minimum_contact_stance_to_trigger: Optional[int] = None
        self.radar_behaviour: Optional[int] = None
        self.specific_targets: str = ""
        self.strike_type: Optional[int] = None
        self.contact_weapon_way_guid: Optional[str] = None
        self.side_weapon_way_guid: Optional[str] = None

        self.var_map = CStrikeMissionDict.var_map

    def get_targets(self) -> dict[str, "CContact"]:
        """
        返回任务打击目标

        Returns:
            dict[str, CContact]: 目标单元组成的词典
        """
        target_guids = self.specific_targets.split("@")
        targets = {k: v for k, v in self.situation.side_dict[self.side].contacts.items() if k in target_guids}
        return targets

    async def assign_unit_as_target(self, target_name_or_guid: str) -> bool:
        """
        分配目标

        Args:
            target_name_or_guid (str): 目标名称或guid

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_AssignUnitAsTarget('{target_name_or_guid}', '{self.name}')"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def assign_targets(self, targets: list[str]) -> bool:
        """
        分配目标

        Args:
            targets (list[str]): 目标名称或guid列表

        Returns:
            bool: 执行结果
        """
        targets_str = f"{{{','.join(f"'{k}'" for k in targets)}}}"
        cmd = f"ScenEdit_AssignUnitAsTarget({targets_str}, '{self.name}')"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def add_target(self, target_list: list[str]) -> bool:
        """
        设置打击目标

        Args:
            target_list (list[str]): 目标列表

        Returns:
            bool: 执行结果
        """
        targets_str = f"{{{','.join(f"'{i}'" for i in target_list)}}}"
        cmd = f"print(ScenEdit_AssignUnitAsTarget({targets_str}, '{self.name}'))"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def remove_target(self, target_list: list[str]) -> bool:
        """
        设置任务：删除打击任务目标

        Args:
            target_list (list[str]): 目标列表

        Returns:
            bool: 执行结果
        """
        targets_str = f"{{{','.join(f"'{i}'" for i in target_list)}}}"
        cmd = f"print(ScenEdit_RemoveUnitAsTarget({targets_str}, '{self.name}'))"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_preplan(self, preplan: bool) -> bool:
        """
        设置任务细节：是否仅考虑计划目标（在目标清单）

        Args:
            preplan (bool): True:是仅考虑计划目标

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.name}',{{strikePreplan={str(preplan).lower()}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_minimum_trigger(self, strike_minimum_trigger: "StrikeMinimumTrigger") -> bool:
        """
        设置打击任务触发条件

        Args:
            strike_minimum_trigger (StrikeMinimumTrigger): 打击任务触发条件

        Returns:
            bool: 执行结果
        """
        cmd = (
            f"ScenEdit_SetMission('{self.side}','{self.name}',{{StrikeMinimumTrigger={strike_minimum_trigger.value}}})"
        )
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_strike_max(self, max: int) -> bool:
        """
        设置任务细节：任务允许出动的最大飞行批次

        Args:
            max (int): 最大飞行批次

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.name}',{{strikeMax={max}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_flight_size(self, size: "FlightSize") -> bool:
        """
        设置打击任务编队规模

        Args:
            size (FlightSize): 编队规模

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.name}',{{strikeFlightSize={size.value}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_min_aircrafts_required(self, min: "StrikeMinAircraftReq") -> bool:
        """
        设置打击任务所需最少飞机数

        Args:
            min (StrikeMinAircraftReq): 最少飞机数

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.name}',{{strikeMinAircraftReq={min.value}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_radar_usage(self, usage: "StrikeRadarUsage") -> bool:
        """
        设置打击任务雷达运用规则

        Args:
            usage (StrikeRadarUsage): 雷达运用规则

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.name}',{{StrikeRadarUsage={usage.value}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_fuel_ammo(self, ammo: "StrikeFuelAmmo") -> bool:
        """
        设置打击任务燃油弹药规则

        Args:
            ammo (StrikeFuelAmmo): 燃油弹药规则

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.name}',{{StrikeFuleAmmo={ammo.value}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_min_strike_radius(self, dist: float) -> bool:
        """
        设置打击任务最小打击半径

        Args:
            dist (float): 公里

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.name}',{{StrikeMinDist={dist}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_max_strike_radius(self, dist: float) -> bool:
        """
        设置打击任务最大打击半径

        Args:
            dist (float): 公里

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.name}',{{StrikeMaxDist={dist}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_flight_size_check(self, check: bool) -> bool:
        """
        设置打击任务是否飞机数低于编组规模数要求就不能起飞

        Args:
            check (bool): 是否飞机数低于编组规模数要求就不能起飞

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.name}',{{strikeUseFlightSize={str(check).lower()}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_auto_planner(self, planner: bool) -> bool:
        """
        设置打击任务是否多扇面攻击（任务AI自动生成）

        Args:
            planner (bool): 是否多扇面攻击

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.name}',{{StrikeUseAutoPlanner={str(planner).lower()}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_strike_one_time_only(self, one_time: bool) -> bool:
        """
        设置打击任务是否仅限一次

        Args:
            one_time (bool): 是否仅一次

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.name}',{{strikeOneTimeOnly={str(one_time).lower()}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success
