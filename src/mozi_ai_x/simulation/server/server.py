import os
import asyncio
from pathlib import Path
from typing import Literal

import psutil
from grpclib import GRPCError
from grpclib.const import Status
from grpclib.client import Channel

from ..scenario import CScenario
from ...utils.log import mprint_with_name
from ..proto import GrpcRequest, GRpcStub as GrpcStub
from mozi_ai_x.utils.validator import validate_literal_args

from .response import ServerResponse


mprint = mprint_with_name("Mozi Server")


class MoziServer:
    """
    仿真服务类，墨子仿真服务器类

    支持三种运行模式：
    - standalone: 单机模式（默认），直接连接墨子服务器
    - master: Master 模式，连接墨子 + 启动内置 API 服务供其他节点访问
    - client: Client 模式，连接到 Master 节点，通过代理访问墨子
    """

    def __init__(
        self,
        server_ip: str,
        server_port: int,
        platform: Literal["windows", "linux"] = "windows",
        scenario_path: str = "",
        compression: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8] = 4,
        synchronous: bool = True,
        platform_mode: Literal["versus", "development", "train", "eval"] = "development",
        agent_key_event_file: str | None = None,
        retry_times: int = 3,
        mode: Literal["standalone", "master", "client"] = "standalone",
        api_port: int = 6061,
    ):
        # 服务器IP
        self.server_ip = server_ip
        # 服务器端口
        self.server_port = server_port
        # 平台： windows 或 linux
        self.platform = platform
        # 想定名称
        # windows上使用想定文件全称且带后缀，如 菲海战事-双方均无任务.scen
        # linux上使用使用想定文件名，不带后缀，且文件名要求不包含中文， 如 phisea-nomssn
        self.scenario_path = scenario_path
        # 推演档位 0-1倍速，1-2倍速，2-5倍速，3-15倍速，4-30倍速，5-60倍速，6-300倍速，7-900倍速，8-1800倍速
        self.compression = compression
        # 推进模式  True 同步 ,False 异步
        self.synchronous = synchronous
        # 平台模式
        # versus 比赛模式：手工或第三方程序启动墨子并加载想定
        # development 开发模式：智能体启动墨子并加载想定
        # train  训练模式：手工或第三方程序启动墨子，智能体加载想定
        # eval   对战模式：手工或第三方程序启动墨子，智能体加载想定
        self.platform_mode = platform_mode

        # grpc客户端
        self.grpc_client: GrpcStub | None = None
        self.channel: Channel | None = None
        self.is_connected = False

        # 命令池
        self.exect_flag = True
        self.command_pool: list[str] = []
        self.command_num = 0

        # 用于比赛，智能体关键事件文件绝对路径，用于判定智能体是否正常运行
        self.agent_key_event_file = agent_key_event_file
        self.step_count = 0

        # 重试次数
        self.retry_times = retry_times

        # 分布式模式相关
        self.mode = mode
        self.api_port = api_port
        # 保留用于向后兼容
        self.api_server = None
        self.api_client = None
        self.scenario: CScenario | None = None

        # 根据模式初始化
        if mode == "master":
            from .distributed import MoziProxyServer

            self.proxy_server = MoziProxyServer(self, api_port)
            mprint.info(f"初始化为 Master 模式，代理端口: {api_port}")
        elif mode == "client":
            from .distributed import MoziProxyClient

            self.proxy_client = MoziProxyClient(server_ip, server_port)
            mprint.info(f"初始化为 Client 模式，连接到 Master 代理: {server_ip}:{server_port}")
        else:
            mprint.info("初始化为 Standalone 模式")

    async def connect_grpc_server(self) -> bool:
        """
        连接墨子服务器

        Returns:
            bool: 连接是否成功
        """
        # 如果已有连接，先关闭
        await self.close()

        try:
            self.channel = Channel(
                host=self.server_ip,
                port=self.server_port,
                ssl=False,  # 明确指定不使用SSL
            )
            self.grpc_client = GrpcStub(channel=self.channel)
            # await self.send_and_recv("test")
            return True
        except Exception as e:
            mprint(f"连接墨子服务器失败：{e}")
            return False

    async def close(self):
        """关闭现有连接"""
        try:
            if self.channel is not None:
                self.channel.close()
            self.channel = None
            self.grpc_client = None
            self.is_connected = False
        except Exception as e:
            mprint(f"关闭连接时出错: {e}")

    async def send_and_recv(self, cmd: str, raise_error: bool = True) -> ServerResponse:
        """
        gRPC发送和接收服务端消息方法

        args:
            cmd: lua命令
            raise_error: 是否在连接失败时抛出异常
        returns:
            ServerResponse: 包含响应状态和数据的对象
        """
        # Client 模式：通过 Master 代理
        if self.mode == "client":
            if hasattr(self, "proxy_client") and self.proxy_client and self.proxy_client.is_connected:
                return await self.proxy_client.send_and_recv(cmd)
            else:
                mprint.warning("未连接到 Master 代理")
                if raise_error:
                    raise RuntimeError("未连接到 Master 代理")
                return ServerResponse.create_error(1000, "未连接到 Master 代理")

        # Master 或 Standalone 模式：直连墨子
        if not self.is_connected:
            if not await self.connect_grpc_server():
                mprint.warning("连接墨子服务器失败")
                if raise_error:
                    raise RuntimeError("连接墨子服务器失败")
                return ServerResponse.create_error(1000, "连接墨子服务器失败")

        if self.grpc_client is None:
            if raise_error:
                raise RuntimeError("grpc_client is not initialized")
            return ServerResponse.create_error(1000, "grpc_client 未初始化")

        if not self.exect_flag:
            self.command_num += 1
            self.throw_into_pool(cmd)
            return ServerResponse.create_success()

        try:
            mprint.debug(f"发送消息: {cmd}")
            response = await self.grpc_client.grpc_connect(grpc_request=GrpcRequest(name=cmd))
            mprint.debug(f"返回结果: {response.to_dict()}")

            if not response.message:
                if raise_error:
                    raise RuntimeError("返回结果为空")
                return ServerResponse.create_error(1001, "返回结果为空")

            return ServerResponse.create_success(raw_data=response.message, data=response.message)

        except Exception as e:
            if isinstance(e, GRPCError) and e.status == Status.UNIMPLEMENTED:
                mprint.warning(f"服务端未实现该RPC方法: {e}")
                return ServerResponse.from_grpc_error(e)

            mprint.warning(f"发送接收消息失败: {e}")
            self.is_connected = False

            # 带重试次数的连接恢复逻辑
            for attempt in range(1, self.retry_times + 1):
                mprint.debug(f"正在尝试第 {attempt}/{self.retry_times} 次重试...")

                if not await self.connect_grpc_server():
                    mprint.warning(f"第 {attempt} 次重连失败")
                    continue

                try:
                    response = await self.grpc_client.grpc_connect(grpc_request=GrpcRequest(name=cmd))
                    if response.message:
                        return ServerResponse.create_success(raw_data=response.message, data=response.message)

                    if raise_error:
                        raise RuntimeError("返回结果为空")
                    return ServerResponse.create_error(status_code=1001)

                except Exception as retry_e:
                    mprint.warning(f"第 {attempt} 次请求失败: {retry_e}")
                    self.is_connected = False

            # 所有重试失败后的处理
            error_msg = f"操作失败，共尝试 {self.retry_times + 1} 次（含重试 {self.retry_times} 次）"
            mprint.warning(error_msg)

            if raise_error:
                raise RuntimeError(error_msg) from e
            return ServerResponse.create_error(status_code=1000, error=e)

    async def start(self):
        """启动墨子仿真服务端"""
        # Client 模式：连接到 Master 代理
        if self.mode == "client":
            if hasattr(self, "proxy_client"):
                success = await self.proxy_client.connect()
                if success:
                    self.is_connected = True
                    response = await self.send_and_recv("GetAllState")
                    scenario = CScenario(self)
                    self.scenario = scenario
                    # 解析态势数据
                    if response.raw_data and response.raw_data != "脚本执行出错":
                        import json

                        try:
                            situation_data = json.loads(response.raw_data)
                            scenario.situation._parse_full_situation(situation_data, scenario)
                            print("✓ 态势数据解析完成")
                        except Exception as e:
                            print(f"✗ 态势数据解析失败: {e}")
                    else:
                        print("✗ 没有获取到有效的态势数据")
                else:
                    mprint.error("✗ 连接 Master 代理失败")
            return

        # Master 或 Standalone 模式：连接墨子
        if self.platform == "windows":
            # 判断墨子是否已经启动
            is_mozi_server_started = False
            for i in psutil.process_iter():
                if i.name() == "MoziServer.exe":
                    mprint(f"墨子已启动: {i.name()}-{i.pid}-{i.status()}")
                    is_mozi_server_started = True
                    break

            # 启动墨子
            if not is_mozi_server_started:
                mozi_path = os.environ.get("MOZIPATH")
                if mozi_path:
                    mozi_server_exe_file = Path(mozi_path) / "MoziServer.exe"
                    os.popen(str(mozi_server_exe_file))
                    mprint("墨子推演方服务端已启动")
                else:
                    mprint("墨子推演方服务端路径未设置")

            # 启动墨子后，稍微等一会，让它初始化一下
            await asyncio.sleep(10)
        else:
            pass

        # 初始化GRPC客户端
        mprint.debug("初始化GRPC客户端")
        self.is_connected = await self.connect_grpc_server()

        # 测试墨子服务端是否启动成功
        connect_cout = 0
        while not self.is_connected and connect_cout < 60:
            self.is_connected = await self.is_server_connected()
            connect_cout += 1
            if not self.is_connected:
                mprint("还没连接上墨子推演服务器,再等1秒")
                await asyncio.sleep(1)  # 使用异步sleep

        if self.is_connected:
            if self.agent_key_event_file:
                self.write_key_event_string_to_file("成功连接墨子推演服务器！")
            mprint("成功连接墨子推演服务器！")

            # Master 模式：启动 Mozi 代理服务
            if self.mode == "master" and hasattr(self, "proxy_server"):
                try:
                    await self.proxy_server.start()
                except Exception as e:
                    mprint.error(f"✗ 启动 Master 代理服务失败: {e}")
        else:
            mprint("连接墨子推演服务器失败（60秒）！")

    async def is_server_connected(self) -> bool:
        """
        判断是否已经连接上墨子服务器。使用笨办法，如果发送数据时发生异常，则认为墨子服务器未启动。

        Returns:
            bool: 是否已连接
        """
        try:
            await self.send_and_recv("test")
            return True
        except Exception as e:
            mprint(f"判断墨子服务器是否连接失败：{e}")
            return False

    async def load_scenario(self) -> "CScenario":
        """
        加载想定
        限制：专项赛禁用

        Returns:
            CScenario: 想定类对象
        """
        # Client 模式：通过代理加载想定
        if self.mode == "client":
            mprint.info("Client 模式：通过 Master 代理加载想定")

        scenario_file = self.scenario_path
        loaded = False
        if self.platform == "windows":
            loaded = await self.load_scenario_in_windows(scenario_file, False)
        else:
            loaded = await self.load_scenario_in_linux(scenario_file, "Edit")

        if not loaded:
            mprint.error("发送想定加载LUA指令给服务器，服务器返回异常！")

        load_success = False
        for _ in range(60):
            if await self.is_scenario_loaded():
                mprint.info("想定加载成功！")
                load_success = True
                break

            mprint.warning(f"想定还没有加载完毕，再等一秒！可能原因，1）时间太短；2）服务端没有想定{self.scenario_path}！")

            await asyncio.sleep(1)

        # 如果想定加载失败
        if not load_success:
            mprint.error(f"超过50秒，想定没有加载成功。可能是服务端没有想定:{scenario_file}！")
            raise ValueError("想定加载失败")

        scenario = CScenario(self)
        self.scenario = scenario
        return scenario

    async def get_scenario(self) -> "CScenario":
        """
        获取想定对象

        Returns:
            CScenario: 想定类对象
        """
        if not self.scenario:
            raise RuntimeError("想定未加载，请先调用 load_scenario()")
        return self.scenario

    async def load_scenario_in_windows(self, scenario_path: str, edit_mode: bool) -> bool:
        """在 Windows 系统上加载想定。

        在 Windows 平台加载指定的想定文件，可选择是否以编辑模式加载。
        注意：此功能在专项赛中禁用。

        Args:
            - scenario_path (str): 想定文件的相对路径，仅支持 .scen 文件
            - edit_mode (bool): 加载模式
                - True: 想定编辑模式
                - False: 想定推演模式

        Returns:
            bool: 加载是否成功

        Examples:
            >>> await server.load_scenario_in_windows("战役想定.scen", False)
            True
        """
        response = await self.send_and_recv(f"Hs_ScenEdit_LoadScenario('{scenario_path}', {str(edit_mode).lower()})")
        return response.lua_success

    @validate_literal_args
    async def load_scenario_in_linux(self, scenario_path: str, model: Literal["Edit", "Play"]) -> bool:
        """
        linux上加载想定
        限制：专项赛禁用

        Args:
            - scenario_path: 想定文件的相对路径（仅支持XML文件）
            - model: 模式
                - "Edit"  想定编辑模式
                - "Play"  想定推演模式

        Returns:
            bool: 加载是否成功
        """
        response = await self.send_and_recv(f"Hs_PythonLoadScenario('{scenario_path}', '{model}')")
        return response.lua_success

    def throw_into_pool(self, cmd: str) -> None:
        """
        将命令投入命令池。

        Args:
            cmd: lua命令

        Returns:
            None
        """
        self.command_pool.append(cmd)

    async def transmit_pool(self) -> bool:
        """
        将命令池倾泄到墨子服务端

        Returns:
            bool: 是否成功
        """
        cmds = "\r\n".join(self.command_pool)
        response = await self.send_and_recv(cmds)
        return response.lua_success

    async def is_scenario_loaded(self) -> bool:
        """
        功获取想定是否加载

        Returns:
            bool: 想定是否加载
        """
        response = await self.send_and_recv("print(Hs_GetScenarioIsLoad())")
        return "yes" in response.raw_data.lower()  # 怎么想的这个返回值，还非得套个引号，服务端真是瞎设计

    async def creat_new_scenario(self) -> bool:
        """
        新建想定
        限制：专项赛禁用

        Returns:
            bool: 新建是否成功
        """
        response = await self.send_and_recv("Hs_ScenEdit_CreateNewScenario()")
        return response.lua_success

    @validate_literal_args
    async def set_simulate_compression(self, n_compression: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8] = 4) -> bool:
        """
        设置想定推演倍速
        限制：专项赛禁用

        Args:
            n_compression 推演时间步长档位
                0: 1 秒
                1: 2 秒
                2: 5 秒
                3: 15 秒
                4: 30 秒
                5: 1 分钟
                6: 5 分钟
                7: 15 分钟
                8: 30 分钟

        Returns:
            bool: 设置是否成功
        """
        response = await self.send_and_recv(f"ReturnObj(Hs_SetSimCompression({n_compression}))")
        return response.lua_success

    async def increase_simulate_compression(self) -> bool:
        """
        推演时间步长提高 1 个档位
        限制：专项赛禁用

        Returns:
            bool: 设置是否成功
        """
        response = await self.send_and_recv("Hs_SimIncreaseCompression()")
        return response.lua_success

    async def decrease_simulate_compression(self) -> bool:
        """
        推演时间步长降低 1 个档位
        限制：专项赛禁用

        Returns:
            bool: 设置是否成功
        """
        response = await self.send_and_recv("Hs_SimDecreaseCompression()")
        return response.lua_success

    async def set_simulate_mode(self, b_mode: bool) -> bool:
        """
        设置想定推演模式
        限制：专项赛禁用

        Args:
            b_mode:
                True - 非脉冲式推进（尽快）
                False - 脉冲式推进（一般）

        Returns:
            bool: 设置是否成功
        """
        response = await self.send_and_recv(f"Hs_SetSimMode({str(b_mode).lower()})")
        return response.lua_success

    async def set_run_mode(self, synchronous: bool = True) -> bool:
        """
        设置python端与墨子服务端的交互模式，智能体决策想定是否暂停
        限制：专项赛禁用

        Args:
            - synchronous: 智能体决策想定是否暂停
                - True - 同步模式-是
                - False - 异步模式-否

        Returns:
            bool: 设置是否成功
        """
        response = await self.send_and_recv(f"SETRUNMODE({str(synchronous).upper()})")
        return response.lua_success

    async def set_decision_step_length(self, step_interval: int) -> bool:
        """
        设置决策间隔
        限制：专项赛禁用

        Args:
            - step_interval: 决策间隔，单位秒

        Returns:
            bool: 设置是否成功
        """
        response = await self.send_and_recv(f"Hs_OneTimeStop('Stop', {step_interval})")
        return response.lua_success

    async def suspend_simulate(self) -> bool:
        """
        设置环境暂停
        限制：专项赛禁用

        Returns:
            bool: 设置是否成功
        """

        response = await self.send_and_recv("Hs_SimStop()")
        return response.lua_success

    async def run_simulate(self) -> bool:
        """
        开始推演

        Returns:
            bool: 推演是否成功
        """
        response = await self.send_and_recv("ReturnObj(Hs_SimRun(true))")
        return response.lua_success

    async def run_grpc_simulate(self) -> bool:
        """
        开始推演

        Returns:
            bool: 推演是否成功
        """
        if self.agent_key_event_file:
            self.step_count += 1
            if self.step_count % 10 == 0:
                self.write_key_event_string_to_file(f"当前是第{self.step_count}步")
        response = await self.send_and_recv("ReturnObj(Hs_GRPCSimRun())")
        return response.lua_success

    @validate_literal_args
    async def init_situation(self, scenario: "CScenario", app_mode: Literal[1, 2, 3, 4]) -> None:
        """
        初始化态势
        限制：专项赛禁用

        Args:
            scenario: 想定类对象
            app_mode: 应用模式
                - 1: local windows train mode
                - 2: local linux train mode
                - 3: remote windows evaluate mode
                - 4: local windows evaluate mode
        """
        return await scenario.situation.init_situation(scenario, app_mode)

    async def update_situation(self, scenario: "CScenario") -> dict:
        """
        更新态势

        Args:
            scenario: 想定类对象

        Returns:
            dict: 返回变更信息
                {
                    "added": <>,
                    "deleted": <>,
                    "pseudo_guids": <>,
                }
        """
        return await scenario.situation.update_situation(scenario)

    async def emulate_no_console(self) -> bool:
        """
        模拟无平台推演

        Returns:
            bool: 模拟是否成功
        """
        response = await self.send_and_recv("Tool_EmulateNoConsole()")
        return response.lua_success

    async def run_script(self, script_path: str) -> bool:
        """
        运行服务端 Lua 文件夹下的 Lua 文件（*.lua）。

        Args:
            script_path: 字符串。服务端 Lua 文件夹下包括 Lua 文件名在内的相对路径

        Returns:
            bool: 运行是否成功
        """
        response = await self.send_and_recv(f"ScenEdit_RunScript('{script_path}')")
        return response.lua_success

    async def set_key_value(self, key: str, value: str) -> bool:
        """
        在系统中有一预设的"键-值"表，本函数向"键-值"表添加一条记录。

        Args:
            - key: 键的内容
            - value: 值的内容

        Returns:
            bool: 设置是否成功
        """
        response = await self.send_and_recv(f"ScenEdit_SetKeyValue('{key}','{value}')")
        return response.lua_success

    async def get_value_by_key(self, key: str) -> str:
        """
        在系统中有一预设的"键-值"表，本函数根据"键"的内容从"键-值"表中获取对应的"值"

        Args:
            - key: 键的内容

        Returns:
            str: 值的内容
        """
        response = await self.send_and_recv(f"ReturnObj(ScenEdit_GetKeyValue('{key}'))")
        return response.raw_data

    def write_key_event_string_to_file(self, key_event_str: str) -> None:
        """
        将智能体关键事件写入文件，用于比赛时检测智能体状态。

        Args:
            key_event_str: 智能体关键事件内容

        Returns:
            None
        """
        if not self.agent_key_event_file:
            mprint.warning("智能体关键事件文件未设置")
            return

        # 使用 Path 对象处理文件路径
        event_file = Path(self.agent_key_event_file)

        # 根据事件内容决定写入模式
        mode = "w" if key_event_str == "成功连接墨子推演服务器！" else "a"

        try:
            with open(event_file, mode, encoding="utf-8") as f:
                f.write(f"{key_event_str}\n")
        except OSError as e:
            mprint.warning(f"写入事件文件失败: {e}")
