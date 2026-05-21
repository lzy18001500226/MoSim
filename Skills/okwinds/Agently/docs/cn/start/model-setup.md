---
title: 模型设置
description: 配置模型 provider、环境变量驱动的配置以及 agent 级覆盖。
keywords: Agently, 模型设置, OpenAICompatible, AnthropicCompatible, 环境变量
---

# 模型设置

> 语言：[English](../../en/start/model-setup.md) · **中文**

Agently 在 `agently.builtins.plugins.ModelRequester` 下提供三个协议层 Request 插件：

- `OpenAICompatible`——任何说 OpenAI Chat Completions API 的端点都走这条路径。覆盖 OpenAI、DeepSeek、Qwen、Ollama、Kimi、GLM、MiniMax、Doubao、SiliconFlow、Groq、ERNIE、Gemini-via-OpenAI。
- `OpenAIResponsesCompatible`——OpenAI Responses API 形态的端点。
- `AnthropicCompatible`——Anthropic 原生 API（Claude）。它是独立 requester 插件，请求体构造是 Anthropic 专属（`anthropic_version`、`anthropic_beta`、必填的 `max_tokens`）。

通过填写哪个插件名下的设置，来决定 active requester 是哪一个。

## 全局 vs Agent 级设置

设置是分层的。`Agently.set_settings(...)` 设全局默认；`agent.set_settings(...)` 只覆盖某个 agent。Agent 没显式覆盖的 key 沿用全局值。

```python
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)

agent = Agently.create_agent()

# 仅这个 agent 覆盖 model
agent.set_settings(
    "OpenAICompatible",
    {"model": "qwen2.5:7b"},
)
```

详细分层规则见 [设置](settings.md)。

## 常见 provider 配置

### OpenAI

```python
Agently.set_settings("OpenAICompatible", {
    "base_url": "https://api.openai.com/v1",
    "api_key": "${ENV.OPENAI_API_KEY}",
    "model": "${ENV.OPENAI_MODEL}",
})
```

### Claude / Anthropic

```python
Agently.set_settings("AnthropicCompatible", {
    "base_url": "https://api.anthropic.com",
    "api_key": "${ENV.ANTHROPIC_API_KEY}",
    "model": "${ENV.ANTHROPIC_MODEL}",
    "max_tokens": 4096,
})
```

### DeepSeek

```python
Agently.set_settings("OpenAICompatible", {
    "base_url": "https://api.deepseek.com/v1",
    "api_key": "${ENV.DEEPSEEK_API_KEY}",
    "model": "${ENV.DEEPSEEK_MODEL}",
})
```

### Qwen / DashScope

```python
Agently.set_settings("OpenAICompatible", {
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "api_key": "${ENV.DASHSCOPE_API_KEY}",
    "model": "${ENV.DASHSCOPE_MODEL}",
})
```

### Ollama（本地）

```python
Agently.set_settings("OpenAICompatible", {
    "base_url": "http://127.0.0.1:11434/v1",
    "model": "qwen2.5:7b",
})
```

本地服务不需要鉴权时可以省略 `api_key`。

更多 provider（Kimi、GLM、MiniMax、Doubao、SiliconFlow、Groq、ERNIE、Gemini）见 [模型概览](../models/overview.md) 与 [Providers](../models/providers/)。

## 环境变量与 dotenv

设置中任何位置使用 `${ENV.<NAME>}` 占位符，会在 settings 被读取时替换为对应环境变量。占位符由 [agently/utils/Settings.py](../../../agently/utils/Settings.py) 解析。

```python
Agently.set_settings("OpenAICompatible", {
    "base_url": "${ENV.OPENAI_BASE_URL}",
    "api_key": "${ENV.OPENAI_API_KEY}",
    "model": "${ENV.OPENAI_MODEL}",
})
```

要在启动时自动加载 `.env`，从配置文件加载时传 `auto_load_env=True`：

```python
from agently import Agently

Agently.load_settings("yaml_file", "settings.yaml", auto_load_env=True)
```

## 验证连通性

```python
result = (
    Agently.create_agent()
    .input("用一句话打个招呼。")
    .start()
)
print(result)
```

如果能打印出文字，说明模型配置已生效。如果出现鉴权或连接错误，问题在 `base_url` / `api_key` / 网络可达性，与 prompt 或 output schema 无关。

## 另见

- [模型概览](../models/overview.md)——协议层细节
- [设置](settings.md)——分层与环境变量
- [项目结构](project-framework.md)——把模型配置放进文件而不是写在代码里
