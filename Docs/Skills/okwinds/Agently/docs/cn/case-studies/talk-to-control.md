---
title: Talk to Control
description: 通过自然语言对域对象采取 action 的对话 agent。
keywords: Agently, 案例研究, talk to control, action, 对话
---

# Talk to Control

> 语言：[English](../../en/case-studies/talk-to-control.md) · **中文**

## 问题

用户用自然语言控制某物 —— 文档、dashboard、记录集。每轮模型：

1. 理解用户意图。
2. 从固定集合选一个 action。
3. 在当前域对象上执行该 action。
4. 回复做了什么以及现在状态。

## 形态

```text
用户输入  →  Agent（带 action）→ action 调用 → 更新 state → 回复
                       ▲
                       │
                  Session（多轮历史）
```

本质上是带 action 的对话 agent。除非每轮内有多步过程，否则不需要 TriggerFlow。

## 走读

```python
from agently import Agently

agent = (
    Agently.create_agent()
    .role("你控制一个购物车。用可用 action 修改它。", always=True)
    .info({"format": "每个 action 后简短确认改了什么。"}, always=True)
)

# demo 用的内存购物车
cart = {"items": [], "total": 0.0}


@agent.action_func
def add_item(name: str, price: float, quantity: int = 1):
    """加一个商品到购物车。"""
    cart["items"].append({"name": name, "price": price, "quantity": quantity})
    cart["total"] += price * quantity
    return cart


@agent.action_func
def remove_item(name: str):
    """从购物车移除一个商品。"""
    cart["items"] = [i for i in cart["items"] if i["name"] != name]
    cart["total"] = sum(i["price"] * i["quantity"] for i in cart["items"])
    return cart


@agent.action_func
def show_cart():
    """返回当前购物车。"""
    return cart


agent.use_actions([add_item, remove_item, show_cart])

# 启用 session，让多轮上下文受限
agent.activate_session(session_id="cart-demo")

# 对话循环
while True:
    user_text = input("> ")
    if not user_text.strip():
        break
    reply = agent.input(user_text).start()
    print(reply)
```

## 为什么这么选

- **每个操作一个 `@agent.action_func`，不是单个「万能」工具** —— 小而具名 action 让模型选对。单一大工具迫使模型把参数编码进字符串里的 JSON。
- **`role(always=True)` 给行为，`info(always=True)` 给格式** —— 都存放在 agent 上，并会进入这个 agent 发起的每次请求；因此每次请求都会计入 prompt。
- **`activate_session()` 而非手工管理 chat history** —— 聊天交互中，session 帮你维护完整历史和当前窗口。需要摘要时注册自定义 resize handler。见 [会话记忆](../requests/session-memory.md)。
- **购物车作为模块 state** —— 真实代码里这是数据库，action 函数读写它。形态不变。
- **不要结构化输出 schema** —— agent 的回复是给人的。除非别处需要程序消费，否则不强加结构。

## 变体

### 流式回复

UI 用流式让用户在生成时就看到：

```python
gen = agent.input(user_text).get_generator(type="delta")
for delta in gen:
    print(delta, end="", flush=True)
```

流式选项见 [模型响应](../requests/model-response.md)。

### 加结构化旁路

UI 需要知道哪个 action 跑了（高亮某行、动画等），每轮后读 `agent.get_action_result()`：

```python
records = agent.get_action_result()
for r in records:
    notify_ui(action=r.name, args=r.input, result=r.output)
```

### 单轮多步

单条用户消息触发多步过程（lookup → confirm → apply）时，把每轮处理升到 TriggerFlow。对话层仍在 agent；flow 在一轮内跑。见 [TriggerFlow 编排 Playbook](../playbooks/triggerflow-orchestration.md)。

## 交叉链接

- [Action Runtime](../actions/action-runtime.md) —— `@agent.action_func` 与 `use_actions`
- [会话记忆](../requests/session-memory.md) —— `activate_session()`、窗口裁剪、自定义 memo
- [Async First](../start/async-first.md) —— 上面循环的 async 等价
