# Webhook Service 测试缺口记录

本文档记录在 PR/MR 状态感知机制开发过程中发现的测试缺口，需要后续补充。

## 已补充的测试

### 1. WebhookConfig GORM Scanner/Valuer (已完成 ✅)
- **文件**: `backend/internal/domain/gitprovider/webhook_config_gorm_test.go`
- **问题**: GORM 无法将 PostgreSQL JSONB 列扫描到 `*WebhookConfig` 结构体
- **测试内容**:
  - `TestWebhookConfig_Value` - 序列化测试
  - `TestWebhookConfig_Scan` - 反序列化测试（含 nil、空字节、无效 JSON 等边界情况）
  - `TestWebhookConfig_ValueScanRoundTrip` - 完整往返测试

### 2. GitLab Webhook Pipeline 事件 (已完成 ✅)
- **文件**: `backend/internal/infra/git/gitlab_webhook_test.go`
- **问题**: `RegisterWebhook` 未正确设置 `pipeline_events`
- **测试内容**:
  - `register webhook with pipeline events` - 验证 pipeline 事件启用
  - `register webhook with all events` - 验证所有事件启用
  - `register webhook with no events` - 验证所有事件禁用

### 3. WebhookService 初始化和依赖注入 (已完成 ✅)
- **文件**: `backend/internal/service/repository/service_webhook_injection_test.go`
- **问题**: `RepositoryService.GetWebhookService()` 返回 nil，导致 HTTP 503
- **测试内容**:
  - `TestNewService_WebhookServiceNil` - 初始状态 nil
  - `TestSetWebhookService` - 正确设置依赖
  - `TestSetWebhookService_CanBeCalledMultipleTimes` - 可多次设置
  - `TestSetWebhookService_NilValue` - 可设置为 nil
  - `TestGetWebhookService_ReturnsInterface` - 返回接口类型
  - `TestCreateWithWebhook_NoWebhookService` - 无 WebhookService 时正常创建仓库
  - `TestCreateWithWebhook_NoUserID` - 无 UserID 时正常创建仓库
  - `TestCreateWithWebhook_WithWebhookService` - 有 WebhookService 时触发 webhook 注册

**代码修复**:
- 在 `webhook_registration.go:getGitProviderForUser` 添加 userService nil 检查
- 在 `webhook_registration.go` 多处添加 logger nil 检查
- 在 `service.go:CreateWithWebhook` 添加 logger nil 检查

### 4. getGitProviderForUser Token 查找优先级 (已完成 ✅)
- **文件**: `backend/internal/service/repository/webhook_token_test.go`
- **问题**: 代码只检查 OAuth tokens，未检查 bot tokens
- **测试内容**:
  - `TestGetGitProviderForUser_PrefersBotToken` - 优先使用 bot token
  - `TestGetGitProviderForUser_FallsBackToOAuthToken` - 回退到 OAuth token
  - `TestGetGitProviderForUser_NoTokensAvailable` - 两种 token 都不存在
  - `TestGetGitProviderForUser_EmptyOAuthToken` - OAuth token 为空
  - `TestGetGitProviderForUser_BotTokenEmptyString` - Bot token 为空字符串
  - `TestProviderTypeToOAuthMapping` - Provider 类型映射

## 待补充的测试

### 5. Webhook 注册集成测试
- **文件**: `backend/internal/service/repository/webhook_registration.go`
- **需要测试**:
  - [ ] 自动注册成功场景（mock git provider）
  - [ ] 自动注册失败时正确设置 `NeedsManualSetup`
  - [ ] `WebhookConfig` 正确保存到数据库
  - [ ] 删除 webhook 时正确清理配置

### 6. PostgreSQL Schema 变更后的连接池处理
- **问题**: Schema 变更后 PostgreSQL prepared statement cache 失效
- **原因**: 这是运维问题，不是代码问题
- **建议**: 在迁移文档中添加说明，提醒需要重启应用或重置连接池

## 相关文件清单

| 文件 | 职责 |
|------|------|
| `backend/internal/domain/gitprovider/gitprovider.go` | WebhookConfig 结构体定义 |
| `backend/internal/domain/gitprovider/webhook_config_gorm_test.go` | Scanner/Valuer 测试 |
| `backend/internal/service/repository/webhook_service.go` | WebhookService 基础定义 |
| `backend/internal/service/repository/webhook_registration.go` | Webhook 注册逻辑 |
| `backend/internal/service/repository/webhook_token_test.go` | Token 优先级测试 |
| `backend/internal/service/repository/service_webhook_injection_test.go` | 依赖注入测试 |
| `backend/internal/infra/git/gitlab_webhook.go` | GitLab Webhook API |
| `backend/internal/infra/git/gitlab_webhook_test.go` | GitLab Webhook 测试 |
| `backend/cmd/server/services_init.go` | 服务初始化 |

## 发现的问题时间线

1. **WebhookService 未注入** (HTTP 503) - `services_init.go` 缺少 `SetWebhookService` 调用
2. **缺少数据库列** (SQL Error) - 需要创建 migration 000044
3. **Prepared Statement Cache** (SQL Error) - Schema 变更后需要重启
4. **Bot Token 未检查** (ErrNoAccessToken) - `getGitProviderForUser` 逻辑不完整
5. **JSONB Scan 失败** (Type Error) - 缺少 Scanner/Valuer 接口
6. **Pipeline 事件未启用** (Webhook Config) - `RegisterWebhook` 缺少 pipeline 事件处理
