import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import MoziServer
    from .situation import CSituation

from .situ_interpret import CWeatherDict
from .base import BaseObject


class CWeather(BaseObject):
    """天气"""

    def __init__(self, mozi_server: "MoziServer", situation: "CSituation"):
        # 态势
        self.situation = situation
        # 仿真服务类MoziServer实例
        self.mozi_server = mozi_server
        # 天气-云
        self.sky_cloud = 0.0
        # 天气-下雨概率
        self.rainfall_rate = 0.0
        # 天气-温度
        self.temperature = 0.0
        # 天气-海上天气情况
        self.sea_state = 0

        self.var_map = CWeatherDict.var_map

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    async def set_weather(self, temperature: float, rainfall: float, undercloud: float, seastate: int) -> bool:
        """
        设置当前天气条件

        Args:
            temperature (float): 当前基线温度（摄氏度），随纬度变化。
            rainfall (float): 降水量，0-50.
            undercloud (float): 云层覆盖度， 0.0-1.0
            seastate (int): 当前海况， 0-9.

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_SetWeather({temperature},{rainfall},{undercloud},{seastate})"
        )
        return response.lua_success

    async def get_weather(self) -> dict:
        """
        得到当前天气条件

        Returns:
            dict: 天气参数数组
        """
        response = await self.mozi_server.send_and_recv("ScenEdit_GetWeather()")
        return json.loads(response.raw_data)
