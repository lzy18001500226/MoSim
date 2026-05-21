# Migration & Compatibility Plan（迁移与兼容）

> 说明：本项目是“新 SDK”，不存在服务端数据迁移。但在真实落地时，通常会从：
> - 直接在业务里手写 `fetch/axios` 调用
> - 或已有内部封装脚本/SDK
> 迁移到本 SDK。

## 1. 兼容目标

| 目标 | 说明 |
|---|---|
| 透明替换请求层 | 迁移后业务侧只需要调用 SDK 方法，不再手写 URL/headers/body |
| 行为一致（默认） | 默认成功判定 `code==1000` 与离线文档一致；错误模型更清晰但不丢信息 |
| 可渐进迁移 | 支持“先迁移某个模块/某几个 endpoint”，而不是一次性切换全部 |

## 2. 迁移步骤（从手写 HTTP 到 SDK）

### Step 1：盘点现有调用点

输出一份清单（建议自动化扫描）：
- URL path（例如 `/sendText`）
- 所属模块（参考 `API_SPEC.md` 的 module）
- 使用的 Authorization 注入方式（是否带前缀）
- 请求体字段（必填/可选）
- 响应处理逻辑（是否只看 `code`）

### Step 2：建立映射（调用点 → operationId）

使用 `docs/specs/engineering-spec/02_Technical_Design/API_SPEC.md`：
- 找到 method+path 对应的 `operationId`
- 迁移到 `client.<module>.<method>(params)`

### Step 3：替换实现并保留回滚开关

建议在业务侧提供 feature flag：
- `USE_WKTEAM_SDK=1`

实现方式：
- 保留旧调用实现 1 个版本周期
- 新旧实现并行打点（不记录敏感信息）对比成功率与错误码分布

### Step 4：清理旧代码

当以下条件满足时删除旧实现：
- 新 SDK 路径稳定运行 ≥ 1 周期
- 关键接口成功率不下降
- 业务错误码分布符合预期（或差异可解释）

## 3. API 兼容性与变更策略（SDK 维度）

### 3.1 对外 API（SDK 导出）稳定性

破坏性变更包括但不限于：
- 方法名/模块名变更（影响 import 与调用）
- 错误类型/字段的大改
- 默认重试策略的改变（可能引发副作用）

必须走 `MAJOR` 版本，并在 release note 中给出迁移指南。

### 3.2 与上游接口的兼容

当发现上游接口变动或文档漂移：
- 优先通过 **endpoint 级覆盖** 兼容（不影响其他接口）
- 对解析差异提供回退策略（保留 raw 片段用于诊断）
- 发布 `PATCH/MINOR`，并在变更说明中明确受影响的 operationId

## 4. 回滚方案（业务侧）

由于 SDK 是库，回滚的最小手段是“降级版本”或“切回旧实现”：

- feature flag 关闭 `USE_WKTEAM_SDK`
- 或锁定依赖版本（例如 pnpm lockfile）

> 要求：每次 SDK 升级都必须能通过 lockfile 固定版本回滚。
