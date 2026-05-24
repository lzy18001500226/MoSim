# Operations Runbook（SDK 故障排查手册）

> 说明：本手册服务于两类人：
> - **SDK 使用方**：遇到请求失败、鉴权失败、回调重复等问题时，能快速定位原因并给出可复现信息。
> - **SDK 维护者**：能按统一流程收集证据、复现、修复与发布补丁。

## 1. 统一信息收集（必填）

出现问题时，请先收集以下信息（不包含任何密钥原文）：

| 字段 | 示例 | 说明 |
|---|---|---|
| `sdkVersion` | `0.1.0` | npm 包版本 |
| `nodeVersion` | `v20.11.1` | Node 版本 |
| `baseUrl`（脱敏） | `https://api.example.com` | 不要包含 query token |
| `operationId` | `deng_lu_member_login` | 对应 `API_SPEC.md` 的 operationId |
| `requestId` | `req_...` | SDK 每次请求生成 |
| `httpStatus` | `200/401/500` | HTTP 状态码 |
| `apiCode` | `1000/1001/...` | 业务 code（若能解析） |
| `errorKind/errorName` | `ApiBusinessError` | 错误分类（ADR-003） |
| `logLevel` | `debug` | 是否开启调试 |

## 2. 常见问题与处理流程

### 2.1 鉴权失败（HTTP 401/403 或 `code != 1000` 且提示未登录）

**现象**
- HTTP 401/403
- 或 HTTP 200，但响应体 `code=1001`，message 表示鉴权失败/登录失效

**排查**
1) 确认初始化配置：
   - `authorization` 是否为空
   - `authorizationPrefix` 是否与上游期望一致（默认不加前缀）
2) 用同一 `baseUrl` + 同一 Authorization 用 curl/POSTMAN 复现（不要把 token 写入 issue）
3) 若接口属于登录流程：
   - 按离线文档流程核对“第一步/第二步/第三步”是否完整

**解决**
- 纠正 prefix/头名配置
- 若 token 过期：使用方实现刷新逻辑（建议传入 `authorization: async () => refreshIfNeeded()`）

### 2.2 业务失败（HTTP 200 但 `code != 1000`）

**现象**
- SDK 抛出 `ApiBusinessError`（或返回 `ok=false` 的结果，视最终实现而定）

**排查**
1) 记录 `apiCode` 与 message（脱敏）
2) 对照对应 `docs/api/.../*.md` 的“返回示例/说明”，确认是否属于合法失败分支
3) 检查请求体字段是否缺失/类型错误（SDK 应在本地先做校验并抛 `ValidationError`）

**解决**
- 补齐必填字段
- 若文档与实际返回结构不一致：记录原始响应（脱敏）并更新 catalog/解析规则

### 2.3 网络错误/超时（`NetworkError` / `TimeoutError`）

**排查**
1) 确认 `baseUrl` 是否可达（DNS/网络/代理）
2) 调整 `timeoutMs`
3) 检查是否开启重试：`retry.enabled` 与 endpoint 是否属于“安全类别”

**解决**
- 对 idempotent/安全接口开启重试与指数退避
- 对可能有副作用的接口（消息发送/群操作等）保持默认不重试，改为上层做“业务幂等”

### 2.4 解析错误（`ParseError`）

**现象**
- HTTP 成功返回，但 JSON 解析失败或字段缺失

**排查**
1) 在 debug 模式下记录响应的 `Content-Type` 与前 200 字节（脱敏）
2) 确认是否被网关/反向代理返回了 HTML 错误页

**解决**
- 改善 transport：确保 `response.text()` 与 `response.json()` 处理正确
- 增强错误报告：将 `httpStatus`、`contentType`、`requestId` 写入错误对象

### 2.5 回调重复/乱序（消息接收类 callback）

离线文档中存在 callback 说明文档（属于 reference 类文档），SDK 将提供 helper：
- 解析 payload
- 计算 `dedupKey`（用于去重）
- 可选的 in-memory 去重器（实现阶段）

**排查**
1) 使用方必须自行持久化去重（SDK 仅提供 key 与参考实现）
2) 若回调乱序：按 message id / timestamp 进行排序处理

## 3. 维护者发布处置（紧急修复）

### 3.1 发现严重问题（已发布版本）
1) 在 npm 上执行 deprecate：
   - `npm deprecate <pkg>@<badVersion> "<原因 + 建议升级版本>"`
2) 发布修复补丁：
   - `PATCH` 版本（优先）或 `MINOR`（新增能力）
3) 在 `docs/worklog.md` 记录：
   - 触发条件、影响面、修复摘要、验证命令与结果

### 3.2 破坏性变更误发
1) 立即发布更正版本并显式升 `MAJOR`
2) 在 README 顶部添加迁移段落（并在 `docs/specs/engineering-spec/06_Implementation/MIGRATION.md` 补齐迁移路径）

## 4. 反馈模板（用于 issue/工单）

```text
SDK 版本：
Node 版本：
baseUrl（脱敏）：
operationId：
requestId：
httpStatus / apiCode：
错误类型（errorKind/errorName）：
复现步骤：
期望结果：
实际结果：
附：脱敏日志片段（debug 模式）
```
