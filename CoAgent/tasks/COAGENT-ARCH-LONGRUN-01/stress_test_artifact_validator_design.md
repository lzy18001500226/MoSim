# COAGENT-ARCH-LONGRUN-01 Stress-Test Artifact Validator Design

Date: 2026-05-30
Status: design contract for `COAGENT-IMPL-NEXT-06`

## Purpose

PX4 parameter identification and UE scene truth are the two product-adjacent
stress tests that expose whether CoAgent is task-first rather than
department-list-first. Their artifacts must be validated before worker results
can claim simulator parameters, planning truth, or RflySim-like readiness.

This is a design artifact. It does not implement validators, parse PX4 logs,
open UE, call MCP tools, export scene truth, run MWORKS, or create product
evidence.

## Core Rule

```text
stress-test claims are not accepted unless their mandatory artifact templates
are present, internally consistent, and honestly labeled by evidence source
```

A PDF summary, screenshot, or chat explanation cannot replace the required
matrix, capability card, or truth manifest.

## Templates Covered

PX4:

```text
CoAgent/protocol/templates/px4_parameter_identifiability_matrix.yaml
```

UE:

```text
CoAgent/protocol/templates/ue_scene_truth_capability_card.yaml
CoAgent/protocol/templates/scene_truth_artifact_manifest.yaml
```

The validator should operate on instantiated copies inside a proof package or
task result directory, not on the template source files alone.

## Inputs

The future validator should accept:

```text
--candidate candidate_b_px4_parameter|candidate_c_ue_scene_truth
--artifact-root <path>
--mode preflight|post_result|fixtures
--json-output <optional path>
```

`preflight` validates required artifact presence and declared limitations.
`post_result` validates result claims against artifact contents and evidence
labels. `fixtures` runs positive and negative examples.

## PX4 Parameter Artifact Checks

Required artifact sections:

- log/source metadata;
- signal inventory;
- vehicle/spec assumptions;
- parameter rows;
- allowed identifiability category per row;
- method or reason;
- uncertainty/residual fields when estimated or behavior-matched;
- additional data required for non-identifiable rows;
- evidence label per claim;
- review owner and next action.

Allowed parameter categories:

- `directly_observed`
- `estimated`
- `calibrated`
- `assumed`
- `behavior_matched`
- `non_identifiable`

Validation rules:

| Claim | Required Support |
|---|---|
| directly observed | signal path, unit, time window |
| estimated | input signals, method, uncertainty, residual |
| calibrated | simulation tuning record and evidence label |
| assumed | source, user spec, or explicit assumption |
| behavior matched | before/after residual or metric |
| non-identifiable | missing signal/spec reason and required data |

Reject any package that claims all simulator parameters are identifiable from a
single log unless every row has matching signal support and uncertainty.

## UE Scene Truth Artifact Checks

Required capability-card sections:

- scene source type;
- engine/version compatibility;
- project/map path;
- import route and manual steps;
- UE/MCP probe summary;
- reversible edit capability;
- truth export capability;
- timeout limits;
- fallback route;
- known limitations;
- review owner and next action.

Required truth-manifest sections:

- scene/map identity;
- coordinate frame and unit scale;
- artifact list;
- truth type per artifact;
- generation method;
- validation checks;
- planning consumer contract;
- manual visual review status;
- Git/LFS/generated-output policy;
- known exclusions.

Accepted truth types include:

- `collision_mesh`
- `navmesh`
- `occupancy_grid`
- `signed_distance_field`
- `semantic_obstacle_map`
- `coordinate_frame`
- `scale_calibration`
- `path_feasibility_check`

Rendering screenshots and visual review can support manual audit only. They do
not satisfy planning truth readiness by themselves.

## Evidence Label Cross-Checks

The stress-test validator should call or share rules with
`evidence_label_doctor_design.md`.

Minimum labels:

- `design_only`
- `offline_script`
- `manual_review`
- `MWORKS_MCP`
- `MWORKS_GUI`
- `UE_MCP`
- `UE_GUI`
- `Fab_manual_import`

Label inflation must fail. Examples:

- offline residual plot labeled `MWORKS_MCP`;
- screenshot labeled planning truth;
- account-visible Fab asset labeled local imported project;
- design card labeled live UE capability proof.

## Output JSON

The future validator should emit:

```json
{
  "ok": false,
  "candidate": "candidate_c_ue_scene_truth",
  "artifact_root": "Results/coagent_proofs/example",
  "decision": "reject",
  "finding_codes": ["UE_TRUTH_RENDERING_AS_TRUTH"],
  "findings": [
    {
      "code": "UE_TRUTH_RENDERING_AS_TRUTH",
      "severity": "error",
      "path": "truth_manifest.yaml",
      "message": "rendering screenshot cannot satisfy planning truth readiness"
    }
  ],
  "next_action": "add collision/navmesh/occupancy/SDF/semantic truth artifact or mark planning_ready=false"
}
```

Allowed decisions:

- `pass`;
- `pass_with_limitations`;
- `needs_review`;
- `blocked`;
- `reject`.

## Stable Finding Codes

PX4 codes:

| Code | Meaning |
|---|---|
| `PX4_MATRIX_MISSING` | identifiability matrix absent |
| `PX4_SIGNAL_INVENTORY_MISSING` | log signal inventory absent |
| `PX4_UNKNOWN_CATEGORY` | parameter category unsupported |
| `PX4_DIRECT_SIGNAL_MISSING` | directly observed claim lacks signal support |
| `PX4_ESTIMATE_UNCERTAINTY_MISSING` | estimated row lacks uncertainty |
| `PX4_RESIDUAL_MISSING` | estimated or behavior-matched row lacks residual |
| `PX4_ASSUMPTION_SOURCE_MISSING` | assumed row lacks source |
| `PX4_NON_IDENTIFIABLE_REASON_MISSING` | non-identifiable row lacks reason |
| `PX4_ALL_IDENTIFIABLE_OVERCLAIM` | package overclaims identifiability |
| `PX4_SIM_EVIDENCE_MISLABELED` | simulation evidence label inflated |

UE codes:

| Code | Meaning |
|---|---|
| `UE_CAPABILITY_CARD_MISSING` | capability card absent |
| `UE_SOURCE_ROUTE_MISSING` | source/import route unclear |
| `UE_ENGINE_COMPAT_MISSING` | engine/version compatibility absent |
| `UE_PROBE_EVIDENCE_MISSING` | UE/MCP capability claim lacks probe evidence |
| `UE_TRUTH_MANIFEST_MISSING` | truth manifest absent |
| `UE_COORD_FRAME_MISSING` | coordinate frame or scale absent |
| `UE_TRUTH_ARTIFACT_MISSING` | no acceptable planning truth artifact |
| `UE_TRUTH_RENDERING_AS_TRUTH` | screenshot/visual review used as truth |
| `UE_MANUAL_IMPORT_UNRECORDED` | Fab/manual import required but not recorded |
| `UE_LARGE_ASSET_POLICY_MISSING` | large asset/generated output policy absent |

Shared codes:

| Code | Meaning |
|---|---|
| `STRESS_EVIDENCE_LABEL_INVALID` | unsupported evidence label |
| `STRESS_EVIDENCE_LABEL_INFLATED` | label claims stronger evidence than artifact supports |
| `STRESS_REVIEW_OWNER_MISSING` | review owner absent |
| `STRESS_NEXT_ACTION_MISSING` | next action absent |

## Fixture Matrix

PX4 fixtures:

| Fixture | Expected |
|---|---|
| valid matrix-only package with limitations | `pass_with_limitations` |
| all parameters identifiable from unsupported log | `PX4_ALL_IDENTIFIABLE_OVERCLAIM` |
| estimated row without uncertainty | `PX4_ESTIMATE_UNCERTAINTY_MISSING` |
| behavior-matched row without residual | `PX4_RESIDUAL_MISSING` |
| offline result labeled MWORKS_MCP | `PX4_SIM_EVIDENCE_MISLABELED` |

UE fixtures:

| Fixture | Expected |
|---|---|
| capability-only card, planning ready false | `pass_with_limitations` |
| planning ready true with screenshot only | `UE_TRUTH_RENDERING_AS_TRUTH` |
| truth manifest missing coordinate frame | `UE_COORD_FRAME_MISSING` |
| Fab manual import required but no import record | `UE_MANUAL_IMPORT_UNRECORDED` |
| large generated mesh with no Git policy | `UE_LARGE_ASSET_POLICY_MISSING` |

Shared fixtures:

| Fixture | Expected |
|---|---|
| unsupported evidence label | `STRESS_EVIDENCE_LABEL_INVALID` |
| design-only artifact claims live tool proof | `STRESS_EVIDENCE_LABEL_INFLATED` |
| no review owner | `STRESS_REVIEW_OWNER_MISSING` |

## Integration With Other Contracts

- `candidate_b_px4_parameter_proof_package.md` defines the PX4 proof shape.
- `candidate_c_ue_scene_truth_proof_package.md` defines the UE proof shape.
- `verification_gate_hardening.md` defines why these templates are mandatory.
- `evidence_label_doctor_design.md` should enforce evidence-label semantics.
- `common_proof_package_validator_design.md` should call the stress-test
  validator for Candidate B and Candidate C package extensions.
- `operating_metrics_snapshot_design.md` should treat missing stress-test
  artifacts as unsupported product claims when completion is asserted.

## Implementation Boundary

The first validator must be read-only:

- no PX4 log parsing beyond supplied artifact paths;
- no estimator execution;
- no MWORKS/Sysplorer run;
- no UE launch or MCP call;
- no Fab/Launcher/account access;
- no file import or asset movement;
- no Git stage/commit/push;
- no conversation dispatch.

## Design Decision

`COAGENT-IMPL-NEXT-06` should implement artifact validators before product
stress tests can be treated as reliable. The validators should permit honest
partial packages with limitations, but reject overclaims that hide missing
signals, missing scene truth, or inflated evidence labels.
