---
title: 项目结构
description: 非琐碎 Agently 项目的推荐目录布局。
keywords: Agently, 项目结构, settings, prompt, 工作流, FastAPI
---

# 项目结构

> 语言：[English](../../en/start/project-framework.md) · **中文**

一旦超出单脚本，关注点分离的收益就很大：

- 设置放在文件，不需要为不同环境改代码。
- Prompt 放在 YAML / JSON，可被非工程同事 review。
- 业务代码不直接 import key 或 model name。

## 推荐布局

```text
my-agently-app/
  pyproject.toml              # 或 requirements.txt
  .env                        # 本地敏感配置（gitignore）
  settings.yaml               # 全局模型与运行时设置
  prompts/
    summarize.yaml            # 一份 prompt 一个文件
    triage.yaml
  flows/
    triage.py                 # TriggerFlow 定义
  app/
    api.py                    # FastAPI 入口
    agents.py                 # agent 工厂
    actions.py                # action / tool 注册
    main.py
  tests/
    test_triage_flow.py
```

只需 `settings.yaml` 与 `prompts/*` 这条主线就能跑起来，其余是可扩展骨架。

## settings.yaml

```yaml
plugins:
  ModelRequester:
    OpenAICompatible:
      base_url: ${ENV.OPENAI_BASE_URL}
      api_key: ${ENV.OPENAI_API_KEY}
      model: ${ENV.OPENAI_MODEL}
debug: false
```

启动时加载：

```python
from agently import Agently

Agently.load_settings("yaml_file", "settings.yaml", auto_load_env=True)
```

`auto_load_env=True` 先读 `.env`，再解析 `${ENV.*}`。

## Prompt 写在文件里

```yaml
# prompts/summarize.yaml
.request:
  instruct: |
    你是一个简洁的编辑，保持事实不变。
  output:
    title:
      $type: str
      $ensure: true
    body:
      $type: str
      $ensure: true
```

加载与使用：

```python
from agently import Agently

agent = Agently.create_agent().load_yaml_prompt("prompts/summarize.yaml")
result = agent.input(article_text).start()
```

`$ensure: true` 是 `(type, "desc", True)` 元组第三槽的 YAML 形式——见 [Schema as Prompt](../requests/schema-as-prompt.md)。Legacy `$default` 已不再支持。

## Agent 工厂

集中创建逻辑，避免调用点重复配置：

```python
# app/agents.py
from agently import Agently


def make_summarizer():
    return Agently.create_agent().load_yaml_prompt("prompts/summarize.yaml")
```

## Flow 放在哪里

每个 TriggerFlow 一个独立模块，放在 `flows/`。Service 代码 import flow 对象再创建 execution，flow 定义本身不耦合 FastAPI / 队列等基础设施。见 [TriggerFlow 概览](../triggerflow/overview.md)。

## Action 放在哪里

如果 agent 需要调工具 / MCP / sandbox，把注册逻辑放在 agent 工厂旁或独立的 `actions.py`。新代码使用 action-first 入口（`@agent.action_func`、`agent.use_actions(...)`）；`tool_func` / `use_tools` / `use_mcp` / `use_sandbox` 仍然可用，但定位为兼容入口，详见 [Action Runtime](../actions/action-runtime.md)。

## 另见

- [设置](settings.md)
- [Prompt 管理](../requests/prompt-management.md)
- [Schema as Prompt](../requests/schema-as-prompt.md)
- [TriggerFlow 概览](../triggerflow/overview.md)
- [FastAPI 服务封装](../services/fastapi.md)
