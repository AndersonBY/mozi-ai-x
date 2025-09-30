"""
分布式 Mozi 使用示例 - Client 节点（蓝方）

这个示例展示蓝方节点如何独立运行，与红方节点并行工作
"""

import asyncio
from mozi_ai_x import MoziServer


async def main():
    # 创建蓝方 Client 节点
    client = MoziServer(
        server_ip="127.0.0.1",  # Master 节点的 IP（需要替换为实际 IP）
        server_port=6061,  # Master 的 API 端口
        mode="client",
    )

    print("=" * 60)
    print("蓝方 Client 节点启动中...")
    print("=" * 60)

    # 连接到 Master
    await client.start()

    if not client.is_connected:
        print("✗ 连接 Master 节点失败")
        return

    print(f"✓ 已连接到 Master: {client.server_ip}:{client.server_port}")

    # 获取想定
    scenario = await client.get_scenario()
    print(f"✓ 想定: {scenario.get_title()}")

    # 获取蓝方
    blue_side = scenario.get_side_by_name("蓝方")
    if not blue_side:
        print("✗ 未找到蓝方")
        return

    print(f"\n✓ 控制方: {blue_side.name}")

    # 获取蓝方单元
    ships = blue_side.get_ships()
    print(f"\n蓝方舰船数量: {len(ships)}")

    for ship in list(ships.values())[:3]:
        print(f"\n舰船: {ship.name}")
        print(f"  位置: ({ship.latitude:.2f}, {ship.longitude:.2f})")

    # 获取蓝方目标（情报）
    contacts = blue_side.get_contacts()
    print(f"\n蓝方发现的目标数量: {len(contacts)}")

    for contact in list(contacts.values())[:3]:
        print(f"\n目标: {contact.name}")

    print("\n\n✓ 蓝方 Client 节点运行正常")
    print("按 Ctrl+C 退出")

    try:
        while True:
            await asyncio.sleep(10)
    except KeyboardInterrupt:
        print("\n正在断开连接...")
        await client.close()
        print("✓ 蓝方节点已关闭")


if __name__ == "__main__":
    asyncio.run(main())
