# Agent Project Operating Layers

> Current MoSim workflow for turning accepted requirements and architecture into
> executable agent work. This file owns layers 3-6 only. Layers 1-2 remain in
> `Docs/Design/需求.md`, `Docs/Design/赛题.md`, `Docs/Design/架构.md`, and
> `Docs/Design/架构/`.

Status: current single-thread workflow, 2026-07-01 CST.

## 1. Scope

Use this file after the startup chain when the task asks how to execute,
tool, guard, or preserve evidence for the current MoSim architecture.

This file must not revive the old visible-thread / CoAgent / R1-R2-R3 dispatch
model. Current MoSim work uses one active Codex thread. Legacy agent material
may be read only for explicit cleanup, audit, or historical trace-back.

## 2. Layer Map

| Layer | Owns | Primary files | Not owned here |
|---|---|---|---|
| 3. Execution | workflow, task goal, run gate, blocker path, output location | this file, `Docs/Workflows/mainline_operations_board.md`, `Docs/Workflows/sunray_ros1_current_runtime_lane.md`, `Docs/Workflows/sunray_ros1_execution_checklist.md`, `Docs/Workflows/run_simulation.md`, `Docs/Workflows/produce_simulation_evidence.md` | product requirements, architecture redesign |
| 4. Tools | capability choice, skill/MCP/script/checker route, tool boundary | `Docs/Index/capability_index.md`, `Docs/Index/api_index.md`, `Docs/Workflows/tooling_assets_governance.md`, `Docs/Skills/`, `Scripts/quality/`, `Scripts/hooks/` | permission by itself |
| 5. Guarantees | hooks, checkers, tests, gates, stop triggers, notification | `Scripts/hooks/README.md`, `Scripts/quality/`, `Scripts/tests/`, `Docs/Workflows/pre_submit_check.md`, this file | runtime success claims |
| 6. Evidence and memory | result bundle, logs, metrics, screenshots, cache, promotion boundary | `Results/`, `PROGRESS.md`, `Docs/Workflows/mainline_operations_board.md`, `Docs/Workflows/session_memory_migration.md`, `Docs/Index/project_work_memory_index.md`, `Docs/Cache/` | chat-only truth |

## 3. Existing Coverage And Gaps

| Layer | Existing coverage | Gap this workflow closes | Deprecated risk to avoid |
|---|---|---|---|
| 3 Execution | Sunray ROS1 lane and checklist define current runtime direction; workflow index lists scenario/controller/report flows | no compact G3-G6 goal contract tying accepted architecture to concrete next gates | returning to old dispatch tickets or treating static docs as progress |
| 4 Tools | capability index, API index, project skills, hook docs, MWORKS/UE/Desktop skills | tools were indexed but not tied to current P0 execution order | raw-scanning every nested `SKILL.md`, guessing APIs, or using UE as control-loop authority |
| 5 Guarantees | native hook, preflight, doctor, quality scripts, evidence gates | hard guardrail vs workflow vs experiment gate needed a short rule | prose-only safety rules, fake point clouds, headless-only acceptance |
| 6 Evidence/memory | Results, board, PROGRESS, session-memory migration, project work memory index | no single rule for what enters project fact vs cache/research | reading old cache/chat as current truth |

## 4. Goal Contracts

### G3 - Execution Layer

Input:

```text
Docs/Design/需求.md
Docs/Design/架构.md
Docs/Workflows/mainline_operations_board.md
topic-specific workflow or source files
```

Output:

```text
local goal
run or edit plan
declared evidence path under Results/
formal runtime run_id under Results/runs/<run_id> when an ExperimentProfile exists
blocker condition
targeted checker or smoke command
```

Acceptance:

- the next action is one executable gate, not a broad ambition;
- the task names the architecture layer being validated;
- source/static checks are not reported as runtime closure;
- a blocker states the missing file, tool, license, window, topic, log, or user
  decision.
- formal runtime gates use `Config/profiles/README.md` and
  `Scripts/quality/prepare_experiment_run.py` / `run_experiment_gate.py` /
  `check_run_evidence.py` when an ExperimentProfile exists; ad hoc result
  folders are for diagnostics or domain-specific review bundles.

Current mainline execution selector:

```text
1. Use Docs/Workflows/mainline_operations_board.md as the current execution
   selector. This workflow explains how to execute a selected task; it does not
   override the board.
2. Treat the frozen ROS1/Sunray runtime baseline as the regression plant:
   px4ctrl, FAST-LIO evaluation, Diff-Planner single-UAV, and Diff-Planner
   three-UAV have evidence baselines on the current board.
3. Do not rerun or retune the frozen runtime baseline unless a scoped
   controller/codegen regression needs A/B evidence.
4. G8/G9/G9.5/G9.6 evidence already recorded on the board must be treated as
   existing evidence, not as automatic next work. Reopen those routes only when
   the board or user explicitly asks for regression, audit, or repair.
5. If the board selects enhancement reopening, start with minimal
   Gazebo-verified L1/AWFF, safety-filter, or fault-allocation work, then move
   accepted enhancements through the MWORKS/codegen evidence chain. Do not
   restart old static-only G10 probes as mainline progress.
6. FAST-LIO through PX4 EKF remains a separate state-source A/B branch. It
   does not erase the frozen runtime plant/planner baseline and must keep
   result groups separated from PX4/MAVROS-fused and Hybrid-Z runs.
7. UE/QGC/frontend display work stays S11/G12+ support unless the current task
   explicitly scopes display or experiment-platform integration.
```

### G4 - Tool Layer

Input:

```text
task goal
Docs/Index/capability_index.md
Docs/Index/api_index.md
task-specific Docs/Skills/*/SKILL.md
```

Output:

```text
selected tool or skill
why it is the right route
forbidden actions
health/preflight command when needed
```

Acceptance:

- existing project-local skill/script/checker is checked before creating a new
  asset;
- live MCP/plugin/GUI actions are separated from read-only inspection;
- MWORKS, ROS1/Sunray, UE, Desktop, Git, and web routes keep their claim
  ceilings;
- unknown APIs are looked up in local/official docs or probed read-only before
  implementation.

Quick route:

| Need | First route |
|---|---|
| current runtime loop | `Docs/Workflows/sunray_ros1_current_runtime_lane.md` |
| step-by-step Sunray execution | `Docs/Workflows/sunray_ros1_execution_checklist.md` |
| capability choice | `Docs/Index/capability_index.md` |
| concrete MCP/API commands | `Docs/Index/api_index.md` |
| hooks/checkers/tools | `Docs/Workflows/tooling_assets_governance.md` |
| MWORKS model/sim evidence | `Docs/Skills/Mworks/*` |
| desktop screenshot/action | `Docs/Skills/Desktop/*` |
| UE display/review | `Docs/Workflows/unreal_renderer.md`, `Docs/Skills/Unreal/*` |

### G5 - Guarantee Layer

Input:

```text
planned command/edit/run
current workflow gate
hook/checker/test list
```

Output:

```text
preflight result
targeted test/checker result
stop or proceed decision
email/blocker when terminal user action is needed
```

Acceptance:

- hard guardrails stay in hooks/checkers/tests, not prose only;
- workflow rules say when to stop but do not claim mechanical enforcement;
- runtime gates reject fake/static/empty point-cloud evidence and UE screenshot
  substitution;
- MWORKS login/license/authorization ambiguity stops engineering work;
- named small-task/goal/gate completion, blocker, or review-required terminal
  states send one sparse Chinese email with a task-specific cooldown key; do
  not email ordinary chat replies or intermediate observations.

Guardrail classes:

| Class | Mechanism | Examples |
|---|---|---|
| hard guardrail | hook/checker/test | outside-project write, destructive Git, secret-risk path, large-file, packet/schema checks |
| workflow gate | current workflow | Sunray lane, MWORKS live gate, UE support boundary, desktop screenshot/action separation |
| experiment acceptance | result/evidence review | nonempty point cloud, trajectory error metrics, RViz screenshot/manifest, logs, raw results |
| human gate | user decision/email | login/license, architecture change, broad deletion, disruptive GUI/runtime action |

### G6 - Evidence And Memory Layer

Input:

```text
run output
logs/metrics/screenshots/manifests
manual review notes
cache/research notes
```

Output:

```text
Results/runs/<run_id>/... for formal ExperimentProfile runtime gates
Results/<domain>/<run_id>/... for diagnostic or domain-specific review bundles
PROGRESS.md newest active entry when useful
board update only when state changes
Docs/Cache/* for research/candidate notes
formal docs only after verification and promotion
```

Acceptance:

- every runtime claim names the evidence path;
- formal runtime claims prefer `RUN_MANIFEST.json`, `runtime_log_manifest.json`,
  `tracking.csv`, `metrics.json`, `threshold_report.json`, and
  `run_gate_report.json` under `Results/runs/<run_id>` when the profile route
  applies;
- screenshots or pretty plots do not replace logs/metrics/raw results;
- cache/research notes remain non-authoritative until promoted;
- old chat/session memory goes through `Docs/Workflows/session_memory_migration.md`;
- legacy ledger is trace-back only and not a current operations board.

Evidence bundle minimums:

| Task type | Minimum evidence |
|---|---|
| Sunray/PX4/MAVROS/px4ctrl runtime | `Results/runs/<run_id>/RUN_MANIFEST.json` when an ExperimentProfile exists; otherwise command log, process/topic state, PX4/MAVROS/px4ctrl logs or metrics, result manifest |
| RViz point-cloud/map review | screenshot or capture manifest, topic/sample proof, nonempty `PointCloud2` summary, frame/TF note |
| FAST-LIO independent evaluation | source dataset/run config, odom/map/log metrics, truth/error or clearly labeled blocker |
| planner baseline | map/source, start/goal, path/trajectory output, collision/trackability report |
| MWORKS model/simulation | model/check/sim result, native result or exported raw data, metrics, source label |
| UE/frontend support | source/static/build/review bundle, screenshot/video when relevant, explicit claim boundary |
| docs/tooling cleanup | changed files, checker output, no runtime success claim |

## 5. Per-Task Operating Loop

Use this loop for non-trivial work:

```text
1. Name local goal and layer.
2. Read the smallest owner files.
3. Select capability/tool route.
4. Declare output/evidence path.
5. Run preflight or read-only probe when risk exists; for profile-backed
   runtime gates, prepare `Results/runs/<run_id>` before live execution.
6. Execute the smallest gate.
7. Validate with checker/test/manifest/review evidence; for profile-backed
   runtime gates, run `Scripts/quality/check_run_evidence.py`.
8. Update board/progress/docs only if state or reusable rules changed.
9. Return evidence path or precise blocker.
```

## 6. Stop Triggers

Stop and ask or return a blocker when:

- the next step would change the accepted architecture or substitute a runtime;
- source boundary cannot be found locally and web/docs lookup does not resolve
  it;
- MWORKS login/license/authorization or unknown GUI blocker appears;
- live ROS/UE/MWORKS scope is not authorized but would be required;
- point cloud, TF, map, or log evidence is empty/static/fake;
- a checker fails on a safety or evidence boundary;
- broad deletion, move, Git mutation, or external path access would be needed.

## 7. Promotion From Cache

`Docs/Cache/design_intake/inbox/20260610_agent_project_operating_layers_and_research_plan.md`
is the source draft promoted into this workflow. It remains useful history, but
this file is the current authority for MoSim layers 3-6.

Future layer changes should land in the owning file:

| Change | Owner |
|---|---|
| execution step or stop trigger | `Docs/Workflows/` task workflow |
| tool route or capability | `Docs/Index/capability_index.md`, `Docs/Index/api_index.md`, or `Docs/Skills/` |
| hard check | `Scripts/hooks/`, `Scripts/quality/`, `Scripts/tests/` |
| evidence layout | this file, domain workflow, or `Results/` manifest schema |
| memory/cache promotion | `Docs/Workflows/session_memory_migration.md` |

Do not put detailed new layer rules into `AGENTS.md` or
`Docs/Workflows/new_conversation_context.md`; leave only short pointers there
when startup behavior truly changes.
