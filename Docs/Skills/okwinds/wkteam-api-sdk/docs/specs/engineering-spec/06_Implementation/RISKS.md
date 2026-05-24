# Risk Register（风险清单）

> 说明：本项目风险主要来自“上游文档的不确定性 + 接口副作用 + 大接口面维护成本”。
> 风险条目必须可操作：包含预防措施与触发后的应对方案。

| ID | Risk | Probability | Impact | Mitigation（预防） | Contingency（发生后） |
|---|---|---|---|---|---|
| R-001 | `baseUrl`/网关路径规则不明确（是否需要前缀 path） | M | H | 配置支持 baseUrl 含 path；URL 归一化单测；README 写清 | 集成 smoke 验证；必要时增加 `basePath` 配置并做 minor 发布 |
| R-002 | `Authorization` 前缀/格式不确定（Bearer? 原文?） | H | H | 默认原文注入 + 可配置 prefix；脱敏测试 | 通过集成验证确认；在文档与示例中给出明确推荐 |
| R-003 | token 生命周期/刷新流程不明确 | H | H | `authorization` 支持函数（sync/async）；不在 SDK 内强行做刷新 | 使用方实现刷新；SDK 提供 hook/错误码帮助判断“需要刷新” |
| R-004 | 文档与真实返回结构存在差异（`message` vs `msg`、data 结构变化） | M | H | envelope 解析兼容；错误对象保留 raw（脱敏）片段；catalog 允许 endpoint 覆盖 | 将差异记录到 worklog；更新解析规则与 fixtures；发布 patch |
| R-005 | 副作用接口重试导致重复发送/重复操作 | M | H | ADR-004 分类重试；默认保守；提供开关与告警日志 | 指导使用方做业务幂等；若上游支持幂等 key，SDK 增加支持 |
| R-006 | 限流/风控策略不明确，容易触发封禁 | M | H | 提供并发限制 `concurrency`；可配置 retryOn 429；文档提示 | 允许使用方实现速率限制器；增加示例与最佳实践 |
| R-007 | 127 endpoints 手写封装易遗漏/漂移 | H | H | 以 catalog 驱动生成/校验；AT-008 覆盖性门槛 | 若发现遗漏：先补齐 wrapper 与测试，再发布 patch |
| R-008 | callback 重复/乱序造成上层业务误处理 | M | M | 提供 dedupKey helper；文档强调“去重需持久化” | 给出参考实现（in-memory + 注释局限）并建议上层落库 |
| R-009 | 日志泄露敏感信息（token/手机号） | M | H | 默认脱敏；单测强制；禁止 raw dump | 紧急 deprecate 版本并 patch 修复；审计发布包 |
| R-010 | 法务/合规风险（使用第三方平台接口的条款与授权） | L/M | H | README 提醒：仅在获得授权的环境使用；不提供绕过/破解 | 若收到投诉：下架示例中敏感内容，保留纯 SDK 形态并澄清用途 |
