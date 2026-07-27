# CoAgent 设计确认简报

日期：2026-05-27

状态：等待用户确认，尚未批准继续实现。

本文是中文确认入口。详细英文版本见
`CoAgent/docs/decisions/coagent_design_review_brief.md`。正式讨论包见
`CoAgent/docs/decisions/coagent_design_discussion_packet.md`。
确认结果必须记录到
`CoAgent/docs/decisions/coagent_design_decision_record.md`，不能只留在聊天里。

## 当前结论

CoAgent 不应该被设计成“很多子 agent 的集合”。

CoAgent 应该是 MoSim 项目自己的工作流控制平面：

- Codex App / VSCode：前端、审阅界面、可见对话界面；
- CoAgent 项目文件：可恢复的事实来源；
- 部门对话：长期职责面，不是隐藏子 agent；
- 一次性子 agent：只做边界清晰的短任务；
- task packet / result packet：跨对话通信格式；
- context pack：长任务启动上下文；
- hooks / policies：硬约束；
- skills：可选择加载的流程知识；
- MCP / tools：能力接口；
- memory / search：带来源的证据检索。

核心原则：控制层要稳定、显式、可恢复；执行层可以专门化，但必须
有任务边界、停止条件和结果证据。

## 30 秒确认摘要

如果你接受默认方案，含义是：

| 项目 | 结论 |
|---|---|
| 常驻对话 | 先保留 7 个：主线总控、调度中台、研发工程、验证测试、文档秘书、安全合规、DevOps 发布 |
| 调度权 | PMO / 调度中台拥有 workflow authority，worker 不自行决定转交任务 |
| 长任务 | 用 task packet、context pack、result packet、artifact/evidence 和 review state 管起来 |
| 状态词 | 区分 simple message、durable task、`input_required`、`auth_required`、`review_required` 和终态 |
| 任务入口 | 先分类再执行：简单回复、清晰任务、复杂任务、混乱事故、含糊任务、长程任务分别走不同规则 |
| 复杂度控制 | 先中心化，再有限分布式；V1 禁止部门内部 durable agent swarm 和 peer-to-peer 隐性通信 |
| Codex App | 只作为 UI / review surface，不作为 durable state source |
| 自动化 | 先 dry-run / guarded；不允许无 hooks / review gate 的自动改代码、文档或 Git |
| 批准后第一步 | 执行 `COAGENT-IMPL-01`：冻结 task-state、event vocabulary、task-intake classes 和 goal hierarchy |

接受这个方案不会立刻启用 app-server transport、unattended automation、
workflow replay，也不会新增 UE/MWORKS/参数识别等常驻部门。

## 建议先保留的常驻对话

当前建议只保留 7 个常驻对话：

| 对话 | 职责 | 不该负责 |
|---|---|---|
| `MoSim｜主线总控` | 和用户对齐目标、优先级、最终决策、综合汇报 | 长时间 Git、测试队列、隐藏执行 |
| `MoSim｜调度中台` | 任务单、状态板、owner 分配、依赖、result packet 回收 | 具体功能实现、Git 执行 |
| `MoSim｜研发工程部` | 默认技术执行线，UE/Fab/MCP/MWORKS/控制器等任务 | 全局优先级、最终验收 |
| `MoSim｜验证测试部` | 独立测试、复现、仿真证据、结果审查 | 实现被测试功能 |
| `MoSim｜文档秘书部` | 用户指令、决策记录、文档一致性 | 全局任务状态调度 |
| `MoSim｜安全合规部` | 路径边界、密钥、大文件、授权、破坏性操作审查 | 产品方向和普通实现 |
| `MoSim｜DevOps 发布部` | Git 状态、分批提交、分支、push、大文件/LFS 检查 | 功能实现和架构批准 |

暂时不新增 UE 部门、MWORKS 部门、参数识别部门、研究部门。长任务用
dedicated task conversation，而不是扩展常驻部门。

## 需要你确认的默认设计

请确认或修改以下 13 项：

1. PMO / 调度中台拥有工作流控制权，worker 不自行路由任务。
2. 现阶段 7 个常驻对话足够。
3. 研发工程部先保持一个通用执行线，只有任务拥堵反复出现时再拆分。
4. DevOps 必须单独保留，因为 Git 风险高、状态重、容易变成长程任务。
5. 文档秘书部只记录决策和维护文档，不拥有完整任务状态板。
6. hooks / policies 负责硬约束，skills 只负责流程知识。
7. 长任务必须有 task_id、父部门、scope、stop condition、context pack、
   result packet。
8. task-state / event vocabulary 必须区分简单回复、长任务、artifact /
   evidence、`input_required`、`auth_required`、`review_required`、
   `completed`、`failed`、`canceled`、`rejected`，不能只用
   `done/blocked`。
9. 任务进入系统前必须先做 intake classification；复杂任务先 discovery，
   长程任务必须有 appetite、circuit breaker、checkpoint 和 escalation。
10. goal 层级必须固定为 Project Goal -> Canonical Task Goal ->
   Conversation Objective -> Subagent Objective；只有 DispatchCenter 记录
   canonical task goal，worker 只能升级不能静默改目标。
11. V1 最大嵌套只允许 PMO/main -> DispatchCenter -> department or
   dedicated task conversation -> short-lived subagent；不允许部门内部
   durable agent swarm。
12. transport 先走 file / CLI；Codex App 暂时只当 UI / review surface。
13. 自动化先保持 dry-run / guarded，不允许在 hooks 和 review gates 证明前
   自动改代码、文档或 Git。

## 如果批准

状态变更：

```text
paused -> ready_for_implementation
```

随后从 `CoAgent/docs/decisions/coagent_post_approval_backlog.md` 开始执行，
第一项是：

```text
COAGENT-IMPL-01: 冻结 task-state、event vocabulary、task-intake classes 和 goal hierarchy
```

批准后第一批实现顺序：

1. 冻结 task-state / event vocabulary / task-intake classes / goal hierarchy，包括 simple
   message、durable task、artifact/evidence、input_required/auth_required/
   review_required、终态、task class、appetite、circuit breaker、checkpoint、
   escalation、acceptance gate、Project Goal、Canonical Task Goal、
   Conversation Objective 和 Subagent Objective。
2. 对齐 task packet / result packet schema。
3. 强化 preflight / hooks。
4. 跑一次小型真实可见对话通信生命周期。
5. 跑一次 dedicated long-task 生命周期。
6. 再决定是否扩展 app-server transport 或 scheduled automation。

批准后先更新：

- `CoAgent/docs/decisions/coagent_design_decision_record.md`
- `CoAgent/docs/decisions/coagent_goal_readiness_audit.md`
- `Docs/Workflows/agent_task_ledger.md`

批准前新增的协议收敛证据：

- `CoAgent/learning/audits/2026-05-27_official_protocol_convergence_round11.md`

## 如果不批准

状态变更：

```text
paused -> design_revision_required
```

需要先修改：

- `CoAgent/docs/decisions/coagent_design_discussion_packet.md`
- `CoAgent/docs/decisions/coagent_design_review_brief.md`
- `CoAgent/docs/decisions/coagent_design_review_brief.zh.md`
- `CoAgent/docs/architecture/ARCHITECTURE.md`
- `CoAgent/docs/architecture/COMPONENT_MAP.md`
- `Docs/Workflows/agent_orchestration.md`
- `Docs/Workflows/agent_task_ledger.md`

典型修改方向：

| 不同意项 | 应该修改 |
|---|---|
| 常驻对话太多 | 合并角色，重写部门边界 |
| 常驻对话太少 | 增加新部门，但必须写清 owner、scope、result contract |
| 调度中台拆分过早 | 先把调度中台作为主线总控下的逻辑角色 |
| 研发工程部应该更早拆 | 写清拆分触发条件和验收边界 |
| file/CLI transport 太弱 | 先定义 app-server 证明门槛 |
| 自动化应该更早启动 | 先定义 hooks、dry-run 证据、人审状态 |

## 你的回复格式

全部接受：

```text
CoAgent design approved.
Decision date: YYYY-MM-DD
Approved defaults: all
Notes: <optional>
```

接受但修改：

```text
CoAgent design approved with edits.
Decision date: YYYY-MM-DD
Accepted defaults: <list>
Rejected or changed defaults: <list>
Required doc updates before implementation: <list>
Notes: <optional>
```

要求重修：

```text
CoAgent design revision required.
Decision date: YYYY-MM-DD
Rejected defaults: <list>
Required changes: <list>
Do not implement until revised packet is reviewed: yes
```

## 当前禁止事项

在你确认前，不做：

- 新增常驻部门；
- app-server transport；
- unattended automation；
- workflow replay；
- task-state schema migration；
- scheduled repo update；
- 无来源证据的 memory promotion；
- 大范围 hooks 重写；
- task/result packet schema 改动；
- 任何运行时代码扩展。
