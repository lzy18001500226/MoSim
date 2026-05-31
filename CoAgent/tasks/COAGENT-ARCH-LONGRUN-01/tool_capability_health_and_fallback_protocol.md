# Tool Capability Health And Fallback Protocol

Date: 2026-05-30
Status: design contract, not implementation
Owner: ToolchainMCPAgent + SafetyComplianceAgent + VerificationAgent
Problem covered: P13

## Purpose

CoAgent must not treat a tool, MCP server, GUI route, or manual import path as
available because a previous conversation used it or because the user installed
related software. Product work can begin only after the relevant route has a
current capability card, a health gate level, evidence, and a stop/fallback
decision.

This protocol closes the current P13 design gap:

```text
How are MCP/tool failures handled, especially UE/MWORKS/Fab workflows?
```

It is design-only. It does not call MCP tools, open UE or MWORKS, launch Fab,
create conversations, change Codex config, stage Git, or implement a checker.

## Core Rule

```text
tool capability is a gated evidence object, not an assumption
```

Every high-impact task that depends on a tool route must record:

1. what route is needed;
2. what health level is currently proven;
3. what evidence proves that level;
4. what the task may claim at that level;
5. what happens if the route is unavailable, stale, blocked, or unsafe.

## Tool Capability Card

A capability card is a small task-local record. It should live with the proof
package or task packet, not only in chat.

Minimum fields:

```yaml
tool_capability_card:
  card_id: toolcap-<task-id>-<route>
  task_id: COAGENT-ARCH-LONGRUN-01
  route_family: MWORKS_SYSPLORER | MWORKS_SYSLAB | UNREAL_EDITOR |
    EPIC_FAB | CODEX_TRANSPORT | GIT_DEVOPS | EXTERNAL_DOCS | OTHER
  route_name: short human-readable route
  route_owner: department or scoped conversation
  required_for: what downstream work needs this route
  requested_claim: what the task wants to claim if route works
  current_health_level: unavailable | discoverable | read_only |
    write_probe_safe | execution_safe | product_evidence_ready
  evidence_label: design_only | runtime_metadata | manual_review |
    MWORKS_MCP | MWORKS_GUI | UE_MCP | UE_GUI | Fab_manual_import |
    git_metadata | external_reference
  evidence_paths:
    - path or command summary inside project, or redacted external evidence id
  probe_timestamp: ISO-8601 or not_run
  probe_command_or_manual_action: exact smallest probe or manual step
  timeout_seconds: 60 by default unless explicitly approved
  known_limitations:
    - limitation
  approved_operations_at_level:
    - operation allowed from this health level
  forbidden_operations_at_level:
    - operation not allowed from this health level
  fallback_routes:
    - route, health requirement, and claim downgrade
  blocker_policy:
    blocker_type: tool_unavailable | auth_or_license_required | gui_required |
      manual_review_required | approval_required
    user_action_required: exact ask or none
    resume_condition: smallest safe health probe or manual confirmation
    retry_policy: no_retry | retry_once_after_changed_condition |
      circuit_breaker_after_second_failure
  review_owner: VerificationAgent or SafetyComplianceAgent
  stale_after: duration or event that invalidates the card
```

The card must be updated when:

- a tool route fails;
- a route is repaired;
- the task changes from read-only inspection to modification or execution;
- the product claim changes;
- the task crosses from design/offline evidence into tool-backed evidence.

## Health Levels

| Level | Meaning | Allowed Claims | Typical Evidence |
|---|---|---|---|
| `unavailable` | route is missing, cannot start, or failed health probe | route blocked; no product claim | error, missing server, failed launch, blocker |
| `discoverable` | route exists in config or inventory but no current content access | installed/configured only | listed MCP server, executable path, library inventory |
| `read_only` | route can inspect current state without mutation | inventory or state observation | MCP read probe, result variable list, actor list, Git status |
| `write_probe_safe` | bounded reversible write probe is safe on non-critical target | reversible mutation capability only | temp actor create/delete, temp file in project, dry-run Git |
| `execution_safe` | route can run intended operation in a bounded scenario | bounded execution, not full product correctness | check/simulate smoke, scene export smoke, controlled dispatch |
| `product_evidence_ready` | route produced evidence that satisfies the product proof contract | product-specific evidence claim | MWORKS result with variables, UE truth artifact manifest |

No level may be inferred from a stronger-sounding but unrelated signal. For
example, UE rendering does not imply planning truth, and Fab library visibility
does not imply automated import.

## Route Families

### MWORKS / Sysplorer / Syslab

Required when a task claims MWORKS-backed simulation, tuning, result variables,
controller integration, or formal report evidence.

Smallest useful probes:

- MCP server availability with the narrowest health probe;
- `check_model` before simulation;
- simulation smoke only after model check passes;
- read required result variables after simulation.

Stop or downgrade:

| Failure | Decision |
|---|---|
| Sysplorer/Syslab MCP missing or `Tools: (none)` | emit `tool_unavailable`; use offline label only if task allows |
| login, activation, license, or GUI prompt | emit `auth_or_license_required`; stop tool loop |
| model check fails | stop simulation claim; route to runtime diagnostics |
| result variables missing | keep execution evidence, reject quality claim |
| offline script output only | label `offline_script`, never `MWORKS_MCP` |

Product rule:

PX4 parameter tuning may not enter simulation-tuning or report-ready claim
state until MWORKS health is at least `execution_safe`. It may produce
identifiability analysis as `offline_script` or `design_only` with explicit
limitations.

### Unreal Editor / UE MCP

Required when a task claims UE scene inspection, scene modification, truth
export, planning readiness, actor/asset operations, or runtime visualization.

Smallest useful probes:

- editor-side listener health;
- current level summary or actor list;
- reversible actor probe only when current map is safe and non-entry;
- truth-export plan before write/export operations.

Stop or downgrade:

| Failure | Decision |
|---|---|
| UE editor closed or listener unreachable | emit `tool_unavailable`; do file-level planning only |
| current map is Entry/unknown | no write probe; require manual map open or safe map |
| write probe crashes or destabilizes editor | emit blocker and require incident review |
| only screenshot/rendering exists | label visual review only; planning truth is false |
| truth artifacts missing coordinate frame or consumer contract | reject planning readiness |

Product rule:

UE scene work becomes planning-ready only when collision/navmesh/occupancy/SDF,
semantic layers, or an accepted equivalent truth artifact is exported and
recorded in a truth-artifact manifest. Visual rendering and map screenshots
are not planning truth.

### Epic / Fab / Manual Import

Required when a task depends on Fab account library, Launcher-installed assets,
Marketplace project creation, plugin installation, or manual import into a UE
project.

Smallest useful probes:

- inventory visibility or local vault/project scan;
- local editable project/source classification;
- manual import record when automation cannot legally or reliably import;
- UE project read-only probe after manual import.

Stop or downgrade:

| Failure | Decision |
|---|---|
| Fab library visible but not downloadable/importable by automation | use `manual_review_required` or local-project fallback |
| Launcher/account/cache access requires user login | emit `auth_or_license_required`; do not scrape private cache broadly |
| asset supports incompatible UE version only | record unsupported route and fallback |
| asset import is manual | label `Fab_manual_import`, not automated Fab capability |
| no editable local scene source exists | block truth-generation work |

Product rule:

Fab visibility alone proves only source discoverability. It does not prove
automatic download, import, UE compatibility, component invocation, map
modification, or planning truth generation. If Fab automation is blocked, the
approved product route is manual import or local project fallback.

### Codex Transport And Visible Conversations

Required when a task dispatches work to visible department conversations or
relies on resume/packet import.

Smallest useful probes:

- department visibility doctor;
- registered thread row and rollout file check;
- bounded dispatch only after context pack and result path are valid;
- timeout closeout with process cleanup evidence.

Stop or downgrade:

| Failure | Decision |
|---|---|
| registered conversation not visible | run approved registered-thread repair or emit blocker |
| unknown thread id or stale deleted thread | do not repair; emit blocker |
| result packet missing after timeout | emit `transport_timeout` blocker |
| invalid result packet | emit `invalid_result_packet` blocker |
| app/VSCode UI state disagrees with project files | project files win |

Product rule:

Visible conversations are review surfaces and worker surfaces. They are not the
source of truth. Project files, packets, context packs, mailbox records, and
runtime state remain authoritative.

### Git / DevOps Tools

Required when a task stages, commits, merges, handles worktrees, classifies
large imports, or integrates multi-conversation outputs.

Smallest useful probes:

- `git status`;
- scoped diff inventory;
- large-file/generated-output classification;
- worktree binding record before multi-worktree integration.

Stop or downgrade:

| Failure | Decision |
|---|---|
| broad unclassified change set | require inventory-first plan |
| large binary/import without policy | emit `approval_required` |
| destructive action needed | emit blocker with exact target |
| same-file multi-agent overlap | require merge owner and integration plan |
| Git auth push failure | stop after exact error; do not retry blindly |

Product rule:

Git metadata can prove change management, not product behavior. A commit does
not prove simulation, UE truth, or parameter-identification correctness.

### External Docs And Search

Required when a task adopts vendor articles, official docs, papers, or
open-source project ideas as architecture or implementation guidance.

Smallest useful probes:

- source citation and date when information may change;
- problem id mapping;
- adoption proposal record;
- evidence level and promotion target.

Stop or downgrade:

| Failure | Decision |
|---|---|
| broad source summary without problem id | reject or defer |
| unreviewed code copy | require license/security review |
| source claim is temporal or high-risk | verify with current source |
| vendor idea conflicts with project boundary | reject with reopen trigger |

Product rule:

External references are not project policy until accepted through the adoption
proposal lifecycle and promoted into a workflow, skill, checker, or backlog
item.

## Stop / Fallback Decision Table

| Situation | Required State | Allowed Next Action |
|---|---|---|
| route missing or server unavailable | `tool_unavailable` blocker | repair route, choose approved fallback, or continue independent design work |
| auth/license/login needed | `auth_or_license_required` blocker | exact PMO ask, wait for user confirmation, then smallest health probe |
| GUI action required | `gui_required` or `manual_review_required` blocker | user performs/manual reviews, then resume condition runs |
| operation would mutate product state without reversible probe | `approval_required` blocker | request approval or design a safer probe |
| evidence label stronger than health level | reject claim | downgrade label or provide stronger evidence |
| fallback reduces claim strength | record claim downgrade | proceed only with downgraded acceptance criteria |
| repeated failure after retry condition unchanged | circuit breaker | retrospective record plus blocker; no further retries |
| failure is outside the task scope but blocks product claim | blocked product slice | continue safe parallel docs/research only if useful |

## Evidence Label Interaction

The evidence label doctor must reject:

- `MWORKS_MCP` without MWORKS route evidence;
- `UE_MCP` without UE route evidence;
- `Fab_manual_import` without a manual import record;
- `runtime_metadata` presented as product proof;
- `git_metadata` presented as test proof;
- `external_reference` presented as adopted policy;
- screenshots or rendering labeled as planning truth.

## Integration With Proof Packages

Candidate B PX4 packages must include a capability card for MWORKS/Sysplorer
before simulation-tuning claims.

Candidate C UE packages must include:

- scene-source capability card;
- UE/MCP capability card;
- truth artifact manifest;
- fallback record for Fab/manual import/local project route.

Candidate D Git-heavy packages must include Git capability and integration
cards when staging or worktree binding is involved.

Candidate E auth/license interruption packages must include the tool route that
triggered the blocker and the resume health probe.

Candidate A may avoid product tools by design. If a Candidate A workflow graph
contains a tool node, it must fail preflight unless the user explicitly
approves expanding the proof scope.

## Future Checker

Future gated backlog item:

```text
COAGENT-IMPL-NEXT-27: Tool Capability Health Gate Checker
```

The checker should be read-only and validate:

- capability card required fields;
- health level vocabulary;
- route family vocabulary;
- evidence label compatibility;
- stale card detection;
- product claim versus health level;
- blocker/resume fields for failed or unavailable routes;
- fallback claim downgrade;
- proof-package integration for Candidate B/C/D/E.

Stable finding code families:

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

The checker must not open tools, repair MCP servers, create conversations,
download assets, inspect account caches, run simulations, mutate maps, stage
Git, send notifications, or rewrite capability cards automatically.

## Current Design Decision

P13 is now design-baselined:

```text
No product-adjacent task may rely on an unproven tool route. Tool routes must
be represented as capability cards with health levels, evidence labels,
stop/fallback rules, and blocker/resume conditions. Failed routes stop or
downgrade claims instead of triggering open-ended retries.
```

Implementation and live proof remain gated by `COAGENT-IMPL-NEXT-27` and the
relevant Candidate B/C/D/E validators.
