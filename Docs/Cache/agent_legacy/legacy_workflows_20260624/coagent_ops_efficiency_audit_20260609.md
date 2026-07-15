# CoAgentOps 效率审计与调度优化建议

状态：人工审核稿，2026-06-09 CST。

本文解释当前 MoSim “小型操作系统”如何运行、每类文档和文件夹承担什么职责、当前线程和子 agent 调度效率损失在哪里，以及如何在不削弱安全边界和工程证据要求的前提下，提高 R1/R2 线程利用率。

本文不是已生效规则。需要 PMO/用户审核后，再把具体条目提升到 `AGENTS.md`、`coagent_ops_patrol_workflow.md`、`communication_contract.md` 或线程注册表。

## 1. 本次审计的 goal 与子 agent 规划

本次 goal：

```text
解释当前 MoSim 小型操作系统，审计文档和线程协作面，结合官方 Codex/OpenAI 与 Anthropic 多 agent 资料，提出更高吞吐的 visible thread、R1/R2 备援、死线程恢复、hook 和 disposable sub-agent 调度方案。
```

关键路径：

1. 阅读当前 MoSim 策略、启动上下文、PMO board、巡检 workflow、通信 contract、组织模型、hook 和线程注册表。
2. 对照官方 Codex/OpenAI 与 Anthropic agent-team 资料。
3. 区分“当前事实”和“建议优化”。
4. 产出本文，并列出需要 PMO/用户拍板的问题。

可并行切片：

| 切片 | 候选 owner | 范围 | 输出 |
|---|---|---|---|
| 当前文档地图 | 主线程或上下文维护 R2 | 只读审查 `AGENTS.md`、workflow、registry、board | 文档/文件夹职责图 |
| 官方资料对照 | 一次性只读 sub-agent | Codex `AGENTS.md`、subagents、hooks；Anthropic Claude Code 与多 agent 模式 | 外部实践摘要 |
| 调度器设计 | 主线程 | R1/R2 状态机、队列策略、failover gate | 调度算法建议 |
| 风险复核 | 一次性 review sub-agent 或 PMO | 检查建议是否削弱 MWORKS/ROS2/UE 证据边界 | 风险清单 |

子 agent 规划：

```text
subagent_plan: useful_but_not_required
subagent_plan_reason: 本次审计以只读分析为主，可以拆成文档审查、外部资料审查、风险复核等独立切片。短生命周期 sub-agent 适合做独立资料审查，但最终调度策略会影响 PMO 权限和 active thread routing，主线程必须负责综合判断。
subagents_used: none in this document-writing pass
verification_gates: 定向读取项目文档，核对官方资料，定向修改本文，不执行运行时派发，不改变线程生命周期。
manual_review_or_blocker_triggers: 自动 R2 failover、前台 Codex UI 截图诊断、automation 生命周期变更、App restart 策略、任何 AGENTS/hooks/patrol workflow 修改。
```

## 2. 当前小型操作系统怎么运行

当前 MoSim 不是隐藏的 autonomous swarm，而是一个“visible thread + packet + board + hook”的本地操作系统。

核心循环如下：

```text
用户 / PMO
  -> 读取 AGENTS + startup context + PMO board
  -> 选择或接受一个 P0 next gate
  -> 写 task packet，包含 surface gate、semantic boundary、return/blocker 路径
  -> 发到 active visible department thread
  -> dispatcher 创建 dispatch ticket 并监控 SLO
  -> department 规划 local goal、critical path、parallel slices、subagent decision
  -> department 返回 result/blocker packet 和工程证据
  -> PMO 验证、集成、更新 board、选择下一步

CoAgentOps 每 10 分钟
  -> 巡检 PMO、CoAgentOps 和 active_visible 工程线程
  -> 分类 thread state 和 dispatch_readiness
  -> 先处理 recovery、approval/provider surface
  -> 满足 bounded gate 时直接派发预授权 P0 idle task
  -> 不能派发时写 packet 或 PMO sync
```

关键区别：

```text
visible conversation = UI 和工作面
packet = durable communication 和恢复 contract
board = PMO 的短状态板
ledger/results = 追溯证据
hook = 机械安全守卫
workflow doc = 可执行流程
AGENTS.md = 持久硬边界和启动策略
```

## 3. 当前文档和文件夹职责

| 路径 | 当前职责 | 是否应保持精简 | 说明 |
|---|---|---:|---|
| `AGENTS.md` | 最高优先级项目策略、硬安全边界、当前路由校正、启动要求 | 是 | 现在已经接近“策略 + 操作手册”混合体。应保留硬边界，详细巡检/恢复/调度过程应放到 workflow。 |
| `Docs/Workflows/new_conversation_context.md` | 新对话启动上下文和当前摘要 | 是 | 应负责指向当前事实和重要入口，不应变成第二份聊天记录。 |
| `Docs/Workflows/mainline_operations_board.md` | PMO 当前短状态板 | 是 | 是 dispatch dashboard，不是历史记录。只保留当前状态、blocker、next PMO action、active SLO row。 |
| `Docs/Workflows/coagent_ops_patrol_workflow.md` | 10 分钟巡检、semantic boundary、recovery、bounded dispatch、MWORKS window classification | 中等 | 最适合承载调度器状态机和死线程 SLO 细节。 |
| `CoAgent/dispatch/communication_contract.md` | packet contract、visible-thread dispatch SLO、native surface gate、本地规划字段 | 中等 | 最适合承载 task packet schema 和 failover 字段。 |
| `CoAgent/dispatch/department_threads.json` | 当前 active-visible allowlist 和部门路由 | 只放结构化数据 | 这是 routing source of truth。应包含 R1/R2 pair metadata、status、model defaults。 |
| `Docs/Workflows/org_operating_model.md` | 组织拓扑和 owner 边界 | 中等 | 解释 PMO、部门、CoAgentOps、上下文维护、support lanes、task teams。 |
| `Docs/Workflows/agent_orchestration.md` | task graph、surface selection、task team、subagent、long-running work 通用规则 | 中等 | 放通用规划机制，不应复制每个 active thread 的状态。 |
| `Docs/Workflows/coagent_meta_maintenance.md` | recurring meta-maintenance、历史 incident、hook/registry upkeep checklist | 中等 | 适合保存历史和 cadence；新的执行规则应回链到 patrol workflow。 |
| `CoAgent/hooks/` | native hook adapter 与 project preflight guardrails | 代码层 | hook 应只硬拦截硬风险，软风险转为 warning 或 checker。 |
| `Docs/Index/` | 跨文档索引和 memory pointer | 是 | 索引只应指路，不应重述完整 policy。 |
| `Docs/Cache/session_memory_migration/` | 旧对话 memory 的 cache-first 迁移 | 没有运行时权威 | 历史 claim 需要审查提升后才成为项目事实。 |
| `Results/agent_packets/` | task、return、blocker、dispatch-ticket、recovery evidence | 机器/证据层 | packet 是 control-plane evidence。除非任务本身是 diagnostic/control-plane，否则不等于工程交付物。 |
| `PROGRESS.md` | 最新 active progress | 是 | 只读最新活跃状态，不作为完整 transcript。 |

文件夹级简化：

- `Docs/Workflows/` 是操作手册集合。
- `CoAgent/dispatch/` 是通信和路由 contract 层。
- `CoAgent/hooks/` 是确定性安全层。
- `Results/agent_packets/` 是恢复和证据总线。
- `Docs/Index/` 与 `Docs/Cache/` 是 memory/navigation 支持，不是 live scheduler。

## 4. 官方实践对照

OpenAI Codex 的 `AGENTS.md` 指南把它定位为项目特定指令，用于让 Codex 理解项目约定、命令和边界。这支持 MoSim 当前方向：持久 policy 放在 `AGENTS.md`，长流程细节通过链接进入 workflow，而不是都堆在入口文件。

Codex subagent 资料强调独立、明确范围、可并行的工作单元。在 MoSim 中，这更适合短生命周期的只读研究、静态 review、source checker、独立 evidence review，不适合不留 packet 的 peer-to-peer swarm，也不适合隐藏式改变 owner。

Anthropic Claude Code 实践强调 plan-first、项目 memory、checklist/task graph 执行、用 subagent 隔离上下文。Anthropic 的 multi-agent research system 是 orchestrator-worker 模式：并行 worker 在任务可清晰拆分时能提高覆盖率，但会增加协调成本和 token 成本。Anthropic hook 文档也把 hook 视为强力的确定性命令；过宽的 hook 会增加延迟和误拦截。

对 MoSim 的含义：

```text
PMO/CoAgentOps 做 orchestrator。
visible department 负责持久高上下文 owner。
disposable sub-agent 负责有界独立切片。
hook 只做硬机械 guardrail。
packet 是 durable state bus。
不要建立无边界 autonomous swarm。
```

## 5. 当前瓶颈

### 5.1 dispatch gate 是正确的，但太容易退回 PMO

当前 patrol workflow 已经要求：CoAgentOps 发现 routable idle P0 且 bounded-dispatch gate 全满足时，必须直接派发，而不是只告诉 PMO。

所以 idle-rate 高的问题不是“没有直接派发规则”，而是 gate 经常缺一个字段、一个 recent live gate、一个 route validation 或一个 PMO scope decision，导致巡检只能返回 `dispatch_needed`。

优化方向：

- 预先物化常见 safe follow-up 的 ready task packet。
- 保持一个小型 P0 ready queue，每项都提前写清 `read_scope`、`write_scope`、return path、blocker path、expected evidence、failover flags。
- 当所有 bounded gate 已满足时，CoAgentOps 可以从 ready queue 直接派发，不再等待 PMO 重新写同一个 packet。

### 5.2 R1/R2 failover 还不完整

MWORKS 和 UE 已经有明确 R1/R2。ROS2 有历史 R2 语境，但当前生产路由仍默认走 R1，除非 PMO/registry 显式恢复 R2。Sunray/PBR 目前是单 lane，并且用户未重开时冻结。

当前 R2 规则偏保守：R2 不得在没有显式 packet 时抢 R1 主线。这保护正确性，但 R1 卡死时会浪费 R2 容量。

建议策略：

```text
R1 负责 primary mainline。
R2 默认负责 auxiliary/source-static/review slices。
当 packet 标明 failover_allowed=true 且 duplicate_safe=true，或 R1 已确认 dispatch-surface failure 且任务可安全重放、不会争抢 live resource 时，R2 可接收 failover work。
```

### 5.3 死线程证据需要两层模型

visible Codex thread 可能 list/read 都可用，但 UI 显示 turn 卡在“正在思考”。反过来，长 live task 也可能安静一段时间，但如果有 checkpoint、tool activity、approval surface 或 expected packet 进展，就不能当作死线程。

当前 SLO 本身合理：

- 发送后立即 readback；
- 2 分钟无 visible turn/readback，记 first miss；
- 5 分钟无 meaningful progress，进入 surface failure suspicion；
- UI 只显示 thinking 但无 agent output 或 packet，不算进展。

缺口：

- native read evidence 和 GUI screenshot evidence 没有明确分层。
- restart 策略偏全局，过激时可能打断其他活跃任务。

建议模型：

```text
Layer 1: native thread evidence
  read_thread/list_thread/send result、latest turn、agent output、expected packet、blocker、checkpoint、approval/provider surface、compression surface。

Layer 2: bounded UI evidence
  只有 native evidence 不清楚且 PMO/用户授权 UI 检查时使用。只截图/观察目标 Codex thread 状态；不要点击 approval、send、save、restart 或无关窗口。

Restart condition
  只有 recovery packet + queue checkpoint 已写入，且可安全重放的工作已尽量派给 R2 后，才进入 restart。
```

### 5.4 App restart 不应是第一调度工具

重启 Codex 能恢复死 surface，但成本高，也可能中断其他 active threads。更好的顺序是：能 failover 先 failover，必须 restart 时先 checkpoint。

restart 前最低要求：

1. 为失败 surface 写 recovery packet。
2. 写 queue checkpoint，列出 running/ready/waiting/review tasks。
3. 标记哪些 task 可重放，哪些持有 live resource lock。
4. 如果 R2 可用，先派发安全的 backup/source-static slice。
5. 需要用户知情时发 sparse email。
6. 只有授权 restart surface 存在且 incident 仍阻塞 P0 时，才 restart。

### 5.5 hook 可能过严

当前 hook 很有价值：它能拦截项目外写入、破坏性 Git、敏感凭据路径、宽泛 staging、runtime output 混入 Git、大文件风险等硬问题。

效率风险：

- 如果 hook 把 advisory concern 也硬拦截，会拖慢每个 tool call。
- 如果每次 pretool 都读太多仓库状态，会增加延迟和误失败。
- 如果 hook 承担会频繁变化的 workflow 细节，而不是稳定硬边界，会变脆。

建议分层：

| Hook 行为 | 建议模式 |
|---|---|
| 项目外写入 | hard deny |
| 敏感凭据路径 | hard deny |
| 破坏性 Git 或宽泛 reset/clean | hard deny |
| 未授权线程生命周期命令 | hard deny 或要求显式 PMO/用户授权 |
| 已知 runtime output staging | commit 前 hard deny |
| 大文件扫描 | 默认 targeted，只有 Git/release 任务才 full scan |
| 缺少 planning field | warning 或 packet checker failure，不做 universal pretool deny |
| board/registry 命名过期 | warning 或 maintenance task |
| 长命令风险 | 要求 timeout/checkpoint，不 blanket deny |

### 5.6 `AGENTS.md` 对启动文件来说过重

`AGENTS.md` 应保持 policy root。它已经把详细 CoAgentOps procedure 指向 workflow，但仍包含很多执行细节。这样会增加启动成本，也增加 stale-rule 风险。

优化方向：

- `AGENTS.md` 只保留硬边界、当前 route corrections、top-level startup order。
- 调度算法进入 `coagent_ops_patrol_workflow.md`。
- packet 字段进入 `communication_contract.md`。
- 组织解释进入 `org_operating_model.md`。
- 本文或后续正式 scheduler workflow 只放一个短链接。

## 6. 建议的高吞吐调度器

### 6.1 队列状态

PMO/CoAgentOps 维护一个小型 queue，状态限定为：

```text
ready
running
waiting_return
waiting_review_or_approval
blocked_open_dependency
blocked_surface_failure
superseded
completed
```

每个 ready/running task 应携带：

```yaml
request_id:
department:
primary_owner:
backup_owner:
task_class:
priority:
read_scope:
write_scope:
resource_lock:
duplicate_safe: true | false
failover_allowed: true | false
checkpoint_due:
expected_return_path:
blocker_return_path:
dispatch_ticket_path:
expected_engineering_outputs:
manual_review_required: true | false
restart_sensitive: true | false
```

### 6.2 10 分钟巡检调度算法

每次 CoAgentOps patrol 执行：

```text
1. 读取 active_visible registry、PMO board、latest accepted packets、active dispatch tickets。
2. 对每组 R1/R2 分类：
   - state_class
   - dispatch_readiness
   - resource locks
   - latest meaningful progress timestamp
   - active packet due time
3. 先关闭或升级 breached dispatch tickets。
4. 如果 R1 healthy 且 busy：
   - R1 保持 critical path；
   - R2 只接 independent source-static/review/checker slices。
5. 如果 R1 idle 且存在 P0 ready task：
   - bounded gates 满足时派给 R1。
6. 如果 R1 surface-failed 或 suspected dead：
   - 停止派发给 R1；
   - 写或更新 recovery packet；
   - 如果没有 live resource lock 或 duplicate risk，把 replayable/failover_allowed work 派给 R2；
   - 不重复派发 live MWORKS/ROS2/UE runtime work。
7. 如果 R1 和 R2 都 idle：
   - critical-path task 派给 R1；
   - 只有存在独立价值且输出明确的 support slice 时，才派给 R2。
8. 如果所有 P0 lane 都被 PMO/user/live-resource decision 阻塞：
   - 输出 `manual_decision_needed` 或 `blocked_open_dependency`，不要写 healthy。
9. 更新 PMO sync packet 和 board 建议。
```

### 6.3 R1/R2 部门策略

| 条件 | R1 动作 | R2 动作 |
|---|---|---|
| R1 healthy + critical path ready | 跑主任务 | 有独立 static/review slice 时执行 |
| R1 healthy + no critical path ready | idle 或 support follow-up | 只在不掩盖 P0 时做 support |
| R1 suspected dead，任务可重放 | quarantine + recovery | `failover_allowed=true` 时接收 failover packet |
| R1 suspected dead，任务 live/exclusive | quarantine + recovery | 不重复执行；可检查 source/static prerequisite |
| R1 waiting approval/provider surface | 等待/升级 | 继续独立不冲突工作 |
| R2 failed | R1 继续，无 backup | PMO/CoAgentOps 单独恢复 R2 |

每个主要部门后续应在 registry 中补充：

```json
{
  "routing_role": "DEPT_R1_primary_mainline",
  "paired_auxiliary_thread_id": "...",
  "failover_policy": {
    "default_failover_allowed": false,
    "allowed_task_classes": ["source_static", "diagnostic_only", "review", "checker"],
    "forbidden_task_classes": ["live_runtime_without_lock", "manual_gui", "license_login"]
  }
}
```

### 6.4 死线程判定规则

不要只按时间判断。必须用“时间 + meaningful progress 缺失”判断：

```text
0 min: send task，写 dispatch ticket，立即 readback
2 min: 无 visible turn/readback，记 first miss
5 min: 无 agent output、final response、checkpoint、expected packet、blocker、approval/provider surface 或 context-compression surface，则标记 dispatch_surface_failure_suspected
10 min: 如果 recovery packet 已存在且同 surface 仍失败，按 incident policy 把安全 backup work 派给 R2 或进入 restart/request
```

截图/click 路线应是有界诊断，不是默认路径：

- 先用 native thread read。
- 只有 native state 不清楚且 UI 状态本身关键时才截图。
- 只有 PMO/用户明确允许时，才做安全 focus/navigation。
- 自动诊断中不得点击 approval、login、activation、save、send-report、restart 或破坏性控件。

### 6.5 restart 优化

适合 restart 的情况：

- P0 visible thread 已确认 start-turn/agent-loop failure；
- bounded probe/recovery 失败；
- approval/provider/context-compression surface 不能解释；
- recovery packet 和 sparse alert 已写入；
- queue checkpoint 已写入；
- safe failover 已尝试或已排除。

不适合 restart 的情况：

- thread 正在等待 approval/review/provider surface；
- thread 已 checkpoint 且仍在预期任务运行时间内；
- 另一个 live task 持有 exclusive MWORKS/ROS2/UE resource 且还没有 checkpoint；
- 唯一证据只是“安静了两分钟”。

## 7. 优先改什么

### 低风险可先做

1. 新的非平凡 task packet 增加 `failover_allowed`、`duplicate_safe`、`resource_lock`、`backup_owner`、`checkpoint_due`。
2. 每个 ready queue item 必须无需 PMO prose interpretation 即可派发。
3. R1 busy 或 failed 且存在独立 slice 时，用 R2 执行 source-static/review/checker work。
4. dispatch ticket 必须保持 open，直到看到 expected packet、blocker、checkpoint 或 surface failure。
5. support-lane probe 或 docs cleanup 不能掩盖 idle P0 lane。

### 需要 PMO/用户授权

1. ROS2 或未来重开的 Sunray/PBR 自动 R2 failover。
2. Codex UI 前台截图诊断死线程。
3. 其他 active task 正在运行时触发 Codex restart 的策略。
4. 为缺少 backup 的部门创建新 R2 visible thread。
5. 修改 `AGENTS.md`、global hooks 或 recurring automations。

### 需要工具能力验证

1. 当前 thread tools 是否能可靠读取 target thread latest turns。
2. automation tools 是否可用于真正的 10 分钟调度，而不只是 thread-attached heartbeat。
3. Windows MCP 是否能在不做危险点击的情况下捕获 Codex UI 状态。
4. dispatch-ticket validators 是否覆盖新增 failover 字段。

## 8. `AGENTS.md` 与 hook 优化建议

`AGENTS.md` 目标形态：

```text
1. workspace 和 safety boundaries。
2. PMO vs CoAgentOps authority。
3. 当前 active route corrections。
4. startup read order。
5. 指向 executable workflow docs 的链接。
6. gpt-5.5 high default。
```

不要继续把 dated incident fixes 堆进 `AGENTS.md`。应放到：

- `coagent_ops_patrol_workflow.md`：patrol/recovery/dispatch execution；
- `communication_contract.md`：packet schema 和 dispatch SLO；
- `coagent_meta_maintenance.md`：recurring maintenance 和历史 incident notes；
- 本文或后续正式 scheduler workflow：utilization policy。

Hook 目标形态：

```text
hard deny: 项目外写入、敏感凭据路径、破坏性命令、未授权线程生命周期、高风险 GUI 动作、不安全 runtime output staging

warn/check: 过期文档、缺少 optional packet field、advisory large scan、support-lane drift

never in hook: 宽泛项目 memory loading、长 registry scans、每个 tool call 都做 full Git status、动态产品优先级判断
```

## 9. 不能为了利用率牺牲的东西

不能用表面 utilization 换工程正确性：

- 任务要求 `.mo`、`check_model`、`SimulateModel`、截图、metrics、UE build/runtime evidence、ROS2 topic evidence 或 visual review artifacts 时，JSON packet 不能算工程进展。
- 不要因为 R1 慢，就在 R2 重复 live MWORKS/ROS2/UE work。
- 不要用 support-lane 开源 crawl 掩盖 idle P0 engineering threads。
- 不要重新建立 PMO 和 departments 之间的 mandatory dispatch-center。
- 不要每次两分钟延迟都 restart Codex。
- 不要让 hook 把每条 workflow preference 都变成 hard deny。
- native thread read/write 足够时，不要默认使用 screenshot/click automation。

## 10. 建议提升路径

如果 PMO 接受本文建议，分四个小 patch 提升：

1. `communication_contract.md`：把 failover fields 加入 task/dispatch ticket requirements。
2. `coagent_ops_patrol_workflow.md`：加入 R1/R2 scheduler algorithm 和 pre-restart queue checkpoint。
3. `department_threads.json`：在用户已批准 backup routing 的部门加入 R1/R2 failover metadata。
4. `AGENTS.md`：只加一行指向正式 scheduler workflow 的链接，不复制完整算法。

## 11. 需要用户/PMO 拍板的问题

1. ROS2 R2 是否恢复为自动 backup route，还是 ROS2 R1 继续作为唯一 production route，直到新 packet 显式启用 R2？
2. Sunray/PBR 重开后是否也建立 R1/R2 split，还是因为当前冻结/support-only 继续单线程？
3. native `read_thread` 证据不清楚时，是否允许有界前台截图 Codex thread UI？
4. 这台机器最多允许同时跑多少个 active department tasks，尤其要考虑 MWORKS、ROS2、UE、Git 和 Codex App 资源竞争？
5. CoAgentOps 是否允许每次 heartbeat 自动更新 PMO board，还是只写 PMO sync packet，由 PMO 改 board？
6. 一个 P0 thread dead 但另一个 long task 正在跑时，restart 是否等 running task 下一个 checkpoint，还是始终先尝试 R2 failover 并延后 restart？
7. 是否现在就把 `AGENTS.md` 重构成更小的 policy root，还是等 scheduler fields 先提升到 packet contract 后再动？

## 12. 已核对的外部资料

- OpenAI Codex AGENTS.md guide:
  `https://developers.openai.com/codex/guides/agents-md`
- OpenAI Codex subagents concept:
  `https://developers.openai.com/codex/concepts/subagents`
- OpenAI Codex hooks documentation:
  `https://developers.openai.com/codex/config/hooks`
- Anthropic Claude Code best practices:
  `https://www.anthropic.com/engineering/claude-code-best-practices`
- Anthropic multi-agent research system:
  `https://www.anthropic.com/engineering/built-multi-agent-research-system`
- Anthropic Claude Code hooks documentation:
  `https://docs.anthropic.com/en/docs/claude-code/hooks`
