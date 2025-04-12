# src/mozi_ai_x/utils/validator.py

import re
import uuid
from functools import wraps
from inspect import signature
from typing import get_type_hints, Literal, Any


def validate_literal_args(func):
    """
    自动校验带 Literal 标注的参数，值必须合法
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        hints = get_type_hints(func)

        sig = signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            typ = hints.get(name)
            if typ is not None and getattr(typ, "__origin__", None) is Literal:
                if value not in typ.__args__:
                    raise ValueError(f"参数{name}={value!r} 不符合约束，期望值之一为 {typ.__args__}")
        return func(*args, **kwargs)

    return wrapper


def validate_uuid4_args(param_names):
    """
    检查指定参数列表是否为合法的UUID4
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for name in param_names:
                value = bound.arguments.get(name)
                if not (isinstance(value, str) and _is_uuid4_string(value)):
                    raise ValueError(f"参数{name}={value!r} 不是合法的UUID4字符串")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_regex_args(arg_regex_map: dict[str, str]):
    """
    检查参数是否满足指定正则表达式
    用法: @validate_regex_args({"param": r"your_regex"})
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for name, pattern in arg_regex_map.items():
                s = bound.arguments.get(name)
                if not isinstance(s, str) or not re.fullmatch(pattern, s):
                    raise ValueError(f"参数{name}={s!r} 不符合正则 {pattern}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_range_args(arg_range_map: dict[str, tuple[Any, Any]]):
    """
    检查参数是否在指定区间（闭区间）
    用法: @validate_range_args({"x": (0,1)})
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for name, (low, high) in arg_range_map.items():
                v = bound.arguments.get(name)
                if not (low <= v <= high):
                    raise ValueError(f"参数{name}={v!r} 超出有效区间[{low},{high}]")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _is_uuid4_string(s: str) -> bool:
    "仅允许标准格式UUID4（带-或不带-的都可以）"
    try:
        # uuid.UUID会校验合法性，version=4可严格校验 UUID4
        uuid_obj = uuid.UUID(s)
        return uuid_obj.version == 4
    except Exception:
        return False
