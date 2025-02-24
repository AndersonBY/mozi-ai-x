from typing import Union
from .side import CSide
from .active_unit.group import CGroup
from .active_unit.submarine import CSubmarine
from .active_unit.ship import CShip
from .active_unit.facility import CFacility
from .active_unit.aircraft import CAircraft
from .active_unit.satellite import CSatellite
from .sensor import CSensor
from .doctrine import CDoctrine
from .loadout.base import CLoadout
from .mount import CMount
from .magazine import CMagazine
from .active_unit.weapon import CWeapon
from .active_unit.unguided_weapon import CUnguidedWeapon
from .weapon_impact import CWeaponImpact
from .sideway import CSideWay
from .waypoint import CWayPoint
from .contact import CContact
from .logged_message import CLoggedMessage
from .sim_event import CSimEvent
from .trigger.unit_detected import CTriggerUnitDetected
from .trigger.unit_damaged import CTriggerUnitDamaged
from .trigger.unit_destroyed import CTriggerUnitDestroyed
from .trigger.points import CTriggerPoints
from .trigger.time import CTriggerTime
from .trigger.regular_time import CTriggerRegularTime
from .trigger.random_time import CTriggerRandomTime
from .trigger.scenario_loaded import CTriggerScenLoaded
from .trigger.unit_remains_in_area import CTriggerUnitRemainsInArea
from .condition.scen_has_started import CConditionScenHasStarted
from .condition.side_posture import CConditionSidePosture
from .condition.lua_script import CConditionLuaScript
from .action.message import CActionMessage
from .action.points import CActionPoints
from .action.teleport_in_area import CActionTeleportInArea
from .action.change_mission_status import CActionChangeMissionStatus
from .action.end_scenario import CActionEndScenario
from .action.lua_script import CActionLuaScript
from .mission.patrol import CPatrolMission
from .mission.strike import CStrikeMission
from .mission.support import CSupportMission
from .mission.cargo import CCargoMission
from .mission.ferry import CFerryMission
from .mission.mining import CMiningMission
from .mission.mine_clearing import CMineClearingMission
from .reference_point import CReferencePoint
from .zone.nav import CNoNavZone
from .zone.exclusion import CExclusionZone
from .response import CResponse

ObjectTypes = Union[
    CSide,
    CGroup,
    CSubmarine,
    CShip,
    CFacility,
    CAircraft,
    CSatellite,
    CSensor,
    CLoadout,
    CMount,
    CDoctrine,
    CMagazine,
    CWeapon,
    CUnguidedWeapon,
    CWeaponImpact,
    CSideWay,
    CWayPoint,
    CContact,
    CLoggedMessage,
    CSimEvent,
    CTriggerUnitDetected,
    CTriggerUnitDamaged,
    CTriggerUnitDestroyed,
    CTriggerPoints,
    CTriggerTime,
    CTriggerRegularTime,
    CTriggerRandomTime,
    CTriggerScenLoaded,
    CTriggerUnitRemainsInArea,
    CConditionScenHasStarted,
    CConditionSidePosture,
    CConditionLuaScript,
    CActionMessage,
    CActionPoints,
    CActionTeleportInArea,
    CActionChangeMissionStatus,
    CActionEndScenario,
    CActionLuaScript,
    CPatrolMission,
    CStrikeMission,
    CSupportMission,
    CCargoMission,
    CFerryMission,
    CMiningMission,
    CMineClearingMission,
    CReferencePoint,
    CNoNavZone,
    CExclusionZone,
    CResponse,
]
