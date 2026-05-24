# Acceptance Tests（验收用例：面向“API 可用”目标）

> 说明：本文件定义“可执行的验收场景”，实现阶段需要把这些场景落到测试代码中（Vitest）。
> 默认使用 **fake transport** 进行离线回归；集成场景以 `WKTEAM_INTEGRATION=1` 为开关。

## AT-001：初始化客户端与配置校验（US-001）

```gherkin
Scenario: create client with minimal config
  Given baseUrl and authorization are provided
  When I create a WkteamClient
  Then the client is created successfully
  And the default headers contain Authorization (redacted in logs)
```

```gherkin
Scenario: missing baseUrl should fail fast
  Given baseUrl is empty
  When I create a WkteamClient
  Then it throws ValidationError
```

## AT-002：Authorization 注入规则（US-001/US-002）

```gherkin
Scenario: authorization prefix disabled by default
  Given authorization = "token_raw" and authorizationPrefix = null
  When calling any endpoint
  Then request header Authorization equals "token_raw"
```

```gherkin
Scenario: authorization prefix enabled
  Given authorization = "token_raw" and authorizationPrefix = "Bearer "
  When calling any endpoint
  Then request header Authorization equals "Bearer token_raw"
```

## AT-003：登录流程封装可用（US-002）

> 说明：登录在离线文档中表现为多步骤接口（第一步/获取二维码/执行登录等）。SDK 需要：
> - 对每个登录 endpoint 提供 wrapper
> - 提供可选的“流程编排 helper”（实现阶段）

```gherkin
Scenario: login endpoints wrappers exist and produce correct requests
  Given I load api_catalog.json
  When I look up operationIds under module "deng-lu"
  Then each operationId can be called via SDK
  And method/path match catalog
```

## AT-004：消息发送接口全覆盖（US-003）

```gherkin
Scenario: send text message wrapper builds request per doc
  Given a fake transport that returns code=1000
  When I call messages.sendText with required parameters
  Then the transport receives POST /sendText with JSON body
  And the SDK returns ok result with parsed data
```

```gherkin
Scenario: send file wrapper rejects invalid inputs
  Given missing fileUrl or invalid file type
  When I call messages.sendFile
  Then it throws ValidationError before sending network request
```

## AT-005：消息接收 callback 解析与去重 key（US-004）

```gherkin
Scenario: callback payload parse success
  Given a callback payload example from docs/api/.../callback.md
  When I call callbacks.parse(payload)
  Then it returns a normalized object with stable fields
```

```gherkin
Scenario: dedupKey is stable for same message
  Given two callback payloads that refer to the same message
  When I call callbacks.dedupKey(payload)
  Then the returned keys are equal
```

## AT-006：统一错误模型与重试策略（US-007）

```gherkin
Scenario: business error maps to ApiBusinessError
  Given fake transport returns HTTP 200 with code=1001 and message
  When I call any endpoint
  Then SDK throws ApiBusinessError
  And error includes operationId, requestId, apiCode
```

```gherkin
Scenario: network error retries only for safe categories
  Given retry.enabled=true and endpoint category is "safe"
  And fake transport fails with network error on attempt 1 and succeeds on attempt 2
  When I call the endpoint
  Then SDK retries once and returns success
```

```gherkin
Scenario: side-effect endpoint does not retry by default
  Given retry.enabled=true and endpoint category is "side_effect"
  And fake transport fails with network error
  When I call the endpoint
  Then SDK does not retry and throws NetworkError
```

## AT-007：日志/Hook 不泄露敏感信息（US-007）

```gherkin
Scenario: Authorization never appears in logs
  Given logLevel=debug and authorization="token_raw"
  When I call any endpoint and it fails
  Then captured logs do not contain "token_raw"
  And hooks receive redacted headers
```

## AT-008：不漏接口（覆盖性核验）（US-008）

```gherkin
Scenario: every endpoint in catalog has an SDK wrapper
  Given api_catalog.json contains N endpoint entries
  When I load SDK manifest of implemented operationIds
  Then the set difference is empty
```

## AT-009：可选集成 Smoke（需要真实环境）（US-002/US-005/US-006）

> 仅当 `WKTEAM_INTEGRATION=1` 时运行。

```gherkin
Scenario: integration smoke calls read-only endpoints successfully
  Given WKTEAM_BASE_URL and WKTEAM_AUTHORIZATION are configured
  When I call a configured list of smoke endpoints
  Then each response can be parsed
  And each response either returns code=1000 or a documented business error
```
