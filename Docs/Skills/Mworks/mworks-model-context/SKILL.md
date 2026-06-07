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
4. If the request touches Sysplorer modeling modality, use the official reference skills under `Skills/Sysplorer/` only as rule references:

```text
ty-sysplorer-modeling-rules
ty-sysblock-diagram-modeling
ty-sysblock-signal-modeling
modelica-library-workflow
```

5. Prefer Sysplorer MCP over guessing:

```text
activation sentinel / maximized target-window screenshot for live GUI/MCP work
  -> stop and return blocker on demo/login/license/error-report state
session_manager
  -> model_manager
  -> get_components / lookup_component / get_component_ports / get_model_text
  -> get_api_document or get_lib_model_document if unclear
```

Activation/login/license state requires a maximized or foreground screenshot
whose content actually shows the target reusable MWORKS/Sysplorer/Syslab main
window. Background `PrintWindow` captures, helper/proxy windows, screenshots
showing Codex/another application, and minimized-window images are auxiliary
only and cannot prove activation.

## Context Resolution

Before choosing an editing method, classify the target:

| Target type | Editing route |
|---|---|
| Modelica physical plant, wrapper, package, experiment | `.mo` text edit with meaningful `Placement` and `annotation(Line(...))` when graphical review matters |
| Sysblock internal controller diagram | Sysplorer/Sysblock API route with `call_code(mode="run_script")`, `ModelingPy`, `AddComponent`, `ConnectPort`, `SetModelParamValue` |
| Hybrid Modelica + Sysblock | build/check Sysblock first, then instantiate/connect it from the Modelica physical top layer |
| uncertain | inspect model text/components and consult `Skills/Sysplorer/ty-sysplorer-modeling-rules/references/modeling_path_router.md` if present |

| User says | MWORKS action |
|---|---|
| this model / official model | identify `QuadrotorModel` model name or loaded file path |
| this example | inspect `QuadrotorModel.Examples.Example1/2/3` candidates |
| this controller | locate controller component and its input/output ports |
| replace PID | find PID controller block/class and document old/new signal interface |
| selected subsystem | use Sysplorer opened model/component query, not Simulink `gcs/gcb` |
| signal interface | list ports, units, dimensions, signs, sample time or continuous/discrete assumption |
| parameter | query component details and model text before editing |
| graphical Sysblock controller | resolve visible topology, child block hierarchy, ports, behavior blocks, and replacement role |

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
7. For Sysblock topology, prefer official API/`ConnectPort` workflow in `Skills/Mworks/mworks-sysblock-graphical-modeling/SKILL.md`; do not rely on hand-written `.mo` text as the verification source.
8. Do not call `ClearAll`, `ChangeDirectory`, or broad workspace reset APIs for context resolution.
9. For MWORKS/Sysplorer/Syslab department context tasks, reference the latest CoAgentOps 30-minute activation/window patrol when available. Return packets should include `mworks_activation_patrol_reference`, `mworks_activation_patrol_age_minutes` when known, `will_not_click_activation_login=true`, and `live_mworks_touched`; do not turn a context task into repeated activation probing.
10. If no recent patrol exists and the context task needs live MCP/GUI work, run at most one bounded sentinel/API check or return a blocker. If current-turn sentinel/capture evidence is collected, inspect the JSON/capture/window-title evidence and classify `activation_state_observation` and `license_state`.
11. If the patrol or current task evidence sees demo edition, login/activation prompt, authorization failure, GUI error-report dialog, mixed blocking license state, visible unknown blocking state, unavailable tooling, or unknown blocking evidence, stop live context probing and return a `status=blocked` `license_or_login` or GUI blocker. Hidden Qt/browser-proxy/helper windows with no license/error text are risk evidence, not standalone blockers. Do not open a new MWORKS window or click login/activation controls.
12. If context probing becomes live MWORKS graphical review, capture enough phase/foreground evidence to prove the reviewed wiring/layout state and return `mworks_phase_screenshots` plus `mworks_phase_observations`. If activation/license/login/authorization/GUI-error evidence appears mid-task, stop and return a P0 MWORKS infrastructure blocker.

## Failure Handling

| Problem | Action |
|---|---|
| component not found | list top-level components and search model text |
| port mismatch | stop, document expected vs actual ports, do not patch blindly |
| model check fails | save error log, inspect model text, search docs |
| GUI opens | continue using minimal MCP calls; do not close reusable MWORKS windows |
| demo edition / activation lost / login prompt | stop live probing; return blocker with sentinel/background screenshot evidence; PMO sends sparse email alert |
