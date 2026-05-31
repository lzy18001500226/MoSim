# Stress Test: PX4 Log To Simulator Parameters

Date: 2026-05-30
Status: architecture walkthrough draft

## User Task

Given a PX4 log, derive simulator parameters and tune the simulation so the
aircraft behavior matches the log as far as the evidence supports.

## Canonical Task Goal

Produce a verified parameter-identification package that states:

- what parameters are directly observed;
- what parameters are estimated from the log;
- what parameters require simulation calibration;
- what parameters are assumed from vehicle specs;
- what parameters are not identifiable from the current data;
- what additional data or manual experiment is required.

## Topology

Use a dynamic task team with gated slice creation.

Initial slices:

| Slice | Conversation Type | Start Condition | Output |
|---|---|---|---|
| Log Audit | scoped conversation | log path and task charter exist | log sufficiency report |
| Method Research | scoped conversation or bounded subagents | log audit scope known | method selection table |
| Identifiability | scoped conversation | log audit initial findings | parameter identifiability matrix |

Conditional slices:

| Slice | Start Condition | Output |
|---|---|---|
| Estimator Implementation | data sufficiency gate passes | estimator code and uncertainty report |
| Simulator Mapping | identifiability matrix exists | simulator parameter mapping |
| Simulation Tuning | MWORKS/Sysplorer available and mapping exists | tuning record and result evidence |
| Verification | estimator/mapping/tuning artifacts exist | verification report |
| DevOps Integration | review accepts artifacts | merged code/docs/results |
| Knowledge Promotion | accepted workflow exists | reusable workflow/skill/doc updates |

## Context Packs

### Shared Context

- task charter;
- log path and data handling rules;
- project control/simulation constraints;
- known vehicle/model assumptions;
- accepted parameter categories.

### Slice Context

Log Audit:

- PX4 log format references;
- expected signal groups;
- unit conventions;
- audit report template.

Method Research:

- only methods matching available signals;
- output table requirement;
- appetite limit.

Estimator:

- selected method;
- allowed parameter categories;
- expected uncertainty output.

Simulation:

- MWORKS/Sysplorer MCP rules;
- simulator parameter interface;
- evidence labeling rules.

## Gate Flow

1. Dispatch creates task charter.
2. ContextMemory creates shared context pack.
3. Log Audit checks data sufficiency.
4. If log is insufficient, task moves to `input_required`.
5. If partial, Method Research and Identifiability proceed with limitations.
6. Estimator starts only for identifiable or weakly identifiable parameters.
7. Simulation tuning starts only after mapping and tool availability checks.
8. Verification rejects any result that hides non-identifiable parameters.

## Blocker Handling

| Blocker | State | User Ask |
|---|---|---|
| missing actuator/control signals | input_required | ask for additional log or accept limited scope |
| missing vehicle specs | input_required | ask for mass/inertia/motor/prop config |
| MWORKS activation lost | auth_required | ask user to reactivate; continue docs/research if possible |
| Sysplorer MCP unavailable | tool_unavailable | stop simulation slice; continue offline-only work with label |
| estimator uncertainty too high | review_required | decide whether to collect new data or mark as calibration-only |

## Acceptance Matrix

| Claim | Required Evidence |
|---|---|
| parameter directly observed | signal path, unit, timestamp window |
| parameter estimated | method, input signals, uncertainty, validation residual |
| parameter calibrated | simulation tuning record and before/after metrics |
| parameter assumed | source or user-provided spec |
| parameter not identifiable | reason and required additional data |
| simulator behavior matches log | MWORKS/Sysplorer evidence or clearly labeled offline demo |

## Required Template

Use:

```text
CoAgent/protocol/templates/px4_parameter_identifiability_matrix.yaml
```

The template is mandatory before estimator implementation or simulation tuning.
It forces each parameter into one of:

- `directly_observed`;
- `estimated`;
- `calibrated`;
- `assumed`;
- `behavior_matched`;
- `non_identifiable`.

It also requires signal inventory, uncertainty, residual thresholds,
additional data requirements, and evidence labels. Verification must reject
any result that claims all parameters are identifiable without matching signal
support.

## Failure Modes And Controls

| Failure | Control |
|---|---|
| agent claims all parameters are identifiable | identifiability gate before estimator |
| research drifts forever | appetite and method selection table |
| simulation gets stuck on activation | auth blocker and resume packet |
| estimator overfits one log | verification requires uncertainty/residuals |
| results cannot be merged | DevOps integration plan and artifact manifest |

## CoAgent Design Gaps Exposed

- Need a reusable `parameter_identifiability_matrix` template. Draft added at
  `CoAgent/protocol/templates/px4_parameter_identifiability_matrix.yaml`.
- Need a task-scoped context-pack generator for log-analysis tasks.
- Need a simulation blocker packet specialized for MWORKS activation/license.
- Need an evidence label checker for `MWORKS_MCP` versus offline demo.
