# COAGENT-ARCH-LONGRUN-01 External Adoption Store Checker Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-10`

## Purpose

CoAgent has a large reference corpus and many vendor/engineering lessons. The
risk is broad learning without a durable decision. This design defines the
future read-only proposal store checker that turns external ideas into
accepted, rejected, deferred, or probe-required records tied to current CoAgent
problems.

This document builds on:

- `problem_driven_external_adoption_queue.md`
- `external_adoption_proposal_contract.md`
- `knowledge_promotion_protocol.md`
- `operating_metrics_snapshot_design.md`

It does not implement a crawler, scheduler, web search agent, third-party
runtime integration, code import, email sender, or automatic promotion.

## Core Rule

```text
external learning is valid only when it maps one bounded source slice
to one current CoAgent problem and one auditable adoption decision
```

No future task should accept "I studied many projects" as durable evidence
unless it produces proposal records that can be checked, rejected, reopened,
or promoted.

## Store Layout

Future implementation should create the directory only when the first approved
proposal is written:

```text
CoAgent/adoption/
  proposals/
    ADOPT-YYYYMMDD-Pxx-short-slug.yaml
  decisions/
    ADOPT-YYYYMMDD-Pxx-short-slug.md
  rejections/
    ADOPT-YYYYMMDD-Pxx-short-slug.md
  fixtures/
    valid_accepted/
    valid_rejected/
    inflated_evidence_level/
    missing_problem/
    unbounded_source_slice/
    external_path_without_note/
    accepted_without_verification/
    rejected_without_reopen_trigger/
```

Task-local proposals may remain under the task directory until the store is
approved, but the checker contract should be the same.

## Checker Modes

The future command should accept:

```text
--proposal <path>
--proposal-dir <path>
--problem-matrix CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/architecture_problem_matrix.md
--queue CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/problem_driven_external_adoption_queue.md
--mode single|store|promotion|fixtures
--json-output <optional path>
--strict
```

Mode behavior:

- `single`: validate one proposal file;
- `store`: validate proposal ids, duplicates, lifecycle transitions, and
  source/proof references across the store;
- `promotion`: validate that a proposal can be promoted into durable docs,
  skills, hooks, doctor checks, or backlog;
- `fixtures`: run positive and negative proposal fixtures.

The checker is read-only. It may not create proposals, update docs, fetch
sources, or promote lessons.

## Required Proposal Schema

Each proposal should be a simple YAML mapping with these fields:

```yaml
proposal_id:
status:
problem_id:
queue_id:
source_family:
source_refs: []
source_slice: []
pattern:
fit_claim:
risk_if_copied_blindly:
license_security_notes:
coagent_adaptation: []
rejected_alternatives: []
evidence_level:
decision:
promotion_target:
verification_method:
owner:
review_owner:
next_trigger:
created_at:
updated_at:
```

Lists must be YAML lists or JSON arrays. Nested structures should be allowed
only inside `source_refs` when a source needs `{local: ...}` or `{url: ...}`.

## Field Rules

| Field | Rule |
|---|---|
| `proposal_id` | matches `ADOPT-YYYYMMDD-P[0-9]+-<slug>` |
| `problem_id` | exists in `architecture_problem_matrix.md` |
| `queue_id` | if present, exists in `problem_driven_external_adoption_queue.md` |
| `source_family` | one of `vendor`, `open_source`, `enterprise`, `local_incident`, `reference_corpus`, `mixed` |
| `source_refs` | non-empty, no secrets/private paths, local refs stay under project root unless explicitly marked external reference |
| `source_slice` | non-empty and bounded; not "all repo", "all docs", or raw transcript |
| `fit_claim` | names the CoAgent failure mode or proof gap |
| `risk_if_copied_blindly` | non-empty and specific |
| `license_security_notes` | non-empty even when "no code copied" |
| `coagent_adaptation` | names CoAgent object targets: doc, protocol, template, checker, backlog, workflow, skill, hook proposal, archive |
| `evidence_level` | allowed evidence level and not inflated beyond backing evidence |
| `decision` | allowed decision value |
| `promotion_target` | required for accepted/adapted proposals |
| `verification_method` | required unless decision is `reject_now`, but rejected proposals still need reopen condition |
| `review_owner` | required for all non-draft states |
| `next_trigger` | required and must be actionable |

## Lifecycle Checks

Allowed states and transitions are inherited from
`external_adoption_proposal_contract.md`.

Additional store-level checks:

- one active proposal id maps to one primary problem id;
- multiple proposals may address the same problem only if their source slices or
  patterns differ;
- a superseded proposal names the replacing proposal;
- rejected proposals keep a reopen trigger;
- accepted proposals name a promotion target;
- promoted proposals cite the durable target that changed;
- no proposal stays in `draft` or `needs_evidence` while being used as context
  for another task.

## Evidence Level Guard

The checker should reject evidence inflation:

| Claimed Level | Required Backing Evidence |
|---|---|
| `source_seen` | source refs and source slice |
| `mapped` | valid problem id and failure mode |
| `designed` | changed design/protocol/backlog artifact path |
| `templated` | template/schema/fixture path |
| `validated` | validator/check command output or fixture result |
| `proved_in_loop` | minimal closed-loop proof package/result |
| `promoted` | durable skill/workflow/hook/doctor/backlog target plus review |

If backing evidence is missing, return `ADOPT_EVIDENCE_INFLATED`.

## Source Boundary Rules

Allowed local refs:

- project docs under `CoAgent/`, `Docs/`, `Scripts/`, `Models/`, `Results/`
  when relevant;
- reference corpus paths under `References/`;
- task artifacts under `CoAgent/tasks/`.

Rejected or review-required refs:

- account caches, credentials, browser profiles, SSH keys, token files;
- broad user directories;
- external absolute paths not explicitly approved as reference material;
- unbounded source slices such as "all References" or "entire GitHub".

When a proposal cites a third-party repo or vendor URL, it must say whether
code was copied. If code is copied later, that is a separate license/security
review and not allowed by this checker.

## Decision Rules

Accepted proposal:

- `status` is `accepted`, `adapt_later`, or `promoted`;
- decision is `adopt_now_design`, `adopt_now_validator`, `adapt_later`, or
  `probe_first`;
- promotion target and verification method are non-empty;
- Safety and Verification owners are clear if runtime/tool/safety risk exists.

Rejected proposal:

- status is `rejected`;
- decision is `reject_now` or `portable_only`;
- rejection reason appears in `risk_if_copied_blindly`,
  `rejected_alternatives`, or decision markdown;
- `next_trigger` says when to reopen, if ever.

Probe proposal:

- status is `needs_probe`;
- decision is `probe_first`;
- bounded experiment is read-only unless separately approved;
- expected output and stop condition are named.

## Output JSON

The checker should emit:

```json
{
  "ok": false,
  "mode": "single",
  "proposal_id": "ADOPT-20260530-P32-example",
  "decision": "reject",
  "finding_codes": ["ADOPT_PROBLEM_UNKNOWN"],
  "findings": [
    {
      "code": "ADOPT_PROBLEM_UNKNOWN",
      "severity": "error",
      "field": "problem_id",
      "message": "problem id P999 is not present in the problem matrix"
    }
  ],
  "promotion_allowed": false,
  "review_required": true,
  "next_action": "map proposal to an existing problem id or add the problem to the matrix first"
}
```

Decisions:

- `accept`: proposal is structurally valid;
- `accept_needs_review`: valid but requires reviewer action;
- `reject`: invalid proposal record;
- `block`: unsafe source, inflated evidence, or promotion attempt violates
  gate.

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `ADOPT_MISSING_FIELD` | required field absent |
| `ADOPT_BAD_ID` | proposal id format invalid |
| `ADOPT_PROBLEM_UNKNOWN` | problem id not in matrix |
| `ADOPT_QUEUE_UNKNOWN` | queue id not in adoption queue |
| `ADOPT_SOURCE_EMPTY` | no source refs or source slice |
| `ADOPT_SOURCE_UNBOUNDED` | source slice too broad |
| `ADOPT_SOURCE_UNSAFE` | source ref is secret/private/out-of-scope |
| `ADOPT_FIT_MISSING` | fit claim does not name CoAgent failure mode |
| `ADOPT_RISK_MISSING` | blind-copy risk missing or generic |
| `ADOPT_LICENSE_MISSING` | license/security notes missing |
| `ADOPT_BAD_STATUS` | invalid lifecycle state |
| `ADOPT_BAD_DECISION` | invalid decision value |
| `ADOPT_BAD_EVIDENCE_LEVEL` | invalid evidence level |
| `ADOPT_EVIDENCE_INFLATED` | claimed evidence level lacks backing artifact |
| `ADOPT_PROMOTION_TARGET_MISSING` | accepted proposal has no promotion target |
| `ADOPT_VERIFICATION_MISSING` | verification method missing |
| `ADOPT_REVIEW_OWNER_MISSING` | non-draft proposal has no reviewer |
| `ADOPT_REOPEN_TRIGGER_MISSING` | rejected/deferred proposal has no next trigger |
| `ADOPT_SUPERSEDES_MISSING` | superseded proposal does not name replacement |
| `ADOPT_DIRECT_RUNTIME_IMPORT` | proposes unreviewed third-party runtime integration |
| `ADOPT_CODE_COPY_WITHOUT_REVIEW` | code copied without license/security review |

Codes are stable test-contract values.

## Fixture Matrix

Positive fixtures:

| Fixture | Expected |
|---|---|
| accepted design-only proposal | `accept_needs_review` or `accept` |
| rejected runtime-import proposal | `accept` as rejected record |
| probe-first read-only experiment proposal | `accept_needs_review` |
| promoted proposal with durable target evidence | `accept` |

Negative fixtures:

| Fixture | Expected Codes |
|---|---|
| missing problem id | `ADOPT_PROBLEM_UNKNOWN` |
| source slice is "all References" | `ADOPT_SOURCE_UNBOUNDED` |
| accepted proposal with no verification method | `ADOPT_VERIFICATION_MISSING` |
| rejected proposal with no reopen trigger | `ADOPT_REOPEN_TRIGGER_MISSING` |
| `validated` without check output | `ADOPT_EVIDENCE_INFLATED` |
| direct third-party runtime replacement | `ADOPT_DIRECT_RUNTIME_IMPORT` |
| copied code without license/security note | `ADOPT_CODE_COPY_WITHOUT_REVIEW` |

## Integration With CoAgent

| Object | Integration |
|---|---|
| problem matrix | proposal must cite one primary `Pxx` problem |
| external adoption queue | proposal may cite one `EXT-xxx` queue item |
| knowledge promotion | promotion requires durable target and stale alternative closeout |
| context index | accepted/rejected proposals become context slices, not raw research notes |
| operating metrics | unmapped research increments `research_loop` / `OMS_RESEARCH_UNMAPPED` |
| proof ladder | validated/proved claims must cite proof-package or checker evidence |

## Acceptance For `COAGENT-IMPL-NEXT-10`

Implementation is acceptable only when:

1. a valid accepted proposal from an existing local reference project passes;
2. a valid rejected proposal passes as a rejection record;
3. unknown problem ids fail;
4. unbounded source slices fail;
5. accepted proposals without verification method fail;
6. rejected proposals without reopen trigger fail;
7. evidence inflation fails;
8. no crawler, scheduler, external fetch, code import, third-party runtime
   integration, notification, conversation creation, or automatic promotion is
   implemented;
9. fixtures cover stable `ADOPT_*` finding codes.

## Current Consequence

For `COAGENT-ARCH-LONGRUN-01`, this design means future study of Hermes,
OpenClaw, Codex, Kimi, Anthropic, or other sources must produce proposal
records tied to a problem id. Broad source summaries remain useful only as
background; they are not accepted architecture changes until the proposal
checker can validate a bounded adoption decision.
