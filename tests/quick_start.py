# @Author: Bi Ying
# @Date:   2025-02-15 12:07:40
import asyncio
from mozi_ai_x.simulation.server import MoziServer
from mozi_ai_x.simulation.scenario import CScenario


async def main():
    # 连接到墨子服务器 (需要先启动墨子服务端程序)
    server = MoziServer(
        "127.0.0.1",
        6060,  # 替换为实际的 IP 和端口
        scenario_path="heli_anti_sub.scen",
    )
    await server.start()

    if server.is_connected:
        # 加载想定 (替换为你的想定文件路径)
        scenario: CScenario = await server.load_scenario()

        print(f"想定加载成功: {scenario.get_title()}")

        # 获取美国海军
        red_side = scenario.get_side_by_name("美国海军")

        if red_side:
            # 获取美国海军所有飞机
            aircrafts = red_side.get_aircrafts()
            print(f"美国海军飞机数量: {len(aircrafts)}")

            for guid, aircraft in aircrafts.items():
                # 示例：获取飞机信息
                print(f"  飞机: {aircraft.name}, GUID: {guid}, 经度: {aircraft.longitude}, 纬度: {aircraft.latitude}")

                # 示例：设置飞机期望速度 (单位：千米/小时)
                # await aircraft.set_desired_speed(500)

        else:
            print("未找到美国海军。")

    else:
        print("无法连接到墨子服务器。")

    await server.close()


# 运行
asyncio.run(main())
