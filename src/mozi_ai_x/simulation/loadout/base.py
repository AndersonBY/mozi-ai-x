from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from ..base import Base
from ..situ_interpret import CLoadoutDict


class CLoadout(Base):
    """
    挂载方案类
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.name = ""
        # 挂载的武器的数量
        self.load_weapon_count = 0
        # 挂载的数量和挂架载荷
        self.load_ratio = ""
        # 飞机的guid
        self.aircraft_guid = ""
        # 是否支持快速出动
        self.quick_turnaround = False
        # 最大飞行波次
        self.max_sorties = 0
        # 货物类型
        self.cargo_type = 0
        # dbid
        self.db_id = 0
        # 是否查找挂实体
        self.select = False

        self.var_map = CLoadoutDict.var_map
