# Monitoring Specification（SDK 可观测性）

> 说明：SDK 自身不“运营服务”，因此本章节关注：
> 1) SDK 对外提供的 **日志/事件 hook** 能力（便于接入上层监控）  
> 2) SDK 内部必须输出的 **结构化诊断信息**（默认可关闭/降级）  
> 3) 敏感信息 **脱敏规则** 与可审计事件规范（与 `03_Security/AUDIT_SPEC.md` 一致）

## 1. 事件与 Hook（面向使用方）

SDK 必须提供一组可选 hook，用于将请求生命周期信息上报到使用方监控系统（Prometheus/OpenTelemetry/自建埋点均可）。

| Hook | 触发时机 | 输入（最小字段） | 说明 |
|---|---|---|---|
| `onRequest` | 发起请求前 | `requestId, operationId, method, path, attempt, headers(redacted)` | 可用于打点与调试 |
| `onResponse` | 收到响应后 | `requestId, operationId, httpStatus, durationMs, apiCode?, attempt` | `apiCode` 来自业务响应解析 |
| `onRetry` | 每次重试前 | `requestId, operationId, attempt, reason, backoffMs` | reason: network/timeout/http5xx/http429 |
| `onError` | 失败返回前 | `requestId, operationId, errorName, errorKind, httpStatus?, apiCode?` | errorKind 见 ADR-003 |

> 约束：hook 不得泄露敏感信息（Authorization、Cookie、手机号等），必须先经脱敏。

## 2. 结构化日志（面向调试与事故定位）

SDK 内部日志建议采用单行 JSON（便于被使用方收集），字段规范如下（实现阶段可根据实际扩展，但不得减少关键字段）：

```json
{
  "ts": "2026-02-10T00:00:00.000Z",
  "level": "info",
  "event": "wkteam.http.response",
  "requestId": "req_01H...",
  "operationId": "messages_send_text",
  "method": "POST",
  "path": "/sendText",
  "httpStatus": 200,
  "apiCode": 1000,
  "durationMs": 123,
  "attempt": 1
}
```

建议的 `event` 枚举（实现阶段形成常量并写单测）：
- `wkteam.http.request`
- `wkteam.http.response`
- `wkteam.http.retry`
- `wkteam.http.error`
- `wkteam.parse.error`
- `wkteam.validation.error`

## 3. 指标建议（Metrics Suggestions）

SDK 不直接暴露 Prometheus endpoint，但应当通过 hook 让使用方采集以下指标：

| Metric | Type | Tags（建议） | 说明 |
|---|---|---|---|
| `wkteam_sdk_request_total` | counter | `operationId, httpStatus, apiCode, errorKind` | 请求总量 |
| `wkteam_sdk_request_duration_ms` | histogram | `operationId, httpStatus` | 延迟分布 |
| `wkteam_sdk_retry_total` | counter | `operationId, reason` | 重试次数 |
| `wkteam_sdk_business_error_total` | counter | `operationId, apiCode` | `code!=1000` 的业务错误计数 |

## 3.1 建议告警阈值（Alert Thresholds Suggestions）

> SDK 不负责“报警”，但为了可运营性，建议使用方基于上述 metrics 设置阈值（按业务容忍度调整）。

| Alert | Condition（示例） | Severity | 说明 |
|---|---|---|---|
| 业务错误激增 | `wkteam_sdk_business_error_total` 5min 增量异常（相对基线 +3σ） | P2 | 可能是上游策略/参数变化/账号异常 |
| 网络失败率升高 | `errorKind in (NetworkError, TimeoutError)` 占比 > 2%（5min） | P1/P2 | 可能是网络、DNS、代理或上游故障 |
| 重试异常 | `wkteam_sdk_retry_total` 占比 > 10%（5min） | P2 | 可能触发限流/不稳定；需检查 retryOn/并发 |
| 延迟劣化 | P95 `wkteam_sdk_request_duration_ms` > 3s（10min） | P2 | 可能是上游慢或本地网络问题 |

## 4. 链路追踪建议（Tracing / OTel）

若使用方已接入 OpenTelemetry，SDK 推荐支持以下两种方式：
1) **由使用方在 transport 层做 tracing**（最通用）
2) SDK 提供可选的 `trace` hook（不强依赖 OTel 包），由使用方适配

最小追踪字段（span attributes）：
- `http.method`, `http.route`（或 path）
- `wkteam.operation_id`
- `wkteam.api_code`（若可解析）
- `wkteam.request_id`（SDK 内部 requestId）

## 5. 脱敏与 PII 规则（强制）

### 5.1 永不记录（NEVER LOG）
- `Authorization`（完整值）
- `Cookie` / `Set-Cookie`
- 账号密码、验证码、二维码 token、任何会话密钥

### 5.2 必须脱敏（MASK）
- 手机号、邮箱、微信号等个人标识（若文档字段中出现）
- 文件下载链接中的签名/临时 token（若出现）

### 5.3 可记录（OK）
- `requestId`（SDK 生成）
- 上游业务 `code`（如 1000/1001）
- HTTP 状态码与耗时
- operationId（SDK 内部稳定标识）

> 验证要求：必须有单元测试覆盖“脱敏输出不包含 Authorization 原文”。

## 6. 诊断开关（Debug Mode）

SDK 必须支持 `logLevel: 'debug'` 输出更丰富的信息，但仍要遵守脱敏规则。建议 debug 模式额外包含：
- 归一化后的 URL（不含 query 的敏感值）
- 解析响应 envelope 的关键字段（`code/message`）
- retry 判定路径（为什么重试/为什么不重试）
