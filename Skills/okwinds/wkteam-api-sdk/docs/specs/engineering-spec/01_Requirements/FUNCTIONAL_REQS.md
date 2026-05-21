# Functional Requirements

> 注：本文件列出“必须实现/必须定义清楚”的功能需求。具体到每个 endpoint 的 method/path/参数/返回请以 `02_Technical_Design/API_SPEC.md` 与 `02_Technical_Design/schemas/api_catalog.json` 为准。

## FR-BASIC-001：配置与多环境

**Source:** US-001 | **Priority:** P0

**Description:** SDK 必须支持配置 `baseUrl`、timeout、logger、重试策略、Authorization 注入策略，并允许按环境切换（dev/staging/prod）。

**Acceptance Criteria:**
- [ ] baseUrl 必填，缺失时本地报错（不发请求）
- [ ] 支持覆盖默认 timeout/retry

## FR-BASIC-002：统一请求管线（request pipeline）

**Source:** US-001/US-004 | **Priority:** P0

**Description:** 所有 endpoint wrapper 经过统一的 request pipeline：参数校验 → 构造请求 → 注入 headers → 发送 → 解析响应 → 错误归类。

**Acceptance Criteria:**
- [ ] 参数缺失/类型不合法在本地抛 `ValidationError`
- [ ] HTTP 非 2xx 抛 `HttpError`
- [ ] JSON 解析失败抛 `ParseError`
- [ ] 业务 code 失败抛 `ApiBusinessError`

## FR-AUTH-001：登录获取 Authorization

**Source:** US-002 | **Priority:** P0

**Description:** SDK 必须封装登录接口（至少包含文档中 `member/login` 等），并输出 Authorization。

**Acceptance Criteria:**
- [ ] 登录成功时返回 Authorization（或包含在 data 内）可被 SDK 使用
- [ ] 登录失败时错误可读且结构化

## FR-AUTH-002：Authorization 注入

**Source:** US-001/US-002 | **Priority:** P0

**Description:** SDK 能将 Authorization 注入到需要鉴权的请求头；允许使用方外部管理 token 并注入 SDK。

**Acceptance Criteria:**
- [ ] 默认使用 token 原文
- [ ] 支持配置前缀（如 `Bearer `）
- [ ] 日志中默认脱敏

## FR-CATALOG-001：endpoint catalog 与覆盖性核验

**Source:** US-003 | **Priority:** P0

**Description:** 必须在仓库内维护机器可读的 endpoint catalog，并可生成覆盖性报告，保证离线文档中的 endpoint 不会漏实现。

**Acceptance Criteria:**
- [ ] `02_Technical_Design/schemas/api_catalog.json` 存在并可由工具生成
- [ ] 覆盖性报告能列出解析缺失与异常条目

## FR-MODULE-001：模块化组织

**Source:** US-003 | **Priority:** P0

**Description:** SDK 的代码组织需与离线文档模块大体一致（消息发送/接收、好友、群、朋友圈、视频号、标签、收藏夹、工具箱、账户管理），并提供清晰命名与 import 路径。

**Acceptance Criteria:**
- [ ] 每个模块有统一前缀/命名规则（见 `02_Technical_Design/ARCHITECTURE.md`）
- [ ] 模块边界清晰（core/auth/modules/webhook）

## FR-CALLBACK-001：回调解析与去重建议

**Source:** US-006 | **Priority:** P0

**Description:** SDK 必须提供回调 payload 的类型定义与解析工具，并明确“重复推送”场景的去重建议（例如按 `newMsgId/timestamp`）。

**Acceptance Criteria:**
- [ ] 提供 callback payload 类型
- [ ] 提供示例与去重策略建议（不强制存储层实现）
