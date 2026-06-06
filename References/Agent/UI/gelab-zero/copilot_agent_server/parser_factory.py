"""Parser 工厂：根据 parser 名称返回对应解析器实例。"""

import importlib
from enum import Enum
from typing import Any, Dict, Type, Union

class TaskType(str, Enum):
    """任务类型枚举（值即 parser 名称）。"""

    PARSER_0922_SUMMARY = "parser_0922_summary"
    PARSER_0920 = "parser_0920"
    PARSER_0920_SUMMARY_ADV = "parser_0920_summary_adv"
    PARSER_0920_SUMMARY_ADV_STATE_COMPRESS = "parser_0920_summary_adv_state_compress"





class DefaultConstants:
    """默认常量定义。"""

    # 默认 parser 对应的 task_type，可按业务场景覆盖。
    TASK_TYPE = TaskType.PARSER_0922_SUMMARY


_PARSER_NAME_MAP: Dict[str, tuple[str, str]] = {
    TaskType.PARSER_0922_SUMMARY.value: ("copilot_tools.parser_0920_summary", "Parser0920Summary"),
    TaskType.PARSER_0920.value: ("copilot_tools.parser_0920_summary", "Parser0920Summary"),
    TaskType.PARSER_0920_SUMMARY_ADV.value: ("copilot_tools.parser_0920_summary_adv", "Parser0920SummaryAdv"),
    TaskType.PARSER_0920_SUMMARY_ADV_STATE_COMPRESS.value: (
        "copilot_tools.parser_0920_summary_adv_state_compress",
        "Parser0920SummaryAdvStateCompress",
    ),
}


def get_parser(parser_name: Union[str, TaskType] = DefaultConstants.TASK_TYPE):
    """构建并返回 parser 实例。

    Args:
        parser_name: parser 名称，支持字符串或 `TaskType` 枚举。

    Returns:
        object: 对应 parser 的实例对象，需具备 `env2messages4ask` 与 `str2action` 等方法。

    Raises:
        ValueError: 当 `parser_name` 不在映射表中时抛出。
    """
    parser_key = parser_name.value if isinstance(parser_name, TaskType) else str(parser_name)
    parser_key = parser_key.strip()

    if parser_key in _PARSER_NAME_MAP:
        module_name, class_name = _PARSER_NAME_MAP[parser_key]
        module = importlib.import_module(module_name)
        parser_cls = getattr(module, class_name)
        return parser_cls()
    raise ValueError(f"Unknown parser name: {parser_name}")
