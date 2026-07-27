# COAGENT-ARCH-LONGRUN-01 End-To-End Task Operating Runbook

Date: 2026-05-30
Status: design-only operating runbook

## Purpose

Define the concrete operating sequence for one serious user task from intake to
closeout.

This runbook is the composition layer over existing protocols. It answers:

```text
When the user gives a long-running task, what does CoAgent do first, second,
third, how does it choose conversations, when does it stop, and how does it
close without relying on chat memory?
```

## Boundary

This is design-only. It does not approve:

- automatic conversation creation;
- live dispatch;
- app-server transport;
- automatic worktree creation;
- Git staging, commit, push, cleanup, or repair;
- MCP/tool execution;
- email or desktop notification;
- unattended scheduling;
- automatic goal mutation or completion.

## Source Protocols

| Layer | Source |
|---|---|
| goal authority | `goal_authority_and_decomposition_protocol.md`, `goal_creation_and_recovery_protocol.md` |
| intake and proof path | `task_intake_to_proof_ladder_decision_table.md`, `proof_ladder_and_validator_order.md` |
| team topology | `dynamic_team_decision_rules.md`, `department_dispatch_plan.md` |
| context | `context_pack.md`, `context_index_and_assembly_design.md`, `context_lifecycle_schema.md` |
| handoff | `handoff_mode_and_workflow_graph_design.md`, `candidate_a_minimal_package_contract.md` |
| communication | `mailbox_ledger_and_replay_design.md`, `result_packet_contract_hardening.md` |
| blockers | `blocker_packet_templates.md`, `safety_human_intervention_protocol.md` |
| evidence and review | `verification_evaluation_protocol.md`, `evidence_label_doctor_design.md` |
| Git/worktree | `worktree_git_integration_protocol.md`, `worktree_merge_recovery_experiment_design.md` |
| learning | `knowledge_promotion_protocol.md`, `external_adoption_proposal_contract.md`, `retrospective_and_improvement_closure_protocol.md` |
| audit | `goal_requirement_audit_map.md`, `goal_completion_gate_protocol.md`, `final_goal_completion_audit.md` |

## Stage 0: Intake Stabilization

MainAgent records the user request as an outcome, not as an activity.

Required fields:

- user objective;
- explicit constraints;
- non-goals stated by the user;
- manual review expectations;
- current project boundary;
- suspected task class;
- first uncertainty that could change routing.

Stop if:

- the task requires credentials, login, license, or destructive action before
  any safe file-level work can proceed;
- the user request is ambiguous enough that a wrong assumption changes project
  direction;
- the only possible next action is outside project scope.

Output:

```text
intake_record
```

## Stage 1: Canonical Task Charter

DispatchAgent creates or updates a durable task charter.

Required fields:

- task id;
- canonical task goal;
- parent user objective;
- definition of done;
- non-goals;
- read scope;
- write scope;
- expected evidence;
- review owner;
- integration owner;
- close owner;
- first checkpoint;
- stop condition;
- blocker policy.

Gate:

```text
The canonical task goal must be at least as strong as the user objective.
```

Reject:

- "create a task";
- "spend 10 hours";
- "open conversations";
- "write documents";
- "run Git";

as the goal unless those are explicitly the user's final outcome.

Output:

```text
task_charter
```

## Stage 2: Task Class And Proof Path

DispatchAgent classifies the task.

| Class | Default First Gate |
|---|---|
| architecture mechanics | Candidate A preflight |
| PX4/log parameter identification | log audit and identifiability matrix |
| UE scene truth/productization | scene-source and tool capability card |
| Git-heavy change | change inventory and Git safety |
| auth/license/manual interruption | blocker packet and resume condition |
| ordinary small task | main-thread targeted check |
| mixed product task | highest-risk gate first |

If multiple classes apply, apply this priority:

```text
auth/license block
  -> Git safety
  -> architecture mechanics
  -> scene truth
  -> data/parameter identification
  -> ordinary small task
```

Output:

```text
proof_path_decision
first_gate
minimum_team
secondary_risks
```

## Stage 3: Context Assembly

ContextMemoryAgent assembles the smallest sufficient context.

Required:

- source path map;
- accepted decisions;
- rejected assumptions;
- stale material excluded or marked;
- budget class;
- result packet contract;
- review and closeout requirements;
- context hash/version;
- acknowledgement requirement for high-risk work.

Rule:

```text
If context is too large, split the task. Do not paste the raw transcript.
```

Output:

```text
context_pack
retrieval_manifest
context_delta_policy
```

## Stage 4: Workflow Graph And Handoff Mode

DispatchAgent turns routing into explicit graph objects.

Every delegated node must have:

- local objective;
- authority transfer;
- input filter;
- context pack path;
- expected result packet path;
- review gate;
- return path;
- cancellation or resume rule;
- forbidden actions.

No graph node may change the canonical task goal.

Output:

```text
workflow_graph
handoff_mode_records
mailbox_required_responses
```

## Stage 5: Topology Selection

Select the smallest topology that can satisfy the first gate.

| Condition | Topology |
|---|---|
| small, low-risk, fits context | MainAgent only |
| bounded read-only/review slice | MainAgent plus short-lived subagents |
| one high-context owner | one scoped conversation |
| independent parallel slices | dynamic task team |
| high-impact decision | review board |
| unsafe session/tool/Git/license state | incident response |

Do not include all departments by default.

Do not spawn or dispatch if:

- context pack missing;
- result path missing;
- review owner missing;
- close condition missing;
- task is in incident state;
- same file write conflicts lack integration plan.

Output:

```text
team_topology_decision
conversation_or_subagent_plan
```

## Stage 6: Execution And Checkpoint Cadence

Workers execute only their local objective.

They may:

- inspect allowed files;
- produce the requested artifact;
- return one result packet;
- emit blocker packets;
- propose context deltas;
- call bounded subagents inside their scope.

They may not:

- weaken the canonical goal;
- expand write scope;
- message the user directly unless they are MainAgent/PMO;
- execute gated tools;
- stage Git;
- create worktrees;
- treat raw chat as evidence.

Checkpoint cadence:

- after each material evidence delta;
- after each blocker;
- before resuming from stale context;
- before any review or merge gate;
- at timeout.

Output:

```text
result_packet
checkpoint_packet
blocker_packet_if_needed
context_delta_if_needed
```

## Stage 7: Communication And Replay

All cross-conversation communication must pass through project-owned records.

Allowed message classes:

- task packet;
- result packet;
- blocker packet;
- review request;
- decision request;
- context delta;
- integration request;
- closeout packet.

Replay rule:

```text
A future conversation must recover the next safe action from files without
reading hidden chat state.
```

Output:

```text
mailbox_ledger
ack_records
replay_summary
```

## Stage 8: Review And Evidence Gate

Verification/Safety/Product/DevOps/PMO review by risk.

Review must state:

- evidence inspected;
- acceptance state;
- rejected claims;
- missing evidence;
- risk;
- next action.

Evidence labels must distinguish:

- design only;
- offline script;
- manual review;
- GUI evidence;
- MCP/tool evidence;
- Git metadata;
- runtime metadata;
- external reference.

Output:

```text
review_packet
evidence_label_summary
```

## Stage 9: Integration Or Hold

DevOpsReleaseAgent integrates only accepted mutable output.

Before Git integration:

- change inventory exists;
- path families are classified;
- write scope matches diff;
- large-file policy exists;
- generated-output policy exists;
- review owner accepted or waived;
- merge owner and close owner are named;
- rollback and cleanup plan exist.

If not ready:

```text
git_disposition = hold | staged_pending_integration | discard | superseded
```

Output:

```text
integration_plan
git_disposition
rollback_plan
cleanup_state
```

## Stage 10: Knowledge Promotion And Retrospective

KnowledgeSecretaryAgent promotes only accepted lessons.

Targets:

- architecture docs;
- workflow docs;
- skills;
- protocol templates;
- doctor checks;
- implementation backlog;
- retrospective action records.

Repeated failures must become retrospective actions, not status text only.

Output:

```text
knowledge_delta
promotion_decision
retrospective_action_if_needed
```

## Stage 11: Closeout

Dispatch/MainAgent can close a task slice only when:

- result packet exists;
- review disposition exists;
- blocker state is closed or explicitly carried forward;
- context delta is accepted/rejected/acknowledged;
- mailbox required responses are closed;
- Git disposition is known for mutable work;
- knowledge promotion decision is recorded;
- remaining work is represented as a task or accepted gated follow-up.

Final closeout must not claim implementation, tool reliability, product
correctness, or automation beyond the evidence.

Output:

```text
closeout_summary
final_audit_update
next_implementation_or_proof_queue
```

## End-To-End Example: PX4 Log Parameter Identification

1. Intake records the user goal: infer usable simulator parameters from PX4
   logs and identify what cannot be inferred.
2. Charter states non-goal: do not claim all parameters are identifiable from
   one log.
3. Classifier selects Candidate B, first gate `log_audit`.
4. Context pack includes log path, PX4 metadata, prior rejected assumption, and
   identifiability template.
5. Topology starts with ProductStrategy, ContextMemory, Verification, and one
   scoped log-audit conversation.
6. Result is an identifiability matrix, not estimator code.
7. Verification rejects unsupported parameter claims.
8. If MWORKS activation is needed later and unavailable, Candidate E blocker
   starts before retries.
9. KnowledgeSecretary promotes the identifiability workflow only after review.

## End-To-End Example: UE Scene Truth

1. Intake records product goal: make scenes usable for planning/navigation
   truth, not only rendering.
2. Charter states non-goal: screenshots do not prove planning truth.
3. Classifier selects Candidate C, first gate `scene_source_classification`.
4. ToolchainMCP fills a capability card; Safety handles Fab/manual blockers.
5. Verification checks truth manifest readiness.
6. Git-heavy assets trigger Candidate D before staging.
7. Algorithm integration starts only after planning truth exists or limitations
   are accepted.

## End-To-End Example: Large Git Rename/Import

1. Intake records the change goal and approval boundary.
2. Classifier selects Candidate D.
3. DevOps creates inventory before staging.
4. Worktree mode is selected by risk.
5. Same-file conflicts, large binaries, external paths, locks, and timeouts are
   blockers or recovery records.
6. MainAgent asks the user only for a specific decision, not a vague Git ask.
7. Closeout records merge/hold/discard/superseded state.

## Anti-Patterns This Runbook Rejects

- treating activity as outcome;
- opening all departments by default;
- continuing product work after a failed first gate;
- allowing workers to rewrite the canonical task goal;
- using raw transcript as context;
- merging work without review and Git disposition;
- retrying login/license/tool failures without blocker packets;
- treating design documents as implementation evidence;
- treating Codex App visibility as durable state;
- letting Git lock/slow status trap the main conversation.

## Future Validator Targets

This runbook should eventually become a read-only checker that validates:

- task charter completeness;
- proof path and first gate;
- context pack source and budget;
- workflow graph/handoff records;
- mailbox replayability;
- result/review/blocker packet completeness;
- evidence labels;
- Git disposition;
- knowledge promotion decision;
- closeout readiness.

Implementation remains gated. The checker must not dispatch conversations,
create worktrees, call tools, stage Git, or mutate goals.
