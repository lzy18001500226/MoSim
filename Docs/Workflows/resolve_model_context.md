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
activation sentinel / background screenshot for live MCP/GUI context work
  -> stop on demo/login/license/error-report/visible unknown/unavailable state
session_manager
  -> model_manager(open/load_file/get_components/get_model_text)
  -> model_manager(get_component_ports / lookup_component)
  -> get_api_document or get_lib_model_document if unclear
  -> check_model when structural assumptions are made
```

## Output

Write findings to the smallest useful place:

```text
Docs/Index/variable_mapping.md
Docs/Design/02_模型接口与运行流程.md
Results/model_checks/{model_or_component}/logs/{experiment_id}_model_context.md
commit message / task summary
```

## Acceptance

Pass if:

1. Model name or file path is explicit.
2. Target component path is explicit.
3. Inputs, outputs, units/dimensions, and sign conventions are documented when relevant.
4. Replacement location and fallback path are documented before editing.
5. Any structural change is followed by `check_model`.
6. Live MWORKS context work records `activation_sentinel_before`,
   `background_screenshot_before`, `license_state`,
   `will_not_click_activation_login=true`, and `live_mworks_touched`.

## Failure Handling

| Failure | Action |
|---|---|
| component not found | list parent components and search model text |
| port mismatch | stop and document expected vs actual interface |
| API unclear | query `get_api_document` before scripting |
| model check fails | save error log and inspect source text |
| demo edition / activation lost / login prompt | stop live context probing and return `license_or_login` blocker with sentinel/background screenshot evidence |
| GUI error-report dialog | stop live context probing and return GUI blocker; do not click restart/send-report/close |
