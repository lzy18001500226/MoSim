# Phase 4 — 概念建模与不变量加固

**日期**: 2026-05-24
**状态**: documented

## 4.1 — `current_org_slug` single-writer invariant

`PersistedSession.current_org_slug`（Rust SSOT）只有**一个** writer：`AuthManager::set_current_org()` (`clients/core/crates/auth/src/manager.rs:73`)。

### 写入路径

```
Zustand setCurrentOrg (web/src/stores/auth.ts)
    ↓
wasm.set_current_org (wasm/src/auth.rs:144) | switch_org (auth.rs:106)
    ↓
AuthManager.set_current_org (manager.rs:73) ← single writer
    ↓
sess.current_org_slug = org.slug
self.persist()
```

调用 `set_current_org` 的内部位置：
- `bootstrap.rs:111` (hydrate)
- `manager.rs:69` (promote first org)
- `org.rs:60` (switch_org)

### 不变量

- `current_org_slug` 改变时**必然**通过 `set_current_org`
- `set_current_org` **总是** 持有 `write_state()` 锁，串行化 mutation
- `persist()` 写入 localStorage / Keychain，绑定到状态变更
- React side guard: `setCurrentOrg` 检查 `previousSlug !== org.slug` 避免相同值重写触发 panel wipe

### 未来约束

- 加新 `current_org_slug` 写入路径必须经过 `manager.set_current_org`
- 不要在 Zustand store 直接 mutate session blob
- 不要在 wasm bridge 之外的地方持有 `current_org_slug`

## 4.2 — proto3 `optional` keyword 规范

### 决策

所有「业务可选」（absent ≠ default value）的字段**必须**用 `optional` keyword。

### 现状

| 用 optional ✓ | 没用 ✗（值/缺失歧义） |
|---|---|
| env_bundle.proto (新写) | 老 proto（pod, channel...） |
| support_ticket.proto (PresignAttachmentUpload) | runner, ticket |
| repo_skill.proto (新增 Presign 字段) | apikey, billing |

### 规则

1. **新字段** 如果有「业务上 absent」语义（如 `optional int64 market_item_id = 4` 表示「非 market 安装」），用 `optional`
2. **三态 update RPC** 用 `has_xxx: bool + xxx: T` 模式（参考 `env_bundle.UpdateEnvBundleRequest.has_data`）：absent / clear / replace 三状态
3. **不要** 用 sentinel 值（`-1`, `0`, `""`）表达 absent — 用 `optional` 或 wrapper message

### 何时 OK 不用 optional

- 字段语义上 default == absent（如 `string email = 1` 空字符串自然表示无 email）
- list 字段（`repeated`）默认空 list 就是「没有」
- map 字段同上

### 历史字段不强制改

存量 proto 字段保持现状（避免 wire format break）。新增字段按规则严格执行。

## 4.3 — Backend domain (GORM) vs proto Go 类型 — 不合并（设计原则）

### 原则

GORM domain 类型和 proto 类型**不是 dual-track，是两个不同的 concern**：

| 维度 | Backend domain (`internal/domain/<x>/`) | proto (`proto/<x>/v1/<x>.proto`) |
|---|---|---|
| **管什么** | 数据库 schema + 业务规则 | 网络传输 payload 形态 |
| **演进周期** | 跟数据库迁移绑定（migration 文件） | 跟 wire-compat 规则绑定（proto v1/v2） |
| **关键 tag** | `gorm:"primaryKey"` / `gorm:"index"` | `[json_name=...]` / `optional` |
| **谁需要重启** | DB migration | 客户端重新拉 proto + 编译 |
| **变更扇出** | repo / service / handler | 所有平台（Web/Desktop/iOS）+ backend |

合并会**把两个独立 concern 强行耦合**：
- DB schema 一变，wire 变（破坏老客户端）
- wire 字段加一个，DB 必须有列（不可能：客户端临时字段 / derived 字段）
- ORM tag 注入到 proto-gen 类型在工具链上不支持，做不到

### 设计

两层独立，用 `convert.go` 显式桥接：

```
Domain (GORM struct) ←→ convert.go ←→ Proto (prost/protoc-gen-go)
   ↑                                       ↑
   repo / service 用                        Connect handler / client 用
```

### 约束

- `convert.go` 文件**必须**跟 Connect handler 同目录（不要散落到 service 层）
- 命名一致：`toProtoX(d *domain.X) *protoX.X` + `fromProtoX(p *protoX.X) *domain.X`
- 关键字段加 round-trip test (`TestConvertX_RoundTrip` 验证 domain → proto → domain 不丢字段)
- 新加字段时**两边都加**：domain struct + GORM tag + proto field + convert.go mapping

## 4.4 — ffi `proto_convert` 层评估 — 保留

### 现状

`clients/core/crates/ffi/src/services/{automation_proto_convert.rs, channel_proto_convert.rs}` — 2 个独立 proto → UniFFI DTO 转换文件。

### 决策

**保留** — 这两个 service 的 DTO 在 Swift 端有特殊 ergonomic 需求：
- `automation_proto_convert`: Autopilot Controller 的 nested timeline / iteration 结构需要在 Swift 端展开成易于 SwiftUI 渲染的形态
- `channel_proto_convert`: ChannelMessage 的 `content_json` 字段需要在 Swift 端解析为 typed enum

其他 14 个 service 没有这类需求，直接走 typed UniFFI 暴露即可（无 proto_convert 文件）。

### 边界规则

新增 ffi service 默认**不**写 proto_convert 文件。只有遇到 Swift 端 strong ergonomic 需求（typed enum 替代 JSON string、nested 展开等）才允许加 proto_convert。

## 验证

- ADR 完成，不需要代码改动（4.1 已是现状，4.4 保留）
- 4.2 规范用于将来 proto 修改的 review 准则
- 4.3 不合并 — domain/proto/convert 三层架构保持
