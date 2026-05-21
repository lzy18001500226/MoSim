---
title: DevTools
description: agently-devtools 中 ObservationBridge、EvaluationBridge 与 InteractiveWrapper 的用法。
keywords: Agently, DevTools, ObservationBridge, EvaluationBridge, InteractiveWrapper
---

# DevTools

> 语言：[English](../../en/observability/devtools.md) · **中文**

`agently-devtools` 是可选的 companion package（配套包）。它消费 Agently 的 observation event（观测事件），提供本地观测、评估和交互式 UI。它不是 workflow 结构的事实来源；TriggerFlow definition（定义）和 execution（执行实例）仍然是事实来源。

## 安装与 listener

```bash
pip install -U agently agently-devtools
agently-devtools start
```

默认本地端点来自 [`examples/devtools/README.md`](../../../examples/devtools/README.md)：

| 接口 | 默认值 |
|---|---|
| DevTools console | `http://127.0.0.1:15596/` |
| Observation ingest | `http://127.0.0.1:15596/observation/ingest` |
| Interactive wrapper UI | `http://127.0.0.1:15365/` |

## ObservationBridge

对应示例是 [`examples/devtools/01_observation_bridge_local.py`](../../../examples/devtools/01_observation_bridge_local.py)。它把 bridge 注册到 `Agently` 上，运行一个 TriggerFlow，然后注销：

```python
from agently import Agently
from agently_devtools import ObservationBridge

bridge = ObservationBridge(app_id="agently-main-examples", group_id="devtools-local-demo")
bridge.register(Agently)

try:
    ...
finally:
    bridge.unregister(Agently)
```

只想上传指定 flow 时，用 `auto_watch=False` 加 `bridge.watch(flow)`；见 [`02_observation_bridge_selective_watch.py`](../../../examples/devtools/02_observation_bridge_selective_watch.py)。

## EvaluationBridge

[`03_scenario_evaluations.py`](../../../examples/devtools/03_scenario_evaluations.py) 会构建一个小 TriggerFlow，用 `EvaluationBinding` 绑定，再通过 `EvaluationRunner` 跑多个 `EvaluationCase`。它适合可重复的场景检查，不适合当作应用请求内的实时校验。

## InteractiveWrapper

`InteractiveWrapper` 可以包：

- 普通 callable 或 generator：[`04_interactive_wrapper_basic.py`](../../../examples/devtools/04_interactive_wrapper_basic.py)
- Agently Agent：[`05_interactive_wrapper_agent.py`](../../../examples/devtools/05_interactive_wrapper_agent.py)
- 会 stream 阶段更新的 TriggerFlow：[`06_interactive_wrapper_trigger_flow.py`](../../../examples/devtools/06_interactive_wrapper_trigger_flow.py)

TriggerFlow 场景下，用 `data.async_put_into_stream(...)` 推进度；wrapper 消费 runtime stream，最后展示 close snapshot。

## 兼容边界

DevTools 消费端应 fail open（宽容失败）：

- 忽略未知 observation event type 和未知 payload 字段
- 关联运行链路时优先使用 `run` 字段，不要解析 `message`
- TriggerFlow 图应从 flow definition 和 runtime metadata 派生，不维护第二份手写图

发布管理上，包版本只能解决一部分问题。未发布分支之间的协作应以 Agently 在 `agently/compatibility.py` 中声明的 runtime protocol 为第一判断依据，包版本范围只作为升级建议。已发布历史版本的分版本 manifest 位于 Agently 主仓库的 `compatibility/releases/<framework_version>.json`。对于已经发布、但早于这套 manifest 机制的 `4.1.0.2` 到 `4.1.1`，DevTools 可以回退到内置的 legacy protocol 映射；超出这段历史窗口，如果仍然没有 manifest，就应视为“兼容性未被验证”，而不是默认兼容。

observation event schema 和 TriggerFlow 事件别名规则见 [Event Center](event-center.md)。
