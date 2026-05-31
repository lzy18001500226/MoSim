# CoAgent Status

Date: 2026-05-31

Status: implementation_longrun_completed_pending_user_review

Latest implementation task:

```text
COAGENT-IMPL-TRANSPORT-GIT-6H-20260531
Results/agent_runtime/tasks.sqlite3
```

Current correction on 2026-05-31:

```text
Git was already pushed and synchronized (`origin/main...HEAD` was `0 0` at
HEAD `6f762994f2`), but the DevOps department conversation did not show a new
front-end-visible message. Root cause: the DevOps dispatch path used shadow
Codex homes under `Results/coagent_transport/`, so project-local result packets
and logs existed but the real WSL/Windows Codex conversation stores were not
updated for the user's front end.

Visible DevOps ping was repaired through the real WSL Codex session:
DevOps 可见通信测试 2026-05-31 收到。

Then `codex_session_repair.py sync-visible --apply` synced DevOps metadata and
rollout state to `/home/linux/.codex` and `/mnt/c/Users/HP/.codex`.

Rule update: local-only packet transport cannot be described as visible
department communication. If a department is expected to communicate visibly,
use the real Codex home resume path and sync both Codex homes, or explicitly
tell the user the fallback is local-only.
```

Goal:

```text
Run the user-approved 6-hour CoAgent implementation task: first harden
cross-conversation dispatch transport so timeout/failure writes an importable
standard result packet and closes the conversation edge; then re-dispatch
DevOps Git split work; then continue CoAgent implementation only through the
doctor/status/evidence/review closed loop. Stop for external credentials,
destructive Git, non-dry-run external notification, app-server transport,
unattended automation expansion, permanent department expansion, MCP/tool
surface expansion, or any unapproved broad hook/runtime rewrite.
```

Previous reviewed checkpoint:

```text
COAGENT-IMPL-MINILOOP-01
state=reviewed boundary reached
```

Superseded runtime task:

```text
COAGENT-ARCH-LONGRUN-01
state=cancelled
reason=user redirected from architecture-design long run to approved
implementation work.
```

Implemented checkpoint:

```text
- `CoAgent/doctor/goal_alignment.py` validates task/context/result goal
  alignment and rejects setup-only substitutes such as "create a task" or
  "open a conversation".
- `CoAgent/runtime/mosim_agent_runtime.py update-metadata` records
  result-packet metadata through the runtime event stream instead of manual
  SQLite edits.
- `CoAgent/automation/automation_tasks.json` and `worker_policy.json` now use
  the current active department registry names.
- `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md` covers the current
  `References/Agent` tree additions.
- `CoAgent/doctor/coagent_doctor.py` includes goal-alignment and metadata
  update smoke tests and reports the current approved implementation task as
  the only allowed active queue item during this checkpoint.
```

Latest health check:

```text
python3 CoAgent/doctor/coagent_doctor.py --mode full --json --output Results/coagent_doctor/latest_gateway_full.json
overallStatus=ok, ok=39, warning=0, fail=0, elapsed_seconds=59.798
```

Current review gate:

```text
COAGENT-IMPL-TRANSPORT-GIT-6H-20260531 is approved for project-local
transport/Git/closed-loop implementation. It supersedes the previous
`COAGENT-IMPL-LONGRUN-20260531` runtime task for current execution. Do not
continue into app-server transport, unattended automation expansion, new
permanent departments, broad hook rewrites, MCP/tool expansion, external
credentials or configuration, destructive reference cleanup, destructive Git,
or non-dry-run external notifications unless the specific action is already
approved or the user explicitly approves it.
```

Current implementation checkpoint:

```text
- cc-connect Weixin smoke passed and is documented in
  `CoAgent/docs/status/cc_connect_weixin_smoke_2026_05_31.md`.
- `CoAgent/gateway/cc_connect_weixin.py` is the narrow approved Weixin gateway
  adapter. It defaults to dry-run; real send requires `--send`; output is
  redacted, deduped, and audited under ignored `Results/coagent_gateway/`.
- `CoAgent/result_router/result_router.py` can generate a Weixin notification
  packet and dry-run or explicitly send it when an imported result packet
  requires human review.
- `CoAgent/tests/test_review_notification_loop.py` proves the minimal
  task/result/review/notification/status-board loop without real external
  sending.
- Result imports now write recoverability metadata back to runtime tasks:
  `review_status`, `human_needed`, `next_action`, summary/review/archive paths,
  and notification packet path.
- `CoAgent/review_queue/review_queue.py` provides a read-only human-review
  queue so returning reviewers can inspect blocked/review-required tasks in
  priority order.
- The review queue suppresses child items whose parent task is already
  cancelled/done/failed by default; use `--include-superseded` only for
  incident review.
- `CoAgent/review_queue/review_queue.py closeout` records accepted,
  accepted-with-concerns, needs-rework, or rejected manual review decisions in
  runtime metadata without automatically resuming work.
- Review closeout now also writes a recoverable JSON evidence artifact under
  `Results/agent_packets/closeouts/` and records `review_closeout_path` in
  runtime metadata, so status exports and future resumed agents can audit the
  exact manual decision instead of relying on chat memory.
- `CoAgent/review_queue/review_queue.py verify-closeout` now verifies that
  runtime review metadata, the closeout artifact, review queue state, and
  task-health continuation decision agree before a resumed agent relies on a
  manual decision. It is read-only except for optional JSON/Markdown reports.
- Human-review packages now include closeout verification, so broken or missing
  review closeout evidence becomes an explicit human-required condition instead
  of being inferred from chat history.
- `CoAgent/review_queue/review_queue.py notify` generates a blocker
  notification packet for a current review-queue item, runs the cc-connect
  Weixin adapter in dry-run mode by default, writes an ignored gateway audit,
  and records the notification packet path back to runtime metadata when the
  caller holds the task claim token or the task is unclaimed.
- `CoAgent/context/context_quality.py` provides a read-only quality gate for
  generated context packs before long-task dispatch.
- `CoAgent/status_export/status_export.py` exports compact JSON/Markdown review
  bundles for a long-running task, including task state, active board, review
  queue, doctor summary, context-quality result, and Git/runtime preflight
  summary.
- `CoAgent/doctor/coagent_doctor.py` includes gateway, review queue, status
  export, and review-notification smoke checks and allows the current long-run
  implementation task in the active queue.
- `CoAgent/transport/codex_exec.py` now uses per-adapter shadow Codex/SQLite
  homes under ignored `Results/coagent_transport/` so concurrent
  doctor/status/dispatch checks do not delete each other's rollout copy target.
- `CoAgent/hooks/preflight.py` now checks `runtime_output_ignore` with
  `git check-ignore` so doctor/status/gateway/transport/runtime local outputs
  stay out of Git unless an explicit reviewed task changes that policy.
- `CoAgent/hooks/preflight.py` now checks `git_workspace_state` for
  `.git/index.lock`, staged runtime artifacts, staged external reference-tree
  batches, and oversized staged sets so Git work can be split or delegated
  before a long task blocks on commit.
- `CoAgent/tests/test_memory_context.py` now uses a unique temporary directory
  per invocation; fixed smoke-test temp directories are unsafe because
  concurrent doctor/status runs can delete each other's SQLite/event files.
- `CoAgent/tests/test_automation_guardrails.py` now uses an isolated temporary
  automation lock directory, so concurrent doctor/status smoke checks do not
  mutate live `Results/coagent_automation/locks`.
- `CoAgent/doctor/coagent_doctor.py` now has `--mode quick|full`. Quick mode is
  the default checkpoint path; full mode is the formal review path. The slower
  split-Git dry-run/apply-plan and review-package smoke tests require
  `--include-heavy`, so routine formal gates stay below the 60 second command
  timeout. Each check records `elapsed_seconds`, so future doctor timeouts are
  attributable to a specific check.
- Status-export bundles intentionally call doctor in quick mode and skip the
  status-export self-check to avoid recursive timeout. Use
  `python3 CoAgent/doctor/coagent_doctor.py --mode full --json --output Results/coagent_doctor/latest_gateway_full.json`
  before formal human review.
- Full doctor previously ran close to the 60 second default command timeout
  because heavy packaging and split-Git integration smoke tests were included
  in every formal run. Use standard full mode for routine formal gates and
  `--mode full --include-heavy` only when those slower tests are the target.
- `CoAgent/devops/git_batch_plan.py` produces a read-only split plan for broad
  CoAgent Git integration. Current output is
  `Results/coagent_status/git_batch_plan.md`.
- `CoAgent/devops/git_split_index_check.py` verifies per-batch staged entries
  through a temporary index under `Results/tmp`. It overlays current staged
  object IDs, runs `git write-tree`, and does not create commits, update refs,
  mutate the live index, or touch the worktree.
- `CoAgent/devops/git_split_commit_dry_run.py` performs a sequential
  temporary-index dry run across all Git batches. It starts from HEAD, applies
  each batch's staged entries in review order, records per-batch tree/diff
  evidence, and verifies HEAD plus the live index fingerprint remain unchanged.
  Use it before any real split-commit implementation when staged/worktree
  overlap exists.
- `CoAgent/devops/git_split_commit_apply.py` is the explicit Git-write helper.
  Default mode only plans and verifies that the live index tree equals the
  latest sequential dry-run final tree. `--apply` creates per-batch commit
  objects with `git commit-tree`, then performs one guarded `git update-ref`
  from the original HEAD to the final split commit. It does not mutate the
  live index or worktree.
- Git safety correction: final split Git evidence should run sequentially, not
  in parallel with other live Git status/diff helpers. Read-only Git commands
  may refresh `.git/index` stat-cache metadata; use the live index tree OID as
  the semantic no-change check and keep the raw index fingerprint as audit
  detail only.
- Current Git evidence for `COAGENT-IMPL-TRANSPORT-GIT-6H-20260531`:
  `Results/coagent_status/git_batches/COAGENT-IMPL-TRANSPORT-GIT-6H-20260531/split_index_check_all.json`
  and
  `Results/coagent_status/git_batches/COAGENT-IMPL-TRANSPORT-GIT-6H-20260531/split_commit_dry_run.json`.
  Latest run checked 10 batches, 271 staged paths, and 25 staged/worktree
  overlap paths without mutating HEAD or the live index. The latest apply-plan
  evidence is
  `Results/coagent_status/git_batches/COAGENT-IMPL-TRANSPORT-GIT-6H-20260531/split_commit_apply_plan.json`;
  it plans 9 non-empty commits and confirms the live index tree matches the
  dry-run final tree before any real ref write.
- Guarded split Git apply completed successfully for the same task. It created
  9 ordinary commits, advanced `main` from
  `8989c8b0ef207be42b4162f2dbf1194895ac9870` to
  `650e23fc7a7baeaa0b4856130aee6d7b7f515954`, and pushed
  `main -> origin/main`. Evidence:
  `Results/coagent_status/git_batches/COAGENT-IMPL-TRANSPORT-GIT-6H-20260531/split_commit_apply_result.json`.
- Git recovery note: ordinary `git commit` can hang in this repository when
  Git LFS hooks are present but unavailable or slow. If a bounded commit attempt
  leaves a 0-byte `.git/index.lock` and no Git process is active, remove that
  stale lock and use the already reviewed `commit-tree` + guarded `update-ref`
  route for the narrow staged set instead of retrying the same hanging command.
- `CoAgent/runtime/mosim_agent_runtime.py` now redacts `claim_token` and other
  token-like fields in CLI JSON output by default. The claim event records only
  `claim_token_issued=true`; use `claim --show-claim-token` only when an
  operator must capture a fresh token locally.
- Latest exported long-run status bundle:
  `Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.status.json` and
  `Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.status.md`.
- `CoAgent/status_export/status_export.py` can now write a short
  `coagent_resume_bundle` via `--resume-output` and
  `--resume-markdown-output`. This is the preferred handoff for a later
  reviewer or fresh conversation because it carries checkpoint, next action,
  review state, evidence paths, health summary, operating limits, and exact
  resume commands without requiring raw chat history.
- `CoAgent/task_health/task_health.py` now emits a machine-readable
  continuation decision with `continue_allowed`, `recommended_action`,
  blocking task ids, human/review/safety task ids, stop reason, and next
  intervention. Status exports, resume bundles, and human-review packages now
  expose this decision so a future dispatcher can stop, ask, review, rework, or
  continue with watch without inferring from prose.
- `CoAgent/blocker_packet/blocker_packet.py` generates standard
  `blocker_notification` packets from task-health continuation decisions. It
  is read-only by default; `--record-metadata --claim-token <claim-token>`
  records the latest blocker check and generated packet paths in runtime
  metadata when the caller owns the task claim.
- Status exports, resume bundles, and human-review packages now expose
  `blocker_packet_needed`, the standard blocker-packet generation command, and
  the optional record-metadata command so a resumed conversation can recover
  the human-intervention route without chat memory.
- `CoAgent/bootstrap/task_bootstrap.py status-task` now returns a read-only
  recovery surface for dedicated long-task conversations: runtime state,
  artifact paths, conversation graph, task-health decision, task-specific
  review-queue items, evidence-manifest summary, and blocker-packet commands.
  This makes terminal-but-review-blocked worker results visible before a
  resumed agent incorrectly treats the task as finished.
- `CoAgent/evidence/evidence_manifest.py` now records artifact freshness
  (`modified_at`, `fresh_after_task_last_event`, `stale_count`) against the
  task's latest runtime event. Status and resume bundles expose these counts so
  a resumed conversation can refresh stale status/review/doctor packages before
  relying on them.
- `CoAgent/evidence/evidence_manifest.py`,
  `CoAgent/status_export/status_export.py`, and
  `CoAgent/review_package/review_package.py` now expose
  `stale_refresh_recommended` plus standard refresh commands when evidence is
  older than the task's latest runtime event. Stale evidence is advisory, not a
  hard review blocker; missing evidence still controls package `ok`.
- `CoAgent/evidence/evidence_manifest.py` now separates stale artifacts into
  `critical_stale_count` and `archival_stale_count`. Current recovery
  artifacts referenced by runtime metadata trigger refresh recommendations;
  older glob-discovered support artifacts remain visible for audit but do not
  create unnecessary refresh noise or review blockers.
- Standard stale-evidence refresh commands now regenerate both quick and full
  doctor outputs. This prevents a registered `doctor_quick_path` from staying
  stale while only the formal full doctor is refreshed.
- `CoAgent/evidence/refresh_commands.py` centralizes the standard refresh plan
  used by evidence manifests, status/resume exports, and review packages. The
  review package is generated last because it summarizes the freshly generated
  evidence manifest.
- Evidence manifests now treat review-package files as downstream package
  outputs. They remain listed for recovery, but they do not contribute to
  stale or critical-stale counts, which prevents evidence/review refresh loops.
- Full doctor now includes `CoAgent/tests/test_evidence_refresh_commands.py`,
  so the shared refresh-command plan is part of formal health. Expected full
  doctor count is now ok=36, warning=0, fail=0.
- Task-health continuation state is now exposed as top-level summary fields in
  task-health, status, resume, and review packages. Resumed conversations
  should read `continue_allowed`, `recommended_action`, `blocking_task_ids`,
  and `watch_task_ids` before inspecting nested per-task findings. This keeps
  `continue_with_watch` risks such as broad Git surfaces visible without
  weakening them to a plain continue decision.
- Human-review packages now use the standard staged-file warning threshold by
  default. Broad Git surfaces therefore remain visible as
  `continue_with_watch` in review packages, matching task-health and status
  exports. Smoke tests can still pass a larger threshold explicitly for clean
  fixtures.
- Resume bundles now mirror the top-level task-health continuation decision
  and evidence-manifest summary. A fresh conversation can read
  `continue_allowed`, `recommended_action`, blocker/watch ids, and evidence
  freshness from the resume bundle root before inspecting nested health
  sections.
- Status export now regenerates evidence manifests after writing current
  status/resume files, then rewrites status/resume with the fresh manifest
  summary. This prevents a newly generated resume bundle from carrying stale
  `critical_stale_count` values for artifacts that were refreshed by the same
  command.
- `CoAgent/bootstrap/task_bootstrap.py status-task` now uses the standard
  task-health/preflight threshold by default instead of hiding live Git watch
  risk behind a smoke-test threshold. It exposes continuation fields,
  blocker/watch ids, and `evidence_manifest_summary` at the response root for
  first-step recovery in a fresh task conversation. `--skip-preflight` is only
  for isolated tests or fixtures.
- User authorization note: real Weixin messages are allowed only for required
  human review or blocker notification. Routine progress, status refresh, and
  local verification should remain dry-run/local artifacts unless a blocker or
  manual-review item exists.
- CoAgent is currently a small project-owned source tree and should be staged
  deliberately as project code, excluding ignored runtime outputs and Python
  caches. Do not use broad `git add -A` over external reference trees.
- Git note: `git commit -m "Add CoAgent runtime review loop"` timed out after
  60 seconds on 2026-05-31 with no new commit created and a stale
  `.git/index.lock`; the lock was removed after confirming no active commit
  process. Keep future CoAgent commits split or delegated to DevOps when Git is
  slow. Current staged set is about 260 files; use the batch plan before any
  real commit.
```

The user confirmed on 2026-05-30 that all 10 recreated permanent department
conversations are visible. They are now promoted to `active_visible` in
`CoAgent/dispatch/department_threads.json`, and the runtime task
`COAGENT-ARCH-LONGRUN-01` links all 11 permanent conversations as recoverable
conversation edges.

Visibility metadata note:

```text
After promotion, `check_department_visibility.py` found stale rows in the WSL
alternate Codex DB for recreated department sessions. The existing
`codex_session_repair.py sync-visible --apply` path was rerun for all 10
departments. Current verification passes with 11 active_visible conversations
and no pending confirmations.

On 2026-05-30, the same WSL alternate DB drift recurred for DispatchAgent:
`/home/linux/.codex/sqlite/state_5.sqlite` had the old cli/user row and long
prompt title while WSL main DB, Windows DB, indexes, and rollout files were
present. The existing `sync-visible --apply` path was rerun for all 10
departments. `check_department_visibility.py` passes again.

Later on 2026-05-30, visibility drift recurred across multiple department
rows during the long-run architecture task. `sync-visible --apply` was rerun
for DispatchAgent, ProductStrategyAgent, RuntimePlatformAgent,
ContextMemoryAgent, ToolchainMCPAgent, KnowledgeSecretaryAgent,
VerificationAgent, SafetyComplianceAgent, DevOpsReleaseAgent, and
ExternalIntelligenceAgent using the registered active_visible thread ids.
`check_department_visibility.py` passes again with 11 active_visible
conversations and valid WSL main DB, WSL alternate DB, Windows DB, and index
rows.
```

Review entry:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/review_brief.md
```

The approved `COAGENT-IMPL-01` through `COAGENT-IMPL-07` checkpoint is complete.
`COAGENT-DESIGN-08` is complete as the current design continuation for
conversation, goal, context, communication, and worktree-isolation protocol
V1. `COAGENT-IMPL-08` is complete as the minimal implementation step for
protocol-compliance enforcement. `COAGENT-DESIGN-09` is complete as the design
closure for task surface, file surface, review surface, task-team modeling,
and review/merge/closeout role modeling. `COAGENT-DESIGN-10` is the current
design continuation for multi-conversation task-team architecture, shared
context, scoped conversation, and worktree strategy. `COAGENT-DESIGN-11`
is the current consolidation pass that maps existing vendor/framework
multi-agent research into CoAgent architecture objects before the final
operating architecture is written. Current unresolved design questions are
tracked in `CoAgent/docs/architecture/coagent_architecture_issue_register.md`; resolve
or explicitly defer them before claiming the task-first multi-conversation
model is settled.
Further implementation must continue through the post-approval backlog and its
acceptance gates.

Last completed task:

```text
CoAgent/docs/decisions/coagent_post_approval_backlog.md
COAGENT-IMPL-07
```

Last completed design task:

```text
CoAgent/docs/decisions/coagent_post_approval_backlog.md
COAGENT-DESIGN-09
```

Current design task:

```text
CoAgent/docs/decisions/coagent_post_approval_backlog.md
COAGENT-DESIGN-10
```

Current design review package:

```text
CoAgent/docs/architecture/coagent_task_surface_model.md
CoAgent/docs/architecture/coagent_review_merge_protocol.md
```

Last completed implementation task:

```text
CoAgent/docs/decisions/coagent_post_approval_backlog.md
COAGENT-IMPL-08
```

Completed scope:

```text
COAGENT-IMPL-01: freeze task-state vocabulary, event vocabulary,
task-intake classes, goal hierarchy, V1 nesting limit, and task/result
protocol references.

COAGENT-IMPL-02: align task/result packet schemas with runtime exports,
dispatch text, result-router validation, canonical status mapping, and packet
validation tests while preserving runtime-state aliases.

COAGENT-IMPL-03: strengthen preflight/hooks/doctor checks for outside-project
writes, secret-risk paths, destructive commands, broad Git risk, large-file
risk, and missing result-packet evidence.

COAGENT-IMPL-04: complete one real visible TestOwner lifecycle with a visible
department result packet imported through the result router.

COAGENT-IMPL-05: complete one dedicated long-task lifecycle with a compact
context pack, runtime checkpoint, result packet, recovery summary, and closed
conversation edge.

COAGENT-IMPL-06: decide transport expansion. App-server transport is deferred;
the staged file/CLI route remains the only real transport path until rollout
and multi-department lifecycle gates pass.

COAGENT-IMPL-07: decide scheduled automation expansion. Guarded dry-run and
explicit reviewed starts are allowed; unattended scheduler expansion is
deferred.
```

Current communication state:

```text
MainAgent and all 10 permanent department conversations are active_visible.
The user confirmed the recreated department conversations are visible/openable
on 2026-05-30. `check_department_visibility.py` currently passes with 11
active_visible conversations, valid WSL/Windows index rows, valid WSL main DB,
WSL alternate DB, and Windows DB rows, and no pending confirmations.

Current active permanent conversations:
- MainAgent / MoSim｜四旋翼无人机仿真系统
- DispatchAgent / MoSim｜调度中台
- ProductStrategyAgent / MoSim｜产品发现战略
- RuntimePlatformAgent / MoSim｜Agent Runtime 平台
- ContextMemoryAgent / MoSim｜上下文记忆索引
- ToolchainMCPAgent / MoSim｜工具链 MCP
- KnowledgeSecretaryAgent / MoSim｜知识秘书
- VerificationAgent / MoSim｜验证评测
- SafetyComplianceAgent / MoSim｜安全合规
- DevOpsReleaseAgent / MoSim｜DevOps 发布
- ExternalIntelligenceAgent / MoSim｜外部情报进化

Historical invisible, pending, deleted, and test-thread ids are diagnostic
artifacts only. Do not route from those old records. Use the active registry
and verify with:
python3 CoAgent/doctor/check_department_visibility.py
```

Current Codex visibility SOP:

```text
The successful creation path is documented in
`CoAgent/docs/status/codex_visible_thread_sop.md`.

Bootstrap tool:
python3 CoAgent/dispatch/bootstrap_department_threads.py create --apply-sync --apply-registry

Important corrections:
- create through real WSL Codex TUI sessions;
- use canonical cwd `/mnt/c/Users/HP/Desktop/MoSim`;
- run `codex_session_repair.py sync-visible --apply` when WSL/Windows metadata
  diverges;
- verify Windows rollout files and all three DB rows before asking the user to
  confirm front-end visibility;
- do not run multiple registry-writing bootstrap commands in parallel.
```

Next implementation should start from a new explicitly approved backlog item.
Do not expand later runtime behavior under the closed `COAGENT-IMPL-01` through
`COAGENT-IMPL-07` scope.

Still gated until later explicit tasks:

```text
app-server transport, unattended automation, new permanent departments,
workflow replay, broad hook rewrites, tool/MCP expansion, and durable
department-internal agent swarms.
```

Current user review entry:

```text
CoAgent/docs/decisions/coagent_design_review_brief.zh.md
```

Current completion/readiness audit:

```text
CoAgent/docs/decisions/coagent_goal_readiness_audit.md
```

Current long-run design additions:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/end_to_end_task_operating_runbook.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/worktree_merge_recovery_experiment_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/human_review_intervention_ux_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/validator_shared_envelope_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_alignment_checker_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/runbook_readiness_checker_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/implementation_approval_gate_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/retrospective_closure_checker_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/worktree_git_recovery_validator_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/human_review_package_checker_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/tool_capability_health_gate_checker_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/real_task_execution_walkthroughs.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/task_health_monitoring_and_intervention_design.md
```

`human_review_intervention_ux_design.md` is the current PMO-facing design for
manual review and external intervention. It requires one-action asks, allowed
decision values, severity, dedupe/rate-limit, redaction, blocker-specific
resume mapping, audit log, and notification readiness fields. It does not
approve email, desktop notification, GUI automation, credential handling,
conversation creation, MCP/tool calls, Git actions, or live dispatch.

`goal_alignment_checker_design.md` is the current L0 design contract for
preventing wrong-goal proof. It covers user objective, canonical task goal,
scoped objective alignment, result goal mutation, checkpoint evidence delta,
completion overclaim, recreated-goal scope loss, recovery records, `GOAL_*`
fixtures, and shared-envelope output. It does not approve goal mutation,
completion, dispatch, MCP/tool calls, worktree creation, Git actions,
notifications, Codex state repair, or automatic document rewriting.

`runbook_readiness_checker_design.md` is the current design contract for
turning the end-to-end operating runbook into a future read-only readiness
gate. It covers readiness levels, charter, proof path, context, workflow,
mailbox, packets, evidence labels, Git disposition, knowledge decision,
retrospective triggers, closeout, dependency reports, `RUNBOOK_*` fixtures,
and shared-envelope output. It does not approve live dispatch, conversation
creation, app-server transport, worktree creation, MCP/tool calls, Git actions,
notifications, scheduler behavior, goal mutation, Codex state edits,
credential/account-cache inspection, or automatic document rewriting.

`implementation_approval_gate_design.md` is the current design contract for
preventing backlog entries, phase order, broad design acceptance, or vague
continuation messages from authorizing implementation. It covers explicit
slice approval, phase entry evidence, scope, forbidden actions, dependency
reports, exit evidence, claim boundaries, `APPROVAL_*` fixtures, and
shared-envelope output. It does not approve implementation, runtime mutation,
conversation dispatch or creation, app-server transport, worktree creation,
MCP/tool calls, Git actions, notifications, scheduler behavior, goal mutation,
Codex state edits, credential/account-cache inspection, or automatic document
rewriting.

`retrospective_closure_checker_design.md` is the current design contract for
validating that repeated failures, user corrections, incidents, and review
escapes close through durable learning rather than chat memory. It covers
trigger discovery, required record shape, ownership, evidence, action targets,
close conditions, promotion/rejection/deferral, stale-action detection,
dependency reporting, `RETRO_*` fixtures, and shared-envelope output. It does
not create issues, edit docs or skills, send notifications, create
conversations, mutate runtime state, call MCP/tools, stage Git, create
worktrees, repair Codex state, inspect account caches, or emit private DB
dumps/raw transcripts.

`worktree_git_recovery_validator_design.md` is the current design contract for
Git-heavy and worktree-bound work. It covers worktree binding, workspace mode,
change inventory, path-family classification, role separation, broad-staging
rejection, large-file/generated-output policy, same-file conflicts, rollback,
cleanup, blockers, evidence-label boundaries, `GIT_*` fixtures, and the
read-only implementation boundary. It does not run Git, create worktrees,
stage, commit, push, delete, move, repair locks, edit Git config, call tools,
or dispatch DevOps work.

`human_review_package_checker_design.md` is the current design contract for
PMO-facing user intervention packets. It covers one-action asks, blocker-type
resume mapping, allowed decisions, dedupe/rate-limit, redaction, last safe
state, safe parallel work, manual evidence boundaries, notification readiness,
`HREV_*` fixtures, and shared-envelope output. It does not ask the user
automatically, send email/desktop notifications, open GUIs, call MCP/tools,
retry blocked tools, inspect credentials/account caches/private Codex DBs, or
mutate runtime/Git/conversation state.

`validator_shared_envelope_design.md` is the current design contract for
`COAGENT-IMPL-NEXT-00`. It requires future validators to use one schema,
decision vocabulary, dependency report shape, finding shape, evidence-path
policy, side-effect declaration, and claim-boundary section. It does not
approve validator implementation beyond shared constants/schema/fixtures, nor
does it approve live dispatch, runtime mutation, MCP/tool calls, Git actions,
worktree creation, notifications, GUI automation, credential handling, or
external fetch.

Current enterprise-management closure:

```text
CoAgent/docs/architecture/technical_enterprise_operating_system_closure.md
```

Current Agent design protocol:

```text
CoAgent/docs/architecture/coagent_agent_design_protocol.md
CoAgent/protocol/conversation_protocol.md
CoAgent/context/context_pack_contract.md
CoAgent/dispatch/communication_contract.md
```

Current task surface model:

```text
CoAgent/docs/architecture/coagent_task_surface_model.md
CoAgent/docs/architecture/coagent_review_merge_protocol.md
```

Current task team architecture:

```text
CoAgent/docs/architecture/coagent_task_team_architecture.md
CoAgent/docs/architecture/coagent_dynamic_task_team_v2_design.md
CoAgent/docs/architecture/coagent_minimal_closed_loop_protocol.md
```

Current vendor/framework pattern mapping:

```text
CoAgent/docs/architecture/coagent_vendor_pattern_mapping.md
```

Current long-run validator design additions:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/blocker_packet_validator_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/stress_test_artifact_validator_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/evidence_label_doctor_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/validator_dependency_and_rollout_plan.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_minimal_package_contract.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_fixture_generation_plan.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_manual_rehearsal_plan.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_completion_gate_protocol.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/architecture_decision_record_summary.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_authority_and_decomposition_protocol.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_creation_and_recovery_protocol.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/early_drift_detection_experiment_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/codex_visibility_recovery_experiment_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/final_goal_completion_audit.md
```

Current architecture issue register:

```text
CoAgent/docs/architecture/coagent_architecture_issue_register.md
```

Current problem-driven operating model:

```text
CoAgent/docs/architecture/coagent_problem_driven_operating_model.md
```

Current department capability model:

```text
CoAgent/docs/architecture/coagent_department_capability_model.md
CoAgent/docs/architecture/coagent_conversation_mapping.md
CoAgent/docs/architecture/coagent_concrete_agent_design.md
CoAgent/docs/architecture/coagent_vendor_gap_review_2026_05_29.md
CoAgent/docs/architecture/coagent_dynamic_agent_codex_feature_gap_2026_05_29.md
CoAgent/protocol/templates/agent_profile.yaml
CoAgent/protocol/templates/task_scoped_agent_profile.yaml
CoAgent/protocol/templates/handoff_mode.yaml
CoAgent/protocol/templates/capability_template.yaml
CoAgent/protocol/templates/conversation_state.yaml
CoAgent/protocol/templates/context_delta.yaml
CoAgent/protocol/templates/artifact_manifest.yaml
CoAgent/protocol/templates/trace_eval_rubric.yaml
CoAgent/protocol/templates/workflow_graph.yaml
```

Current problem-to-solution synthesis:

```text
CoAgent/docs/architecture/coagent_solution_synthesis.md
CoAgent/docs/architecture/coagent_user_intervention_ux.md
CoAgent/docs/architecture/coagent_dynamic_task_team_v2_design.md
CoAgent/docs/architecture/coagent_minimal_closed_loop_protocol.md
CoAgent/protocol/templates/
CoAgent/doctor/check_solution_design.py
```

Current minimum closed-loop proof:

```text
task_id: COAGENT-MINILOOP-01
state: needs_user_review
protocol: CoAgent/docs/architecture/coagent_minimal_closed_loop_protocol.md
bundle: Results/coagent_miniloop/COAGENT-MINILOOP-01/
human_review: CoAgent/docs/decisions/coagent_miniloop_01_human_review.md
check: python3 CoAgent/doctor/check_miniloop.py
```

Current real communication proofs:

```text
COAGENT-MINILOOP-02:
  state: accepted_with_concerns
  proof: separate Codex CLI execution surface wrote/imported a scoped result
  check: python3 CoAgent/doctor/check_miniloop_02.py

COAGENT-MINILOOP-03:
  state: superseded_not_visible
  proof: historical rollout file could be resumed, but this is not accepted as
    department communication because the user confirmed the department UI
    conversations had already been deleted
  target_thread: 019e62b1-a1d3-74c2-853c-85c510e41f59
  check: python3 CoAgent/doctor/check_miniloop_03.py
```

Current transport/session warning:

```text
MainAgent and all 10 permanent department conversations are currently
active_visible, but this does not prove unattended transport reliability.
Before routing durable work, run:
python3 CoAgent/doctor/check_department_visibility.py

Known remaining warning: visible Codex conversation transport can still spend
the 60s budget on startup/plugin/MCP noise and fail to return a result packet.
Codex App remains a review/front-end surface; CoAgent runtime state, packet
files, and the task ledger remain the durable coordination source.
```

Current verified Codex CLI entrypoint:

```text
CoAgent/docs/status/codex_cli_entrypoint.md
```

Current protocol compliance check:

```text
CoAgent/doctor/protocol_compliance.py
CoAgent/tests/test_protocol_compliance_smoke.py
```

Current known external warning:

```text
CoAgent/doctor/coagent_doctor.py remains overall warning because most registered
department thread ids still lack matching rollout files under
/home/linux/.codex/sessions. This is a transport/session-state visibility issue,
not a protocol-compliance implementation failure.
```

Current gate check:

```bash
python3 CoAgent/doctor/check_design_gate.py
```

Current gate output summary:

```text
ok: true
decision_status: approved
implementation_allowed: true
review_entry: CoAgent/docs/decisions/coagent_design_review_brief.zh.md
decision_record: CoAgent/docs/decisions/coagent_design_decision_record.md
next_action: continue from CoAgent/docs/decisions/coagent_post_approval_backlog.md; select the next approved incomplete backlog task or add a new explicit backlog item instead of expanding runtime scope opportunistically
```

Current long-running architecture task:

```text
COAGENT-ARCH-LONGRUN-01 is active. It is actual architecture design work, not a
placeholder for a 10-hour task. Current review entry:
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/review_brief.md
```

Current goal creation/recovery rule:

```text
If a wrong active goal weakens the user objective into setup work, stop using it
as authoritative. After user deletion or safe recovery, recreate the goal from
`goal_creation_and_recovery_protocol.md` preflight fields. The recreated goal
must name the real outcome and required scope components, not "create a task",
"open conversations", "spend time", or "write documents".
```

Current early drift detection design:

```text
`early_drift_detection_experiment_design.md` defines the negative and positive
scenarios that future operating-metrics checks must catch before they are
trusted: setup-only goals, scope loss on goal recreation, checkpoints without
evidence deltas, fake parallelism, stale-context resume, missing blocker
packets, timeout closeout gaps, unsupported tool claims, repeated review
escapes, and completion overclaims.
```

Current Codex visibility recovery design:

```text
`codex_visibility_recovery_experiment_design.md` records the current recovery
claim: registered department metadata drift can be checked, repaired, or
blocked with evidence, but this does not prove root-cause reliability. During
the latest check, DispatchAgent and then ProductStrategyAgent failed visibility
checks before all registered non-Main departments were resynced and the 11
active_visible registry passed again. A later check in the same continuation
failed on DispatchAgent again and was restored by another registered
all-department sync; this rapid recurrence is now a future incident scenario,
not evidence of stable unattended transport.
```

Latest long-running architecture design additions:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/enterprise_to_coagent_execution_mapping.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/operating_metrics_and_anti_drift_cadence.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/minimal_multiconversation_proof_requirements.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/handoff_mode_and_workflow_graph_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/problem_driven_external_adoption_queue.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/task_intake_to_proof_ladder_decision_table.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_packet_chain_blueprint.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_proof_package_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_b_px4_parameter_proof_package.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_c_ue_scene_truth_proof_package.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_d_git_heavy_change_proof_package.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_e_auth_license_interruption_proof_package.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/proof_ladder_and_validator_order.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/common_proof_package_validator_design.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/goal_requirement_audit_map.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/candidate_a_fixture_spec.md
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/ten_hour_audit_package.md
```

These additions keep the design task-first: enterprise-management ideas now
map to concrete CoAgent objects, and long-running work now has explicit
checkpoint cadence, drift states, operating metrics, escalation rules, and
retrospective triggers. The next minimal proof is now specified as a small
visible architecture packet chain before PX4/UE proofs, and handoff/workflow
routing is modeled as explicit objects. These are design artifacts only;
read-only metrics snapshot, handoff/workflow validators, and proof execution
remain later approved backlog items. External learning is now problem-driven:
future study must map one source slice to a current architecture problem and an
adoption/rejection decision instead of broad summary work.
Candidate A is now specified as a concrete future proof blueprint with task id
`COAGENT-PROOF-CANDIDATE-A`, required visible conversations, handoff records,
context-pack requirements, result/review/context-delta/trace-eval outputs,
pass/block criteria, and explicit non-goals. It is not yet authorized for live
execution.
The follow-up proof-package design defines the required inputs, outputs,
workflow graph shape, preflight checks, post-dispatch checks, negative
fixtures, and result interpretation for Candidate A. Default next step is a
proof-package validator or fixture generator before live multi-conversation
dispatch.
The PX4 and UE stress tests are now also mapped into proof packages. Candidate
B starts with log audit and parameter identifiability before estimator or
MWORKS tuning. Candidate C starts with scene-source classification and UE/MCP
capability before map modification or planning-readiness claims. Both remain
design-only and should run after Candidate A is stable or after explicit user
approval of packet/transport risk.
Candidate D and Candidate E now cover operational risk: Git-heavy changes must
start with inventory, worktree binding, integration plan, blockers, and
rollback; auth/license/GUI/manual interruptions must become blocker/resume
packets with exact PMO user asks and safe parallel-work decisions. Both remain
design-only.
`worktree_merge_recovery_experiment_design.md` now expands Candidate D from a
high-level Git-heavy proof package into a concrete recovery scenario design:
workspace mode selection, same-file conflicts, broad staging rejection, large
binary/generated-output policy, external path rejection, destructive-action
blockers, Git lock/timeout closeout, review/merge/close owner separation,
rollback, cleanup, user-change reconciliation, third-party reformat risk, and
main-thread Git blockage. This remains design-only and does not approve
staging, commit, push, worktree creation, cleanup, destructive repair, or
automatic DevOps dispatch.
`end_to_end_task_operating_runbook.md` now composes the separate protocols into
one serious-task operating sequence: intake, canonical charter, proof-path
classification, context assembly, workflow graph, topology selection,
execution checkpoints, mailbox replay, evidence review, integration or hold,
knowledge promotion, retrospective, and closeout. This is the default design
entry for routing future serious tasks, but it remains design-only and does
not approve live dispatch, conversation creation, worktree creation, Git
operations, MCP/tool calls, notifications, schedulers, or automatic goal
mutation.
`proof_ladder_and_validator_order.md` consolidates Candidate A-E into the
default proof ladder, common package contract, shared checks, validator order,
deviation rules, and audit questions.
`common_proof_package_validator_design.md` specifies the future read-only
validator contract for the ladder, including modes, layout, error codes,
candidate extensions, JSON output, fixture matrix, and no-dispatch/no-tool/no-
Git/no-notification boundary.
`goal_requirement_audit_map.md` maps the active goal to current evidence,
weak/incomplete evidence, audit commands, and next work priorities. It is an
interim audit aid and explicitly does not mark the goal complete.
`candidate_a_fixture_spec.md` adds the fixture-level source of truth for
Candidate A: valid minimal package, negative fixture matrix, stable expected
finding codes, validator order, and implementation acceptance. This keeps the
next validator implementation from being prose-driven or live-dispatch-driven.
`candidate_a_validator_execution_design.md` now defines how
`COAGENT-IMPL-NEXT-15` should run Candidate A validation: preflight,
post-dispatch, and fixture modes; package layout; validation pipeline;
dependency boundaries; report JSON; finding codes; live-proof gate; closeout
gate; and forbidden implementation scope. This remains design-only.
`handoff_workflow_validator_design.md` now defines how
`COAGENT-IMPL-NEXT-13` should validate handoff and workflow graph objects:
handoff-only, workflow-only, pre-dispatch, post-dispatch, and fixture modes;
required fields; cross-object checks; dispatch safety checks; post-dispatch
checks; JSON output; `HWFLOW_*` finding codes; Candidate A integration; and
forbidden implementation scope. This remains design-only.
`task_intake_to_proof_ladder_decision_table.md` adds the task-first routing
bridge: incoming user tasks are classified into proof path A-E, first gate,
minimum team, secondary risks, and anti-drift questions before conversations
or departments are selected.
`ten_hour_audit_package.md` is now the concentrated 10-hour review entry with
verdict format, required commands, requirement mapping, forbidden claims, user
decision points, next approval queue, and closeout checklist.
`external_adoption_proposal_contract.md` now defines how external vendor,
open-source, enterprise, and local-incident ideas become auditable adoption
proposals with one problem id, bounded source slice, lifecycle state, evidence
level, accept/reject/defer/probe decision, promotion target, reviewer, and
future validation method. This is design-only; the proposal store/checker
remains gated under `COAGENT-IMPL-NEXT-10`.
`context_index_and_assembly_design.md` now defines how new scoped
conversations should receive context from named index families and slice types
instead of raw transcript volume. It covers retrieval manifests, budget
classes, stale/rejected material filters, context fit checks, PX4/UE examples,
and the future `COAGENT-IMPL-NEXT-21` read-only checker. This is design-only;
no vector search, automatic context generation, or automatic dispatch is
approved.
`context_delta_checker_design.md` now defines how `COAGENT-IMPL-NEXT-02`
should validate context deltas and acknowledgements: strict lifecycle fields,
ack records, fresh/stale/paused state, pre-resume checks, post-result checks,
JSON output, `CTX_*` finding codes, fixtures, and integration with Candidate A,
context index, mailbox, and handoff/workflow validators. This remains
design-only.
`operating_metrics_snapshot_design.md` now defines how
`COAGENT-IMPL-NEXT-09` should generate a read-only long-task health snapshot:
durable input sources, metric states, evidence classification, progress/
coordination/quality/organization/safety metrics, drift detection rules,
negative fixtures, JSON/Markdown output, stable `OMS_*` finding codes, and
integration with packet, context, handoff, mailbox, visibility, and proof
validators. This remains design-only and does not approve dashboards,
schedulers, transport, conversation creation, Git operations, or notifications.
`transport_timeout_hardening_design.md` now defines how
`COAGENT-IMPL-NEXT-12` should close out Codex visible-conversation dispatch
timeouts: attempt state machine, timeout classes, startup/plugin/MCP noise
classification, required closeout records, timeout blocker packets, late-result
reconciliation, targeted cleanup policy, dispatch-edge reconciliation,
stable `TRN_*` finding codes, and fixtures. The RuntimePlatformAgent run is now
understood as a transport timeout with later result-packet inconsistency; the
hardening design remains design-only and does not approve unattended dispatch,
app-server transport, conversation creation, process cleanup automation, or
global Codex configuration changes.
`external_adoption_store_checker_design.md` now defines how
`COAGENT-IMPL-NEXT-10` should validate problem-driven external learning:
proposal store layout, checker modes, schema fields, lifecycle and store checks,
evidence-level guard, source boundary rules, accepted/rejected/probe decision
rules, JSON output, stable `ADOPT_*` finding codes, fixture matrix, and
promotion gate. This remains design-only and does not approve crawling,
scheduling, external fetch, code import, third-party runtime integration,
notifications, conversation creation, or automatic knowledge promotion.
`check_department_visibility.py` has now exposed recurring DispatchAgent
visible-thread metadata drift in the WSL alternate Codex DB. The existing
`sync-visible --apply` repair still restores all 11 active_visible rows, but
the recurrence is tracked as P47 and should become a transport/session-state
diagnose plus repair-or-blocker design item before reliable dispatch.
`codex_visibility_drift_reliability_design.md` now specifies that design item:
pre-dispatch visibility invariants, bounded registered-thread repair policy,
`codex_visibility_drift` blocker packet, evidence records, state machine, and
future `COAGENT-IMPL-NEXT-22` gate. This remains design-only and does not
approve automatic conversation creation or unattended dispatch.
Latest diagnosis shows WSL main DB and Windows DB keep the correct
`vscode/vscode` short-title row, while `/home/linux/.codex/sqlite/state_5.sqlite`
reverts DispatchAgent to `source=cli`, `thread_source=user`, lowercase cwd, and
the long bootstrap prompt as title/preview/first user message.
`mailbox_ledger_and_replay_design.md` now defines the missing durable mailbox
layer for cross-conversation communication: task-local messages, ack records,
state transitions, replay, timeout/retry, contradiction handling, closeout,
and recovery. The future gated implementation item is
`COAGENT-IMPL-NEXT-23`; no transport, delivery, app-server, email, or
automatic conversation behavior is approved by this design.
`goal_authority_and_decomposition_protocol.md` now defines the missing
goal-authority layer: user objective, canonical task goal, task-team goal,
department goal, scoped conversation objective, subagent prompt objective, and
implementation step goal. It rejects setup work, visible conversations,
elapsed time, and document volume as substitutes for the user's outcome. The
future gated implementation item is `COAGENT-IMPL-NEXT-25`; no automatic goal
mutation, task completion, dispatch, tool/MCP call, worktree creation, or Git
operation is approved by this design.
`retrospective_and_improvement_closure_protocol.md` now defines the missing
retrospective closure layer: mandatory triggers, improvement-action schema,
owner/review-owner rules, promotion/rejection gates, stale-action policy,
current COAGENT-ARCH-LONGRUN-01 retrospective candidates, and future
`COAGENT-IMPL-NEXT-26` read-only checker with stable `RETRO_*` finding codes.
This remains design-only and does not approve issue creation, notification,
automatic documentation edits, conversation creation, runtime dispatch, Git
operations, tool/MCP calls, or skill/hook mutation.
`tool_capability_health_and_fallback_protocol.md` now defines the missing P13
tool capability layer: route-family capability cards, health levels from
`unavailable` through `product_evidence_ready`, evidence-label compatibility,
stop/fallback decisions, blocker/resume policy, and future
`COAGENT-IMPL-NEXT-27` read-only checker with stable `TOOL_*` finding codes.
This remains design-only and does not approve MCP/tool execution, UE map
mutation, Fab download/import automation, MWORKS simulation execution, Codex
dispatch, Git staging, automatic repair, or broad tool expansion.
`tool_capability_health_gate_checker_design.md` now defines the concrete
P13/NEXT-27 read-only checker contract: card discovery, required fields,
route/health/evidence vocabulary, stale-card detection, health-level claim
ceilings, blocker/fallback checks, unsafe probe rejection, route-specific
UE/Fab/MWORKS/Codex/Git/external-reference rules, dependency behavior, and
`TOOL_*` fixtures. This remains design-only and does not call or repair tools.
`real_task_execution_walkthroughs.md` now maps the architecture onto concrete
MoSim task families: PX4/Sunray150 parameter identification and UE/Fab/local
scene-truth productization. It records canonical goals, invalid weakened goals,
initial departments, task-scoped conversations, context packs, workflow graphs,
mailbox/result packet boundaries, contradiction handling, PMO asks, Git
disposition, evidence boundaries, and completion criteria. This remains
design-only and does not run product proofs or create conversations.
`task_health_monitoring_and_intervention_design.md` now defines the runtime
intervention playbook for active long-running tasks: health states, trigger
table, critical-path ownership, topology shrink rules, one-action PMO blocker
asks, PX4/UE task-health applications, close-ready criteria, and future
`COAGENT-IMPL-NEXT-32` read-only checker scope. This remains design-only and
does not approve scheduler, dashboard, live dispatch, task mutation,
conversation creation, worktree creation, MCP/tool calls, notification, Git
operations, or automatic document edits.
`implementation_sequence_and_release_plan.md` now defines the missing P23
implementation sequence layer: R0 review baseline, R1 validator foundation,
R2 packet/blocker atoms, R3 Candidate A preflight, R4 supervised Candidate A
proof, R5 communication recovery, R6 product-adjacent proofs, R7 tool-backed
product execution, and R8 operating evolution. It records entry/exit evidence,
skip rules, approval-packet fields, release milestones, and forbidden claims.
This remains design-only and does not approve implementation by itself.

Current department review findings:

```text
DispatchAgent: topology/context/communication direction accepted with runtime
enforcement and recovery risks.

ContextMemoryAgent: context pack is sufficient for scoped handoff, but context
version/hash, context delta, acknowledgement, pause/resume, reviewer, and
resume condition must become machine-checkable.

VerificationAgent: verification detects the right long-task drift modes
conceptually, but thresholds, required packet fields, PX4/UE templates, and
negative drift tests are still required.

RuntimePlatformAgent: visible conversation transport is not yet reliable enough
for unattended default dispatch. The latest RuntimePlatform dispatch reached
the visible conversation and read evidence, but produced no result packet
within 60s and was cleaned up.

Result packet contract: department conversations must use the flat text packet
template in `CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/result_packet_contract_hardening.md`
until nested YAML support is deliberately implemented. Conditional completion
must be represented by `review_status=needs_review`,
`acceptance_state=partially_met`, and `risks`, not custom status values.

Blocker contract: transport timeouts and invalid result packets are now first
class blocker types in
`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/blocker_packet_templates.md`.

Result packet validator contract:
`CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/result_packet_validator_design.md`
now defines the missing read-only validator layer for
`COAGENT-IMPL-NEXT-11`: required fields, allowed values, structural and
semantic rejection rules, stable finding codes, positive/negative fixtures,
output JSON, repair policy, and implementation boundary. This is design-only;
no router semantics, dispatch behavior, conversation creation, notification,
Git staging, or tool/MCP execution is approved by it.
```

Current checkpoint evidence:

```text
Results/agent_packets/COAGENT-IMPL-04-VISIBLE-LIFECYCLE.yaml
Results/agent_packets/COAGENT-IMPL-05-LONG-TASK-LIFECYCLE.yaml
Results/coagent_bootstrap/COAGENT-IMPL-05-LONG-TASK-LIFECYCLE.recovery.json
Results/coagent_doctor/latest.json
CoAgent/transport/TRANSPORT_EXPANSION_DECISION.md
CoAgent/automation/SCHEDULED_AUTOMATION_DECISION.md
CoAgent/docs/decisions/coagent_impl_03_07_completion_audit.md
CoAgent/docs/architecture/technical_enterprise_operating_system_closure.md
```

Shortest approval template:

```text
CoAgent design approved.
Decision date: YYYY-MM-DD
Approved defaults: all
Notes: <optional>
```

Completed implementation tasks:

```text
CoAgent/docs/decisions/coagent_post_approval_backlog.md
COAGENT-IMPL-01
COAGENT-IMPL-02
COAGENT-IMPL-03
COAGENT-IMPL-04
COAGENT-IMPL-05
COAGENT-IMPL-06
COAGENT-IMPL-07
```
