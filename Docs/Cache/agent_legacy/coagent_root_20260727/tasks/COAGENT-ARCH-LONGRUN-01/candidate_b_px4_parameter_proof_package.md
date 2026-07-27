# COAGENT-ARCH-LONGRUN-01 Candidate B PX4 Parameter Proof Package

Date: 2026-05-30
Status: design blueprint for later PX4 proof

## Purpose

Candidate B is the first product-adjacent proof after Candidate A. It tests
whether CoAgent can turn a PX4 log task into a bounded, evidence-driven
parameter-identification workflow without claiming more than the data supports.

This is design-only. It does not parse a real log, run estimators, call
MWORKS/Sysplorer, create worktrees, or commit results.

## Proof Goal

```text
Given one PX4 log path and vehicle context, produce a parameter-identification
proof package that separates directly observed, estimated, calibrated,
assumed, behavior-matched, and non-identifiable simulator parameters, with
explicit uncertainty, residuals, evidence labels, and blocker packets.
```

## Recommended Future Package Root

```text
Results/coagent_proofs/COAGENT-PROOF-PX4-PARAMETER/
```

## Required Inputs

| File | Producer | Purpose |
|---|---|---|
| `task_charter.yaml` | DispatchAgent | canonical goal, non-goals, appetite, acceptance |
| `context_pack.md` | ContextMemoryAgent | PX4 log, vehicle, MWORKS, and evidence-label context |
| `workflow_graph.yaml` | DispatchAgent | gated flow from log audit to verification |
| `log_inventory.yaml` | Log Audit slice | available signals, windows, units, missing data |
| `method_selection.md` | Method Research slice | candidate estimation/calibration methods and appetite |
| `px4_parameter_identifiability_matrix.yaml` | Identifiability slice | mandatory categorization before estimator or tuning |

The mandatory template is:

```text
CoAgent/protocol/templates/px4_parameter_identifiability_matrix.yaml
```

## Required Dynamic Slices

Start immediately:

| Slice | Owner | Required Output |
|---|---|---|
| Log Audit | task-scoped conversation | `log_inventory.yaml` or input blocker |
| Method Research | task-scoped conversation or bounded subagents | `method_selection.md` |
| Identifiability | task-scoped conversation | `px4_parameter_identifiability_matrix.yaml` |

Start only after gates:

| Slice | Gate | Required Output |
|---|---|---|
| Estimator Implementation | identifiable or weakly identifiable rows exist | estimator result and uncertainty report |
| Simulator Mapping | matrix exists | simulator parameter mapping |
| Simulation Tuning | MWORKS/Sysplorer health and mapping pass | tuning record and evidence labels |
| Verification | artifacts exist | review packet, residual checks, rejected claims |
| DevOps Integration | Verification accepts | integration plan, staged files, Git policy |
| Knowledge Promotion | workflow accepted | reusable docs/skills/update proposal |

## Workflow Graph Shape

```text
charter
  -> context_pack
  -> log_audit
  -> identifiability_matrix
  -> method_selection
  -> estimator_or_calibration_gate
  -> optional_estimator
  -> optional_simulator_mapping
  -> optional_mworks_tuning
  -> verification
  -> closeout
```

Key rule:

`optional_mworks_tuning` cannot start unless a smallest useful Sysplorer/Syslab
MCP health probe passes and the task records an evidence label. Offline scripts
may continue, but their outputs must remain `offline_script`.

## Required Blocker Packets

| Blocker | Use When | Required User Ask |
|---|---|---|
| `input_required` | log path missing, log unreadable, required signal missing | provide log/spec or approve limited scope |
| `auth_or_license_required` | MWORKS/Sysplorer activation or login blocks simulation | reactivate/login, then confirm health probe can rerun |
| `tool_unavailable` | Sysplorer/Syslab MCP unavailable | choose offline-only label or wait for tool repair |
| `review_required` | uncertainty/residuals are too weak | accept limitation, collect new data, or re-scope |
| `manual_review_required` | vehicle specs or assumptions require user confirmation | answer one concrete assumption question |

## Acceptance Rules

Verification must reject:

- claiming all parameters are identifiable without signal support;
- hiding non-identifiable parameters;
- omitting uncertainty for estimated parameters;
- omitting residuals or thresholds for calibrated/behavior-matched parameters;
- labeling offline script output as MWORKS evidence;
- starting simulation tuning while MWORKS/Sysplorer health is unknown;
- treating one overfit log match as general simulator validity.

The proof can pass with limitations if:

- non-identifiable rows are explicit;
- assumptions are named;
- additional required data is listed;
- uncertainty/residuals are reported where estimation/calibration is claimed;
- simulation evidence is labeled honestly.

## Required Outputs

| Output | Meaning |
|---|---|
| `closeout.md` | what parameters were supported, limited, or blocked |
| `review_packet.yaml` | Verification decision and rework if any |
| `trace_eval.yaml` | process metrics, blockers, handoff failures, evidence gaps |
| `context_delta.yaml` | reusable PX4 lesson or stale assumption update |
| `knowledge_promotion.md` | accepted workflow/skill/doc update or rejection |

## Result Interpretation

| Outcome | Meaning | Next Action |
|---|---|---|
| matrix-only pass | CoAgent can classify parameter support but has not tuned simulation | approve estimator or simulation slice |
| estimator pass, no MWORKS | algorithm package works offline only | keep evidence label `offline_script` |
| MWORKS tuning pass | simulator parameter workflow has product evidence | promote workflow and run broader tests |
| input blocker | data is insufficient | ask user for log/spec or accept limited result |
| auth/license blocker | tool route is valid but blocked externally | pause simulation slice and continue docs/research |

## Design Decision

Candidate B should only run after Candidate A packet-chain mechanics are
stable or after the user explicitly accepts packet/transport risk. Its first
gate is the identifiability matrix, not estimator code or simulation tuning.
