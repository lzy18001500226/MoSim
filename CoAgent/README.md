# CoAgent

MoSim's project-owned agent-system workspace.

This directory is not a third-party runtime copy. It holds the architecture,
decision records, bounded research, protocol/runtime modules, tests, and
health checks for MoSim's task-first multi-conversation agent system.

## Start Here

Read these first in a new conversation:

1. `CoAgent/STATUS.md`
2. `CoAgent/docs/operating/agent_os_operating_model.md`
3. `CoAgent/docs/operating/README.md`
4. `CoAgent/docs/README.md`
5. `CoAgent/docs/architecture/coagent_architecture_issue_register.md`
6. `CoAgent/docs/architecture/coagent_problem_driven_operating_model.md`
7. `CoAgent/docs/architecture/COMPONENT_MAP.md`

Do not infer the current CoAgent direction from old chat history alone.

Current MoSim operating rule: PMO directly dispatches work to visible Codex
department threads, or creates a new visible department thread when the work
needs reusable specialty context. CoAgent is the project-owned support layer
for packet schemas, registry helpers, runtime/recovery state, result import,
doctor checks, and evidence manifests. It is not a required scheduling middle
office for ordinary MoSim work.

## Current Gate

The current approved implementation task is
`COAGENT-IMPL-TRANSPORT-GIT-6H-20260531`. It may continue project-local
CoAgent transport, Git integration, task/result, review, notification-packet,
checkpoint, status, evidence, and recovery work. Later app-server transport,
unattended automation, new permanent departments, broad hook rewrites,
tool/MCP expansion, external credentials/configuration, destructive reference
cleanup, routine external notifications, and durable internal agent swarms
remain gated.

Recent long-run checkpoints:

- `COAGENT-IMPL-NEXT-44`: status, resume, review, and evidence surfaces expose
  stale-evidence refresh recommendations and standard refresh commands.
- `COAGENT-IMPL-NEXT-45`: evidence freshness is split into current recovery
  artifacts (`critical_stale_count`) and older supporting artifacts
  (`archival_stale_count`), so archival audit files do not create unnecessary
  refresh noise.
- `COAGENT-IMPL-NEXT-46`: standard evidence-refresh commands are centralized
  in `CoAgent/evidence/refresh_commands.py`, with quick/full doctor, status,
  evidence manifest, and final review-package generation ordered consistently.
- `COAGENT-IMPL-NEXT-47`: task-health continuation summaries are promoted to
  top-level fields in task-health, status, resume, and review packages so a
  resumed conversation can read `continue_allowed`, `recommended_action`, and
  watch/blocking task ids without reverse-engineering nested task entries.
- `COAGENT-IMPL-NEXT-48`: review packages now use the same staged-file warning
  threshold as task-health/status exports by default, so broad Git surfaces
  remain visible as `continue_with_watch` instead of disappearing from the
  manual review packet.
- `COAGENT-IMPL-NEXT-49`: resume bundles now mirror the same top-level
  task-health continuation fields and evidence-manifest summary used by status
  and review packages, so a fresh conversation can make the first resume
  decision without knowing nested bundle paths.
- `COAGENT-IMPL-NEXT-50`: status export now refreshes evidence manifests after
  writing current status/resume files and rewrites the bundles with the fresh
  manifest summary. This prevents resume bundles from embedding a stale
  `critical_stale_count` for files the same command just regenerated.
- `COAGENT-IMPL-NEXT-51`: `task_bootstrap.py status-task` now uses the same
  default task-health/preflight threshold as status and review packages,
  exposes continuation and blocker/watch ids at the response root, and mirrors
  the evidence-manifest summary for first-step recovery by a fresh task
  conversation.

Gate anchors:

```text
decision_record: CoAgent/docs/decisions/coagent_design_decision_record.md
review_entry: CoAgent/docs/decisions/coagent_design_review_brief.zh.md
implementation_allowed: true
first_allowed_task: COAGENT-IMPL-01
```

## Directory Map

| Path | Purpose |
|---|---|
| `docs/` | Human-facing architecture, decision, research, and status documents |
| `docs/operating/` | Portable CoAgent agent-OS operating model, patrol/recovery, orchestration, tooling governance, and migration map |
| `learning/` | Structured audit database and learning indexer only |
| `runtime/` | Local task queue, event stream, and conversation graph seed |
| `protocol/` | Task/result packet schemas and conversation protocol |
| `context/` | Context-pack generation and contract |
| `dispatch/` | Conversation registry, task-packet text, visibility/transport-facing helpers |
| `transport/` | Visible-conversation transport adapter boundary |
| `result_router/` | Result packet validation, review gate, import, archive, summary |
| `bootstrap/` | Long-task handoff and recovery helpers |
| `memory/` | Fenced project-memory recall used as background evidence |
| `knowledge/` | Project-owned source index and search |
| `status_export/` | Compact task/doctor/context/review status bundles for human review |
| `task_health/` | Read-only active-task health snapshots and intervention hints |
| `blocker_packet/` | Read-only blocker-notification packets derived from task-health decisions |
| `evidence/` | Read-only evidence manifests that gather review/status/check artifacts |
| `review_package/` | Read-only human-review packages for long-running tasks |
| `review_queue/` | Human-review queue, gated notification packet generation, closeout recording, and closeout verification |
| `hooks/` | Preflight and safety guardrails |
| `automation/` | Guarded automation definitions and runner |
| `devops/` | Read-only Git batch and DevOps handoff helpers |
| `doctor/` | Recoverability and protocol health checks |
| `tests/` | CoAgent smoke and unit tests |

## Document Map

Use `CoAgent/docs/README.md` for the detailed document map. The short version:

- `docs/architecture/` is for system design and unresolved architecture issues.
- `docs/decisions/` is for approvals, backlogs, review briefs, and completion audits.
- `docs/research/` is for external-source learning strategy and source indexes.
- `docs/status/` is for migration/status snapshots.
- `learning/audits/` is the structured source-to-decision audit corpus.

## Validation

Run the smallest useful checks after restructuring or editing CoAgent docs:

```bash
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/doctor/check_design_gate.py
python3 CoAgent/tests/test_design_surface_docs.py
git diff --check -- CoAgent
```

Use the quick doctor for routine runtime health:

```bash
python3 CoAgent/doctor/coagent_doctor.py
```

Use the full doctor for formal review checkpoints:

```bash
python3 CoAgent/doctor/coagent_doctor.py --mode full
```

Use the extended heavy doctor only when the checkpoint specifically needs
slower split-Git or review-package smoke tests:

```bash
python3 CoAgent/doctor/coagent_doctor.py --mode full --include-heavy
```

Export a compact review bundle for one long-running task:

```bash
python3 CoAgent/status_export/status_export.py \
  --task-id COAGENT-IMPL-LONGRUN-20260531 \
  --output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.status.json \
  --markdown-output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.status.md
```

Export a read-only task-health snapshot before resuming or reviewing a long task:

```bash
python3 CoAgent/task_health/task_health.py \
  --task-id COAGENT-IMPL-LONGRUN-20260531 \
  --output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.task_health.json \
  --markdown-output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.task_health.md
```

Export a compact evidence manifest when handing a long task to another
conversation or reviewer:

```bash
python3 CoAgent/evidence/evidence_manifest.py \
  --task-id COAGENT-IMPL-LONGRUN-20260531 \
  --output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.evidence_manifest.json \
  --markdown-output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.evidence_manifest.md
```

If the manifest or resume bundle reports `stale_refresh_recommended=true`, run
the listed refresh commands before relying on old status, review, doctor, or
evidence files as current state. Stale evidence is advisory; missing evidence
is the failure condition.

Generate a blocker-notification packet from task health when continuation must
stop for user, review, safety, or rework intervention:

```bash
python3 CoAgent/blocker_packet/blocker_packet.py \
  --task-id COAGENT-IMPL-LONGRUN-20260531 \
  --output Results/agent_packets/blockers/COAGENT-IMPL-LONGRUN-20260531.blocker.json \
  --markdown-output Results/agent_packets/blockers/COAGENT-IMPL-LONGRUN-20260531.blocker.md
```

Add `--record-metadata --claim-token <claim-token>` only when the caller owns
the active task claim and needs the blocker packet path to appear in later
status, resume, evidence, and review packages.

Build one human-review package from the generated task artifacts:

```bash
python3 CoAgent/review_package/review_package.py \
  --task-id COAGENT-IMPL-LONGRUN-20260531 \
  --output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.review_package.json \
  --markdown-output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.review_package.md
```

Verify a manual review closeout before resuming from it:

```bash
python3 CoAgent/review_queue/review_queue.py verify-closeout \
  --task-id COAGENT-IMPL-LONGRUN-20260531 \
  --output Results/agent_packets/closeouts/COAGENT-IMPL-LONGRUN-20260531.closeout_verification.json \
  --markdown-output Results/agent_packets/closeouts/COAGENT-IMPL-LONGRUN-20260531.closeout_verification.md \
  --json
```

This is read-only except for the requested report files. It checks metadata,
the closeout artifact, review queue state, and task-health continuation state.
