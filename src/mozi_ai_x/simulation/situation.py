import json
import uuid
import asyncio
from typing import TYPE_CHECKING, Any, Dict, Type, List, Optional

from .doctrine import CDoctrine
from .weather import CWeather
from .side import CSide
from .active_unit import (
    CGroup,
    CSubmarine,
    CShip,
    CFacility,
    CAircraft,
    CSatellite,
    CWeapon,
    CUnguidedWeapon,
)
from .sensor import CSensor
from .loadout.base import CLoadout
from .mount import CMount
from .magazine import CMagazine
from .weapon_impact import CWeaponImpact
from .sideway import CSideWay
from .waypoint import CWayPoint
from .contact import CContact
from .logged_message import CLoggedMessage
from .sim_event import CSimEvent
from .trigger import (
    CTriggerUnitDetected,
    CTriggerUnitDamaged,
    CTriggerUnitDestroyed,
    CTriggerPoints,
    CTriggerTime,
    CTriggerRegularTime,
    CTriggerRandomTime,
    CTriggerScenLoaded,
    CTriggerUnitRemainsInArea,
)
from .condition import (
    CConditionScenHasStarted,
    CConditionSidePosture,
    CConditionLuaScript,
)
from .action import (
    CActionMessage,
    CActionPoints,
    CActionTeleportInArea,
    CActionChangeMissionStatus,
    CActionEndScenario,
    CActionLuaScript,
)
from .mission import (
    CPatrolMission,
    CStrikeMission,
    CSupportMission,
    CCargoMission,
    CFerryMission,
    CMiningMission,
    CMineClearingMission,
)
from .zone import (
    CNoNavZone,
    CExclusionZone,
)
from .reference_point import CReferencePoint
from .response import CResponse

from ..utils.log import mprint_with_name
from mozi_ai_x.utils.validator import validate_uuid4_args

if TYPE_CHECKING:
    from .server import MoziServer
    from .scenario import CScenario

mprint = mprint_with_name("Situation")


class ObjectType:
    """
    对象类型常量定义
    按功能模块分类，数值与原始代码完全保持一致
    """

    # 推演实体
    CURRENT_SCENARIO = 1001  # CCurrentScenario (未在原始代码中显式处理)

    # 条令和阵营
    DOCTRINE = 1002  # CDoctrine
    SIDE = 1004  # CSide
    GROUP = 1005  # CGroup

    # 活动单元
    SUBMARINE = 2001  # CSubmarine
    SHIP = 2002  # CShip
    FACILITY = 2003  # CFacility
    AIRCRAFT = 2004  # CAircraft
    SATELLITE = 2005  # CSatellite

    # 传感器与武器系统
    SENSOR = 3001  # CSensor
    LOADOUT = 3002  # CLoadout
    MOUNT = 3003  # CMount
    MAGAZINE = 3004  # CMagazine
    WEAPON = 3005  # CWeapon
    UNGUIDED_WEAPON = 3006  # CUnguidedWeapon
    WEAPON_IMPACT = 3007  # CWeaponImpact

    # 路径规划
    SIDEWAY = 3008  # CSideWay
    WAYPOINT = 3009  # CWayPoint

    # 战场感知
    CONTACT = 4001  # CContact

    # 日志系统
    LOGGED_MESSAGE = 5001  # CLoggedMessage

    # 仿真事件
    SIM_EVENT = 6001  # CSimEvent

    # 触发器类型
    TRIGGER_UNIT_DETECTED = 7001  # CTriggerUnitDetected
    TRIGGER_UNIT_DAMAGED = 7002  # CTriggerUnitDamaged
    TRIGGER_UNIT_DESTROYED = 7003  # CTriggerUnitDestroyed
    TRIGGER_POINTS = 7004  # CTriggerPoints
    TRIGGER_TIME = 7005  # CTriggerTime
    TRIGGER_REGULAR_TIME = 7006  # CTriggerRegularTime
    TRIGGER_RANDOM_TIME = 7007  # CTriggerRandomTime
    TRIGGER_SCEN_LOADED = 7008  # CTriggerScenLoaded
    TRIGGER_UNIT_REMAINS_IN_AREA = 7009  # CTriggerUnitRemainsInArea

    # 条件类型
    CONDITION_SCEN_HAS_STARTED = 8001  # CConditionScenHasStarted
    CONDITION_SIDE_POSTURE = 8002  # CConditionSidePosture
    CONDITION_LUA_SCRIPT = 8003  # CConditionLuaScript

    # 动作类型
    ACTION_MESSAGE = 9001  # CActionMessage
    ACTION_POINTS = 9002  # CActionPoints
    ACTION_TELEPORT_IN_AREA = 9003  # CActionTeleportInArea
    ACTION_CHANGE_MISSION_STATUS = 9004  # CActionChangeMissionStatus
    ACTION_END_SCENARIO = 9005  # CActionEndScenario
    ACTION_LUA_SCRIPT = 9006  # CActionLuaScript

    # 任务类型
    PATROL_MISSION = 10001  # CPatrolMission
    STRIKE_MISSION = 10002  # CStrikeMission
    SUPPORT_MISSION = 10003  # CSupportMission
    CARGO_MISSION = 10004  # CCargoMission
    FERRY_MISSION = 10005  # CFerryMission
    MINING_MISSION = 10006  # CMiningMission
    MINE_CLEARING_MISSION = 10007  # CMineClearingMission

    # 地理要素
    REFERENCE_POINT = 11001  # CReferencePoint
    NO_NAV_ZONE = 11002  # CNoNavZone
    EXCLUSION_ZONE = 11003  # CExclusionZone

    # 响应系统
    RESPONSE = 11004  # CResponse

    # 环境因素（原始代码中存在但未定义类型值）
    WEATHER = 12001  # CWeather


class HandlerRegistry:
    def __init__(self):
        self._handlers = {}
        self._type_mapping = {}

    def register(
        self,
        class_name: str,
        cls: Type,
        dict_name: str,
        obj_type: int,
        has_side: bool = False,
        is_active: bool = False,
    ):
        """完整注册方法"""
        self._handlers[class_name] = {
            "class": cls,
            "dict": dict_name,
            "type": obj_type,
            "has_side": has_side,
            "is_active": is_active,
        }
        self._type_mapping[obj_type] = {"dict": dict_name, "has_side": has_side}

    def get_type_handler(self, obj_type: int) -> Optional[Dict]:
        """
        根据对象类型代码获取处理信息
        参数：
            obj_type: ObjectType枚举值（如ObjectType.SHIP）
        返回：
            包含以下信息的字典：
            - dict: 对应的对象字典名称（如'ship_dict'）
            - has_side: 是否关联阵营
            - is_active: 是否活动单元（可选）
        """
        return self._type_mapping.get(obj_type)

    def get_handler(self, class_name: str):
        return self._handlers.get(class_name)


# 初始化注册表（完整版）
registry = HandlerRegistry()

registry.register("CDoctrine", CDoctrine, "doctrine_dict", ObjectType.DOCTRINE)
registry.register("CSide", CSide, "side_dict", ObjectType.SIDE, has_side=True, is_active=True)

# 环境系统
registry.register("CWeather", CWeather, "weather_dict", ObjectType.WEATHER)

# 军事单元
registry.register("CGroup", CGroup, "group_dict", ObjectType.GROUP, has_side=True, is_active=True)
registry.register("CSubmarine", CSubmarine, "submarine_dict", ObjectType.SUBMARINE, has_side=True, is_active=True)
registry.register("CShip", CShip, "ship_dict", ObjectType.SHIP, has_side=True, is_active=True)
registry.register("CFacility", CFacility, "facility_dict", ObjectType.FACILITY, has_side=True, is_active=True)
registry.register("CAircraft", CAircraft, "aircraft_dict", ObjectType.AIRCRAFT, has_side=True, is_active=True)
registry.register("CSatellite", CSatellite, "satellite_dict", ObjectType.SATELLITE, has_side=True, is_active=True)

# 传感器与武器系统
registry.register("CSensor", CSensor, "sensor_dict", ObjectType.SENSOR)
registry.register("CLoadout", CLoadout, "loadout_dict", ObjectType.LOADOUT)
registry.register("CMount", CMount, "mount_dict", ObjectType.MOUNT)
registry.register("CMagazine", CMagazine, "magazine_dict", ObjectType.MAGAZINE)
registry.register("CWeapon", CWeapon, "weapon_dict", ObjectType.WEAPON, has_side=True)
registry.register(
    "CUnguidedWeapon", CUnguidedWeapon, "unguided_weapon_dict", ObjectType.UNGUIDED_WEAPON, has_side=True
)
registry.register("CWeaponImpact", CWeaponImpact, "weapon_impact_dict", ObjectType.WEAPON_IMPACT)

# 路径与导航
registry.register("CSideWay", CSideWay, "sideway_dict", ObjectType.SIDEWAY, has_side=True)
registry.register("CWayPoint", CWayPoint, "waypoint_dict", ObjectType.WAYPOINT)

# 战场感知
registry.register("CContact", CContact, "contact_dict", ObjectType.CONTACT, has_side=True)

# 日志系统
registry.register("CLoggedMessage", CLoggedMessage, "logged_messages_dict", ObjectType.LOGGED_MESSAGE, has_side=True)

# 事件系统
registry.register("CSimEvent", CSimEvent, "simevent_dict", ObjectType.SIM_EVENT)

# 触发器系统（完整注册）
registry.register(
    "CTriggerUnitDetected", CTriggerUnitDetected, "trigger_unit_detected_dict", ObjectType.TRIGGER_UNIT_DETECTED
)
registry.register(
    "CTriggerUnitDamaged", CTriggerUnitDamaged, "trigger_unit_damaged_dict", ObjectType.TRIGGER_UNIT_DAMAGED
)
registry.register(
    "CTriggerUnitDestroyed", CTriggerUnitDestroyed, "trigger_unit_destroyed_dict", ObjectType.TRIGGER_UNIT_DESTROYED
)
registry.register("CTriggerPoints", CTriggerPoints, "trigger_points_dict", ObjectType.TRIGGER_POINTS)
registry.register("CTriggerTime", CTriggerTime, "trigger_time_dict", ObjectType.TRIGGER_TIME)
registry.register(
    "CTriggerRegularTime", CTriggerRegularTime, "trigger_regular_time_dict", ObjectType.TRIGGER_REGULAR_TIME
)
registry.register("CTriggerRandomTime", CTriggerRandomTime, "trigger_random_time_dict", ObjectType.TRIGGER_RANDOM_TIME)
registry.register("CTriggerScenLoaded", CTriggerScenLoaded, "trigger_scen_loaded_dict", ObjectType.TRIGGER_SCEN_LOADED)
registry.register(
    "CTriggerUnitRemainsInArea",
    CTriggerUnitRemainsInArea,
    "trigger_unit_remains_in_area_dict",
    ObjectType.TRIGGER_UNIT_REMAINS_IN_AREA,
)

# 条件系统
registry.register(
    "CConditionScenHasStarted",
    CConditionScenHasStarted,
    "condition_scen_has_started_dict",
    ObjectType.CONDITION_SCEN_HAS_STARTED,
)
registry.register(
    "CConditionSidePosture", CConditionSidePosture, "condition_side_posture_dict", ObjectType.CONDITION_SIDE_POSTURE
)
registry.register(
    "CConditionLuaScript", CConditionLuaScript, "condition_lua_script_dict", ObjectType.CONDITION_LUA_SCRIPT
)

# 动作系统
registry.register("CActionMessage", CActionMessage, "action_message_dict", ObjectType.ACTION_MESSAGE)
registry.register("CActionPoints", CActionPoints, "action_points_dict", ObjectType.ACTION_POINTS)
registry.register(
    "CActionTeleportInArea", CActionTeleportInArea, "action_teleport_in_area_dict", ObjectType.ACTION_TELEPORT_IN_AREA
)
registry.register(
    "CActionChangeMissionStatus",
    CActionChangeMissionStatus,
    "action_change_mission_status_dict",
    ObjectType.ACTION_CHANGE_MISSION_STATUS,
)
registry.register("CActionEndScenario", CActionEndScenario, "action_end_scenario_dict", ObjectType.ACTION_END_SCENARIO)
registry.register("CActionLuaScript", CActionLuaScript, "action_lua_script_dict", ObjectType.ACTION_LUA_SCRIPT)

# 任务系统
registry.register("CPatrolMission", CPatrolMission, "mission_patrol_dict", ObjectType.PATROL_MISSION, has_side=True)
registry.register("CStrikeMission", CStrikeMission, "mission_strike_dict", ObjectType.STRIKE_MISSION, has_side=True)
registry.register(
    "CSupportMission", CSupportMission, "mission_support_dict", ObjectType.SUPPORT_MISSION, has_side=True
)
registry.register("CCargoMission", CCargoMission, "mission_cargo_dict", ObjectType.CARGO_MISSION, has_side=True)
registry.register("CFerryMission", CFerryMission, "mission_ferry_dict", ObjectType.FERRY_MISSION, has_side=True)
registry.register("CMiningMission", CMiningMission, "mission_mining_dict", ObjectType.MINING_MISSION, has_side=True)
registry.register(
    "CMineClearingMission",
    CMineClearingMission,
    "mission_mine_clearing_mission_dict",
    ObjectType.MINE_CLEARING_MISSION,
    has_side=True,
)

# 地理要素
registry.register(
    "CReferencePoint", CReferencePoint, "reference_point_dict", ObjectType.REFERENCE_POINT, has_side=True
)
registry.register("CNoNavZone", CNoNavZone, "zone_no_nav_dict", ObjectType.NO_NAV_ZONE, has_side=True)
registry.register("CExclusionZone", CExclusionZone, "zone_exclusion_dict", ObjectType.EXCLUSION_ZONE, has_side=True)

# 响应系统
registry.register("CResponse", CResponse, "response_dict", ObjectType.RESPONSE)


class CSituation:
    """
    态势类
    """

    def __init__(self, mozi_server: "MoziServer"):
        # 基础服务
        self.mozi_server = mozi_server
        self.all_guid_info: Dict[str, Dict] = {}  # 所有GUID的元信息
        self.all_guid: List[str] = []  # 全局GUID集合
        self.all_guid_delete_info: Dict[str, Dict] = {}  # 最近删除的GUID信息
        self.all_guid_add_info: Dict[str, Dict] = {}  # 新增GUID信息记录

        # 对象存储初始化（与注册表严格对应）
        self.doctrine_dict: Dict[str, CDoctrine] = {}
        self.weather_dict: Dict[str, CWeather] = {}
        self.side_dict: Dict[str, CSide] = {}
        self.group_dict: Dict[str, CGroup] = {}
        self.submarine_dict: Dict[str, CSubmarine] = {}
        self.ship_dict: Dict[str, CShip] = {}
        self.facility_dict: Dict[str, CFacility] = {}
        self.aircraft_dict: Dict[str, CAircraft] = {}
        self.satellite_dict: Dict[str, CSatellite] = {}
        self.sensor_dict: Dict[str, CSensor] = {}
        self.loadout_dict: Dict[str, CLoadout] = {}
        self.mount_dict: Dict[str, CMount] = {}
        self.magazine_dict: Dict[str, CMagazine] = {}
        self.weapon_dict: Dict[str, CWeapon] = {}
        self.unguided_weapon_dict: Dict[str, CUnguidedWeapon] = {}
        self.weapon_impact_dict: Dict[str, CWeaponImpact] = {}
        self.sideway_dict: Dict[str, CSideWay] = {}
        self.waypoint_dict: Dict[str, CWayPoint] = {}
        self.contact_dict: Dict[str, CContact] = {}
        self.logged_messages_dict: Dict[str, CLoggedMessage] = {}
        self.simevent_dict: Dict[str, CSimEvent] = {}
        self.trigger_unit_detected_dict: Dict[str, CTriggerUnitDetected] = {}
        self.trigger_unit_damaged_dict: Dict[str, CTriggerUnitDamaged] = {}
        self.trigger_unit_destroyed_dict: Dict[str, CTriggerUnitDestroyed] = {}
        self.trigger_points_dict: Dict[str, CTriggerPoints] = {}
        self.trigger_time_dict: Dict[str, CTriggerTime] = {}
        self.trigger_regular_time_dict: Dict[str, CTriggerRegularTime] = {}
        self.trigger_random_time_dict: Dict[str, CTriggerRandomTime] = {}
        self.trigger_scen_loaded_dict: Dict[str, CTriggerScenLoaded] = {}
        self.trigger_unit_remains_in_area_dict: Dict[str, CTriggerUnitRemainsInArea] = {}
        self.condition_scen_has_started_dict: Dict[str, CConditionScenHasStarted] = {}
        self.condition_side_posture_dict: Dict[str, CConditionSidePosture] = {}
        self.condition_lua_script_dict: Dict[str, CConditionLuaScript] = {}
        self.action_message_dict: Dict[str, CActionMessage] = {}
        self.action_points_dict: Dict[str, CActionPoints] = {}
        self.action_teleport_in_area_dict: Dict[str, CActionTeleportInArea] = {}
        self.action_change_mission_status_dict: Dict[str, CActionChangeMissionStatus] = {}
        self.action_end_scenario_dict: Dict[str, CActionEndScenario] = {}
        self.action_lua_script_dict: Dict[str, CActionLuaScript] = {}
        self.mission_patrol_dict: Dict[str, CPatrolMission] = {}
        self.mission_strike_dict: Dict[str, CStrikeMission] = {}
        self.mission_support_dict: Dict[str, CSupportMission] = {}
        self.mission_cargo_dict: Dict[str, CCargoMission] = {}
        self.mission_ferry_dict: Dict[str, CFerryMission] = {}
        self.mission_mining_dict: Dict[str, CMiningMission] = {}
        self.mission_mine_clearing_mission_dict: Dict[str, CMineClearingMission] = {}
        self.reference_point_dict: Dict[str, CReferencePoint] = {}
        self.zone_no_nav_dict: Dict[str, CNoNavZone] = {}
        self.zone_exclusion_dict: Dict[str, CExclusionZone] = {}
        self.response_dict: Dict[str, CResponse] = {}

        self.weather = None

        # 伪态势管理
        self.pseudo_situ_all_guid: List[str] = []
        self.pseudo_situ_all_name: List[str] = []
        self.update_start: bool = False

        # 注册表实例（全功能版）
        self.registry = registry
        self.object_dict_map = self._build_object_dict_map()

    def _build_object_dict_map(self) -> Dict[str, Dict]:
        """完整的字典映射构建"""
        return {
            # 推演核心
            "doctrine_dict": self.doctrine_dict,
            "weather_dict": self.weather_dict,
            # 军事单元
            "side_dict": self.side_dict,
            "group_dict": self.group_dict,
            "submarine_dict": self.submarine_dict,
            "ship_dict": self.ship_dict,
            "facility_dict": self.facility_dict,
            "aircraft_dict": self.aircraft_dict,
            "satellite_dict": self.satellite_dict,
            # 武器系统
            "sensor_dict": self.sensor_dict,
            "loadout_dict": self.loadout_dict,
            "mount_dict": self.mount_dict,
            "magazine_dict": self.magazine_dict,  # 添加缺失的映射
            "weapon_dict": self.weapon_dict,
            "unguided_weapon_dict": self.unguided_weapon_dict,
            "weapon_impact_dict": self.weapon_impact_dict,
            # 导航与路径
            "sideway_dict": self.sideway_dict,
            "waypoint_dict": self.waypoint_dict,
            # 感知系统
            "contact_dict": self.contact_dict,
            # 日志与事件
            "logged_messages_dict": self.logged_messages_dict,
            "simevent_dict": self.simevent_dict,
            # 触发器系统
            "trigger_unit_detected_dict": self.trigger_unit_detected_dict,
            "trigger_unit_damaged_dict": self.trigger_unit_damaged_dict,
            "trigger_unit_destroyed_dict": self.trigger_unit_destroyed_dict,
            "trigger_points_dict": self.trigger_points_dict,
            "trigger_time_dict": self.trigger_time_dict,
            "trigger_regular_time_dict": self.trigger_regular_time_dict,
            "trigger_random_time_dict": self.trigger_random_time_dict,
            "trigger_scen_loaded_dict": self.trigger_scen_loaded_dict,
            "trigger_unit_remains_in_area_dict": self.trigger_unit_remains_in_area_dict,
            # 条件系统
            "condition_scen_has_started_dict": self.condition_scen_has_started_dict,
            "condition_side_posture_dict": self.condition_side_posture_dict,
            "condition_lua_script_dict": self.condition_lua_script_dict,
            # 动作系统
            "action_message_dict": self.action_message_dict,
            "action_points_dict": self.action_points_dict,
            "action_teleport_in_area_dict": self.action_teleport_in_area_dict,
            "action_change_mission_status_dict": self.action_change_mission_status_dict,
            "action_end_scenario_dict": self.action_end_scenario_dict,
            "action_lua_script_dict": self.action_lua_script_dict,
            # 任务系统
            "mission_patrol_dict": self.mission_patrol_dict,
            "mission_strike_dict": self.mission_strike_dict,
            "mission_support_dict": self.mission_support_dict,
            "mission_cargo_dict": self.mission_cargo_dict,
            "mission_ferry_dict": self.mission_ferry_dict,
            "mission_mining_dict": self.mission_mining_dict,
            "mission_mine_clearing_mission_dict": self.mission_mine_clearing_mission_dict,
            # 地理要素
            "reference_point_dict": self.reference_point_dict,
            "zone_no_nav_dict": self.zone_no_nav_dict,
            "zone_exclusion_dict": self.zone_exclusion_dict,
            # 响应系统
            "response_dict": self.response_dict,
        }

    async def _check_scenario_loaded(self):
        """检查想定是否加载"""
        response = await self.mozi_server.send_and_recv("IsPacked")
        return response.raw_data.lower() == "true"

    async def init_situation(self, scenario: "CScenario", app_mode: int):
        """初始化态势"""
        if app_mode not in [2, 3]:
            for _ in range(50):
                if await self._check_scenario_loaded():
                    break
                await asyncio.sleep(1)
            else:
                raise TimeoutError("想定加载超时")

        response = await self.mozi_server.send_and_recv("GetAllState")
        self._parse_full_situation(json.loads(response.raw_data), scenario)

    def _parse_full_situation(self, situation_data: Dict, scenario: "CScenario"):
        """解析完整态势"""
        for data in situation_data.values():
            if data["ClassName"] == "CCurrentScenario":
                scenario.parse(data)
            elif data["ClassName"] == "CResponse":
                self.parse_response(data)
            elif data["ClassName"] == "CWeather":
                self.parse_weather(data)
            else:
                self._parse_generic(data)

    def _parse_generic(self, data: Dict):
        """通用对象解析逻辑"""
        handler = self.registry.get_handler(data["ClassName"])
        if not handler:
            mprint.warning(f"未注册的对象类型: {data['ClassName']}")
            return

        # 获取存储字典
        obj_dict = self.object_dict_map[handler["dict"]]
        guid = data["strGuid"]

        # 处理新增对象
        if guid not in self.all_guid_info:
            obj = handler["class"](guid, self.mozi_server, self)
            obj.parse(data)

            # 记录元信息
            meta = {"strType": handler["type"]}
            if handler["has_side"]:
                meta["side"] = getattr(obj, "side", None)

            # 更新全局索引
            self.all_guid_info[guid] = meta
            self.all_guid.append(guid)

            # 当前更新周期记录
            if self.update_start and handler.get("is_active", False):
                self.all_guid_add_info[guid] = meta

            # 存储对象
            obj_dict[guid] = obj
        else:
            # 更新已有对象
            obj_dict[guid].parse(data)

    def parse_response(self, response_json: dict):
        response_id = response_json["ID"]
        if response_id not in self.response_dict:
            response = CResponse(response_id)
            response.parse(response_json)
            self.all_guid_info[response_id] = {"strType": 11004}
            self.all_guid.append(response_id)
            self.response_dict[response_id] = response
        else:
            self.response_dict[response_id].parse(response_json)

    def parse_weather(self, weather_json: dict):
        weather = CWeather(self.mozi_server, self)
        weather.parse(weather_json)
        self.weather = weather

    def parse_delete(self, delete_json: Dict):
        """统一删除处理"""
        guid = delete_json["strGuid"]
        if guid not in self.all_guid_info:
            return

        meta = self.all_guid_info.pop(guid)
        handler = self.registry.get_type_handler(meta["strType"])

        if not handler:
            return

        # 从对应字典中删除
        obj_dict = self.object_dict_map[handler["dict"]]
        if guid in obj_dict:
            # 经验记录
            if handler["has_side"]:
                self.all_guid_delete_info[guid] = {"strType": meta["strType"], "side": obj_dict[guid].side}
            del obj_dict[guid]

        # 更新全局索引
        if guid in self.all_guid:
            self.all_guid.remove(guid)

    def generate_guid(self) -> str:
        """UUID 标准格式 GUID生成"""
        while True:
            new_guid = str(uuid.uuid4())
            if new_guid not in self.all_guid + self.pseudo_situ_all_guid:
                return new_guid

    @validate_uuid4_args(["guid"])
    def get_obj_by_guid(self, guid: str) -> Optional[Any]:
        """GUID 全局查询"""
        if guid not in self.all_guid_info:
            return None

        meta = self.all_guid_info[guid]
        handler = self.registry.get_type_handler(meta["strType"])
        if not handler:
            return None

        return self.object_dict_map[handler["dict"]].get(guid)

    @validate_uuid4_args(["guid"])
    def throw_into_pseudo_situ(self, guid: str, name: str):
        """伪态势管理"""
        self.pseudo_situ_all_guid.append(guid)
        self.pseudo_situ_all_name.append(name)

    @validate_uuid4_args(["guid"])
    def throw_into_pseudo_situ_all_guid(self, guid: str):
        """
        伪态势管理

        Args:
            guid (str): 对象的GUID
        """
        self.pseudo_situ_all_guid.append(guid)

    async def update_situation(self, scenario: "CScenario"):
        """更新态势"""
        self._prepare_for_update()
        response = await self.mozi_server.send_and_recv("UpdateState")
        self._process_update_data(json.loads(response.raw_data), scenario)
        return self._collect_changes()

    def _prepare_for_update(self):
        """更新前准备"""
        self.update_start = True
        self.all_guid_add_info.clear()
        self.pseudo_situ_all_guid.clear()
        self.pseudo_situ_all_name.clear()

    def _process_update_data(self, data: Dict, scenario: "CScenario"):
        """处理更新数据"""
        for item_data in data.values():
            if item_data.get("ClassName") == "CCurrentScenario":
                scenario.parse(item_data)
            elif item_data.get("ClassName") == "Delete":
                self.parse_delete(item_data)
            elif item_data.get("ClassName") == "CResponse":
                self.parse_response(item_data)
            elif item_data.get("ClassName") == "CWeather":
                self.parse_weather(item_data)
            elif item_data.get("ClassName"):
                self._parse_generic(item_data)
            else:
                mprint.error(f"未知的对象类型: {item_data}")

    def _collect_changes(self) -> Dict:
        """收集变更信息"""
        return {
            "added": self.all_guid_add_info,
            "deleted": self.all_guid_delete_info,
            "pseudo_guids": self.pseudo_situ_all_guid,
        }
