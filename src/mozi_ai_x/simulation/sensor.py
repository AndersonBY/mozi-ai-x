from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import MoziServer
    from .situation import CSituation

from .base import Base
from .situ_interpret import CSensorDict


class CSensor(Base):
    """传感器"""

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 传感器名称
        self.name = ""
        # 所属单元GUID
        self.parent_platform = ""
        # 部件状态
        self.component_status = 0
        # 毁伤程度的轻,中,重
        self.damage_severity = 0
        # 挂载方位
        self.coverage_arc = ""
        # 是否开机
        self.active = False
        # 传感器类型描述
        self.description = ""
        # 传感器工作状态
        self.work_status = ""
        # 传感器类型
        self.sensor_type = 0
        # 传感器角色
        self.sensor_role = ""
        # 最大探测距离
        self.max_range = 0.0
        # 最小探测距离
        self.min_range = 0.0
        # 当传感器用作武器指示器时，正在跟踪照射的目标列表数量
        self.tracking_targets_when_used_as_director = 0
        # 当传感器用作武器指示器时，正在跟踪照射的目标列表集合
        self.tracking_targets_when_used_as_director = ""
        # 传感器能力
        self.sensor_capability = ""
        # 对空探测
        self.air_search = False
        # 对地/海面搜索
        self.surface_search = False
        # 潜艇搜索
        self.submarine_search = False
        # 地面搜索-移动设备
        self.land_search_mobile = False
        # 地面搜索-固定设施
        self.land_search_fixed = False
        # 潜望镜搜索
        self.periscope_search = False
        # 太空搜索-ABM （反弹道导弹）
        self.abm_space_search = False
        # 水/地雷与障碍物搜索
        self.mine_obstacle_search = False
        # 距离信息
        self.range_information = False
        # 航向信息
        self.heading_information = False
        # 高度信息
        self.altitude_information = False
        # 速度信息
        self.speed_information = False
        # 仅导航
        self.navigation_only = False
        # 仅地面测绘
        self.ground_mapping_only = False
        # 仅地形回避/跟随
        self.terrain_avoidance_or_following = False
        # 仅气象探测
        self.weather_only = False
        # 仅气象探测与导航
        self.weather_and_navigation = False
        # OTH-B （后向散射超视距雷达）
        self.oth_backscatter = False
        # OTH-SW （表面波超视距雷达）
        self.oth_surface_wave = False
        # 鱼雷告警
        self.torpedo_warning = False
        # 导弹逼近告警
        self.missile_approach_warning = False
        # 数据库ID
        self.db_id = 0
        # 舷侧传感器位置标识
        self.port_stern_1 = False  # 左弦尾1
        self.port_mid_aft_1 = False  # 左弦中后1
        self.port_mid_fore_1 = False  # 左弦中前1
        self.port_bow_1 = False  # 左弦首1
        self.starboard_stern_1 = False  # 右弦尾1
        self.starboard_mid_aft_1 = False  # 右弦中后1
        self.starboard_mid_fore_1 = False  # 右弦中前1
        self.starboard_bow_1 = False  # 右弦首1
        self.port_stern_2 = False  # 左弦尾2
        self.port_mid_aft_2 = False  # 左弦中后2
        self.port_mid_fore_2 = False  # 左弦中前2
        self.port_bow_2 = False  # 左弦首2
        self.starboard_stern_2 = False  # 右弦尾2
        self.starboard_mid_aft_2 = False  # 右弦中后2
        self.starboard_mid_fore_2 = False  # 右弦中前2
        self.starboard_bow_2 = False  # 右弦首2
        self.select = False  # 是否需要查找挂载单元

        self.var_map = CSensorDict.var_map

    @property
    def component_status_label(self) -> str:
        return CSensorDict.Labels.component_status.get(self.component_status, "")

    @property
    def damage_severity_label(self) -> str:
        return CSensorDict.Labels.damage_severity.get(self.damage_severity, "")

    @property
    def sensor_type_label(self) -> str:
        return CSensorDict.Labels.sensor_type.get(self.sensor_type, "")

    async def switch(self, active: bool) -> bool:
        """
        设置单元上一个具体的传感器的开关状态。

        Args:
            active (bool): 开关状态标识符
                - True: 开
                - False: 关

        Returns:
            bool: 执行结果
        """
        lua = f"Hs_ScenEdit_SetSensorSwitch({{guid={self.parent_platform},SENSORGUID={self.guid},ISACTIVE={str(active).lower()}}})"
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success
