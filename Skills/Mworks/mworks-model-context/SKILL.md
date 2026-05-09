---
name: mworks-model-context
description: Resolve and inspect MWORKS.Sysplorer model context for this quadrotor project. Use when the user says this model, this component, this controller, selected subsystem, official example, QuadrotorModel, model replacement location, signal interface, port, parameter, or asks where to edit a Sysplorer/Modelica/Sysblock model.
---

# MWORKS Model Context

Resolve what model, component, port, parameter, or replacement point the user means before editing or simulating.

## Start Here

1. Read project rules in `AGENTS.md`.
2. Check `docs/index/mathworks_to_mworks_migration.md` if the request sounds like Simulink.
3. Use `docs/mworks/converted/matlab_compat/` only as a migration reference, not as API truth.
4. Prefer Sysplorer MCP over guessing:

```text
session_manager
  -> model_manager
  -> get_components / lookup_component / get_component_ports / get_model_text
  -> get_api_document or get_lib_model_document if unclear
```

## Context Resolution

| User says | MWORKS action |
|---|---|
| this model / official model | identify `QuadrotorModel` model name or loaded file path |
| this example | inspect `QuadrotorModel.Examples.Example1/2/3` candidates |
| this controller | locate controller component and its input/output ports |
| replace PID | find PID controller block/class and document old/new signal interface |
| selected subsystem | use Sysplorer opened model/component query, not Simulink `gcs/gcb` |
| signal interface | list ports, units, dimensions, signs, sample time or continuous/discrete assumption |
| parameter | query component details and model text before editing |

## Required Output

Every model-context task must leave one of these artifacts:

```text
docs/index/variable_mapping.md update
Design/*.md interface note
workflows/*.md procedure update
results/logs/*.md or *.jsonl evidence
model file diff with documented replacement location
```

## Editing Rules

1. Check model text or component ports before editing.
2. Do not silently overwrite official model files.
3. Put project wrappers or experiments under project-owned model/package paths when possible.
4. After structural edits, run `check_model`.
5. If a Modelica/Sysplorer API name is unclear, call `get_api_document`.
6. If a library component meaning is unclear, call `get_lib_model_document`.

## Failure Handling

| Problem | Action |
|---|---|
| component not found | list top-level components and search model text |
| port mismatch | stop, document expected vs actual ports, do not patch blindly |
| model check fails | save error log, inspect model text, search docs |
| GUI opens | continue using minimal MCP calls; do not close reusable MWORKS windows |
