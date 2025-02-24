import re
from datetime import datetime

import numpy as np


def np3_to_np1(np_3: np.ndarray | None) -> np.ndarray | None:
    """
    三维0/1数组转换成1维uint8的数组

    Args:
        np_3: 三维0/1数组

    Returns:
        1维uint8的数组
    """
    if np_3 is None:
        return None
    num = np_3.size // 8
    if np_3.size % 8 > 0:
        num += 1
    np_1 = np.zeros(num, dtype=np.uint8)

    (alt_num, lat_num, lon_num) = np_3.shape
    for x in range(alt_num):
        for y in range(lat_num):
            for z in range(lon_num):
                if np_3[x][y][z] > 0:
                    n_num = x * lat_num * lon_num + y * lon_num + z
                    index = n_num // 8
                    bit = n_num % 8
                    np_1[index] = np_1[index] | (pow(2, bit))

    return np_1


def np1_to_np3(np_1: np.ndarray | None, shape: tuple[int, int, int] | None) -> np.ndarray | None:
    """
    1维uint8的数组转换成三维0/1数组

    Args:
        np_1: 1维uint8的数组
        shape: tuple(num1, num2, num3)三维数组形状

    Returns:
        三维0/1数组
    """
    if np_1 is None or shape is None:
        return None

    (alt_num, lat_num, lon_num) = shape

    if np_1.size * 8 < alt_num * lat_num * lon_num:
        return None

    np_3 = np.zeros((alt_num, lat_num, lon_num), dtype=np.uint8)
    for x in range(alt_num):
        for y in range(lat_num):
            for z in range(lon_num):
                n_num = x * lat_num * lon_num + y * lon_num + z
                index = n_num // 8
                bit = n_num % 8
                np_3[x][y][z] = (np_1[index] >> bit) & 1

    return np_3


def get_scenario_time(time_stamp: int) -> str:
    """
    获取当前想定时间，字符串格式

    Args:
        time_stamp: 时间戳(秒)

    Returns:
        格式化的时间字符串 YYYY/MM/DD HH:MM:SS
    """
    return datetime.fromtimestamp(time_stamp).strftime("%Y/%m/%d %H:%M:%S")


def get_sides(situation_str: str) -> dict[str, str]:
    """
    返回推演方 guid和推演方明

    Args:
        situation_str:

    Returns:
        推演方 guid和推演方明
    """
    guid2name = {}
    side_pat = re.compile(r'{"ClassName":"CSide","strName":"([^,]+)","strGuid":"([a-z0-9-]+)')
    for re_ret in side_pat.findall(situation_str):
        guid2name[re_ret[1]] = re_ret[0]
    return guid2name
