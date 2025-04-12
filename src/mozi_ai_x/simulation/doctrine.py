from typing import TYPE_CHECKING, Literal, overload

if TYPE_CHECKING:
    from .server import MoziServer
    from .situation import CSituation
    from .types import ObjectTypes

from .base import Base
from .side import CSide
from .response import CResponse
from .active_unit import CGroup
from .mission import MissionTypes
from .situ_interpret import CDoctrineDict
from ..utils.log import mprint_with_name
from mozi_ai_x.utils.validator import validate_literal_args

mprint = mprint_with_name("Doctrine")


class CDoctrine(Base):
    """
    条令类
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 条令属主类型
        self.category: str | None = None
        # 条令的拥有者GUID（具体作用对象）
        self.doctrine_owner = ""
        # 核武器使用规则
        self.nukes = 0
        # 对空目标武器控制规则
        self.wcs_air = 0
        # 对海目标武器控制规则C
        self.wcs_surface = 0
        # 对潜目标武器控制规则
        self.wcs_submarine = 0
        # 对地目标武器控制规则
        self.wcs_land = 0
        # 进攻时是否忽略绘制航线规则
        self.ignore_plotted_course_when_attacking = 0
        # 对不明目标的行为态度规则
        self.behavior_towards_ambigous_target = 0
        # 对临机目标进行射击规则
        self.shoot_tourists = 0
        # 受攻击时是否考虑电磁管控规则
        self.ignore_emcon_under_attack = 0
        # 鱼雷使用动力航程规则
        self.use_torpedoes_kinematic_range = 0
        # 是否自动规避目标规则
        self.automatic_evasion = 0
        # 是否可加油/补给规则
        self.use_refuel = 0
        # 对所选单元加油/补给时加油机选择规则
        self.refuel_selection = 0
        # 与盟军单元加油/补给规则
        self.refuel_allies = 0
        # 空战节奏规则
        self.air_ops_tempo = 0
        # 快速出动规则
        self.quick_turnaround = 0
        # 预先规划终止任务返回基地油量阈值规则
        self.bingo_joker = 0
        # 编组成员达到预先规划油量状态时编组或成员返回基地规则
        self.bingo_joker_rtb = 0
        # 预先规划武器使用规则、武器状态与平台脱离战斗规则
        self.weapon_state = 0
        # 编组成员达到预先规划武器状态时，编组或成员返回基地规则
        self.weapon_state_rtb = 0
        # 航炮是否对地面目标扫射规则
        self.gun_strafe_ground_targets = 0
        # 受到攻击时是否抛弃弹药规则
        self.jettison_ordnance = 0
        # 以反舰模式使用舰空导弹规则
        self.sam_asuw = 0
        # 与目标保持一定距离规则
        self.maintaining_standoff = 0
        # 尽可能规避目标规则
        self.avoid_contact = 0
        # 探测到威胁目标后下潜规则
        self.dive_when_threats_detected = 0
        # 巡逻任务充电时电池剩余电量规则
        self.recharge_percentage_patrol = 0
        # 进攻战充电时电池剩余电量规则
        self.recharge_percentage_attack = 0
        # AIP推进技术使用规则
        self.aip_usage = 0
        # 吊放声呐使用规则
        self.dipping_sonar = 0
        # 毁伤达到阈值时应撤退规则
        self.withdraw_damage_threshold = 0
        # 油量达到阈值时应撤退规则
        self.withdraw_fuel_threshold = 0
        # 进攻战武器数量达到阈值应撤退规则
        self.withdraw_attack_threshold = 0
        # 防御战武器数量达到阈值应撤退规则
        self.withdraw_defence_threshold = 0
        # 毁伤达到阈值时应重新部署规则
        self.redeploy_damage_threshold = 0
        # 油量达到阈值时应重新部署规则
        self.redeploy_fuel_threshold = 0
        # 进攻战武器数量达到阈值时应重新部署规则
        self.redeploy_attack_threshold = 0
        # 防御战武器数量达到阈值时应重新部署规则
        self.redeploy_defence_threshold = 0
        # 电磁管控设置是否有值
        self.emcon_according_to_superior = False
        # 雷达管控规则设置模式
        self.emcon_radar_mode = 0
        # 声呐管控规则设置模式
        self.emcon_sonar_mode = 0
        # 进攻型电子对抗措施（干扰机）管控规则设置模式
        self.emcon_oecm_mode = 0
        # 武器使用规则的武器DBID
        self.weapon_rule_db_id = ""
        # 武器使用规则
        self.weapon_rule = ""
        # 使用核武器
        self.use_nuclear = False
        # 武器控制状态对空是否允许用户编辑
        self.weapon_control_air_edit = False
        # 武器控制状态对海是否允许用户编辑
        self.weapon_control_surface_edit = False
        # 武器控制状态对潜是否允许用户编辑
        self.weapon_control_subsurface_edit = False
        # 武器控制状态对地是否允许用户编辑
        self.weapon_control_land_edit = False
        # 受到攻击时忽略计划航线是否允许用户编辑
        self.ignore_routes_edit = False
        # 接战模糊位置目标是否允许用户编辑
        self.engage_fuzzy_targets_edit = False
        # 接战临机出现目标是否允许用户编辑
        self.engage_opportunity_targets_edit = False
        # 受攻击时忽略电磁管控是否允许用户编辑
        self.ignore_emcon_edit = False
        # 鱼雷使用动力航程是否允许用户编辑
        self.torpedo_kinematic_range_edit = False
        # 自动规避是否允许用户编辑
        self.auto_evade_edit = False
        # 加油/补给是否允许用户编辑
        self.refuel_edit = False
        # 对所选单元进行加油/补给是否允许用户编辑
        self.refuel_selected_edit = False
        # 对盟军单元进行加油/补给是否允许用户编辑
        self.refuel_allies_edit = False
        # 空战节奏是否允许用户编辑
        self.air_ops_tempo_edit = False
        # 快速出动是否允许用户编辑
        self.quick_turnaround_edit = False
        # 燃油状态，预先规划是否允许用户编辑
        self.fuel_state_planned_edit = False
        # 燃油状态—返航是否允许用户编辑
        self.fuel_state_rtb_edit = False
        # 武器状态, 预先规划是否允许用户编辑
        self.weapon_state_planned_edit = False
        # 武器状态-返航是否允许用户编辑
        self.weapon_state_rtb_edit = False
        # 空对地扫射(航炮)是否允许用户编辑
        self.gun_strafe_edit = False
        # 抛弃弹药是否允许用户编辑
        self.jettison_ordnance_edit = False
        # 以反舰模式使用舰空导弹规则是否允许用户编辑
        self.sam_asuw_edit = False
        # 与目标保持一定距离规则是否允许用户编辑
        self.maintain_standoff_edit = False
        # 规避搜索规则是否允许用户编辑
        self.avoid_contact_edit = False
        # 探测到威胁进行下潜规则是否允许用户编辑
        self.dive_on_threat_edit = False
        # 电池充电 %, 出航/阵位是否允许用户编辑
        self.recharge_patrol_edit = False
        # 电池充电%, 进攻/防御是否允许用户编辑
        self.recharge_attack_edit = False
        # 使用AIP推进技术是否允许用户编辑
        self.aip_edit = False
        # 吊放声纳是否允许用户编辑
        self.dipping_sonar_edit = False

        self.var_map = CDoctrineDict.var_map

    @overload
    def get_doctrine_owner(self, raise_error: Literal[True]) -> "ObjectTypes": ...

    @overload
    def get_doctrine_owner(self, raise_error: Literal[False]) -> "ObjectTypes | None": ...

    @overload
    def get_doctrine_owner(self) -> "ObjectTypes": ...

    def get_doctrine_owner(self, raise_error: bool = True) -> "ObjectTypes | None":
        """
        获取条令所有者

        Args:
            raise_error: 是否在获取失败时抛出异常

        Returns:
            条令所有者
        """
        owner = self.situation.get_obj_by_guid(self.doctrine_owner)
        if owner is None and raise_error:
            mprint.error("获取条令所有者失败")
            return None
        return owner

    @staticmethod
    def _classify_owner(owner: "ObjectTypes") -> str:
        """
        对条令所属对象进行分类

        Args:
            owner: 条令所属对象

        Returns:
            str: 'Side','Mission'或'Others'
        """
        if isinstance(owner, CSide):
            return "Side"
        elif isinstance(owner, MissionTypes):
            return "Mission"
        elif not isinstance(owner, CResponse):
            return "Others"
        raise ValueError(f"无法对条令所有者进行分类: {owner}")

    def _build_doctrine_command(self, command_params: dict) -> str:
        """
        构建通用的条令命令字符串

        Args:
            command_params: 命令参数字典

        Returns:
            str: 构建好的命令字符串
        """
        owner = self.get_doctrine_owner()

        if isinstance(owner, CSide):
            base_cmd = f"{{side ='{owner.guid}'}}"
        elif isinstance(owner, MissionTypes):
            base_cmd = f"{{side ='{owner.side}', mission ='{owner.guid}'}}"
        elif not isinstance(owner, CResponse):
            base_cmd = f"{{guid ='{owner.guid}'}}"
        else:
            raise ValueError(f"无效的所有者类型: {type(owner)}")

        params_str = ", ".join(
            f"{k} = {str(v).lower()}" if isinstance(v, bool) else f"{k} = '{v}'" for k, v in command_params.items()
        )
        return f"ScenEdit_SetDoctrine({base_cmd}, {{{params_str}}})"

    async def _execute_doctrine_command(self, command: str) -> bool:
        """
        执行条令命令

        Args:
            command: 要执行的命令字符串

        Returns:
            bool: 命令执行结果
        """
        self.mozi_server.throw_into_pool(command)
        response = await self.mozi_server.send_and_recv(command)
        return response.lua_success

    async def use_nuclear_weapons(self, use: bool) -> bool:
        """
        设置是否使用核武器

        Args:
            use: 是否使用核武器

        Returns:
            bool: 命令执行结果
        """
        cmd = self._build_doctrine_command({"use_nuclear_weapons": use})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def set_weapon_control_status(
        self,
        domain: Literal[
            "weapon_control_status_subsurface",
            "weapon_control_status_surface",
            "weapon_control_status_land",
            "weapon_control_status_air",
        ],
        fire_status: Literal[0, 1, 2],
    ) -> bool:
        """
        设置武器控制状态

        Args:
            domain: 武器控制状态的域
            fire_status: 开火状态(0:自由开火,1:谨慎开火,2:限制开火)

        Returns:
            bool: 命令执行结果
        """
        cmd = self._build_doctrine_command({domain: fire_status})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def set_weapon_control_status_subsurface(self, fire_status: Literal[0, 1, 2]) -> bool:
        """
        设置对潜武器控制状态

        Args:
            fire_status: 开火状态(0:自由开火,1:谨慎开火,2:限制开火)

        Returns:
            bool: 执行结果
        """
        return await self.set_weapon_control_status("weapon_control_status_subsurface", fire_status)

    @validate_literal_args
    async def set_weapon_control_status_surface(self, fire_status: Literal[0, 1, 2]) -> bool:
        """
        设置对海武器控制状态

        Args:
            fire_status: 开火状态(0:自由开火,1:谨慎开火,2:限制开火)

        Returns:
            bool: 执行结果
        """
        return await self.set_weapon_control_status("weapon_control_status_surface", fire_status)

    @validate_literal_args
    async def set_weapon_control_status_land(self, fire_status: Literal[0, 1, 2]) -> bool:
        """
        设置对地武器控制状态

        Args:
            fire_status: 开火状态(0:自由开火,1:谨慎开火,2:限制开火)

        Returns:
            bool: 执行结果
        """
        return await self.set_weapon_control_status("weapon_control_status_land", fire_status)

    @validate_literal_args
    async def set_weapon_control_status_air(self, fire_status: Literal[0, 1, 2]) -> bool:
        """
        设置对空武器控制状态

        Args:
            fire_status: 开火状态(0:自由开火,1:谨慎开火,2:限制开火)

        Returns:
            bool: 执行结果
        """
        return await self.set_weapon_control_status("weapon_control_status_air", fire_status)

    async def ignore_plotted_course(self, ignore: bool) -> bool:
        """
        设置是否忽略计划航线

        Args:
            ignore: 是否忽略

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"ignore_plotted_course": ignore})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def set_ambiguous_targets_engaging_status(
        self, status: Literal["Ignore", "Optimistic", "Pessimistic"]
    ) -> bool:
        """
        设置与模糊位置目标的交战状态

        Args:
            status: 交战状态
                Ignore: 忽略模糊性
                Optimistic: 乐观决策
                Pessimistic: 悲观决策

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"engaging_ambiguous_targets": status})
        return await self._execute_doctrine_command(cmd)

    async def set_opportunity_targets_engaging_status(self, engage: bool) -> bool:
        """
        设置与临机目标的交战状态

        Args:
            engage: 是否可与任何目标交战
                True: 可与任何目标交战
                False: 只与任务相关目标交战

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"engage_opportunity_targets": engage})
        return await self._execute_doctrine_command(cmd)

    async def ignore_emcon_while_under_attack(self, ignore: bool) -> bool:
        """
        设置受到攻击时是否忽略电磁管控

        Args:
            ignore: 是否忽略电磁管控
                True: 忽略电磁管控
                False: 不忽略电磁管控

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"ignore_emcon_while_under_attack": ignore})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def use_kinematic_range_for_torpedoes(self, usage_mode: Literal[0, 1, 2]) -> bool:
        """
        设置如何使用鱼雷的动力航程

        Args:
            usage_mode: 鱼雷动力航程使用方式
                0: 手动自动开火下都使用 (AutomaticAndManualFire)
                1: 仅手动开火下使用 (ManualFireOnly)
                2: 不使用 (No)

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"kinematic_range_for_torpedoes": usage_mode})
        return await self._execute_doctrine_command(cmd)

    async def evade_automatically(self, evade: bool) -> bool:
        """
        设置是否自动规避

        Args:
            evade: 是否自动规避
                True: 自动规避
                False: 不自动规避

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"automatic_evasion": evade})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def use_refuel_supply(self, policy: Literal[0, 1, 2]) -> bool:
        """
        设置是否允许加油补给

        Args:
            policy: 加油补给设置
                0: 允许但禁止加油机相互加油
                1: 不允许
                2: 允许

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"use_refuel_unrep": policy})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def select_refuel_supply_object(self, policy: Literal[0, 1, 2]) -> bool:
        """
        设置加油补给的选择对象

        Args:
            policy: 选择对象策略
                0: 选择最近的加油机
                1: 选择敌我之间的加油机
                2: 优先选择敌我之间的加油机并禁止回飞

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"refuel_unrep_selection": policy})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def refuel_supply_allies(self, policy: Literal[0, 1, 2, 3]) -> bool:
        """
        设置是否给盟军单元加油补给

        Args:
            policy: 补给策略
                0: 是
                1: 是且仅接受
                2: 是且仅供给
                3: 否

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"refuel_unrep_allied": policy})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def set_air_operations_tempo(self, tempo: Literal["Surge", "Sustained"]) -> bool:
        """
        设置空战节奏

        Args:
            tempo: 空战节奏
                Surge: 快速出动 (0)
                Sustained: 一般强度出动 (1)

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"air_operations_tempo": tempo})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def quick_turnaround_for_aircraft(self, mode: Literal["Yes", "FightersAndASW", "No"]) -> bool:
        """
        设置是否快速出动飞机

        Args:
            mode: 快速出动设置
                Yes: 是
                FightersAndASW: 仅战斗机和反潜机快速出动
                No: 否

        Returns:
            bool: 执行结果

        已知问题:
            设置为1(FightersAndASW)时可能会执行出错
        """
        cmd = self._build_doctrine_command({"quick_turnaround_for_aircraft": mode})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def set_fuel_state_for_aircraft(
        self,
        fuel_state: Literal[
            "Bingo",
            "Joker10Percent",
            "Joker20Percent",
            "Joker25Percent",
            "Joker30Percent",
            "Joker40Percent",
            "Joker50Percent",
            "Joker60Percent",
            "Joker70Percent",
            "Joker75Percent",
            "Joker80Percent",
            "Joker90Percent",
        ],
    ) -> bool:
        """
        设置单架飞机返航的油料状态

        Args:
            fuel_state: 油料状态设置
                Bingo: 剩下计划储备油量时即终止任务返航
                Joker10Percent: 剩下1.1倍计划储备油量时即终止任务返航
                Joker20Percent: 剩下1.2倍计划储备油量时即终止任务返航
                Joker25Percent: 剩下1.25倍计划储备油量时即终止任务返航
                Joker30Percent: 剩下1.3倍计划储备油量时即终止任务返航
                Joker40Percent: 剩下1.4倍计划储备油量时即终止任务返航
                Joker50Percent: 剩下1.5倍计划储备油量时即终止任务返航
                Joker60Percent: 剩下1.6倍计划储备油量时即终止任务返航
                Joker70Percent: 剩下1.7倍计划储备油量时即终止任务返航
                Joker75Percent: 剩下1.75倍计划储备油量时即终止任务返航
                Joker80Percent: 剩下1.8倍计划储备油量时即终止任务返航
                Joker90Percent: 剩下1.9倍计划储备油量时即终止任务返航

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"fuel_state_planned": fuel_state})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def set_fuel_state_for_air_group(
        self,
        fuel_state: Literal[
            "No",
            "YesLastUnit",
            "YesFirstUnit",
            "YesLeaveGroup",
        ],
    ) -> bool:
        """
        设置飞行编队返航的油料状态

        Args:
            fuel_state: 编队返航状态设置
                No - 无约束，编队不返航
                YesLastUnit - 编队中所有飞机均因达到单机油料状态要返航时，编队才返航
                YesFirstUnit - 编队中任意一架飞机达到单机油料状态要返航时，编队就返航
                YesLeaveGroup - 编队中任意一架飞机达到单机油料状态要返航时，其可离队返航

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"fuel_state_rtb": fuel_state})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def set_weapon_state_for_aircraft(
        self,
        weapon_state: Literal[
            0,  # 使用挂载设置
            2001,  # 任务武器已耗光，立即脱离战斗
            2002,  # 任务武器已耗光，允许使用航炮对临机目标进行打击（推荐）
            3001,  # 所有超视距与防区外打击武器已耗光，立即脱离战斗
            3002,  # 所有超视距与防区外打击武器已耗光，允许使用视距内或防区内打击武器对较易攻击的临机目标进行攻击，不使用航炮
            3003,  # 所有超视距与防区外打击武器已耗光，允许使用视距内、防区内打击武器或航炮对较易攻击的临机目标进行攻击
            5001,  # 使用超视距或防区外打击武器进行一次交战，立即脱离战斗
            5002,  # 使用超视距或防区外打击武器进行一次交战，允许使用视距内或防区内打击武器对较易攻击的临机目标进行攻击，不使用航炮
            5003,  # 使用超视距或防区外打击武器进行一次交战，允许使用视距内、防区内打击武器或航炮对较易攻击的临机目标进行攻击
            5005,  # 同时使用超视距/视距内或防区外/防区内打击武器进行一次交战，不使用航炮
            5006,  # 同时使用超视距/视距内或防区外/防区内打击武器进行一次交战，允许使用航炮对较易攻击的临机目标进行攻击
            5011,  # 使用视距内或防区内打击武器进行一次交战，立即脱离战斗
            5012,  # 使用视距内或防区内打击武器进行一次交战，允许使用航炮与临机目标格斗
            5021,  # 使用航炮进行一次交战
            4001,  # 25%相关武器已耗光，立即脱离战斗
            4002,  # 25%相关武器已耗光，允许与临机目标交战，包括航炮
            4011,  # 50%相关武器已耗光，立即脱离战斗
            4012,  # 50%相关武器已耗光，允许与临机目标交战，包括航炮
            4021,  # 75%相关武器已耗光，立即脱离战斗
            4022,  # 75%相关武器已耗光，允许与临机目标交战，包括航炮
        ],
    ) -> bool:
        """
        设置单架飞机的武器状态

        Args:
            weapon_state: 武器状态设置
                0: 使用挂载设置
                2001: 任务武器已耗光，立即脱离战斗
                2002: 任务武器已耗光，允许使用航炮对临机目标进行打击（推荐）
                3001: 所有超视距与防区外打击武器已耗光，立即脱离战斗
                3002: 所有超视距与防区外打击武器已耗光，允许使用视距内或防区内打击武器对较易攻击的临机目标进行攻击，不使用航炮
                3003: 所有超视距与防区外打击武器已耗光，允许使用视距内、防区内打击武器或航炮对较易攻击的临机目标进行攻击
                5001: 使用超视距或防区外打击武器进行一次交战，立即脱离战斗
                5002: 使用超视距或防区外打击武器进行一次交战，允许使用视距内或防区内打击武器对较易攻击的临机目标进行攻击，不使用航炮
                5003: 使用超视距或防区外打击武器进行一次交战，允许使用视距内、防区内打击武器或航炮对较易攻击的临机目标进行攻击
                5005: 同时使用超视距/视距内或防区外/防区内打击武器进行一次交战，不使用航炮
                5006: 同时使用超视距/视距内或防区外/防区内打击武器进行一次交战，允许使用航炮对较易攻击的临机目标进行攻击
                5011: 使用视距内或防区内打击武器进行一次交战，立即脱离战斗
                5012: 使用视距内或防区内打击武器进行一次交战，允许使用航炮与临机目标格斗
                5021: 使用航炮进行一次交战
                4001: 25%相关武器已耗光，立即脱离战斗
                4002: 25%相关武器已耗光，允许与临机目标交战，包括航炮
                4011: 50%相关武器已耗光，立即脱离战斗
                4012: 50%相关武器已耗光，允许与临机目标交战，包括航炮
                4021: 75%相关武器已耗光，立即脱离战斗
                4022: 75%相关武器已耗光，允许与临机目标交战，包括航炮

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"weapon_state_planned": weapon_state})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def set_weapon_state_for_air_group(
        self,
        weapon_state: Literal[
            "No",
            "YesLastUnit",
            "YesFirstUnit",
            "YesLeaveGroup",
        ],
    ) -> bool:
        """
        设置飞行编队的武器状态

        Args:
            weapon_state: 编队返航状态设置
                No - 无约束，编队不返航
                YesLastUnit - 编队中所有飞机均因达到单机武器状态要返航时，编队才返航
                YesFirstUnit - 编队中任意一架飞机达到单机武器状态要返航时，编队就返航
                YesLeaveGroup - 编队中任意一架飞机达到单机武器状态要返航时，其可离队返航

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"weapon_state_rtb": weapon_state})
        return await self._execute_doctrine_command(cmd)

    async def gun_strafe_for_aircraft(self, allow: bool) -> bool:
        """
        设置是否允许航炮扫射

        Args:
            allow: 航炮扫射设置
                True - 允许航炮扫射
                False - 不允许航炮扫射

        Returns:
            bool: 执行结果
        """
        allow_str = "Yes" if allow else "No"
        cmd = self._build_doctrine_command({"gun_strafing": allow_str})
        return await self._execute_doctrine_command(cmd)

    async def jettison_ordnance_for_aircraft(self, allow: bool) -> bool:
        """
        设置是否允许抛弃弹药

        Args:
            allow: 抛弃弹药设置
                True - 允许抛弃弹药
                False - 不允许抛弃弹药

        Returns:
            bool: 执行结果
        """
        decision = "Yes" if allow else "No"
        cmd = self._build_doctrine_command({"jettison_ordnance": decision})
        return await self._execute_doctrine_command(cmd)

    async def use_sams_to_anti_surface(self, allow: bool) -> bool:
        """
        设置是否以反舰模式使用舰空导弹

        Args:
            allow: 是否允许以反舰模式使用舰空导弹
                True: 允许以反舰模式使用舰空导弹
                False: 不允许以反舰模式使用舰空导弹

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"use_sams_in_anti_surface_mode": allow})
        return await self._execute_doctrine_command(cmd)

    async def maintain_standoff(self, keep_distance: bool) -> bool:
        """
        设置是否与目标保持距离

        Args:
            keep_distance: 是否与目标保持距离
                True: 与目标保持距离
                False: 不与目标保持距离

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"maintain_standoff": keep_distance})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def avoid_being_searched_for_submarine(
        self, decision: Literal["No", "Yes_ExceptSelfDefence", "Yes_Always"]
    ) -> bool:
        """
        设置是否规避搜索

        Args:
            decision: 规避搜索设置
                No - 否
                Yes_ExceptSelfDefence - 除非自卫均是
                Yes_Always - 总是

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"avoid_contact": decision})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def dive_on_threat(
        self, decision: Literal["Yes", "Yes_ESM_Only", "Yes_Ships20nm_Aircraft30nm", "No"]
    ) -> bool:
        """
        设置探测到威胁时是否下潜

        Args:
            decision: 下潜策略
                Yes - 在敌潜望镜或对面搜索雷达侦察时下潜
                Yes_ESM_Only - 在敌电子侦察措施侦察或目标接近时下潜
                Yes_Ships20nm_Aircraft30nm - 在20海里内有敌舰或30海里内有敌机时下潜
                No - 否

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"dive_on_threat": decision})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def set_recharging_condition_on_patrol(
        self,
        recharging_condition: Literal[
            "Recharge_Empty",  # 电量用完再充
            "Recharge_10_Percent",  # 电量剩下10%时再充
            "Recharge_20_Percent",  # 电量剩下20%时再充
            "Recharge_30_Percent",  # 电量剩下30%时再充
            "Recharge_40_Percent",  # 电量剩下40%时再充
            "Recharge_50_Percent",  # 电量剩下50%时再充
            "Recharge_60_Percent",  # 电量剩下60%时再充
            "Recharge_70_Percent",  # 电量剩下70%时再充
            "Recharge_80_Percent",  # 电量剩下80%时再充
            "Recharge_90_Percent",  # 电量剩下90%时再充
        ],
    ) -> bool:
        """
        设置出航或阵位再充电条件

        Args:
            recharging_condition: 充电条件设置
                Recharge_Empty: 电量用完再充
                Recharge_10_Percent: 电量剩下10%时再充
                Recharge_20_Percent: 电量剩下20%时再充
                Recharge_30_Percent: 电量剩下30%时再充
                Recharge_40_Percent: 电量剩下40%时再充
                Recharge_50_Percent: 电量剩下50%时再充
                Recharge_60_Percent: 电量剩下60%时再充
                Recharge_70_Percent: 电量剩下70%时再充
                Recharge_80_Percent: 电量剩下80%时再充
                Recharge_90_Percent: 电量剩下90%时再充

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"recharge_on_patrol": recharging_condition})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def set_recharging_condition_on_attack(
        self,
        recharging_condition: Literal[
            "Recharge_Empty",  # 电量用完再充
            "Recharge_10_Percent",  # 电量剩下10%时再充
            "Recharge_20_Percent",  # 电量剩下20%时再充
            "Recharge_30_Percent",  # 电量剩下30%时再充
            "Recharge_40_Percent",  # 电量剩下40%时再充
            "Recharge_50_Percent",  # 电量剩下50%时再充
            "Recharge_60_Percent",  # 电量剩下60%时再充
            "Recharge_70_Percent",  # 电量剩下70%时再充
            "Recharge_80_Percent",  # 电量剩下80%时再充
            "Recharge_90_Percent",  # 电量剩下90%时再充
        ],
    ) -> bool:
        """
        设置进攻或防御再充电条件

        Args:
            recharging_condition: 充电条件设置
                Recharge_Empty: 电量用完再充
                Recharge_10_Percent: 电量剩下10%时再充
                Recharge_20_Percent: 电量剩下20%时再充
                Recharge_30_Percent: 电量剩下30%时再充
                Recharge_40_Percent: 电量剩下40%时再充
                Recharge_50_Percent: 电量剩下50%时再充
                Recharge_60_Percent: 电量剩下60%时再充
                Recharge_70_Percent: 电量剩下70%时再充
                Recharge_80_Percent: 电量剩下80%时再充
                Recharge_90_Percent: 电量剩下90%时再充

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"recharge_on_attack": recharging_condition})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def use_aip(
        self,
        decision: Literal[
            "No",  # 否
            "Yes_AttackOnly",  # 在进攻或防御时使用
            "Yes_Always",  # 总是
        ],
    ) -> bool:
        """
        设置是否使用"不依赖空气推进"系统

        Args:
            decision: 使用策略
                No: 不使用
                Yes_AttackOnly: 仅在进攻或防御时使用
                Yes_Always: 始终使用

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"use_aip": decision})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def use_dipping_sonar(
        self,
        decision: Literal[
            "Automatically_HoverAnd150ft",  # 自动到150英尺悬停并使用
            "ManualAndMissionOnly",  # 只能人工使用或者分配到任务
        ],
    ) -> bool:
        """
        设置是否使用吊放声呐

        Args:
            decision: 使用策略
                Automatically_HoverAnd150ft: 自动到150英尺悬停并使用
                ManualAndMissionOnly: 只能人工使用或者分配到任务

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"dipping_sonar": decision})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def set_em_control_status(
        self, em_item: Literal["Radar", "Sonar", "OECM"], status: Literal["Passive", "Active"]
    ) -> bool:
        """
        设置电磁管控状态

        Args:
            em_item:
                'Radar'-雷达
                'Sonar'-声呐
                'OECM'-光电对抗
            status:
                'Passive'-仅有被动设备工作
                'Active'-另有主动设备工作

        Returns:
            bool: 执行结果
        """
        owner = self.get_doctrine_owner()
        if isinstance(owner, CSide):
            cmd = f"ScenEdit_SetEMCON('Side','{owner.guid}','{em_item}={status}')"
        elif isinstance(owner, MissionTypes):
            cmd = f"ScenEdit_SetEMCON('Mission','{owner.guid}','{em_item}={status}')"
        elif isinstance(owner, CGroup):
            cmd = f"ScenEdit_SetEMCON('Group','{owner.guid}','{em_item}={status}')"
        elif not isinstance(owner, CResponse):
            cmd = f"ScenEdit_SetEMCON('Unit','{owner.guid}','{em_item}={status}')"
        else:
            raise ValueError(f"Invalid owner type: {type(owner)}")
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_weapon_release_authority(
        self,
        weapon_db_id: int,
        target_type: int,
        quantity_salvo: int = 2,
        shooter_salvo: int = 1,
        firing_range: str = "none",
        self_defense: str = "max",
        escort: bool = False,
    ) -> bool:
        """
        设置条令的武器使用规则

        Args:
            weapon_dbid: 武器的数据库ID
            target_type: 目标类型号,具体映射关系参照args.py中的WRA_WeaponTargetType
            quantity_salvo: 齐射武器数('n'/inherit/max/none)
            shooter_salvo: 齐射发射架数('n'/inherit/max)
            firing_range: 自动开火距离('n'/inherit/max/none)
            self_defense: 自动防御距离('n'/inherit/max/none)
            escort: 是否护航任务(true/false)
            注：n为数字,若不匹配则取最近值

        Returns:
            bool: 执行结果
        """
        owner = self.get_doctrine_owner()
        escort_str = str(escort).lower()
        if isinstance(owner, CSide):
            cmd = f"Hs_SetDoctrineWRA({{side='{owner.guid}', WEAPON_ID='{weapon_db_id}', target_type='{target_type}', escort='{escort_str}'}},{{qty_salvo='{quantity_salvo}',shooter_salvo='{shooter_salvo}',firing_range='{firing_range}',self_defence='{self_defense}'}})"
        elif isinstance(owner, MissionTypes):
            cmd = f"Hs_SetDoctrineWRA({{side='{owner.side}', mission='{owner.guid}', WEAPON_ID='{weapon_db_id}', target_type='{target_type}', escort='{escort_str}'}},{{qty_salvo='{quantity_salvo}',shooter_salvo='{shooter_salvo}',firing_range='{firing_range}',self_defence='{self_defense}'}})"
        elif not isinstance(owner, CResponse):
            cmd = f"Hs_SetDoctrineWRA({{guid='{owner.guid}', WEAPON_ID='{weapon_db_id}', target_type='{target_type}', escort='{escort_str}'}},{{qty_salvo='{quantity_salvo}',shooter_salvo='{shooter_salvo}',firing_range='{firing_range}',self_defence='{self_defense}'}})"
        else:
            raise ValueError(f"无效的所有者类型: {type(owner)}")

        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    @validate_literal_args
    async def withdraw_on_damage(
        self,
        damage_degree: Literal[
            "Ignore",  # 忽略毁伤不撤退
            "Percent5",  # 毁伤大于5%撤退
            "Percent25",  # 毁伤大于25%撤退
            "Percent50",  # 毁伤大于50%撤退
            "Percent75",  # 毁伤大于75%撤退
        ],
    ) -> bool:
        """
        设置导致撤退的毁伤程度

        Args:
            damage_degree: 毁伤程度设置
                Ignore: 忽略毁伤不撤退
                Percent5: 毁伤大于5%撤退
                Percent25: 毁伤大于25%撤退
                Percent50: 毁伤大于50%撤退
                Percent75: 毁伤大于75%撤退

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"withdraw_on_damage": damage_degree})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def withdraw_on_fuel(
        self,
        fuel_quantity: Literal[
            "Ignore",  # 忽略油量不撤退
            "Bingo",  # 少于计划储备油量时撤退
            "Percent25",  # 少于25%时撤退
            "Percent50",  # 少于50%时撤退
            "Percent75",  # 少于75%时撤退
        ],
    ) -> bool:
        """
        设置导致撤退的油量阈值

        Args:
            fuel_quantity: 油量阈值设置
                Ignore: 忽略油量不撤退
                Bingo: 少于计划储备油量时撤退
                Percent25: 少于25%时撤退
                Percent50: 少于50%时撤退
                Percent75: 少于75%时撤退

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"withdraw_on_fuel": fuel_quantity})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def withdraw_on_attack_weapon(
        self,
        weapon_quantity: Literal[
            "Ignore",  # 忽略武器量不撤退
            "Exhausted",  # 打光才撤
            "Percent25",  # 主攻武器量消耗到25%时撤退
            "Percent50",  # 主攻武器量消耗到50%时撤退
            "Percent75",  # 主攻武器量消耗到75%时撤退
        ],
    ) -> bool:
        """
        设置导致撤退的主攻武器量阈值

        Args:
            weapon_quantity: 主攻武器量阈值设置
                Ignore: 忽略武器量不撤退
                Exhausted: 打光才撤
                Percent25: 主攻武器量消耗到25%时撤退
                Percent50: 主攻武器量消耗到50%时撤退
                Percent75: 主攻武器量消耗到75%时撤退

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"withdraw_on_attack": weapon_quantity})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def withdraw_on_defence_weapon(
        self,
        weapon_quantity: Literal[
            "Ignore",  # 忽略武器量不撤退
            "Exhausted",  # 打光才撤
            "Percent25",  # 主防武器量消耗到25%时撤退
            "Percent50",  # 主防武器量消耗到50%时撤退
            "Percent75",  # 主防武器量消耗到75%时撤退
        ],
    ) -> bool:
        """
        设置导致撤退的主防武器量阈值

        Args:
            weapon_quantity: 主防武器量阈值设置
                Ignore: 忽略武器量不撤退
                Exhausted: 打光才撤
                Percent25: 主防武器量消耗到25%时撤退
                Percent50: 主防武器量消耗到50%时撤退
                Percent75: 主防武器量消耗到75%时撤退

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"withdraw_on_defence": weapon_quantity})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def redeploy_on_damage(
        self,
        damage_degree: Literal[
            "Ignore",  # 忽略毁伤重新部署
            "Percent5",  # 毁伤小于5%重新部署
            "Percent25",  # 毁伤小于25%重新部署
            "Percent50",  # 毁伤小于50%重新部署
            "Percent75",  # 毁伤小于75%重新部署
        ],
    ) -> bool:
        """
        设置导致重新部署的毁伤程度阈值

        Args:
            damage_degree: 毁伤程度阈值设置
                Ignore: 忽略毁伤重新部署
                Percent5: 毁伤小于5%重新部署
                Percent25: 毁伤小于25%重新部署
                Percent50: 毁伤小于50%重新部署
                Percent75: 毁伤小于75%重新部署

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"deploy_on_damage": damage_degree})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def redeploy_on_fuel(
        self,
        fuel_quantity: Literal[
            "Ignore",  # 忽略油量重新部署
            "Bingo",  # 至少为计划储备油量时重新部署
            "Percent25",  # 至少为25%时重新部署
            "Percent50",  # 至少为50%时重新部署
            "Percent75",  # 至少为75%时重新部署
            "Percent100",  # 必须满油才能重新部署
        ],
    ) -> bool:
        """
        设置导致重新部署的油量阈值

        Args:
            fuel_quantity: 油量阈值设置
                Ignore: 忽略油量重新部署
                Bingo: 至少为计划储备油量时重新部署
                Percent25: 至少为25%时重新部署
                Percent50: 至少为50%时重新部署
                Percent75: 至少为75%时重新部署
                Percent100: 必须满油才能重新部署

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"deploy_on_fuel": fuel_quantity})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def redeploy_on_attack_weapon(
        self,
        weapon_quantity: Literal[
            "Ignore",  # 忽略武器量重新部署
            "Exhausted",  # 耗光也要重新部署
            "Percent25",  # 主攻武器量处于25%时重新部署
            "Percent50",  # 主攻武器量处于50%时重新部署
            "Percent75",  # 主攻武器量处于75%时重新部署
            "Percent100",  # 主攻武器满载才能重新部署
            "LoadFullWeapons",  # 所有武器挂满才能重新部署
        ],
    ) -> bool:
        """
        设置导致重新部署的主攻武器量阈值

        Args:
            weapon_quantity: 主攻武器量阈值设置
                Ignore: 忽略武器量重新部署
                Exhausted: 耗光也要重新部署
                Percent25: 主攻武器量处于25%时重新部署
                Percent50: 主攻武器量处于50%时重新部署
                Percent75: 主攻武器量处于75%时重新部署
                Percent100: 主攻武器满载才能重新部署
                LoadFullWeapons: 所有武器挂满才能重新部署

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"deploy_on_attack": weapon_quantity})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def redeploy_on_defence_weapon(
        self,
        weapon_quantity: Literal[
            "Ignore",  # 忽略武器量重新部署
            "Exhausted",  # 耗光也要重新部署
            "Percent25",  # 主防武器量处于25%时重新部署
            "Percent50",  # 主防武器量处于50%时重新部署
            "Percent75",  # 主防武器量处于75%时重新部署
            "Percent100",  # 主防武器满载才能重新部署
            "LoadFullWeapons",  # 所有武器挂满才能重新部署
        ],
    ) -> bool:
        """
        设置导致重新部署的主防武器量阈值

        Args:
            weapon_quantity: 主防武器量阈值设置
                Ignore: 忽略武器量重新部署
                Exhausted: 耗光也要重新部署
                Percent25: 主防武器量处于25%时重新部署
                Percent50: 主防武器量处于50%时重新部署
                Percent75: 主防武器量处于75%时重新部署
                Percent100: 主防武器满载才能重新部署
                LoadFullWeapons: 所有武器挂满才能重新部署

        Returns:
            bool: 执行结果
        """
        cmd = self._build_doctrine_command({"deploy_on_defence": weapon_quantity})
        return await self._execute_doctrine_command(cmd)

    @validate_literal_args
    async def reset(
        self,
        level: Literal["Left", "Middle", "Right"],
        aspect: Literal["Ensemble", "EMCON", "Weapon"],
        escort_status: bool = False,
    ) -> bool:
        """
        重置作战条令

        Args:
            level:
                Left-重置本级作战条令
                Middle-重置关联单元的作战条令
                Right-重置关联任务的作战条令
            aspect:
                Ensemble-总体条令
                EMCON-电磁管控条令
                Weapon-武器使用规则
            escort_status:
                True-针对护航任务
                False-非护航任务

        Returns:
            bool: 执行结果
        """
        owner = self.get_doctrine_owner()
        owner_type = self._classify_owner(owner)
        escort_status_str = str(escort_status).lower()
        if owner_type == "Side" and level == "Left":
            raise ValueError("推演方没有上级，无法继承条令设置。")
        if owner_type == "Group" and level == "Right":
            raise ValueError("编队之下没有受其影响的任务，无法向其传递条令。")
        if owner_type == "Others" and level != "Left":
            raise ValueError("单元之下没有受其影响的任务或单元，无法向下传递条令。")
        if isinstance(owner, CResponse):
            raise ValueError("CResponse 无法重置条令。")
        cmd = f"Hs_ResetDoctrine('{owner.guid}', '{level}', '{aspect}', {escort_status_str})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def set_emcon_according_to_superiors(self, follow_superiors: bool, escort: bool = False) -> bool:
        """
        设置单元电磁管控与上级一致.

        Args:
            - follow_superiors (bool): 是否与上级一致
                - True-与上级一致
                - False-与上级不一致
            - escort (bool): 是否为护航任务
                True-为护航电磁管控
                False-非护航电磁管控

        Returns:
            bool: 执行结果
        """
        owner = self.get_doctrine_owner()
        owner_type = self._classify_owner(owner)
        escort_status_str = str(escort).lower()
        if owner_type in ["Side", "Mission", "Group"] or isinstance(owner, CResponse):
            return False
        else:
            follow_superiors_str = "yes" if follow_superiors else "no"
            cmd = f"Hs_SetInLineWithSuperiors('{owner.guid}', '{follow_superiors_str}', {escort_status_str})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success

    async def unit_obeys_emcon(self, obey: bool) -> bool:
        """
        设置单元是否遵循电磁管控

        Args:
            obey:
                True-遵循电磁管控
                False-不遵循电磁管控

        Returns:
            bool: 执行结果
        """
        owner = self.get_doctrine_owner()
        owner_type = self._classify_owner(owner)
        if owner_type in ["Side", "Mission", "Group"] or isinstance(owner, CResponse):
            return False
        else:
            cmd = f"Hs_UnitObeysEMCON('{owner.guid}', {str(obey).lower()})"
        self.mozi_server.throw_into_pool(cmd)
        response = await self.mozi_server.send_and_recv(cmd)
        return response.lua_success
