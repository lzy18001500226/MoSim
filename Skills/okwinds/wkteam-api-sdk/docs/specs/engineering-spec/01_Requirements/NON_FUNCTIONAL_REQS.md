# Non-Functional Requirements（SDK）

> 说明：SDK 项目与服务端系统不同，Availability/DR 等指标主要约束“SDK 工程质量与发布稳定性”，不直接约束平台 API 本身的 SLA。

## Compatibility

| ID | Requirement | Target | Verification |
|----|-------------|--------|--------------|
| NFR-COMPAT-001 | Node 版本支持 | Node >= 18.18（建议 20 LTS） | CI matrix（实现阶段） |
| NFR-COMPAT-002 | 模块格式 | 同时提供 ESM/CJS + types | 构建产物检查 |
| NFR-COMPAT-003 | 配置方式 | 支持显式配置对象 + 环境变量（集成测试） | 单测 + 文档 |

## Reliability

| ID | Requirement | Target | Verification |
|----|-------------|--------|--------------|
| NFR-REL-001 | 超时可控 | 每个请求可配置 timeout | 单测 |
| NFR-REL-002 | 重试可控 | 重试策略可配置，默认保守 | 单测 + 文档 |
| NFR-REL-003 | 失败可诊断 | 错误携带 operationId/status/code 等上下文 | 单测 |

## Security

| ID | Requirement | Standard | Verification |
|----|-------------|----------|--------------|
| NFR-SEC-001 | 敏感信息保护 | token 脱敏 + 最小日志 | 单测（脱敏）+ 代码审查 |
| NFR-SEC-002 | 传输安全 | 使用 HTTPS（由 baseUrl 决定） | 文档约束 + 集成测试 |

## Observability

| ID | Requirement | Target | Verification |
|----|-------------|--------|--------------|
| NFR-OBS-001 | 可插拔 logger | 支持注入 logger 接口 | 单测 |
| NFR-OBS-002 | 请求关联 | requestId/operationId 可记录 | 单测 |

## Performance（SDK 内部）

| ID | Requirement | Metric | Target | Verification |
|----|-------------|--------|--------|--------------|
| NFR-PERF-001 | 解析与序列化开销 | CPU/alloc | 不引入明显 O(n^2) | 基准测试（可选） |

