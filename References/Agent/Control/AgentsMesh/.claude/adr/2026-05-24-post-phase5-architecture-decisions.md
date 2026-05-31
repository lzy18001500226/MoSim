# ADR 2026-05-24: Architecture Decisions Post Phase 5

## Status
Accepted

## Context

Phase 5 (R6 Connect migration + adapter removal) 之后做了一次完整架构审查 (`/arch_check`)。审查过程中发现 3 个被误判为「技术债」的设计实际上是合理决策。本 ADR 文档化这些决策，避免未来 reviewer 再次将它们标记为问题。

## Decision 1: Relay 数据面保留二进制 frame，不入 proto

### 上下文
Relay 数据面（Browser ↔ Relay ↔ Runner）用自定义二进制帧格式（type byte + length-prefix bytes），见 `relay/internal/protocol/message.go` 与 `clients/core/crates/wasm/src/relay/`。这是整个系统唯一未走 proto schema 的 wire。

### 决定
**保留二进制帧格式，不迁移到 proto-RPC。**

### 理由
- PTY 字节流是**高频低延迟**场景：单次终端按键 = 一帧。每秒可能数十帧。
- proto 序列化开销（schema lookup + varint encoding）相对于裸字节 + 1 byte type tag **不可忽略**。
- 帧格式极简：type (u8) + payload (bytes)，无嵌套结构，proto 的可演进性价值小。
- message-type 取值由 Rust enum (`MessageType`) 锁住，跨端实现已对齐。

### 后果
- 增加跨端实现负担（每个客户端要手写 codec）— 已通过 wasm-bindgen 暴露 `relay_encode_*` / `relay_decode_message` 给 web/desktop 共用，iOS 通过 UniFFI 调用同一 Rust codec。复用度高。
- 不能像 proto 那样自动生成多语言 codec — 接受。

## Decision 2: iOS WKWebView 内 amBridge — 是 service-runtime transport 注册的对称延伸，不是「另类」

### 上下文
`clients/web/src/lib/ios-bridge/RpcBlockstoreService.ts` 通过 `window.webkit.messageHandlers.amBridge` 暴露 25 个 blockstore JSON-RPC 方法。

初看像是「两套 RPC 并存」（与 iOS 主线 SwiftUI + UniFFI typed bindings）。**这个理解是错的**。

### 真实架构（重要）

业务 JS 在所有场景调用同一组 service interface（`getBlockstoreService()` 等）。**底层 transport 由 `service-runtime` 在启动时切换注册**：

| 场景 | Service 注册的实现 | 业务 JS 体验 |
|---|---|---|
| Browser/PWA | wasm-bindgen class 实例（同进程 wasm runtime） | 一致 |
| Desktop renderer | electron contextBridge proxy → main 进程 napi-rs → Rust core | 一致 |
| iOS WKWebView | amBridge JSON-RPC proxy → Swift Coordinator → UniFFI → Rust core | 一致 |
| iOS native (SwiftUI) | UniFFI typed bindings 直调 | （非 JS 层） |

三种 web JS transport 共享同一个 service interface 契约（`packages/service-interface`），是**同一类东西**，不是「特殊例外」。

### 关键不变量

每个进程内只有**一个** Rust runtime 实例持有 state：

| 进程 | Rust runtime 持有者 | 进程内复用方式 |
|---|---|---|
| Browser tab | wasm runtime（每 tab 一份） | 单 JS 上下文直接调 wasm-bindgen |
| Desktop | main process Rust core | renderer JS → contextBridge → main napi-rs |
| iOS app | native Rust core (UniFFI) | SwiftUI 直调 UniFFI；WKWebView JS → amBridge → 同进程 UniFFI |

### 为什么 iOS WKWebView 内**禁止**加载 wasm（SSOT 的必然推论）

若 WKWebView 也独立加载 21MB wasm bundle 启动 Rust runtime：
- App 进程内会有 2 个 Rust runtime（一个 native UniFFI 持的，一个 WKWebView 内 wasm 持的）
- Native SwiftUI 修改块 → 改的是 UniFFI 持的 state；WKWebView 内 wasm 持的另一份不知道
- 用户在 SwiftUI 和 WKWebView 间切换看到**不一致**的内容
- 违反 「同进程同 SSOT」 不变量

### Runtime 检测机制（service-runtime 切换）

- `WasmProvider.tsx`：`window.location.pathname.startsWith("/blocks-embed")` → **跳过 wasm 初始化**，`setReady(true)` 直接返回
- `blocks-embed/page.tsx`：调 `setupIosBridge()` 替代默认 wasm init，注册 `RpcBlockstoreService` 作为 blockstore service 实现
- 业务 JS（块编辑器）**完全感知不到**底层是 wasm 还是 amBridge

### 后果

- 不是「两个 RPC 表面并存」— 是 service interface 的两种 transport binding（与 Desktop NAPI 完全对称）
- 复用 web 块编辑器 UI（避免 SwiftUI 重写富文本编辑器）的同时维持 SSOT
- 未来若用 SwiftUI 重写块详情，可以删除整个 ios-bridge/ 目录（25 RPC + WKWebView 桥）— 但当前**没有这样的计划**

## Decision 3: types crate 已完成 prost 化（R1c 已结束）

### 上下文
`/arch_check` 报告最初判断「types crate 仍是手写 serde」并标记为高优先级技术债，与任务 #28-38 (R1: 用 prost-build 替换手写 mirror) 声称完成不一致。

### 决定
**R1c 已完成。审查报告判断错误，本 ADR 纠正。**

### 实际状态（已验证）
- `clients/core/crates/types/src/lib.rs`: 31 个 `pub use ::*_proto::*` re-export。
- **0 个** include!()，**0 个** 手写 *_proto.rs 文件。
- 手写补充 ~230 LOC 是**合理的非 proto 边界类型**：
  - `enums.rs` — client-side mapping for proto string-status
  - `runner.rs` — REST-only DTO（runner device auth，proto 不覆盖该路径）
  - `service_error.rs` — wasm/UniFFI/NAPI 错误桥接（无对应 proto）

### 后果
- 这些手写边界类型与 proto 无重叠，不是 dual-track。
- 未来若 runner device auth 改用 Connect-RPC，runner.rs 也应切 proto；但当前 REST 是设计选择（runner 静态二进制不带 wasm runtime，REST 简化分发）。

## Cross-cutting Principles 确认

| 原则 | 状态 | 证据 |
|---|---|---|
| Single-writer invariant | ✅ | `current_org_slug` 只能通过 `AuthManager::set_current_org()` 写，编译期禁止外部写 |
| Rust Core SSOT | ✅ | 业务逻辑只在 `clients/core/crates/services/` 一处，三端 binding 消费 |
| Connect-RPC control plane | ✅ | R5 后 32 REST 路由删尽，control plane 100% Connect |
| Charged domain entity | ✅ | Backend 26 个 entity 包都有行为方法（`Subscription.CanAddSeats()`），非贫血 |
| Wire 双轨明确 | ✅ | Control plane = Connect-RPC binary；Data plane = Relay binary frame；Events = Connect ServerStream |

## References
- 任务 #28-38 (R1 series)
- 任务 #98-101 (R6 state proto)
- Phase 5 ADRs：`2026-05-24-r7-rest-cleanup.md`、`2026-05-24-phase4-invariants.md`、`2026-05-24-phase5-adapter-removal.md`
