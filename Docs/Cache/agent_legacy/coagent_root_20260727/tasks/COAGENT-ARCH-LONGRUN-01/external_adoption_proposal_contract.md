# COAGENT-ARCH-LONGRUN-01 External Adoption Proposal Contract

Date: 2026-05-30
Status: design contract for later validator/store

## Purpose

External learning is useful only when it changes a current CoAgent problem in a
controlled way. This contract defines how a vendor article, open-source project,
or management practice becomes an adoption proposal that can be accepted,
rejected, deferred, validated, and promoted.

This is a design artifact. It does not approve a crawler, scheduler, third-party
runtime integration, automatic code import, email sender, or new permanent
department.

## Core Rule

```text
one current problem
  -> one bounded source slice
  -> one adoption proposal
  -> one decision
  -> one promotion or rejection record
```

No proposal may start from "study everything". It must start from a problem id
in `architecture_problem_matrix.md` or a task-specific blocker.

## Storage Model

Future implementation should store proposals under:

```text
CoAgent/adoption/proposals/<proposal_id>.yaml
CoAgent/adoption/decisions/<proposal_id>.md
CoAgent/adoption/rejections/<proposal_id>.md
```

Until that store exists, task-level proposals may be recorded in this task
directory and linked from `problem_driven_external_adoption_queue.md`.

## Proposal Identifier

Format:

```text
ADOPT-YYYYMMDD-<problem_id>-<short_slug>
```

Examples:

- `ADOPT-20260530-P32-handoff-graph`
- `ADOPT-20260530-P10-drift-metrics`
- `ADOPT-20260530-P12-codex-worktree-boundary`

## Required Proposal Fields

| Field | Required | Meaning |
|---|---|---|
| `proposal_id` | yes | stable identifier |
| `status` | yes | proposal lifecycle state |
| `problem_id` | yes | matrix problem or task blocker |
| `queue_id` | optional | external queue item such as `EXT-003` |
| `source_family` | yes | vendor, open_source, enterprise, local_incident |
| `source_refs` | yes | exact paths or URLs read |
| `source_slice` | yes | files, modules, sections, or pages actually inspected |
| `pattern` | yes | pattern being considered |
| `fit_claim` | yes | why the pattern addresses this problem |
| `risk_if_copied_blindly` | yes | failure mode if imported without adaptation |
| `license_security_notes` | yes | license, credential, privacy, cloud, or runtime risk |
| `coagent_adaptation` | yes | how the idea maps to CoAgent objects |
| `rejected_alternatives` | yes | options considered and rejected |
| `evidence_level` | yes | current evidence level |
| `decision` | yes | adopt, adapt, reject, defer, or probe |
| `promotion_target` | yes | doc, protocol, skill, hook, doctor, backlog, archive |
| `verification_method` | yes | how future regression or success is checked |
| `owner` | yes | accountable department |
| `review_owner` | yes | reviewer that can accept/reject |
| `next_trigger` | yes | event that reopens or advances the proposal |

## Lifecycle States

| State | Meaning | Allowed Next States |
|---|---|---|
| `draft` | proposal written but not reviewed | `needs_evidence`, `ready_for_decision`, `rejected` |
| `needs_evidence` | source slice or fit claim is too weak | `ready_for_decision`, `rejected`, `deferred` |
| `ready_for_decision` | enough evidence exists for owner review | `accepted`, `adapt_later`, `rejected`, `needs_probe` |
| `needs_probe` | bounded experiment is required | `accepted`, `adapt_later`, `rejected`, `deferred` |
| `accepted` | may update a design/protocol/backlog target | `promoted`, `superseded` |
| `adapt_later` | useful but not current implementation scope | `ready_for_decision`, `deferred`, `superseded` |
| `deferred` | valid but blocked by approval, data, or runtime | `ready_for_decision`, `rejected`, `superseded` |
| `rejected` | not suitable for current CoAgent/MoSim | `superseded` |
| `promoted` | accepted lesson is in durable project knowledge | `superseded` |
| `superseded` | replaced by newer decision | terminal |

## Decision Values

| Decision | Meaning |
|---|---|
| `adopt_now_design` | update design/protocol/backlog now |
| `adopt_now_validator` | create a later validator/backlog item |
| `adapt_later` | keep as candidate after proof or approval |
| `portable_only` | useful for another project, not current MoSim |
| `reject_now` | do not use in current CoAgent |
| `probe_first` | run bounded read-only experiment before decision |

## Evidence Levels

Evidence level must never be inflated.

| Level | Minimum Evidence |
|---|---|
| `source_seen` | source path/URL and inspected slice are recorded |
| `mapped` | linked to one CoAgent problem and one failure mode |
| `designed` | a CoAgent design/protocol/backlog target is updated |
| `templated` | schema, packet, or fixture draft exists |
| `validated` | validator/check/fixture has passed or failed as expected |
| `proved_in_loop` | minimal closed-loop task used the pattern |
| `promoted` | lesson is in stable skill, workflow, hook, doctor, or backlog |

## Acceptance Rules

A proposal can be accepted only if all are true:

1. it maps to exactly one primary problem id;
2. source evidence is bounded and cited;
3. the CoAgent adaptation is specific;
4. Safety can name the risk boundary;
5. Verification can name the evidence or validator;
6. Dispatch can place the result in a task, protocol, or backlog item;
7. KnowledgeSecretary can state where the accepted lesson will live.

## Rejection Rules

Reject or defer a proposal when it:

- requires direct third-party runtime integration before a proof exists;
- moves durable state outside project-owned files;
- depends on hidden group chat or UI state as source of truth;
- requires credentials, cloud services, or external automation not approved;
- adds permanent departments without task pressure;
- copies code without license/security review;
- solves a generic agent problem that is not current CoAgent friction.

## Minimal Positive Example

```yaml
proposal_id: ADOPT-20260530-P31-handoff-workflow-objects
status: accepted
problem_id: P31
queue_id: EXT-003
source_family: vendor_and_framework
source_refs:
  - local: CoAgent/docs/architecture/coagent_vendor_pattern_mapping.md
source_slice:
  - handoff and workflow graph patterns only
pattern: typed handoff modes plus explicit workflow graph
fit_claim: reduces prose-only routing and makes pre-dispatch validation possible
risk_if_copied_blindly: a full graph engine would add runtime complexity before packet checks are stable
license_security_notes: no code copied; design pattern only
coagent_adaptation:
  - CoAgent/protocol/templates/handoff_mode.yaml
  - CoAgent/protocol/templates/workflow_graph.yaml
rejected_alternatives:
  - raw group chat routing
  - importing an external graph runtime now
evidence_level: designed
decision: adopt_now_validator
promotion_target: COAGENT-IMPL-NEXT-13
verification_method: fixture validator rejects missing goal/result/review/return path
owner: DispatchAgent
review_owner: VerificationAgent
next_trigger: user approves handoff/workflow validator slice
```

## Minimal Rejection Example

```yaml
proposal_id: ADOPT-20260530-P12-third-party-agent-runtime
status: rejected
problem_id: P12
queue_id: EXT-004
source_family: open_source
source_refs:
  - local: References/Agent
source_slice:
  - runtime orchestration pattern only
pattern: replace CoAgent runtime with a third-party agent engine
fit_claim: could provide graph execution and agent scheduling
risk_if_copied_blindly: moves task state, tool authority, and safety boundaries into an unreviewed runtime
license_security_notes: code/license/security review not performed
coagent_adaptation:
  - keep event-log and checkpoint ideas only
rejected_alternatives:
  - direct runtime replacement
  - third-party API integration
evidence_level: mapped
decision: reject_now
promotion_target: rejected idea archive
verification_method: future adoption requires proof package plus security/license review
owner: RuntimePlatformAgent
review_owner: SafetyComplianceAgent
next_trigger: only reopen after Candidate A and common validator are stable
```

## Future Validator Checks

`COAGENT-IMPL-NEXT-10` should add a read-only checker that verifies:

- proposal id format;
- valid lifecycle state;
- primary problem id exists in `architecture_problem_matrix.md`;
- source refs are non-empty and project-safe when local;
- source slice is bounded;
- decision and evidence level are from the allowed vocabulary;
- accepted proposals name a promotion target and verification method;
- rejected proposals name the rejection reason and reopen trigger;
- no proposal claims `validated`, `proved_in_loop`, or `promoted` without a
  matching artifact/check reference.

## Promotion Closeout

When a proposal is promoted, the closeout must update at least one durable
target:

- architecture/protocol document;
- workflow;
- skill;
- hook or doctor-check backlog;
- validator/backlog item;
- rejected idea archive;
- context pack or task board if it affects active work.

The closeout must also mark stale alternatives as rejected, deferred, or
superseded so future conversations do not revive old assumptions from memory.
