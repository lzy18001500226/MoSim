# Audit & Compliance Specification（SDK 日志与审计）

> 说明：SDK 本身不是合规系统，但应当提供“审计友好”的日志事件结构，帮助使用方在生产环境排障与追踪调用链路。

## Events to Log（建议事件）

| Category | Events | Data Captured（默认） |
|----------|--------|------------------------|
| Authentication | `auth.login.start/success/fail` | operationId、status、code、elapsedMs（不含密码/token 明文） |
| Requests | `api.request` / `api.response` | operationId、method、path、status、elapsedMs、businessCode |
| Errors | `api.error` | errorType、operationId、status/code、message（截断） |
| Webhook | `webhook.received` | messageType、dedupKey（不含 payload 全量，除非 debug 开启） |

## Log Format（结构化日志）

建议 SDK 的 logger 支持结构化对象输入（或能被适配到 JSON logger）。

```json
{
  "ts": "ISO-8601",
  "level": "info",
  "event": "api.response",
  "operationId": "xiao_xi_fa_song_sendFile",
  "http": { "method": "POST", "path": "/sendFile", "status": 200, "elapsedMs": 1234 },
  "api": { "code": "1000" }
}
```

## PII / Secrets in Logs（强约束）

- NEVER log: `Authorization` 明文、账号密码明文、回调 payload 全量（默认）
- OK (default): operationId、method、path、status、业务 code、简短 message

## Retention（SDK 建议）

| Log Type | Retention | Access |
|----------|-----------|--------|
| SDK logs（应用日志的一部分） | 跟随使用方策略 | engineering |

