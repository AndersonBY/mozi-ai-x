# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: GRPCServerBase.proto
# plugin: python-betterproto
# This file has been @generated

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Dict,
    Optional,
)
from collections.abc import AsyncIterator

import betterproto
import grpclib
from betterproto.grpc.grpclib_server import ServiceBase


if TYPE_CHECKING:
    import grpclib.server
    from betterproto.grpc.grpclib_client import MetadataLike
    from grpclib.metadata import Deadline


@dataclass(eq=False, repr=False)
class GrpcRequest(betterproto.Message):
    name: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class GrpcReply(betterproto.Message):
    message: str = betterproto.string_field(1)
    length: int = betterproto.int32_field(2)


class GRpcStub(betterproto.ServiceStub):
    async def grpc_connect(
        self,
        grpc_request: "GrpcRequest",
        *,
        timeout: float | None = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> "GrpcReply":
        return await self._unary_unary(
            "/GRPC.gRPC/GrpcConnect",
            grpc_request,
            GrpcReply,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def grpc_connect_stream(
        self,
        grpc_request: "GrpcRequest",
        *,
        timeout: float | None = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None,
    ) -> AsyncIterator[GrpcReply]:
        async for response in self._unary_stream(
            "/GRPC.gRPC/GrpcConnectStream",
            grpc_request,
            GrpcReply,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        ):
            yield response


class GRpcBase(ServiceBase):
    async def grpc_connect(self, grpc_request: "GrpcRequest") -> "GrpcReply":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def grpc_connect_stream(self, grpc_request: "GrpcRequest") -> AsyncIterator[GrpcReply]:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)
        yield GrpcReply()

    async def __rpc_grpc_connect(self, stream: "grpclib.server.Stream[GrpcRequest, GrpcReply]") -> None:
        request = await stream.recv_message()
        response = await self.grpc_connect(request)
        await stream.send_message(response)

    async def __rpc_grpc_connect_stream(self, stream: "grpclib.server.Stream[GrpcRequest, GrpcReply]") -> None:
        request = await stream.recv_message()
        await self._call_rpc_handler_server_stream(
            self.grpc_connect_stream,
            stream,
            request,
        )

    def __mapping__(self) -> dict[str, grpclib.const.Handler]:
        return {
            "/GRPC.gRPC/GrpcConnect": grpclib.const.Handler(
                self.__rpc_grpc_connect,
                grpclib.const.Cardinality.UNARY_UNARY,
                GrpcRequest,
                GrpcReply,
            ),
            "/GRPC.gRPC/GrpcConnectStream": grpclib.const.Handler(
                self.__rpc_grpc_connect_stream,
                grpclib.const.Cardinality.UNARY_STREAM,
                GrpcRequest,
                GrpcReply,
            ),
        }
