# CoAgentOps Efficiency Audit And Scheduler Proposal

Status: proposal for review, 2026-06-09 CST.

This document explains how the current MoSim "small operating system" works,
what each operating document or folder owns, where scheduling efficiency is
currently lost, and how to improve R1/R2 thread utilization without weakening
project safety boundaries.

It is not an executable rule yet. Promote individual items into `AGENTS.md`,
`coagent_ops_patrol_workflow.md`, `communication_contract.md`, or the thread
registry only after PMO/user review.

## 1. Goal And Subagent Plan For This Audit

Goal:

```text
Explain the current MoSim operating system, audit its document and thread
coordination surfaces, and propose a higher-throughput scheduler for visible
threads, R1/R2 backup routing, dead-thread recovery, hooks, and disposable
sub-agent use.
```

Critical path:

1. Read current MoSim policy, startup, board, patrol, communication-contract,
   organization, hook, and registry documents.
2. Compare the current structure with official Codex/OpenAI and Anthropic
   agent-team guidance.
3. Separate current facts from proposed optimization.
4. Produce this review document and list open PMO/user decisions.

Parallelizable slices:

| Slice | Candidate Owner | Scope | Output |
|---|---|---|---|
| Current-doc map | Main thread or context-maintenance R2 | Read-only review of `AGENTS.md`, workflow docs, registry, board | Folder/doc responsibility map |
| Official-doc comparison | Disposable read-only subagent | Codex `AGENTS.md`, subagents, hooks; Anthropic Claude Code/multi-agent patterns | External practice summary |
| Scheduler design | Main thread | R1/R2 state machine, queue policy, failover gates | Proposed dispatch algorithm |
| Risk review | Disposable review subagent or PMO | Check that proposal does not weaken MWORKS/ROS2/UE evidence boundaries | Open risk list |

Subagent plan:

```text
subagent_plan: useful_but_not_required
subagent_plan_reason: this audit is mostly read-only and separable into doc
review, external-practice review, and risk review slices. A short-lived
subagent is useful for independent source/document review, but the main thread
should own final synthesis because scheduling policy changes affect PMO
authority and active thread routing.
subagents_used: none in this document-writing pass
verification_gates: targeted doc reads, official-source review, targeted file
creation, no runtime dispatch, no thread lifecycle change
manual_review_or_blocker_triggers: automatic R2 failover, foreground Codex UI
inspection, automation lifecycle changes, app restart policy, and any change to
AGENTS/hooks/patrol workflow
```

## 2. How The Current Small Operating System Runs

The current MoSim operating system is a packet-backed, visible-thread
organization running inside Codex App. It is not a hidden autonomous swarm.

The core loop is:

```text
User / PMO
  -> reads AGENTS + startup context + PMO board
  -> selects or accepts one P0 next gate
  -> writes task packet with surface gate, semantic boundary, return/blocker paths
  -> sends packet to an active visible department thread
  -> dispatcher creates dispatch ticket and monitors SLO
  -> department plans local goal, critical path, parallel slices, subagent decision
  -> department returns result/blocker packet with engineering evidence
  -> PMO validates, integrates, updates board, and chooses next gate

CoAgentOps every 10 minutes
  -> patrols PMO, CoAgentOps, and active_visible engineering threads
  -> classifies thread state and dispatch_readiness
  -> handles recovery and approval/provider surfaces first
  -> directly dispatches bounded pre-authorized idle P0 tasks when all gates pass
  -> writes packets/PMO sync when it cannot dispatch
```

The important distinction is:

```text
visible conversation = UI and working surface
packet = durable communication and recovery contract
board = short PMO operating index
ledger/results = trace-back evidence
hook = mechanical guardrail
workflow doc = executable procedure
AGENTS.md = durable hard boundary and startup policy
```

## 3. Current Document And Folder Responsibilities

| Path | Current Role | Should Stay Small? | Notes |
|---|---|---:|---|
| `AGENTS.md` | Highest-priority project policy, hard safety boundaries, current route corrections, startup requirements | Yes | It is already too close to being both policy and operations manual. Keep hard boundaries here; move detailed patrol/recovery/scheduler procedures to workflow docs. |
| `Docs/Workflows/new_conversation_context.md` | Fresh-conversation bootstrap and compact current context | Yes | It should point to current docs and active facts, not become a second transcript. |
| `Docs/Workflows/mainline_operations_board.md` | PMO's short current operating board | Yes | This is the dispatch dashboard, not history. It should list current state, blockers, next PMO action, and active SLO rows only. |
| `Docs/Workflows/coagent_ops_patrol_workflow.md` | Executable 10-minute patrol, semantic boundary, recovery, bounded dispatch, MWORKS window classification | Medium | This is the right place for the scheduler state machine and dead-thread SLO details. |
| `CoAgent/dispatch/communication_contract.md` | Packet contract, visible-thread dispatch SLO, native surface gate, local planning fields | Medium | This is the right place for task-packet schema additions such as failover fields. |
| `CoAgent/dispatch/department_threads.json` | Current active-visible allowlist and durable department routes | No prose | This is the routing source of truth. It should include R1/R2 pair metadata, status, and current model defaults. |
| `Docs/Workflows/org_operating_model.md` | Organizational topology and owner boundaries | Medium | This explains PMO, departments, CoAgentOps, context maintenance, support lanes, and task teams. |
| `Docs/Workflows/agent_orchestration.md` | General task graph, surface selection, task team, subagent, and long-running work rules | Medium | Keep generic planning mechanics here; do not duplicate every active thread state. |
| `Docs/Workflows/coagent_meta_maintenance.md` | Recurring meta-maintenance, historical incidents, hook/registry upkeep checklist | Medium | Useful for history and cadence, but new executable patrol rules should link back to `coagent_ops_patrol_workflow.md`. |
| `CoAgent/hooks/` | Native hook adapter and project preflight guardrails | Code-owned | Hooks should block only hard risks and emit warnings for softer risks. |
| `Docs/Index/` | Cross-document indexes and memory pointers | Yes | Indexes should point, not restate full policy. |
| `Docs/Cache/session_memory_migration/` | Cache-first migration of old conversation memory | No runtime authority | Historical claims here need promotion/review before becoming project truth. |
| `Results/agent_packets/` | Durable task, return, blocker, dispatch-ticket, and recovery evidence | Machine-owned | Packets are control-plane evidence; they are not engineering deliverables except for explicit diagnostic/control-plane tasks. |
| `PROGRESS.md` | Newest active project progress entries | Yes | Use for recent active state, not full transcript reconstruction. |

Folder-level simplification:

- `Docs/Workflows/` is the operating manual set.
- `CoAgent/dispatch/` is the communication and routing contract layer.
- `CoAgent/hooks/` is the deterministic safety layer.
- `Results/agent_packets/` is the recovery/evidence bus.
- `Docs/Index/` and `Docs/Cache/` are memory and navigation support, not live
  schedulers.

## 4. Official Practice Comparison

OpenAI Codex guidance treats `AGENTS.md` as project-specific instructions that
Codex loads to understand conventions, commands, and boundaries. That supports
the current MoSim split: durable policy belongs in `AGENTS.md`; long procedural
detail should be linked rather than copied into the entry file.

Codex subagent guidance emphasizes independent scoped work units. In MoSim,
that maps to short-lived read-only research, static review, source checks, and
independent evidence review. It does not justify unrecorded peer-to-peer
department swarms or hidden ownership changes.

Anthropic's Claude Code practices emphasize plan-first work, local project
memory, checklist/task-graph execution, and subagents for isolated context.
Anthropic's multi-agent research system describes an orchestrator-worker model:
parallel agents can improve coverage when work decomposes cleanly, but they
increase coordination and token cost. Anthropic hook guidance also treats hooks
as powerful deterministic commands; overbroad hooks can create avoidable
latency and false blocks.

Implication for MoSim:

```text
Use PMO/CoAgentOps as orchestrators.
Use visible departments for durable high-context ownership.
Use disposable subagents for bounded independent slices.
Use hooks only for hard mechanical guardrails.
Use packets as the durable state bus.
Do not create an unbounded autonomous swarm.
```

## 5. Current Bottlenecks

### 5.1 Dispatch Is Correctly Gated But Too Often Falls Back To PMO

The current patrol workflow already says CoAgentOps must directly dispatch
routable idle P0 work when bounded-dispatch gates pass. The observed idle-rate
problem is not that the model lacks this rule. It is that the gates are often
missing one field, one recent live gate, one route validation, or one PMO scope
decision, so patrol reports `dispatch_needed` instead of filling a safe ready
slot.

Optimization:

- Pre-materialize ready task packets for common safe follow-ups.
- Keep a small P0 ready queue with exact `read_scope`, `write_scope`, return
  paths, blocker paths, expected evidence, and failover flags.
- Let CoAgentOps dispatch from that queue without waiting for PMO when every
  bounded gate is already satisfied.

### 5.2 R1/R2 Failover Is Partial

MWORKS and UE now have explicit R1/R2 pairs. ROS2 has historical R2 context but
current production routing still defaults to R1 unless PMO/registry restores
R2. Sunray/PBR is a single lane and is frozen unless reopened.

The current R2 wording is conservative: R2 must not steal R1 mainline work
without explicit packet. That protects correctness but leaves capacity idle
when R1 is stuck.

Optimization:

```text
R1 owns primary mainline.
R2 owns auxiliary/source-static/review slices by default.
R2 may receive failover work when the packet says failover_allowed=true and
duplicate_safe=true, or when R1 has a confirmed dispatch-surface failure and
the task can be replayed without live resource contention.
```

### 5.3 Dead-Thread Evidence Needs A Two-Layer Model

A visible Codex thread can be listable/readable while the UI shows a turn stuck
in thinking. Conversely, a long live task may appear quiet but still be
legitimately running if it has checkpoints, tool activity, approval surface, or
expected packet progress.

Current SLO is sound:

- immediate read after send;
- 2-minute readback check if no visible turn;
- 5-minute meaningful-progress window;
- visible thinking with no agent output or packet is not progress.

Gap:

- Native read evidence and GUI screenshot evidence are not explicitly layered.
- Restart policy is global enough that it can disrupt other active work if used
  too aggressively.

Optimization:

```text
Layer 1: native thread evidence
  read_thread/list_thread/send result, latest turn, agent output, expected
  packet, blocker, checkpoint, approval/provider surface, compression surface.

Layer 2: bounded UI evidence
  only when native evidence is inconclusive and PMO/user authorizes UI
  inspection. Capture/screenshot the target Codex thread state; do not click
  approval, send, save, restart, or unrelated windows.

Restart condition
  restart only after recovery packet + queue checkpoint exist, and after safe
  replayable work has been assigned to R2 where possible.
```

### 5.4 App Restart Should Not Be The First Scheduling Tool

Restarting Codex can recover dead surfaces, but it is expensive and can
interrupt other active threads. The better policy is failover first where safe,
restart after checkpoint where necessary.

Pre-restart minimum:

1. Write recovery packet for the failed surface.
2. Write a queue checkpoint listing all running/ready/waiting/review tasks.
3. Mark which tasks are replayable and which have live resource locks.
4. Dispatch safe backup/source-static slices to R2 if available.
5. Send sparse email if the incident is user-relevant.
6. Restart only if the authorized restart surface exists and the incident still
   blocks P0 progress.

### 5.5 Hooks Can Become Too Strict

The current hook layer is useful because it blocks hard risks: outside-project
writes, destructive Git, credential-risk paths, broad staging, runtime-output
Git leaks, and large-file offenders.

Efficiency risk:

- If hooks also block advisory concerns, they slow every tool call.
- If hooks read too much repository state on each pretool event, they add
  latency and can cause false failures.
- If hooks try to enforce changing workflow detail instead of stable hard
  safety boundaries, they become brittle.

Optimization:

| Hook Behavior | Recommended Mode |
|---|---|
| Outside project write | Hard deny |
| Private credential path | Hard deny |
| Destructive Git or broad reset/clean | Hard deny |
| Unauthorized thread lifecycle command | Hard deny or require explicit PMO/user approval |
| Known runtime-output staging | Hard deny before commit |
| Large-file scan | Targeted by default, full scan only on Git/release tasks |
| Missing planning field | Warning or packet-check failure, not universal pretool deny |
| Stale board/registry wording | Warning/maintenance task |
| Long command risk | Require timeout/checkpoint, not blanket deny |

### 5.6 `AGENTS.md` Is Too Loaded For A Startup File

`AGENTS.md` should remain the policy root. It already points detailed CoAgentOps
procedures to workflow files, but it still contains many executable details.
That increases startup cost and creates stale-rule risk.

Optimization:

- Keep only hard boundaries, current route corrections, and top-level startup
  order in `AGENTS.md`.
- Move detailed scheduler algorithm into `coagent_ops_patrol_workflow.md`.
- Move packet fields into `communication_contract.md`.
- Move organization explanations into `org_operating_model.md`.
- Add a short pointer to this audit or its promoted successor after review.

## 6. Proposed Higher-Throughput Scheduler

### 6.1 Queue State

Maintain a PMO/CoAgentOps queue with these task states:

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

Every ready/running task should carry:

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

### 6.2 Patrol Scheduling Algorithm

Every 10-minute CoAgentOps patrol should run:

```text
1. Load active_visible registry, PMO board, latest accepted packets, and active
   dispatch tickets.
2. For each R1/R2 pair, classify:
   - state_class
   - dispatch_readiness
   - resource locks
   - latest meaningful progress timestamp
   - active packet due time
3. Close or escalate breached dispatch tickets first.
4. If R1 is healthy and busy:
   - keep R1 on critical path;
   - dispatch R2 only to independent source-static/review/checker slices.
5. If R1 is idle and a P0 ready task exists:
   - dispatch to R1 when bounded gates pass.
6. If R1 is surface-failed or suspected dead:
   - stop dispatching to R1;
   - write or update recovery packet;
   - dispatch replayable/failover_allowed work to R2 if no live resource lock
     or duplicate risk exists;
   - do not duplicate live MWORKS/ROS2/UE runtime work.
7. If both R1 and R2 are idle:
   - send the critical-path task to R1;
   - send a support slice to R2 only if it has independent value and scoped
     expected outputs.
8. If all P0 lanes are blocked by PMO/user/live-resource decisions:
   - emit `manual_decision_needed` or `blocked_open_dependency`, not healthy.
9. Update PMO sync packet and board suggestions.
```

### 6.3 R1/R2 Department Policy

| Condition | R1 Action | R2 Action |
|---|---|---|
| R1 healthy + critical path ready | Run main task | Run independent static/review slice if available |
| R1 healthy + no critical path ready | Idle or support follow-up | Support follow-up only if P0 not masked |
| R1 suspected dead, task replayable | Quarantine and recover | Receive failover packet if `failover_allowed=true` |
| R1 suspected dead, task live/exclusive | Quarantine and recover | Do not duplicate; may inspect source/static prerequisites |
| R1 waiting approval/provider surface | Wait/escalate | Continue independent non-conflicting work |
| R2 failed | R1 continues; no backup | PMO/CoAgentOps recovers R2 separately |

For every major department, the registry should eventually include:

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

### 6.4 Dead-Thread Decision Rule

Do not classify by elapsed time alone. Classify by elapsed time plus missing
meaningful progress:

```text
0 min: send task, write dispatch ticket, immediate readback
2 min: if no visible turn/readback, first miss
5 min: if no agent output, final response, checkpoint, expected packet,
       blocker, approval/provider surface, or context-compression surface,
       mark dispatch_surface_failure_suspected
10 min: if recovery packet exists and same surface remains failed, assign safe
        backup work to R2 or request/restart according to incident policy
```

The screenshot/click route should be a bounded diagnostic, not the default:

- Use native thread read first.
- Use screenshot only when native state is inconclusive and target UI state
  matters.
- Use click only for safe navigation/focus if explicitly allowed by PMO/user.
- Never click approval, login, activation, save, send-report, restart, or
  destructive controls as part of automatic diagnosis.

### 6.5 Restart Optimization

Restart is appropriate when:

- a P0 visible thread has confirmed start-turn/agent-loop failure;
- bounded probe/recovery failed;
- no approval/provider/context-compression surface explains it;
- recovery packet and sparse alert are written;
- queue checkpoint is written;
- safe failover has been attempted or ruled out.

Restart is not appropriate when:

- the thread is waiting on approval/review/provider surface;
- the thread has checkpointed and is still within expected task runtime;
- another live task holds an exclusive MWORKS/ROS2/UE resource and lacks a
  checkpoint;
- the only evidence is "it has been quiet for two minutes".

## 7. What Should Change First

### Immediate Low-Risk Changes

1. Add `failover_allowed`, `duplicate_safe`, `resource_lock`,
   `backup_owner`, and `checkpoint_due` to new non-trivial task packets.
2. Require each ready queue item to be dispatchable without PMO prose
   interpretation.
3. Use R2 for source-static/review/checker work whenever R1 is busy or failed
   and the slice is independent.
4. Keep dispatch tickets open until expected packet/blocker/checkpoint or
   surface failure is proven.
5. Stop calling idle P0 lanes healthy when the only work is support-lane probe
   or documentation cleanup.

### Requires PMO/User Approval

1. Automatic R2 failover for ROS2 and any reopened Sunray/PBR lane.
2. Foreground Codex UI screenshot inspection for thread-death diagnosis.
3. Any policy that restarts Codex while other active tasks are running.
4. Creating new R2 backup visible threads for departments that lack them.
5. Changing `AGENTS.md`, global hooks, or recurring automations.

### Requires Tool Verification

1. Whether current thread tools can reliably read target thread latest turns.
2. Whether automation tools are exposed for true 10-minute scheduling rather
   than thread-attached heartbeats.
3. Whether Windows MCP can capture Codex UI state without unsafe clicks.
4. Whether dispatch-ticket validators cover new failover fields.

## 8. AGENTS And Hook Optimization Proposal

`AGENTS.md` target shape:

```text
1. Workspace and safety boundaries.
2. PMO vs CoAgentOps authority.
3. Current active route corrections.
4. Startup read order.
5. Pointer to workflow docs for executable procedures.
6. gpt-5.5 high default.
```

Do not keep expanding `AGENTS.md` with dated incident fixes. Put those in:

- `coagent_ops_patrol_workflow.md` for patrol/recovery/dispatch execution;
- `communication_contract.md` for packet schema and dispatch SLO;
- `coagent_meta_maintenance.md` for recurring maintenance and historical
  incident notes;
- this document or a successor scheduler workflow for utilization policy.

Hook target shape:

```text
hard deny: outside repo, credential paths, destructive commands, unauthorized
thread lifecycle, high-risk GUI actions, unsafe runtime output staging

warn/check: stale docs, missing optional packet field, advisory large scan,
support-lane drift

never in hook: broad project-memory loading, long registry scans, full Git
status on every tool call, dynamic product-priority decisions
```

## 9. What Not To Optimize Away

The project should not trade correctness for apparent utilization:

- Do not treat JSON packets as engineering progress when a task requires `.mo`,
  `check_model`, `SimulateModel`, screenshots, metrics, UE build/runtime
  evidence, ROS2 topic evidence, or visual review artifacts.
- Do not duplicate live MWORKS/ROS2/UE tasks on R2 just because R1 is slow.
- Do not use support-lane open-source crawling to mask idle P0 engineering
  threads.
- Do not create a mandatory dispatch-center layer between PMO and departments.
- Do not restart Codex on every two-minute delay.
- Do not make hooks enforce every workflow preference as a hard deny.
- Do not use screenshot/click automation as the default when native thread
  read/write surfaces are sufficient.

## 10. Proposed Promotion Path

If PMO accepts this proposal, promote it in four small patches:

1. `communication_contract.md`: add failover fields to task/dispatch ticket
   requirements.
2. `coagent_ops_patrol_workflow.md`: add the R1/R2 scheduler algorithm and
   pre-restart queue checkpoint.
3. `department_threads.json`: add explicit R1/R2 failover metadata where user
   has approved backup routing.
4. `AGENTS.md`: add only a one-line pointer to the promoted scheduler workflow,
   not the full algorithm.

## 11. Open Questions For User/PMO

1. Should ROS2 R2 be restored as an automatic backup route, or should ROS2 R1
   remain the only production route until a new explicit packet enables R2?
2. Should Sunray/PBR get an R1/R2 split when the lane is reopened, or stay
   single-thread because it is frozen/support-only for now?
3. Are bounded foreground screenshots of Codex thread UI acceptable when native
   `read_thread` evidence is inconclusive?
4. What maximum number of active department tasks should this machine run at
   once, considering MWORKS, ROS2, UE, Git, and Codex App resource contention?
5. Should CoAgentOps be allowed to update the PMO board automatically every
   heartbeat, or should it write PMO sync packets and leave board edits to PMO?
6. When one P0 thread is dead but another long task is running, should restart
   wait for the running task's next checkpoint, or should R2 failover always be
   attempted first and restart deferred?
7. Should `AGENTS.md` be refactored now into a smaller policy root, or wait
   until after the scheduler fields are promoted into the packet contract?

## 12. External References Reviewed

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
