# Milestones（里程碑）

> 说明：日期在规格阶段不强制承诺，优先用“可验证交付物”定义里程碑完成条件。

## M1：基础 SDK 可用（P0）

**Status:** Planned

**Deliverables:**
- 可创建 client（配置校验/鉴权注入）
- transport 抽象可注入（默认 fetch）
- 统一错误模型与响应 envelope 解析（默认 `code==1000`）
- 结构化日志 + hooks + 脱敏

**Tasks:** TASK-001..TASK-005

**Success Criteria:**
- 离线单测全部通过
- `pnpm build` 生成可被 import 的产物（哪怕 endpoint wrapper 还未铺开）

## M2：API 覆盖机制闭环（P0）

**Status:** Planned

**Deliverables:**
- endpoint wrapper 的规模化方案落地（生成或通用 request + 薄封装）
- 覆盖性门槛（US-008）测试落地：catalog endpoint 不遗漏
- 至少覆盖 P0 模块的代表性 endpoint（离线 stub）

**Tasks:** TASK-006..TASK-008

**Success Criteria:**
- `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json` 中 `kind='endpoint'` 全部可被 SDK 调用（manifest 校验通过）

## M3：回调/异步任务能力（P1）

**Status:** Planned

**Deliverables:**
- callback payload parse + dedupKey helper
- pollUntil helper（用于异步接口）

**Tasks:** TASK-009..TASK-010

**Success Criteria:**
- AT-005 通过
- helper 有 README 示例（脱敏）

## M4：集成验证与发布准备（P1）

**Status:** Planned

**Deliverables:**
- 可选 integration smoke（环境变量开关）
- `.env.example`、发布 gate、文档收尾

**Tasks:** TASK-011..TASK-012

**Success Criteria:**
- 按 `DEPLOYMENT.md` 的 gate 在新环境可复现（命令 + 结果写入 worklog）

## 风险汇总（对应 `RISKS.md`）

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| 上游隐含契约不明确（baseUrl/token/限流） | M | H | 集成 smoke + 允许配置覆盖 + 文档显式化 |
| 副作用接口重试导致重复执行 | M | H | ADR-004 分类重试 + 默认保守 + 提供开关 |
