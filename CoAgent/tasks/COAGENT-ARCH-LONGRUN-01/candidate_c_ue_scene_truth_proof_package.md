# COAGENT-ARCH-LONGRUN-01 Candidate C UE Scene Truth Proof Package

Date: 2026-05-30
Status: design blueprint for later UE scene-truth proof

## Purpose

Candidate C is the first UE/Fab/product-mainline proof after Candidate A. It
tests whether CoAgent can classify a scene source, prove UE/MCP capability,
separate rendering from planning truth, and produce a truth-artifact package
that downstream planning/navigation algorithms can trust.

This is design-only. It does not launch UE, import Fab assets, modify maps,
export truth, create worktrees, or commit large assets.

## Proof Goal

```text
Given one scene source, produce a scene-truth proof package that classifies the
source, proves or blocks the UE/MCP route, records manual-import requirements,
exports or specifies collision/navmesh/occupancy/SDF truth artifacts, and
states whether the scene is planning/navigation ready.
```

## Recommended Future Package Root

```text
Results/coagent_proofs/COAGENT-PROOF-UE-SCENE-TRUTH/
```

## Required Inputs

| File | Producer | Purpose |
|---|---|---|
| `task_charter.yaml` | DispatchAgent | canonical goal, non-goals, acceptance |
| `context_pack.md` | ContextMemoryAgent | UE project, MCP, Fab/manual-import, Git/LFS, truth context |
| `workflow_graph.yaml` | DispatchAgent | gated flow from source gate to truth validation |
| `scene_source_inventory.yaml` | ToolchainMCPAgent | source type, path, engine, plugin/import route |
| `ue_scene_truth_capability_card.yaml` | ToolchainMCPAgent | UE/MCP capability and fallback decision |
| `scene_truth_artifact_manifest.yaml` | ToolchainMCPAgent + VerificationAgent | truth artifacts, validation, manual review, Git policy |

Mandatory templates:

```text
CoAgent/protocol/templates/ue_scene_truth_capability_card.yaml
CoAgent/protocol/templates/scene_truth_artifact_manifest.yaml
```

## Required Dynamic Slices

Start immediately:

| Slice | Owner | Required Output |
|---|---|---|
| Scene Source Gate | ToolchainMCPAgent + SafetyComplianceAgent | source inventory and route decision |
| Product Scope | ProductStrategyAgent | P0/P1/P2 scope and non-goals |
| UE/MCP Capability Proof | ToolchainMCPAgent | capability card or blocker |

Start only after gates:

| Slice | Gate | Required Output |
|---|---|---|
| Truth Export Design | capability card says route is viable | export spec and artifact plan |
| Planning Truth Validation | artifacts exist or are specified | validation report |
| Algorithm Contract | planning readiness known | FastLIO/planning/nav input-output contract |
| Experiment Controls | product scope accepts runtime controls | wind/degradation parameter contract |
| DevOps Integration | large-asset policy approved | ignore/LFS/staging plan |
| Knowledge Promotion | route accepted or rejected | reusable MCP/UE skill or blocker lesson |

## Workflow Graph Shape

```text
charter
  -> context_pack
  -> scene_source_gate
  -> capability_card
  -> source_route_decision
  -> optional_manual_import_blocker
  -> truth_export_design
  -> truth_artifact_manifest
  -> planning_truth_validation
  -> product_scope_check
  -> verification
  -> closeout
```

Key rule:

Rendering or screenshots are never planning truth. A visual review can support
manual acceptance, but planning readiness requires collision, navmesh,
occupancy grid, SDF, semantic map, path-feasibility, or coordinate-calibration
artifacts with validation status.

## Required Blocker Packets

| Blocker | Use When | Required User Ask |
|---|---|---|
| `gui_required` | Fab login/import or Marketplace GUI action required | import manually, then provide local project/source path |
| `tool_unavailable` | UE/MCP cannot connect, inspect, or export | choose repair route or manual/export-script route |
| `approval_required` | large asset tracking/LFS/staging decision needed | approve Git/LFS/ignore policy |
| `manual_review_required` | visual or product review cannot be automated | answer one concrete review question |
| `review_required` | truth artifact is incomplete or unvalidated | accept limitation or request re-export |

## Acceptance Rules

Verification must reject:

- rendering screenshot used as truth;
- missing coordinate frame or unit scale;
- planning claim without collision/navmesh/occupancy/SDF/semantic/path truth;
- unsupported engine version without fallback;
- Fab manual import required but not recorded;
- large UE asset path prepared for Git without policy;
- MCP write operation that saves unintended map changes;
- product UI/control claims without scenario/config/evidence path.

The proof can pass with limitations if:

- manual import is clearly recorded as a blocker/resume path;
- scene is classified as local, account-visible, unsupported, plugin-only,
  manual-import, or rejected/deferred;
- truth artifacts and missing artifacts are explicit;
- planning readiness is false when required truth is missing;
- manual visual review is separate from planning-truth validation.

## Required Outputs

| Output | Meaning |
|---|---|
| `closeout.md` | source route, capability result, truth status, next action |
| `review_packet.yaml` | Verification decision and rework if any |
| `trace_eval.yaml` | process metrics, blockers, handoff failures, evidence gaps |
| `context_delta.yaml` | reusable UE/MCP/Fab lesson or stale assumption update |
| `knowledge_promotion.md` | accepted skill/workflow/tool update or rejected route |

## Result Interpretation

| Outcome | Meaning | Next Action |
|---|---|---|
| source gate pass only | CoAgent can classify source but not yet prove truth | run capability proof |
| capability pass, no truth | UE/MCP route works but planning readiness not proven | run truth export design |
| truth manifest pass | map is ready for planning consumers within stated limits | start algorithm contract |
| Fab/manual blocker | automation route is not worth forcing | user imports manually, then resume local inspection |
| MCP/tool blocker | toolchain must be repaired before claiming UE automation | fix MCP or use explicit fallback |

## Design Decision

Candidate C should only run after Candidate A packet-chain mechanics are stable
or after the user explicitly accepts packet/transport risk. Its first gate is
scene-source classification and UE/MCP capability, not rendering or map
modification.
