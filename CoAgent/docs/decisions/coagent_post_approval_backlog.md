# CoAgent Post-Approval Backlog

Date: 2026-05-27

Status: approved checkpoint; `COAGENT-IMPL-01` through `COAGENT-IMPL-07` complete as of 2026-05-28.

This file converts the approved implementation sequence into small tasks with
clear acceptance gates. The entry condition has been satisfied and the first
checkpoint is closed through `COAGENT-IMPL-07`. Do not reopen closed tasks to
expand scope; add a new explicit backlog item instead.

## Entry Condition

Required before any task below starts:

```text
CoAgent design approved
or
CoAgent design approved with edits and required doc updates completed
```

Required recorded evidence:

- `CoAgent/docs/decisions/coagent_design_decision_record.md` status is `approved` or
  `approved_with_edits`,
- decision date,
- accepted defaults,
- rejected/changed defaults, if any,
- next implementation task id,
- updated ledger state: `ready_for_implementation`.

## Checkpoint Evidence

Current completion audit:

```text
CoAgent/docs/decisions/coagent_impl_03_07_completion_audit.md
```

Key evidence paths:

```text
Results/agent_packets/COAGENT-IMPL-04-VISIBLE-LIFECYCLE.yaml
Results/agent_packets/COAGENT-IMPL-05-LONG-TASK-LIFECYCLE.yaml
Results/coagent_bootstrap/COAGENT-IMPL-05-LONG-TASK-LIFECYCLE.recovery.json
Results/coagent_doctor/latest.json
CoAgent/transport/TRANSPORT_EXPANSION_DECISION.md
CoAgent/automation/SCHEDULED_AUTOMATION_DECISION.md
CoAgent/docs/architecture/technical_enterprise_operating_system_closure.md
```

## Design Continuation

The closed `COAGENT-IMPL-01` through `COAGENT-IMPL-07` checkpoint did not
approve broad runtime expansion. The next approved work is a design protocol
closure, not implementation:

| ID | Task | Owner | Write Scope | Acceptance | Stop / Rollback Condition |
|---|---|---|---|---|---|
| COAGENT-DESIGN-08 | Freeze conversation, goal, context, communication, and worktree-isolation protocol V1 | PMO + DispatchCenter | `CoAgent/docs/architecture/coagent_agent_design_protocol.md`, `CoAgent/protocol/conversation_protocol.md`, `CoAgent/context/context_pack_contract.md`, `CoAgent/dispatch/communication_contract.md`, indexes/status docs | documents define conversation types, worktree binding, creation criteria, goal inheritance, context pack required/forbidden content, packet flow, checkpoint/result contracts, owner/goal change rules, and V1 non-goals; validation passes | stop if protocol requires runtime, transport, automation, app-server, or new permanent department implementation |
| COAGENT-IMPL-08 | Enforce protocol compliance for task/context/result artifacts | DispatchCenter + Verification | `CoAgent/protocol/*.json`, `CoAgent/runtime/mosim_agent_runtime.py`, `CoAgent/context/context_pack.py`, `CoAgent/doctor/*`, `CoAgent/tests/*`, status docs | runtime exports phase/worktree/review fields; context pack includes goal stack, worktree binding, review gate, escalation, and result contract; doctor runs a protocol-compliance smoke test; lifecycle/context tests still pass | stop if protocol enforcement requires transport expansion, app-server mutation, or broad runtime schema rewrite |
| COAGENT-DESIGN-09 | Freeze task surface, file surface, and review surface model V1 | PMO + DispatchCenter | `CoAgent/docs/architecture/coagent_task_surface_model.md`, `CoAgent/docs/architecture/coagent_review_merge_protocol.md`, `CoAgent/learning/README.md`, `CoAgent/docs/architecture/ARCHITECTURE.md`, `CoAgent/docs/architecture/COMPONENT_MAP.md`, `Docs/Workflows/agent_orchestration.md`, status docs | design defines main-thread task, department task, task team, scoped task conversation, one-shot subagent slice, shared workspace, dedicated worktree, review worktree, integration worktree, default mapping by task class, binding rules, review/merge/closeout roles, closeout rules, and anti-patterns | stop if design starts requiring transport/app-server automation or automatic worktree provisioning |
| COAGENT-DESIGN-10 | Freeze multi-conversation task-team architecture V1 | PMO + DispatchCenter | `CoAgent/docs/architecture/coagent_task_team_architecture.md`, `CoAgent/docs/architecture/coagent_agent_design_protocol.md`, `CoAgent/docs/architecture/coagent_task_surface_model.md`, `CoAgent/docs/architecture/coagent_review_merge_protocol.md`, `Docs/Workflows/org_operating_model.md`, indexes/status docs | design distinguishes governance core from visible operating threads, defines task-team charter, shared context vs slice context, scoped conversation contract, conversation/worktree binding, subagent ephemeral worktree rule, allowed packet communication, and states that deleted historical rollout files are diagnostic artifacts rather than routing channels; active department routing requires a user-confirmed visible conversation registered as `active_visible` | stop if design starts implementing transport, automatic conversation creation, automatic worktree provisioning, or unattended multi-agent execution |
| COAGENT-DESIGN-11 | Consolidate vendor/framework multi-agent patterns into CoAgent architecture mapping | PMO + DispatchCenter | `CoAgent/docs/architecture/coagent_vendor_pattern_mapping.md`, `CoAgent/learning/README.md`, `CoAgent/docs/architecture/ARCHITECTURE.md`, `CoAgent/docs/architecture/COMPONENT_MAP.md`, status docs | document maps existing audits and URL seeds into CoAgent objects, evidence levels, adopted/deferred/rejected patterns, missing abstractions, and the next operating-architecture synthesis step; it clearly distinguishes audited sources from seed-only sources | stop if the work becomes a new broad research pass or starts implementing runtime/transport/worktree/conversation automation |
| COAGENT-DESIGN-12 | Convert the problem register into a task-oriented solution baseline and intervention UX | PMO + DispatchCenter | `CoAgent/docs/architecture/coagent_solution_synthesis.md`, `CoAgent/docs/architecture/coagent_user_intervention_ux.md`, `CoAgent/protocol/templates/`, `CoAgent/doctor/check_solution_design.py`, `CoAgent/tests/test_solution_design_docs.py`, status/index docs | design maps issue groups to decisions/unresolved items; defines task topology selector, lifecycle, context quality, packet communication, worktree strategy, human-intervention UX, PX4 and UE stress-test flows; templates exist for task charter, context pack, scoped conversation packet, blocker notification, and review packet; static check passes | stop if the work starts implementing automatic conversation creation, app-server transport, email sending, automatic worktree provisioning, new permanent departments, or broad hook/tool expansion |
| COAGENT-MINILOOP-01 | Prove the full architecture with a file-level manual-review closed loop | PMO + DispatchCenter + Verification | `CoAgent/protocol/templates/`, `CoAgent/docs/architecture/coagent_minimal_closed_loop_protocol.md`, `CoAgent/docs/decisions/coagent_miniloop_01_human_review.md`, `CoAgent/doctor/check_miniloop.py`, `CoAgent/tests/test_miniloop_static.py`, `Results/coagent_miniloop/COAGENT-MINILOOP-01/`, status/index docs | one sample task moves through charter, board, mailbox, context pack, scoped packet, result packet, review packet, context delta, integration plan, trace eval, and closeout summary; static check passes; human-review packet explains what was proven and what remains unimplemented | stop if the work starts creating real Codex conversations, app-server transport, automatic worktrees, email, runtime schema expansion, hooks, plugins, MCP/tool expansion, or unattended execution |
| COAGENT-MINILOOP-02 | Prove one real scoped worker communication loop | PMO + DispatchCenter + Verification | `Results/coagent_miniloop/COAGENT-MINILOOP-02/`, runtime task/result packet state, `CoAgent/docs/decisions/coagent_miniloop_02_human_review.md`, `CoAgent/doctor/check_miniloop_02.py`, `CoAgent/tests/test_miniloop_02_static.py`, status/progress docs | main thread creates a scoped task/context/result contract; one real Codex worker surface receives the task and writes a result packet; main thread imports/reviews the packet and records communication evidence, closeout, and residual risks; this task does not by itself prove UI-visible department communication | stop if no real result packet can be produced within 60 seconds, if Codex CLI/App state is unavailable, or if the proof would require app-server transport, automatic worktrees, email, hooks, plugins, MCP expansion, or unattended automation |
| COAGENT-MINILOOP-03 | Record invalidated historical rollout resume proof and harden active-visible dispatch gate | PMO + DispatchCenter + Verification | `CoAgent/dispatch/department_threads.json`, `CoAgent/dispatch/codex_transport.py`, `CoAgent/transport/codex_exec.py`, `Results/coagent_miniloop/COAGENT-MINILOOP-03/`, `CoAgent/docs/decisions/coagent_miniloop_03_human_review.md`, `CoAgent/doctor/check_miniloop_03.py`, `CoAgent/tests/test_miniloop_03_static.py`, status/progress docs | old rollout resume is explicitly not accepted as visible department communication; only currently visible user-confirmed conversations may be `active_visible`; deleted departments are `inactive_ui_deleted`; transport rejects non-`active_visible` departments before `codex exec resume`; check passes | stop if a deleted historical rollout file is treated as an active department route or if the fix would require app-server transport, automatic conversation creation, email, hooks, plugins, MCP expansion, or unattended automation |
| COAGENT-MINILOOP-04 | Prove a newly created candidate Codex conversation can complete a packet loop without being auto-registered | PMO + DispatchCenter + Verification | `Results/coagent_miniloop/COAGENT-MINILOOP-04/`, `CoAgent/doctor/check_miniloop_04.py`, `CoAgent/tests/test_miniloop_04_static.py`, status/progress docs | a new candidate Codex session receives a scoped packet, writes a result packet, repairs schema defects when found, result router imports it as accepted, and the candidate remains `awaiting_user_visible_confirmation` until the user confirms it is visible in VSCode/Codex App | stop before `active_visible` registration; stop if no result is produced within 60 seconds, if candidate conversation is not visible to the user, or if proof would require app-server transport, automatic worktrees, email, hooks, plugins, MCP expansion, or unattended automation |

## Backlog

| ID | Task | Owner | Write Scope | Acceptance | Stop / Rollback Condition |
|---|---|---|---|---|---|
| COAGENT-IMPL-01 | Freeze task-state, event vocabulary, task-intake classes, and goal hierarchy | PMO + DispatchCenter | `CoAgent/protocol/`, `Docs/Workflows/agent_orchestration.md`, `CoAgent/docs/architecture/ARCHITECTURE.md`, `CoAgent/docs/architecture/task_intake_and_governance.md`, `CoAgent/docs/architecture/enterprise_to_agent_mapping.md`, `CoAgent/docs/architecture/coagent_complexity_control.md` | one canonical state/event/intake/goal table exists; it distinguishes simple replies, durable tasks, artifacts/evidence, `input_required`, `auth_required`, review states, terminal states, task class, appetite, circuit breaker, checkpoint, escalation, acceptance gate, project goal, canonical task goal, conversation objective, and subagent objective; all task/result/context docs reference it; no conflicting vocabulary remains in CoAgent docs | stop if user changes department/communication model; revise design packet first |
| COAGENT-IMPL-02 | Align task packet and result packet schemas | DispatchCenter + Verification | `CoAgent/protocol/`, `CoAgent/dispatch/`, tests/docs that validate packets | packet schemas include task id, owner, task class, appetite, circuit breaker, scope, state, evidence, blocker, review status, next action; schema validation test passes | rollback if schema breaks existing readable packets without migration note |
| COAGENT-IMPL-03 | Strengthen preflight and hooks | Security + DevOps + Verification | `CoAgent/hooks/`, `CoAgent/doctor/`, policy docs | preflight catches outside-project writes, secrets-risk paths, destructive commands, broad Git risk, large-file risk, and missing result-packet evidence | stop if a hook blocks normal read-only work or requires secret/account material |
| COAGENT-IMPL-04 | Run one small real visible-conversation lifecycle | DispatchCenter + DevOps or Verification | runtime events, ledger, result packet under approved result path | task packet is sent to a deleted-UI rollout conversation; visible result packet returns; runtime/ledger records received/reviewed state | stop if result comes from hidden subagent or only from main chat |
| COAGENT-IMPL-05 | Run one dedicated long-task lifecycle | PMO + DispatchCenter + parent department | context pack, task packet, result packet, ledger, recovery note | dedicated task conversation starts from context pack, runs at least one checkpoint, returns result packet, and gets summarized back into project state | stop if context is raw full transcript or result lacks evidence/review status |
| COAGENT-IMPL-06 | Decide transport expansion | PMO + Security + DevOps | design note only unless approved | file/CLI route has two successful lifecycles; app-server transport proof gate is documented before any implementation | do not implement app-server transport if Codex App thread/state remains unstable |
| COAGENT-IMPL-07 | Decide scheduled automation expansion | PMO + Security + Verification | automation docs and guarded scheduler only if approved | dry-run automation creates task tickets without mutating project files; human review state is explicit | stop if automation can write code/docs/Git without review gate |

## Minimum Verification Before Each Task Closes

Every task above must produce:

- task id,
- owner,
- files changed,
- commands run,
- pass/fail output,
- evidence path,
- next action,
- reviewer or human-review state.

No task may close with only a prose claim.

## First Recommended Task Packet

After approval, start with:

```text
task_id: COAGENT-IMPL-01
owner_department: MoSim｜调度中台
objective: Freeze CoAgent task-state, event vocabulary, task-intake classes, and goal hierarchy after design approval.
read_scope:
  - CoAgent/docs/decisions/coagent_design_review_brief.md
  - CoAgent/docs/decisions/coagent_goal_readiness_audit.md
  - CoAgent/docs/decisions/coagent_design_discussion_packet.md
  - CoAgent/docs/architecture/task_intake_and_governance.md
  - CoAgent/docs/architecture/enterprise_to_agent_mapping.md
  - CoAgent/docs/architecture/coagent_complexity_control.md
  - CoAgent/protocol/
  - Docs/Workflows/agent_orchestration.md
write_scope:
  - CoAgent/protocol/
  - CoAgent/docs/architecture/ARCHITECTURE.md
  - Docs/Workflows/agent_orchestration.md
acceptance:
  - canonical state/event/intake/goal table exists
  - vocabulary distinguishes simple message, durable task, artifact/evidence,
    input_required, auth_required, review_required, and terminal states
  - intake vocabulary distinguishes simple message, clear task, complicated
    task, complex task, chaotic incident, disordered task, and long-running task
  - durable task fields include appetite, circuit breaker, checkpoint,
    escalation, and acceptance gate
  - goal hierarchy distinguishes project goal, canonical task goal,
    conversation objective, and subagent objective
  - V1 nesting limit is documented and referenced by protocol docs
  - packet and workflow docs reference one vocabulary
  - no conflicting state vocabulary remains in CoAgent docs
stop_condition:
  - done with evidence
  - blocked by user design change
  - blocked by conflicting existing protocol schema
result_packet_required: yes
```

## Non-Execution Rule

This backlog is executable only after user approval. Before approval, allowed
work is limited to correcting this backlog, discussion packet, review brief,
and readiness audit.
