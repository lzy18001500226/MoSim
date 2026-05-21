---
title: 会话记忆
description: Session 如何接入 agent、记录多轮历史、控制上下文窗口并导入导出。
keywords: Agently, session, activate_session, chat history, memo, context window
---

# 会话记忆

> 语言：[English](../../en/requests/session-memory.md) · **中文**

Session 是 Agently 的多轮对话容器。它保存完整对话历史（`full_context`），同时维护真正放进下一次请求的窗口（`context_window`）。默认策略只做长度控制；如果你需要摘要、长期偏好或更复杂的裁剪逻辑，需要注册自己的 analysis / resize handler。

## 启用与关闭

```python
from agently import Agently

agent = Agently.create_agent()
agent.activate_session(session_id="support-demo")

agent.input("请记住：我的订单号是 A-100。").start()
reply = agent.input("我的订单号是什么？").start()

agent.deactivate_session()
```

`activate_session(session_id=...)` 会创建或复用这个 id 对应的 `Session`，并把 `runtime.session_id` 写进 agent settings。关闭时用 `deactivate_session()`；关闭后 agent 不再把 session chat history 注入请求。

## Chat history 入口

启用 session 后，agent 上这几个方法会代理到当前 session：

```python
agent.set_chat_history([
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好，我是 Agently 助手。"},
])

agent.add_chat_history({"role": "user", "content": "继续上个话题"})
agent.reset_chat_history()
```

当前 session 在 `agent.activated_session`。没有启用 session 时，上面这些方法会退回普通 agent prompt 的 chat history 行为。

## 默认窗口策略

`Session` 的默认配置是：

```python
agent.set_settings("session.max_length", 12000)
```

当 `context_window` 的近似文本长度超过 `session.max_length` 时，默认 handler 使用 `simple_cut`：从最新消息往前保留，直到窗口长度不超过限制。如果只有最后一条消息也超长，就截取这条消息的末尾。

这个长度是按消息序列化后的字符数近似，不是精确 token 计数。

## 记录哪些内容

默认情况下，请求结束后 session 会把本次 prompt 文本作为 user 内容、把结果数据作为 assistant 内容追加到历史。想只记录部分字段时，用：

```python
agent.set_settings("session.input_keys", ["info.task", "input.question"])
agent.set_settings("session.reply_keys", ["answer", "score"])
```

`session.input_keys` 从 prompt 数据里取路径；`session.reply_keys` 从解析后的结果数据里取路径。设为 `None` 时恢复默认记录方式。

## 自定义 resize / memo

框架内置的 session 不会自动调用模型生成摘要。`memo` 是一个可序列化字段，供自定义 resize handler 写入：

```python
def analysis_handler(full_context, context_window, memo, session_settings):
    if len(context_window) > 6:
        return "keep_last_four"
    return None


def keep_last_four(full_context, context_window, memo, session_settings):
    new_memo = {
        "previous_turns": len(full_context) - 4,
        "note": "Older turns were summarized by application code.",
    }
    return None, list(context_window[-4:]), new_memo


agent.register_session_analysis_handler(analysis_handler)
agent.register_session_resize_handler("keep_last_four", keep_last_four)
```

如果你要做“模型摘要记忆”，把模型调用放进自己的 resize handler；Session 只负责保存 handler 返回的 `memo` 并在后续请求里注入它。

## 导入 / 导出

```python
from agently.core import Session

session = agent.activated_session
json_text = session.get_json_session()
yaml_text = session.get_yaml_session()

restored = Session(settings=agent.settings)
restored.load_json_session(json_text)

agent.sessions[restored.id] = restored
agent.activate_session(session_id=restored.id)
```

也可以用别名：`session.to_json()` / `session.to_yaml()`、`session.load_json(...)` / `session.load_yaml(...)`。

## 边界

Session 负责多轮 chat history、当前上下文窗口、可选 memo 字段和导入导出。它不负责持久化后端、向量库、跨设备用户画像或精确 token 预算。那些应该在应用层或知识库层实现。

## 另见

- [Context Engineering](context-engineering.md) —— 知识该放 session、prompt info 还是 KB
- [知识库](../knowledge/knowledge-base.md) —— 检索型上下文
- [Prompt 管理](prompt-management.md) —— chat history 如何进入请求
