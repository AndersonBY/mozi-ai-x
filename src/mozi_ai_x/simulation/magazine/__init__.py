from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from ..base import Base
from ..situ_interpret import CMagazineDict
from mozi_ai_x.utils.validator import validate_literal_args, validate_uuid4_args


class CMagazine(Base):
    """弹药库"""

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 弹药库名称
        self.name = ""
        # 父平台guid
        self.parent_platform = ""
        # 状态
        self.component_status = 0
        # 毁伤程度的轻,中,重
        self.damage_severity = 0
        # 覆盖角度
        self.coverage_arc = ""
        # 挂架已挂载的数量和挂架载荷
        self.load_ratio = ""
        self.select = False  # 选择是否查找所属单元

        self.var_map = CMagazineDict.var_map

    @validate_literal_args
    async def set_magazine_state(self, state: Literal["正常运转", "轻度毁伤", "中度毁伤", "重度毁伤", "摧毁"]) -> bool:
        """
        设置弹药库状态
        限制：专项赛禁用

        Args:
            state(str): '正常运转'，'轻度毁伤'，'中度毁伤'，'重度毁伤' 或 '摧毁'

        Returns:
            bool
        """
        lua_script = (
            f"Hs_ScenEdit_SetMagazineState({{guid='{self.parent_platform}', magazine_guid='{self.guid}',state='{state}'}})"
        )
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success

    @validate_uuid4_args(["weapon_guid"])
    async def remove_weapon(self, weapon_guid: str) -> bool:
        """
        删除单元中指定弹药库下的指定武器
        限制：专项赛禁用

        Args:
            weapon_guid(str): 武器guid

        Returns:
            bool
        """
        lua_script = f"Hs_ScenEdit_RemoveMagazineWeapon({{GUID='{self.parent_platform}',WPNREC_GUID='{weapon_guid}'}})"
        response = await self.mozi_server.send_and_recv(lua_script)
        return response.lua_success
