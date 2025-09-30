"""
单机模式使用示例（向后兼容）

展示传统的单机使用方式，与分布式模式前完全兼容
不指定 mode 参数就是 standalone 模式
"""

import asyncio
from mozi_ai_x import MoziServer


async def main():
    # 传统单机模式（默认）
    server = MoziServer(
        server_ip="127.0.0.1",
        server_port=6060,
        scenario_path="test.scen",
        # mode="standalone",  # 默认就是 standalone，可以不指定
    )

    print("=" * 60)
    print("单机模式（传统用法）")
    print("=" * 60)

    # 启动并连接墨子
    await server.start()

    if not server.is_connected:
        print("✗ 连接墨子服务器失败")
        return

    print("✓ 已连接到墨子服务器")

    # 加载想定
    scenario = await server.load_scenario()
    print(f"✓ 想定: {scenario.get_title()}")

    # 初始化态势
    print("\n初始化态势...")
    await server.init_situation(scenario, app_mode=1)
    print("✓ 态势初始化完成")

    # 获取红方
    red_side = scenario.get_side_by_name("红方")
    if red_side:
        aircrafts = red_side.get_aircrafts()
        print(f"\n红方飞机数量: {len(aircrafts)}")

        for aircraft in list(aircrafts.values())[:3]:
            print(f"  - {aircraft.name}")

    # 推演
    print("\n开始推演...")
    for step in range(3):
        print(f"  第 {step + 1} 步...")
        await server.run_grpc_simulate()
        await asyncio.sleep(1)

    print("\n✓ 完成")


if __name__ == "__main__":
    asyncio.run(main())
