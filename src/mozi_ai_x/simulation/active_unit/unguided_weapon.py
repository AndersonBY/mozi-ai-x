from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from .weapon import CWeapon
from ..situ_interpret import CUnguidedWeaponDict


class CUnguidedWeapon(CWeapon):
    """
    动态创建非制导武器
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__(guid, mozi_server, situation)
        self.var_map = CUnguidedWeaponDict.var_map
