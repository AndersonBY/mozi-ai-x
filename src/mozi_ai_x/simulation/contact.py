from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .server import MoziServer
    from .situation import CSituation
    from .side import CSide

from .base import Base
from .situ_interpret import CContactDict


class CContact(Base):
    contact_type_map = {
        # 空中目标
        0: "Air",
        # 导弹
        1: "Missile",
        # 水面 / 地面
        2: "Surface",
        # 潜艇
        3: "Submarine",
        # 未确定的海军
        4: "UndeterminedNaval",
        # 瞄准点？？
        5: "Aimpoint",
        # 轨道目标
        6: "Orbital",
        # 固定设施
        7: "Facility_Fixed",
        # 移动设施
        8: "Facility_Mobile",
        # 鱼雷
        9: "Torpedo",
        # 水雷
        10: "Mine",
        # 爆炸
        11: "Explosion",
        # 不确定
        12: "Undetermined",
        # 空中诱饵
        13: "Decoy_Air",
        # 表面诱饵
        14: "Decoy_Surface",
        # 陆地诱饵
        15: "Decoy_Land",
        # 水下诱饵
        16: "Decoy_Sub",
        # 声纳浮标
        17: "Sonobuoy",
        # 军事设施
        18: "Installation",
        # 空军基地
        19: "AirBase",
        # 海军基地
        20: "NavalBase",
        # 移动集群
        21: "MobileGroup",
        # 激活点：瞄准点
        22: "ActivationPoint",
    }

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        # 地理高度
        self.altitude_agl = 0.0
        # 海拔高度
        self.altitude_asl = 0
        # 所在推演方ID
        self.side = ""
        # 实体类别
        self.unit_class = ""
        # 当前纬度
        self.latitude = 0.0
        # 当前经度
        self.longitude = 0.0
        # 当前朝向
        self.current_heading = 0.0
        # 当前速度
        self.current_speed = 0.0
        # 当前海拔高度
        self.current_altitude_asl = 0.0
        # 倾斜角
        self.pitch = 0.0
        # 翻转角
        self.roll = 0.0
        # 是否在陆地上
        self.on_land = False
        # 可能匹配结果
        self.matching_db_id_list = ""
        # 识别出的辐射平台
        self.radiant_point = ""
        self.icon_type = ""
        self.common_icon = ""
        # 目标类型
        self.contact_type = 0
        # 属方是否已知
        self.side_is_known = False
        # 单元的识别状态
        # 0--未知
        # 1--已知空域（如空中、地面）
        # 2--已知类型（如飞机、导弹）
        # 3--已知级别
        # 4--确认对象
        self.identification_status = 0
        # 本身单元的GUID
        self.actual_unit = ""
        # 探测到的推演方
        self.original_detector_side = ""
        # 其它推演方对本目标的立场姿态
        self.side_posture_stance_dictionary = ""
        # 速度是否已知
        self.speed_known = False
        # 朝向是否已知
        self.heading_known = False
        # 高度是否已知
        self.altitude_known = False
        # 电磁辐射Title
        self.electromagnetism_eradiate_title = ""
        # 电磁辐射集合
        self.electromagnetism_eradiate = ""
        # 匹配结果标题
        self.matching_title = ""
        # 侦察记录
        self.detection_record = ""
        # 不确定区域集合
        self.uncertainty_area = ""
        # 目标持续时间
        self.age = ""
        # 取目标发射源容器中传感器的最大探测距离
        self.max_detect_range = 0.0
        # 获取最大对海探测范围
        self.max_range_detect_surface_and_facility = 0.0
        # 获取最大对潜探测范围
        self.max_range_detect_subsurface = 0.0
        # 获取目标探测时间
        self.time_since_detection_visual = 0.0
        # 获取瞄准目标的武器数量
        self.weapons_aiming_at_me = 0
        # 目标武器对空最大攻击距离
        self.air_range_max = 0.0
        # 目标武器对海最大攻击距离
        self.surface_range_max = 0.0
        # 目标武器对陆最大攻击距离
        self.land_range_max = 0.0
        # 目标武器对潜最大攻击距离
        self.subsurface_range_max = 0.0
        # 态势控制——目标电磁辐射显示信息
        self.contact_emissions = ""
        self.original_detector_side = ""

        self.var_map = CContactDict.var_map

    def get_type_description(self):
        """
        获取探测目标的类型描述

        Returns:
            str: 以 self.contact_type 为 key 获取的 self.contact_type_map 中的值
        """
        return self.contact_type_map[self.contact_type]

    def get_contact_info(self):
        """
        获取目标信息字典

        Returns:
            dict: 目标信息字典
        """
        info_dict = {
            "type": self.get_type_description(),
            "typed": self.contact_type,
            "classification_level": self.identification_status,
            "name": self.name,
            "guid": self.actual_unit,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.current_altitude_asl,
            "heading": self.current_heading,
            "speed": self.current_speed,
            "firing_at": [],
            "missile_defence": 0,
            "from_units": self.detection_record,
            "fg": self.guid,
        }
        return info_dict

    def get_original_detector_side(self) -> "CSide":
        """
        获取探测到单元的方

        Returns:
            CSide: 推演方对象
        """
        return self.situation.side_dict[self.original_detector_side]

    def get_original_target_side(self) -> "CSide":
        """
        获取目标单元所在方

        Returns:
            CSide: 推演方对象
        """
        return self.situation.side_dict[self.side]

    async def set_mark_contact(self, contact_type: Literal["F", "N", "U", "H"]) -> bool:
        """
        标识目标立场

        Args:
            contact_type (str): 'F'-友方，'N'-中立，'U'-非友方，'H'-敌方

        Returns:
            bool: 执行结果
        """
        lua_script = f"Hs_SetMarkContact('{self.original_detector_side}', '{self.guid}', '{contact_type}')"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def rename(self, new_name: str) -> bool:
        """
        重命名目标

        Args:
            new_name (str): 新的目标名称

        Returns:
            bool: 执行结果
        """
        lua_script = f"Hs_ContactRename('{self.original_detector_side}', '{self.guid}', '{new_name}')"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    async def drop_target(self) -> bool:
        """
        放弃目标，不再将所选目标列为探测对象。

        Returns:
            bool: 执行结果
        """
        lua_script = f"Hs_ContactDropTarget('{self.original_detector_side}', '{self.guid}')"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    def get_actual_unit(self):
        """
        获取目标真实单元
        """
        return self.situation.get_obj_by_guid(self.actual_unit)
