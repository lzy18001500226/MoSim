# Data Security Specification（SDK）

## Data Classification（SDK 处理的数据）

| Level | Examples | Encryption | Access | Retention |
|-------|----------|-----------|--------|-----------|
| Public | API 文档、接口路径 | N/A | Anyone | repo 内长期 |
| Confidential | `wId`、`wcId`、msgId/newMsgId、回调 payload（含业务内容） | in-transit | app 内部 | 由使用方控制 |
| Restricted | `Authorization` token、账号密码（登录参数） | in-transit | need-to-know | 不落盘；仅内存 |

## Encryption

| Context | Method | Algorithm | Key Management |
|---------|--------|-----------|---------------|
| In transit | HTTPS | TLS 1.2+（建议 1.3） | 由平台与使用方 baseUrl 决定 |
| At rest | SDK 默认不落盘 | - | - |

> 备注：如使用方需要落盘（缓存 token/消息内容），属于使用方系统安全设计范畴，不在 SDK 默认行为内；但 SDK 文档应提示风险与建议。

## Logging & Redaction（日志与脱敏）

### 禁止输出（默认）

- `Authorization` 明文
- 账号密码明文
- 回调 payload 中可能包含的敏感业务内容（可配置允许 debug，但必须显式开启）

### 允许输出（默认）

- operationId、method、path
- HTTP status（不含 body 全量）
- 业务 `code` 与 message（可截断）

### 脱敏策略（建议）

| Field | Strategy |
|------|----------|
| token | 仅保留前 6 + 后 4，其余 `*` |
| URL | 保留 path，query 做白名单或全隐藏 |
| response body | 截断（例如最多 2KB） |

## Input Security（输入安全）

SDK 的“输入”来自调用方传参与平台回调 payload：

- 运行时校验必填字段，拒绝无意义空值（减少误调用）
- 对 URL/路径类参数（文件 URL、回调 URL）做基本格式校验（防止错误配置造成 SSRF/出网风险）
- 不对 XML/富文本做任何执行，仅作为字符串透传

## Secrets Management（配置与密钥）

| Secret Type | Storage | Rotation | Access |
|-------------|---------|----------|--------|
| `Authorization` | 环境变量 / 密钥管理系统（建议） | 平台侧决定 | 最小权限 |
| 登录账号密码 | 环境变量/CI Secret（集成测试） | 建议定期 | 最小权限 |

仓库要求：

- 必须提供 `.env.example`（实现阶段）列出所有配置项
- 禁止提交 `.env`、token、账号密码到 git

