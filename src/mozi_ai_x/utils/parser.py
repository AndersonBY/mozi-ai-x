import re

from ..database import default_db


guid_list_pattern = re.compile(r"\[\d\] = '([0-9a-z-^=]+)'")
mission_guid_pattern = re.compile(r"mission {\r\n guid = '([a-z0-9-]+)',", re.M | re.S)


def mission_guid_parser(mission_return_str: str) -> str | None:
    """
    通过创建任务或获取任务详情返回的字符串，获取任务guid

    Args:
        mission_return_str (str): 创建任务或获取任务详情返回的字符串,  mission {guid = 'fdbd661d-2c96-46fb-8e2d-ea0738764604'

    Returns:
        str | None: 任务guid
    """
    m_ret = mission_guid_pattern.match(mission_return_str)
    if m_ret is not None:
        guid = m_ret.group(1)
        return guid
    return None


def guid_list_parser(guids: str) -> list[str]:
    """
    返回的guid列表字符串解析器

    Args:
        guids (str): 获取的guid列表，例：'{ [1] = \'8cd0c4d5-4d58-408a-99fd-4a75dfa82364\',
                                                    [2] = \'ef9ac5b8-008a-4042-bbdb-d6bafda6dfb3\' }'

    Returns:
        list[str]: guid列表
    """
    guid_list = []
    for match_guid in guid_list_pattern.finditer(guids):
        guid_list.append(match_guid.group(1))
    return guid_list


def parse_weapons_record(weapon_ratio: str) -> list[dict]:
    """
    返回武器的精简信息，适用于挂架，挂载，弹药库的武器解析

    Args:
        weapon_ratio: 武器比例

    Returns:
        武器的精简信息
    """
    info = []
    weapon_name_type = {}
    w_set = set()
    if "@" in weapon_ratio:
        load_ratios = weapon_ratio.split("@")
        for record in load_ratios:
            record_v = record.split("$")
            w_id = int(record_v[1])
            info.append(
                {
                    "wpn_guid": record_v[0],
                    "wpn_dbid": w_id,
                    "wpn_current": int(record_v[2]),
                    "wpn_maxcap": int(record_v[3]),
                }
            )
            w_set.add(w_id)
    else:
        if "$" in weapon_ratio:
            record_v = weapon_ratio.split("$")
            w_id = int(record_v[1])
            info.append(
                {
                    "wpn_guid": record_v[0],
                    "wpn_dbid": w_id,
                    "wpn_current": int(record_v[2]),
                    "wpn_maxcap": int(record_v[3]),
                }
            )
            w_set.add(w_id)
    if info:
        for wid in w_set:
            weapon_name_type[wid] = default_db.get_weapon_name_type(wid)
        for w_info in info:
            name_type = weapon_name_type[w_info["wpn_dbid"]]
            w_info["wpn_name"] = name_type[0]
            w_info["wpn_type"] = name_type[1]
    return info
