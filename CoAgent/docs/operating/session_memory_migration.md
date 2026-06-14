# Session Memory Migration Workflow

> Portable CoAgent workflow for turning old conversation context into reviewed
> project memory without letting stale chat become current truth.

Status: split-audited portable core, 2026-06-10 CST.

Host projects must provide their own cache folders, formal target documents,
and project-specific risk examples. For the MoSim host adapter, use
`Docs/Workflows/session_memory_migration.md` and
`Docs/Index/project_work_memory_index.md`.

## 1. Core Rule

No historical chat item may be promoted directly into a formal design,
workflow, parameter, model, operating, or evidence document.

Every item must pass at least three rounds:

```text
round 1: capture as a sourced candidate
round 2: verify against current project files, evidence, and contradictions
round 3: re-verify narrow final wording, then patch the formal target
```

Until round 3 is complete, the item is cache-only. It may guide investigation,
but it is not a project claim.

## 2. Authority And Source Priority

When sources disagree, use this order:

```text
1. Current source files, generated artifacts, test output, and result packets.
2. Current workflow/design/operating docs with evidence references.
3. Explicit user or PMO decisions recorded in current project docs or packets.
4. Current visible conversation content.
5. Old session transcript content.
```

Old transcript content is useful for locating work. It is not proof of current
parameters, runtime state, acceptance, tool health, or operating authority.

## 3. Host Storage Contract

A host project using this workflow must define:

```text
formal workflow pointer:
candidate cache folder:
review logs:
scratch folder, if any:
formal target document classes:
index file for migration coverage:
ledger or event log for long migrations:
```

Do not paste full session dumps into the portable CoAgent layer. Store compact
facts, source pointers, contradiction notes, and next verification actions in
the host cache.

## 4. Candidate Schema

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

Use `risk=high` when a remembered claim would affect physical parameters,
runtime behavior, acceptance, external tool state, manual review, private auth
state, or any irreversible workflow decision.

## 5. Round Gates

Round 1 is complete only when:

- the item is written to a host cache file;
- the item has a risk level and an explicit next verification action;
- stale or rejected history is separated from candidate current facts.

Round 2 is complete only when:

- current project files or result artifacts have been re-read;
- contradictions are listed;
- high-risk items name the exact files, commands, screenshots, packets, or
  manual-review artifacts needed for proof;
- the item is updated to `round2_verified`, `rejected`, `superseded`, or
  `needs_user_review`.

Round 3 is complete only when:

- final wording is narrow and tied to current evidence;
- a formal target document is named;
- the changed docs pass the host project's formatting or doc checks;
- the cache records where the item was promoted.

Long migrations should also write round checkpoints to a host ledger or event
log with stable event names such as:

```text
round_started
round_learned
round_doc_patched
round_rejected
round_promoted
```

## 6. Promotion Rules

Promote to formal docs only when the target is the right owner:

| Item Type | Formal Target Class |
|---|---|
| Reusable operating rule | operating workflow, schema, checker, or entry pointer |
| Current task state | board, ledger, progress file, or result packet |
| Product or domain architecture | host design document |
| Runtime or simulation evidence | result artifact plus workflow reference |
| Tool procedure | host workflow or skill |
| Repair command | host debugging workflow |
| Candidate or uncertain memory | host cache only |

Never promote obsolete experiments as the latest answer. Keep them only as
`rejected` or `superseded` entries when they explain why a route must not be
resumed.

## 7. Anti-Pollution Rules

- Do not turn a historical parameter into a current parameter without checking
  the current owning source or evidence file.
- Do not turn offline helper output into formal runtime evidence unless the
  source is explicitly labeled and accepted by the host workflow.
- Do not treat App, CLI, or visible-thread state as durable project memory
  unless it is represented in current project files or packets.
- Do not keep only chat memory for user corrections, manual review decisions,
  or rejected routes.
- Do not store private auth material, full account caches, full session JSONL
  dumps, or private database contents in the migration cache.

## 8. Completion Definition

A full session-memory migration is complete only when:

1. All extractable important items from the selected session have round-1
   cache entries or are explicitly marked out of scope.
2. All high-risk items have completed round 3 promotion or are recorded as
   `rejected`, `superseded`, or `needs_user_review`.
3. The cache has a promoted-target map showing which formal docs received each
   stable item.
4. Host indexes, board/progress files, and ledgers point to the migration
   state when they are needed for recovery.
5. A new conversation can recover project direction from repository docs plus
   the reviewed cache without reading the old transcript.
