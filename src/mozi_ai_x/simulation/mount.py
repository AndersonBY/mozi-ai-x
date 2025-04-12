from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import MoziServer
    from .situation import CSituation

from .base import Base
from .situ_interpret import CMountDict


class CMount(Base):
    """挂载"""

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        # 名称
        self.name = ""
        # 所属单元GUID
        self.parent_platform = ""
        # 部件状态
        self.component_status = 0
        # 毁伤程度的轻,中,重
        self.damage_severity = 0
        # 挂载方位
        self.coverage_arc = ""
        # 挂载的武器开火状态
        self.weapon_fire_state = ""
        # 挂载的武器的数量
        self.load_weapon_count = ""
        # 获取挂架下武器的最大载弹量和当前载弹量集合
        self.load_ratio = ""  # 5a8226e3-a454-4a61-977d-c8b518a350f1$hsfw-dataweapon-00000000001152$4$4
        # 传感器的guid
        self.sensor_guids = ""
        # 重新装载优先级选中的武器DBID集合
        self.reload_priority_set = ""
        # 左弦尾1
        self.ps1 = False
        # 左弦中后1
        self.pma1 = False
        # 左弦中前
        self.pmf1 = False
        # 左弦首1
        self.pb1 = False
        # 右弦尾1
        self.ss1 = False
        # 右弦中后1
        self.sma1 = False
        # 右弦中前1
        self.smf1 = False
        # 右弦首1-bow
        self.sb1 = False
        # 左弦尾2-stern
        self.ps2 = False
        # 左弦中后2
        self.pma2 = False
        # 左弦中前2
        self.pmf2 = False
        # 左弦首2
        self.pb2 = False
        # 右弦尾2
        self.ss2 = False
        # 右弦中后2
        self.sma2 = False
        # 右弦中前2
        self.smf2 = False
        # 右弦首2
        self.sb2 = False
        # 是否查找挂实体
        self.select = False

        self.var_map = CMountDict.var_map
