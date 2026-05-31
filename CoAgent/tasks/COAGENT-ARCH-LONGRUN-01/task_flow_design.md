# COAGENT-ARCH-LONGRUN-01 Task Flow Design

Date: 2026-05-30
Status: phase 1 draft

## Purpose

This document answers the operational question:

```text
When the user gives one serious task, what exactly happens?
```

It intentionally starts from real MoSim tasks rather than from a generic agent
diagram.

## Universal Flow

### 1. PMO Intake

MainAgent records:

- user request;
- user-visible goal;
- why the task matters;
- expected audit point;
- manual review expectations;
- hard constraints from `AGENTS.md`;
- any explicit user preferences or corrections.

Output:

- candidate task note or direct answer.

Decision:

- if the task is small, handle in main thread;
- if long-running, hand to Dispatch for a canonical task charter.

### 2. Dispatch Shaping

DispatchAgent creates:

- task id;
- canonical task goal;
- task class;
- owner department;
- integration owner;
- review owner;
- non-goals;
- definition of done;
- stop conditions;
- first checkpoint;
- topology.

Output:

- `task_charter`;
- `shared_task_board`;
- runtime task record.

Decision:

- do not create scoped conversations until context pack, result contract, and
  close condition exist.

### 3. Context Pack Construction

ContextMemoryAgent builds:

- shared task context;
- slice-specific context;
- accepted prior decisions;
- excluded stale decisions;
- source path map;
- forbidden assumptions;
- output contract.

Decision:

- if context pack is too large, split the task by slice instead of adding more
  transcript.

### 4. Topology Selection

DispatchAgent selects the smallest viable topology:

| Topology | Use |
|---|---|
| main thread | small, low-risk, no durable handoff needed |
| main thread + short-lived subagents | bounded read-only or review work returning one result |
| one scoped conversation | high-context single-owner long task |
| task team without worktrees | multiple mostly read-only/design slices |
| task team with worktrees | implementation slices need file isolation |
| review board | high-impact design or evidence claim |
| incident response | tool/Git/session/license failure dominates the task |

Before selecting the topology for a serious delegated task, Dispatch must also
classify the task through:

```text
CoAgent/tasks/COAGENT-ARCH-LONGRUN-01/task_intake_to_proof_ladder_decision_table.md
```

The classifier selects the first proof path and first gate:

- Candidate A for architecture mechanics;
- Candidate B for data/parameter identification;
- Candidate C for UE scene truth/productization;
- Candidate D for Git-heavy change;
- Candidate E for auth/license/manual interruption.

Topology follows this proof path. A department is included only if it is needed
for the selected first gate, review, integration, or blocker policy.

### 5. Execution

Each worker conversation receives:

- local objective derived from canonical goal;
- context pack;
- read scope;
- write scope;
- result packet path;
- stop condition;
- review owner;
- forbidden actions.

Workers may use short-lived subagents only for bounded subquestions.

### 6. Communication

Communication uses packets and mailbox items:

- task packet;
- context refresh;
- checkpoint;
- blocker;
- decision required;
- review request;
- result packet;
- integration request;
- closeout packet.

Direct peer communication is allowed only if copied into the coordinator-visible
mailbox.

### 7. Review

Verification, Safety, DevOps, Product Strategy, or PMO review based on risk
class.

Review can return:

- accepted;
- accepted with concerns;
- rework required;
- rejected;
- blocked on human action;
- superseded.

### 8. Integration

DevOpsReleaseAgent integrates only accepted outputs:

- confirms worktree/write-scope;
- checks diff;
- stages in small slices;
- records large-file or LFS decisions;
- runs required checks;
- commits only when scope is clean and approved by project rules.

### 9. Knowledge Promotion

KnowledgeSecretaryAgent promotes stable lessons into:

- architecture docs;
- decision records;
- workflow docs;
- skills;
- hooks;
- doctor checks;
- runtime backlog.

Raw chat is not promoted directly.

## Stress Test A: PX4 Log Parameter Identification

### Intake

User request example:

```text
Here is a PX4 log. Derive simulation parameters and tune the simulator.
```

### Topology

Start with a task team, but do not start all slices at once.

Initial slices:

1. Data Sufficiency / Log Audit
2. Method Research
3. Identifiability Matrix

Conditional slices:

4. Estimator Implementation
5. Simulator Parameter Mapping
6. Simulation Tuning
7. Verification
8. DevOps Integration
9. Knowledge Promotion

### Gate Order

1. Log audit must state available signals, units, timestamps, flight windows,
   excitation, actuator data, and missing data.
2. Identifiability matrix must classify parameters before estimator code is
   trusted.
3. Method research must recommend a bounded method for available data, not a
   generic literature survey.
4. Estimator output must include uncertainty and non-identifiable categories.
5. Simulator mapping must state which parameters can be written directly and
   which require calibration.
6. Simulation tuning must label results as provisional until verified against
   the log.
7. Verification must compare evidence, not merely confirm code ran.

### Required Artifacts

- `log_audit_report`
- `parameter_identifiability_matrix`
  (`CoAgent/protocol/templates/px4_parameter_identifiability_matrix.yaml`)
- `method_selection_table`
- `estimator_result_with_uncertainty`
- `simulator_mapping_table`
- `simulation_tuning_record`
- `verification_report`
- `integration_plan`
- `knowledge_delta`

### Human Intervention

Trigger `input_required` if:

- log lacks actuator/control signals needed for requested parameters;
- vehicle geometry, motor constants, mass/inertia, or controller settings are
  missing and cannot be inferred;
- MWORKS/Sysplorer activation is lost;
- manual simulation visual review is required.

## Stress Test B: UE Scene Truth / RflySim-Like Simulation

### Intake

User request example:

```text
Use downloaded UE/Fab scenes to build map truth, integrate algorithms, and move
toward an RflySim-like simulation product.
```

### Topology

Start with gated task team:

1. Scene Source Gate
2. Toolchain/MCP Capability Proof
3. Scene Truth Export Design
4. Planning-Ready Occupancy/Navmesh Design
5. Runtime Integration Design
6. Algorithm Integration Design
7. Product UI Scope
8. Verification / Manual Review
9. Safety / Large Asset / License Review
10. DevOps Integration

### Gate Order

1. Scene source gate classifies local project files, vault assets, and
   unsupported Fab-only assets.
2. Toolchain proof checks whether UE/MCP can open editor, inspect level, and
   export collision/planning truth.
3. If Fab automation is not feasible, the task explicitly switches to
   user-assisted import or local project files.
4. Scene truth design defines collision, navmesh, occupancy, coordinate frames,
   and export format.
5. Algorithm integration receives truth artifacts, not rendered screenshots.
6. Product UI scope states which RflySim-like controls are P0/P1/P2.
7. Verification checks planning truth, reproducibility, and manual visual audit.

### Required Artifacts

- `scene_source_inventory`
- `ue_mcp_capability_card`
  (`CoAgent/protocol/templates/ue_scene_truth_capability_card.yaml`)
- `truth_export_spec`
- `scene_truth_artifact_manifest`
  (`CoAgent/protocol/templates/scene_truth_artifact_manifest.yaml`)
- `planning_truth_validation_report`
- `algorithm_integration_contract`
- `rflysim_like_product_scope`
- `manual_review_packet`
- `large_asset_git_policy`
- `knowledge_delta`

### Human Intervention

Trigger `manual_review_required` if:

- Fab/Launcher login or asset import needs user GUI action;
- UE editor fails due to missing plugin or version mismatch;
- visual scene review is required;
- map truth cannot be trusted without human inspection.

## Anti-Drift Controls

For any long task:

- first checkpoint must happen before implementation-heavy work;
- every result packet must state unknowns and forbidden claims;
- three repeated failed attempts trigger incident or blocker state;
- research slices have an appetite and output table;
- task goal changes require Dispatch + PMO record;
- accepted decisions update context pack or docs before new slices start.
