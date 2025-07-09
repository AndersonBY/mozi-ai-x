from pathlib import Path


class LuaScriptLoader:
    """用于加载和缓存 Lua 脚本文件的类"""

    def __init__(self, lua_path: str | Path = "lua"):
        self.lua_path = lua_path
        self._cache = {}
        self._script_files = {
            "table2json": "table_to_json.lua",
            "mission": "lua_mission.lua",
            "common": "lua_common_function.lua",
            "contacts_all": "contacts_all.lua",
            "contact": "contact.lua",
            "units_all": "units_all.lua",
            "unit": "unit.lua",
            "situation": "situation.lua",
            "detect": "detect.lua",
        }

    def _load_script(self, script_name):
        """
        从文件加载指定的 Lua 脚本内容

        Args:
            script_name (str): 脚本名称

        Returns:
            str: 脚本内容

        Raises:
            ValueError: 如果脚本名称未知
            FileNotFoundError: 如果脚本文件不存在
        """
        if script_name not in self._script_files:
            raise ValueError(f"Unknown script name: {script_name}")

        if script_name not in self._cache:
            file_path = Path(self.lua_path) / self._script_files[script_name]
            with open(file_path, encoding="ascii") as fp:
                self._cache[script_name] = fp.read()

        return self._cache[script_name]

    @property
    def table2json(self):
        """获取用于将 Lua table 转换为 JSON 的脚本"""
        return self._load_script("table2json")

    @property
    def mission(self):
        """获取用于解析任务详细信息的脚本"""
        return self._load_script("mission")

    @property
    def common(self):
        """获取通用函数脚本，用于获取所有实体和情报实体"""
        return self._load_script("common")

    @property
    def contacts_all(self):
        """获取用于获取所有情报实体的脚本"""
        return self._load_script("contacts_all")

    @property
    def contact(self):
        """获取用于获取单个情报实体的脚本"""
        return self._load_script("contact")

    @property
    def units_all(self):
        """获取用于获取所有本方实体的脚本"""
        return self._load_script("units_all")

    @property
    def unit(self):
        """获取用于获取单个本方实体的脚本"""
        return self._load_script("unit")

    @property
    def situation(self):
        """获取用于获取战场态势的脚本"""
        return self._load_script("situation")

    @property
    def detect(self):
        """获取用于获取探测区域的脚本"""
        return self._load_script("detect")


# 创建单例实例供其他模块使用
lua_scripts = LuaScriptLoader()
