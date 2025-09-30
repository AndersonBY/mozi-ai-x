"""
分布式 Mozi 服务支持模块

提供 Master-Client 架构，Master 作为 Mozi gRPC 的透明代理
"""

from typing import TYPE_CHECKING

import grpclib.server
from grpclib.client import Channel

from ...utils.log import mprint_with_name

if TYPE_CHECKING:
    from .server import MoziServer

mprint = mprint_with_name("Distributed")


class MoziProxyServer:
    """
    Mozi gRPC 透明代理服务器
    在 Master 节点上运行，代理所有 Mozi gRPC 调用
    """

    def __init__(self, mozi_server: "MoziServer", proxy_port: int):
        self.mozi_server = mozi_server
        self.proxy_port = proxy_port
        self.server: grpclib.server.Server | None = None
        self._mozi_channel: Channel | None = None
        self._mozi_stub = None

    async def start(self):
        """启动代理服务器"""
        try:
            # 连接到真实的 Mozi 服务器
            self._mozi_channel = Channel(
                host=self.mozi_server.server_ip,
                port=self.mozi_server.server_port,
                ssl=False
            )

            # 导入 Mozi 的 gRPC stub
            from ..proto.grpc import GRpcStub
            self._mozi_stub = GRpcStub(self._mozi_channel)

            # 创建代理服务实现
            from ..proto.grpc import GRpcBase

            class MoziProxyImplementation(GRpcBase):
                def __init__(self, proxy_server):
                    self.proxy = proxy_server

                async def grpc_connect(self, request):
                    """代理 grpc_connect 调用"""
                    # 直接转发到真实 Mozi 服务器
                    response = await self.proxy._mozi_stub.grpc_connect(request)

                    # 拦截特定命令，更新 Master 本地态势
                    if hasattr(self.proxy.mozi_server, 'scenario') and self.proxy.mozi_server.scenario:
                        await self.proxy._intercept_response(request.name, response)

                    return response

            # 启动代理服务器
            self.server = grpclib.server.Server([MoziProxyImplementation(self)])
            await self.server.start(host="0.0.0.0", port=self.proxy_port)

            mprint.info(f"✓ Mozi 代理服务器已启动在 0.0.0.0:{self.proxy_port}")
            mprint.info(f"  代理目标: {self.mozi_server.server_ip}:{self.mozi_server.server_port}")

        except Exception as e:
            mprint.error(f"启动代理服务器失败: {e}")
            raise

    async def stop(self):
        """停止代理服务器"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        if self._mozi_channel:
            self._mozi_channel.close()

        mprint.info("Mozi 代理服务器已停止")

    async def _intercept_response(self, command: str, response):
        """拦截响应，更新 Master 本地态势"""
        try:
            # 拦截态势相关的命令
            if command in ["GetAllState", "UpdateState"]:
                # GrpcReply 有 message 字段，检查是否有内容
                if response.message and response.message != "脚本执行出错":
                    # 解析并更新本地态势
                    import json
                    situation_data = json.loads(response.message)

                    # 更新 scenario 对象
                    if command == "GetAllState":
                        # 全量更新
                        self.mozi_server.scenario.situation._parse_full_situation(
                            situation_data, self.mozi_server.scenario
                        )
                        mprint.debug("Master 本地态势已全量同步")
                    elif command == "UpdateState":
                        # 增量更新
                        self.mozi_server.scenario.situation._process_update_data(
                            situation_data, self.mozi_server.scenario
                        )
                        mprint.debug("Master 本地态势已增量同步")

        except Exception as e:
            mprint.warning(f"态势同步失败: {e}")


class MoziProxyClient:
    """
    Mozi gRPC 客户端（用于 Client 模式）
    直接连接到 Master 的代理端口
    """

    def __init__(self, master_ip: str, master_port: int):
        self.master_ip = master_ip
        self.master_port = master_port
        self.channel: Channel | None = None
        self.stub = None
        self._connected = False

    async def connect(self) -> bool:
        """连接到 Master 代理服务器"""
        try:
            self.channel = Channel(host=self.master_ip, port=self.master_port, ssl=False)

            from ..proto.grpc import GRpcStub
            self.stub = GRpcStub(self.channel)

            # 测试连接
            from ..proto.grpc import GrpcRequest
            test_request = GrpcRequest(name="print('test')")
            response = await self.stub.grpc_connect(test_request)

            if response:
                self._connected = True
                mprint.info(f"✓ 已连接到 Master 代理 {self.master_ip}:{self.master_port}")
                return True
            else:
                mprint.warning("Master 代理连接测试失败")
                return False

        except Exception as e:
            mprint.error(f"连接到 Master 代理失败: {e}")
            self._connected = False
            return False

    async def disconnect(self):
        """断开连接"""
        if self.channel:
            self.channel.close()
            self._connected = False
            mprint.info("已断开 Master 代理连接")

    @property
    def is_connected(self) -> bool:
        """是否已连接"""
        return self._connected

    async def send_and_recv(self, command: str):
        """发送命令到 Master 代理"""
        if not self._connected:
            raise RuntimeError("未连接到 Master 代理")

        try:
            from ..proto.grpc import GrpcRequest
            request = GrpcRequest(name=command)
            response = await self.stub.grpc_connect(request)

            # 转换为 ServerResponse 格式
            from .response import ServerResponse
            return ServerResponse(
                status_code=0,
                message="OK",
                raw_data=response.message,
                data=response.message,
                error=None,
            )

        except Exception as e:
            mprint.error(f"发送命令失败: {e}")
            raise
