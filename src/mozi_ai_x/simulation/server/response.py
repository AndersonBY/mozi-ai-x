from typing import Any
from grpclib import GRPCError
from grpclib.const import Status


class ServerResponse:
    """
    Mozi 服务器响应包装类（仿 HTTP Response 设计）

    属性:
        status_code (int): 状态码（兼容 gRPC 状态码 + 自定义扩展码）
        message (str): 人类可读的状态消息
        data (Any): 解析后的响应数据（可为空）
        raw_data (str): 原始响应字符串
        error (Optional[Exception]): 异常对象（请求失败时）
        is_success (bool): 请求是否成功
    """

    # 状态码定义（扩展 gRPC 状态码）
    STATUS_CODES = {
        Status.OK.value: "OK",
        Status.UNIMPLEMENTED.value: "Not Implemented",
        Status.UNAVAILABLE.value: "Service Unavailable",
        1000: "Connection Error",
        1001: "Empty Response",
        1002: "Lua execution error",
    }

    def __init__(
        self,
        status_code: int = Status.OK.value,
        message: str = "OK",
        raw_data: str = "",
        data: Any = None,
        error: Exception | None = None,
    ):
        self.status_code = status_code
        self.message = message
        self.raw_data = raw_data
        self.data = data
        self.error = error

    @property
    def success(self) -> bool:
        return self.status_code == Status.OK.value

    @property
    def lua_success(self) -> bool:
        return self.status_code == Status.OK.value and self.raw_data == "lua执行成功"

    @classmethod
    def create_success(cls, raw_data: str = "", data: Any = None):
        """成功响应工厂方法"""
        return cls(
            status_code=Status.OK.value, message=cls.STATUS_CODES[Status.OK.value], raw_data=raw_data, data=data
        )

    @classmethod
    def create_error(cls, status_code: int, raw_data: str = "", error: Exception | None = None):
        """错误响应工厂方法"""
        return cls(
            status_code=status_code,
            message=cls.STATUS_CODES.get(status_code, "Unknown Error"),
            raw_data=raw_data,
            error=error,
        )

    @classmethod
    def from_grpc_error(cls, error: GRPCError, raw_data: str = ""):
        """从 gRPC 错误创建响应"""
        return cls.create_error(status_code=error.status.value, raw_data=raw_data, error=error)

    def __str__(self):
        return f"<ServerResponse {self.status_code} {self.message}>"

    def __repr__(self):
        return f"ServerResponse(status_code={self.status_code}, message={self.message!r}, data={self.data!r})"
