from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import MoziServer
    from .situation import CSituation
    from .trigger import CTrigger
    from .condition import CCondition
    from .action import CAction
    from .server import ServerResponse

from .base import Base
from .situ_interpret import CSimEventDict


class CSimEvent(Base):
    """
    事件类
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        # 描述文本
        self.description = ""
        # 是否重复使用
        self.repeatable = False
        # 是否激活
        self.active = False
        # 是否在消息中显示
        self.message_shown = False
        # 发生概率
        self.probability = 0
        # 所属触发器
        self.triggers = {}
        # 所属条件
        self.conditions = {}
        # 所属动作
        self.actions = {}

        self.var_map = CSimEventDict.var_map

    def get_triggers(self) -> dict[str, "CTrigger"]:
        """
        获取所有触发器

        Returns:
            dict[str, CTrigger]: 所有触发器
        """
        triggers = {}
        triggers.update(self.situation.trigger_unit_detected_dict)
        triggers.update(self.situation.trigger_unit_damaged_dict)
        triggers.update(self.situation.trigger_unit_destroyed_dict)
        triggers.update(self.situation.trigger_points_dict)
        triggers.update(self.situation.trigger_time_dict)
        triggers.update(self.situation.trigger_regular_time_dict)
        triggers.update(self.situation.trigger_random_time_dict)
        triggers.update(self.situation.trigger_scen_loaded_dict)
        triggers.update(self.situation.trigger_unit_remains_in_area_dict)
        return triggers

    def get_conditions(self) -> dict[str, "CCondition"]:
        """
        获取所有条件

        Returns:
            dict[str, CCondition]: 所有条件
        """
        conditions = {}
        conditions.update(self.situation.condition_scen_has_started_dict)
        conditions.update(self.situation.condition_side_posture_dict)
        conditions.update(self.situation.condition_lua_script_dict)
        return conditions

    def get_actions(self) -> dict[str, "CAction"]:
        """
        获取所有动作

        Returns:
            dict[str, CAction]: 所有动作
        """
        actions = {}
        actions.update(self.situation.action_message_dict)
        actions.update(self.situation.action_points_dict)
        actions.update(self.situation.action_teleport_in_area_dict)
        actions.update(self.situation.action_change_mission_status_dict)
        actions.update(self.situation.action_end_scenario_dict)
        actions.update(self.situation.action_lua_script_dict)
        return actions

    async def execute_action(self) -> "ServerResponse":
        """
        执行某个 lua 类型的动作，会将动作中的 lua 脚本运行一次，可以查验动作中 lua 脚本效果

        Returns:
            ServerResponse: 服务器响应
        """
        return await self.mozi_server.send_and_recv(f"ScenEdit_ExecuteEventAction ('{self.guid}')")

    async def update_setting(
        self, new_name: str, description: str, active: bool, show: bool, repeatable: bool, prob: float
    ) -> bool:
        """
        更新事件的属性

        Args:
            - new_name:新事件名称
            - description:事件说明
            - active:是否启用
            - show:是否显示
            - repeatable:是否可重复
            - prob:发生概率

        Returns:
            bool: 执行结果
        """
        lua_scrpt = f"ScenEdit_UpdateEvent('{self.guid}',{{'{new_name}', '{description}',{str(active).lower()},{str(show).lower()},{str(repeatable).lower()},{prob}}})"
        response = await self.mozi_server.send_and_recv(lua_scrpt)
        return response.lua_success
