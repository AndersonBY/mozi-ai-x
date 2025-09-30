"""
分布式 Mozi 使用示例 - Master 节点

这个示例展示如何在 Master 模式下运行 MoziServer：
1. 连接墨子服务器
2. 启动 Mozi gRPC 透明代理服务
3. 加载想定并初始化态势
4. 控制推演进度（Master 本地会自动同步态势）
"""

import asyncio
from mozi_ai_x import MoziServer


async def main():
    # 创建 Master 节点
    # Master 负责连接墨子并提供 API 服务
    master = MoziServer(
        server_ip="127.0.0.1",  # 墨子服务器 IP
        server_port=6060,  # 墨子服务器端口
        scenario_path="shiptest.scen",  # 想定文件路径
        mode="master",  # 指定为 Master 模式
        api_port=6061,  # Master API 服务端口
        platform="windows",
        compression=4,
    )

    print("=" * 60)
    print("Master 节点启动中...")
    print("=" * 60)

    # 启动 Master：连接墨子 + 启动 API 服务
    await master.start()

    if not master.is_connected:
        print("✗ 连接墨子服务器失败")
        return

    print("\n✓ Master 已启动")
    print("  - 墨子连接: 127.0.0.1:6060")
    print(f"  - API 服务: 0.0.0.0:{master.api_port}")
    print("\n其他节点可以通过以下方式连接：")
    print(f"  client = MoziServer('{master.server_ip}', {master.api_port}, mode='client')")
    print("  # Client 会直接连接到 Master 的代理端口，使用完全相同的 API")

    # 加载想定
    print("\n加载想定中...")
    scenario = await master.load_scenario()
    print(f"✓ 想定加载成功: {scenario.get_title()}")

    # 初始化态势
    print("\n初始化态势...")
    await master.init_situation(scenario, app_mode=1)  # 1 = local windows train mode
    print("✓ 态势初始化完成")

    sides = scenario.sides
    print(f"想定中共有 {len(sides)} 个参演方:")
    for side_name, side in sides.items():
        print(f"  - {side.name} ({side_name[:8]}...)")

    # 获取美国信息
    red_side = scenario.get_side_by_name("美国")
    if red_side:
        aircrafts = red_side.get_aircrafts()
        print(f"\n美国飞机数量: {len(aircrafts)}")
        for guid, aircraft in list(aircrafts.items())[:3]:  # 只显示前3个
            print(f"  - {aircraft.name} ({guid[:8]}...)")

    # 推演循环（示例）
    print("\n开始推演...")
    for step in range(3):
        print(f"\n第 {step + 1} 步推演...")
        await master.run_grpc_simulate()

        # 更新态势
        changes = await master.update_situation(scenario)
        print(f"  态势变化: 新增 {len(changes.get('added', {}))} 个单元")

        await asyncio.sleep(2)

    print("\n✓ 推演完成")
    print("\nMaster 节点保持运行，等待 Client 连接...")
    print("按 Ctrl+C 退出")

    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭 Master 节点...")
        await master.close()
        print("✓ Master 节点已关闭")


if __name__ == "__main__":
    asyncio.run(main())
