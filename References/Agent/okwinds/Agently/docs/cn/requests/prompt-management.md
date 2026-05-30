---
title: Prompt 管理
description: 分层 prompt 槽位、agent 与 request 作用域、YAML/JSON 加载与占位符。
keywords: Agently, prompt, role, system, info, instruct, input, configure_prompt
---

# Prompt 管理

> 语言：[English](../../en/requests/prompt-management.md) · **中文**

Agently 把 prompt 拆成命名槽位。槽位可组合，所以 agent 级持久内容只设一次，请求级槽位每次按需填。

## 槽位映射

| 槽位 | 落在哪 | 典型用途 |
|---|---|---|
| `role` / `system` | system 消息 | 角色、能力边界 |
| `info` | system 或 user（实现细节） | 背景事实、目录、工具清单 |
| `instruct` | user 消息 | 这类请求的步骤指令 |
| `input` | user 消息 | 实际问题或 payload |
| `output` | user 消息 + parser | 期望的返回结构 |

agent 级持久设置：

```python
agent = (
    Agently.create_agent()
    .role("你是 Agently 客服助手。", always=True)
    .info({"product": "Agently 4.x"}, always=True)
)
```

`always=True` 表示该槽位停留在 agent 级，每次请求都带。

请求级单次设置：

```python
result = (
    agent
    .instruct(["回复不超过 80 字。", "不要编造产品名。"])
    .input("怎么配置一个模型？")
    .output({"answer": (str, "answer", True)})
    .start()
)
```

这里 `instruct(...)` 没传 `always=True`，所以仅本次请求生效。

## Agent vs Request 作用域

| 作用域 | API |
|---|---|
| Agent（每次请求都生效） | `.role(...)`、`.info(...)`、`.instruct(...)`、`.set_agent_prompt(key, value)` |
| Request（仅一次） | `.input(...)`、`.output(...)`、`.set_request_prompt(key, value)` |

同一作用域内最后一次设置覆盖前面，所以可以在单次请求里覆盖 agent 默认值，而不修改 agent。

## YAML / JSON prompt 文件

同一套槽位模型，声明式写法：

```yaml
# prompts/triage.yaml
$ensure_all_keys: true
.agent:
  system: 你是一个工单分流助手。
  info:
    severities: ["P0", "P1", "P2", "P3"]
.request:
  instruct: 对工单文本分类。
  output:
    severity:
      $type: str
      $desc: P0/P1/P2/P3 之一
      $ensure: true
    rationale:
      $type: str
      $desc: 一行说明原因
      $ensure: true
```

加载：

```python
agent = Agently.create_agent().load_yaml_prompt("prompts/triage.yaml")

result = (
    agent
    .set_request_prompt("input", "EU 区域所有用户登录失败。")
    .start()
)
```

`load_json_prompt(...)` 是 JSON 版本的同一 API。两者都接受路径或原始字符串。可以一份配置一个 prompt，也可以用 `prompt_key_path="demo.output_control"` 在多 prompt 文件里挑一个。

顶层 `$ensure_all_keys: true` 会强制所有叶子都必填，覆盖每叶子的 `$ensure`。整个 schema 必须完整返回时使用。

## 往返转换

可以把代码里组装的 prompt 转成 YAML/JSON 用于 review 或存储：

```python
agent.role("你是 Agently 助手。", always=True).input("打个招呼。").output({
    "reply": (str, "reply", True),
})
print(agent.get_yaml_prompt())
print(agent.get_json_prompt())
print(agent.get_prompt_text())  # 模型实际看到的渲染文本
```

这种往返是把「我以为我在发」与「框架实际发的」对上的标准方式。

## 占位符

prompt 槽位中：`{name}` 引用另一个槽位的 key；`${name}` 在加载时由 `mappings={"name": "value"}` 替换。常见用法：

- `instruct: "Reply {input} politely."` — 把请求的 `input` 拉进 instruct。
- `${ENV.OPENAI_API_KEY}` 是**设置**层的环境变量替换，不是 prompt 的；prompt 用 `${name}` + 显式 mappings。

加载时触发 `${...}` 替换：

```python
agent.load_yaml_prompt(yaml_text, mappings={"product_name": "Agently"})
```

## 每层 prompt 的来源

请求实际发出时，Agently 按以下顺序合并 prompt：

1. Agent 级槽位（`always=True` 或 `set_agent_prompt`）
2. Request 级槽位（不带 `always=True`）
3. 框架扩展或应用代码填入的槽位（Session 注入 chat history；检索代码通常把片段放进本次请求的 `info(...)`）

发送前用 `agent.get_prompt_text()` 看合并结果。

## 另见

- [Schema as Prompt](schema-as-prompt.md) — 叶子 authoring 与 `$ensure`
- [输出控制](output-control.md) — 解析之后的事
- [项目结构](../start/project-framework.md) — 多 prompt 项目的目录布局
