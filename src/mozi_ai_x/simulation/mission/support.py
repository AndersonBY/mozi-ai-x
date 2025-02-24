from typing import TYPE_CHECKING

from .base import CMission

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation
    from ..args import FlightSize, Throttle

from ..situ_interpret import CSupportMissionDict


class CSupportMission(CMission):
    """
    支援任务
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.var_map = CSupportMissionDict.var_map

    async def set_maintain_unit_number(self, support_maintain_count: int) -> bool:
        """
        阵位上每类平台保持几个

        Args:
            support_maintain_count (int): 保持阵位的数量

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side_name}','{self.name}',{{SupportMaintainUN={support_maintain_count}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_one_time_only(self, one_time_only: bool) -> bool:
        """
        仅一次

        Args:
            one_time_only (bool): 是否仅一次

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side_name}','{self.name}',{{oneTimeOnly={str(one_time_only).lower()}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_emcon_usage(self, active: bool) -> bool:
        """
        仅在阵位上打开电磁辐射

        Args:
            active (bool): 是否打开

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side_name}','{self.name}',{{activeEMCON={str(active).lower()}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_loop_type(self, loop: bool) -> bool:
        """
        导航类型

        Args:
            - loop (bool):
                - True-仅一次；
                - False-连续循环

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side_name}','{self.name}',{{loopType={str(loop).lower()}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_flight_size(self, size: "FlightSize") -> bool:
        """
        编队规模

        Args:
            size (FlightSize): 编队规模

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side_name}','{self.name}',{{flightSize={size.value}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_flight_size_check(self, check: bool) -> bool:
        """
        是否飞机数低于编队规模不允许起飞

        Args:
            check (bool): 是否飞机数低于编队规模不允许起飞

        Returns:
            bool: 执行结果
        """
        cmd = f"ScenEdit_SetMission('{self.side_name}','{self.name}',{{useFlightSize={str(check).lower()}}})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_throttle_transit(self, throttle: "Throttle") -> bool:
        """
        设置任务的出航油门

        Args:
            throttle (Throttle): 油门列举类中的具体列举项。

        Returns:
            bool: 执行结果
        """
        return await super().set_throttle("transitThrottleAircraft", throttle)

    async def set_throttle_station(self, throttle: "Throttle") -> bool:
        """
        设置任务的阵位油门

        Args:
            throttle (Throttle): 油门列举类中的具体列举项。

        Returns:
            bool: 执行结果
        """
        return await super().set_throttle("stationThrottleAircraft", throttle)

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
