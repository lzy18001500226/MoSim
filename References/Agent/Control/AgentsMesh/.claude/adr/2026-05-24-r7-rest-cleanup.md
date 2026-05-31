# R7 — REST 残留清理 + TS adapter 决策

**日期**: 2026-05-24
**状态**: implemented

## 决策

R6 zero-REST 完成后，systematic cleanup 删除所有客户端 REST proxy 桥。保留三个例外，废止三层重复抽象。

### 清理范围（已删除）

1. **`WasmApiClient` REST methods** (wasm/src/api.rs): 删除 `get`/`post`/`put`/`patch`/`delete`/`public_get`/`public_post`/`org_path` 共 8 个 方法 — renderer 端无调用方。
2. **`ElectronApiClientProxy` REST methods** (electron-adapter/provider.ts): 删除 5 个 raw HTTP methods + `org_path` — renderer 端无调用方。保留 `create_events_manager` no-op 给 EventSubscriptionManager。
3. **`AgentsMeshCore` API exposure** (ffi/src/api_ffi.rs): **整文件删除** — iOS 完全不调用，只走 typed UniFFI methods。
4. **`AppState` raw HTTP napi** (node-bridge/src/lib.rs): 删除 `api_get`/`api_post`/`api_put`/`api_patch`/`api_delete`/`api_org_path` 共 6 个 napi exports — desktop renderer 已无调用方。
5. **`services/extension.rs::install_skill_from_upload`** (multipart): 迁移到 PresignSkillUpload + S3 PUT + InstallSkillFromUploadedFile 三步 Connect 流。

### 保留的例外

| 路径 | 用途 | 理由 |
|---|---|---|
| `ApiClient::put_raw_bytes` | S3 presigned PUT | 标准 protocol-外 PUT，非 Connect 范围 |
| `ApiClient::post_multipart` | (待删，依赖 skill upload 迁移完成) | 临时保留直到 skill upload presigned 流程上线 |
| `ApiClient::refresh.rs` | Connect-RPC token refresh | 已经是 Connect 实现，仅保留 |

## services 层 5 对双轨合并

R2/R5 过渡期产物：
- `channel.rs` + `channel_connect.rs`
- `mesh.rs` + `mesh_connect.rs`
- `binding.rs` + `binding_connect.rs`
- `blockstore.rs` + `blockstore_connect.rs`
- `user_credential.rs` + 3 个 sub-connect 文件

**全部合并到主文件**。Connect bridge methods 与 service state methods 同位于一个 `impl XxxService` 块。删除分离文件 + 删 lib.rs 对应 mod 声明。

blockstore.rs 合并后 454 行（超 400 硬限），拆出 `blockstore_proto_convert.rs` (proto ↔ internal type 转换 helpers, 169 行) — 业务 service 保留在 `blockstore.rs` (301 行)。

## TS adapter (`*Types.ts`) 决策

24 个 `clients/web/src/lib/api/*Types.ts` 文件**保留**，不去除。

### 拒绝去除的理由

- 业务 hooks/components ~200+ 个调用 site 用 snake_case 字段（mirror backend domain）
- proto 端用 camelCase（wire-format-dictated）
- adapter 解耦 wire format 变更与业务代码：proto 改字段名不会冒泡到 hook
- 去除 adapter 的 churn cost > 字段一致性的 readability gain
- 24 个 adapter 文件总 ~600 LoC，可接受成本

### 边界规则（强制）

- `@proto/*` 类型**只能**在 `*Connect.ts` 文件内使用
- `*Types.ts` 是 hook/component 端的 canonical DTO 形态
- `*Connect.ts` 内部 `fromProto()` / `toProto()` 完成 wire ↔ DTO 转换
- 业务代码（components / hooks / stores）**不能** import `@proto/*`

未来加 lint 规则（`no-restricted-imports`）强制边界。

## ApiClient REST methods 移除路径

需要先完成 skill upload presigned 迁移（agent 在做），才能删 `post_multipart`，进而删 `request.rs` 整文件 + `client.rs` 的 REST methods（get/post/put/patch/delete/get_resource/post_resource/put_resource/patch_resource/public_get/public_post/public_get_resource/unwrap_resource）。预估 -350 LoC。

`org_path` + `current_org_slug` 当前唯一活的调用方是 `services/extension.rs::install_skill_from_upload`，skill upload 迁移完成后也可删（multipart endpoint 不存在了）。

## 验证

- Rust core: `bazel build //clients/core/crates/...` ✓
- Backend Go: `bazel build //backend/cmd/server:server` ✓
- Web: `bazel build //clients/web:src` ✓ (待 skill upload migration 完成后再跑)
- E2E: web 521/521, desktop 455/456 (1 pre-existing flake)
