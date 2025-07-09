import os
import sqlite3
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, cast, LiteralString

# 常量定义
NM2KM = 1.852  # 海里转千米
FEET2M = 0.3048  # 英尺转米
WEAPONS_ASSIST = {1001, 2005, 2006, 2007, 2008, 3001, 3002, 3003, 3004, 4003, 4101, 6001, 7001, 9001, 9002, 9003}


class DBType(str, Enum):
    """数据库类型枚举"""

    SQLITE = "sqlite"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"


@dataclass
class DBConfig:
    """数据库配置类"""

    db_type: DBType
    host: str
    port: int
    database: str
    username: str
    password: str

    @classmethod
    def from_env(cls) -> "DBConfig":
        """从环境变量读取数据库配置"""
        return cls(
            db_type=DBType(os.environ.get("MOZI_DB_TYPE", DBType.SQLITE)),
            host=os.environ.get("MOZI_DB_HOST", "localhost"),
            port=int(os.environ.get("MOZI_DB_PORT", "3306")),
            database=os.environ.get("MOZI_DB_NAME", str(Path("./data/modeldata.db").absolute())),
            username=os.environ.get("MOZI_DB_USER", "root"),
            password=os.environ.get("MOZI_DB_PASSWORD", ""),
        )


@dataclass
class WeaponInfo:
    """武器信息数据类"""

    id: int
    name: str
    type: int
    air_range_min: float
    air_range_max: float
    land_range_min: float
    land_range_max: float
    launch_speed_max: float
    launch_speed_min: float
    launch_altitude_min: float
    launch_altitude_max: float
    target_speed_max: float
    target_speed_min: float
    target_altitude_max: float
    target_altitude_min: float

    @classmethod
    def from_db_row(cls, row: tuple) -> "WeaponInfo":
        """从数据库行创建WeaponInfo实例"""
        return cls(
            id=row[0],
            name=row[1],
            type=row[2],
            air_range_min=row[3] * NM2KM,
            air_range_max=row[4] * NM2KM,
            land_range_min=row[5] * NM2KM,
            land_range_max=row[6] * NM2KM,
            launch_speed_max=row[7] * NM2KM,
            launch_speed_min=row[8] * NM2KM,
            launch_altitude_min=row[9],
            launch_altitude_max=row[10],
            target_speed_max=row[11] * NM2KM,
            target_speed_min=row[12] * NM2KM,
            target_altitude_max=row[13],
            target_altitude_min=row[14],
        )


@dataclass
class ModelInfo:
    """模型信息数据类"""

    name: str
    type: int


class DatabaseBackend(ABC):
    """数据库后端抽象基类"""

    def __init__(self, config: DBConfig):
        self.config = config

    @abstractmethod
    def connect(self) -> Any:
        """建立数据库连接"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """关闭数据库连接"""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: tuple = ()) -> Any:
        """执行查询"""
        pass


class SQLiteBackend(DatabaseBackend):
    """SQLite数据库后端实现"""

    def __init__(self, config: DBConfig):
        super().__init__(config)
        self._conn: sqlite3.Connection | None = None
        self._cursor: sqlite3.Cursor | None = None

    def connect(self) -> sqlite3.Connection:
        if not self._conn:
            self._conn = sqlite3.connect(self.config.database)
            self._cursor = self._conn.cursor()
        return self._conn

    def disconnect(self) -> None:
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()
            self._conn = None
            self._cursor = None

    def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        if not self._cursor:
            self.connect()
        assert self._cursor is not None  # 帮助类型检查器理解
        return self._cursor.execute(query, params)


# 可选数据库后端


class MySQLBackend(DatabaseBackend):
    """MySQL数据库后端实现"""

    def __init__(self, config: DBConfig):
        try:
            import mysql.connector  # noqa: F401
        except ImportError as e:
            raise ImportError("MySQL support requires mysql-connector-python package") from e
        super().__init__(config)
        self._conn = None
        self._cursor = None

    def connect(self) -> Any:
        try:
            import mysql.connector as mysql_db
        except ImportError as e:
            raise ImportError("MySQL support requires mysql-connector-python package") from e
        if not self._conn:
            self._conn = mysql_db.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
            )
            self._cursor = self._conn.cursor()
        return self._conn

    def disconnect(self) -> None:
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()
            self._conn = None
            self._cursor = None

    def execute_query(self, query: str, params: tuple = ()) -> Any:
        if not self._cursor:
            self.connect()
        assert self._cursor is not None
        return self._cursor.execute(query, params)


class PostgreSQLBackend(DatabaseBackend):
    """PostgreSQL数据库后端实现"""

    def __init__(self, config: DBConfig):
        try:
            import psycopg  # noqa: F401
        except ImportError as e:
            raise ImportError("PostgreSQL support requires psycopg package") from e
        super().__init__(config)
        self._conn = None
        self._cursor = None

    def connect(self) -> Any:
        try:
            from psycopg.connection import Connection  # noqa: F401
        except ImportError as e:
            raise ImportError("PostgreSQL support requires psycopg package") from e
        if not self._conn:
            self._conn = Connection.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
            )
            self._cursor = self._conn.cursor()
        return self._conn

    def disconnect(self) -> None:
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()
            self._conn = None
            self._cursor = None

    def execute_query(self, query: str, params: tuple = ()) -> Any:
        try:
            from psycopg.sql import SQL
        except ImportError as e:
            raise ImportError("PostgreSQL support requires psycopg package") from e
        if not self._cursor:
            self.connect()
        assert self._cursor is not None
        return self._cursor.execute(SQL(cast(LiteralString, query)), params)


def create_backend(config: DBConfig) -> DatabaseBackend:
    """根据配置创建对应的数据库后端"""
    backends = {DBType.SQLITE: SQLiteBackend, DBType.MYSQL: MySQLBackend, DBType.POSTGRESQL: PostgreSQLBackend}

    backend_class = backends.get(config.db_type)
    if not backend_class:
        raise ValueError(f"Unsupported database type: {config.db_type}")

    return backend_class(config)


class ModelDatabase:
    """模型数据库管理类"""

    def __init__(self, backend: DatabaseBackend):
        self.backend = backend

    @classmethod
    def from_env(cls) -> "ModelDatabase":
        """从环境变量创建数据库实例"""
        config = DBConfig.from_env()
        backend = create_backend(config)
        return cls(backend)

    @contextmanager
    def connection(self):
        """数据库连接上下文管理器"""
        try:
            self.backend.connect()
            yield
        finally:
            self.backend.disconnect()

    def get_weapon_info(self, weapon_id: int) -> WeaponInfo | None:
        """获取武器信息"""
        query = """
            SELECT ID, Name, Type, AirRangeMin, AirRangeMax, LandRangeMin, LandRangeMax,
                   LaunchSpeedMax, LaunchSpeedMin, LaunchAltitudeMin_ASL, LaunchAltitudeMax_ASL,
                   TargetSpeedMax, TargetSpeedMin, TargetAltitudeMax, TargetAltitudeMin
            FROM dataweapon WHERE ID = ?
        """
        result = self.backend.execute_query(query, (weapon_id,)).fetchone()
        return WeaponInfo.from_db_row(result) if result else None

    def get_weapon_name_type(self, weapon_id: int) -> tuple[str, int]:
        """获取武器名称和类型"""
        query = "SELECT Name, Type FROM dataweapon WHERE ID = ?"
        result = self.backend.execute_query(query, (weapon_id,)).fetchone()
        return (result[0], result[1]) if result else ("", 0)

    def get_weapon_type(self, weapon_id: int) -> int:
        """获取武器类型"""
        query = "SELECT Type FROM dataweapon WHERE ID = ?"
        result = self.backend.execute_query(query, (weapon_id,)).fetchone()
        return result[0] if result else 0

    def check_weapon_attack(self, weapon_id: int) -> bool:
        """检查武器是否可以攻击"""
        _, weapon_type = self.get_weapon_name_type(weapon_id)
        return weapon_type not in WEAPONS_ASSIST

    def get_model_info(self, category: str, db_id: int) -> ModelInfo | None:
        """获取模型信息"""
        if category not in {"aircraft", "facility", "weapon"}:
            return None

        query = f"SELECT Name, Type FROM data{category} WHERE ID = ?"
        result = self.backend.execute_query(query, (db_id,)).fetchone()
        return ModelInfo(name=result[0], type=result[1]) if result else None


# 默认数据库实例
default_db = ModelDatabase.from_env()
