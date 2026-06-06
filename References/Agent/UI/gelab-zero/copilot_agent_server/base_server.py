"""Copilot Server 抽象接口定义。

该模块约束 server 的最小能力：
1. 创建会话；
2. 基于会话执行单步推理。
"""

class BaseCopilotServer:
    """Copilot 服务基类（接口层）。"""

    def __init__(self):
        """初始化基类。"""
        pass

    def get_session(self, payload: dict) -> str:
        """创建会话并返回会话 ID。

        Args:
            payload: 会话初始化参数，通常包括任务描述、parser 类型、模型配置等信息。

        Returns:
            str: 会话唯一标识 `session_id`。
        """
        raise NotImplementedError

    def automate_step(self, payload: dict) -> dict:
        """执行单步推理并返回动作。

        Args:
            payload: 单步观察输入，通常包括 `session_id` 与当前截图/上下文。

        Returns:
            dict: 当前步推理结果，至少应包含动作信息。
        """
        raise NotImplementedError

DEFAULT_MAX_RETRY = 5
if __name__ == "__main__":
    pass
