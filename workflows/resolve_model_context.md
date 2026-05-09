# Resolve MWORKS Model Context

> Purpose: identify the exact Sysplorer/Modelica/Sysblock model, component, port, parameter, and replacement location before editing or simulating.

## Use When

Use this workflow when a task mentions:

```text
this model
official example
QuadrotorModel
this controller
replace PID
signal interface
component port
model parameter
```

## Inputs

```text
model_name or model_path
component_name if known
intended edit or inspection goal
expected signal interface if known
```

## MCP Sequence

```text
session_manager
  -> model_manager(open/load_file/get_components/get_model_text)
  -> model_manager(get_component_ports / lookup_component)
  -> get_api_document or get_lib_model_document if unclear
  -> check_model when structural assumptions are made
```

## Output

Write findings to the smallest useful place:

```text
docs/index/variable_mapping.md
Design/02_模型接口与运行流程.md
results/logs/{experiment_id}_model_context.md
commit message / task summary
```

## Acceptance

Pass if:

1. Model name or file path is explicit.
2. Target component path is explicit.
3. Inputs, outputs, units/dimensions, and sign conventions are documented when relevant.
4. Replacement location and fallback path are documented before editing.
5. Any structural change is followed by `check_model`.

## Failure Handling

| Failure | Action |
|---|---|
| component not found | list parent components and search model text |
| port mismatch | stop and document expected vs actual interface |
| API unclear | query `get_api_document` before scripting |
| model check fails | save error log and inspect source text |
