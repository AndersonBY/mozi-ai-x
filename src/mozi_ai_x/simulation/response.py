from .base import BaseObject
from .situ_interpret import CResponseDict


class CResponse(BaseObject):
    """
    响应类
    """

    def __init__(self, id: str):
        # 编号
        self.id = id  # changed by aie
        # 响应内容
        self.response = ""
        # 类型
        self.type = ""

        self.var_map = CResponseDict.var_map

    @property
    def class_name(self) -> str:
        return self.__class__.__name__
