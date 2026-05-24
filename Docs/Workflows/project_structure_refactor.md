# Project Structure Refactor

This project is moving from a competition experiment repository toward a
RflySim-like simulation product. Directory structure must therefore separate
product runtime, MWORKS evidence, Unreal rendering, automation, references, and
generated results.

Do not perform a one-shot tree rewrite. First stabilize path aliases and
documentation, then migrate one ownership group at a time.

## Current Problem

The current top level mixes different ownership classes:

```text
Config/controllers/      controller parameter configs
Models/           project MWORKS/Sysplorer model extensions
References/MWORKS/QuadrotorModel/   official MWORKS case model
Config/planners/         planning configs and small planner modules
Config/scenarios/        experiment scenario configs
Scripts/          batch runners, metrics, plotting, UE tools, docs tools
UE5/           project UE renderer and bridge
References/       vendor docs, cloned repos, specs, scene candidates
Docs/Skills/           project/reference skills
References/Agent/            agent tooling experiments
Docs/Workflows/        operating procedures
Results/          formal results, smoke results, GUI review caches, temp data
```

This was acceptable for rapid prototyping. It is not acceptable for a product
layout because automation, product code, external repos, generated evidence,
and local review caches become indistinguishable.

## Target Product Layout

Target tree:

```text
apps/
  sim_ui/                 future user-facing GUI shell

sim/
  mworks/
    official/             official QuadrotorModel package or pointer
    extensions/           project Sysplorer/Sysblock/Modelica models
  UE5/
    renderer/             project UE renderer project
    bridge/               UE UDP/playback plugin
    scenes/               small project-owned scene adapters only
  runtime/
    bridge_protocols/     packet schemas, UDP/TCP contracts
    replay/               replay adapters

configs/
  Config/controllers/
  Config/planners/
  Config/scenarios/
  vehicles/
  scenes/

src/
  control/
  planning/
  evaluation/
  orchestration/
  visualization/

tools/
  mworks/
  UE5/
  data/
  Docs/
  git/

Scripts/tests/
Docs/
Docs/Design/
Docs/Workflows/
automation/
  skills/
  agents/
  prompts/

external/
  specs/                  lightweight public specs/manuals
  source_repos/            external cloned repos, usually ignored by default
  vendor_assets/           Fab/RflySim/AirSim/UE assets, ignored by default

Results/
  formal/                  report-backed evidence
  review/                  manual GUI review assets
  diagnostics/
  tmp/
```

## Mapping From Current Layout

| Current | Target | Migration Risk |
|---|---|---|
| `Config/controllers/` | `configs/controllers/` | Low. Mostly YAML. |
| `Config/planners/` | `configs/planners/` plus `src/planning/` | Medium. Scripts reference current paths. |
| `Config/scenarios/` | `configs/scenarios/` | Medium. Batch scripts reference current paths. |
| `Models/` | `sim/mworks/extensions/` | High. MWORKS model paths and load scripts may break. |
| `References/MWORKS/QuadrotorModel/` | `sim/mworks/official/QuadrotorModel/` or keep as compatibility alias | High. Many scripts and Sysplorer load paths depend on it. |
| `UE5/MworksUnrealRenderer/` | `sim/UE5/renderer/` | High. UE project paths and scripts depend on it. |
| `UE5/QuadrotorMworksBridge/` | `sim/UE5/bridge/` | High. UE plugin paths and build scripts depend on it. |
| `Scripts/` | split into `tools/*` and `src/orchestration/*` | Medium/high. Tests and docs reference scripts. |
| `Docs/Skills/`, `References/Agent/` | `automation/skills/`, `automation/agents/` | Medium. AGENTS/workflows/config references must update. |
| `References/` | `external/specs`, `external/source_repos`, `external/vendor_assets` | High. Large files and Git ignore rules. |
| `Results/` | keep now; later split `formal/review/diagnostics/tmp` | Medium. Report paths depend on existing evidence. |

## Refactor Phases

### Phase 0: Freeze Current Cleanup

Finish and commit the current Unreal cleanup before moving directories.

Acceptance:

```text
git diff --check
python3 Scripts/UE5/check_unreal_bridge.py
python3 -m py_compile Scripts/UE5/check_unreal_bridge.py Scripts/UE5/check_unreal_s0_s1_readiness.py
```

### Phase 1: Introduce Path Registry

Add a single path registry before moving files:

```text
configs/project_paths.yaml
src/orchestration/project_paths.py
```

It must expose logical names such as:

```text
mworks_official_model
mworks_extensions
controller_configs
planner_configs
scenario_configs
unreal_renderer
unreal_bridge
external_vendor_assets
formal_results
review_results
```

Scripts should read logical paths instead of hardcoding top-level directories.

### Phase 2: Move Low-Risk Configs

Move only low-risk YAML/config directories first:

```text
Config/controllers/ -> configs/controllers/
Config/planners/    -> configs/planners/
Config/scenarios/   -> configs/scenarios/
```

Keep temporary compatibility wrappers or update all references in one commit.

Acceptance:

```text
python3 -m pytest tests
python3 Scripts/quality/check_reference_outputs.py
python3 Scripts/mworks/run_mworks_batch.py --dry-run configs/scenarios/official/*.yaml
```

### Phase 3: Split Scripts

Classify scripts:

```text
tools/mworks/      MWORKS scenario runners, result extraction
tools/UE5/      UE build/open/probe/stream tools
tools/data/        metrics, plotting, replay, event log
tools/Docs/        conversion/indexing docs tools
src/orchestration/ reusable Python modules used by Scripts/tests
```

Do not move scripts that are still referenced by many docs until wrappers or
path aliases exist.

### Phase 4: Move Product Runtimes

Only after Phase 1-3:

```text
Models/                -> sim/mworks/extensions/
References/MWORKS/QuadrotorModel/         -> sim/mworks/official/QuadrotorModel/ or retained as alias
UE5/MworksUnrealRenderer/ -> sim/UE5/renderer/
UE5/QuadrotorMworksBridge/ -> sim/UE5/bridge/
```

This phase must be guarded by MWORKS/UE build and smoke checks. It is not a
documentation-only move.

### Phase 5: Repartition References And Results

External data should be explicit:

```text
external/specs/          small manuals/specs that are useful to cite
external/source_repos/   cloned research/simulator repos, ignored unless audited
external/vendor_assets/  Fab/Epic/RflySim/AirSim assets, ignored by default
```

Results should separate evidence from review caches:

```text
Results/formal/
Results/review/
Results/diagnostics/
Results/tmp/
```

Never move report-backed evidence without updating `Docs/simulation_report.md`,
`Docs/user_manual.md`, and result manifests.

## Naming Rules

1. Product code and runtime adapters live under `src/`, `sim/`, or `apps/`.
2. Configs live under `configs/`.
3. External inputs live under `external/`.
4. Generated outputs live under `Results/`.
5. Agent-only operating material lives under `automation/` or `Docs/Workflows/`.
6. Keep `AGENTS.md` short. Long procedures belong here or in other workflows.
7. Do not create empty future directories.
8. Do not move MWORKS or Unreal project directories without a passing smoke
   check in the same change.

## Immediate Recommendation

Do not start with `Models/`, `References/MWORKS/QuadrotorModel/`, or `UE5/`. Start with:

```text
Phase 0: commit current cleanup
Phase 1: add path registry
Phase 2: migrate Config/controllers/planners/scenarios to configs/
```

This reduces top-level clutter without breaking the heavy MWORKS/UE path
contracts first.
