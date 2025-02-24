import os
import logging
import logging.handlers
from pathlib import Path


class MPrint:
    def __init__(self, name: str = ""):
        self.name = name
        self.prefix = f"[{self.name}] " if name else ""

        # 从环境变量读取配置
        self.enable_console = os.getenv("MOZI_LOG_CONSOLE", "1").lower() in ("1", "true", "yes")
        self.enable_file = os.getenv("MOZI_LOG_FILE", "0").lower() in ("1", "true", "yes")
        self.log_level = os.getenv("MOZI_LOG_LEVEL", "DEBUG").upper()

        # 设置日志
        self.logger = logging.getLogger(f"mozi_ai.{name}" if name else "mozi_ai")
        self.logger.propagate = False  # 阻止向父logger传播

        # 检查现有handler类型
        existing_handlers = {type(h).__name__ for h in self.logger.handlers}

        self.logger.setLevel(getattr(logging, self.log_level, logging.DEBUG))
        formatter = logging.Formatter("%(asctime)s - %(message)s")

        # 配置文件日志
        if self.enable_file and "TimedRotatingFileHandler" not in existing_handlers:
            log_path = Path(os.getenv("MOZI_LOG_PATH", "./log"))
            if not log_path.exists():
                log_path.mkdir(parents=True, exist_ok=True)

            log_handler = logging.handlers.TimedRotatingFileHandler(
                log_path / "mozi_ai.log",
                when="D",
                interval=1,
                backupCount=20,
                encoding="utf8",
            )
            log_handler.setLevel(getattr(logging, self.log_level, logging.DEBUG))
            log_handler.setFormatter(formatter)
            self.logger.addHandler(log_handler)

        # 配置控制台日志
        if self.enable_console and "StreamHandler" not in existing_handlers:
            console = logging.StreamHandler()
            console.setLevel(getattr(logging, self.log_level, logging.DEBUG))
            console.setFormatter(formatter)
            console.stream = open(console.stream.fileno(), "w", encoding="utf-8", closefd=False)
            self.logger.addHandler(console)

    def __call__(self, *args):
        self.info(*args)

    def debug(self, *args):
        message = "[DEBUG] " + self.prefix + " ".join([str(arg) for arg in args])
        self.logger.debug(message)

    def info(self, *args):
        message = "[INFO] " + self.prefix + " ".join([str(arg) for arg in args])
        self.logger.info(message)

    def warning(self, *args):
        message = "[WARNING] " + self.prefix + " ".join([str(arg) for arg in args])
        self.logger.warning(message)

    def error(self, *args):
        message = "[ERROR] " + self.prefix + " ".join([str(arg) for arg in args])
        self.logger.error(message)


# 创建默认实例
mprint = MPrint()


def mprint_with_name(name: str):
    return MPrint(name)
