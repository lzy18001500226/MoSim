# Business Logic（SDK 行为规则）

> 说明：这里的“业务逻辑”指 SDK 的工程行为规则（而非平台业务）。平台业务语义以离线文档为准。

## Rule: BR-001 成功/失败判定

**Source:** `docs/specs/PRD.md`，离线文档多数接口  
**Priority:** Critical

**Description:** SDK 默认以 `code == 1000` 判定成功，否则视为业务失败并抛 `ApiBusinessError`。

**Algorithm（pseudocode）**

```pseudocode
envelope = parseJson(responseBody)
code = envelope.code
if code == 1000:
  return envelope.data (or envelope)
else:
  throw ApiBusinessError(code, envelope.message/msg, envelope.data)
```

**Edge Cases**

| Case | Input | Expected | Rationale |
|------|-------|----------|-----------|
| `code` 为 number | 1000 | success | 文档示例有 string/number 混用可能 |
| message 字段名差异 | message/msg | 取其一 | 文档存在差异 |

## Rule: BR-002 Authorization 注入与脱敏

**Priority:** Critical

**Description:**

- 当 endpoint 需要鉴权时，SDK 将 `Authorization` header 注入请求
- 默认不对 token 做任何格式化；前缀（如 `Bearer `）由 `authorizationPrefix` 配置控制
- 所有日志输出默认对 token 脱敏（仅保留前后若干字符或输出 `***`）

```pseudocode
if config.authorization is set:
  headers["Authorization"] = config.authorizationPrefix + config.authorization
logHeaders = redactSensitive(headers)
```

## Rule: BR-003 URL 拼装

**Priority:** Critical

**Description:** 以 `baseUrl` + `path` 拼装请求 URL，避免双斜杠与遗漏斜杠。

```pseudocode
url = joinUrl(baseUrl, path)
```

## Rule: BR-004 参数校验（Validation）

**Priority:** High

**Description:** 根据离线文档的参数表进行校验：

- 必填字段缺失：抛 `ValidationError`
- 类型不匹配：抛 `ValidationError`
- 对 `wId/wcId/msgId/newMsgId` 等关键字段做基本校验（非空、类型）

> 注：参数校验的“权威来源”来自 `API_SPEC.md`/`api_catalog.json` 提取结果；若提取不全需手工补齐规则（通过覆盖性报告追踪）。

## Rule: BR-005 重试策略（Retry Policy）

**Priority:** High

**Description:** 默认保守，避免副作用重放：

- 默认仅对“连接失败/超时”做最多 1 次重试（可关闭）
- 对“可能产生副作用”的接口（消息发送、群操作等）默认不自动重试
- 重试使用指数退避（可配置），并在日志中记录 retry 次数与原因

**Decision Table**

| Error Type | Endpoint Class | Retry? | Notes |
|------------|----------------|--------|------|
| NetworkError(timeout) | idempotent | Yes (<=1) | 可配置 |
| NetworkError(timeout) | side-effect | No | 需显式启用 |
| HttpError(5xx) | idempotent | Optional | 需谨慎，默认关闭 |
| ApiBusinessError | any | No | 业务失败不重试 |

## Rule: BR-006 异步结果轮询（Polling Helpers）

**Priority:** Medium

**Description:** 文档中存在“发起异步任务 → 查询结果”的接口对（例如下载视频、朋友圈视频发送结果等）。SDK 需要提供可选 helper：

- `pollUntil(...)`：按固定间隔/退避策略轮询结果接口
- 超时/最大次数后失败，返回结构化错误

**Example Contract**

```pseudocode
pollUntil(
  startOperation,
  queryOperation,
  isDone,
  { intervalMs, timeoutMs, maxAttempts }
)
```

## Rule: BR-007 Webhook 回调去重建议

**Priority:** High

**Description:** 回调文档提示“可能重复推送历史消息”，SDK 必须：

- 明确建议使用 `data.newMsgId`（或 `timestamp`）作为去重 key
- 提供 helper：`getCallbackDedupKey(payload)`（纯函数，不做存储）

```pseudocode
key = payload.data.newMsgId ?? payload.data.timestamp ?? hash(payload)
```

