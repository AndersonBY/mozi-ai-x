# mozi_ai_x

**墨子人工智能体 SDK (异步版本)**

## 简介

`mozi_ai_x` 是一个基于墨子仿真推演平台的异步 Python SDK。它旨在帮助开发者快速构建和部署与墨子系统交互的人工智能体，支持异步操作以提高效率。

本 SDK 提供了一套完整的 API，用于与墨子服务端进行通信，获取态势信息，控制作战单元，执行任务规划等。

## 特性

*   **异步支持:** 基于 `asyncio` 和 `grpclib`，提供高性能的异步 API。
*   **全面的 API:** 覆盖墨子系统的大部分功能，包括：
    *   态势感知 (获取单元、目标、环境信息等)
    *   单元控制 (移动、攻击、传感器控制、条令设置等)
    *   任务管理 (创建、分配、修改任务)
    *   事件与触发器 (设置和响应事件)
    *   数据库访问 (查询武器、平台等信息)
*   **良好的结构:** 代码结构清晰，模块化设计，易于理解和扩展。
*   **MIT 许可:** 开源且允许商业使用。

## 安装

1.  **安装依赖:**

    ```bash
    pip install -U pip  # 建议升级 pip
    pip install grpcio grpcio-tools numpy psutil
    ```
    或 使用`pdm`
    ```bash
    pdm install
    ```

2.  **生成 protobuf 代码:**

    ```bash
    # 假设你已经安装了 grpcio-tools
    # 如果没有, 先执行： pip install grpcio-tools
    python scripts/proto/gen_proto.py -o src/mozi_ai_x/simulation/proto
    ```

    或者，如果你使用 `pdm`：

    ```bash
    pdm run gen-proto
    ```

    注意：`GRPCServerBase.proto` 文件使用了 `package grpc;`, 并且 `gen_proto.py`会把生成的`py`文件中`/grpc.gRPC/`替换成`/GRPC.gRPC/`

3.  **安装 mozi_ai_x (可选):**

    如果你想将 `mozi_ai_x` 安装为一个可导入的包，可以执行：
    ```bash
    pip install .
    ```
    或者
    ```bash
    pdm build #构建包
    pdm install dist/mozi_ai_x-0.1.0-py3-none-any.whl
    ```

## 快速开始 (示例)

```python
import asyncio
from mozi_ai_x.simulation.server import MoziServer
from mozi_ai_x.simulation.scenario import CScenario

async def main():
    # 连接到墨子服务器 (需要先启动墨子服务端程序)
    server = MoziServer("127.0.0.1", 6060)  # 替换为实际的 IP 和端口
    await server.start()

    if server.is_connected:
        # 加载想定 (替换为你的想定文件路径)
        scenario: CScenario = await server.load_scenario()

        if scenario:
            print(f"想定加载成功: {scenario.get_title()}")

            # 获取红方
            red_side = scenario.get_side_by_name("红方")

            if red_side:
                # 获取红方所有飞机
                aircrafts = red_side.get_aircrafts()
                print(f"红方飞机数量: {len(aircrafts)}")

                for guid, aircraft in aircrafts.items():
                    # 示例：获取飞机信息
                    print(f"  飞机: {aircraft.name}, GUID: {guid}, 经度: {aircraft.longitude}, 纬度: {aircraft.latitude}")

                    # 示例：设置飞机期望速度 (单位：千米/小时)
                    # await aircraft.set_desired_speed(500)

            else:
                print("未找到红方。")
        else:
            print("想定加载失败。")

    else:
        print("无法连接到墨子服务器。")

# 运行
asyncio.run(main())
```

## API 文档

更详细的 API 文档和用法示例，请参考代码中的 docstring 和后续补充的文档。

## 贡献

欢迎提交 Issues 和 Pull Requests，共同完善这个 SDK。

## 许可

本项目使用 MIT 许可。

## 免责声明

本 SDK 是为墨子仿真推演平台开发的非官方工具。使用本 SDK 产生的任何问题，开发者不承担任何责任。请确保您对墨子系统及其使用有充分的了解。
