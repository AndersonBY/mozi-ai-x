# mozi_ai_x

**墨子人工智能体 SDK (异步版本)**

## 简介

`mozi_ai_x` 是一个基于墨子仿真推演平台的异步 Python SDK。它旨在帮助开发者快速构建和部署与墨子系统交互的人工智能体，支持异步操作以提高效率。

本 SDK 提供了一套完整的 API，用于与墨子服务端进行通信，获取态势信息，控制作战单元，执行任务规划等。

## 特性

*   **异步支持:** 基于 `asyncio` 和 `grpclib`，提供高性能的异步 API。
*   **分布式支持 (NEW):** 内置 Master-Client 架构，支持多节点分布式访问
    *   零配置：无需手动搭建服务器
    *   API 透明：分布式和单机使用完全相同的 API
    *   自动代理：Client 模式下所有操作自动通过 Master 代理
*   **全面的 API:** 覆盖墨子系统的大部分功能，包括：
    *   态势感知 (获取单元、目标、环境信息等)
    *   单元控制 (移动、攻击、传感器控制、条令设置等)
    *   任务管理 (创建、分配、修改任务)
    *   事件与触发器 (设置和响应事件)
    *   数据库访问 (查询武器、平台等信息)
*   **良好的结构:** 代码结构清晰，模块化设计，易于理解和扩展。
*   **MIT 许可:** 开源且允许商业使用。

## 安装

### 快速安装（推荐）

推荐使用 `pip` 直接从 PyPI 安装，无需从源码安装：

```bash
pip install mozi-ai-x
```

除非你需要本地开发或使用尚未发布的最新功能，否则无需从源码安装。

### 从源码安装（如需本地开发）

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

3.  **本地安装 mozi_ai_x:**

    将仓库安装为可导入的包：
    ```bash
    pip install .
    ```
    或者
    ```bash
    pdm build #构建包
    pdm install dist/mozi_ai_x-0.1.0-py3-none-any.whl
    ```

## 快速开始 (示例)

### 单机模式（传统用法）

```python
import asyncio
from mozi_ai_x import MoziServer

async def main():
    # 连接到墨子服务器 (需要先启动墨子服务端程序)
    server = MoziServer("127.0.0.1", 6060)  # 替换为实际的 IP 和端口
    await server.start()

    if server.is_connected:
        # 加载想定 (替换为你的想定文件路径)
        scenario = await server.load_scenario()

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

### 分布式模式（新功能）

#### Master 节点（主控节点）

```python
import asyncio
from mozi_ai_x import MoziServer

async def main():
    # Master 模式：连接墨子 + 启动 API 服务
    master = MoziServer(
        server_ip="127.0.0.1",
        server_port=6060,
        scenario_path="test.scen",
        mode="master",      # 指定为 Master 模式
        api_port=6061,      # API 服务端口
    )

    await master.start()
    scenario = await master.load_scenario()

    print(f"Master 已启动，API 端口: {master.api_port}")
    print(f"想定: {scenario.get_title()}")

    # 控制推演
    await master.run_grpc_simulate()

asyncio.run(main())
```

#### Client 节点（工作节点 - 红方）

```python
import asyncio
from mozi_ai_x import MoziServer

async def main():
    # Client 模式：连接到 Master
    client = MoziServer(
        server_ip="192.168.1.100",  # Master 的 IP
        server_port=6061,            # Master 的 API 端口
        mode="client"                # 指定为 Client 模式
    )

    await client.start()

    # 从 Master 获取想定（API 完全一致！）
    scenario = await client.get_scenario()

    # 控制红方（所有操作自动通过 Master 代理）
    red_side = scenario.get_side_by_name("红方")
    aircrafts = red_side.get_aircrafts()

    # 设置飞机速度（会自动代理到墨子）
    for guid, aircraft in aircrafts.items():
        await aircraft.set_desired_speed(500)

asyncio.run(main())
```

#### Client 节点（工作节点 - 蓝方）

```python
# 蓝方节点可以独立运行，与红方并行工作
client = MoziServer(
    server_ip="192.168.1.100",
    server_port=6061,
    mode="client"
)

await client.start()
scenario = await client.get_scenario()

# 控制蓝方
blue_side = scenario.get_side_by_name("蓝方")
# ... 蓝方的控制逻辑
```

### 运行分布式系统

```bash
# 1. 在主服务器上运行 Master
python examples/distributed_master.py

# 2. 在红方服务器上运行 Client
python examples/distributed_client_red.py

# 3. 在蓝方服务器上运行 Client
python examples/distributed_client_blue.py
```

更多示例请查看 `examples/` 目录。

## API 文档

更详细的 API 文档和用法示例，请参考代码中的 docstring 和后续补充的文档。

## 分布式功能详解

### 架构说明

```
┌─────────────┐
│ Mozi Server │ (墨子仿真服务器)
└──────┬──────┘
       │ gRPC (6060)
       │
┌──────▼──────────────────────┐
│  MoziServer (Master Mode)   │  主节点
│  - 连接墨子                  │
│  - 加载想定                  │
│  - 控制推演                  │
│  - 内置 API 服务 (6061)     │
└──────┬──────────────────────┘
       │ Network
       │
   ┌───┴────┬─────────┬────────┐
   │        │         │        │
┌──▼──┐ ┌──▼──┐  ┌──▼──┐  ┌──▼──┐
│ 红方 │ │ 蓝方 │  │监控 │  │分析 │  工作节点
│Client│ │Client│  │Client│  │Client│
└─────┘ └─────┘  └─────┘  └─────┘
```

### 三种运行模式

1. **standalone** (默认)
   - 传统单机模式
   - 直接连接墨子
   - 向后兼容，不影响现有代码

2. **master**
   - 连接墨子服务器
   - 负责想定加载和推演控制
   - 自动启动内置 API 服务
   - 为 Client 节点提供代理访问

3. **client**
   - 连接到 Master 节点
   - 通过 Master 代理访问墨子
   - API 完全一致，无需修改代码
   - 支持多个 Client 并行运行

### 使用场景

#### 场景 1：多人协同开发
```
Master 节点（共享服务器）：加载想定，控制推演
Client 节点（开发者A）：开发红方智能体
Client 节点（开发者B）：开发蓝方智能体
Client 节点（开发者C）：监控和分析
```

#### 场景 2：分布式 AI 训练
```
Master 节点：管理训练环境
Client 节点 1-N：并行运行多个智能体实例
```

#### 场景 3：红蓝对抗
```
Master 节点：控制推演进度
Client 节点（红方服务器）：红方决策系统
Client 节点（蓝方服务器）：蓝方决策系统
Client 节点（裁判服务器）：监控和评分
```

### 关键特性

✅ **零配置**：无需手动搭建 gRPC 服务器，MoziServer 内置
✅ **API 透明**：分布式和单机使用完全相同的 API
✅ **自动代理**：Client 的所有操作自动转发到 Master
✅ **向后兼容**：不影响现有单机代码
✅ **易于扩展**：可以轻松添加认证、加密、负载均衡等功能

### 注意事项

1. **proto 文件生成**：首次使用需要生成分布式 API 的 proto 文件
   ```bash
   pdm run gen-proto
   ```

2. **网络配置**：确保 Master 的 API 端口（默认 6061）可被 Client 访问

3. **性能考虑**：Client 通过网络代理，会有轻微延迟

4. **安全性**：当前版本未加密，生产环境建议使用 VPN 或添加 TLS

## 贡献

欢迎提交 Issues 和 Pull Requests，共同完善这个 SDK。

## 许可

本项目使用 MIT 许可。

## 免责声明

本 SDK 是为墨子仿真推演平台开发的非官方工具。使用本 SDK 产生的任何问题，开发者不承担任何责任。请确保您对墨子系统及其使用有充分的了解。
