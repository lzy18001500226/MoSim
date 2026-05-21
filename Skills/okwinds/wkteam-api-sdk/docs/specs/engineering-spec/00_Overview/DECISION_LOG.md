# Architecture Decision Log（ADR）

> 说明：本项目先规格后实现。以下 ADR 在规格阶段先给出“推荐选项”，实现前允许再次确认，但必须保留变更记录与影响评估。

## ADR-001：SDK 主要语言与发布形态

**Date:** 2026-02-10 | **Status:** Accepted

### Context

API 面大（>100 endpoint），参数/返回字段多，长期维护需要强类型与自动化回归；同时使用方多为后端集成场景。

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| A: TypeScript SDK（npm 包） | 类型系统强；生态完善；易集成 | Node 版本约束；浏览器支持需明确 |
| B: Python SDK（pip 包） | 数据集成常用；部署简单 | 类型表达弱一些；需要额外维护链路 |
| C: Go SDK | 性能好、部署简单 | 生态与接口面维护成本较高 |

### Decision

优先交付 **TypeScript SDK（npm 包）**，并在架构上保留“可移植模型”（API catalog + 类型生成/映射），便于后续扩展多语言。

### Consequences

- 需要明确 Node 最低版本与 ESM/CJS 兼容策略
- 需要设计“可注入 HTTP transport”，避免强绑运行时

## ADR-002：HTTP Client 选型与可注入传输层

**Date:** 2026-02-10 | **Status:** Accepted

### Context

SDK 需要兼顾不同运行环境（Node / 未来可能浏览器 / serverless）。文档未给出特殊签名算法，主要是 HTTP + JSON。

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| A: 原生 `fetch`（transport 可注入） | 依赖最少；可跨运行时 | 某些能力需自行封装（超时、重试） |
| B: axios | 生态成熟、功能全 | 依赖更重；运行时耦合；类型细节需额外维护 |
| C: undici 直接使用 | Node 性能与控制更强 | 非 Node 环境复用性差 |

### Decision

默认使用 `fetch`，并将 transport 设计为 **可注入接口**（便于 mock、代理、替换 axios/undici）。

### Consequences

- SDK 需要自行实现超时、重试、日志、错误分类等中间件能力

## ADR-003：成功/失败判定与错误模型

**Date:** 2026-02-10 | **Status:** Accepted

### Context

离线文档中大量接口以 `code == 1000` 表示成功，`1001` 表示失败，但不排除存在差异（字段名 `message` vs `msg` 等）。

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| A: 固定判定（`code == 1000`） | 实现简单 | 一旦接口差异会误判 |
| B: 允许 per-endpoint 覆盖 | 兼容差异；可渐进完善 | catalog 与实现复杂度上升 |

### Decision

采用 **默认规则 + endpoint 级覆盖**：
- 默认：`code == 1000` 成功
- 允许在 API catalog 中对特定 endpoint 配置成功判定/字段映射

错误模型分层：
- `NetworkError`、`HttpError`、`ApiBusinessError`、`ParseError`、`ValidationError`

### Consequences

- 需要在工程规格中定义统一 error contract（字段、序列化、可观测性）

## ADR-004：重试策略与幂等风险控制

**Date:** 2026-02-10 | **Status:** Accepted

### Context

消息发送、群操作等接口可能产生副作用。文档未给出幂等 key 机制。

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| A: 默认重试（网络错误就重试） | 稳定性更好 | 副作用重放风险 |
| B: 默认不重试，使用方自行处理 | 安全 | 需要更多业务方实现 |
| C: 分类重试（只对“明确安全”的接口重试） | 折中 | 需要分类与维护 |

### Decision

采用 **分类重试**：
- 默认：对网络超时/连接错误最多 1 次重试（可关闭）
- 对“可能产生副作用”的接口默认不重试（消息发送/群管理等），除非使用方显式启用
- 所有重试策略必须可配置（全局与 endpoint 级）

### Consequences

- 需要在 `API_SPEC.md` / catalog 中给出 endpoint 分类字段（实现阶段落地）

## ADR-005：Endpoint Wrapper 的规模化落地方式（Codegen vs 通用请求）

**Date:** 2026-02-10 | **Status:** Accepted

### Context

离线文档解析得到 127 个 endpoint（见 `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json`）。若纯手写封装：
- 极易遗漏与漂移
- review 成本高
- 难以保证“文档变更后”快速同步

同时，文档中的请求参数/返回结构存在不一致与不确定性，SDK 需要允许渐进完善（先保证 endpoint 可调用 + 统一错误/可观测性，再逐步增强类型与校验）。

### Options Considered

| Option | Pros | Cons |
|---|---|---|
| A: 运行时通用 `request(operationId, params)` + 少量手写薄封装 | 开发快；可先跑通 | IDE 发现性差；参数/返回类型弱；长期维护容易“越写越散” |
| B: 基于 catalog 的 **编译期代码生成（codegen）** | 不漏接口；方法/模块可发现；可自动生成 manifest 与覆盖性测试输入 | 需要维护生成器；生成代码需要稳定格式与 diff 控制 |

### Decision

选择 **B：编译期 codegen**。

实现策略（实现阶段必须满足）：
- `src/typescript-sdk/tools/generate_api_artifacts.mjs` 负责生成 catalog 与覆盖报告
- `src/typescript-sdk/tools/generate_sdk.mjs`：
  - 从 `api_catalog.json` + `docs/api/` 提取 endpoint 元数据（method/path/参数表）
  - 生成 `src/typescript-sdk/src/generated/**`：模块方法、operationId 清单、（可选）zod 校验器与 TS 类型
- SDK 运行时代码（`src/core/**`）只负责：transport、错误、解析、hook、脱敏、重试
- 覆盖性门槛（AT-008）以“catalog endpoint 集合 == SDK manifest 集合”为准

### Consequences

- 需要在仓库中明确“生成流程”的可复现命令（见 `04_Operations/DEPLOYMENT.md`）
- 生成器必须稳定（同输入产生同输出），避免无意义 diff
- 对无法可靠推断的字段类型：优先生成 `unknown` 并保留原文说明，避免伪精确

## ADR-006：Python SDK 的交付形态与 HTTP Client 选型

**Date:** 2026-02-10 | **Status:** Accepted

### Context

用户要求在同一仓库中额外交付 **Python 3.11** SDK，并且目标同 TypeScript：接口全覆盖、可离线回归、可配置的鉴权/超时/重试/并发限制、以及日志脱敏与 hook。

同时，用户明确：
- `baseUrl`、`Authorization` 等信息无法从离线文档推断（实际来自平台登录/后台登录返回），因此必须做成配置项。

### Options Considered

| Option | Pros | Cons |
|---|---|---|
| A: requests（sync only） | 依赖小；使用广泛 | 无 async；后续扩展需要再引入 aiohttp/httpx |
| B: aiohttp（async only） | async 生态成熟 | 仅 async；对同步集成不友好；抽象成本更高 |
| C: **httpx（sync + async）** | 同一套 API 同时覆盖 sync/async；timeout/transport 抽象清晰；易于注入 mock | 依赖略重；需要明确版本锁定 |

### Decision

选择 **C：httpx**，并在 Python SDK 中提供两套入口：
- `WkteamClient`（sync）
- `AsyncWkteamClient`（async）

两者共享同一份生成的 endpoint wrapper 与 manifest（以 `operationId` 为准），并通过 pytest 落地 AT-008 的“覆盖性门槛”（catalog 与 manifest 集合一致）。

### Consequences

- Python SDK 将新增 `src/python-sdk/` 子项目：
  - 所有运行时代码收敛在一个源代码文件夹：`src/python-sdk/wkteam_api_sdk/`
  - 生成物（wrappers/manifest）也位于该文件夹中，避免跨目录引用导致分发困难
- 与 TypeScript SDK 一致：不在 SDK 内强行实现 token 刷新，仅支持 `authorization` 作为字符串或函数（sync/async）由使用方控制
