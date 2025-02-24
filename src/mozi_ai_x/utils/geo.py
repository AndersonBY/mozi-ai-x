"""
地理信息库
"""

import bisect
from collections import namedtuple
from typing import TypedDict, TYPE_CHECKING
from math import radians, cos, sin, asin, sqrt, degrees, atan2, tan

import numpy as np


if TYPE_CHECKING:
    from mozi_ai_x.simulation.side import CSide
    from mozi_ai_x.simulation.reference_point import CReferencePoint


PI = 3.1415926535897932
degree2radian = PI / 180.0
NM2KM = 1.852  # 海里转千米
EARTH_RADIUS = 6371137  # 地球平均半径


class GeoPoint(TypedDict):
    latitude: float
    longitude: float


def get_end_point(geopoint1: tuple[float, float], distance: float, bearing: float) -> tuple[float, float]:
    """
    获取终点经纬度

    Args:
        geopoint1: 起点的经纬度
        distance: 距离
        bearing: 起点到终点的方位角

    Returns:
        tuple[float, float]: 终点经纬度
    """
    distance = distance * 1000
    lat1 = geopoint1[0] * degree2radian
    lon1 = geopoint1[1] * degree2radian
    brng = bearing * degree2radian
    lat2 = asin(sin(lat1) * cos(distance / EARTH_RADIUS) + cos(lat1) * sin(distance / EARTH_RADIUS) * cos(brng))
    lon2 = lon1 + atan2(
        sin(brng) * sin(distance / EARTH_RADIUS) * cos(lat1),
        cos(distance / EARTH_RADIUS) - sin(lat1) * sin(lat2),
    )
    lat2 = degrees(lat2)
    lon2 = degrees(lon2)
    return lat2, lon2


def get_horizontal_distance(
    geopoint1: tuple[float, float] | tuple[float, float, float],
    geopoint2: tuple[float, float] | tuple[float, float, float],
) -> float:
    """
    求地面两点的水平距离   Haversine公式

    Args:
        geopoint1: tuple, (lat, lon) | (lat, lon, alt), 例：(40.9, 140.0) | (40.9, 140.0, 560.8)
        geopoint2: tuple, (lat, lon) | (lat, lon, alt), 例：(40.9, 142.0) | (40.9, 142.0, 4560.8)

    Returns:
        float: KM
    """
    lat1 = geopoint1[0] * degree2radian
    lon1 = geopoint1[1] * degree2radian
    lat2 = geopoint2[0] * degree2radian
    lon2 = geopoint2[1] * degree2radian

    difference = lat1 - lat2
    mdifference = lon1 - lon2
    distance = 2 * asin(sqrt(pow(sin(difference / 2), 2) + cos(lat1) * cos(lat2) * pow(sin(mdifference / 2), 2)))
    distance = distance * EARTH_RADIUS / 1000
    return distance


def get_slant_distance(geopoint1: tuple[float, float, float], geopoint2: tuple[float, float, float]) -> float:
    """
    获取三维直线距离, 点高需为海拔高度

    Args:
        geopoint1: tuple, (lat, lon, alt), 例：(40.9, 140.0, 560.8)
        geopoint2: tuple, (lat, lon, alt), 例：(40.9, 142.0, 4560.8)

    Returns:
        float: KM
    """
    hd = get_horizontal_distance(geopoint1, geopoint2)
    delta_alt = geopoint1[2] - geopoint2[2]
    return get_range(hd, delta_alt)


def get_range(range_km: float, delta_alt: float) -> float:
    """
    获取直线距离

    Args:
        range_km: float, 水平距离 KM
        delta_alt: float, 垂直距离 m

    Returns:
        float: KM
    """
    range_km *= 1000.0
    return sqrt((range_km * range_km + delta_alt * delta_alt)) / 1000.0


def normal_angle(angle: float):
    """
    将任意角度标准化到[0, 360)范围内

    Args:
        angle: float, 输入角度

    Returns:
        float: 标准化后的角度 [0, 360)
    """
    return angle % 360


def get_azimuth(point1: tuple[float, float], point2: tuple[float, float]) -> float:
    """
    获取point1 指向 point2 的方位角

    Args:
        point1: tuple, (lat, lon), 例：(40.9, 140.0)
        point2: tuple, (lat, lon), 例：(40.9, 142.0)

    Returns:
        float: 角度 0-360, 正北: 0, 正东: 90, 顺时针旋转, 正西: 270
    """
    lat1 = point1[0] * degree2radian
    lon1 = point1[1] * degree2radian
    lat2 = point2[0] * degree2radian
    lon2 = point2[1] * degree2radian
    azimuth = 180 * atan2(sin(lon2 - lon1), tan(lat2) * cos(lat1) - sin(lat1) * cos(lon2 - lon1)) / PI
    return normal_angle(azimuth)


def get_point_with_point_bearing_distance(
    latitude: float, longitude: float, bearing: float, distance: float
) -> GeoPoint:
    """
    一直一点求沿某一方向一段距离的点

    Args:
        latitude: 纬度
        longitude: 经度
        bearing: 朝向角
        distance: 距离

    Returns:
        GeoPoint: 包含经纬度的字典
    """
    # pylog.info("lat:%s lon:%s bearing:%s distance:%s" % (lat, lon, bearing, distance))
    radiusEarthKilometres = 3440
    initialBearingRadians = radians(bearing)
    disRatio = distance / radiusEarthKilometres
    distRatioSine = sin(disRatio)
    distRatioCosine = cos(disRatio)
    startLatRad = radians(latitude)
    startLonRad = radians(longitude)
    startLatCos = cos(startLatRad)
    startLatSin = sin(startLatRad)
    endLatRads = asin((startLatSin * distRatioCosine) + (startLatCos * distRatioSine * cos(initialBearingRadians)))
    endLonRads = startLonRad + atan2(
        sin(initialBearingRadians) * distRatioSine * startLatCos, distRatioCosine - startLatSin * sin(endLatRads)
    )
    return GeoPoint(latitude=degrees(endLatRads), longitude=degrees(endLonRads))


def get_two_point_distance(longitude1: float, latitude1: float, longitude2: float, latitude2: float) -> float:
    """
    获得两点间的距离

    Args:
        longitude1: 1点的经度
        latitude1: 1点的纬度
        longitude2: 2点的经度
        latitude2: 2点的纬度

    Returns:
    """
    longitude1, latitude1, longitude2, latitude2 = map(radians, [longitude1, latitude1, longitude2, latitude2])
    dlon = longitude2 - longitude1
    dlat = latitude2 - latitude1
    a = sin(dlat / 2) ** 2 + cos(latitude1) * cos(latitude2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r * 1000


def get_degree(latitude1: float, longitude1: float, latitude2: float, longitude2: float) -> float:
    """
    获得朝向与正北方向的夹角

    Args:
        latitude1: A点的纬度
        longitude1: A点的经度
        latitude2: B点的纬度
        longitude2: B点的经度

    Returns:
    """
    radLatA = radians(latitude1)
    radLonA = radians(longitude1)
    radLatB = radians(latitude2)
    radLonB = radians(longitude2)
    dLon = radLonB - radLonA
    y = sin(dLon) * cos(radLatB)
    x = cos(radLatA) * sin(radLatB) - sin(radLatA) * cos(radLatB) * cos(dLon)
    brng = degrees(atan2(y, x))
    brng = (brng + 360) % 360
    return brng


def plot_square(num: int, side: "CSide", rp1: tuple[float, float], rp2: tuple[float, float]) -> list[GeoPoint]:
    """
    根据对角线上的两个点经纬度，做一个正方形，并且平分成num个小正方形

    Args:
        num: 一行（一列）小正方形的数量，行列数量都是num
        rp1: 左上顶点1的经纬度  rp1=(lat1,lon1) lat维度  lon经度
        rp2: 右下顶点2的经纬度

    Returns:
        list[GeoPoint]: 包含经纬度的字典
    """
    Referpoint = namedtuple("Referpoint", ["name", "lat", "lon"])
    gap = rp1[0] - rp2[0]
    inter = gap / num
    point_list = []

    for i in range(num):
        k = 1
        for j in range(num):
            point = Referpoint("rp" + str(i) + str(j), rp1[0] - i * inter, rp1[1] + k * inter)
            # f1.name = 'rp' + str(i) + str(j)
            point = side.add_reference_point(side.name, point.lat, point.lon)
            k += 1
            point_list.append(point)
    return point_list


def motion_dirc(
    point_list: list["CReferencePoint"],
    rp1: tuple[float, float],
    rp2: tuple[float, float],
    rp3: tuple[float, float],
    rp4: tuple[float, float],
) -> dict[str, dict[int, list[str]]]:
    """
    rp1, rp2, rp3, rp4 顺时针正方形的参考点
    给定4一个点的名称，我需要根据plot_square画出
    朝前：从下往上3个正方形，顺时针标记参考点名称
    朝上：下下往上3个正方形，顺时针标记参考点名称
    朝后：下往上3个正方形，顺时针标记参考点名称

    Returns:
        dict[str, dict[int, list[str]]]: 包含运动方向和参考点名称的字典
    """
    point_name = []
    for point in point_list:
        point_name.append(point.name)

    # 从输入元组中提取经纬度
    rp1_pos = (rp1[0], rp1[1])
    rp2_pos = (rp2[0], rp2[1])
    rp3_pos = (rp3[0], rp3[1])
    rp4_pos = (rp4[0], rp4[1])

    # 创建带名称的参考点
    Referpoint = namedtuple("Referpoint", ["name", "lat", "lon"])
    rp1_ref = Referpoint("rp01", *rp1_pos)
    rp2_ref = Referpoint("rp02", *rp2_pos)
    rp3_ref = Referpoint("rp03", *rp3_pos)
    rp4_ref = Referpoint("rp04", *rp4_pos)

    rp1_num = int(rp1_ref.name[2:])
    rp2_num = int(rp2_ref.name[2:])
    rp3_num = int(rp3_ref.name[2:])
    rp4_num = int(rp4_ref.name[2:])
    rp0_num = int(rp1_num) - 11  # rp1点向左上的对角点
    rp5_num = int(rp3_num) + 11  # rp3点向右下的对角点

    forward1 = [rp4_ref.name, rp3_ref.name, "rp" + str(rp3_num + 10), "rp" + str(rp4_num + 10)]
    forward2 = [rp3_ref.name, "rp" + str(rp3_num + 1), "rp" + str(rp5_num), "rp" + str(rp3_num + 10)]
    forward3 = [rp2_ref.name, "rp" + str(rp2_num + 1), "rp" + str(rp3_num + 1), rp3_ref.name]

    middle1 = ["rp" + str(rp4_num - 1), rp4_ref.name, "rp" + str(rp4_num + 10), "rp" + str(rp4_num + 9)]
    middle2 = [rp1_ref.name, rp2_ref.name, rp3_ref.name, rp4_ref.name]
    middle3 = ["rp" + str(rp2_num - 10), "rp" + str(rp2_num - 9), "rp" + str(rp2_num + 1), rp2_ref.name]

    backward1 = ["rp" + str(rp1_num - 1), rp1_ref.name, rp4_ref.name, "rp" + str(rp4_num - 1)]
    backward2 = ["rp" + str(rp0_num), "rp" + str(rp0_num + 1), rp1_ref.name, "rp" + str(rp1_num - 1)]
    backward3 = ["rp" + str(rp0_num + 1), "rp" + str(rp0_num + 2), rp2_ref.name, rp1_ref.name]

    dic1 = {1: forward1, 2: forward2, 3: forward3}
    dic2 = {1: middle1, 2: middle2, 3: middle3}
    dic3 = {1: backward1, 2: backward2, 3: backward3}

    motion_dict = {"forward": dic1, "middle": dic2, "backward": dic3}
    for k, v in motion_dict.items():
        for point, j in v.items():
            for index, name in enumerate(j):
                if len(name[2:]) == 1:
                    s = name[0:2] + "0" + str(name[2:])
                    del j[index]
                    j.insert(index, s)
        for point, j in v.items():
            # if any(j) not in point_name:
            if not set(point_name) > set(j):
                j = [None, None, None, None]
                v[point] = j
                motion_dict[k] = v
    return motion_dict


def get_cell_middle(
    num: int, rp1: tuple[float, float], rp2: tuple[float, float], rp_find: tuple[float, float]
) -> tuple[float, float]:
    """
    功能：给出画的网格，然后给一个坐标，返回这个坐标所在表格的中心点坐标

    Args:
        num: 一行（一列）小矩形的数量，行列数量都是num，总共 num*num个小矩形
        rp1: 左上顶点1的经纬度  rp1=(lat1,lon1) lat纬度  lon经度
        rp2: 右下顶点2的经纬度
        rp_find: 要查找的坐标 rp_find=(lat,lon)

    Returns:
        tuple[float, float]: 包含经纬度的字典
    """
    # if rp2[0] < rp1[0]: 经纬度大小，南北纬，东西经这个要怎么考虑
    ax = np.linspace(rp2[0], rp1[0], num + 1)
    col = np.linspace(rp1[1], rp2[1], num + 1)
    id_ax = bisect.bisect(ax, rp_find[0])  # 返回rp_find坐标点纬度在维度np.array的索引
    id_col = bisect.bisect(col, rp_find[1])
    lat = ax[id_ax - 1] + (ax[id_ax] - ax[id_ax - 1]) / 2
    lon = col[id_col - 1] + (col[id_col] - col[id_col - 1]) / 2
    return lat, lon
