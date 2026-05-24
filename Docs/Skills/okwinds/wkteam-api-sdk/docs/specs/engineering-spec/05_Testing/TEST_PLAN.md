# Test Plan（SDK：离线回归优先 + 可选集成验证）

> 目标：把 “离线 API 文档” 变成可回归的 SDK 能力。  
> 核心约束：默认测试 **不依赖外网/真实密钥**；真实环境验证仅作为可选集成测试。

## 1. 测试分层与范围

| Level | 范围 | 必须 | 主要覆盖点 | 建议框架 |
|---|---|---:|---|---|
| Unit（离线） | 纯函数/模块/客户端方法 | ✅ | URL 拼接、鉴权注入、参数校验、响应解析、错误映射、重试判定、脱敏 | Vitest |
| Contract（离线） | “请求/响应契约”验证 | ✅ | 与 `API_SPEC.md` / catalog 一致性、operationId 稳定性 | Vitest |
| Integration（可选） | 真实 baseUrl + token | ⚠️ | 连通性、真实返回结构差异、隐藏契约补齐 | Vitest（标记） |
| Example/Smoke（可选） | 示例脚本 | ⚠️ | 最短路径演示与文档正确性 | node script |

> 本 SDK 没有传统 E2E（无 UI / 无服务端）。如果使用方需要端到端业务流，应在其应用层编写。

## 2. 测试原则（必须遵守）

1) **离线可复现是硬门槛**：任何核心逻辑必须能通过注入 `transport` 在本地完全回归。
2) **不把真实 token 写入仓库**：集成测试通过环境变量注入，默认跳过。
3) **失败可诊断**：断言失败时应输出 `operationId/requestId/httpStatus/apiCode` 等关键字段（脱敏后）。
4) **覆盖性防遗漏**：必须有测试确保“catalog 中的 endpoint 清单”在 SDK 中有对应 wrapper（US-008）。

## 3. 测试环境与开关

### 3.1 本地/CI（默认）

- 运行：`pnpm test`（实现阶段确认包管理器后统一）
- 不需要任何环境变量
- 使用 fake transport（内存 stub）与 fixtures

### 3.2 集成测试（可选，默认跳过）

启用条件：
- 环境变量 `WKTEAM_INTEGRATION=1`
- 必填：`WKTEAM_BASE_URL`、`WKTEAM_AUTHORIZATION`

运行方式建议（实现阶段落地为脚本）：
- `pnpm test:integration`
- 或 `pnpm test -- --runInBand -t integration`

> 集成测试只覆盖“低副作用/只读类”接口的 smoke（例如：查询调用次数、查询流量、获取标签列表等）。
> 任何会产生副作用的接口（发送消息/删除/修改）默认不纳入集成测试，除非使用方显式启用并提供隔离环境。

## 4. 必测清单（离线单元/契约）

### 4.1 配置与初始化

- `baseUrl` 归一化（含尾 `/`、含 path 前缀的处理）
- `authorization` 注入规则（原文注入 + 可选 prefix）
- 必填字段缺失抛 `ValidationError`

### 4.2 请求构造（Contract）

- method/path 必须与 `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json` 一致
- header：`Authorization`、`Content-Type`（按接口需要）
- body：JSON 序列化一致性（字段命名与文档一致）

### 4.3 响应解析与成功判定（ADR-003）

- 默认成功判定：`code == 1000`
- message 字段兼容：`message` vs `msg`
- data 缺失/空值策略（保持原样 vs 标准化）
- 当实际接口差异存在时：通过 endpoint 级覆盖（实现阶段落地）

### 4.4 错误分类与重试（ADR-004）

必须覆盖：
- `NetworkError`（DNS/连接断开模拟）
- `TimeoutError`（Abort 模拟）
- `HttpError`（非 2xx）
- `ApiBusinessError`（HTTP 200 + `code!=1000`）
- `ParseError`（非 JSON/字段缺失）
- retry 判定：哪些错误会触发重试，哪些不会

### 4.5 脱敏与审计事件

- 日志/hook 输出不包含 `Authorization` 原文
- `AUDIT_SPEC.md` 中定义的关键事件至少有 1 个单测覆盖其字段形态（结构化）

### 4.6 回调解析（reference 文档）

针对 `docs/api/.../callback.md` 等 reference 类文档：
- payload 解析 helper 的输入校验
- `dedupKey` 计算稳定（同一消息同一 key）
- 空字段/缺字段的容错与错误类型

## 5. 覆盖性门槛（Coverage Gate）

### 5.1 代码覆盖率（实现阶段启用）

| Area | Target | Gate |
|---|---:|---|
| transport + error mapping | ≥ 95% | CI 阻断 |
| response parsing + success rules | ≥ 95% | CI 阻断 |
| redaction + hooks | ≥ 90% | CI 阻断 |
| endpoint wrappers（自动生成/手写） | ≥ 80% | CI 阻断 |

### 5.2 “不漏接口”门槛（US-008）

必须实现一条离线测试：
- 读取 `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json`
- 读取 SDK 导出的 `operationId` 清单（实现阶段产出一个 `sdk_manifest.json` 或运行时代码导出）
- 断言：catalog 中所有 `kind='endpoint'` 的 `operationId` 都能在 SDK 中找到对应实现

> 若有明确“暂不实现”的 endpoint，必须在 spec 中列出理由与替代方案，并在此测试中允许白名单（默认禁止白名单）。
