# Session Memory Migration Workflow

> Current MoSim workflow for promoting old conversation memory into project
> documents without polluting active context. legacy agent-era variants are
> legacy/reference only.

> Purpose: migrate important context from long Codex conversations into MoSim
> project documents without letting stale or wrong historical conclusions pollute
> the current engineering source of truth.

This workflow applies to the long conversation currently named around
`MoSim|四旋翼无人机仿真系统` / `四旋翼无人机图形化仿真系统`, and to any later
high-context Codex App / VSCode / CLI thread that must be summarized before
starting a new conversation.

## Core Rule

No historical chat item may be promoted directly into a formal design,
workflow, parameter, model, or evidence document.

Every item must pass at least three rounds:

```text
round 1: capture in cache as a candidate
round 2: verify against current project files, evidence, and contradictions
round 3: re-verify narrow final wording, then patch the formal target document
```

Until round 3 is complete, the item is cache-only. It may guide investigation,
but it is not a project claim.

## Storage Layout

Use project-local storage only:

```text
Docs/Workflows/session_memory_migration.md
  Formal workflow and promotion gate.

Docs/Cache/session_memory_migration/
  Tracked cache-only candidate facts, rejected historical notes, extraction
  backlog, and round review logs. These files are recoverable across new
  conversations but are not formal project truth until promoted.

Results/tmp/session_memory_migration/
  Optional local scratch output only. Do not use this ignored directory as the
  durable memory surface.
```

Do not paste full session dumps into the repository. Store compact facts,
source pointers, contradiction notes, and next verification actions.

## Source Priority

When sources disagree, use this priority order:

```text
1. Current source files, scripts, model files, generated manifests, and test output.
2. Current project workflow/design docs that have evidence references.
3. Explicit user manual-review results recorded in project docs or result files.
4. Current visible conversation content.
5. Old session transcript content.
```

Old transcript content is useful for locating work, but it is not proof. It is
especially weak for numeric assembly parameters, controller behavior,
simulation evidence, visual acceptance, MCP state, and Codex runtime behavior.

## Candidate Schema

Each cached item should record:

```text
id:
topic:
round:
status: candidate | contradiction | rejected | superseded | round2_verified | ready_for_round3 | promoted
risk: low | medium | high
candidate_statement:
known_sources:
contradictions_or_history:
current_evidence_needed:
formal_target_if_promoted:
next_round_action:
```

Use `risk=high` for:

- physical or visual assembly parameters;
- controller or simulation performance claims;
- MWORKS/Sysplorer integration claims;
- ROS/FAST-LIO/RViz evidence claims;
- manual visual acceptance or rejection;
- Codex state repair commands that touch files outside the project.

## Round Gates

Round 1 is complete only when:

- the item is written to a cache file under
  `Docs/Cache/session_memory_migration/`;
- the item has a risk level and an explicit next verification action;
- stale or rejected history is marked separately from candidate current facts.

Round 2 is complete only when:

- the current project files or result artifacts have been re-read;
- contradictions are listed;
- high-risk items include exact file paths, test commands, screenshots,
  result manifests, or manual-review packet paths needed for proof.
- the cache item is updated to `round2_verified`, `rejected`, `superseded`, or
  `needs_user_review`.

Round 3 is complete only when:

- final wording is narrow and tied to current evidence;
- a formal target document is named;
- `git diff --check` passes for the changed docs;
- the cache item records where it was promoted.

For long migrations, also record round checkpoints in a task-local cache note
under `Docs/Cache/session_memory_migration/` or an event log under
`Results/agent_runs/<run_id>/events.jsonl`, using the existing
`round_started`, `round_learned`, and `round_doc_patched` event vocabulary.
`Docs/Workflows/agent_task_ledger.md` is legacy trace-back only and is not the
normal surface for new migration state.

## Promotion Rules

Promote to formal docs only when the target is the right owner:

| Item Type | Formal Target |
|---|---|
| Current operating rule | `AGENTS.md` or the relevant `Docs/Workflows/*.md` |
| Active task state | the current conversation's direct user request plus a task-local result/status note; `PROGRESS.md` and the retired board are historical hints only |
| Algorithm/system architecture | `Docs/Design/*.md` |
| Simulation evidence | `Results/...` manifest plus report/workflow reference |
| MWORKS/Sysplorer procedure | `Docs/Workflows/*.md` or `Docs/Skills/Mworks/*/SKILL.md` |
| Codex/App/CLI repair | `Docs/Workflows/debug_mcp.md` |
| Candidate or uncertain memory | `Docs/Cache/session_memory_migration/*.md` only |

Never promote obsolete experiments as the latest answer. Keep them only in a
`rejected` or `superseded` section if they explain why a route must not be
resumed.

## Explicit Anti-Pollution Rules

- Do not turn a historic parameter into a final parameter without checking the
  current asset/model/source file and the latest manual review status.
- Do not call an offline script result MWORKS evidence unless it ran through
  MWORKS/Sysplorer/MCP or is explicitly labeled `source=offline_script`.
- Do not treat Codex App/VSCode/CLI live sync as durable project memory.
- Do not keep only chat memory for user corrections, manual review decisions,
  or rejected routes.
- Do not store secrets, auth files, full account caches, full session JSONL
  dumps, or private database contents in the cache.

## Completion Definition For A Full Session Migration

The long-session migration is complete only when:

1. All extractable important items from the selected session have round-1 cache
   entries or are explicitly marked out of scope.
2. All high-risk items have either completed round 3 promotion or are recorded
   as `rejected`, `superseded`, or `needs_user_review`.
3. The cache has a promoted-target map showing which formal docs received each
   stable item.
4. `Docs/Index/workflow_index.md`, `PROGRESS.md`, and the relevant
   `Docs/Cache/session_memory_migration/` index or note point to the migration
   state.
5. A new Codex conversation can recover project direction from repository docs
   plus the cache without reading the old chat transcript.
