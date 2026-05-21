# OpenAICompatible Settings Cookbook（通用：接入任意 OpenAI-compatible 服务）

目标：用**统一的配置结构**接入各种 OpenAI-compatible / 内网网关 / 代理服务，避免把 skill 写死在某个 provider 上。

来源：
- `agently-exmaples/model_configures/*`
- 本仓库 demo 的 `.env` + ASGI stub 思路（离线回归）

---

## 1) 最小配置（base_url + model）

```py
from agently import Agently

Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "https://my-server/v1",
        "model": "my-model",
        "options": {"temperature": 0.2},
    },
)
agent = Agently.create_agent()
```

建议：
- `base_url` 统一写到 `/v1`（OpenAI-compatible 的常见约定）。
- 把“会变”的东西（base_url/model/auth）放 env，不要硬编码到代码里。

---

## 2) 鉴权：标准 token（最常见）

> 具体字段名取决于你的 OpenAICompatible 实现；通常可直接把 token 放进 `auth`。

安全提示：
- **不要把真实 key 写进代码/仓库**；优先从环境变量读取。
- 不要在 `debug` 日志/trace 中打印 `auth` 或请求 header。

```py
import os

Agently.set_settings(
  "OpenAICompatible",
  {
    "base_url": "https://my-server/v1",
    "model": "my-model",
    "auth": os.environ.get("OPENAI_COMPAT_API_KEY", ""),
  },
)
```

---

## 3) 鉴权：自定义 Header（内网网关常见）

适用：需要自定义 `Authorization: Customize ...`，或额外 header token。

```py
Agently.set_settings(
  "OpenAICompatible",
  {
    "base_url": "https://my-server/v1",
    "model": "my-model",
    "auth": {
      "headers": {
        "Authorization": "Customize <My-Token>",
      }
    },
    "options": {"temperature": 0.7},
  },
)
```

要点：
- 这是“配置形态”抽象：不要写死某个厂商 header 名。
- 如果你要做回归测试：不要在仓库里提交真实 token。

---

## 4) 鉴权：自定义 Body 字段（更偏网关/代理）

适用：某些服务要求 token 在请求 body 里，例如 `X-User-Token`。

```py
Agently.set_settings(
  "OpenAICompatible",
  {
    "base_url": "https://my-server/v1",
    "model": "my-model",
    "auth": {
      "body": {
        "X-User-Token": "<My-Token>",
      }
    },
  },
)
```

变体：
- 有的实现允许你把自定义字段直接放在 `options` 里（本质也是“把额外字段带入请求”）。

---

## 5) `base_url` vs “full url”（当服务不是标准 /v1）

适用：某些兼容层把路径做成非标准形式（或你需要指定一个更完整的 URL）。

建议：
- **优先用 `base_url`**，保持一致性与可迁移性；
- 确有必要时，才在配置中声明“全路径模式”（具体字段名以 OpenAICompatible 实现为准）。

---

## 6) embeddings（RAG 必备：model_type）

典型模式：用单独的 embedding agent（`model_type="embeddings"`）给 KB/Chroma 做向量化。

```py
embedding = Agently.create_agent()
embedding.set_settings(
  "OpenAICompatible",
  {
    "base_url": "https://my-server/v1",
    "model": "my-embedding-model",
    "model_type": "embeddings",
    "auth": os.environ.get("OPENAI_COMPAT_API_KEY", ""),
  },
)
```

建议：
- embedding 与 chat 模型分开配置（不同模型、不同限流、不同计费）。

---

## 7) 离线回归（强烈推荐）

目标：不依赖外网/真实 key，也能跑通：
- schema/ensure_keys
- streaming（instant/delta 的解析链路）
- 服务化 SSE 的协议正确性

做法（推荐）：
- 在测试里启动 OpenAI-compatible stub（ASGI），通过 `httpx.ASGITransport(app=stub)` 把请求路由到本地。
- 用环境变量开关启用（例如 `AGENTLY_OFFLINE_STUB=1`），CI 默认跑离线回归。

对应策略见：
- `references/testing-strategy.md`
