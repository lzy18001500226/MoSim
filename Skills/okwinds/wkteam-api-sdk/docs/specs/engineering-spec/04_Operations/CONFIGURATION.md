# Configuration Specification（SDK）

> 说明：本仓库交付的是 “wkteam-api-wen-dang2” 的客户端 SDK（npm 包）。
> 因此本章节的“配置”主要指：**SDK 初始化配置**、**运行时可注入依赖**、以及本仓库的 **集成测试/示例** 所需环境变量。

## 1. 配置层级（优先级从高到低）

1) **代码显式传入**（`new WkteamClient(config)` / `createClient(config)`）
2) **运行时注入依赖**（`transport` / `logger` / hooks 等）
3) **环境变量（仅用于本仓库集成测试与示例）**
4) **默认值**

> 约束：SDK 作为库不应强依赖 `.env`；`.env` 仅用于仓库内的 `integration tests` 与示例脚本。

## 2. 配置注册表（Configuration Registry）

### 2.1 核心配置（必需/强烈建议）

| Config Key | Type | Default | Env Var（仅仓库用） | Secret | 变更生效 | 说明 |
|---|---|---:|---|---|---|---|
| `baseUrl` | `string` | - | `WKTEAM_BASE_URL` | No | 立即 | API 基地址。离线文档使用 `http://域名地址/...` 占位，必须由使用方配置。要求：无尾 `/`（SDK 内部可做归一化）。 |
| `authorization` | `string \| (() => string \| Promise<string>)` | - | `WKTEAM_AUTHORIZATION` | Yes | 立即 | 请求头 `Authorization` 的原始值。允许传入函数以支持刷新/动态读取。 |
| `authorizationHeaderName` | `string` | `Authorization` | `WKTEAM_AUTH_HEADER_NAME` | No | 立即 | 少数网关可能改名（不建议）。 |
| `authorizationPrefix` | `string \| null` | `null` | `WKTEAM_AUTH_PREFIX` | No | 立即 | 是否自动为 `authorization` 添加前缀（如 `Bearer `）。默认不添加，避免与上游期望冲突。 |

### 2.2 请求行为（超时/重试/并发）

| Config Key | Type | Default | Env Var（仅仓库用） | Secret | 变更生效 | 说明 |
|---|---|---:|---|---|---|---|
| `timeoutMs` | `number` | `15000` | `WKTEAM_TIMEOUT_MS` | No | 立即 | 单次请求超时。实现阶段使用 `AbortController`。 |
| `retry.enabled` | `boolean` | `true` | `WKTEAM_RETRY_ENABLED` | No | 立即 | 是否启用重试（仅对“安全类别”默认生效，详见 ADR-004）。 |
| `retry.maxAttempts` | `number` | `2` | `WKTEAM_RETRY_MAX_ATTEMPTS` | No | 立即 | 最大尝试次数（含首次）。默认 2 = 1 次重试。 |
| `retry.backoffMs` | `number \| ((attempt:number)=>number)` | `200` | `WKTEAM_RETRY_BACKOFF_MS` | No | 立即 | 退避策略（固定/函数）。 |
| `retry.retryOn` | `('network' \| 'timeout' \| 'http5xx' \| 'http429')[]` | `['network','timeout','http5xx']` | `WKTEAM_RETRY_ON` | No | 立即 | 重试触发条件集合。 |
| `concurrency` | `number \| null` | `null` | `WKTEAM_CONCURRENCY` | No | 立即 | 并发上限（`null` 表示不限制）。用于批量接口/工具方法。 |

### 2.3 可观测性（日志/事件/脱敏）

| Config Key | Type | Default | Env Var（仅仓库用） | Secret | 变更生效 | 说明 |
|---|---|---:|---|---|---|---|
| `logLevel` | `'silent'\|'error'\|'warn'\|'info'\|'debug'` | `info` | `WKTEAM_LOG_LEVEL` | No | 立即 | SDK 内部日志等级。 |
| `logger` | `{ debug/info/warn/error }` | `console` | - | No | 立即 | 注入日志器（建议接入应用方日志系统）。 |
| `redaction.enabled` | `boolean` | `true` | `WKTEAM_REDACT_ENABLED` | No | 立即 | 是否对敏感信息脱敏输出。 |
| `redaction.headers` | `string[]` | `['authorization','cookie']` | - | No | 立即 | 需要脱敏的 header（大小写不敏感）。 |
| `redaction.jsonPaths` | `string[]` | 见默认 | - | No | 立即 | 请求/响应体脱敏路径（实现阶段以简单规则或 jsonpath 形式落地）。 |
| `hooks` | `object` | `{}` | - | No | 立即 | 生命周期 hook：`onRequest/onResponse/onRetry/onError`（详见 `MONITORING.md`）。 |

### 2.4 传输层注入（Transport）

| Config Key | Type | Default | Env Var（仅仓库用） | Secret | 变更生效 | 说明 |
|---|---|---:|---|---|---|---|
| `transport` | `(req) => Promise<resp>` | `fetch` wrapper | - | No | 立即 | 可注入以支持：代理、mTLS、自定义 header、mock、在非 Node 环境使用 axios/undici 等。 |
| `defaultHeaders` | `Record<string,string>` | `{}` | - | No | 立即 | 追加到每个请求的默认 header（不应覆盖 `Authorization`）。 |
| `userAgent` | `string \| null` | `wkteam-sdk/<version>` | - | No | 立即 | User-Agent（在 Node fetch 中作为普通 header 发送）。 |

### 2.5 异步/轮询类接口的统一配置（可选）

离线文档中存在“异步发送/异步下载”等接口（典型模式：发起任务 → 轮询查询结果）。SDK 将提供可复用的 `pollUntil` helper。

| Config Key | Type | Default | 说明 |
|---|---|---:|---|
| `polling.initialDelayMs` | `number` | `500` | 首次轮询等待 |
| `polling.intervalMs` | `number` | `1000` | 轮询间隔 |
| `polling.timeoutMs` | `number` | `60000` | 轮询总超时 |
| `polling.maxAttempts` | `number \| null` | `null` | 最大轮询次数（`null` 由 timeout 控制） |

## 3. 本仓库环境变量规范（仅用于集成测试/示例）

> 目的：让维护者能在本地/CI 里用真实环境验证连通性与关键路径；默认不在 CI 强制执行（避免泄露密钥）。

| Env Var | Required | Example | 说明 |
|---|---:|---|---|
| `WKTEAM_INTEGRATION` | No | `1` | 置为 `1` 时才运行集成测试（默认跳过）。 |
| `WKTEAM_BASE_URL` | Yes（集成） | `https://api.example.com` | API baseUrl |
| `WKTEAM_AUTHORIZATION` | Yes（集成） | `xxxxx` | Authorization 原始值 |
| `WKTEAM_AUTH_PREFIX` | No | `Bearer ` | 自动前缀（可空） |
| `WKTEAM_TIMEOUT_MS` | No | `15000` | 超时 |
| `WKTEAM_LOG_LEVEL` | No | `debug` | 日志级别 |

## 4. `.env.example`（规范）

本仓库实现阶段必须提供 `.env.example`（不包含真实密钥），至少包含上表字段，并在 `README.md` 中说明：
- 如何启用集成测试
- 如何避免把 `.env` 提交到仓库

## 5. 配置校验（实现要求）

为降低运行时隐性错误，SDK 初始化时必须做最小校验并抛出 `ValidationError`：
- `baseUrl` 非空且是 http(s) URL
- `authorization` 非空（若某些接口无需鉴权，则允许调用时覆盖/跳过，但默认应要求存在）
- `timeoutMs/retry.maxAttempts` 为正整数（边界：0 表示禁用）

所有校验规则必须写入单元测试，并在 `TEST_PLAN.md` 中可追溯。
