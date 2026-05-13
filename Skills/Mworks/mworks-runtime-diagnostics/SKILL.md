---
name: mworks-runtime-diagnostics
description: Diagnose failed, slow, unstable, or suspicious MWORKS simulations and model runs. Use when results are wrong at a time step, variables are missing, a model fails check/translate/simulate, solver/runtime is slow, controller output looks wrong, or you need a Simulink sldebug/profiler-style workflow adapted to MWORKS.
---

# MWORKS Runtime Diagnostics

Translate Simulink debugging/profiling habits into MWORKS evidence-first diagnostics.

## Triage Order

1. Identify the model, scenario, controller, and expected variable.
2. Run or inspect `check_model`.
3. If structure changed, inspect model text and component ports.
4. Run the smallest targeted simulation that reproduces the issue.
5. Probe result variables and values around the suspicious time.
6. Save the failure as evidence; do not hide unstable results.

## MCP Sequence

```text
session_manager
  -> model_manager(get_components/get_model_text/get_component_ports)
  -> check_model
  -> translate_model if compilation/build detail is needed
  -> simulate_model with shortest useful target_time
  -> result_manager(get_result_variable_info/get_vars_value_at/get_vars_values)
```

## Common Cases

| Problem | Diagnostic |
|---|---|
| missing variable | inspect components/ports and update `docs/index/variable_mapping.md` |
| wrong signal sign | compare model port meaning, coordinate convention, and reference bus |
| unstable controller | preserve raw result and inspect saturation, NaN, mode, motor commands |
| slow simulation | reduce scenario, compare target time, note compile vs run-time symptoms |
| model check failure | inspect source text and library docs before patching |
| solver/runtime issue | record error, time range, model name, controller, and minimal reproduction |

## Outputs

Use the smallest artifact that helps future debugging:

```text
results/test_reports/{case}.jsonl
results/logs/{case}_diagnostics.md
docs/index/variable_mapping.md update
workflow/report note with source label
```

## Do Not

1. Do not guess an equivalent of Simulink `sldebug`; use MWORKS introspection and result probing.
2. Do not claim a GUI plot proves correctness without raw data or metrics.
3. Do not broaden to batch runs until a smoke case reproduces or clears the issue.
