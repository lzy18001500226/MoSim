# Agent Orchestration Workflow

> Use this when a task is large enough that sub-agents, long Git work, or
> reference-repository audits could continue across user turns.

## 1. Task Graph First

Before spawning agents, write a short task graph:

```text
critical path:
parallel streams:
write ownership:
blocking risks:
verification:
git/quality owner:
```

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
objective:
read scope:
write set:
owner role:
dependencies:
acceptance check:
reviewer role:
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

Provider behavior matrix:

| Capability | Codex policy here | Claude Code note |
|---|---|---|
| Subagent trigger | Explicitly spawned by main agent/user-authorized task graph | May auto-delegate from descriptions |
| Nested delegation | Default depth 1; depth 2 only for bounded parent/child queue with WAL | Do not assume named subagents can spawn subagents |
| Worktrees | Prefer one Git owner; use isolated worktrees only for disjoint branches/scopes | Claude has separate worktree-isolation concepts |
| Custom schemas | Treat local `.toml` examples as unverified until official Codex docs confirm | Claude frontmatter is not Codex syntax |
| Background tools | Record pending/denied tool state in WAL | Claude background behavior may deny prompt-required tools |

For long-running execution streams such as Git batching, Unreal project smoke
tests, simulator bring-up, large reference audits, and repeated documentation
learning passes, assign one owner agent and keep feeding that agent until its
stop condition is reached. Do not let the main agent take over the worker's
implementation details unless the worker is blocked, closed, or explicitly
hands back a decision point.

The main agent must not close a long-running owner agent just because one
checkpoint succeeded. Close it only after the full stop condition is reached,
the task is superseded, or the owner is blocked and the ledger records the
recovery point. Do not batch-close agents. For each agent, first write or
update the terminal checkpoint in the ledger/PROGRESS/WAL, then close that one
agent deliberately.

Management analogy for long work:

```text
main agent:
  director / general manager; owns objective, priorities, queue, approvals,
  integration, verification, and final report
TaskSecretary:
  secretary / PMO; records instructions, checkpoints, blockers, task state,
  review requirements, and supervision signals
child owner:
  project manager; owns one bounded stream and may coordinate workers
grandchild worker:
  employee; executes one explicit batch and returns evidence
reviewer:
  independent QA; checks evidence and risks before integration
```

The detailed department model lives in
`workflows/org_operating_model.md`. Use it when a task needs company-style
division of labor: secretary/PMO, project owners, testing, security, DevOps,
architecture, knowledge management, and incident review.

The director should not grind through every worker task when the queue is
large. It should update durable state, assign the next owner, keep the critical
path moving, and review evidence before integration. A child owner must not
silently wait after a small checkpoint when its assigned stream still has ready
items inside the same scope.

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
checkpoint must be captured in `results/tmp/task_intake/`, promoted to
`workflows/agent_task_ledger.md` or `PROGRESS.md` when stable, and only then
treated as recoverable state. Chat memory alone is not state.

Testing is a separate stream. Use a `TestOwner` child agent when validation has
multiple kinds, such as unit tests, Git checks, large-file checks, model checks,
MCP smoke tests, or GUI/manual review preparation. Do not mix TestOwner with a
Git owner or implementation owner unless the task is explicitly tiny.

Skills are work instructions, not task owners. Agents use skills to execute a
role; the orchestration ledger decides who owns the task, what evidence is
required, and when the task is complete.

## 2. Ledger Requirement

Record every long-running delegated task in `workflows/agent_task_ledger.md`.
For runs lasting more than one turn, also write JSONL events under:

```text
results/agent_runs/<run_id>/events.jsonl
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
  "summary": "Started safe integration of Skills/okwinds and branch cleanup",
  "paths_read": ["workflows/agent_task_ledger.md"],
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
{"path":"results/.../metrics.json","source":"MWORKS_MCP","sha256":"","bytes":0,"role":"metrics"}
```

Do not paste secret-bearing payloads or full GUI event streams into WAL.
Record paths, hashes, sizes, and claim roles instead.

For delegated runs, record child WAL locators as artifacts:

```json
{"path":"results/agent_runs/<child_run>/events.jsonl","source":"agent_wal","sha256":"","bytes":0,"role":"child_wal"}
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
results/tmp/task_intake/YYYY-MM-DD.md
```

Promote only stable items into `workflows/agent_task_ledger.md` or
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
| TaskSecretary | Convert user instructions and agent returns into recoverable tasks | `results/tmp/task_intake/*` plus promoted ledger/PROGRESS rows |
| Research owner | Complete bounded source audit or parameter-identification research | Source list, evidence/inference/unknowns, patch plan or report |
| Reviewer | Review docs/code/model changes without implementing | Findings with file references and residual risk |

Every sub-agent prompt for this project should include a concrete goal and
terminal condition. If runtime support allows it, request `model=gpt-5.5` and
`reasoning_effort=high` explicitly at spawn time.

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
docs/workflows/AGENTS/PROGRESS
Skills/Mworks
Skills/Agent and Skills/okwinds
scripts/tests
models/scenarios
references/AirSim
references/Lab
references/PX4
references/Sunray/CUAV
references/MWORKS/RflySim
unreal/UE source/config
results/tmp and generated outputs
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
links in docs/index/workflow_index.md still resolve:
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
docs/workflows
Skills/*
references/AirSim/*
references/Lab/*
references/RflySim/*
unreal/*
```

Each branch must pass large-file and gitlink checks before push. If a branch
push fails because the pack is too large, split by narrower repository group
instead of retrying the same pack repeatedly.

## 5.1 AirSim Batch Migration With Nested Agents

Use this section when importing external AirSim-family repositories from a
source directory such as `C:\Users\HP\Desktop\AirSim` into
`references/AirSim/`.

Do not copy the whole source tree into the repository in one operation. Treat
AirSim migration as a queue-backed Git task:

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
  C:\Users\HP\Desktop\Quadrotor\references\AirSim
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

When many repositories are present under `references/`, split audits by
technical domain:

| Stream | Examples |
|---|---|
| UE/rendering | AirSim, ProjectAirSim, RflySim, SPEAR, UnrealCV |
| Planning/trajectory | ego-planner, GCOPTER, Fast-Racing, SUPER |
| Perception/mapping | FAST-LIO, FAST-LIVO2, Point-LIO |
| Skills/workflow | Codex skills, subagent catalogs, agent runtime repos |
| Git/quality | large-file scan, secret scan, nested repo cleanup |

Use `workflows/audit_external_repo.md` and `scripts/audit_external_repo.py` for
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

External docs/skills learning is a recurring workflow, not a one-time cleanup.
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

Use `docs/index/external_learning_index.md` as the compact source inventory.
Do not store raw session dumps, prompts, provider configs, secrets, or huge
logs in durable docs. If no project rule improves, record `patch_or_no_patch:
no_patch` with evidence and stop.
