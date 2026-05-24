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
controllers/      controller parameter configs
models/           project MWORKS/Sysplorer model extensions
QuadrotorModel/   official MWORKS case model
planners/         planning configs and small planner modules
scenarios/        experiment scenario configs
scripts/          batch runners, metrics, plotting, UE tools, docs tools
unreal/           project UE renderer and bridge
references/       vendor docs, cloned repos, specs, scene candidates
Skills/           project/reference skills
Agent/            agent tooling experiments
workflows/        operating procedures
results/          formal results, smoke results, GUI review caches, temp data
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
  unreal/
    renderer/             project UE renderer project
    bridge/               UE UDP/playback plugin
    scenes/               small project-owned scene adapters only
  runtime/
    bridge_protocols/     packet schemas, UDP/TCP contracts
    replay/               replay adapters

configs/
  controllers/
  planners/
  scenarios/
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
  unreal/
  data/
  docs/
  git/

tests/
docs/
Design/
workflows/
automation/
  skills/
  agents/
  prompts/

external/
  specs/                  lightweight public specs/manuals
  source_repos/            external cloned repos, usually ignored by default
  vendor_assets/           Fab/RflySim/AirSim/UE assets, ignored by default

results/
  formal/                  report-backed evidence
  review/                  manual GUI review assets
  diagnostics/
  tmp/
```

## Mapping From Current Layout

| Current | Target | Migration Risk |
|---|---|---|
| `controllers/` | `configs/controllers/` | Low. Mostly YAML. |
| `planners/` | `configs/planners/` plus `src/planning/` | Medium. Scripts reference current paths. |
| `scenarios/` | `configs/scenarios/` | Medium. Batch scripts reference current paths. |
| `models/` | `sim/mworks/extensions/` | High. MWORKS model paths and load scripts may break. |
| `QuadrotorModel/` | `sim/mworks/official/QuadrotorModel/` or keep as compatibility alias | High. Many scripts and Sysplorer load paths depend on it. |
| `unreal/MworksUnrealRenderer/` | `sim/unreal/renderer/` | High. UE project paths and scripts depend on it. |
| `unreal/QuadrotorMworksBridge/` | `sim/unreal/bridge/` | High. UE plugin paths and build scripts depend on it. |
| `scripts/` | split into `tools/*` and `src/orchestration/*` | Medium/high. Tests and docs reference scripts. |
| `Skills/`, `Agent/` | `automation/skills/`, `automation/agents/` | Medium. AGENTS/workflows/config references must update. |
| `references/` | `external/specs`, `external/source_repos`, `external/vendor_assets` | High. Large files and Git ignore rules. |
| `results/` | keep now; later split `formal/review/diagnostics/tmp` | Medium. Report paths depend on existing evidence. |

## Refactor Phases

### Phase 0: Freeze Current Cleanup

Finish and commit the current Unreal cleanup before moving directories.

Acceptance:

```text
git diff --check
python3 scripts/check_unreal_bridge.py
python3 -m py_compile scripts/check_unreal_bridge.py scripts/check_unreal_s0_s1_readiness.py
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
controllers/ -> configs/controllers/
planners/    -> configs/planners/
scenarios/   -> configs/scenarios/
```

Keep temporary compatibility wrappers or update all references in one commit.

Acceptance:

```text
python3 -m pytest tests
python3 scripts/check_reference_outputs.py
python3 scripts/run_mworks_batch.py --dry-run configs/scenarios/official/*.yaml
```

### Phase 3: Split Scripts

Classify scripts:

```text
tools/mworks/      MWORKS scenario runners, result extraction
tools/unreal/      UE build/open/probe/stream tools
tools/data/        metrics, plotting, replay, event log
tools/docs/        conversion/indexing docs tools
src/orchestration/ reusable Python modules used by scripts/tests
```

Do not move scripts that are still referenced by many docs until wrappers or
path aliases exist.

### Phase 4: Move Product Runtimes

Only after Phase 1-3:

```text
models/                -> sim/mworks/extensions/
QuadrotorModel/         -> sim/mworks/official/QuadrotorModel/ or retained as alias
unreal/MworksUnrealRenderer/ -> sim/unreal/renderer/
unreal/QuadrotorMworksBridge/ -> sim/unreal/bridge/
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
results/formal/
results/review/
results/diagnostics/
results/tmp/
```

Never move report-backed evidence without updating `docs/simulation_report.md`,
`docs/user_manual.md`, and result manifests.

## Naming Rules

1. Product code and runtime adapters live under `src/`, `sim/`, or `apps/`.
2. Configs live under `configs/`.
3. External inputs live under `external/`.
4. Generated outputs live under `results/`.
5. Agent-only operating material lives under `automation/` or `workflows/`.
6. Keep `AGENTS.md` short. Long procedures belong here or in other workflows.
7. Do not create empty future directories.
8. Do not move MWORKS or Unreal project directories without a passing smoke
   check in the same change.

## Immediate Recommendation

Do not start with `models/`, `QuadrotorModel/`, or `unreal/`. Start with:

```text
Phase 0: commit current cleanup
Phase 1: add path registry
Phase 2: migrate controllers/planners/scenarios to configs/
```

This reduces top-level clutter without breaking the heavy MWORKS/UE path
contracts first.
