# Phase 5 — Wire adapter (*Types.ts) 系统性删除

**日期**: 2026-05-24
**状态**: in progress

## 决策

撤回之前 `2026-05-24-r7-rest-cleanup.md` ADR 中的"保留 adapter"判断。
**删除 24 个 `*Types.ts` adapter**，hooks/components 直接消费 proto 类型 (`@proto/<x>/v1/*_pb`)。

## 撤回理由

原 ADR 论证的"adapter 解耦 wire 变更"是**假的解耦**：
- proto 改字段名是 wire-breaking — 客户端必须重新编译，adapter `fromProto` 必定红
- adapter 只是把改动点从 hook 挪到 adapter，多一层 friction，不能屏蔽变更
- 实际成本：
  - 维护 2 处定义（proto + adapter），每加字段写 2 遍
  - Silent failure 风险（EnvBundle UI 9 测试失败花 1 小时调试，根因就是 adapter 字段映射不一致）
- "200+ 组件 churn"被高估：IDE 时代字段重命名 + tsc 是 30 分钟机械工作

## 边界规则

**Wire 类型** (proto) 与 **业务 ViewModel** 分离：

| 类型 | 来源 | 命名风格 | id 类型 | 例子 |
|---|---|---|---|---|
| **Wire** | `@proto/<x>/v1/*_pb` | camelCase | bigint | `EnvBundle`, `Channel`, `Pod` |
| **ViewModel** | `lib/viewModels/<x>.ts` | snake_case | number | `EnvBundleSummary`, `CredentialProfileViewModel`, UI markdown `Block`/`InlineElement` |

**判断标准**：
- 如果 Type 名字带 `Summary` / `ViewModel` / 业务别名 (`CredentialProfile`) / UI 内部 schema (markdown `Block`、`InlineElement`) → ViewModel，保留并移到 `lib/viewModels/`
- 如果 Type 名字跟 proto message 一致 (`EnvBundle`, `Pod`, `Channel`) → wire mirror，删除并直接用 proto

## *Connect.ts 重写模式

```ts
// 旧 adapter pattern
function fromProto(p: ProtoX): X { return { ...mapSnakeCase(p) }; }
async function listX(): Promise<X[]> { return resp.items.map(fromProto); }

// 新 proto-SSOT pattern
import { type X } from "@proto/<x>/v1/<x>_pb";
export type { X };

async function listX(): Promise<X[]> { return resp.items; }
async function createX(input: MessageInitShape<typeof CreateXRequestSchema>): Promise<X> {
  const req = create(CreateXRequestSchema, input);
  return fromBinary(XSchema, await call(req));
}
```

**输入端**：用 `MessageInitShape<typeof XxxRequestSchema>`，避免手写 input DTO。

**id 边界**：proto `int64 → bigint`。调 API 时 `BigInt(profileId)`，显示给 ViewModel 时 `Number(b.id)`。

**Optional 字段**：proto repeated/map 永不 undefined，配 ViewModel optional 时 `arr.length > 0 ? arr : undefined`。

## 27 个领域进度

### ✅ 已完成（5）

| 领域 | importer | 文件改动 | 状态 |
|---|---|---|---|
| envBundle | 25 | 11 文件 + 新建 ViewModel | PoC，e2e 7/7 通过 |
| notification | 2 | 3 文件 | 主线完成 |
| binding | 1 | 2 文件 | 主线完成 |
| agentpod | 0 (orphan) | 2 文件 | 主线完成（adapter 完全死代码） |
| mesh | 0 (orphan) | 2 文件 | 主线完成（adapter 完全死代码） |

### 🚧 进行中（17）

3 个 agent 并行：

- **Agent 1**: organization, loop, sso, userRepositoryProvider, invitation, supportTicket (6)
- **Agent 2**: apikey, extension, runner, ticket (4)
- **Agent 3**: agent, autopilot, channel, promoCode, tokenUsage, userGitCredential, message (7)

### 📋 剩余（5，大领域）

| 领域 | importer | 复杂度 | 备注 |
|---|---|---|---|
| billing | 14 | 中 | wire mirror，按模板删 |
| channel-message | 16 | **保留** | UI markdown 内部 schema，移到 viewModels/ 不删 |
| message | 16 | 中（agent 3 可能跳过） | wire mirror（mesh.AgentMessage），按模板删 |
| repository | 17 | 中 | wire mirror，按模板删 |
| blockstore | 65 | 高 | 混合：wire 类型删，UI 常量保留并移到 viewModels/ |

## 验证策略

- 每个领域单独 `bazel build //clients/web:src` (tsc) 必须通过
- 全套 e2e 在所有领域完成后跑一次
- ESLint 规则后续加：禁止业务代码直接 import `@proto/*`（强制经过 `*Connect.ts`）— 后续 ADR 落实

## 下一步

- 等 3 个 agent 完成 17 个中小领域
- 主线处理 5 个大领域（billing, message, repository, channel-message[特殊], blockstore[特殊]）
- 整合 + tsc 验证 + e2e 跑全套
- 用 ESLint 加 import 边界规则
