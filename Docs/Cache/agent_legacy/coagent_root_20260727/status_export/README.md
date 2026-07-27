# CoAgent Status Export

## Purpose

This directory owns compact review bundles for long-running CoAgent work.

The export is read-only apart from writing the requested bundle file. It
collects the current runtime task, active task board, human-review queue,
doctor summary, optional context-pack quality result, and compact Git/runtime
preflight state into one JSON/Markdown artifact for later user review. It also
embeds the runtime event audit so the reviewer can see whether SQLite task
events and the append-only JSONL event stream are still consistent. It embeds
the read-only task-health snapshot so a reviewer can see whether a long task is
clear to continue, stale, waiting for review, blocked for user input, or blocked
for safety. For broad Git surfaces, it also embeds a compact read-only DevOps
handoff summary and points to the full handoff packet. It also writes and
summarizes a compact evidence manifest so a later conversation can locate the
task's status, resume, doctor, review, notification, and handoff artifacts.

## Command

```bash
python CoAgent/status_export/status_export.py \
  --task-id COAGENT-IMPL-LONGRUN-20260531 \
  --output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.status.json
```

Use `--markdown-output` for a human-readable summary.

Use `--resume-output` and `--resume-markdown-output` when another conversation
or a later reviewer needs a short recovery surface instead of the full status
bundle:

```bash
python CoAgent/status_export/status_export.py \
  --task-id COAGENT-IMPL-LONGRUN-20260531 \
  --output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.status.json \
  --markdown-output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.status.md \
  --resume-output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.resume.json \
  --resume-markdown-output Results/coagent_status/COAGENT-IMPL-LONGRUN-20260531.resume.md
```

The resume bundle is intentionally shorter than the full status bundle. It
contains the current checkpoint, next action, review state, evidence paths,
quick health summary, task-health intervention state, Git handoff summary,
evidence-manifest summary, blocker packet paths when present, blocker packet
generation commands, operating limits, and exact resume commands for the next
agent/reviewer.

Task-health continuation fields are exposed both as a nested `decision` object
and as top-level fields in the task-health summary. A fresh or resumed
conversation should first read `continue_allowed`, `recommended_action`,
`blocking_task_ids`, and `watch_task_ids`; then inspect per-task findings only
when it needs the detailed reason.

The Markdown bundle includes:

- task state and latest checkpoint,
- review queue count,
- doctor counts,
- context quality,
- Git index-lock status,
- staged file count,
- staged runtime-output count,
- staged external-reference count,
- runtime-output ignore-rule status.
- runtime event audit counts, drift findings, and sensitive event payload
  counts.
- task health state and findings.
- task-health continuation decision, including whether autonomous continuation
  is allowed and which task ids block it.
- blocker packet need state and the command to generate a packet if task health
  says continuation must stop.
- Git handoff batch totals, overlap counts, risks, and recommended sequence.
- evidence-manifest output path, evidence counts, missing evidence count, and
  stale evidence count.
- optional resume bundle path and Markdown handoff when requested.

The Git summary is informational for broad staged sets. Hard failures remain
`.git/index.lock`, staged runtime artifacts, staged external reference trees,
or missing runtime-output ignore rules.

## Doctor Interaction

`status_export` embeds a compact doctor summary in each status bundle. That
embedded doctor call uses doctor `quick` mode and skips the
`coagent.status_export` smoke check; otherwise doctor calls status export,
status export calls doctor, and the check recurses until the 60 second command
timeout.

Use the full doctor for top-level human-review health:

```bash
python3 CoAgent/doctor/coagent_doctor.py --mode full --json --output Results/coagent_doctor/latest_gateway.json
```

Expected top-level count in full mode after the status-export, task-health, Git
handoff, evidence-refresh-command, evidence-manifest, and review-package smoke
checks are included:

```text
overallStatus=ok, ok=36, warning=0, fail=0
```

Status bundles intentionally report the embedded doctor in quick mode. The
exact count is lower than full mode because the heavier smoke tests are not
part of the checkpoint status path.

```text
overallStatus=ok, mode=quick
```

## Evidence Freshness

The embedded evidence manifest includes freshness metadata. `stale_count` means
one or more recorded evidence files are older than the task's latest runtime
event. This is a warning surface for resumed conversations: refresh the affected
status, review, doctor, or evidence package before treating it as current.

When stale evidence exists, the status JSON, status Markdown, resume JSON, and
resume Markdown all expose `stale_refresh_recommended=true` and a standard
`refresh_commands` list. Run those commands before relying on a recovered
review package or status bundle after a checkpoint changed `last_event_at`.
The standard refresh list updates both quick and full doctor outputs because
either can be registered as current recovery evidence in runtime metadata.
The list is generated centrally by `CoAgent/evidence/refresh_commands.py` and
ends with `review_package.py`, after the evidence manifest has been refreshed.

The freshness summary separates `critical_stale_count` from
`archival_stale_count`. Only critical stale recovery artifacts trigger the
refresh recommendation. Archival stale files are retained as audit history and
should not stop autonomous continuation by themselves.
Review package files are downstream consumers of the evidence manifest, so the
manifest lists them but does not use them as freshness inputs.
