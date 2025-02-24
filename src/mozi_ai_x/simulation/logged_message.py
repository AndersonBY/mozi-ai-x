from .situ_interpret import CLoggedMessageDict
from .base import BaseObject


class CLoggedMessage(BaseObject):
    """
    日志消息类
    """

    def __init__(self, guid: str):
        # 消息对象guid
        self.guid = guid
        # 方的GUID
        self.side = ""
        # 事件的内容
        self.message_text = ""
        # 消息发生的时间
        self.timestamp = 0.0
        # 消息类型
        self.message_type = 0
        # 消息编号
        self.increment = 0.0
        # 等级
        self.level = ""
        # 经度
        self.longitude = 0.0
        # 纬度
        self.latitude = 0.0
        # 报告者GUID
        self.reporter_guid = ""
        # 事件关联的目标本身单元的GUID
        self.contact_active_unit_guid = ""

        self.var_map = CLoggedMessageDict.var_map
