from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .server import MoziServer
    from .situation import CSituation
    from .mission.base import CMission
    from .active_unit import CWeapon
    from .contact import CContact
    from .doctrine import CDoctrine
    from .active_unit import CActiveUnit
    from .sideway import CSideWay
    from .logged_message import CLoggedMessage

from .mission import CPatrolMission
from .mission import CStrikeMission
from .mission import CSupportMission
from .mission import CCargoMission
from .mission import CFerryMission
from .mission import CMiningMission
from .mission import CMineClearingMission

from .zone import CNoNavZone
from .zone import CExclusionZone

from .active_unit import CSubmarine
from .active_unit import CShip
from .active_unit import CAircraft
from .active_unit import CSatellite
from .active_unit import CFacility
from .active_unit import CGroup

from .reference_point import CReferencePoint

from .args import is_in_domain
from .args import ArgsMission

from .situ_interpret import CSideDict

from .base import Base


class CSide(Base):
    """方"""

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        self.__zone_index_increment = 1  # 创建封锁区或禁航区的自增命名序号
        self.__reference_point_index_increment = 1  # 创建参考点的自增命名序号
        self.missions: dict[str, "CMission"] = {}  # key:key:mission name, value: Mission instance
        # 实体
        self.aircrafts: dict[str, "CAircraft"] = {}  # key:unit guid, value: Unit instance
        self.facilities: dict[str, "CFacility"] = {}  # key:unit guid, value: Unit instance
        self.ships: dict[str, "CShip"] = {}
        self.submarines: dict[str, "CSubmarine"] = {}
        self.weapons: dict[str, "CWeapon"] = {}
        self.satellites: dict[str, "CSatellite"] = {}
        # 目标
        self.contacts: dict[str, "CContact"] = {}  # key:contact guid, value, contact instance
        # 编组
        self.groups: dict[str, "CGroup"] = {}
        # 点
        self.action_points = {}
        # 参考点
        self.reference_points = {}
        # 条令
        self.doctrine = None
        # 天气
        self.weather = None
        # 消息
        self.logged_messages = self.get_logged_messages()
        self.current_point = 0  # 当前得分
        self.point_record = []  # 得分记录
        self.simulate_time = ""  # 当前推演时间
        self.last_step_missing = {}  # 当前决策步损失的单元（我方），丢掉或击毁的单元（敌方）
        self.last_step_new = {}  # 当前决策步新增的单元（我方），新增的情报单元（敌方）
        self.all_units = {}
        self.activeunit = {}
        self.name = ""  # 名称
        self.postures_dictionary = []  # 获取针对其它推演方的立场
        self.coctrine = ""  # 作战条令
        self.proficiency_level = []
        self.awareness_level = ""
        self.total_score = 0.0
        self.expenditures = ""  # 战损
        self.losses = ""  # 战耗
        self.scoring_disaster = 0.0  # 完败阀值
        self.scoring_triumph = 0.0  # 完胜阀值
        self.catc = False  # 自动跟踪非作战单元
        self.collective_responsibility = False  # 集体反应
        self.ai_only = False  # 只由计算机扮演
        self.briefing = ""  # 简要
        self.close_result = ""  # 战斗结束后的结果
        self.camera_altitude = 0.0  # 中心点相机高度
        self.center_latitude = 0.0  # 地图中心点纬度
        self.center_longitude = 0.0  # 地图中心点经度
        self.side_color_key = ""  # 推演方颜色Key
        self.friendly_color_key = ""  # 友方颜色Key
        self.neutral_color_key = ""  # 中立方颜色Key
        self.unfriendly_color_key = ""  # 非友方颜色Key
        self.hostile_color_key = ""  # 敌方颜色Key
        self.side_stop_count = 0  # 推演方剩余停止次数
        self.scoring_logs = ""
        self.contact_list = ""  # 所有的目标
        self.war_damage_other_total = ""  # 战损的其它统计，包含但不限于(统计损失单元带来的经济和人员损失)
        self.pointname_to_location = {}  # 存放已命名的参考点的名称     #aie 20200408

        self.var_map = CSideDict.var_map

    def static_construct(self):
        """
        将推演方准静态化
        by aie
        """
        self.doctrine = self.get_doctrine()
        self.groups = self.get_groups()
        self.submarines = self.get_submarines()
        self.ships = self.get_ships()
        self.facilities = self.get_facilities()
        self.aircrafts = self.get_aircrafts()
        self.satellites = self.get_satellites()
        self.weapons = self.get_weapons()
        self.unguided_weapons = self.get_unguided_weapons()
        self.sideways = self.get_sideways()
        self.contacts = self.get_contacts()
        self.logged_messages = self.get_logged_messages()
        self.patrol_missions = self.get_patrol_missions()
        self.strike_missions = self.get_strike_missions()
        self.support_missions = self.get_support_missions()
        self.cargo_missions = self.get_cargo_missions()
        self.ferry_missions = self.get_ferry_missions()
        self.mining_missions = self.get_mining_missions()
        self.mine_clearing_missions = self.get_mine_clearing_missions()
        self.reference_points = self.get_reference_points()
        self.no_nav_zones = self.get_no_nav_zones()
        self.exclusion_zones = self.get_exclusion_zones()

        self.missions.update(self.patrol_missions)
        self.missions.update(self.strike_missions)
        self.missions.update(self.support_missions)
        self.missions.update(self.cargo_missions)
        self.missions.update(self.ferry_missions)
        self.missions.update(self.mining_missions)
        self.missions.update(self.mine_clearing_missions)

    def static_update(self):
        """静态更新推演方类下的关联类实例"""
        self.static_add()
        self.static_delete()

    def static_delete(self):
        """将推演方删除的准静态化对象进行更新"""
        popped = []
        for k, v in self.situation.all_guid_delete_info.items():
            if v["side"] == self.guid:
                popped.append(k)
                if v["strType"] == 1005 and k in self.groups.keys():
                    self.groups.pop(k)
                    continue
                if v["strType"] == 2001 and k in self.submarines.keys():
                    self.submarines.pop(k)
                    continue
                if v["strType"] == 2002 and k in self.ships.keys():
                    self.ships.pop(k)
                    continue
                if v["strType"] == 2003 and k in self.facilities.keys():
                    self.facilities.pop(k)
                    continue
                if v["strType"] == 2004 and k in self.aircrafts.keys():
                    self.aircrafts.pop(k)
                    continue
                if v["strType"] == 2005 and k in self.satellites.keys():
                    self.satellites.pop(k)
                    continue
                if v["strType"] == 3005 and k in self.weapons.keys():
                    self.weapons.pop(k)
                    continue
                if v["strType"] == 3006 and k in self.unguided_weapons.keys():
                    self.unguided_weapons.pop(k)
                    continue
                if v["strType"] == 3008 and k in self.sideways.keys():
                    self.sideways.pop(k)
                    continue
                if v["strType"] == 4001 and k in self.contacts.keys():
                    self.contacts.pop(k)
                    continue
                if v["strType"] == 5001 and k in self.logged_messages.keys():
                    self.logged_messages.pop(k)
                    continue
                if v["strType"] == 10001 and k in self.missions.keys():
                    self.missions.pop(k)
                    continue
                if v["strType"] == 10001 and k in self.patrol_missions.keys():
                    self.patrol_missions.pop(k)
                    continue
                if v["strType"] == 10002 and k in self.strike_missions.keys():
                    self.strike_missions.pop(k)
                    continue
                if v["strType"] == 10003 and k in self.support_missions.keys():
                    self.support_missions.pop(k)
                    continue
                if v["strType"] == 10004 and k in self.cargo_missions.keys():
                    self.cargo_missions.pop(k)
                    continue
                if v["strType"] == 10005 and k in self.ferry_missions.keys():
                    self.ferry_missions.pop(k)
                    continue
                if v["strType"] == 10006 and k in self.mining_missions.keys():
                    self.mining_missions.pop(k)
                    continue
                if v["strType"] == 10007 and k in self.mine_clearing_missions.keys():
                    self.mine_clearing_missions.pop(k)
                    continue
                if v["strType"] == 11001 and k in self.reference_points.keys():
                    self.reference_points.pop(k)
                    continue
                if v["strType"] == 11002 and k in self.no_nav_zones.keys():
                    self.no_nav_zones.pop(k)
                    continue
                if v["strType"] == 11003 and k in self.exclusion_zones.keys():
                    self.exclusion_zones.pop(k)
        for k in popped:
            self.situation.all_guid_delete_info.pop(k)

    def static_add(self):
        """将推演方增加的准静态化对象进行更新"""
        for k, v in self.situation.all_guid_add_info.items():
            if v["side"] == self.guid:
                if v["strType"] == 1005:
                    self.groups.update({k: self.situation.group_dict[k]})
                    continue
                if v["strType"] == 2001:
                    self.submarines.update({k: self.situation.submarine_dict[k]})
                    continue
                if v["strType"] == 2002:
                    self.ships.update({k: self.situation.ship_dict[k]})
                    continue
                if v["strType"] == 2003:
                    self.facilities.update({k: self.situation.facility_dict[k]})
                    continue
                if v["strType"] == 2004:
                    self.aircrafts.update({k: self.situation.aircraft_dict[k]})
                    continue
                if v["strType"] == 2005:
                    self.satellites.update({k: self.situation.satellite_dict[k]})
                    continue
                if v["strType"] == 3005:
                    self.weapons.update({k: self.situation.weapon_dict[k]})
                    continue
                if v["strType"] == 3006:
                    self.unguided_weapons.update({k: self.situation.unguided_weapon_dict[k]})
                    continue
                if v["strType"] == 3008:
                    self.sideways.update({k: self.situation.sideway_dict[k]})
                    continue
                if v["strType"] == 4001:
                    self.contacts.update({k: self.situation.contact_dict[k]})
                    continue
                if v["strType"] == 5001:
                    self.logged_messages.update({k: self.situation.logged_messages_dict[k]})
                    continue
                if v["strType"] == 10001:
                    self.patrol_missions.update({k: self.situation.mission_patrol_dict[k]})
                    self.missions.update({k: self.situation.mission_patrol_dict[k]})
                    continue
                if v["strType"] == 10002:
                    self.strike_missions.update({k: self.situation.mission_strike_dict[k]})
                    self.missions.update({k: self.situation.mission_strike_dict[k]})
                    continue
                if v["strType"] == 10003:
                    self.support_missions.update({k: self.situation.mission_support_dict[k]})
                    self.missions.update({k: self.situation.mission_support_dict[k]})
                    continue
                if v["strType"] == 10004:
                    self.cargo_missions.update({k: self.situation.mission_cargo_dict[k]})
                    self.missions.update({k: self.situation.mission_cargo_dict[k]})
                    continue
                if v["strType"] == 10005:
                    self.ferry_missions.update({k: self.situation.mission_ferry_dict[k]})
                    self.missions.update({k: self.situation.mission_ferry_dict[k]})
                    continue
                if v["strType"] == 10006:
                    self.mining_missions.update({k: self.situation.mission_mining_dict[k]})
                    self.missions.update({k: self.situation.mission_mining_dict[k]})
                    continue
                if v["strType"] == 10007:
                    self.mine_clearing_missions.update({k: self.situation.mission_mine_clearing_mission_dict[k]})
                    self.missions.update({k: self.situation.mission_mine_clearing_mission_dict[k]})
                    continue
                if v["strType"] == 11001:
                    self.reference_points.update({k: self.situation.reference_point_dict[k]})
                    continue
                if v["strType"] == 11002:
                    self.no_nav_zones.update({k: self.situation.zone_no_nav_dict[k]})
                    continue
                if v["strType"] == 11003:
                    self.exclusion_zones.update({k: self.situation.zone_exclusion_dict[k]})

    def get_doctrine(self) -> "CDoctrine | None":
        """获取推演方条令"""
        if self.coctrine in self.situation.doctrine_dict:
            doctrine = self.situation.doctrine_dict[self.coctrine]
            doctrine.category = "Side"
            return doctrine
        return None

    def get_weapon_db_guids(self) -> list[str]:
        """
        获取编组内所有武器的数据库guid

        Returns:
            list[str]: 编组内所有武器的guid组成的列表
        """
        unit_collections = [self.submarines, self.ships, self.facilities, self.aircrafts, self.satellites]

        weapon_guids = []
        for units in unit_collections:
            # 获取每个单元的武器记录
            for unit in units.values():
                if not unit.unit_weapons:
                    continue
                # 解析武器记录字符串,格式为: "weapon1$guid1@weapon2$guid2@..."
                weapon_records = unit.unit_weapons.split("@")
                # 提取每个武器记录中的guid部分
                weapon_guids.extend(record.split("$")[1] for record in weapon_records)

        return weapon_guids

    def get_weapon_infos(self) -> list[list[str]]:
        """获取编组内所有武器的名称及数据库guid

        遍历所有单元类型(潜艇、舰船、设施、飞机、卫星),提取它们的武器信息。

        Returns:
            list[list[str]]: 武器信息列表,每个元素为 [weapon_name, weapon_guid]

        Example:
            >>> side.get_weapon_infos()
            [['weapon1', 'guid1'], ['weapon2', 'guid2'], ...]
        """
        unit_collections = [self.submarines, self.ships, self.facilities, self.aircrafts, self.satellites]

        weapon_infos = []
        for units in unit_collections:
            # 获取每个单元的武器记录
            for unit in units.values():
                if not unit.unit_weapons:
                    continue
                # 解析武器记录字符串,格式为: "weapon1$guid1@weapon2$guid2@..."
                weapon_records = unit.unit_weapons.split("@")
                # 提取每个武器记录的名称和guid
                weapon_infos.extend(record.split("$") for record in weapon_records)

        return weapon_infos

    def get_groups(self) -> dict[str, "CGroup"]:
        """
        获取本方编组

        Returns:
            dict 格式 {unit_guid_1: unit_obj_1, unit_guid_2: unit_obj_2, ...}  CGroup
        """
        group_dic = {}
        for k, v in self.situation.group_dict.items():
            if v.side == self.guid:
                group_dic[k] = v
        return group_dic

    def get_submarines(self) -> dict[str, "CSubmarine"]:
        """
        获取本方潜艇

        Returns:
            dict 格式 {unit_guid_1: unit_obj_1, unit_guid_2: unit_obj_2, ...}  CSubmarine
        """
        submarine_dic = {}
        for k, v in self.situation.submarine_dict.items():
            if v.side == self.guid:
                submarine_dic[k] = v
        return submarine_dic

    def get_ships(self) -> dict[str, "CShip"]:
        """
        获取本方船

        Returns:
            dict 格式 {unit_guid_1: unit_obj_1, unit_guid_2: unit_obj_2, ...}  CShip
        """
        ship_dic = {}
        for k, v in self.situation.ship_dict.items():
            if v.side == self.guid:
                ship_dic[k] = v
        return ship_dic

    def get_facilities(self) -> dict[str, "CFacility"]:
        """
        获取本方地面单位

        Returns:
            dict 格式 {unit_guid_1: unit_obj_1, unit_guid_2: unit_obj_2, ...}  CFacility
        """
        facility_dic = {}
        for k, v in self.situation.facility_dict.items():
            if v.side == self.guid:
                facility_dic[k] = v
        return facility_dic

    def get_aircrafts(self) -> dict[str, "CAircraft"]:
        """
        获取本方飞机

        Returns:
            dict 格式 {unit_guid_1: unit_obj_1, unit_guid_2: unit_obj_2, ...}  CAircraft
        """
        aircrafts_dict = {}
        for k, v in self.situation.aircraft_dict.items():
            if v.side == self.guid:
                aircrafts_dict[k] = v
        return aircrafts_dict

    def get_satellites(self) -> dict[str, "CSatellite"]:
        """
        获取本方卫星

        Returns:
            dict 格式 {unit_guid_1: unit_obj_1, unit_guid_2: unit_obj_2, ...}  CSatellite
        """
        satellite_dic = {}
        for k, v in self.situation.satellite_dict.items():
            if v.side == self.guid:
                satellite_dic[k] = v
        return satellite_dic

    def get_weapons(self) -> dict[str, "CWeapon"]:
        """
        获取本方武器

        Returns:
            dict 格式 {unit_guid_1: unit_obj_1, unit_guid_2: unit_obj_2, ...}  CWeapon
        """
        weapon_dic = {}
        for k, v in self.situation.weapon_dict.items():
            if v.side == self.guid:
                weapon_dic[k] = v
        return weapon_dic

    def get_unguided_weapons(self) -> dict[str, "CWeapon"]:
        """
        获取本方非制导武器

        Returns:
            dict 格式 {unit_guid_1: unit_obj_1, unit_guid_2: unit_obj_2, ...}
        """
        unguidedwpn_dic = {}
        for k, v in self.situation.unguided_weapon_dict.items():
            if v.side == self.guid:
                unguidedwpn_dic[k] = v
        return unguidedwpn_dic

    def get_sideways(self) -> dict[str, "CSideWay"]:
        """
        获取预定义航路

        Returns:
            dict 格式 {unit_guid_1: unit_obj_1, unit_guid_2: unit_obj_2, ...}  CSideWay
        """
        return {k: v for k, v in self.situation.sideway_dict.items() if v.side == self.guid}

    def get_contacts(self) -> dict[str, "CContact"]:
        """
        获取本方目标

        Returns:
            dict 格式 {contact_guid_1: contact_obj_1, contact_guid_2: contact_obj_2, ...}  CContact
        """
        contact_dic = {}
        for k, v in self.situation.contact_dict.items():
            if v.original_detector_side == self.guid:  # changed by aie
                contact_dic[k] = v
        return contact_dic

    def get_logged_messages(self) -> dict[str, "CLoggedMessage"]:
        """
        获取本方日志消息 # 接口暂不可用

        Returns:
            dict 格式 {guid_1: _obj_1, guid_2: obj_2, ...}
        """
        logged_messages = {}
        for k, v in self.situation.logged_messages_dict.items():
            if v.side == self.guid:
                logged_messages[k] = v
        return logged_messages

    def get_patrol_missions(self) -> dict[str, "CPatrolMission"]:
        """
        获取巡逻任务

        Returns:
            dict 格式 {mission_guid_1: mission_obj_1, mission_guid_2: mission_obj_2, ...}  CPatrolMission
        """
        return {k: v for k, v in self.situation.mission_patrol_dict.items() if v.side == self.guid}

    def get_strike_missions(self) -> dict[str, "CStrikeMission"]:
        """
        获取打击任务

        Returns:
            dict 格式 {mission_guid_1: mission_obj_1, mission_guid_2: mission_obj_2, ...}  CStrikeMission
        """
        return {k: v for k, v in self.situation.mission_strike_dict.items() if v.side == self.guid}

    def get_support_missions(self) -> dict[str, "CSupportMission"]:
        """
        获取支援任务

        Returns:
            dict 格式 {mission_guid_1: mission_obj_1, mission_guid_2: mission_obj_2, ...}  CSupportMission
        """
        return {k: v for k, v in self.situation.mission_support_dict.items() if v.side == self.guid}

    def get_cargo_missions(self) -> dict[str, "CCargoMission"]:
        """
        获取运输任务

        Returns:
            dict 格式 {mission_guid_1: mission_obj_1, mission_guid_2: mission_obj_2, ...}  CCargoMission
        """
        return {k: v for k, v in self.situation.mission_cargo_dict.items() if v.side == self.guid}

    def get_ferry_missions(self) -> dict[str, "CFerryMission"]:
        """
        获取转场任务

        Returns:
            dict 格式 {mission_guid_1: mission_obj_1, mission_guid_2: mission_obj_2, ...}  CFerryMission
        """
        return {k: v for k, v in self.situation.mission_ferry_dict.items() if v.side == self.guid}

    def get_mining_missions(self) -> dict[str, "CMiningMission"]:
        """
        获取布雷任务 # 接口暂不可用

        Returns:
            dict 格式 {mission_guid_1: mission_obj_1, mission_guid_2: mission_obj_2, ...}  CMiningMission
        """
        return {k: v for k, v in self.situation.mission_mining_dict.items() if v.side == self.guid}

    def get_missions_by_name(self, name: str) -> dict[str, "CMission"]:
        """
        根据任务名称获取任务

        Returns:
            dict 格式 {mission_guid_1: mission_obj_1, mission_guid_2: mission_obj_2, ...}  CMission
        """
        return {k: v for k, v in self.missions.items() if v.name == name}
        # # 临时需改，by 赵俊义
        # for k, v in self.missions.items():
        #     if v.name == name:
        #         return v

    def get_mine_clearing_missions(self) -> dict[str, "CMineClearingMission"]:
        """
        获取扫雷任务 # 接口暂不可用

        Returns:
            dict 格式 {mission_guid_1: mission_obj_1, mission_guid_2: mission_obj_2, ...}  CMineClearingMission
        """
        return {k: v for k, v in self.situation.mission_mine_clearing_mission_dict.items() if v.side == self.guid}

    def get_reference_points(self) -> dict[str, "CReferencePoint"]:
        """
        获取参考点

        Returns:
            dict 格式 {item_guid_1: item_obj_1, item_guid_2: item_obj_2, ...}  CReferencePoint
        """
        referencept_dic = {}
        for k, v in self.situation.reference_point_dict.items():
            if v.side == self.guid:
                referencept_dic[k] = v
        return referencept_dic

    def get_no_nav_zones(self) -> dict[str, "CNoNavZone"]:
        """
        获取禁航区

        Returns:
            dict 格式 {item_guid_1: item_obj_1, item_guid_2: item_obj_2, ...}  CNoNavZone
        """
        zonenonav_dic = {}
        for k, v in self.situation.zone_no_nav_dict.items():
            if v.side == self.guid:
                zonenonav_dic[k] = v
        return zonenonav_dic

    async def set_reference_point(self, name: str, latitude: float | int, longitude: float | int) -> bool:
        """
        更新参考点坐标

        Args:
            name (str): 参考点名称
            latitude (float | int): 纬度
            longitude (float | int): 经度

        Returns:
            bool 格式 True 或 False
        """
        # 传入int后，获取point经纬度为0，这里做下强制类型转换
        if isinstance(latitude, int):
            latitude = float(latitude)
        if isinstance(longitude, int):
            longitude = float(longitude)
        lua_script = (
            f"ScenEdit_SetReferencePoint({{side='{self.name}',name='{name}', lat={latitude}, lon={longitude}}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    def get_exclusion_zones(self) -> dict[str, "CExclusionZone"]:
        """
        获取封锁区

        Returns:
            dict 格式 {item_guid_1: item_obj_1, item_guid_2: item_obj_2, ...}  CExclusionZone
        """
        zonexclsn_dic = {}
        for k, v in self.situation.zone_exclusion_dict.items():
            if v.side == self.guid:
                zonexclsn_dic[k] = v
        return zonexclsn_dic

    def get_score(self) -> float:
        """
        获取本方分数

        Returns:
            float 本方总分
        """
        return self.total_score

    def get_unit_by_guid(self, guid: str) -> "CActiveUnit | None":
        """
        根据guid获取实体对象

        Args:
            guid (str): 实体guid

        Returns:
            活动单元对象
        """
        if guid in self.aircrafts:
            return self.aircrafts[guid]
        if guid in self.facilities:
            return self.facilities[guid]
        if guid in self.weapons:
            return self.weapons[guid]
        if guid in self.ships:
            return self.ships[guid]
        if guid in self.satellites:
            return self.satellites[guid]
        if guid in self.submarines:
            return self.submarines[guid]
        return None

    def get_contact_by_guid(self, contact_guid: str) -> "CContact | None":
        """
        根据情报对象guid获取情报对象

        Args:
            contact_guid (str): 情报对象guid

        Returns:
            情报对象
        """
        if contact_guid in self.contacts:
            return self.contacts[contact_guid]
        else:
            return None

    def get_identified_targets_by_name(self, name: str) -> dict[str, "CContact"]:
        """
        从推演方用名称确认目标

        Args:
            name (str): 情报对象名称

        Returns:
            dict 格式 {item_guid_1: item_obj_1, item_guid_2: item_obj_2, ...}  CContact
        """
        # 需求来源：20200330-1.3/3:lzy
        return {k: v for k, v in self.contacts.items() if v.name == name}

    async def get_elevation(self, coordinate: tuple[float, float]) -> float:
        """
        获取某点的海拔高度

        Args:
            coordinate (tuple[float, float]): 经纬度元组 (lat, lon)

        Returns:
            该点的海拔高度，单位米
        """
        lua_cmd = f"ReturnObj(World_GetElevation ({{latitude='{coordinate[0]}',longitude='{coordinate[1]}'}}))"
        response = await self.mozi_server.send_and_recv(lua_cmd)
        return float(response.raw_data)

    async def add_mission_patrol(
        self, name: str, patrol_type_num: Literal[0, 1, 2, 3, 4, 5, 6], zone_points: list[str]
    ) -> "CPatrolMission | None":
        """
        添加巡逻任务

        Args:
            - name (str): 任务名称
            - patrol_type_num (int): 巡逻类型的编号 详见 args.py ArgsMission.patrol_type
                - 0: 'AAW : 空战巡逻',
                - 1: 'SUR_SEA : 反面(海)巡逻',
                - 2: 'SUR_LAND : 反面(陆)巡逻',
                - 3: 'SUR_MIXED : 反面(混)巡逻',
                - 4: 'SUB : 反潜巡逻',
                - 5: 'SEAD : 压制敌防空巡逻',
                - 6: 'SEA : 海上控制巡逻'
            - zone_points (list[str]): 参考点名称组成的列表

        Returns:
            创建的巡逻任务对象 或 None
        """
        if not is_in_domain(patrol_type_num, ArgsMission.patrol_type):
            raise ValueError("patrol_type_num不在域中")
        patrol_type = ArgsMission.patrol_type[patrol_type_num].replace(" ", "").split(":")[0]
        area_str = str(zone_points).replace("[", "").replace("]", "")
        detail = f"{{type='{patrol_type}', Zone={{{area_str}}}}}"

        cmd = f"ReturnObj(ScenEdit_AddMission('{self.guid}','{name}','Patrol',{detail}))"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)

        obj = None
        if name in response.raw_data:
            return_dict = self.__convert_lua_obj_to_dict(response.raw_data)
            self.situation.throw_into_pseudo_situ_all_guid(return_dict["guid"])
            obj = CPatrolMission(return_dict["guid"], self.mozi_server, self.situation)
            obj.name = name
            obj.side = self.guid
            obj.mission_class = 2  # 巡逻
        return obj

    async def add_mission_strike(self, name: str, strike_type_num: Literal[0, 1, 2, 3]):
        """
        添加打击任务

        Args:
            - name (str): 任务名称
            - strike_type_num (int): 打击类型的编号 详见 args.py ArgsMission.strike_type
                - 0: 'AIR : 空中拦截',
                - 1: 'LAND : 对陆打击',
                - 2: 'SEA : 对海打击',
                - 3: 'SUB : 对潜打击'

        Returns:
            创建的打击任务对象 或 None
        """
        if not is_in_domain(strike_type_num, ArgsMission.strike_type):
            raise ValueError("strike_type_num不在域中")
        strike_type = ArgsMission.strike_type[strike_type_num].replace(" ", "").split(":")[0]
        detail = f"{{type='{strike_type}'}}"

        cmd = f"ReturnObj(ScenEdit_AddMission('{self.guid}','{name}','Strike',{detail}))"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)

        obj = None
        if name in response.raw_data:
            return_dict = self.__convert_lua_obj_to_dict(response.raw_data)
            self.situation.throw_into_pseudo_situ_all_guid(return_dict["guid"])
            obj = CStrikeMission(return_dict["guid"], self.mozi_server, self.situation)
            obj.name = name
            obj.side = self.guid
            obj.mission_class = 1  # 打击任务
            obj.strike_type = strike_type_num  # 需确认是否一致
        return obj

    async def add_mission_support(self, name: str, zone_points: list[str]) -> "CSupportMission | None":
        """
        添加支援任务

        Args:
            - name (str): 任务名称
            - zone_points (list[str]): 参考点名称组成的列表

        Returns:
            创建的支援任务对象 或 None
        """
        area_str = str(zone_points).replace("[", "").replace("]", "")
        detail = f"{{Zone={{{area_str}}}}}"

        cmd = f"ReturnObj(ScenEdit_AddMission('{self.guid}','{name}','Support',{detail}))"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)

        obj = None
        if name in response.raw_data:
            return_dict = self.__convert_lua_obj_to_dict(response.raw_data)
            self.situation.throw_into_pseudo_situ_all_guid(return_dict["guid"])
            obj = CSupportMission(return_dict["guid"], self.mozi_server, self.situation)
            obj.name = name
            obj.side = self.guid
            obj.mission_class = 3  # 支援
        return obj

    async def add_mission_ferry(self, name: str, destination: str) -> "CFerryMission | None":
        """
        添加转场任务

        Args:
            - name (str): 任务名称
            - destination (str): 目的地名称或guid

        Returns:
            创建的转场任务对象 或 None
        """
        detail = f"{{destination='{destination}'}}"

        cmd = f"ReturnObj(ScenEdit_AddMission('{self.guid}','{name}','Ferry',{detail}))"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)

        obj = None
        if name in response.raw_data:
            return_dict = self.__convert_lua_obj_to_dict(response.raw_data)
            self.situation.throw_into_pseudo_situ_all_guid(return_dict["guid"])
            obj = CFerryMission(return_dict["guid"], self.mozi_server, self.situation)
            obj.name = name
            obj.side = self.guid
            obj.mission_class = 4  # 转场
        return obj

    async def add_mission_mining(self, name: str, zone_points: list[str]) -> "CMiningMission | None":
        """
        添加布雷任务

        Args:
            - name (str): 任务名称
            - zone_points (list[str]): 参考点名称组成的列表

        Returns:
            创建的布雷任务对象 或 None
        """
        area_str = str(zone_points).replace("[", "").replace("]", "")
        detail = f"{{Zone={{{area_str}}}}}"
        cmd = f"ReturnObj(ScenEdit_AddMission('{self.guid}','{name}','Mining',{detail}))"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)

        obj = None
        if name in response.raw_data:
            return_dict = self.__convert_lua_obj_to_dict(response.raw_data)
            self.situation.throw_into_pseudo_situ_all_guid(return_dict["guid"])
            obj = CMiningMission(return_dict["guid"], self.mozi_server, self.situation)
            obj.name = name
            obj.side = self.guid
            obj.mission_class = 5  # 布雷
        return obj

    async def add_mission_mine_clearing(self, name: str, zone_points: list[str]) -> "CMineClearingMission | None":
        """
        添加扫雷任务

        Args:
            - name (str): 任务名称
            - zone_points (list[str]): 参考点名称组成的列表

        Returns:
            创建的扫雷任务对象 或 None
        """
        area_str = str(zone_points).replace("[", "").replace("]", "")
        detail = f"{{Zone={{{area_str}}}}}"
        cmd = f"ReturnObj(ScenEdit_AddMission('{self.guid}','{name}','MineClearing',{detail}))"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)

        obj = None
        if name in response.raw_data:
            return_dict = self.__convert_lua_obj_to_dict(response.raw_data)
            self.situation.throw_into_pseudo_situ_all_guid(return_dict["guid"])
            obj = CMineClearingMission(return_dict["guid"], self.mozi_server, self.situation)
            obj.name = name
            obj.side = self.guid
            obj.mission_class = 6  # 扫雷
        return obj

    async def add_mission_cargo(self, name: str, zone_points: list[str]) -> "CCargoMission | None":
        """
        添加投送任务

        Args:
            - name (str): 任务名称
            - zone_points (list[str]): 参考点名称组成的列表

        Returns:
            创建的投送任务对象 或 None
        """
        area_str = str(zone_points).replace("[", "").replace("]", "")
        detail = f"{{Zone={{{area_str}}}}}"
        cmd = f"ReturnObj(ScenEdit_AddMission('{self.guid}','{name}','Cargo',{detail}))"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)

        obj = None
        if name in response.raw_data:
            return_dict = self.__convert_lua_obj_to_dict(response.raw_data)
            self.situation.throw_into_pseudo_situ_all_guid(return_dict["guid"])
            obj = CCargoMission(return_dict["guid"], self.mozi_server, self.situation)
            obj.name = name
            obj.side = self.guid
            obj.mission_class = 8  # 投送
        return obj

    async def delete_mission(self, mission_name: str) -> bool | None:
        """
        删除任务

        Args:
            mission_name (str): 任务名称

        Returns:
            None: 该任务不存在
            True: lua执行成功
            False: 脚本执行出错
        """
        missions = self.get_missions_by_name(mission_name)
        if not missions:
            return None
        mission = list(missions.values())[0]
        if mission:
            lua = f"ScenEdit_DeleteMission('{self.name}', '{mission_name}')"
            response = await self.mozi_server.send_and_recv(lua)
            if response.lua_success:
                del self.missions[mission.guid]
            return response.lua_success
        return None

    async def add_group(self, unit_guid_list: list[str]) -> "CGroup | None":
        """
        将同类型单元单元合并创建编队，暂不支持不同类型单元。

        Args:
            unit_guid_list (list[str]): 单元guid列表

        Returns:
            所添加单元的活动单元对象 或 None
        """
        table = str(unit_guid_list).replace("[", "{").replace("]", "}")
        response = await self.mozi_server.send_and_recv(f"ReturnObj(Hs_ScenEdit_AddGroup({table}))")
        if "unit {" in response.raw_data:
            # 将返回的字符串转换成字典
            return_dict = self.__convert_lua_obj_to_dict(response.raw_data)
            self.situation.throw_into_pseudo_situ_all_guid(return_dict["guid"])
            obj = CGroup(return_dict["guid"], self.mozi_server, self.situation)
            obj.name = return_dict["name"]
            obj.side = self.guid
            return obj
        return None

    async def air_group_out(self, air_guid_list: list[str]) -> bool:
        """
        飞机编组出动。

        Args:
            - air_guid_list (list[str]): 单元guid列表
                - 例子：['71136bf2-58ba-4013-92f5-2effc99d2wds','71136bf2-58ba-4013-92f5-2effc99d2fa0']

        Returns:
            True: lua执行成功
            False: 脚本执行出错
        """
        table = str(air_guid_list).replace("[", "{").replace("]", "}")
        lua_script = f"Hs_LUA_AirOpsGroupOut('{self.name}',{table})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @staticmethod
    def __convert_lua_obj_to_dict(return_str: str):
        # 功能：将lua返回的对象，转化成python字典
        return_dict = {}
        if "\r\n" in return_str:
            return_list = return_str.split("\r\n")
        else:
            return_str = return_str.strip()[1:-1]
            return_list = return_str.split(",")
        for item in return_list:
            if "=" in item:
                item = item.strip()
                if item.endswith(","):
                    item = item[:-1]
                kv = item.split("=")
                return_dict[kv[0].strip()] = kv[1].strip().replace("'", "")
        return return_dict

    async def set_ecom_status(
        self, object_type: Literal["Side", "Mission", "Group", "Unit"], object_name: str, emcon: str
    ) -> bool:
        """
        设置选定对象的 EMCON

        Args:
            - object_type (str): 对象类型
                - 'Side'
                - 'Mission'
                - 'Group'
                - 'Unit'
            - object_name (str): 对象名称或guid
            - emcon (str): 感器类型和传感器状态
                - Inherit 继承上级设置
                or Radar/Sonar/OECM=Active/Passive 设置开关

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_SetEMCON('{object_type}','{object_name}','{emcon}')"
        )
        return response.lua_success

    async def add_reference_point(self, name: str, latitude: float, longitude: float) -> "CReferencePoint | None":
        """
        添加参考点

        Args:
            - name (str): 参考点名称
            - latitude (float): 纬度
            - longitude (float): 经度

        Returns:
            参考点对象 或 None
        """
        cmd = f"ReturnObj(ScenEdit_AddReferencePoint({{side='{self.name}', name='{name}', lat={latitude}, lon={longitude}}}))"
        response = await self.mozi_server.send_and_recv(cmd)
        point = None
        if name in response.raw_data:
            result_dict = self.__convert_lua_obj_to_dict(response.raw_data)
            self.mozi_server.throw_into_pool(cmd)
            point = CReferencePoint(result_dict["guid"], self.mozi_server, self.situation)
            point.name = name
            point.latitude = latitude
            point.longitude = longitude
        return point

    async def add_zone(
        self,
        zone_type: Literal[0, 1],
        description: str,
        area: list[str],
        affects: list[str],
        mark_as: Literal["Unfriendly", "Hostile"],
        active: bool = True,
    ) -> "CNoNavZone | CExclusionZone | None":
        """
        创建区域

        Args:
            - zone_type (int): 0 - 禁航区，1 - 封锁区
            - description (str): 区域名称
            - area (list[str]): 参考点名称列表
            - affects (list[str]): 应用于单元类型
                - 例子：['Aircraft', 'Ship', 'Submarine']
            - active (bool): 是否启用
            - mark_as (str): 封锁区闯入者立场
                - 例子：'Unfriendly'

        Returns:
            None 或 区域对象
        """
        area_str = str(area).replace("[", "{").replace("]", "}")
        affects_str = str(affects).replace("[", "{").replace("]", "}")
        mark_as_str = ""
        if zone_type == 1:
            mark_as_str = f", Markas='{mark_as}'"
        lua_script = (
            f"ReturnObj(ScenEdit_AddZone('{self.guid}', {zone_type}, {{description='{description}', "
            f"Isactive={str(active).lower()}, Affects={affects_str}, Area={area_str}{mark_as_str}}}))"
        )
        response = await self.mozi_server.send_and_recv(lua_script)

        if description in response.raw_data:
            # 将返回的字符串转换成字典
            return_dict = self.__convert_lua_obj_to_dict(response.raw_data)
            self.situation.throw_into_pseudo_situ_all_guid(return_dict["guid"])
            type_selected = {0: CNoNavZone, 1: CExclusionZone}
            obj = type_selected[zone_type](return_dict["guid"], self.mozi_server, self.situation)
            obj.name = description
            obj.description = description
            obj.side = self.guid
            return obj
        return None

    async def set_zone(
        self,
        zone_guid: str,
        description: str | None = None,
        area: list[str] | None = None,
        affects: list[str] | None = None,
        active: bool | None = None,
        mark_as: Literal["Unfriendly", "Hostile"] | None = None,
        ref_point_visible: bool | None = None,
    ) -> bool:
        """
        设置区域

        Args:
            - zone_guid (str): 区域guid
            - description (str): 区域名称
            - area (list[str]): 参考点名称列表
            - affects (list[str]): 应用于单元类型
                - 例子：['Aircraft', 'Ship', 'Submarine']
            - is_active (bool): 是否启用
            - mark_as (str): 封锁区闯入者立场
                - 例子：'Unfriendly'
            - rp_visible (bool): 参考点是否可见

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if description:
            update_str += f", description='{description}'"
        if area:
            area_str = str(area).replace("[", "{").replace("]", "}")
            update_str += f", Area={area_str}"
        if affects:
            affects_str = str(affects).replace("[", "{").replace("]", "}")
            update_str += f", Affects={affects_str}"
        if active:
            update_str += f", Isactive={str(active).lower()}"
        if mark_as:
            update_str += f", Markas='{mark_as}'"
        if ref_point_visible:
            update_str += f", RPVISIBLE={str(ref_point_visible).lower()}"
        if update_str:
            update_str = update_str[1:]

        lua_script = f"Hs_ScenEdit_SetZone('{self.guid}', '{zone_guid}', {{{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    def get_reference_point_by_name(self, name: str) -> "CReferencePoint | None":
        """
        根据参考点名称获取参考点对象

        Args:
            - name (str): 参考点名称

        Returns:
            None 或 参考点对象
        """
        ref_points = self.get_reference_points()
        for v in ref_points.values():
            if v.name == name:
                return v
        return None

    async def assign_target_to_mission(self, contact_guid: str, mission_name_or_guid: str) -> bool:
        """
        将目标分配给一项打击任务

        Args:
            - contact_guid (str): 目标guid
            - mission_name_or_guid (str): 任务名称或guid

        Returns:
            bool: 执行结果
        """
        lua = f"ScenEdit_AssignUnitAsTarget('{{{contact_guid}}}', '{mission_name_or_guid}')"
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success

    async def drop_contact(self, contact_guid: str) -> bool:
        """
        放弃目标, 不再将所选目标列为探测对象

        Args:
            - contact_guid (str): 探测目标guid

        Returns:
            bool: 执行结果
        """
        lua_script = f"Hs_ContactDropTarget('{self.guid}','{contact_guid}')"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def wcsfa_contact_types_all_unit(self, attack_status: Literal["Hold", "Tight", "Free", "Inherited"]) -> bool:
        """
        控制所有单元对所有目标类型的攻击状态。

        Args:
            - attack_status (str): 攻击状态
                - 'Hold'-禁止
                - 'Tight'-限制
                - 'Free'-自由
                - 'Inherited'-按上级条令执行

        Returns:
            bool: 执行结果
        """
        lua = f"Hs_WCSFAContactTypesAllUnit('{self.guid}','{attack_status}')"
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success

    async def lpcw_attack_all_unit(self, ignore_planned_path: Literal["Yes", "No", "Inherited"]) -> bool:
        """
        所有单元攻击时是否忽略计划航线。

        Args:
            ignore_planned_path (str): 是否忽略计划航线
                - 'Yes' - 忽略
                - 'No' - 不忽略
                - 'Inherited' - 按上级条令执行

        Returns:
            bool: 执行结果
        """
        lua = f"Hs_LPCWAttackAllUnit('{self.guid}','{ignore_planned_path}')"
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success

    async def set_side_options(
        self,
        awareness: Literal["Blind", "Normal", "AutoSideID", "AutoSideAndUnitID", "OMNI"] | None = None,
        proficiency: Literal["Novice", "Cadet", "Regular", "Veteran", "Ace"] | None = None,
        ai_only: bool | None = None,
        coll_response: bool | None = None,
        auto_track_civs: bool | None = None,
    ) -> bool:
        """
        设置认知能力、训练水平、AI 操控、集体反应、自动跟踪非作战单元等组成的属性集合

        Args:
            - awareness (str):
                - Blind-一无所知
                - Normal-普通水平
                - AutoSideID-知其属方
                - AutoSideAndUnitID-知其属方与单元
                - OMNI-无所不知
            - proficiency (str):
                - Novice-新手
                - Cadet-初级
                - Regular-普通
                - Veteran-老手
                - Ace-顶级
            - ai_only (bool): 推演方是否由计算机扮演
            - coll_response (bool): 推演方是否集体反应
            - auto_track_civs (bool): 推演方是否自动跟踪非作战单元

        Returns:
            bool: 执行结果
        """
        update_str = ""
        if awareness:
            update_str += f", awareness='{awareness}'"
        if proficiency:
            update_str += f", proficiency='{proficiency}'"
        if ai_only:
            update_str += f", isAIOnly={str(ai_only).lower()}"
        if coll_response:
            update_str += f", isCollRespons={str(coll_response).lower()}"
        if auto_track_civs:
            update_str += f", isAutoTrackCivs={str(auto_track_civs).lower()}"
        if not update_str:
            return False
        lua_script = f"ScenEdit_SetSideOptions({{side='{self.name}'{update_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def get_side_options(self) -> dict | None:
        """
        获取推演方属性

        Returns:
            dict: 推演方属性字典
            example: {'proficiency': 'Regular', 'side': '红方',
                    'guid': 'f40500f8-dbde-4b02-9190-a8453a922c98', 'awareness': 'Normal'}
        """
        lua_script = f"print(ScenEdit_GetSideOptions({{side='{self.name}'}}))"
        response = await self.mozi_server.send_and_recv(lua_script)
        if self.name in response.raw_data:
            return self.__convert_lua_obj_to_dict(response.raw_data)
        return None

    async def get_side_is_human(self) -> bool:
        """
        获取推演方操控属性，以便判断该推演方是人操控还是计算机操控

        Returns:
            bool:
                True-推演方由人操控
                False-推演方只由计算机扮演
        """
        lua_script = f"print(ScenEdit_GetSideIsHuman('{self.name}'))"
        response = await self.mozi_server.send_and_recv(lua_script)
        if "yes" in response.raw_data.lower():
            return True
        if "no" in response.raw_data.lower():
            return False
        raise ValueError(f"推演方{self.name}的操控属性获取失败，返回值为{response.raw_data}")

    async def remove_zone(self, zone_guid: str) -> bool:
        """
        删除指定推演方的指定禁航区或封锁区

        Args:
            zone_guid (str): 区域guid

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(f"Hs_ScenEdit_RemoveZone('{self.name}','{zone_guid}')")
        return response.lua_success

    async def delete_reference_point(self, point_guid: str) -> bool:
        """
        删除参考点

        Args:
            point_guid (str): 参考点guid

        Returns:
            bool: 执行结果
        """
        set_str = f'ScenEdit_DeleteReferencePoint({{side="{self.guid}",guid="{point_guid}"}})'
        response = await self.mozi_server.send_and_recv(set_str)
        return response.lua_success

    async def delete_reference_point_by_name(self, ref_point_name: str) -> bool:
        """
        按参考点名称删除参考点

        Args:
            ref_point_name (str): 参考点名称

        Returns:
            bool: 执行结果
        """
        set_str = f'ScenEdit_DeleteReferencePoint({{side="{self.guid}",name="{ref_point_name}"}})'
        response = await self.mozi_server.send_and_recv(set_str)
        return response.lua_success

    async def add_plan_way(self, way_type: Literal[0, 1], way_name: str) -> bool:
        """
        为指定推演方添加一预设航线（待指定航路点）

        Args:
            way_type (int): 航线类型
                - 0-单元航线
                - 1-武器航线
            way_name (str): 航线名称

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(f"Hs_AddPlanWay('{self.name}',{way_type},'{way_name}')")
        return response.lua_success

    async def set_plan_way_showing_status(self, way_name_or_id: str, show: bool) -> bool:
        """
        控制预设航线的显示或隐藏

        Args:
            way_name_or_id (str): 航线名称或guid
            show (bool): 是否显示
                - True-显示
                - False-隐藏

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_PlanWayIsShow('{self.guid}','{way_name_or_id}',{str(show).lower()})"
        )
        return response.lua_success

    async def rename_plan_way(self, way_name_or_id: str, new_name: str) -> bool:
        """
        修改预设航线的名称

        Args:
            way_name_or_id (str): 航线名称或guid
            new_name (str): 新的航线名称

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_RenamePlanWay('{self.guid}','{way_name_or_id}','{new_name}')"
        )
        return response.lua_success

    async def add_plan_way_point(self, way_name_or_id: str, latitude: float, longitude: float) -> bool:
        """
        为预设航线添加航路点

        Args:
            way_name_or_id (str): 航线名称或guid
            latitude (float): 纬度
            longitude (float): 经度

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_AddPlanWayPoint('{self.guid}','{way_name_or_id}',{longitude},{latitude})"
        )
        return response.lua_success

    async def update_plan_way_point(self, way_name_or_id: str, way_point_id: str, table: dict) -> bool:
        """
        修改航路点信息

        Args:
            - way_name_or_id (str): 航线名称或guid
            - way_point_id (str): 航路点guid
            - table (dict): 航路点信息
                - {NAME='12',LONGITUDE = 12.01,LATITUDE=56.32,ALTITUDE=1(为0-7的数值)，THROTTLE = 1(为0-5
                      的数值)，RADAR= 1(为0-2的数值),SONAR=1(为0-2的数值) ,OECM=1(为0-2的数值)},可根据需要自己构造

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_UpDataPlanWayPoint('{self.guid}','{way_name_or_id}','{way_point_id}',{table})"
        )
        return response.lua_success

    async def remove_plan_way_point(self, way_name_or_id: str, way_point_id: str) -> bool:
        """
        删除航路点

        Args:
            way_name_or_id (str): 航线名称或guid
            way_point_id (str): 航路点guid

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_RemovePlanWayPoint('{self.guid}','{way_name_or_id}','{way_point_id}')"
        )
        return response.lua_success

    async def remove_plan_way(self, way_name_or_id: str) -> bool:
        """
        删除预设航线

        Args:
            way_name_or_id (str): 航线名称或guid

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(f"Hs_RemovePlanWay('{self.guid}','{way_name_or_id}')")
        return response.lua_success

    async def edit_brief(self, briefing: str) -> bool:
        """
        修改指定推演方的任务简报

        Args:
            briefing (str): 任务简报

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(f"Hs_EditBriefing('{self.guid}','{briefing}')")
        return response.lua_success

    def is_target_existed(self, target_name: str) -> bool:
        """
        检查目标是否存在

        Args:
            target_name (str): 目标名称

        Returns:
            bool
        """
        ret = self.get_guid_from_name(target_name, self.contacts)
        if ret:
            return True
        return False

    @staticmethod
    def get_guid_from_name(_name: str, _dic: dict) -> str | None:
        """
        通过名字查找guid

        Args:
            _name (str): 对象名称
            _dic (dict): 字典：key为对象guid，value为对象实例

        Returns:
            str | None: 对象guid
        """
        for key, value in _dic.items():
            if _name in value.name:
                return key
        return None

    async def hold_position_all_units(self, hold: bool) -> bool:
        """
        保持所有单元阵位，所有单元停止机动，留在原地

        Args:
            hold (bool): 是否保持

        Returns:
            bool
        """
        cmd = f"Hs_HoldPositonAllUnit('{self.guid}', {str(hold).lower()})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def launch_units_in_group(self, units: list["CActiveUnit"]) -> bool:
        """
        停靠任务编队出航

        Args:
            units (list["CActiveUnit"]): 活动单元对象列表

        Returns:
            bool
        """
        _units = [v.guid for v in units]
        table = str(_units).replace("[", "{").replace("]", "}")
        cmd = f"Hs_ScenEdit_DockingOpsGroupOut({table})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def launch_units_abort(self, units: list["CActiveUnit"]) -> bool:
        """
        停靠任务终止出航

        Args:
            units (list["CActiveUnit"]): 活动单元对象列表

        Returns:
            bool
        """
        _units = [v.guid for v in units]
        table = str(_units).replace("[", "{").replace("]", "}")
        cmd = f"Hs_ScenEdit_DockingOpsAbortLaunch({table})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_mark_contact(self, contact_guid: str, relation: str) -> bool:
        """
        设置目标对抗关系

        Args:
            contact_guid (str): 目标guid
            relation (str): 目标立场类型
                - 'F'-友方
                - 'N'-中立
                - 'U'-非友方
                - 'H'-敌方

        Returns:
            bool
        """
        lua = f"Hs_SetMarkContact('{self.name}', '{contact_guid}', '{relation}')"
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success

    async def delete_group(self, group_name: str, remove_child: bool = False) -> bool:
        """
        删除编组
        限制：专项赛禁用设置 remove_child='true'

        Args:
            - group_name: 编组名称
            - remove_child: 是否删除编组内子单元
                - True - 是
                - False - 否

        Returns:
            bool
        """
        response = await self.mozi_server.send_and_recv(
            f"ScenEdit_DeleteUnit({{name='{group_name}', Removechild={str(remove_child).lower()}}})"
        )
        return response.lua_success

    async def add_unit(
        self,
        unit_type: Literal["submarine", "ship", "facility", "aircraft"],
        name: str,
        db_id: int,
        latitude: float,
        longitude: float,
        heading: int,
    ) -> tuple[bool, "CAircraft | CFacility | CShip | CSubmarine | None"]:
        """
        添加单元  # 朝向和高度设置不起作用
        限制：专项赛禁用

        Args:
            unit_type (Literal["submarine", "ship", "facility", "aircraft"]): 单元类型
                - submarine - 潜艇
                - ship - 舰船
                - facility - 地面兵力设施
                - aircraft - 飞机
            name (str): 单元名称
            db_id (int): 单元数据库dbid
            latitude (float): 纬度
            longitude (float): 经度
            heading (int): 朝向

        Returns:
            tuple[bool, "CAircraft | CFacility | CShip | CSubmarine | None"]: 执行结果和创建的活动单元对象
        """
        guid = self.situation.generate_guid()
        cmd = (
            f"HS_LUA_AddUnit({{side = '{self.name}', guid = '{guid}', type = '{unit_type}', name = '{name}', dbid = {db_id}, latitude = {latitude}, "
            f"longitude = {longitude}, heading = {heading}}})"
        )
        response = await self.mozi_server.send_and_recv(cmd)
        type_selected: dict[str, type[CSubmarine] | type[CShip] | type[CFacility] | type[CAircraft]] = {
            "submarine": CSubmarine,
            "ship": CShip,
            "facility": CFacility,
            "aircraft": CAircraft,
        }
        if response.lua_success:
            self.mozi_server.throw_into_pool(cmd)
            self.situation.throw_into_pseudo_situ_all_guid(guid)
            obj = type_selected[unit_type](guid, self.mozi_server, self.situation)
            obj.name = name
            obj.db_id = db_id
            obj.latitude = latitude
            obj.longitude = longitude
            obj.current_heading = heading
        else:
            obj = None
        return response.lua_success, obj

    async def add_submarine(
        self, name: str, db_id: int, latitude: float, longitude: float, heading: int
    ) -> tuple[bool, "CSubmarine | None"]:
        """
        添加潜艇  # 朝向和高度设置不起作用
        限制：专项赛禁用

        Args:
            name (str): 单元名称
            db_id (int): 单元数据库dbid
            latitude (float): 纬度
            longitude (float): 经度
            heading (int): 朝向

        Returns:
            tuple[bool, "CSubmarine | None"]: 执行结果和创建的活动单元对象
        """
        guid = self.situation.generate_guid()
        cmd = (
            f"HS_LUA_AddUnit({{type = 'SUB', name = '{name}', guid = '{guid}', heading = {heading}, dbid = {db_id}, "
            f"side = '{self.name}', latitude={latitude}, longitude={longitude}}})"
        )
        response = await self.mozi_server.send_and_recv(cmd)
        obj = None
        if response.lua_success:
            self.mozi_server.throw_into_pool(cmd)
            self.situation.throw_into_pseudo_situ_all_guid(guid)
            obj = CSubmarine(guid, self.mozi_server, self.situation)
            obj.name = name
            obj.db_id = db_id
            obj.latitude = latitude
            obj.longitude = longitude
            obj.current_heading = heading
        return response.lua_success, obj

    async def add_ship(
        self, name: str, db_id: int, latitude: float, longitude: float, heading: int
    ) -> tuple[bool, "CShip | None"]:
        """
        添加舰船 # 朝向和高度设置不起作用
        限制：专项赛禁用

        Args:
            name (str): 单元名称
            db_id (int): 单元数据库dbid
            latitude (float): 纬度
            longitude (float): 经度
            heading (int): 朝向

        Returns:
            tuple[bool, "CShip | None"]: 执行结果和创建的活动单元对象
        """
        guid = self.situation.generate_guid()
        cmd = (
            f"HS_LUA_AddUnit({{type = 'ship', name = '{name}', guid = '{guid}', heading = {heading}, dbid = {db_id}, "
            f"side = '{self.name}', latitude={latitude}, longitude={longitude}}})"
        )
        response = await self.mozi_server.send_and_recv(cmd)
        obj = None
        if response.lua_success:
            self.mozi_server.throw_into_pool(cmd)
            self.situation.throw_into_pseudo_situ_all_guid(guid)
            obj = CShip(guid, self.mozi_server, self.situation)
            obj.name = name
            obj.db_id = db_id
            obj.latitude = latitude
            obj.longitude = longitude
            obj.current_heading = heading
        return response.lua_success, obj

    async def add_facility(
        self, name: str, db_id: int, latitude: float, longitude: float, heading: int
    ) -> tuple[bool, "CFacility | None"]:
        """
        添加地面兵力设施  # 朝向设置不起作用
        限制：专项赛禁用

        Args:
            name (str): 单元名称
            db_id (int): 单元数据库dbid
            latitude (float): 纬度
            longitude (float): 经度
            heading (int): 朝向

        Returns:
            tuple[bool, "CFacility | None"]: 执行结果和创建的活动单元对象
        """
        guid = self.situation.generate_guid()
        cmd = (
            f"HS_LUA_AddUnit({{type = 'facility', name = '{name}', guid = '{guid}', heading = {heading}, dbid = {db_id}, "
            f"side = '{self.name}', latitude={latitude}, longitude={longitude}}})"
        )
        response = await self.mozi_server.send_and_recv(cmd)
        obj = None
        if response.lua_success:
            self.mozi_server.throw_into_pool(cmd)
            self.situation.throw_into_pseudo_situ_all_guid(guid)
            obj = CFacility(guid, self.mozi_server, self.situation)
            obj.name = name
            obj.db_id = db_id
            obj.latitude = latitude
            obj.longitude = longitude
            obj.current_heading = heading
        return response.lua_success, obj

    async def add_aircraft(
        self,
        name: str,
        db_id: int,
        loadout_db_id: int,
        latitude: float,
        longitude: float,
        altitude: int,
        heading: int,
    ) -> tuple[bool, "CAircraft | None"]:
        """
        添加飞机  # 高度和朝向设置不起作用
        限制：专项赛禁用

        Args:
            name (str): 单元名称
            db_id (int): 单元数据库dbid
            loadout_db_id (int): 挂载dbid
            latitude (float): 纬度
            longitude (float): 经度
            heading (int): 朝向

        Returns:
            tuple[bool, "CAircraft | None"]: 执行结果和创建的活动单元对象
        """
        guid = self.situation.generate_guid()
        cmd = (
            f"HS_LUA_AddUnit({{type = 'air', name = '{name}', guid = '{guid}', loadoutid = {loadout_db_id}, heading = {heading}, dbid = {db_id}, "
            f"side = '{self.name}', latitude={latitude}, longitude={longitude}, altitude={altitude}}})"
        )
        response = await self.mozi_server.send_and_recv(cmd)
        obj = None
        if response.lua_success:
            self.mozi_server.throw_into_pool(cmd)
            self.situation.throw_into_pseudo_situ_all_guid(guid)
            obj = CAircraft(guid, self.mozi_server, self.situation)
            obj.name = name
            obj.db_id = db_id
            obj.loadout_db_id = loadout_db_id
            obj.latitude = latitude
            obj.longitude = longitude
            obj.current_altitude_asl = altitude
            obj.current_heading = heading
        return response.lua_success, obj

    async def add_satellite(self, satellite_db_id: int, orbital: str) -> tuple[bool, "CSatellite | None"]:
        """
        添加卫星
        限制：专项赛禁用

        Args:
            satellite_db_id (int): 卫星db id
            orbital (str): 卫星轨道编号

        Returns:
            tuple[bool, "CSatellite | None"]: 执行结果和创建的活动单元对象
        """
        cmd = f"Hs_AddSatellite('{self.name}','{satellite_db_id}',{orbital})"
        response = await self.mozi_server.send_and_recv(cmd)
        obj = None
        if response.lua_success:
            self.mozi_server.throw_into_pool(cmd)
            obj = CSatellite("generate-obj-for-cmd-operation", self.mozi_server, self.situation)
            obj.db_id = satellite_db_id
            obj.tracks_points = orbital
        return response.lua_success, obj

    async def import_inst_file(self, filename: str) -> bool:
        """
        导入 inst 文件  # 具体用法待确定
        限制：专项赛禁用

        Args:
            filename (str): inst 文件名

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(f"ScenEdit_ImportInst('{self.name}','{filename}')")
        return response.lua_success

    async def import_mission(self, mission_name: str) -> bool:
        """
        从 Defaults 文件夹中查找对应的任务，导入到想定中
        专项赛禁用

        Args:
            mission_name (str): 任务名称

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(f"ScenEdit_ImportMission('{self.guid}','{mission_name}')")
        return response.lua_success

    async def add_unit_to_facility(
        self,
        unit_type: Literal["facility", "submarine", "ship", "aircraft"],
        name: str,
        db_id: int,
        base_unit_guid: str,
        loadout_id: int | None = None,
    ) -> "CSubmarine | CShip | CFacility | CAircraft | None":
        """
        往机场，码头添加单元
        限制：专项赛禁用

        Args:
            unit_type (Literal["facility", "submarine", "ship", "aircraft"]): 单元类型
            name (str): 单元名称
            dbid (int): 单元数据库dbid
            base_unit_guid (str): 机场、码头单元guid
            loadout_id (int | None): 飞机的挂载方案dbid

        Returns:
            CSubmarine | CShip | CFacility | CAircraft | None: 所添加单元的活动单元对象
        """
        loadout_str = ""
        if loadout_id:
            loadout_str = f", loadoutid={loadout_id}"
        lua_script = (
            f"ReturnObj(ScenEdit_AddUnit({{type='{unit_type}', unitname='{name}',side='{self.name}', "
            f"dbid={db_id}, base='{base_unit_guid}'{loadout_str}}}))"
        )
        response = await self.mozi_server.send_and_recv(lua_script)

        if "unit {" in response.raw_data:
            # 将返回的字符串转换成字典
            return_dict = self.__convert_lua_obj_to_dict(response.raw_data)
            self.situation.throw_into_pseudo_situ_all_guid(return_dict["guid"])
            type_selected: dict[str, type[CSubmarine] | type[CShip] | type[CFacility] | type[CAircraft]] = {
                "submarine": CSubmarine,
                "ship": CShip,
                "facility": CFacility,
                "aircraft": CAircraft,
            }
            obj = type_selected[unit_type](return_dict["guid"], self.mozi_server, self.situation)
            obj.name = name
            obj.side = self.guid
            obj.host_active_unit = base_unit_guid
            return obj
        return None

    async def delete_all_unit(self) -> bool:
        """
        删除本方所有单元
        限制：专项赛禁用

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(f"Hs_DeleteAllUnits('{self.name}')")
        return response.lua_success

    async def deploy_mine(self, mine_db_guid: str, mine_count: int, area: list[str]) -> bool:
        """
        给某一方添加雷
        限制：专项赛禁用

        Args:
            mine_db_guid (str): 水雷数据库guid
            mine_count (int): 水雷数量
            area (list[str]): 参考点名称列表

        Returns:
            bool: 执行结果
        """
        area_str = ""
        for rp in area:
            rp_obj = self.get_reference_point_by_name(rp)
            if rp_obj:
                area_str += f", {{lat={rp_obj.latitude}, lon={rp_obj.longitude}}}"
        if area_str:
            area_str = area_str[1:]
        lua_script = f"Hs_DeployMine('{self.name}', '{mine_db_guid}', {mine_count}, {{{area_str}}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def set_new_name(self, new_name: str) -> bool:
        """
        推演方重命名
        限制：专项赛禁用

        Args:
            new_name (str): 新的推演方名称

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(f"Hs_SetSideName('{self.name}','{new_name}')")
        return response.lua_success

    async def set_score(self, score: int, reason_for_change: str = "") -> bool:
        """
        设置推演方总分
        限制：专项赛禁用

        Args:
            score (int): 推演方总分
            reason_for_change (str): 总分变化原因

        Returns:
            bool: 执行结果
        """
        lua = f"ScenEdit_SetScore('{self.guid}',{score},'{reason_for_change}')"
        response = await self.mozi_server.send_and_recv(lua)
        return response.lua_success

    async def side_scoring(self, defeat_threshold: int, victory_threshold: int) -> bool:
        """
        设置完胜完败阈值
        限制：专项赛禁用

        Args:
            defeat_threshold (int): 完败分数线
            victory_threshold (int): 完胜分数线

        Returns:
            bool: 执行结果
        """
        response = await self.mozi_server.send_and_recv(
            f"Hs_SideScoring('{self.guid}',{defeat_threshold},{victory_threshold})"
        )
        return response.lua_success

    async def copy_unit(self, unit_name: str, latitude: float, longitude: float) -> bool:
        """
        将想定中当前推演方中的已有单元复制到指定经纬度处
        限制：专项赛禁用

        Args:
            unit_name (str): 被复制的单元名称
            latitude (float): 纬度
            longitude (float): 经度

        Returns:
            bool: 执行结果
        """
        lua_script = f"Hs_CopyUnit('{unit_name}',{longitude},{latitude})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def delete_unit(self, unit_name: str) -> bool:
        """
        删除当前推演方中指定单元
        限制：专项赛禁用

        Args:
            unit_name (str): 单元名称

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_DeleteUnit({{name='{unit_name}'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def kill_unit(self, unit_name: str) -> bool:
        """
        摧毁单元
        摧毁指定推演方的指定单元，并输出该摧毁事件的消息，并影响到战损统计
        限制：专项赛禁用

        Args:
            unit_name (str): 单元名称

        Returns:
            bool: 执行结果
        """
        lua_script = f"ScenEdit_KillUnit({{side='{self.name}',name='{unit_name}'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success
