---
title: Schema as Prompt
description: 用嵌套 dict + 类型化叶子 + ensure 标记表达结构化输出。
keywords: Agently, schema, output, ensure, type, description, YAML
---

# Schema as Prompt

> 语言：[English](../../en/requests/schema-as-prompt.md) · **中文**

Agently 的 `.output(...)` 是 **prompt-native**：你写的结构既会被渲染成给模型的文本提示，也会作为返回的 parser/validator。无需另外维护 JSON Schema —— 同一份嵌套 dict 同时驱动两端。

## 叶子

叶子是元组：

```python
(TypeExpr, "description", True)
```

| 槽 | 含义 |
|---|---|
| 1. `TypeExpr` | Python 类型、typing 表达式、`Enum`、`BaseModel`，或字符串 token 如 `"str"`、`"list[str]"` |
| 2. description | 给模型与人的软提示 |
| 3. ensure | `True` 表示必填，会写入 `ensure_keys` |

> 第三槽是 **ensure 标记**，不是默认值。旧的「第三槽 = default value」约定已不再支持，YAML 的 `$default` 也已移除。

简写形式：

```python
(str,)                         # 仅类型
(str, "简短描述")              # 类型 + 描述
"仅描述"                       # 等价于 (Any, "仅描述")
```

## Object 与 array 节点

dict 与 list 嵌套组合：

```python
{
    "title": (str, "文章标题", True),
    "tags": [(str, "标签", True)],
    "sections": [
        {
            "heading": (str, "标题", True),
            "body": (str, "正文", True),
        }
    ],
}
```

| 容器 | 含义 |
|---|---|
| `dict` | object 节点——字段顺序保留且有语义 |
| `list` 单个元素 | 同质数组——只写**一个** prototype |
| `list` 多个元素 | 例子/示意；标准写法只放一个 prototype |

## 字段顺序是契约的一部分

模型按你定义的顺序输出字段。如果你显式暴露 `notes`、`analysis` 这类字段，它们会排在 `answer` 前面并被下游消费。换序就是换行为——不存在「模型自己摸出来」的最佳顺序。不要要求模型输出隐藏推理过程；只暴露业务上确实要保存的字段。

## ensure 编译为 ensure_keys

第三槽每个 `True` 都把对应叶子的路径写进解析时的 `ensure_keys`：

```python
{
    "title": (str, "标题", True),
    "items": [
        {
            "name": (str, "名称", True),
            "value": (str, "值"),  # 不强制
        }
    ],
}
```

编译为：

```python
ensure_keys = ["title", "items[*].name"]
```

数组通配 `items[*]` 是路径语法的一部分。如果解析后 `title` 缺失或任意 `items[i].name` 缺失就触发重试（受 `max_retries` 限制）。`value` 允许缺失。

要求「整套 schema 都必须回来」时，agent 上设 `ensure_all_keys: True`，或 YAML/JSON prompt 顶层 `$ensure_all_keys: true` —— 它覆盖每叶子的 `ensure`。

## YAML / JSON 写法

```yaml
output:
  title:
    $type: str
    $desc: 标题
    $ensure: true
  items:
    $type:
      - name:
          $type: str
          $desc: 名称
          $ensure: true
        value:
          $type: str
          $desc: 值
```

约定：

- `$type` —— 类型表达（字符串 token 或嵌套结构）
- `$desc` —— 描述
- `$ensure: true`（或 `$ensure: 1`）—— ensure 标记
- 别名 `.type` / `.desc` 也被 loader 接受，但推荐 `$` 前缀

`$default` **不再支持** —— default 已不属于 authoring。

## YAML 类型 token

常用字符串 token：

| Token | 含义 |
|---|---|
| `"str"`、`"int"`、`"bool"`、`"float"` | 标量 Python 类型 |
| `"list[str]"`、`"dict[str, int]"` | typing 风格 |
| `"Literal[open, closed]"` | 字面量 |
| `"Optional[str]"` | 可选类型 |

## Pydantic 与 Enum

`TypeExpr` 允许 Pydantic 模型与 Enum：

```python
from enum import Enum
from pydantic import BaseModel

class Severity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"

class Ticket(BaseModel):
    severity: Severity
    rationale: str

agent.output(Ticket)  # 等价于把 BaseModel 展开为嵌套叶子
```

当 `output()` 接收的是 `BaseModel` 时，response 的 `get_data_object()` 会返回 Pydantic 实例。

## 纯文本

需要纯文本而不是结构化输出时，**不要**用 `output()` —— `agent.input("...").start()` 直接返回字符串，或 `response.result.get_text()`。Schema as Prompt 是给结构化输出用的。

## 不在范围内

Schema as Prompt 是单次模型请求的 **authoring** 层，不是：

- JSON Schema 在外部 API 契约场景的替代。
- TriggerFlow 的契约（TriggerFlow 用自己的 `set_contract(...)`）。
- UI 表单定义。

早期把 `.output()`、TriggerFlow 契约和外部 schema 统一为同一 DSL（"Agently DSL"）的尝试已归档。每个消费者保留自己的入口；本页只覆盖 prompt 侧的 authoring。

## 另见

- [输出控制](output-control.md) —— 解析之后的事
- [Prompt 管理](prompt-management.md) —— 槽位与 YAML/JSON 加载
- [术语表：ensure](../reference/glossary.md#ensure第三槽)
