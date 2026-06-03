# Agent Orchestration Workflow

> Use this when a task is large enough that sub-agents, long Git work, or
> reference-repository audits could continue across user turns.

## 0. Canonical CoAgent Protocol

The current approved protocol entry is `CoAgent/protocol/README.md`. New task
packets, result packets, context packs, and workflow text must use that
vocabulary unless they explicitly document a temporary runtime alias.

Canonical interaction classes:

```text
simple_message
durable_task
long_running_task
checkpoint
result
```

Canonical task-intake classes:

```text
simple_message
clear_task
complicated_task
complex_task
chaotic_incident
disordered_task
long_running_task
```

Canonical states:

```text
planned
ready
working
input_required
auth_required
review_required
blocked
failed
completed
canceled
rejected
superseded
```

Goal hierarchy:

```text
Project Goal -> Canonical Task Goal -> Conversation Objective -> Subagent Objective
```

Task/worktree/review surface selection is defined in
`CoAgent/docs/architecture/coagent_task_surface_model.md`. Use that document before
deciding whether work stays in the main thread, moves to a department
conversation, becomes a task team with scoped task conversations, or needs an
isolated worktree.

Review acceptance, merge ownership, and worktree closeout are further defined
in `CoAgent/docs/architecture/coagent_review_merge_protocol.md`.

Multi-conversation task-team architecture is defined in
`CoAgent/docs/architecture/coagent_task_team_architecture.md`. Use it before splitting
one long task across several conversations or worktrees.

V1 maximum durable nesting:

```text
PMO/main -> DispatchCenter -> department or task team -> scoped task conversation -> short-lived subagent
```

No department-internal durable agent swarms, peer-to-peer worker state,
app-server transport, or unattended write automation are allowed in V1 without
a later approved task.

## 1. Task Graph First

Planning is mandatory before execution. For any non-trivial task, the main
agent must first create or update a task graph, even when the next action looks
obvious. Do not spawn agents, copy large trees, run simulations, or start Git
batches before this planning pass exists in chat or in a recoverable intake /
ledger record.

Before spawning agents, write a short task graph:

```text
critical path:
parallel streams:
write ownership:
blocking risks:
verification:
git/quality owner:
```

Runtime guard: any interactive Codex thread bootstrap, external GUI probe, MCP
probe, or unclear-progress command gets a 60 second timeout by default. On
timeout, terminate only the directly related child process, record what was
created or not created, and return to the task graph. Do not spend multi-minute
turns waiting for a bootstrap command unless the user explicitly approved that
wait.

Minimum planning gate:

```text
objective:
current repo / tool state:
critical path:
parallelizable side work:
owners and write scopes:
verification gates:
Git strategy:
stop / ask conditions:
```

Execution may begin only after the plan identifies the next local critical-path
step and any delegated streams. If the user says "continue", recover the
current plan from `PROGRESS.md`, `Docs/Workflows/agent_task_ledger.md`,
`Results/tmp/task_intake/`, or `Results/agent_runs/*` before acting.

For a learn-and-update audit, the task graph must also declare the round
boundaries:

```text
round 1 source slice:
round 1 doc patch target:
round 2 source slice:
round 2 doc patch target:
round 3 source slice:
round 3 doc patch target:
do-not-adopt guardrails:
```

Keep the main agent on the critical path. Delegated work should be independent
and material, not a copy of the same work the main agent is doing.

For long tasks, convert the graph into a task queue. The queue is the work
source; chat memory is not the work source. A task is ready only when it has:

```text
task_id:
task_class:
project_goal:
canonical_task_goal:
conversation_objective:
objective:
read scope:
write set:
owner role:
accountable_owner:
dependencies:
acceptance check:
definition_of_done:
non_goals:
required_evidence:
reviewer role:
appetite:
circuit_breaker:
checkpoint_plan:
escalation_conditions:
next task on success:
next task on blocker:
```

An owner agent may continue taking the next ready task in its assigned queue
without waiting for a new user message, provided the next task is inside the
same write set and does not require new approval. If the next task changes
write ownership, touches external paths, requires GUI/login/license action, or
needs destructive Git/history operations, the owner must stop and report the
blocker.

Queue-pull owner contract:

```text
queue_source:
claim_rule:
max_items_per_checkpoint:
checkpoint_cadence:
terminal_event_required:
reviewer_role:
stop_on_scope_change:
stop_on_missing_evidence:
stop_on_permission_or_gui_requirement:
```

The owner may process the next ready item only when it remains inside the same
declared read/write scope and acceptance gate. Otherwise it must return a
handoff instead of silently expanding its task.

Sub-agent communication topology:

```text
main agent
  -> child owner
  -> reviewer owner
  -> git owner
  -> optional grandchild workers
```

Sub-agents cannot be assumed to communicate with each other. All cross-agent
coordination, review routing, and follow-up instructions must go through the
main agent or a single explicitly assigned parent owner. If a child owner uses
grandchild workers, the main agent must still receive the parent owner's
checkpoint, decide the next instruction, and distribute any reviewer feedback.
Do not leave one agent waiting for another agent's result unless the dependency
is recorded in the ledger and the main agent owns the handoff.

Nested delegation is allowed only when all of these are true:

```text
max_depth has been intentionally enabled for the session:
the parent owner has a queue and WAL:
child agents are read-only or have disjoint worktrees/write sets:
the parent records child WAL locators:
the main agent remains responsible for final integration:
```

Default to main-agent chaining instead of uncontrolled nested delegation. If a
tool/runtime does not support nested subagents, split the queue from the main
agent instead.

Provider-specific note: Codex subagents are explicitly spawned by the main
agent. Do not assume Claude-style automatic subagent routing. Runtime spawn
arguments such as `reasoning_effort` are not the same as persistent Codex config
keys such as `model_reasoning_effort`; mark unverified config keys as
unsupported until checked against official docs for the installed version.

Codex subagents are not the same thing as durable workers. In this project they
are short-lived capability calls: useful for a bounded audit, focused research,
or a one-batch execution, but not reliable as Git departments, permanent
reviewers, test daemons, secretaries, or cross-turn supervisors. They have
isolated context and must return evidence to the main agent; they cannot be the
source of truth for task state.

Visible department conversations are also not the same thing as internal
Codex subagents. If the user asks to send work to `MoSim｜DevOps 发布部`,
`MoSim｜验证测试部`, or another visible department thread, do not use an
internal `spawn_agent` call and claim the department received it. Dispatch to
the real visible thread with `codex exec resume <thread_id>` and capture the
last response with `--output-last-message`. Internal subagents may still be used
for one bounded private analysis slice, but they are not acceptable evidence of
department communication.

Known visible department dispatch command pattern:

```bash
codex exec resume <department_thread_id> \
  -m gpt-5.5 \
  -c model_reasoning_effort='"high"' \
  --dangerously-bypass-approvals-and-sandbox \
  --output-last-message /tmp/<task_id>_result.txt \
  - < /tmp/<task_id>_packet.txt
```

Use a 60 second outer timeout for probes and short packets. For long Git or
large-tree tasks, split the task into path-scoped batches and require the
department owner to return a checkpoint/result packet instead of waiting on a
full-tree scan. Communication is proven only when the visible thread returns a
department result. The first accepted DevOps communication probe returned:
`DEVOPS_COMM_OK｜received_from_main｜task_id=comm-probe-20260526-01`.

Codex App / VSCode visibility and CLI communication use different metadata
contracts. Keep WSL-side thread metadata CLI-compatible for communication:
`source=cli`, `thread_source=user`, and lowercase WSL `cwd`. Keep Windows App
metadata UI-compatible for display: `source=vscode`, `thread_source=vscode`,
and canonical `/mnt/c/Users/HP/Desktop/MoSim` `cwd`. If both sides are forced
to `vscode`, `codex exec resume` may fail with `unknown thread source: vscode`.
If both sides are forced to `cli`, the department conversation may disappear
from the App/VSCode task list. After each visible-thread dispatch, copy or
materialize the updated rollout to the Windows session store and update the
Windows index/state preview; do not mutate the WSL source away from `cli/user`.
Accepted regression probe:
`DEVOPS_VISIBLE_ACK｜task_id=DEVOPS-VISIBLE-PROBE-20260526-03`.

Durable department behavior must be implemented by MoSim-owned infrastructure:
a persistent task queue, append-only event stream, path/security hooks, explicit
claim/heartbeat/terminal events, and human-readable recovery surfaces in this
workflow, `PROGRESS.md`, and `Docs/Workflows/agent_task_ledger.md`. Subagents may
help inspect or execute one queue item, but the queue and state machine are not
owned by the subagent runtime.

The first project-local implementation is
`CoAgent/runtime/mosim_agent_runtime.py`. It is deliberately a local state tool:
SQLite task queue plus JSONL event stream. It does not call model APIs, does not
spawn Codex, and does not open GUI tools. Use it to make long work recoverable
before assigning one-shot Codex subagents or manual workers.

Project-owned architecture and migration status live under `CoAgent/`.
Use `CoAgent/docs/architecture/ARCHITECTURE.md` for the layered design, and
`CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md` before scanning large external repos under
`References/`.

Minimum runtime commands:

```bash
python CoAgent/runtime/mosim_agent_runtime.py create \
  --objective "Review current UE MCP design" \
  --role ArchitectureReviewer \
  --read-scope Docs/Skills/Unreal \
  --write-scope Results/agent_runs \
  --acceptance "structured review event recorded" \
  --stop-condition "done, blocked, or failed with evidence"

python CoAgent/runtime/mosim_agent_runtime.py claim --owner ArchitectureReviewer
python CoAgent/runtime/mosim_agent_runtime.py checkpoint --task-id <id> --actor ArchitectureReviewer --summary "read first slice"
python CoAgent/runtime/mosim_agent_runtime.py complete --task-id <id> --actor ArchitectureReviewer --summary "review complete"
```

Runtime state aliases exist during migration. Treat `queued` as `ready`,
`claimed`/`running` as `working`, `done` as `completed`,
`done_with_concerns` as `review_required`, and `cancelled` as `canceled`.
New documentation should use the canonical state names.

User-facing task UI:

Use the VSCode/Codex App task/conversation list as the front end. The user opens
separate Codex conversations manually when a stream needs sustained context,
manual inspection, or long-running ownership. The main agent provides a standard
task packet for each conversation, or dispatches it with
`codex exec resume <thread_id>` when the target visible thread id is known, and
records the task in the MoSim runtime/ledger. Do not build a separate web
dashboard unless the VSCode/Codex task UI becomes insufficient.

Conversation classes:

| Class | Owner | Purpose | Examples |
|---|---|---|---|
| Primary conversation | MainAgent | User dialogue, goal, integration, final decisions | current WSL-backed project thread |
| Department conversation | Department owner | Recurring work inside one broad responsibility | `MoSim｜DevOps 发布部`, `MoSim｜验证测试部` |
| Task team | Parent department + DispatchCenter | One long-running task containing multiple scoped visible conversations with shared canonical goal | `Sunray150 参数识别`, `UE Fab 场景导入` |
| Scoped task conversation | Task team owner | One bounded slice inside a long-running task team | log audit, estimator implementation, verification slice |
| One-shot subagent | MainAgent or parent owner | Bounded research/review/execution slice returning one result | one repo audit slice, one doc review |

Use a task team instead of a one-shot subagent when the task:

```text
will take multiple turns or manual review cycles
needs to preserve technical context across many messages
has iterative user feedback
requires independent progress visibility in Codex App
would fail if treated as a single disposable subagent call
```

The PX4-log-based Sunray150 parameter identification task is the canonical
example: it should be a task team under the Project Department, not a one-shot
subagent, because it needs literature/code audit, log-field requirements,
user-provided data, estimator design, MWORKS parameter mapping, and
verification across multiple visible conversations.

Each scoped task conversation inside a task team must start from a compact
context pack rather than raw accumulated chat. Use
`CoAgent/docs/research/LEARNING_STRATEGY.md` for the current context-pack fields. At minimum,
include:

```text
task_id:
parent_goal:
owner_department:
objective:
read_scope:
write_scope:
current_state:
relevant_decisions:
known_blockers:
required_tools:
acceptance:
stop_condition:
result_packet_path:
knowledge_search_queries:
```

After the task returns a result packet, summarize useful context into runtime
events, run summaries, knowledge sources, workflows, or progress notes, then
release the task-specific conversation context. Do not let an old transcript
become the only memory of why a technical decision was made.

Current CoAgent implementation is frozen at the design-review boundary. Before
adding new runtime, transport, automation, department, or packet-schema work,
confirm the checklist in
`CoAgent/docs/decisions/coagent_design_discussion_packet.md`. Use
`CoAgent/docs/research/THREE_ROUND_STUDY_AND_DISCUSSION.md` as the supporting
evidence packet.

Generate the current project-owned format with:

```bash
python CoAgent/context/context_pack.py --task-id <id>
```

For a recoverable handoff, write it under `Results/context_packs/`:

```bash
python CoAgent/context/context_pack.py --task-id <id> --output Results/context_packs/<id>.md
```

Conversation communication protocol:

```text
MainAgent responsibilities:
  1. Keep the top-level goal accurate.
  2. Decide whether work stays local, goes to a department conversation, becomes
     a dedicated task conversation, or is a one-shot subagent call.
  3. Ensure the DispatchCenter creates or updates the durable task record first.
  4. Produce one copy-paste task packet for the user-opened conversation.
  5. Continue the main critical path without waiting unless the result blocks it.
  6. Parse returned result packets, update runtime/ledger, and integrate or reject.

DispatchCenter responsibilities:
  1. Maintain task tickets and department status board.
  2. Track owner conversation, task conversation, blocker, next action, and evidence.
  3. Detect stale waiting tasks and request a checkpoint.
  4. Route result packets to test, security, docs, Git, or main integration.

DocumentationSecretary responsibilities:
  1. Record directives, decisions, corrections, and manual-review outcomes.
  2. Patch durable docs after stable decisions.
  3. Run or request docs-quality review.
  4. Avoid becoming the global dispatcher or hidden implementation worker.

User responsibilities:
  1. Open the Codex conversation manually when asked.
  2. Paste the task packet exactly.
  3. Keep the conversation visible for manual progress inspection when desired.
  4. Paste the returned result packet back to MainAgent when integration is needed.
```

Task packet template:

```text
[MoSim Task Packet]
task_id:
role:
objective:
read_scope:
write_scope:
allowed_actions:
forbidden_actions:
acceptance:
stop_condition:
required_checks:
return_format:
  summary:
  files_changed:
  evidence:
  blockers:
  next_recommended_action:
```

Current local runtime export command:

```bash
python CoAgent/runtime/mosim_agent_runtime.py task-packet --task-id <id>
```

Or build a department-ready dispatch envelope with:

```bash
python CoAgent/dispatch/dispatch_helper.py dispatch-envelope \
  --department ProjectOwner \
  --task-id <id>
```

For a copy-paste department assignment message, use:

```bash
python CoAgent/dispatch/dispatch_helper.py department-task-text \
  --department ProjectOwner \
  --task-id <id>
```

Result packet requirements:

```text
[MoSim Result Packet]
task_id:
status: completed | review_required | input_required | auth_required | blocked | failed | canceled | rejected | superseded
canonical_status:
task_class:
canonical_task_goal:
conversation_objective:
summary:
files_changed:
commands_run:
evidence:
risks:
blockers:
review_status:
acceptance_state:
continue_or_stop:
next_recommended_action:
```

Older runtime packets may still say `done`, `done_with_concerns`, or
`cancelled`; importers should map those aliases to `completed`,
`review_required`, and `canceled`.

Current local runtime export command:

```bash
python CoAgent/runtime/mosim_agent_runtime.py result-packet --task-id <id>
```

To import a returned packet into runtime state:

```bash
python CoAgent/dispatch/dispatch_helper.py import-result \
  --packet /abs/path/result_packet.json
```

For a human review handoff, use:

```bash
python CoAgent/dispatch/dispatch_helper.py review-brief --task-id <id>
```

Do not rely on a side conversation's memory as project state. A conversation is
only an execution/review surface; durable state remains in the runtime database,
JSONL events, `Docs/Workflows/agent_task_ledger.md`, and `PROGRESS.md`.

Department status board entry:

```text
[MoSim Status Board Entry]
task_id:
parent_goal:
department:
owner_conversation:
task_conversation:
state:
read_scope:
write_scope:
dependencies:
next_action:
human_needed:
last_checkpoint:
evidence:
review_status:
git_status:
```

Current local runtime snapshot command:

```bash
python CoAgent/runtime/mosim_agent_runtime.py status-board
```

Before wide-scope CoAgent runtime or dispatch work, run:

```bash
python CoAgent/hooks/preflight.py
```

Daily/recurring Codex App automations may be used only after their behavior is
verified for the current installed App version. Until then, model them as
normal task tickets:

```text
Daily workflow/skills improvement:
  owner: DispatchCenter + KnowledgeDepartment
  action: inspect recent incidents, official docs, local skills, and update workflow docs

Daily external repository update:
  owner: DevOpsDepartment + KnowledgeDepartment
  action: pull/update tracked reference repos within ignored/reference scope,
  summarize changes, and flag useful upstream fixes

Daily documentation drift check:
  owner: DocumentationSecretary + DocsQualityTest
  action: compare PROGRESS/ledger/workflows against current task state

Daily safety scan:
  owner: SecurityDepartment
  action: large files, secrets, external paths, destructive-operation residues
```

Do not assume App automations replace durable MoSim status records. They can
trigger or remind; they are not the project state source.

Provider behavior matrix:

| Capability | Codex policy here | Claude Code note |
|---|---|---|
| Subagent trigger | Explicitly spawned by main agent/user-authorized task graph; one bounded result expected | May auto-delegate from descriptions |
| Durable workers | Use MoSim task queue/runtime, not Codex subagent chat state | Claude subagents still need external state for reliability |
| Nested delegation | Avoid for durable work; depth 2 only for bounded read-only or disjoint-scope batches with WAL | Do not assume named subagents can spawn subagents |
| Worktrees | Prefer one Git owner; use isolated worktrees only for disjoint branches/scopes | Claude has separate worktree-isolation concepts |
| Custom schemas | Treat local `.toml` examples as unverified until official Codex docs confirm | Claude frontmatter is not Codex syntax |
| Background tools | Record pending/denied tool state in WAL | Claude background behavior may deny prompt-required tools |

For long-running execution streams such as Git batching, Unreal project smoke
tests, simulator bring-up, large reference audits, and repeated documentation
learning passes, create a durable queue item first. A Codex subagent may process
one bounded item, but it must not be left as the only holder of continuation
state. If the task needs to continue after a checkpoint, the next item must be
recorded in the MoSim queue/ledger, then explicitly dispatched again.

The main agent must not treat a missing or closed subagent as task completion.
Completion is defined only by the durable queue state and required evidence. If
a subagent returns a useful checkpoint, consume it, update the queue/ledger, and
either dispatch the next bounded task or mark the durable task blocked/done.

Management analogy for long work:

```text
main agent:
  director / general manager; owns objective, priorities, queue, approvals,
  integration, verification, and final report
TaskSecretary:
  role definition for MoSim runtime, not a Codex subagent job by default;
  records instructions, checkpoints, blockers, task state, review requirements,
  and supervision signals
MoSim runtime worker:
  durable worker process; claims queue items, emits heartbeat/events, returns
  terminal evidence, and can survive chat/session loss
Codex subagent:
  short-lived specialist; executes one explicit batch and returns evidence
reviewer:
  durable queue role when ongoing; Codex subagent only for one bounded review
```

The detailed department model lives in
`Docs/Workflows/org_operating_model.md`. Use it when a task needs company-style
division of labor: dispatch center, documentation secretary, project owners,
testing, security, DevOps, architecture, knowledge management, and incident
review.

The director should not grind through every worker task when the queue is
large, but Codex subagents are not the replacement for a real worker pool. The
director should update durable state, enqueue bounded items, review returned
evidence, and use Codex subagents only as disposable specialists until a
MoSim-owned runtime worker exists.

For visible department conversations, the director must not operate the
department as a synchronous sub-process by sending repeated step-by-step
``continue`` ticks. Send one complete department charter instead: objective,
context pack, allowed scope, forbidden actions, evidence format, result packet
path, checkpoint cadence, and stop conditions. The department conversation owns
its own goal, plan, execution, checkpoints, and result packet. The director only
does visible dispatch, periodic status collection, integration review, and
human escalation. If a visible department times out on a command, send at most
one corrective charter that changes operating policy, then let the department
continue autonomously or return a blocker.

Current Codex CLI limitation: a foreground `timeout 60s codex exec resume ...`
is only a bounded visible message/probe. If the command is killed by the outer
timeout, the department is not continuing autonomously in the background. For
real long-running department work, pair the visible charter with the
project-owned background dispatch runner (`CoAgent/dispatch/codex_transport.py
start-dispatch`) and recover through `poll-dispatch` or `finalize-timeout`.
Until app-server transport is explicitly approved, treat this as two surfaces:
visible thread for user/auditor visibility, and background runner/result packet
for execution evidence.

The TaskSecretary is not an implementation worker. It should:

```text
record:
  user directives, changed priorities, owner assignments, checkpoints,
  blockers, and manual-review decisions
supervise:
  whether owners are still progressing, waiting, blocked, or missing evidence
review:
  whether returned work matches scope, stop condition, and required evidence
fan out review:
  when several independent reviews are required, spawn the same number of
  read-only secretary/reviewer grandchildren with disjoint review scopes
```

Secretary intake is mandatory for volatile instructions. Every new user
directive, correction, manual-review result, sub-agent return, blocker, or work
checkpoint must be captured in `Results/tmp/task_intake/`, promoted to
`Docs/Workflows/agent_task_ledger.md` or `PROGRESS.md` when stable, and only then
treated as recoverable state. Chat memory alone is not state.

Testing is a separate stream. For sustained test coverage, use the MoSim task
queue/runtime and record results in durable logs. A Codex `TestOwner` subagent is
acceptable only for one bounded review or test-analysis slice; it must return
evidence and cannot remain the test department of record.

Skills are work instructions, not task owners. Agents use skills to execute a
role; the orchestration ledger decides who owns the task, what evidence is
required, and when the task is complete.

## 2. Ledger Requirement

Record every long-running delegated task in `Docs/Workflows/agent_task_ledger.md`.
For runs lasting more than one turn, also write JSONL events under:

```text
Results/agent_runs/<run_id>/events.jsonl
```

If a sub-agent disappears, recover from the ledger. Do not infer state from old
chat memory or nicknames.

## 2.1 JSONL Event Schema

Use an append-only event log for runs that span multiple user turns or involve
multiple agents. Required fields:

```json
{
  "event_id": "GIT-20260521-OKWINDS-0001",
  "ts": "2026-05-21T11:20:00+08:00",
  "task_id": "GIT-20260521-OKWINDS",
  "agent_role": "GitIntegrator",
  "event_type": "agent_spawned",
  "summary": "Started safe integration of Docs/Skills/okwinds and branch cleanup",
  "paths_read": ["Docs/Workflows/agent_task_ledger.md"],
  "paths_written": [],
  "artifact_refs": [],
  "wal_locator": "",
  "parent_run_id": "",
  "resume_from_event_id": "",
  "resume_from_line_index": "",
  "terminal_event": "",
  "approval_state": "none",
  "tool_state": "none",
  "error_kind": "",
  "risk": "",
  "next_action": "scan large files and commit safe batches"
}
```

`event_id` order must be stable and monotonic within each `task_id`. When
resuming from a WAL, treat `resume_from_line_index` as 0-based and preserve the
old event ids in `artifact_refs` or `summary` instead of renumbering history.

Allowed `event_type` values:

```text
task_started
plan_updated
round_started
round_learned
round_doc_patched
agent_spawned
skill_injected
checkpoint
handoff_received
evidence_saved
human_request
human_response
approval_requested
approval_decided
tool_call_started
tool_call_finished
blocked
resumed
forked
completed
superseded
run_terminal
```

Use `round_started`, `round_learned`, and `round_doc_patched` for explicit
three-round learn-and-update work. A round is complete only after the doc patch
for that round exists or the event records a blocker.

The event log is not a replacement for Git history or simulation evidence. It
is the recovery trail for orchestration state.

Use these shared state values:

```text
approval_state = none | requested | approved | denied | pending
tool_state = none | requested | finished | pending | failed
error_kind = timeout | validation | permission | approval_denied |
             sandbox_denied | mcp_unavailable | gui_blocked |
             license_or_login | result_binding_failed | git_push_rejected |
             pack_too_large | unknown
```

Artifact refs should use:

```json
{"path":"Results/.../metrics.json","source":"MWORKS_MCP","sha256":"","bytes":0,"role":"metrics"}
```

Do not paste secret-bearing payloads or full GUI event streams into WAL.
Record paths, hashes, sizes, and claim roles instead.

For delegated runs, record child WAL locators as artifacts:

```json
{"path":"Results/agent_runs/<child_run>/events.jsonl","source":"agent_wal","sha256":"","bytes":0,"role":"child_wal"}
```

Do not treat UI/SSE projection events as the source of truth. Prefer terminal
tool results, result files, metrics, artifact manifests, child WAL locators,
and NodeReport-style terminal summaries.

## 2.2 Resume Rule

Before resuming a long-running task, inspect the latest ledger row and, when
available, the latest `events.jsonl`. Summarize:

```text
latest_terminal_event:
pending_approvals:
pending_tool_calls:
latest_artifact_refs:
error_kind:
next_safe_action:
```

Do not infer completion from missing chat context or a missing sub-agent id.

## 2.3 Task Secretary Intake

Use a `TaskSecretary` record when the user is steering a long session, when
many sub-agents are active, or when instructions arrive as corrections across
multiple turns. The secretary role is a planner/recorder, not a hidden worker.

The secretary's job is to turn user messages and agent returns into a durable
task queue:

```text
message_id/time:
raw_user_directive:
interpreted_task:
goal:
owner_role:
read_scope:
write_scope:
acceptance:
state:
next_action:
needs_user_review:
```

Write current-turn intake drafts under:

```text
Results/tmp/task_intake/YYYY-MM-DD.md
```

Promote only stable items into `Docs/Workflows/agent_task_ledger.md` or
`PROGRESS.md`. Do not paste entire session dumps into durable docs.

Trigger a secretary update when any of these happen:

```text
new user instruction or correction
user says a previous interpretation was wrong
sub-agent returns DONE / DONE_WITH_CONCERNS / BLOCKED
manual review result changes task status
Git/MCP/simulator task reaches a blocker
the current goal is too broad or stale
```

The main agent remains responsible for decisions. The secretary record only
preserves the task state and makes the next safe action explicit.

## 2.4 Goal Assignment

Do not use one broad goal to hide unrelated streams. Assign goals at the level
where completion can be verified.

Recommended goal split:

| Layer | Goal Scope | Completion Evidence |
|---|---|---|
| Main agent | Orchestrate current project objective, integrate results, and keep the ledger accurate | Current plan, intake record, ledger updates, final verification |
| Git owner | Classify every path group as pushed, ignored, needs-user-decision, or blocked | Pushed branch refs, commit hashes, large-file scan, residual table |
| TaskSecretary | Convert user instructions and agent returns into recoverable tasks | `Results/tmp/task_intake/*` plus promoted ledger/PROGRESS rows |
| Research owner | Complete bounded source audit or parameter-identification research | Source list, evidence/inference/unknowns, patch plan or report |
| Reviewer | Review Docs/code/model changes without implementing | Findings with file references and residual risk |

Every sub-agent prompt for this project should include a concrete goal and
terminal condition. If runtime support allows it, request `model=gpt-5.5` and
`reasoning_effort=high` explicitly at spawn time.

If a goal record becomes malformed, stale, over-narrow, or impossible to update
through the available goal tools, do not let it block execution. Reset/delete
the bad goal record and recreate only the durable total objective. Single
implementation steps belong in this ledger or the active task queue, not in the
top-level goal.

Codex thread goals are display and recovery metadata for one visible
conversation. They are not the CoAgent task-control plane. For project tasks,
record cancellation through `CoAgent/runtime/mosim_agent_runtime.py cancel` or
through a validated result packet with status `canceled`; keep the tombstone and
audit history. Ask the user to clear a Codex goal only when the visible
conversation itself is blocked by stale UI goal state. Do not assume another
conversation can clear its own Codex goal automatically; that requires a
separate proven app-server or CLI primitive and visible-front-end verification.

## 2.5 Git Owner Stop Condition

A Git owner is not done after pushing one small branch unless that was the
entire assigned objective. For broad repository convergence, the terminal table
must classify each path group:

```text
pushed
ignored/excluded
needs-user-decision
blocked
```

Minimum path groups:

```text
Docs/Workflows/AGENTS/PROGRESS
Docs/Skills/Mworks
Docs/Skills/Agent and Docs/Skills/okwinds
Scripts/tests
Models/scenarios
References/AirSim
References/Lab
References/PX4
References/Sunray/CUAV
References/MWORKS/RflySim
UE5/UE source/config
Results/tmp and generated outputs
```

If a full `git status` is too slow, the Git owner must use path-limited
commands and clean-branch strategies. Do not push polluted aggregate branches.

For stale-ledger recovery, use this order:

```text
1. Read the ledger row for objective, write scope, and last checkpoint.
2. Read the latest events.jsonl if it exists.
3. Trust only terminal task/run events for completion and WAL locators.
4. Treat pending approvals, pending tool calls, missing terminal events, or
   expired UI/SSE after_id cursors as diagnostic state, not as success.
5. If the user requested three learn-and-update rounds, verify all three
   round_doc_patched checkpoints before continuing from "done".
```

If the ledger says `done` but the event log lacks a terminal event or round
patch checkpoints, mark the row stale and resume from the last confirmed safe
checkpoint.

## 3. Standard Sub-Agent Contract

Each delegated task must state:

```text
role:
objective:
depends_on:
read scope:
write set:
side_effect_policy:
stop condition:
expected output:
expected evidence:
forbidden actions:
```

For queue-owning agents, also state:

```text
queue source:
claim rule:
max tasks per checkpoint:
checkpoint cadence:
review trigger:
handoff condition:
```

Use stable role names such as `GitIntegrator`, `SceneResearcher`,
`SimulationReviewer`, `ParameterIdentificationResearcher`, and
`DocsWorkflowAuditor`. Do not rely on arbitrary nicknames for recovery.

For documentation-discovery or external skill/workflow audit agents, include:

```text
round:
source slice:
patch target:
do-not-adopt candidates:
contradictions to current docs:
minimum evidence paths:
```

For write-capable agents, the write set must be disjoint. Use only one
Git/quality agent at a time.

## 3.1 Reviewer Agents

After a write-capable agent reports completion, run review through either the
main agent or a dedicated read-only reviewer. The reviewer must use at least the
relevant subset of these six angles:

```text
requirements fit:
interface and integration:
runtime/performance:
evidence and reproducibility:
Git/large-file/secrets:
documentation and recovery:
```

Reviewer agents are read-only by default. They do not fix issues unless the
main agent assigns a separate write set.

For documentation changes, run a dedicated `DocsQualityReviewer` before
declaring the task complete. It must check:

```text
policy vs workflow separation:
no accidental pasted XML/HTML/questionnaire/config fragments:
no unsupported tool/config claims without verification note:
no duplicated or contradictory rules:
AGENTS.md remains concise and policy-level:
workflow files contain detailed mechanics:
PROGRESS.md contains live state only:
links in Docs/Index/workflow_index.md still resolve:
```

If the reviewer finds contamination or misplaced detail, fix the docs and run
the review again.

Use two reviewer lanes when the task changed rules, workflows, or generated
artifacts:

```text
spec/compliance reviewer:
  checks requested scope, forbidden paths, source coverage, and acceptance gates
quality/risk reviewer:
  checks correctness, regression risk, security/secrets, and recovery evidence
```

For small documentation-only patches, the same read-only reviewer may cover
both lanes, but the final note must state which lane checks were performed. Do
not treat a worker self-review as either reviewer lane.

Before accepting a review finding, evaluate it against local project facts:

```text
review finding:
confirmed file/line or source path:
does it match current AGENTS/workflow constraints:
would the fix add unsupported scope or YAGNI behavior:
accept / reject / needs user decision:
evidence:
```

External reviewer feedback is input to evaluate, not an order to apply. Push
back or record `do_not_adopt` when the suggested fix imports an external runtime,
changes provider semantics, writes outside the approved path, or lacks evidence.

## 4. Evidence Format

Returned results must separate:

```text
confirmed evidence:
inference:
unknowns:
risks:
recommended next validation:
changed paths:
```

Do not merge a high-impact conclusion if the sub-agent did not provide evidence.

Use this NodeReport-style terminal summary for long tasks:

```text
task_id:
role:
status:
confirmed evidence:
artifacts:
commands/checks:
paths changed:
unknowns:
risks:
next reviewer action:
resume point:
```

GUI windows, plots, animations, and UI streams are review surfaces. They are
not the audit source. The stable audit source is the tool result, result path,
metrics, logs, native-result locator, artifact manifest, and Git commit.

For agent/workflow audits, use a capability coverage map before declaring a
process complete:

```text
capability or rule:
source evidence path:
project doc target:
workflow/checklist entry:
validation gate or manual review:
known gap:
```

Documentation-only changes may use manual review and `git diff --check` as the
validation gate, but they must still identify which future check would detect
drift.

Completion claims require fresh verification evidence from the current turn or
current resumed run. Before saying a task is done, record:

```text
claim:
verification command or manual review gate:
fresh output / exit status:
files or artifacts checked:
known gaps:
```

For documentation-only work, acceptable fresh gates are scoped source coverage
review, target-file diff review, link/path checks, and `git diff --check`.
For code, model, or simulation work, documentation review is not enough; use the
project's targeted test, build, model check, or simulation evidence route.

## 4.1 Round 3 Validation Gates

For the third learn-and-update round, add a source-to-doc coverage matrix before
declaring completion:

```text
source slice:
finding:
adopted rule:
target file:
validation gate:
future drift detector:
do_not_adopt:
```

The matrix should cover at least:

```text
multi-agent scheduling / queue ownership:
reviewer agent lanes:
WAL and stale-state recovery:
goal/task completion evidence:
documentation pollution prevention:
unsupported external runtime patterns:
```

If a source was read but produced no project change, include it with
`adopted rule: none` and explain the rejected pattern. This prevents silent
"read but unused" claims.

## 5. Long Git Work

Large `git add`, large-file scans, and reference import cleanup should be
delegated to `GitIntegrator` when an agent slot is available. The main agent
continues architecture, implementation, or review while Git runs.

Git delegation is not limited to huge imports. If Git is slow, has LFS/hook
side effects, stale `index.lock`, old polluted branches, broad untracked trees,
or any repeated blocker, the main agent must treat Git as a separate DevOps
stream. In that state, even a small Markdown commit should be assigned to
`GitIntegrator`; the main agent's role is to give scope, review the result, and
continue the engineering critical path.

Normal small commits may be done by the main agent only when all of these are
true:

```text
git status is fast enough to inspect safely
no stale .git/index.lock exists
no LFS hook is known to scan the whole repository
the staged scope is explicit and small
the commit/push is expected to finish quickly
no other Git owner is active on the same worktree or branch
```

If any condition is false, spawn or reuse `GitIntegrator` and record the Git
task in the ledger.

`GitIntegrator` may:

- inspect status and diffs;
- update `.gitignore` for generated or over-limit files;
- stage, commit, and push approved project files;
- report exact blockers.

`GitIntegrator` must not:

- force push;
- rewrite history;
- delete user source material;
- commit files over GitHub's hard size limit;
- submit nested repositories as gitlinks unless explicitly requested.

For large imported repositories, prefer isolated worktrees or throwaway clones
when parallelizing Git analysis:

```text
git worktree add ../Quadrotor-git-<scope> <base-branch>
```

Use this only inside the project parent path approved by the user or a
project-local worktree directory. Each worktree owner must have a disjoint
branch and scope. Never run two write-capable Git agents against the same
working tree or branch. The main agent or single `GitIntegrator` owns final
integration and push ordering.

When splitting Git work, use content-family branches:

```text
Docs/workflows
Docs/Skills/*
References/AirSim/*
References/Lab/*
References/RflySim/*
UE5/*
```

Each branch must pass large-file and gitlink checks before push. If a branch
push fails because the pack is too large, split by narrower repository group
instead of retrying the same pack repeatedly.

Large batch default strategy:

```text
1. Put the whole incoming tree behind `.gitignore`, or keep it outside the
   repository until the queue is ready.
2. Build an inventory grouped by source repo, content type, and expected value.
3. Open one narrow batch by adding a precise negative `.gitignore` rule or by
   copying only that slice into the tracked target.
4. Run the batch gates: >100 MB scan, gitlink scan, LFS pointer scan, secret
   scan, generated-artifact scan, and path-count sanity check.
5. Stage only the reviewed slice with path-limited `git add`.
6. Commit and push that slice before opening the next slice.
7. Record skipped paths and the next batch in the ledger.
```

Do not treat IDE visibility settings as a substitute for this strategy.
Specifically, do not solve a huge untracked surface by setting
`git.showUntrackedChanges=false`, `git.showIgnoredFiles=false`,
`files.exclude`, `files.watcherExclude`, or broad `search.exclude` entries for
the incoming trees. Those settings hide evidence from the operator and can make
the file explorer/source-control surface misleading. Use `.gitignore` or a
project-local exclude file for temporary Git isolation, then drain the ignore
rules with reviewed small batches.

This strategy is mandatory when any of these are true:

```text
incoming file count is roughly 1000+:
source tree contains external simulator/game/asset repositories:
GitHub rejected a push for file size or pack size:
git status/add/commit becomes slow because untracked trees are huge:
the user explicitly says to use the previous divide-and-conquer method:
```

Do not solve a large import by repeatedly retrying one aggregate branch. The
correct recovery is to ignore the aggregate, reopen one reviewed slice, and
push slice-by-slice. If the batch is important but too large for Git, keep it
ignored under `References/` and commit only a manifest plus usage notes.

For ten-thousand to hundred-thousand file surfaces, treat chat output, shell
argument length, hook scans, and GitHub limits as first-class constraints:

```text
1. Do not print full path lists to chat. Write reviewed path lists under
   Results/coagent_status/git_batches/<task>/.
2. Stage from files with `git add --pathspec-from-file=<paths-file>` or an
   equivalent path-limited command instead of reconstructing huge pathspecs in
   the shell.
3. Keep each batch well under 1000 files unless a prior dry-run proves the
   repo, hooks, and transport handle that specific slice.
4. Scan every opened batch for files at or above GitHub's 100 MiB hard limit.
   Use Git LFS only for approved binary assets that genuinely belong in the
   project; otherwise keep large assets ignored and commit a manifest.
5. If a giant tree is already tracked, `.gitignore` alone will not remove it
   from Git. First stop new generated/untracked mass with ignore rules, then
   decide whether the tracked tree should remain, be split by future commits,
   move to manifest-only/LFS, or be removed through an explicit reviewed task.
6. For local performance, consider Git's large-repo features only as bounded
   helpers: sparse checkout or partial clone for fresh analysis clones, and
   split-index/untracked-cache/fsmonitor only after recording the local config
   change and confirming it does not hide files from the release audit.
```

Known local Git incident pattern:

```text
git commit can hang in git-lfs post-commit because git-lfs runs
git ls-files -z --others --cached --exclude-standard over the whole large
working tree.
```

When this recurs, `GitIntegrator` should:

1. confirm no live Git process is using `.git/index.lock`;
2. remove only stale zero-byte `.git/index.lock` after process check;
3. prefer path-limited status/diff commands;
4. avoid broad `git status` during large external-repo staging;
5. if a single small commit is blocked only by slow hooks, use a documented
   hook-bypass or Git plumbing path and report the exact command;
6. push and report commit hash, branch, skipped paths, and residual state.

Do not let the main agent spend multiple minutes debugging Git unless the user
explicitly asks it to. Git blocker diagnosis belongs to `GitIntegrator`, with
main-agent review of the final evidence.

## 5.1 AirSim Batch Migration With Nested Agents

Use this section when importing external AirSim-family repositories from a
source directory such as `C:\Users\HP\Desktop\AirSim` into
`References/AirSim/`.

Do not copy the whole source tree into the repository in one operation. Treat
AirSim migration as a queue-backed Git task:

If the source has already been copied into the repo and produces thousands of
untracked files, immediately ignore the whole target subtree first. Then
unignore or re-copy one AirSim content family at a time. This prevents the
whole repository from becoming hostage to one failed bulk add/push.

```text
parent role:
  AirSimMigrationCoordinator
child role:
  AirSimGitBatchOwner:<content_family>
grandchild role:
  AirSimBatchWorker:<batch_id>
```

The parent owns the migration plan, ledger, integration order, and final Git
state. The child owner owns one content family and may spawn grandchildren only
for single-batch scan/migrate/verify tasks. Grandchildren must not spawn more
agents.

Recommended content families:

```text
AirSimCore
CosysAirSim
ProjectAirSim
PegasusSimulator
UnrealCV
SPEAR
IsaacSim
CarlaUE
LabPlanning
DocsAndExamples
GeneratedOrBinaryArtifacts
```

Each batch must declare:

```text
batch_id:
source_paths:
target_paths:
excluded_paths:
write_set:
large_file_scan:
gitlink_scan:
lfs_pointer_scan:
secret_scan:
expected_commit_branch:
rollback_note:
next_batch_hint:
```

Hard gates before commit:

```text
no file > 100 MB:
no nested repository committed as gitlink:
no broken Git LFS pointer files:
no Binaries/Intermediate/Saved/DerivedDataCache unless explicitly approved:
no copied credentials, tokens, or local IDE/user config:
path count and pack size small enough for one push:
```

If a batch fails due to GitHub pack size, LFS missing objects, or slow status,
split by narrower repository group or file type. Do not retry the same failed
aggregate branch.

External source exception:

```text
source:
  C:\Users\HP\Desktop\AirSim
target:
  C:\Users\HP\Desktop\MoSim\References\AirSim
scope:
  read and copy only from that source into the target
forbidden:
  deleting source files, force push, history rewrite, writing outside target
```

Review every migrated batch with a read-only reviewer before merging it into
`main`. The reviewer must check at least:

```text
requirements fit:
file-size and GitHub limit:
gitlink/LFS correctness:
generated artifact pollution:
license/attribution notes:
recovery and rollback:
```

## 5.2 Agent Log Analysis

For long-running agents, parse their WAL/run logs before changing the queue.
Track:

```text
tasks assigned:
tasks completed:
blocked tasks:
retries:
elapsed time by task:
missing evidence:
review failures:
```

Use these fields to improve the next assignment: split oversized scopes,
tighten stop conditions, add missing acceptance checks, or route the task to a
reviewer instead of another worker.

When analyzing WAL/logs, classify noisy stream events separately from stable
evidence:

```text
stable evidence:
  terminal tool results, exit codes, artifacts, commits, metrics, terminal reports
diagnostic only:
  streaming deltas, SSE/UI projection events, progress chatter, labels, raw PTY spam
pollution to exclude:
  secrets, credentials, full prompts with private data, base64 media, huge logs
```

Keep summaries path-rich and payload-light: record locators, hashes, byte
counts, and roles instead of pasting full logs into workflow docs.

## 6. External Repository Audits

When many repositories are present under `References/`, split audits by
technical domain:

| Stream | Examples |
|---|---|
| UE/rendering | AirSim, ProjectAirSim, RflySim, SPEAR, UnrealCV |
| Planning/trajectory | ego-planner, GCOPTER, Fast-Racing, SUPER |
| Perception/mapping | FAST-LIO, FAST-LIVO2, Point-LIO |
| Docs/Skills/workflow | Codex skills, subagent catalogs, agent runtime repos |
| Git/quality | large-file scan, secret scan, nested repo cleanup |

Use `Docs/Workflows/audit_external_repo.md` and `Scripts/reference/audit_external_repo.py` for
repeatable summaries.

## 7. Skills / Workflow Runtime Audits

When auditing external agent, skill, or workflow-runtime repositories, use one
owner audit agent and require three passes before changing project rules:

```text
PASS 1 inventory:
  repo purpose, useful modules, irrelevant modules, local evidence paths

PASS 2 extraction:
  reusable orchestration, WAL, evidence, validation, delegation, resume,
  doctor, and capability-coverage patterns

PASS 3 comparison:
  current project docs already covered, missing updates, contradictions,
  stale ledger rows, and exact doc patch list
```

The owner agent must return a `DO NOT ADOPT` list. Do not import full runtime
dependencies only to copy a workflow pattern.

If the user asks for `学习+更新文档三遍` or equivalent, the three passes above
become three separate learn-and-update rounds. Patch project docs after each
round:

```text
ROUND 1:
  learn inventory/relevance/source-of-truth
  patch durable routing and do-not-adopt guardrails

ROUND 2:
  learn orchestration/WAL/delegation/event patterns
  patch task graph, sub-agent contract, WAL schema, templates, and checklists

ROUND 3:
  learn validation/coverage/resume/doctor/document-pollution patterns
  patch consistency gates, stale-ledger recovery, coverage review rules,
  reviewer lanes, and rejected-pattern lists
```

Do not mark the audit done until the final summary lists the changed paths and
what each round updated.

For Round 3, prefer source slices that were not already used in Rounds 1/2:

```text
validation-before-completion and reviewer workflows:
subagent/task-distributor/reviewer definitions:
skills-runtime testing, capability coverage, and applied workflow gates:
skill/repo compliance audit checklists:
log-noise and prompt/output pollution warnings:
loop/goal/task stop contracts:
```

### 7.1 Recurring Learning Owner

External Docs/skills learning is a recurring workflow, not a one-time cleanup.
Start a fresh recurring-learning row when any trigger below occurs:

```text
sub-agent disappears, waits indefinitely, or is closed without checkpoint
task plan exists but the conversation ends before the plan is recoverable
Git, MCP, simulator, or docs workflow fails in a repeated pattern
new major tool, skill pack, MCP server, simulator, or reference repo is added
user identifies a recurring workflow mistake
major milestone completes and the workflow should be simplified or hardened
```

Recurring-learning output must be small and actionable:

```text
trigger:
source_slice:
observed_project_failure:
adopt:
reject:
target_docs:
patch_or_no_patch:
review_required:
next_trigger:
```

Use `Docs/Index/external_learning_index.md` as the compact source inventory.
Do not store raw session dumps, prompts, provider configs, secrets, or huge
logs in durable docs. If no project rule improves, record `patch_or_no_patch:
no_patch` with evidence and stop.
