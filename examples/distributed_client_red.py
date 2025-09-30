"""
分布式 Mozi 使用示例 - Client 节点（美国）

这个示例展示如何在 Client 模式下运行：
1. 连接到 Master 节点
2. 获取想定信息
3. 控制美国单元
4. 所有操作自动通过 Master 代理到墨子
"""

import asyncio
from mozi_ai_x import MoziServer


async def main():
    # 创建 Client 节点
    # Client 连接到 Master，通过代理访问墨子
    client = MoziServer(
        server_ip="127.0.0.1",  # Master 节点的 IP（需要替换为实际 IP）
        server_port=6061,  # Master 的 API 端口
        mode="client",  # 指定为 Client 模式
    )

    print("=" * 60)
    print("美国 Client 节点启动中...")
    print("=" * 60)

    # 连接到 Master
    await client.start()

    if not client.is_connected:
        print("✗ 连接 Master 节点失败")
        print("  请确保 Master 节点已启动并可访问")
        return

    print(f"✓ 已连接到 Master: {client.server_ip}:{client.server_port}")

    # Client 不需要重新加载想定，直接获取 Master 的想定信息即可
    print("\n获取想定信息...")

    # 通过代理获取当前想定信息
    print("✓ 已连接到代理，可以执行命令")

    # 初始化态势（获取完整态势信息）
    print("\n获取态势信息...")
    response = await client.send_and_recv("GetAllState")
    print("✓ 态势信息获取完成")

    # 创建本地 scenario 对象并解析态势数据
    from mozi_ai_x.simulation.scenario import CScenario

    scenario = CScenario(client)
    client.scenario = scenario

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

    sides = scenario.sides
    print(f"想定中共有 {len(sides)} 个参演方:")
    for side_name, side in sides.items():
        print(f"  - {side.name} ({side_name[:8]}...)")

    # 获取美国
    red_side = scenario.get_side_by_name("美国")
    if not red_side:
        print("✗ 未找到美国")
        return

    print(f"\n✓ 控制方: {red_side.name}")

    # 获取美国飞机
    aircrafts = red_side.get_aircrafts()
    print(f"\n美国飞机数量: {len(aircrafts)}")

    for guid, aircraft in list(aircrafts.items())[:5]:  # 显示前5个
        print("\n飞机信息:")
        print(f"  名称: {aircraft.name}")
        print(f"  GUID: {guid}")
        print(f"  位置: ({aircraft.latitude:.2f}, {aircraft.longitude:.2f})")
        print(f"  高度: {aircraft.altitude} 米")

        # 示例：设置飞机期望速度（命令会自动通过 Master 代理）
        try:
            # await aircraft.set_desired_speed(500)
            # print(f"  ✓ 已设置期望速度: 500 km/h")
            print("  (可以通过 aircraft.set_desired_speed(500) 设置速度)")
        except Exception as e:
            print(f"  ✗ 设置速度失败: {e}")

    # 示例：获取单元详细信息（也会通过 Master 代理）
    if aircrafts:
        first_guid = list(aircrafts.keys())[0]
        first_aircraft = aircrafts[first_guid]

        print(f"\n\n获取 {first_aircraft.name} 的详细信息...")
        try:
            # 这些方法调用都会自动通过 Master 代理到墨子
            summary_info = await first_aircraft.get_summary_info()
            print(f"  总结信息: {summary_info}%")

            sensors = await first_aircraft.get_sensors()
            print(f"  传感器数量: {len(sensors)}")

            print("  (所有 API 调用都会自动通过 Master 代理)")
        except Exception as e:
            print(f"  ✗ 获取信息失败: {e}")

    contacts = red_side.get_contacts()
    print(f"\n美国接敌情况: {contacts}")

    print("\n\n✓ Client 节点运行正常")
    print("  API 完全一致，无需修改代码")
    print("  所有操作自动通过 Master 代理")

    # 持续监控（可选）
    print("\n持续监控中... 按 Ctrl+C 退出")
    try:
        while True:
            # 定期更新信息
            await asyncio.sleep(5)

            # 重新获取想定（获取最新状态）
            scenario = await client.get_scenario()
            red_side = scenario.get_side_by_name("美国")
            if red_side:
                aircrafts = red_side.get_aircrafts()
                print(f"\r当前美国飞机数量: {len(aircrafts)}", end="", flush=True)

    except KeyboardInterrupt:
        print("\n\n正在断开连接...")
        await client.close()
        print("✓ Client 节点已关闭")


if __name__ == "__main__":
    asyncio.run(main())
