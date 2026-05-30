# Python SDK Architecture（Python 3.11）

## Goal

在同一仓库中交付 `wkteam api-wen-dang2` 的 **Python 3.11 SDK**，满足“工程可用”目标：

- **全量 endpoint wrapper**：覆盖 `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json` 中 `kind='endpoint'` 的全部 `operationId`（当前 127 个）。
- **一致的请求管线**：配置校验 → 构建请求 → transport → 解析 envelope → 错误映射 → 重试/幂等风险控制 → hook/日志（脱敏）。
- **可离线回归**：默认用 fake transport 做单元测试与覆盖性护栏；集成测试以环境变量开关控制（默认跳过）。
- **可复制使用**：SDK 源码与生成物收敛在单一源代码文件夹，便于直接引用/复制。

## Constraints

- `baseUrl`、`Authorization` 等运行时信息 **无法从离线文档推断**，必须全部做成 SDK 配置项（见 `04_Operations/CONFIGURATION.md`）。
- SDK 作为库 **不依赖** `.env`；`.env` 仅用于本仓库的集成测试与示例。
- 不做“伪精确”类型推断：离线文档的参数/返回字段不完备时，Python SDK 的类型注解以 `Any/Mapping[str, Any]` 为主，并在 docstring 保留原文说明。

## Repo Layout（Python SDK）

> 约束：所有运行时代码收敛在一个源代码文件夹（用户要求）。

- `src/python-sdk/`
  - `pyproject.toml`：Python SDK 的打包/依赖/工具配置（版本固定）。
  - `README.md`：Python SDK 使用说明（安装/初始化/示例/开发命令）。
  - `wkteam_api_sdk/`：**唯一**源码目录（可直接复制使用）
    - `__init__.py`：公共导出入口。
    - `client.py`：对外 client（sync/async），挂载 `client.api.*` 全量 wrapper。
    - `core_client.py`：请求管线（transport/重试/错误/解析/并发限制）。
    - `config.py`：配置结构、默认值、校验与归一化。
    - `errors.py`：统一错误类型（Network/Timeout/Http/Business/Parse/Validation）。
    - `hooks.py`：生命周期 hook 的事件结构（可选；也可直接使用 `config.Hooks`）。
    - `redaction.py`：脱敏规则（至少 header 的 Authorization）。
    - `polling.py`：`poll_until` helper（sync/async）。
    - `callbacks.py`：回调 payload 解析与去重 key helper（reference 文档）。
    - `generated_api.py`：由 codegen 生成的模块化 wrapper（不要手改）。
    - `manifest.py`：由 codegen 生成的 operationId 与 endpoint 元数据（用于覆盖性测试）。
  - `tests/`：pytest 离线回归（覆盖性护栏 + 请求/解析/重试/脱敏）。
  - `tools/`：生成器（从 `api_catalog.json` 生成 `wkteam_api_sdk/generated_api.py` 与 `manifest.py`）。

## Key Components

| Component | Purpose | Contract | Notes |
|---|---|---|---|
| `WkteamClient` | 同步对外入口 | `WkteamClient(config).api.<module>.<method>(...)` | 适合脚本/后端同步调用 |
| `AsyncWkteamClient` | 异步对外入口 | `await AsyncWkteamClient(config).api...` | 兼容 asyncio 应用 |
| `WkteamCoreClient` | 请求管线 | `call(endpoint_def, params, options)` | 不暴露 httpx 细节给 wrapper |
| `Transport` | 发送 HTTP 请求 | 可注入 interface | 默认基于 httpx；测试用 fake transport |
| `manifest` | 覆盖性与可观测性 | `operation_ids` + `endpoint_defs` | AT-008 的权威对照 |
| `generated_api` | 模块化 wrapper | `client.api.<module>` | 由 `tools/generate_sdk.py` 生成 |

## Naming & Module Conventions（Python）

- module：来自离线文档目录（例如 `xiao-xi-fa-song`），Python attribute 采用 `snake_case`（`xiao_xi_fa_song`）。
- method：优先使用 endpoint path（例如 `/addContactLabel` → `add_contact_label`）；无法从 path 得到时使用 `operationId` 去掉 module 前缀后的部分并转 snake。
- `operationId`：保持与 `api_catalog.json` 完全一致（用于日志、错误上下文、覆盖性测试）。

## Coverage Gate（AT-008）

Python SDK 必须实现离线回归测试：

- 读取 `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json` 中所有 `kind='endpoint'` 的 `operationId`
- 读取 Python SDK 导出的 `wkteam_api_sdk.manifest.operation_ids`
- 断言集合一致（默认不允许白名单）

该 gate 是“接口不漏”的硬约束，与 TypeScript SDK 的 gate 保持一致。
