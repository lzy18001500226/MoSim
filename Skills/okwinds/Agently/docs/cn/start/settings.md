---
title: 设置
description: Agently 设置如何在全局、agent 与 request 之间分层，含环境变量占位。
keywords: Agently, 设置, set_settings, 分层, 环境变量, dotenv
---

# 设置

> 语言：[English](../../en/start/settings.md) · **中文**

Agently 设置是一个分层 key-value 存储，分三个 scope：

| Scope | 设置方式 | 可见范围 |
|---|---|---|
| 全局 | `Agently.set_settings(...)` | 此调用之后创建的所有 agent / request |
| Agent | `agent.set_settings(...)` | 由该 agent 创建的所有 request |
| Request / runtime | `start(..., max_retries=...)` 等方法级参数 | 仅这一次调用 |

低 scope 覆盖高 scope；没显式覆盖的 key 沿用上层。

## 设置路径

`set_settings(...)` 的第一个参数是点路径，常用：

| 路径 | 含义 |
|---|---|
| `OpenAICompatible` | `plugins.ModelRequester.OpenAICompatible` 的别名 |
| `AnthropicCompatible` | Claude requester 的别名 |
| `plugins.ModelRequester.<Name>` | 完整路径，与上面别名等价 |
| `debug` | 打开模型请求的流式控制台日志 |
| `runtime.show_model_logs` | 打开模型请求与响应解析的控制台日志；`True` 等价于 `"simple"` |
| `runtime.show_action_logs` | 打开 Action Runtime planning 与 execution 的控制台日志；`True` 等价于 `"simple"` |
| `runtime.show_tool_logs` | `runtime.show_action_logs` 的兼容别名，用于旧工具回路示例 |
| `runtime.show_trigger_flow_logs` | 打开 TriggerFlow execution / signal 的控制台日志；`True` 等价于 `"simple"` |
| `runtime.show_runtime_logs` | 打开 request、session、chunk、`runtime.print` 等通用 observation 事件的控制台日志；`True` 等价于 `"simple"` |
| `runtime.show_deprecation_warnings` | 发出 deprecated API warning；默认 `True`，设为 `False` / `"off"` 可全局关闭 deprecation warning |
| `runtime.session_id` | 把请求绑定到指定的 session id |

也可以一次传入一个 dict，按 key 合并：

```python
Agently.set_settings("OpenAICompatible", {
    "base_url": "https://api.openai.com/v1",
    "model": "${ENV.OPENAI_MODEL}",
})
```

## 读取设置

```python
agent_settings = agent.settings.get("plugins.ModelRequester.OpenAICompatible", {})
print(agent_settings.get("model"))
```

`settings.get(path, default)` 按点路径查找，找不到时返回 default。

## 环境变量占位

设置值的任何位置都可以写 `${ENV.<NAME>}`，读取时替换为对应环境变量。占位符由 [agently/utils/Settings.py](../../../agently/utils/Settings.py) 解析。

```python
Agently.set_settings("OpenAICompatible", {
    "api_key": "${ENV.OPENAI_API_KEY}",
})
```

## 从文件加载

非琐碎项目里，把设置放到 YAML / TOML / JSON，而不是写在 Python 内：

```python
from agently import Agently

Agently.load_settings("yaml_file", "settings.yaml", auto_load_env=True)
```

`auto_load_env=True` 会先加载工作目录下的 `.env`，然后再解析 `${ENV.*}`。

如果需要直接操作 `Settings` 对象，也可以用 `Settings().load(...)`：

```python
from agently.utils import Settings

settings = Settings()
settings.load("yaml_file", "settings.yaml", auto_load_env=True)
```

完整的项目结构示例见 [项目结构](project-framework.md)。

## Debug 开关

```python
Agently.set_settings("debug", True)
```

打印模型请求的流式日志，用于核验 prompt 槽位、output schema 与重试是否符合预期。

运行时日志也可以按 family 单独打开：

```python
Agently.set_settings("runtime.show_model_logs", True)
Agently.set_settings("runtime.show_action_logs", True)
Agently.set_settings("runtime.show_trigger_flow_logs", True)
Agently.set_settings("runtime.show_runtime_logs", "detail")
```

这些开关都接受 `False` / `"off"`、`True` / `"simple"`、`"detail"`。`"simple"` 打印摘要和 warning/error/critical 事件；`"detail"` 打印该 family 的完整 observation 事件。Action loop 事件显示为 `ActionLoop`；具体 `action.*` 事件会显示 action 名称和 `action_type`。`runtime.show_tool_logs` 仍兼容旧代码；当没有显式设置 `runtime.show_action_logs` 时，它会启用同一组 Action Runtime 日志。开始事件显示 `Started`，正常结束显示 `Completed`，只有失败事件或显式失败 payload 才显示 `Failed`。

如果生产环境明确保留了一些 legacy compatibility 调用，可以全局关闭 deprecation warning：

```python
Agently.set_settings("runtime.show_deprecation_warnings", False)
```

这个开关只影响 Agently 的 deprecation warning。运行期告警、错误，以及 `flow_data` 这类 risky-scope warning，仍由各自 API 与设置控制。

## 另见

- [模型设置](model-setup.md)——provider 专属配置
- [项目结构](project-framework.md)——基于文件的设置布局
