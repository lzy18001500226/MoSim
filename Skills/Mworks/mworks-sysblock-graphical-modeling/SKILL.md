---
name: mworks-sysblock-graphical-modeling
description: Build, repair, validate, or review graphical MWORKS.Sysblock controller block diagrams for this quadrotor project. Use when creating Sysblock controller diagrams, converting equation-form controllers into visible block topology, checking missing wires, repairing red-box components, or proving graphical controller behavior equivalence.
---

# MWORKS Sysblock Graphical Modeling

Use this skill for graphical Sysblock controller work. It is adapted from the official opencode Sysblock/modeling skills, but narrowed to this quadrotor project.

## Scope

- Graphical Sysblock controller diagrams under `models/QuadrotorControllerBlocks/`.
- Hybrid integration where a graphical Sysblock controller is paired with a Modelica plant wrapper.
- Repair of missing connections, red-box components, port mismatch, and behavior-equivalence gaps.

Do not use this for pure Modelica plant modeling, pure report writing, or offline-only Python demos.

## Source Priority

Use these in order:

```text
AGENTS.md
Design/
workflows/build_sysblock_graphical_controller.md
docs/index/api_index.md
docs/index/variable_mapping.md
docs/mworks/converted/
```

The official opencode skills under `C:\Users\HP\.config\opencode\skills` are external references only. Do not copy OAuth/provider config or token files into this repo.

## Non-Negotiable Rules

1. Sysblock topology must be created or repaired through official Sysplorer/Sysblock APIs when available, preferably `call_code(mode="run_script")`.
2. Use `ModelingPy` / official APIs for new graphical topology:
   - `NewModel(..., "Sysblock")`
   - `OpenModel`
   - `AddComponent`
   - `ConnectPort`
   - `SetModelParamValue`
3. Do not treat hand-written `.mo` text alone as a verified graphical Sysblock diagram.
4. Do not use `SetModelText` or text patches as the primary method for Sysblock topology unless you are only repairing generated annotation metadata and the behavior is rechecked afterwards.
5. Use full library component paths and verify concrete block ports before wiring.
6. Every formal controller simulation must have a graphical counterpart that expresses the same structure and time behavior.
7. Equation-form Sysblock models are allowed only as full-plant integration bridges when graphical embedding is blocked by platform/compiler limits. They do not replace the graphical deliverable.

## Required Gates

Before claiming a graphical Sysblock controller is ready:

1. **Context gate**: identify model name, file path, controller role, ports, sample-time/continuous assumption, and replacement location.
2. **Topology gate**: verify visible blocks and wires exist in Sysplorer, not only equations.
3. **Structure gate**: run `scripts/check_sysblock_graphics.py`.
4. **MCP gate**: run `scripts/check_graphical_sysblock_mcp.py` or a targeted `check_model` through Sysplorer MCP.
5. **Behavior gate**: compare against the equation/reference implementation or expected scenario signals.
6. **Evidence gate**: save logs under `results/model_checks/` or the relevant scenario result folder.

## Behavior Elements That Must Be Visible

Expose the controller behaviors that matter for simulation, including:

```text
Saturation / limiter
DeadZone or threshold logic
UnitDelay / discrete integrator / filters
Switch or mode logic
Product / gain / allocation matrix path
fault estimate and efficiency compensation path
reference, feedback, error, command, and debug outputs
```

Small wrapper blocks are acceptable only if their subcomponents also expose meaningful visible topology. Avoid recursive wrapper shells that look wired at the top level but hide empty or identical child diagrams.

## MCP Sequence

Use the smallest sequence that proves the current claim:

```text
session_manager
  -> load_library / model_manager(load_file)
  -> get_api_document or get_lib_model_document if a block/API is unclear
  -> call_code(mode="run_script") for graphical edits
  -> check_model
  -> simulate_model only when needed
  -> result_manager for behavior evidence
```

Keep reusable Sysplorer windows open by default. Do not close them before Git unless the user asks or the window/session is blocking progress.

## Failure Handling

| Symptom | Action |
|---|---|
| red rectangle / diagonal line | resolve missing class/package path, then re-open and check model |
| user sees no wires | verify connections are graphical `ConnectPort`/annotation-visible, not just equations |
| child block is empty | build the child diagram, do not add another wrapper layer |
| API call succeeds but model fails | save JSONL log, inspect ports/classes, repair the smallest failing chain |
| simulation works but diagram is incomplete | mark as equation-bridge evidence, not completed graphical Sysblock |

## Output

State the model file, graphical model name, gates run, logs produced, behavior-equivalence status, and remaining risks.
