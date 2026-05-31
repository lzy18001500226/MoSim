# COAGENT-ARCH-LONGRUN-01 Tool Capability Health Gate Checker Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-27`

## Purpose

Define the read-only checker that validates tool capability cards before a
task relies on MCP, GUI, Codex transport, Git, Fab/manual-import, MWORKS, UE,
or external-reference routes for product, runtime, or coordination claims.

This checker exists because CoAgent has repeatedly faced tool-route ambiguity:

- Fab inventory visibility was easy to confuse with automated download/import;
- UE rendering or screenshots were easy to confuse with planning truth;
- MWORKS offline scripts were easy to confuse with Sysplorer/MCP evidence;
- Codex App/VSCode visibility was easy to confuse with durable task state;
- Git metadata was easy to confuse with product correctness;
- previously working MCP routes could become stale, missing, or login-blocked.

This design extends:

- `tool_capability_health_and_fallback_protocol.md`
- `evidence_label_doctor_design.md`
- `blocker_packet_validator_design.md`
- `candidate_b_px4_parameter_proof_package.md`
- `candidate_c_ue_scene_truth_proof_package.md`
- `candidate_d_git_heavy_change_proof_package.md`
- `candidate_e_auth_license_interruption_proof_package.md`
- `validator_shared_envelope_design.md`

It is design-only. It does not open UE/MWORKS/Fab, inspect account caches,
repair MCP servers, create conversations, dispatch work, run simulations,
mutate maps, download assets, stage Git, send notifications, or rewrite
capability cards.

## Core Rule

```text
tool claims are valid only at or below the proven capability-card health level
```

The checker does not prove a tool works. It proves that a task's declared
claims, fallbacks, blockers, and next actions are consistent with the current
capability evidence.

## Inputs

The future checker should accept:

```text
--task-id <task id>
--package-root <task or proof package directory>
--mode scan|strict|proof_package|closeout|fixture
--json-output <optional path>
```

Input files, when present:

| File | Purpose |
|---|---|
| `tool_capability_cards.yaml` or `tool_capabilities/*.yaml` | route-family capability records |
| `task_charter.yaml` | canonical task goal, requested claims, allowed paths |
| `workflow_graph.yaml` | tool nodes and required route families |
| evidence manifest or evidence-label report | provenance and label compatibility |
| blocker packet | unavailable, auth/license, GUI, timeout, unsafe-write, or approval stop |
| proof package metadata | Candidate B/C/D/E route-specific requirements |
| manual import/review record | user-performed Fab/UE/MWORKS/manual step |
| truth artifact manifest | UE planning-truth claim support |
| Git inventory or worktree binding record | Git/tool route claim support |
| closeout record | final claim, fallback, held blocker, or downgraded state |

The checker may validate standalone cards in `scan` mode, but `strict`,
`proof_package`, and `closeout` modes must report missing dependencies instead
of silently passing a claim that needs evidence from another checker.

## Capability Card Discovery

The checker should discover required route cards from four sources:

| Source | Examples |
|---|---|
| task class | PX4 parameter tuning needs MWORKS/Sysplorer before simulation tuning |
| workflow graph | tool node names `UE_MCP`, `MWORKS_MCP`, `git_integration`, `Fab_manual_import` |
| evidence labels | `MWORKS_MCP`, `UE_MCP`, `Fab_manual_import`, `git_metadata`, `external_reference` |
| product claims | planning truth, report-ready simulation, automated dispatch, staged Git integration |

If a product or coordination claim needs a route and no matching card exists,
the checker fails with `TOOL_CARD_MISSING`.

## Card Required Fields

Each card must include the protocol fields:

```yaml
card_id: toolcap-<task-id>-<route>
task_id: COAGENT-ARCH-LONGRUN-01
route_family: MWORKS_SYSPLORER | MWORKS_SYSLAB | UNREAL_EDITOR |
  EPIC_FAB | CODEX_TRANSPORT | GIT_DEVOPS | EXTERNAL_DOCS | OTHER
route_name: <short route>
route_owner: <department or scoped conversation>
required_for: <downstream need>
requested_claim: <claim this route would support>
current_health_level: unavailable | discoverable | read_only |
  write_probe_safe | execution_safe | product_evidence_ready
evidence_label: design_only | runtime_metadata | manual_review |
  MWORKS_MCP | MWORKS_GUI | UE_MCP | UE_GUI | Fab_manual_import |
  git_metadata | external_reference
evidence_paths:
  - <project path or approved external evidence id>
probe_timestamp: <ISO-8601 or not_run>
probe_command_or_manual_action: <smallest probe or manual action>
timeout_seconds: 60
known_limitations:
  - <limitation>
approved_operations_at_level:
  - <allowed operation>
forbidden_operations_at_level:
  - <forbidden operation>
fallback_routes:
  - <route and claim downgrade>
blocker_policy:
  blocker_type: <type>
  user_action_required: <exact ask or none>
  resume_condition: <smallest safe probe or confirmation>
  retry_policy: <retry rule>
review_owner: <agent>
stale_after: <duration or invalidating event>
```

Cards may include additional route-specific fields, but missing required fields
must not be accepted because another document happens to describe the route.

## Required Checks

### Route And Vocabulary

Reject if:

- route family is not in the allowed vocabulary;
- health level is missing or unsupported;
- evidence label is missing or unsupported;
- route owner, required downstream claim, or review owner is missing;
- route name is too vague to map to a tool, MCP server, GUI route, manual
  import step, Git route, or external-reference route.

### Evidence And Label Compatibility

Reject if:

- health level above `unavailable` has no evidence path or manual record;
- evidence path is outside the project without approved infrastructure
  exception;
- evidence label is stronger than the route evidence;
- `runtime_metadata` or `git_metadata` is used to prove product behavior;
- `external_reference` is used as adopted policy without an adoption proposal;
- evidence-label doctor output is missing when the package claims MCP, GUI,
  manual import, Git, runtime, or external-reference evidence.

### Staleness

Reject if a card is stale because:

- `stale_after` elapsed;
- the task moved from read-only to write/execution/product claim;
- the route failed after the card was written;
- the route was repaired but no post-repair probe is recorded;
- the target model, map, Codex thread, worktree, or asset source changed;
- the user/manual intervention changed the environment and no resume probe is
  recorded.

The checker should prefer explicit invalidating events over a fixed time rule.
When the card omits `stale_after`, report `TOOL_CARD_STALE` in strict modes
because there is no durable freshness policy.

### Health Level Versus Requested Claim

The checker must enforce claim ceilings:

| Health Level | Maximum Claim |
|---|---|
| `unavailable` | blocked route only |
| `discoverable` | installed/configured/inventory-visible only |
| `read_only` | observed state only |
| `write_probe_safe` | reversible mutation on non-critical target only |
| `execution_safe` | bounded execution smoke only |
| `product_evidence_ready` | product-specific evidence claim named by proof package |

Reject any stronger claim with `TOOL_PRODUCT_OVERCLAIM`.

### Blocker And Fallback Policy

Reject if:

- unavailable or failed routes lack blocker type, resume condition, and retry
  policy;
- auth/license/manual-review blockers ask the user vaguely;
- fallback route is used without explicit claim downgrade;
- retry policy allows blind retry after unchanged evidence;
- safe parallel work advances a claim that the blocked route was supposed to
  prove.

### Unsafe Write Or Execution Probes

Reject if:

- UE map mutation is proposed before `write_probe_safe`;
- MWORKS simulation claim is proposed before model-check route is
  `execution_safe`;
- Fab download/import automation is proposed from inventory visibility alone;
- Codex transport dispatch is proposed from UI visibility without project
  packet and registry evidence;
- Git staging/commit/push is proposed from unclassified inventory or broad
  change set;
- a proof package asks the checker to run the tool in order to validate the
  card.

## Route-Specific Rules

### MWORKS / Sysplorer / Syslab

Reject:

- offline scripts labeled `MWORKS_MCP` or `MWORKS_GUI`;
- simulation-quality claims without result-variable evidence;
- report-ready claims without model name, scenario, raw result, metrics, and
  source label;
- repeated login/license retry without user confirmation and smallest health
  probe.

Allowed downgrade:

- identifiability or algorithm analysis can proceed as `offline_script` or
  `design_only` if simulation tuning remains blocked.

### Unreal Editor / UE MCP

Reject:

- screenshots, rendered views, or visual inspection as planning truth;
- planning readiness without collision/navmesh/occupancy/SDF/semantic-layer
  artifact or accepted equivalent;
- write probe on Entry/unknown map;
- map mutation or truth export without safe map and route health record.

Allowed downgrade:

- visual review may support a visual claim, but not route planning,
  navigation, collision, or map-truth claims.

### Epic / Fab / Manual Import

Reject:

- Fab library visibility as proof of download, automated import, UE
  compatibility, component invocation, map modification, or truth generation;
- account-cache body access without explicit approved infrastructure need;
- unsupported UE-version assets used as active scene-source proof;
- manual import claims without manual record and follow-up UE project probe.

Allowed downgrade:

- use local editable projects or user-performed manual import as the product
  route when Fab automation is blocked.

### Codex Transport

Reject:

- App/VSCode UI visibility as durable task source of truth;
- unknown or deleted thread ids;
- dispatch without context pack, packet target, expected result path, timeout,
  and closeout condition;
- repeated hidden retries after transport timeout.

Allowed downgrade:

- UI can be used as a review surface; project registry, packets, mailbox, and
  runtime state remain authoritative.

### Git / DevOps

Reject:

- Git status, diff, or commit as proof of product correctness;
- `git add -A` plans for broad/import/binary batches;
- large-file, generated-output, or external-reference changes without policy;
- destructive cleanup without explicit approval.

Allowed downgrade:

- Git metadata can support inventory and integration-process claims only.

### External Docs And Open-Source References

Reject:

- broad summaries without problem id;
- unreviewed code copying;
- temporal vendor claims without current citation;
- direct promotion into policy without adoption proposal and review owner.

Allowed downgrade:

- record an external idea as candidate knowledge until adoption is accepted.

## Decisions

The checker should emit exactly one top-level decision:

| Decision | Meaning |
|---|---|
| `pass` | cards and claims are consistent |
| `pass_with_warnings` | route is usable only with explicit limitations |
| `needs_dependency` | dependent evidence/checker output is missing |
| `needs_review` | human reviewer must accept, reject, or rework claim boundary |
| `block` | route is unavailable, stale, unsafe, or waiting on user/tool condition |
| `reject` | claim is invalid, inflated, or unsafe |

The decision must be wrapped in the shared validator envelope once
`COAGENT-IMPL-NEXT-00` exists.

## Stable Finding Codes

| Code | Meaning |
|---|---|
| `TOOL_CARD_MISSING` | task needs tool route but no card exists |
| `TOOL_ROUTE_UNKNOWN` | route family or route name is unsupported |
| `TOOL_HEALTH_INVALID` | health level is missing or not allowed |
| `TOOL_EVIDENCE_MISSING` | claimed health lacks evidence path or manual record |
| `TOOL_EVIDENCE_LABEL_MISMATCH` | label is stronger than route evidence |
| `TOOL_CARD_STALE` | card is older than stale policy or task state changed |
| `TOOL_PRODUCT_OVERCLAIM` | product claim exceeds health level |
| `TOOL_BLOCKER_INCOMPLETE` | failed route lacks blocker/resume/retry fields |
| `TOOL_FALLBACK_UNDECLARED` | fallback used without claim downgrade |
| `TOOL_UNSAFE_WRITE_PROBE` | write or execution attempted before safe level |
| `TOOL_SCREENSHOT_AS_TRUTH` | visual evidence used as planning truth |
| `TOOL_FAB_VISIBILITY_OVERCLAIM` | Fab inventory used as import/execution proof |
| `TOOL_MWORKS_OFFLINE_OVERCLAIM` | offline output labeled as MWORKS evidence |
| `TOOL_CODEX_UI_OVERCLAIM` | UI visibility treated as durable task state |

If the implementation needs more granular diagnostics, it should add a
`detail_code` field under these stable codes instead of fragmenting the public
finding vocabulary.

## Fixture Matrix

Positive fixtures:

| Fixture | Expected |
|---|---|
| MWORKS execution-safe card with result evidence and smoke-test-only claim | `pass` |
| UE read-only card with current-level summary and planning readiness false | `pass` |
| Fab manual-import card with user action record, UE follow-up probe, and downgraded claim | `pass_with_warnings` |
| Codex transport card with registry, packet path, timeout, and UI-as-review-only boundary | `pass` |
| Git inventory card that claims process evidence only | `pass` |
| external-reference card linked to an adoption proposal | `pass` |

Negative fixtures:

| Fixture | Expected Codes |
|---|---|
| proof package has tool node but no card | `TOOL_CARD_MISSING` |
| unknown route family | `TOOL_ROUTE_UNKNOWN` |
| missing or unsupported health level | `TOOL_HEALTH_INVALID` |
| read-only card with no evidence path | `TOOL_EVIDENCE_MISSING` |
| runtime metadata used as product proof | `TOOL_EVIDENCE_LABEL_MISMATCH` |
| card invalidated by task phase change | `TOOL_CARD_STALE` |
| discoverable Fab inventory claims automated import | `TOOL_FAB_VISIBILITY_OVERCLAIM` |
| screenshot claims UE planning truth | `TOOL_SCREENSHOT_AS_TRUTH` |
| offline CSV labeled MWORKS evidence | `TOOL_MWORKS_OFFLINE_OVERCLAIM` |
| Codex App visible row used as durable state without packet/registry | `TOOL_CODEX_UI_OVERCLAIM` |
| UE map mutation before reversible write probe | `TOOL_UNSAFE_WRITE_PROBE` |
| unavailable route lacks blocker/resume/retry policy | `TOOL_BLOCKER_INCOMPLETE` |
| fallback route used without downgraded acceptance | `TOOL_FALLBACK_UNDECLARED` |

## Dependency Policy

The checker should return `needs_dependency`, not `pass`, when required reports
are absent:

| Missing Dependency | Why It Matters |
|---|---|
| shared validator envelope | common decision/finding contract not available |
| evidence label doctor | provenance inflation cannot be ruled out |
| blocker packet validator | failed route may not be resumable |
| Candidate B/C/D/E validator | route-specific proof package may be incomplete |
| human-review package checker | manual action may be vague or unsafe |
| worktree/Git validator | Git route may stage unsafe batch |

## Implementation Boundary

The first implementation must be read-only:

- no MCP calls;
- no UE, Fab, Launcher, MWORKS, Sysplorer, or Syslab launch;
- no account-cache inspection;
- no simulation or truth export;
- no Codex conversation creation or dispatch;
- no Git status, staging, commit, push, worktree creation, cleanup, or repair;
- no notification;
- no automatic card rewriting.

It may report exact next safe probes or manual asks, but those remain separate
approved tasks.

## Closeout Rule

A task may close a tool-dependent claim only when its final record states:

1. which capability card was used;
2. what health level was current at closeout;
3. what evidence path supports that level;
4. what claim was allowed;
5. what claim was downgraded, blocked, or deferred;
6. which checker reports were used;
7. what remains unproven.

This prevents a final report from turning partial tool visibility into product
readiness.
