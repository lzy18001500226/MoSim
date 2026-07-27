# Stress Test: UE Scene Truth And RflySim-Like Simulation Product

Date: 2026-05-30
Status: architecture walkthrough draft

## User Task

Use UE/Fab/local scene sources to build map truth, integrate simulation
algorithms, and move toward an RflySim-like product where users can select
maps, algorithms, wind, motor degradation, and experiment tasks.

## Canonical Task Goal

Produce a scene-truth and simulation-product workflow that can:

- classify scene sources;
- prove UE/MCP capability;
- export or validate collision/planning truth;
- provide planning/navigation-ready artifacts;
- integrate SLAM/planning/navigation/control experiments;
- expose experiment controls such as wind and motor degradation;
- record manual review and verification evidence.

## Topology

Use a dynamic task team with early gates.

Initial slices:

| Slice | Owner | Output |
|---|---|---|
| Scene Source Gate | ToolchainMCPAgent + SafetyComplianceAgent | source inventory and route decision |
| UE/MCP Capability Proof | ToolchainMCPAgent | capability card |
| Product Scope | ProductStrategyAgent | P0/P1/P2 product scope |

Conditional slices:

| Slice | Start Condition | Output |
|---|---|---|
| Truth Export Design | capability proof passes | truth export spec |
| Planning Truth Validation | truth export spec exists | validation report |
| Algorithm Integration | planning artifacts defined | FastLIO/planning/nav contract |
| Experiment Controls | simulation runtime scope accepted | wind/degradation control spec |
| Verification | artifacts exist | test/manual review report |
| DevOps | large asset strategy approved | integration and Git policy |
| Knowledge Promotion | accepted route exists | docs/skills/tool lessons |

## Scene Source Gate

Classify each source as:

- local UE project;
- local Vault/Fab asset available on disk;
- Fab account-visible but not downloaded;
- unsupported engine version;
- plugin-only asset;
- manual import required;
- reject/defer.

If Fab automation cannot safely import assets, the route becomes:

```text
manual user import
  -> local project inspection
  -> MCP/tool truth export
```

Do not spend days trying to automate Fab if the route is blocked by GUI/account
constraints.

## Capability Card

UE/MCP capability card must answer:

- can launch or connect to the correct UE version;
- can open the project/map;
- can inspect current level and actors;
- can export collision/navmesh/occupancy truth;
- can modify actors without saving unwanted changes;
- can run with bounded timeout;
- known version/plugin limitations;
- fallback path.

## Truth Acceptance

Rendering is not truth.

Accepted truth artifacts may include:

- collision mesh export;
- navmesh export;
- occupancy grid;
- signed distance field;
- semantic obstacle map;
- coordinate frame definition;
- scale/unit calibration;
- ground-truth path feasibility checks.

## Product Scope

P0:

- select a local scene;
- verify planning truth;
- run one navigation/planning experiment;
- configure wind and motor-degradation parameters;
- save scenario, metrics, and evidence.

P1:

- multiple algorithms;
- scene library index;
- repeatable batch experiments;
- manual visual review UI.

P2:

- cluster execution;
- richer RflySim-like UI;
- automated Fab ingestion;
- large scenario marketplace.

## Blocker Handling

| Blocker | State | Action |
|---|---|---|
| Fab login/import required | gui_required | ask user to import manually, then resume local inspection |
| UE version mismatch | tool_unavailable | record supported versions and decide fallback |
| MCP cannot inspect level | tool_unavailable | fix MCP or switch to manual/export script path |
| collision truth missing | review_required | reject planning claim until truth exists |
| large assets in Git | approval_required | DevOps decides ignore/LFS/staging plan |
| visual scene uncertainty | manual_review_required | request user visual audit |

## Acceptance Matrix

| Claim | Required Evidence |
|---|---|
| scene source usable | source inventory and engine/version compatibility |
| UE/MCP route works | capability card and probe logs |
| map truth valid | exported truth artifact and validation report |
| planning can use scene | coordinate frame and obstacle/navmesh contract |
| algorithm integrated | scenario config, input/output contract, run evidence |
| wind/degradation works | parameter interface and experiment evidence |
| product scope is coherent | P0/P1/P2 scope and non-goals |

## Required Templates

Use:

```text
CoAgent/protocol/templates/ue_scene_truth_capability_card.yaml
CoAgent/protocol/templates/scene_truth_artifact_manifest.yaml
```

The capability card is mandatory before claiming a scene route is usable. It
must record source type, engine/version compatibility, UE/MCP probes, timeout
limits, known limitations, and fallback route.

The truth artifact manifest is mandatory before claiming a map is
planning/navigation ready. It must record collision/navmesh/occupancy/SDF or
semantic artifacts, coordinate frames, validation checks, known exclusions,
manual visual review status, and Git/LFS policy.

Verification must reject any planning claim that substitutes rendering
screenshots or visual review for collision/navmesh/occupancy truth.

## CoAgent Design Gaps Exposed

- Need a scene-source capability-card template. Draft added at
  `CoAgent/protocol/templates/ue_scene_truth_capability_card.yaml`.
- Need a manual-import blocker/resume packet for Fab/UE.
- Need a truth-artifact manifest schema. Draft added at
  `CoAgent/protocol/templates/scene_truth_artifact_manifest.yaml`.
- Need Git policy for large UE assets and generated truth outputs.
- Need a verification rubric separating visual review from planning truth.
