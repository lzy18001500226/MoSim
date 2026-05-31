# COAGENT-ARCH-LONGRUN-01 Real Task Execution Walkthroughs

Date: 2026-05-30
Status: design walkthrough, not implementation
Owner: DispatchAgent + ProductStrategyAgent + ToolchainMCPAgent + VerificationAgent

## Purpose

This document turns the abstract CoAgent architecture into concrete execution
walkthroughs for two real MoSim task families:

1. PX4/Sunray150 log-based simulator parameter identification;
2. UE/Fab/local scene truth and RflySim-like productization.

The goal is to answer the operational question:

```text
When the user gives this task, what conversations are created or reused, what
context do they receive, what packets do they exchange, when do they stop, and
how does the work become reviewed, merged, learned, or blocked?
```

This file is the scenario-level composition of:

- `end_to_end_task_operating_runbook.md`
- `task_intake_to_proof_ladder_decision_table.md`
- `candidate_b_px4_parameter_proof_package.md`
- `candidate_c_ue_scene_truth_proof_package.md`
- `context_index_and_assembly_design.md`
- `mailbox_ledger_and_replay_design.md`
- `worktree_git_recovery_validator_design.md`
- `human_review_package_checker_design.md`
- `tool_capability_health_gate_checker_design.md`
- `implementation_approval_gate_design.md`

It is design-only. It does not create conversations, dispatch Codex work,
parse PX4 logs, call UE/MWORKS/Fab/MCP tools, mutate maps, create worktrees,
stage Git, or send notifications.

## Shared Execution Principles

For both walkthroughs:

- the canonical task goal is task outcome, not activity;
- permanent department conversations are capability homes, not the whole task
  team by default;
- task-scoped conversations are created only for high-context, long-running,
  independently reviewable slices;
- disposable subagents are used only inside one conversation for bounded local
  research, review, or code inspection;
- context is assembled from indexed slices, not raw transcript;
- every cross-conversation exchange is a mailbox record plus result packet;
- every blocker has a last safe state, exact resume condition, and review
  owner;
- product claims require evidence labels and tool capability cards;
- Git work starts from inventory and owner binding, not staging.

## Walkthrough A: PX4/Sunray150 Parameter Identification

### User Request Shape

Example request:

```text
Here is a PX4/Sunray150 log. Derive simulator parameters for MoSim and tune
the simulator so the aircraft behavior is credible.
```

### Canonical Task Goal

DispatchAgent writes the task goal as:

```text
Produce a reviewed parameter-identification package that classifies which
simulator parameters are directly observed, estimated, assumed,
behavior-matched, or non-identifiable from the supplied data; records
uncertainty, residuals, missing data, and evidence labels; and defines the
next safe MWORKS tuning step if tool capability exists.
```

Invalid weakened goals:

- read papers about PX4 parameter identification;
- write an estimator script;
- produce "some parameters";
- tune until it looks right;
- open several department conversations.

### Stage A0: Intake And Data Sufficiency Precheck

MainAgent extracts:

- log path or missing-log blocker;
- `.params` export path if available;
- vehicle mass, motor order, prop/ESC/motor model if supplied;
- target simulator parameter interface;
- user tolerance for matrix-only, estimator-only, or MWORKS-tuned outcome;
- whether MWORKS login/license state is known.

If the log or minimum vehicle context is absent, CoAgent creates a human-review
packet with one concrete ask:

```text
Please provide a PX4 .ulg log, .params export if available, measured takeoff
mass, motor order, and motor/prop/ESC information, or approve a limited
matrix-only analysis.
```

No task-scoped worker starts estimator or tuning work before this precheck.

### Stage A1: First Gate And Initial Team

Primary class:

```text
data_parameter_identification
```

First proof path:

```text
Candidate B
```

First gate:

```text
log inventory -> identifiability matrix -> method selection
```

Initial permanent departments:

| Department | Role |
|---|---|
| MainAgent | PMO, user asks, final synthesis |
| DispatchAgent | task charter, workflow graph, mailbox |
| ProductStrategyAgent | parameter appetite and simulator relevance |
| ContextMemoryAgent | context pack and rejected assumptions |
| VerificationAgent | identifiability and evidence-label review |

Task-scoped conversations proposed only after preflight:

| Scoped Conversation | Why It Is A Conversation, Not A Subagent | Output |
|---|---|---|
| `PX4LogAudit` | log inventory can be long, tool/data dependent, and independently reviewable | `log_inventory.yaml` |
| `PX4Identifiability` | parameter classification must persist across later tuning and review | `px4_parameter_identifiability_matrix.yaml` |
| `PX4MethodResearch` | method choices may need local reference/paper review and tradeoffs | `method_selection.md` |

Do not open:

- `MWORKSTuning` until MWORKS capability is at least `execution_safe`;
- `DevOpsIntegration` until reviewed artifacts exist;
- additional research conversations without a problem id.

### Stage A2: Context Pack

ContextMemoryAgent builds a compact context pack with:

- user objective and non-goals;
- supplied log/spec paths;
- parameter categories from
  `CoAgent/protocol/templates/px4_parameter_identifiability_matrix.yaml`;
- known rejected assumption: not all simulator parameters are identifiable from
  one PX4 log;
- evidence-label rules for `offline_script`, `MWORKS_MCP`, `MWORKS_GUI`, and
  `manual_review`;
- MWORKS capability-card requirement before simulation tuning;
- result packet contract and expected output paths.

Context budget rule:

```text
PX4 workers receive the log/context/matrix rules they need, not the entire
CoAgent architecture history.
```

### Stage A3: Workflow Graph

The workflow graph is:

```text
task_charter
  -> context_pack
  -> log_inventory
  -> identifiability_matrix
  -> method_selection
  -> verification_gate_1
  -> optional_estimator
  -> optional_simulator_mapping
  -> optional_mworks_tuning
  -> verification_gate_2
  -> integration_or_hold
  -> knowledge_promotion
  -> closeout
```

Gate rules:

- `optional_estimator` starts only if identifiable or weakly identifiable rows
  exist;
- `optional_simulator_mapping` starts only after the matrix names simulator
  parameters and units;
- `optional_mworks_tuning` starts only after MWORKS tool capability is current;
- `integration_or_hold` starts only after VerificationAgent accepts evidence
  labels and limitations.

### Stage A4: Communication And Contradiction Handling

Every scoped conversation returns one result packet:

| Packet | Required Claim Boundary |
|---|---|
| Log inventory | available signals and missing signals only |
| Identifiability matrix | parameter support class, not tuned values unless proven |
| Method selection | candidate method and assumptions, not final validity |
| Estimator result | offline estimator evidence unless MWORKS was used |
| MWORKS tuning | formal simulation evidence only with capability card and result paths |

If `PX4MethodResearch` says a parameter is estimable but
`PX4Identifiability` marks the required signal missing, Dispatch records a
contradiction:

```text
contradiction_type: evidence_vs_method_claim
resolution_owner: VerificationAgent
next_safe_action: revise method claim or mark parameter weak/non-identifiable
```

The task does not continue into estimator implementation while the
contradiction is open.

### Stage A5: Human Intervention

Common PMO asks:

| Situation | Ask |
|---|---|
| missing mass or motor order | provide exact vehicle mass and motor order, or approve assumed values |
| log lacks actuator/RPM signals | approve limited identification scope or provide stronger log/thrust data |
| MWORKS license/login prompt | reactivate/login, then confirm smallest health probe may rerun |
| weak residual match | accept limitation, collect new data, or re-scope the parameter claim |

Each ask is a human-review packet, not a raw chat note.

### Stage A6: Git And Integration

Before any generated estimator, matrix, figure, or workflow file enters Git:

1. DevOpsReleaseAgent receives a change inventory request;
2. generated outputs, source scripts, docs, and raw data are separated;
3. large logs and native result files remain untracked unless explicitly
   approved;
4. staged slices are ordered: templates/docs first, source scripts second,
   small evidence samples third;
5. raw logs, large binaries, and local GUI outputs are held or ignored.

No broad `git add -A` is allowed.

### Stage A7: Completion Criteria

The task is complete only if closeout states:

- which parameters were directly observed;
- which were estimated and with what uncertainty;
- which were behavior-matched and with what residuals;
- which were assumed and from what source;
- which were non-identifiable and what data would be needed;
- whether MWORKS tuning ran, and with which evidence label;
- what files were integrated, held, ignored, or deferred;
- which lessons were promoted or rejected.

Matrix-only completion is allowed only if the user objective is downgraded in
the closeout and the next tuning task is explicit.

## Walkthrough B: UE/Fab/Local Scene Truth Productization

### User Request Shape

Example request:

```text
Use these Fab/local UE maps in MoSim, generate planning truth, integrate
navigation, and move toward an RflySim-like simulation product.
```

### Canonical Task Goal

DispatchAgent writes:

```text
Produce a reviewed scene-truth package for one selected scene source that
classifies the source route, proves or blocks UE/MCP/manual-import capability,
separates visual rendering from planning truth, records truth artifacts and
limitations, and defines the next safe planning/navigation integration step.
```

Invalid weakened goals:

- list Fab assets;
- open UE;
- show a screenshot;
- create a pretty rendering;
- assume a downloaded Marketplace asset is editable or planning-ready.

### Stage B0: Scene Source Intake

MainAgent records:

- target scene source or selection rule;
- whether source is local project, local Vault/Fab cache, account-visible
  asset, manual import, plugin-only, unsupported engine version, or unknown;
- desired product claim: visual review, scene modification, planning truth,
  navigation demo, or RflySim-like product step;
- user willingness to do manual Fab/Launcher import;
- Git/LFS risk expectations for large assets.

If the source is only account-visible and automation cannot import it, the
first user ask is:

```text
Please manually add or create the selected Fab asset into the local UE project,
then provide the local project/map path for read-only inspection.
```

The task does not claim Fab automation.

### Stage B1: First Gate And Initial Team

Primary class:

```text
scene_truth_productization
```

First proof path:

```text
Candidate C
```

First gate:

```text
scene-source classification -> UE/MCP capability card -> truth manifest
```

Initial permanent departments:

| Department | Role |
|---|---|
| MainAgent | PMO, manual import/review asks, final synthesis |
| DispatchAgent | task charter, workflow graph, mailbox |
| ToolchainMCPAgent | UE/Fab/local route capability and truth artifact plan |
| ProductStrategyAgent | P0/P1/P2 product scope and non-goals |
| VerificationAgent | rendering-versus-truth and planning-readiness review |
| SafetyComplianceAgent | license, GUI, account, and unsafe-mutation blockers |

Task-scoped conversations proposed after preflight:

| Scoped Conversation | Why It Is A Conversation | Output |
|---|---|---|
| `SceneSourceGate` | scene source and import route can branch heavily | `scene_source_inventory.yaml` |
| `UECapabilityGate` | UE/MCP/editor state must be current and separately reviewable | `ue_scene_truth_capability_card.yaml` |
| `TruthArtifactDesign` | planning truth contract has downstream algorithm implications | `scene_truth_artifact_manifest.yaml` |
| `PlanningConsumerContract` | FastLIO/planning/navigation interface should not pollute truth gate | `planning_consumer_contract.md` |

Do not start:

- map mutation before write-probe-safe capability;
- path planning claims before truth artifacts;
- broad Git asset handling before Candidate D inventory.

### Stage B2: Context Pack

ContextMemoryAgent builds:

- user product objective and non-goals;
- source path or source-selection rule;
- UE engine/version/plugin constraints;
- Fab/manual import boundaries;
- tool capability health card schema;
- truth artifact manifest requirements;
- rejected assumption: screenshots/rendering are not planning truth;
- Git large-asset and ignored-output policy;
- result packet and blocker packet contracts.

### Stage B3: Workflow Graph

The workflow graph is:

```text
task_charter
  -> context_pack
  -> scene_source_inventory
  -> ue_or_manual_capability_card
  -> source_route_decision
  -> optional_manual_import_blocker
  -> truth_artifact_design
  -> truth_artifact_manifest
  -> planning_truth_validation
  -> optional_planning_consumer_contract
  -> optional_devops_asset_policy
  -> verification
  -> closeout
```

Gate rules:

- `truth_artifact_design` starts only when source route is known;
- `truth_artifact_manifest` cannot claim readiness without collision/navmesh,
  occupancy grid, SDF, semantic layers, path-feasibility artifact, or accepted
  equivalent;
- `planning_consumer_contract` starts only after truth readiness or limitations
  are explicit;
- `devops_asset_policy` starts before any large source/output enters Git.

### Stage B4: Tool Capability And Manual Import

ToolchainMCPAgent records cards for:

| Route | Minimum Claim |
|---|---|
| Fab account/library | source discoverability only |
| manual import | user-performed source availability |
| UE read-only MCP | current map/actor/source inspection only |
| UE write probe | reversible non-critical mutation only |
| truth export | bounded export operation, not full product correctness |

If Fab is visible but not automatable:

```text
claim: source_discoverable
forbidden_claim: automatic_download_import_or_truth_generation
fallback: user_manual_import_or_local_project
```

If UE is closed or MCP listener fails:

```text
blocker_type: tool_unavailable
resume_condition: smallest UE listener/read-only probe after user opens safe map
safe_parallel_work: product-scope docs and truth manifest schema only
```

### Stage B5: Review And Evidence Boundaries

VerificationAgent rejects:

- screenshot or rendering as planning truth;
- map visual inspection as collision/navmesh proof;
- Fab visibility as import proof;
- UE read-only access as map-modification capability;
- truth artifact without frame, unit scale, map/source id, and consumer
  contract;
- planning algorithm integration before truth readiness or accepted limitation.

Allowed partial outcomes:

| Outcome | Meaning |
|---|---|
| source classified | CoAgent knows what route exists, not planning readiness |
| manual import pending | user action required; no automation claim |
| UE read-only pass | scene can be inspected, not necessarily modified |
| truth design pass | artifact plan exists, export not yet proven |
| truth manifest pass | planning consumers may proceed within stated limits |

### Stage B6: Git And Large Assets

If scene files, generated meshes, truth grids, SDFs, screenshots, or native UE
outputs become part of the work:

1. Candidate D inventory starts before staging;
2. source assets, generated truth, local review screenshots, and code/scripts
   are separated;
3. large binaries require ignore/LFS/hold policy;
4. local review outputs remain untracked unless explicitly approved;
5. map-source imports are not silently committed.

### Stage B7: Completion Criteria

The task is complete only if closeout states:

- selected source and route classification;
- UE/Fab/manual capability card and current health;
- whether manual import occurred or is still blocked;
- truth artifacts produced or explicitly missing;
- planning readiness true/false with reasons;
- coordinate frame/unit/consumer contract status;
- visual review status separate from planning truth;
- Git asset disposition;
- next planning/navigation integration task if ready;
- lessons promoted into MCP/UE/Fab workflows or rejected.

## Cross-Walk: Conversations, Worktrees, And Subagents

| Need | Use | Reason |
|---|---|---|
| one bounded literature/code search | subagent inside a scoped conversation | disposable result is enough |
| log inventory, identifiability, scene gate, UE capability | scoped conversation | output must persist, be reviewed, and may run long |
| PMO user ask | MainAgent only | prevents scattered user prompts |
| final evidence review | VerificationAgent | keeps producer and reviewer separate |
| broad Git/asset integration | DevOpsReleaseAgent plus Candidate D | prevents main-thread Git blockage |
| repeated failure learning | KnowledgeSecretaryAgent plus retrospective record | prevents memory-only fixes |

Worktrees are not mandatory for every task. They become required when:

- the task has broad file writes;
- multiple conversations modify overlapping paths;
- generated assets or large files are involved;
- review needs a clean integration surface;
- Git status is slow, locked, or risky.

## What This Adds Beyond Existing Protocols

Existing protocol files define components. This walkthrough binds them into
task-level operating traces:

- exact dynamic conversations for two real task families;
- first gates and delayed teams;
- context contents and rejected assumptions;
- packet and contradiction rules;
- human ask examples;
- Git disposition and completion criteria;
- forbidden weakened goals.

The remaining gap is implementation and fixture proof, not the scenario design
for how these tasks should move through CoAgent.
