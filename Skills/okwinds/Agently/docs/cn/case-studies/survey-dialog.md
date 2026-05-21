---
title: 问卷对话
description: 多轮问卷，含动态 prompt、分支跟进、稳定 session 记忆。
keywords: Agently, 案例研究, survey, dialog, session, 动态 prompt
---

# 问卷对话

> 语言：[English](../../en/case-studies/survey-dialog.md) · **中文**

## 问题

通过对话界面跑结构化问卷。模型：

1. 根据已答内容问下一个问题。
2. 校验回答（类型对、范围内、对题）。
3. 必要时分支到跟进问题。
4. 知道问卷何时完成。
5. 末尾产出结构化结果。

## 形态

带 session 的对话 agent，加每轮结构化输出包含：

- 下一个要问的问题
- 正在填的 slot
- 是否完成

应用循环读模型结构化输出决定是否继续。

## 走读

```python
from agently import Agently

agent = (
    Agently.create_agent()
    .role(
        "你在跑客户入职问卷。一次问一个问题。必要时分支到跟进。"
        "所有必填 slot 填完时结束问卷。",
        always=True,
    )
    .info({
        "required_slots": ["company_size", "primary_use_case", "current_tools", "decision_timeline"],
        "format": "仅按 schema 回答。",
    }, always=True)
)

agent.activate_session(session_id="survey-dialog")  # 多轮

state = {"answers": {}}


def step(user_message: str):
    return (
        agent
        .info({"answers_so_far": state["answers"]}, always=False)
        .input(user_message)
        .output({
            "reply_to_user": (str, "给用户看的内容", True),
            "current_slot": (str, "正在填的 slot", True),
            "captured": {
                "slot": (str, "刚捕获的 slot（或空）"),
                "value": "捕获的值（任意类型）",
            },
            "survey_complete": (bool, "所有必填 slot 都捕获后才为 True", True),
        })
        .start()
    )


# 跑
print("你好！我们开始吧，准备好了吗？")
user_text = input("> ")
while True:
    result = step(user_text)
    print(result["reply_to_user"])

    captured = result.get("captured") or {}
    if captured.get("slot"):
        state["answers"][captured["slot"]] = captured.get("value")

    if result["survey_complete"]:
        break
    user_text = input("> ")

print("\n最终回答：")
print(state["answers"])
```

## 为什么这么选

- **每轮结构化输出，不是自由回复** —— 应用需要知道哪个 slot 被捕获、问卷是否结束。让模型在散文里格式化这个不可靠。
- **`info(answers_so_far, always=False)`** —— 捕获 state 每轮变；作为请求侧 `info` 传保证总是最新而不污染 agent 持久 prompt。
- **`info({"required_slots": [...]}, always=True)`** —— slot 列表不变；pin 到 agent。
- **session 启用** —— 模型需要记住对话流（「上轮你说小/中型，所以我会问定价层级」）。`activate_session()` 处理。
- **分支由模型驱动** —— 模型根据已捕获回答选跟进问题。应用不需要硬编码决策树。取舍：不如手工问卷可预测，但对话更自然。
- **`survey_complete: bool`** —— 显式终止。应用循环信任它；模型被告诉只在所有必填 slot 填完时设置。

## 变体

### 在接受前校验捕获值

`value` 应是某个 enum 时用自定义 `.validate(...)`：

```python
def value_check(result, ctx):
    captured = result.get("captured") or {}
    slot = captured.get("slot")
    value = captured.get("value")
    if slot == "decision_timeline" and value not in ("now", "this_quarter", "this_year", "exploring"):
        return {"ok": False, "reason": f"unknown timeline: {value}", "validator_name": "enum"}
    return True
```

见 [输出控制](../requests/output-control.md)。

### 长问卷的自定义摘要

问卷长（20+ 问题）时，给 session 注册自定义 resize handler，把较早轮次摘要进 `memo`：

```python
agent.set_settings("session.max_length", 12000)
agent.register_session_analysis_handler(analysis_handler)
agent.register_session_resize_handler("summarize_old_turns", resize_handler)
```

Session 默认只裁剪窗口；摘要逻辑由你的 handler 提供。见 [会话记忆](../requests/session-memory.md)。

### 分支深时切 TriggerFlow

单条用户回答触发多步处理（lookup、validate、score）时，把每轮处理升到 TriggerFlow。对话层留在 agent 循环；每轮跑一个 flow。见 [TriggerFlow 编排 Playbook](../playbooks/triggerflow-orchestration.md)。

## 交叉链接

- [会话记忆](../requests/session-memory.md) —— 多轮上下文、窗口裁剪、自定义 memo
- [Schema as Prompt](../requests/schema-as-prompt.md) —— `survey_complete: bool` 作为 ensure 字段
- [输出控制](../requests/output-control.md) —— `.validate(...)` 值检查
- [Context Engineering](../requests/context-engineering.md) —— `info(always=True)` vs `always=False`
