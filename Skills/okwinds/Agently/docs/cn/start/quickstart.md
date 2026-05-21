---
title: 快速开始
description: 五分钟内完成 Agently 安装、模型配置，并跑通一次结构化请求。
keywords: Agently, 快速开始, 结构化输出, OpenAICompatible, AnthropicCompatible
---

# 快速开始

> 语言：[English](../../en/start/quickstart.md) · **中文**

目标是先把一次最小可用的端到端请求跑通，然后给你一条明确的下一步路径。

## 安装

```bash
pip install -U agently
```

`uv pip install -U agently` 同样可用。

## 配置一个模型

Agently 内置三个协议层 Request 插件：`OpenAICompatible`（Chat Completions 兼容端点）、`OpenAIResponsesCompatible`（Responses API 形态）和 `AnthropicCompatible`（Claude / Anthropic Messages API）。按你要调用的端点协议选择对应插件。

```python
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "https://api.openai.com/v1",
        "api_key": "${ENV.OPENAI_API_KEY}",
        "model": "${ENV.OPENAI_MODEL}",
    },
)
```

Claude：

```python
Agently.set_settings(
    "AnthropicCompatible",
    {
        "base_url": "https://api.anthropic.com",
        "api_key": "${ENV.ANTHROPIC_API_KEY}",
        "model": "${ENV.ANTHROPIC_MODEL}",
        "max_tokens": 4096,
    },
)
```

Ollama 或任何 OpenAI 兼容的本地服务：把 `base_url` 指向该服务（Ollama 默认 `http://127.0.0.1:11434/v1`），`model` 设为本地模型名。本地服务不需要鉴权时可以省略 `api_key`。

更完整的 provider 列表与 `${ENV.*}` 占位写法见 [模型设置](model-setup.md)。

## 跑一次结构化请求

```python
from agently import Agently

agent = Agently.create_agent()

result = (
    agent
    .input("用一句话写出 Agently 的定位，再写两个产品亮点。")
    .output({
        "positioning": (str, "一句话定位", True),
        "highlights": [
            {
                "title": (str, "亮点标题", True),
                "detail": (str, "一句话描述", True),
            }
        ],
    })
    .start()
)

print(result)
```

每个叶子写作 `(type, description, ensure)`。第三槽是 **`ensure` 标记**——置为 `True` 时该字段会被强制要求出现，必要时框架会自动重试。详见 [Schema as Prompt](../requests/schema-as-prompt.md)。

## 接下来读什么

- 写服务、流式 UI 或工作流 → [Async First](async-first.md)
- 更多 provider 与环境变量驱动的配置 → [模型设置](model-setup.md)
- 更强的输出约束与校验 → [输出控制](../requests/output-control.md)
- 从一次响应里读 text / data / metadata → [模型响应](../requests/model-response.md)
- 项目变大后的目录结构 → [项目结构](project-framework.md)
- 分支、循环、暂停恢复 → [TriggerFlow 概览](../triggerflow/overview.md)

## 常见误区

- 在 `output()` 之前自己写 JSON 解析。
- 单次请求还没稳定就跳进 TriggerFlow。
- 把 prompt 定义、配置、业务逻辑写在同一个脚本里——见 [项目结构](project-framework.md)。
