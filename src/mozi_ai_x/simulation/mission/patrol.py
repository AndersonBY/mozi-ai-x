from typing import TYPE_CHECKING, Literal


if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation
    from ..args import FlightSize, Throttle

from .base import CMission
from ..situ_interpret import CPatrolMissionDict
from mozi_ai_x.utils.validator import validate_literal_args


class CPatrolMission(CMission):
    """
    巡逻任务
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.var_map = CPatrolMissionDict.var_map

    def __get_zone_str(self, point_list: list[tuple[float, float] | list[tuple[float, float, str]] | list[str]]):
        """
        功能：构造区域点集形成的字符串
        参数：point_list-参考点列表: {list: 例:[(40, 39.0), (41, 39.0), (41, 40.0), (40, 40.0)]，其中纬度值在前，经度值在后，(40, 39.0)中,
                                        latitude = 40, longitude = 39.0
                                        或者[(40, 39.0, 'RP1'), (41, 39.0, 'RP2'), (41, 40.0, 'RP3'), (40, 40.0, 'RP4')]
                                        或者['RP1', 'RP2'，'RP3'，'RP4']，传入参考点名称要求提前创建好参考点
        返回：区域点集形成的字符串
        """
        zone_str = ""
        if all(isinstance(item, str) for item in point_list):
            point_list_str = ",".join(point_list)  # type: ignore
            zone_str = f"Zone={{{point_list_str}}}"
        elif isinstance(point_list[0], tuple):
            if isinstance(point_list[0][-1], str):
                t = [str(k[-1]) for k in point_list]
                zone_str = f"Zone={{{','.join(t)}}}"
            else:
                t = [f"latitude={k[0]},longitude={k[1]}" for k in point_list]
                zone_str = f"Zone={{{','.join(t)}}}"
        return zone_str

    async def add_prosecution_zone(
        self, point_list: list[tuple[float, float] | list[tuple[float, float, str]] | list[str]]
    ) -> bool:
        """
        增加巡逻任务的警戒区

        Args:
            point_list (list[tuple[float, float] | list[tuple[float, float, str]] | list[str]]): 参考点列表
                - 例: `[(40, 39.0), (41, 39.0), (41, 40.0), (40, 40.0)]`，其中纬度值在前，经度值在后，(40, 39.0)中,latitude = 40, longitude = 39.0
                - 或者 `[(40, 39.0, 'RP1'), (41, 39.0, 'RP2'), (41, 40.0, 'RP3'), (40, 40.0, 'RP4')]`
                - 或者 `['RP1', 'RP2', 'RP3', 'RP4']`，传入参考点名称要求提前创建好参考点

        Returns:
            bool: 执行结果
        """
        cmd = f"ReturnObj(ScenEdit_SetMission('{self.side}','{self.name}',{{{self.__get_zone_str(point_list).replace('Zone', 'prosecutionZone')}}}))"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_prosecution_zone(self, point_list: list[str]) -> bool:
        """
        设置巡逻任务的警戒区

        Args:
            point_list (list): 参考点名称列表

        Returns:
            bool: 执行结果
        """
        area_str = ", ".join(f"'{point}'" for point in point_list)
        lua_script = f"ScenEdit_SetMission('{self.side}','{self.name}',{{prosecutionZone={{{area_str}}}}})"
        self.mozi_server.throw_into_pool(lua_script)
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def set_patrol_zone(self, point_list: list[str]) -> bool:
        """
        设置巡逻任务的巡逻区

        Args:
            - point_list (list): 参考点名称列表
                - example: ['RP1', 'RP2', 'RP3', 'RP4']

        Returns:
            bool: 执行结果
        """
        area_str = ", ".join(f"'{point}'" for point in point_list)
        lua_script = f"ScenEdit_SetMission('{self.side}','{self.name}',{{patrolZone={{{area_str}}}}})"
        self.mozi_server.throw_into_pool(lua_script)
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def set_maintain_unit_number(self, unit_number: int) -> bool:
        """
        巡逻任务阵位上每类平台保存作战单元数量

        Args:
            unit_number (int): 阵位上每类平台保存单元数量

        Returns:
            bool: 执行结果
        """
        cmd = f'ScenEdit_SetMission("{self.side}","{self.name}",{{PatrolMaintainUnitNumber={unit_number}}})'
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_opa_check(self, check: bool) -> bool:
        """
        设置任务是否对巡逻区外的探测目标进行分析

        Args:
            check (bool): True:分析，False:不分析

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{str(self.side)}', '{str(self.guid)}', {{ checkOPA = {str(check).lower()} }})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_emcon_usage(self, active: bool) -> bool:
        """
        设置任务是否仅在巡逻/警戒区内打开电磁辐射

        Args:
            active (bool): True:打开 False:不打开

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{str(self.side)}', '{str(self.guid)}', {{ activeEMCON = {str(active).lower()} }})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_wwr_check(self, check: bool) -> bool:
        """
        设置任务是否对武器射程内探测目标进行分析

        Args:
            check (bool): True遵守 或 False不遵守

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{str(self.side)}', '{str(self.guid)}', {{ checkWWR = {str(check).lower()} }})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_flight_size(self, flight_size: "FlightSize") -> bool:
        """
        设置任务编队规模

        Args:
            flight_size (FlightSize): 编队规模

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{str(self.side)}', '{str(self.guid)}', {{ flightSize = {flight_size.value} }})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_flight_size_check(self, check: bool) -> bool:
        """
        是否飞机数低于编队规模不允许起飞

        Args:
            check (bool): True:是 False:否

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{str(self.side)}', '{str(self.guid)}', {{ useFlightSize = {str(check).lower()} }})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_throttle_transit(self, throttle: "Throttle") -> bool:
        """
        设置任务的出航油门

        Args:
            throttle (Throttle): 油门

        Returns:
            bool: 执行结果
        """
        return await super().set_throttle("transitThrottleAircraft", throttle)

    async def set_throttle_station(self, throttle: "Throttle") -> bool:
        """
        设置任务的阵位油门

        Args:
            throttle (Throttle): 油门

        Returns:
            bool: 执行结果
        """
        return await super().set_throttle("stationThrottleAircraft", throttle)

    async def set_throttle_attack(self, throttle: "Throttle") -> bool:
        """
        设置任务的攻击油门

        Args:
            throttle (Throttle): 油门

        Returns:
            bool: 执行结果
        """
        return await super().set_throttle("attackThrottleAircraft", throttle)

    async def set_transit_altitude(self, altitude: float) -> bool:
        """
        设置任务的出航高度

        Args:
            altitude (float): 高度

        Returns:
            bool: 执行结果
        """
        return await super().set_altitude("transitAltitudeAircraft", altitude)

    async def set_station_altitude(self, altitude: float) -> bool:
        """
        设置任务的阵位高度

        Args:
            altitude (float): 高度

        Returns:
            bool: 执行结果
        """
        return await super().set_altitude("stationAltitudeAircraft", altitude)

    async def set_attack_altitude(self, altitude: float) -> bool:
        """
        设置任务的攻击高度

        Args:
            altitude (float): 高度

        Returns:
            bool: 执行结果
        """
        return await super().set_altitude("attackAltitudeAircraft", altitude)

    async def set_attack_distance(self, distance: float) -> bool:
        """
        设置任务的攻击距离

        Args:
            distance (float): 攻击距离，单位：公里

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{str(self.side)}', '{str(self.guid)}', {{ attackDistanceAircraft = {distance} }})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_patrol_sonobuoys_cover(self, sonobuoys_cover: float, drop_sonobuoys_type: str) -> bool:
        """
        为反潜巡逻任务设置声呐浮标在巡逻区域内的覆盖密度和深浅类型。

        Args:
            sonobuoys_cover (float): 声呐与声呐之间的距离，按照投放声呐的探测圈范围
            drop_sonobuoys_type (str): 声呐的深浅

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_SetPatrolSonobuoysCover('{self.guid}',{sonobuoys_cover},{drop_sonobuoys_type})"
        )
        return response.lua_success

    async def set_throttle_transit_ship(self, throttle: "Throttle") -> bool:
        """
        设置任务的水面舰艇出航油门

        Args:
            throttle (Throttle): 油门

        Returns:
            bool: 执行结果
        """
        return await super().set_throttle("transitThrottleShip", throttle)

    async def set_throttle_station_ship(self, throttle: "Throttle") -> bool:
        """
        设置任务的水面舰艇阵位油门

        Args:
            throttle (Throttle): 油门

        Returns:
            bool: 执行结果
        """
        return await super().set_throttle("stationThrottleShip", throttle)

    async def set_throttle_attack_ship(self, throttle: "Throttle") -> bool:
        """
        设置任务的水面舰艇攻击油门

        Args:
            throttle (Throttle): 油门

        Returns:
            bool: 执行结果
        """
        return await super().set_throttle("attackThrottleShip", throttle)

    @validate_literal_args
    async def set_group_size(self, group_size: Literal[1, 2, 3, 4, 6]) -> bool:
        """
        设置巡逻任务水面舰艇/潜艇编队规模

        Args:
            group_size (Literal[1, 2, 3, 4, 6]): 编队规模
                - 1: 单艇
                - 2: 2x艇
                - 3: 3x艇
                - 4: 4x艇
                - 6: 6x艇

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side}','{self.name}',{{groupSize={group_size}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success
