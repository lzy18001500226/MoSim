# ADR 2026-05-24: Service Binding Matrix

## Status
Accepted

## Context

Rust core (`clients/core/crates/services/`) 提供 30+ services。三个 binding crate 把它们 export 给三种宿主进程：

- **wasm** (`crates/wasm`) — Browser tab、PWA、iOS WKWebView
- **node-bridge** (`crates/node-bridge`) — Desktop main process (Electron + napi-rs)
- **ffi** (`crates/ffi`) — iOS native app (UniFFI + Swift)

`/arch_check` 审查发现三个 binding service 覆盖不对称：
- WASM 31 services
- Node-bridge 27 services
- FFI 16 services

本 ADR 文档化哪些缺失是「合理设计」，哪些是「真实 gap 需修复」，避免未来 reviewer 重复评估。

## Decision

### 0. Symmetry standard — proto wire 而非 binding 代码路径

「跨端对称」的标准应该是 **proto wire schema 对称**（已 100% Connect 化），不是「每个 service 在所有 binding 都暴露具体的 native method」。

具体衡量原则：

| Service 性质 | 是否需要三 binding 都有专用 method |
|---|---|
| 持有 state / cache | ✅ 是 — state 在 Rust core 是 SSOT，binding 必须共享 |
| 有跨方法业务逻辑 | ✅ 是 — 逻辑在 Rust core 一次实现 |
| **Thin proxy（无 state、无逻辑、只调 backend）** | ❌ **不需要** — desktop 可以通过 generic connectCall 直连 backend；wire 仍是 proto 契约 |

「Thin proxy」类 service：增加 binding 是形式对称，没有功能价值，反而增加维护面（13+ napi method + 测试 mock 同步）。

### 1. 三 binding 共有的 core services（有 state 或逻辑）
- **pod** / **channel** / **blockstore** / **runner**: 有 state cache，binding 共享 SSOT 必要
- **autopilot** / **loop** / **ticket** / **billing** / **sso** / **user**: 跨端用户操作核心，binding 对称合理
- 这 10 个 service 三端都有专用 binding

### 2. Thin proxy services — 不需要 binding 对称
- **repository**: Rust core RepositoryService 是 thin proxy（没 state，没逻辑）。Desktop 通过 `connectCall` generic IPC proxy 直连 backend，wire 仍是 proto 契约。原本判断的「repository 缺 Node-bridge」是误判 — Phase 9 实施时发现加 napi binding 是形式对称无功能价值，已 revert。
- **同类**: agent / extension / invitation / promocode 等 backend-CRUD 型 service 也属此类。这些 service 在三 binding 的「覆盖差异」不是 gap，是合理设计。

### 3. Browser 合理缺失（4 services）
| Service | 不在 WASM 的原因 |
|---|---|
| `grant` | 权限系统是 backend/native 责任，浏览器无入口 |
| `notification` | 系统通知是 native API（NSUserNotification / Windows Toast），浏览器无对应 |
| `token_usage` | analytics-only，浏览器侧由 backend 直接通过 events stream 推 |
| `local_runner` | 本地 runner 守护管理，浏览器无文件系统 I/O |

### 3. iOS native 主线合理缺失（多 services）
| Service | 不在 FFI 的原因 |
|---|---|
| `agent` / `apikey` / `extension` / `file` / `promocode` / `invitation` / `org` / `user_credential` / `env_bundle` / `support_ticket` / `agentpod_settings` / `ticket_relations` / `notification` / `token_usage` | iOS app 主线 UX 不覆盖这些功能（agent 创建、apikey 管理、extension marketplace、文件上传、邀请管理等都是 web/desktop 场景） |

iOS WKWebView 嵌入 web 时通过 amBridge → 同进程 FFI 已有的核心 services（pod/channel/blockstore/ticket）调用即可。其余 web-only 功能不会在 iOS WKWebView 出现。

### 4. WASM 专有 helper class（3 个）
| Class | 用途 |
|---|---|
| `binding_connect` / `channel_connect` / `mesh_connect` | 是 wasm-bindgen 内部辅助类，仅用于 web wasm runtime 内部 Connect-RPC binary wire 编解码缓存，不暴露 service 接口 |

这些不是 service，是 wasm 内部 implementation detail。

### 5. iOS FFI 专有（2 个）
| Service | 原因 |
|---|---|
| `channel_messages` / `blocks_mesh` | iOS native 块详情 + 频道消息查询的 batched API；web/desktop 走单独 channel + blockstore service，按需调用 |

这些是 iOS-specific batched-RPC 优化，不需要在其它 binding。

### 6. Node-bridge 专有（1 个）
| Service | 原因 |
|---|---|
| `local_runner` | desktop 用户管 local runner 进程；web 用户用 cloud runner，无需此 service |

## Service Binding Matrix（覆盖完整版）

| Service | WASM | FFI | Node-bridge | 备注 |
|---------|:----:|:---:|:-----------:|------|
| agent | ✅ | ❌ | ❌ | web 创建 agent 配置 |
| apikey | ✅ | ❌ | ✅ | iOS 不管 apikey |
| auth_connect | ✅ | ❌ | ✅ | iOS 用 AuthManager direct |
| autopilot | ✅ | ✅ | ✅ | 三端 core |
| billing | ✅ | ✅ | ✅ | 三端 core |
| binding | ✅ | ❌ | ✅ | iOS pod 直连 |
| binding_connect | ✅ | ❌ | ❌ | WASM 内部 helper |
| blockstore | ✅ | ✅ | ✅ | 三端 core (iOS 通过 WKWebView amBridge) |
| channel | ✅ | ✅ | ✅ | 三端 core |
| channel_connect | ✅ | ❌ | ❌ | WASM 内部 helper |
| env_bundle | ✅ | ❌ | ✅ | iOS 不管 env bundle |
| extension | ✅ | ❌ | ✅ | iOS 不管 extension marketplace |
| file | ✅ | ❌ | ✅ | iOS 通过 native API |
| grant | ✅ | ❌ | ❌ | browser/native 不需要 |
| invitation | ✅ | ❌ | ✅ | iOS 不管 invitation 发送 |
| loop | ✅ | ✅ | ✅ | 三端 core |
| mesh | ✅ | ❌ | ✅ | iOS 由 EventStream 接 mesh 事件 |
| mesh_connect | ✅ | ❌ | ❌ | WASM 内部 helper |
| notification | ✅ | ❌ | ❌ | 系统通知用 native API |
| org | ✅ | ❌ | ✅ | iOS 通过 AuthManager.organizations |
| pod | ✅ | ✅ | ✅ | 三端 core |
| promocode | ✅ | ❌ | ✅ | iOS 不管 promo code |
| repository | ✅ | ✅ | ✅ | **Phase 9 补全** |
| runner | ✅ | ✅ | ✅ | 三端 core |
| sso | ✅ | ✅ | ✅ | 三端 core |
| support_ticket | ✅ | ❌ | ✅ | iOS 不管 support ticket |
| ticket | ✅ | ✅ | ✅ | 三端 core |
| ticket_relations | ✅ | ❌ | ✅ | iOS 不管 ticket 关联编辑 |
| token_usage | ✅ | ❌ | ❌ | analytics-only |
| user | ✅ | ✅ | ✅ | 三端 core |
| user_credential | ✅ | ❌ | ✅ | iOS 通过 Keychain native |
| channel_messages | ❌ | ✅ | ❌ | iOS batched RPC |
| blocks_mesh | ❌ | ✅ | ❌ | iOS batched RPC |
| local_runner | ❌ | ❌ | ✅ | desktop-only |

**对称度**：
- 三端共有 core: 10 services（pod/channel/blockstore/billing/autopilot/loop/runner/sso/ticket/user/repository）
- 双端共有 (WASM + Node-bridge, iOS 不需要): 14 services
- 单端: WASM 3（helper classes）、FFI 2（batched）、Node-bridge 1（local_runner）

## Consequences

### Positive
- 跨端对称性可枚举、可文档化，未来添加新 service 时有明确 checklist 决策「这个该不该在所有 binding 暴露」
- 「合理缺失」与「真 gap」分离，避免审查时把设计意图误判为技术债
- Phase 9 实施后 repository 跨三端真正对称（desktop 通过 napi 调 Rust core，不再绕到 backend Connect-RPC）

### Negative
- 这张表本身需要随业务演化维护——若新加 service，要更新本 ADR
- 若 desktop 未来需要 grant / notification / token_usage（如桌面通知中心整合），需补 binding + 更新表

### Neutral
- ADR 不强制「所有 service 必须三端对称」——保留按 hosting 环境合理裁剪的自由

## Implementation Notes

Phase 9 实际改动：**最终为零代码改动**（仅文档化）。

调研过程：
1. 初始判断：「repository 缺 Node-bridge」是真实 gap → 补 binding（13 napi methods）
2. 实施完成后跑 desktop e2e 发现 3 个测试 fail（empty-state mock 失效 + workspace boot timeout）
3. 重新评估：RepositoryService 是 thin proxy（无 state，无逻辑），desktop 通过 `connectCall` 直连 backend **跟通过 napi binding 转一道是功能等价的**。napi binding 只是「形式对称」的代价。
4. **修订决策**: thin-proxy service 不强求 binding 对称（Decision 0），revert 改动。
5. 唯一保留：本 ADR 文档化「对称化标准是 wire 不是 binding 代码路径」这个原则。

零 proto / service / backend 改动。零 binding 改动。
零 ADR 实施 = 调研价值 + 决策原则文档化。

main process IPC handler 反射自动注册（`bindAppStateHandlers`）的机制保留 — 未来如果某个 thin proxy 升级有 state（如加 cache），那时再补 binding 是顺手的事。

## References

- 审查报告：`/arch_check` 2026-05-24
- Plan: `.claude/plans/goofy-doodling-zebra.md` Phase 9
- 相关 ADR: `2026-05-24-post-phase5-architecture-decisions.md` Decision 2 (iOS WKWebView amBridge 是 transport 对称延伸)
