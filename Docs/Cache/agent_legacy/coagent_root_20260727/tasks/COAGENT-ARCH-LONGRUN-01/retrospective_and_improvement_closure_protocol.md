# COAGENT-ARCH-LONGRUN-01 Retrospective And Improvement Closure Protocol

Date: 2026-05-30
Status: design contract for retrospective and continuous-improvement closure

## Purpose

CoAgent must not only detect drift, blockers, invalid packets, unsafe retries,
and transport failures. It must also close the learning loop so the same
failure is less likely in the next task.

This protocol defines how incidents, repeated mistakes, user corrections, and
review escapes become bounded improvement actions with owners, evidence,
closeout criteria, and promotion or rejection decisions.

This is design-only. It does not implement a scheduler, automatic issue
creation, notification sender, hook, doctor check, skill rewrite, runtime
transport, or automatic documentation edit.

## Control Principle

```text
every repeated failure must end as one of:
  fixed by a named implementation slice
  blocked by a named policy/gate
  promoted into durable knowledge
  rejected with rationale
  explicitly deferred with a trigger
```

If a failure only appears in chat, a review note, or a status paragraph, the
system has not learned from it.

## When A Retrospective Is Mandatory

Create a retrospective record when any of these occur:

| Trigger | Example | Required Response |
|---|---|---|
| repeated same-cause failure | Codex visible-thread metadata drift recurs | incident retrospective |
| invalid durable packet | result/blocker packet cannot be imported | template or validator action |
| unsafe retry risk | tool/license/auth failure is retried without new evidence | safety action |
| user correction repeats | user says the architecture goal was weakened | goal/process action |
| review escape | issue found after an item was accepted | gate/check action |
| context stale event | work resumes from superseded context | context action |
| false progress signal | time, topology, or document volume replaces outcome | goal alignment action |
| broad external research drift | source study produces no problem-linked decision | external adoption action |
| Git/runtime integration surprise | broad diff, lock, large file, or hidden worktree issue appears | DevOps action |
| manual-intervention duplication | user receives duplicate or vague asks | operator-experience action |

Single low-risk mistakes may be logged in the task board. Repeated or
high-impact mistakes require this protocol.

## Retrospective Record

Each record should live under a task-local or project-level improvement store
when implementation is approved. Until then, design examples may reference this
shape.

```yaml
retrospective_id: RETRO-YYYYMMDD-001
task_id: COAGENT-ARCH-LONGRUN-01
trigger_type: repeated_failure
trigger_summary: "DispatchAgent visibility metadata drift recurred after repair."
first_seen_at: "2026-05-30T00:00:00+08:00"
repeated_count: 2
owner: RuntimePlatformAgent
review_owner: VerificationAgent
safety_owner: SafetyComplianceAgent
affected_goal_requirement:
  - cross_conversation_communication
  - reviewable_architecture_documents
evidence_paths:
  - CoAgent/STATUS.md
  - CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/codex_visibility_drift_reliability_design.md
classification:
  incident: true
  process_gap: true
  tool_gap: true
  knowledge_gap: false
root_cause_status: suspected
root_cause_hypothesis:
  - "WSL alternate Codex DB keeps stale cli/user metadata."
improvement_actions:
  - action_id: RETRO-YYYYMMDD-001-A1
    type: implementation_backlog
    target: COAGENT-IMPL-NEXT-22
    owner: RuntimePlatformAgent
    close_condition: "registered drift is repaired or blocked with evidence"
    status: open
rejected_actions:
  - action: "repair arbitrary Codex sessions"
    reason: "outside approved registered-thread scope"
closeout_decision: open
```

## Action Types

Allowed improvement action types:

| Type | Target | Example |
|---|---|---|
| `implementation_backlog` | named `COAGENT-IMPL-*` item | visibility drift gate |
| `doctor_check` | read-only checker | goal alignment checker |
| `protocol_template` | reusable packet/manifest template | blocker packet template |
| `workflow_doc` | repeatable procedure | visible-thread SOP |
| `skill_update` | project-local or reusable skill | MCP operation rule |
| `hook_or_preflight_proposal` | gated automation policy | large-file preflight |
| `context_delta` | current task context update | stale assumption notice |
| `external_adoption_proposal` | source-linked idea | OpenClaw-style user alert |
| `rejected_idea` | rationale archive | raw transcript as context pack |
| `deferred_trigger` | explicit future trigger | real email sender after Candidate E |

Forbidden action types:

- `remember_next_time`;
- `agent_should_be_careful`;
- `discuss_later` without trigger;
- `already_fixed` without evidence;
- `add_more_agents` without a task goal and close condition.

## Closeout States

| State | Meaning |
|---|---|
| `open` | action exists but no accepted closeout evidence |
| `in_progress` | owner is actively working on the action |
| `blocked` | a blocker packet or user decision is required |
| `closed_promoted` | lesson is promoted into a durable doc, skill, hook, checker, or backlog item |
| `closed_rejected` | proposed change was rejected with rationale |
| `closed_deferred` | change is deferred with a trigger and owner |
| `closed_duplicate` | covered by another retrospective or backlog item |

Closed records must cite evidence paths. A retrospective is not closed by
claiming the next agent will remember it.

## Ownership Rules

| Situation | Primary Owner | Review Owner |
|---|---|---|
| goal substitution or fake progress | MainAgent + DispatchAgent | VerificationAgent |
| visible conversation/session/transport issue | RuntimePlatformAgent | SafetyComplianceAgent |
| packet, mailbox, or proof-package issue | DispatchAgent + RuntimePlatformAgent | VerificationAgent |
| context drift or stale knowledge | ContextMemoryAgent | KnowledgeSecretaryAgent |
| product evidence overclaim | VerificationAgent | ProductStrategyAgent |
| unsafe tool/path/credential action | SafetyComplianceAgent | MainAgent |
| Git/large-change incident | DevOpsReleaseAgent | VerificationAgent |
| external-learning drift | ExternalIntelligenceAgent | KnowledgeSecretaryAgent |

If ownership is unclear, DispatchAgent owns routing until the retrospective is
assigned.

## Promotion Gate

A retrospective action can be promoted only when:

1. it names the task and trigger;
2. evidence paths are inside the project or explicitly approved external
   infrastructure paths;
3. the action maps to an existing problem id or creates a new problem id;
4. the target is one of the allowed action types;
5. the owner and review owner are named;
6. the close condition is testable or reviewable;
7. Safety has checked tool, secret, path, destructive-action, and GUI risk when
   relevant;
8. Verification can state how future recurrence will be detected.

Promotion targets include:

- `architecture_problem_matrix.md`;
- `post_design_implementation_backlog.md`;
- `validator_dependency_and_rollout_plan.md`;
- `knowledge_promotion_protocol.md`;
- `problem_driven_external_adoption_queue.md`;
- project-local skills;
- doctor checks;
- workflow docs;
- rejected-idea archive.

## Rejection Gate

Rejected ideas are useful if they prevent future churn.

Reject an action when:

- it solves a local symptom by widening unsafe permissions;
- it requires automatic user notification before Candidate E is proven;
- it increases permanent department count without task evidence;
- it adds context volume instead of better context selection;
- it uses vendor/open-source patterns without a problem-linked proposal;
- it automates a destructive, credential, GUI, or external-path action without
  an approved gate.

Rejected actions must record rationale and the condition under which they could
be revisited.

## Staleness Policy

Open improvement actions become stale when:

- they have no owner;
- they have no close condition;
- their triggering problem has recurred since the action was opened;
- the action references superseded context;
- the action blocks a proof package but is absent from the proof closeout.

Stale records should produce `needs_review`, not silent pass.

## Future Retrospective Checker

Future gated item: `COAGENT-IMPL-NEXT-26`.

The checker should be read-only and validate retrospective records plus their
links to problem matrix, backlog, knowledge promotion, external adoption, and
proof closeout.

Stable finding-code families:

| Code | Meaning |
|---|---|
| `RETRO_RECORD_MISSING` | mandatory trigger has no retrospective record |
| `RETRO_OWNER_MISSING` | owner or review owner is missing |
| `RETRO_EVIDENCE_MISSING` | record lacks evidence paths |
| `RETRO_ACTION_UNTESTABLE` | close condition cannot be reviewed |
| `RETRO_PROMOTION_UNLINKED` | promoted lesson lacks durable target |
| `RETRO_REJECTION_UNJUSTIFIED` | rejected action lacks rationale |
| `RETRO_STALE_OPEN_ACTION` | action is open past trigger or recurrence |
| `RETRO_UNSAFE_ACTION` | action widens permissions or automates gated risk |
| `RETRO_DUPLICATE_UNRESOLVED` | duplicate records exist without canonical owner |
| `RETRO_CLOSEOUT_OVERCLAIM` | record is closed without evidence or validator proof |

The checker must not edit records automatically, create issues, send email,
modify skills, create conversations, dispatch work, or mutate task state.

## Integration With Existing Protocols

| Existing Protocol | Integration |
|---|---|
| `operating_metrics_and_anti_drift_cadence.md` | provides triggers and cadence |
| `operating_metrics_snapshot_design.md` | should count stale/open retrospective actions |
| `goal_authority_and_decomposition_protocol.md` | turns goal-substitution incidents into retro actions |
| `blocker_packet_validator_design.md` | ensures blocker-driven retrospectives are resumable |
| `mailbox_ledger_and_replay_design.md` | records cross-conversation requests and closeout |
| `external_adoption_proposal_contract.md` | routes external ideas from retrospectives |
| `knowledge_promotion_protocol.md` | promotes accepted lessons |
| `validator_dependency_and_rollout_plan.md` | places checker in the gate graph |
| `goal_completion_gate_protocol.md` | prevents closing a goal with unresolved mandatory retro actions |

## Current Application To COAGENT-ARCH-LONGRUN-01

Current known retrospective candidates:

| Candidate | Trigger | Required Action |
|---|---|---|
| goal wording weakened to task setup | user correction | P58 and goal alignment checker already created; close when final audit references it |
| DispatchAgent visibility drift recurred | repeated tool/session drift | P47 and visibility drift gate already created; still needs future checker/proof |
| RuntimePlatformAgent dispatch timed out | transport timeout | transport timeout hardening already created; close after implementation proof |
| nested/custom result packets failed import | invalid durable packet | result packet contract and validator design already created; close after validator fixtures |
| broad external learning risk | research-loop risk | external adoption proposal contract and checker design already created; close after proposal store proof |

These candidates show why retrospective closure must be explicit: several
problems have design responses, but their closeout evidence still lives in
separate artifacts and is easy to miss during a future review.

## Design Decision

CoAgent should treat retrospective closure as a first-class operating object,
not as a prose appendix. Repeated failures must become owned, evidence-backed
improvement actions with clear closeout or rejection. This keeps the system
evolving without depending on the current conversation's memory.
