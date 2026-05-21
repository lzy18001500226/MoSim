# 输出契约（可复用模板）

> 用途：当用户“要你写 UI/UX 研发规格”，但 PRD/约束不全时，用此模板先补齐输入与输出契约，避免后续漂。

## 1) PRD 最小骨架（缺 PRD 时先补）

至少补齐：
- Goal（目标）
- Users（角色/权限）
- Core Objects（核心对象与术语，例如 Work/Project/Run）
- Key Flows（关键流程 3–5 条）
- Non-Goals（明确不做）
- Acceptance Criteria（验收标准）
- Test Plan（离线回归如何验证）

## 2) UI/UX 研发规格包（必交付物）

- `docs/specs/ui-ux-rd-spec/OVERVIEW.md`：总纲 + TODO
- `docs/specs/ui-ux-rd-spec/DOCS_INDEX.md`：索引
- `docs/specs/ui-ux-rd-spec/00_SourceInventory/COVERAGE.md`：覆盖映射
- `docs/specs/ui-ux-rd-spec/01_Foundation/FOUNDATION.md`：公共基座
- `docs/specs/ui-ux-rd-spec/02_Components/*`：组件契约（可复用控件）
- `docs/specs/ui-ux-rd-spec/04_Pages/*`：页面规格（每页含状态机/AC/测试计划）

## 3) 质量门槛（复刻级定义）

通过线（必须同时满足）：
1) 目录结构本身能说明“分层与覆盖”
2) 页面规格能在没有口头补充的情况下实现复刻（含边界/错误/空态）
3) 可演进内容用契约承接（不写死固定章节）

