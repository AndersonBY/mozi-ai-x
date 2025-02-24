from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import MoziServer
    from ..situation import CSituation

from ...utils.log import mprint_with_name


mprint = mprint_with_name("Base")


class BaseObject:
    def __init__(self):
        self.var_map = {}

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    def parse(self, json_data: dict):
        """解析 JSON 数据并设置为实例属性。

        Args:
            json_data (dict): 需要解析的 JSON 数据。

        Returns:
            None
        """
        for k, v in self.var_map.items():
            if k in json_data:
                try:
                    setattr(self, v, json_data[k])
                except Exception as e:
                    mprint.error(f"parse {self.class_name} {k} error: {e}")


class Base(BaseObject):
    """
    基础类
    """

    def __init__(self, guid: str, mozi_server: "MoziServer", situation: "CSituation"):
        super().__init__()
        self.guid = guid
        self.mozi_server = mozi_server
        self.situation = situation
