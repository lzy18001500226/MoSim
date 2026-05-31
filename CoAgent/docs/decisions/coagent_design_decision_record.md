# CoAgent Design Decision Record

Date created: 2026-05-27

Status: approved

This file is the durable decision record for the current CoAgent design
approval gate.

Runtime, transport, automation, task-state schema migration, and tool expansion
remain gated. The approved first implementation task is limited to
`COAGENT-IMPL-01`: freeze the task-state vocabulary, event vocabulary,
task-intake classes, goal hierarchy, and V1 complexity boundary before any
larger runtime expansion.

Implementation may proceed only when the work is inside the accepted
post-approval task sequence and respects the current V1 limits:

- `approved`
- `approved_with_edits`

If the status becomes `revision_required`, update the design packet and review
briefs before any implementation work.

## Source Documents

- `CoAgent/docs/decisions/coagent_design_review_brief.zh.md`
- `CoAgent/docs/decisions/coagent_design_review_brief.md`
- `CoAgent/docs/decisions/coagent_design_discussion_packet.md`
- `CoAgent/docs/architecture/task_intake_and_governance.md`
- `CoAgent/docs/architecture/enterprise_to_agent_mapping.md`
- `CoAgent/docs/architecture/coagent_complexity_control.md`
- `CoAgent/docs/decisions/coagent_goal_readiness_audit.md`
- `CoAgent/docs/decisions/coagent_post_approval_backlog.md`
- `CoAgent/learning/audits/2026-05-27_official_protocol_convergence_round11.md`
- `CoAgent/learning/audits/2026-05-28_technical_enterprise_operating_system_round2_gap_analysis.md`

## Decision State

```yaml
decision_id: COAGENT-DESIGN-20260527
status: approved
decision_date: 2026-05-28
decision_source: user_chat: "再次检查文档是否有问题，如果没问题，就设置好goal，规划好任务，开始执行"
approved_defaults: all
rejected_or_changed_defaults: none
required_doc_updates_before_implementation: none
next_state_if_accepted: ready_for_implementation
next_state_if_rejected: design_revision_required
next_implementation_task_if_accepted: COAGENT-IMPL-01
notes: User approved moving from the design gate into the first minimal protocol implementation phase after checks passed.
```

## Defaults Under Review

1. PMO / DispatchCenter own workflow authority; workers do not self-route.
2. Seven permanent conversations are enough for the next phase.
3. Engineering stays one general execution lane until repeated queue pressure
   proves a split is needed.
4. DevOps remains separate because Git is high-risk and state-heavy.
5. Documentation records decisions but does not own task state.
6. Hooks/policies enforce hard boundaries; skills do not.
7. Long tasks require task id, parent department, scope, stop condition,
   context pack, and result packet.
8. Task-state/event vocabulary distinguishes simple replies, durable tasks,
   artifacts/evidence, `input_required`, `auth_required`, `review_required`,
   `completed`, `failed`, `canceled`, and `rejected`.
9. Task intake classifies requests before execution. Complex work starts with
   discovery; long-running work requires appetite, circuit breaker,
   checkpoint, and escalation conditions.
10. Goal hierarchy is fixed: Project Goal -> Canonical Task Goal ->
    Conversation Objective -> Subagent Objective. DispatchCenter records the
    canonical task goal; workers escalate drift instead of silently changing it.
11. V1 maximum nesting is PMO/main -> DispatchCenter -> department or
    dedicated task conversation -> short-lived subagent. Department-internal
    durable agent swarms are out of scope.
12. Transport stays file/CLI first; Codex App remains UI/review until app-server
   behavior is proven stable.
13. Automation stays dry-run/guarded until hooks and review gates are proven.

## How To Record A User Decision

When the user replies with one of the response formats from
`CoAgent/docs/decisions/coagent_design_review_brief.zh.md`, update `Decision State`.

Accepted decision:

```yaml
status: approved
decision_date: YYYY-MM-DD
decision_source: user_chat
approved_defaults: all
rejected_or_changed_defaults: none
required_doc_updates_before_implementation: none
next_state_if_accepted: ready_for_implementation
next_implementation_task_if_accepted: COAGENT-IMPL-01
```

Accepted with edits:

```yaml
status: approved_with_edits
decision_date: YYYY-MM-DD
decision_source: user_chat
approved_defaults: <list>
rejected_or_changed_defaults: <list>
required_doc_updates_before_implementation: <list>
next_state_if_accepted: ready_for_implementation
next_implementation_task_if_accepted: COAGENT-IMPL-01
```

Revision required:

```yaml
status: revision_required
decision_date: YYYY-MM-DD
decision_source: user_chat
approved_defaults: <list or none>
rejected_or_changed_defaults: <list>
required_doc_updates_before_implementation: <list>
next_state_if_rejected: design_revision_required
next_implementation_task_if_accepted: none
```

## Required Follow-Up After Decision

If approved or approved with edits:

1. Update this file.
2. Update `CoAgent/docs/decisions/coagent_goal_readiness_audit.md`.
3. Update `Docs/Workflows/agent_task_ledger.md`.
4. Set the CoAgent task state to `ready_for_implementation`.
5. Start `COAGENT-IMPL-01` from
   `CoAgent/docs/decisions/coagent_post_approval_backlog.md`.

If revision is required:

1. Update this file.
2. Update the review brief and discussion packet.
3. Update `Docs/Workflows/agent_task_ledger.md`.
4. Keep implementation frozen.
