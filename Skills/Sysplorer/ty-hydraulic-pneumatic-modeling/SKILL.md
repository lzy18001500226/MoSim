---
name: ty-hydraulic-pneumatic-modeling
description: 在 Sysplorer 中构建、修复、验证、评审并打包 TY 液压、热液压和气动系统模型。仅当提示明确提到 `TYOilMedia`、`TYHydraulics`、`TYHydraulicComponents`、`TYThermalHydraulics`、`TYThermalHydraulicComponents`、`TYGasMedia`、`TYPneumatics`、`TYPneumaticComponents` 或 `TYThermals`，或明确要求将 Sysplorer 内置/商业库用于流体领域任务时使用。这是一个领域附加技能，必须仅在 `ty-sysplorer-modeling-rules` 之后使用。
---

# TY Hydraulic / Pneumatic Modeling

Use this only as a thin domain add-on to `ty-sysplorer-modeling-rules`. The parent skill owns routing, seven gates, layout timing, repair loop, and delivery evidence.

## Minimal Reading

Read only the files needed for the current task:

| Need | Read |
|---|---|
| Requirement classification | `references/requirement-map.md` |
| Library / component mapping | `references/library-selection.md`, `references/component-map.md` |
| Medium selection | `references/media-selection.md` |
| Parameters | `references/parameter-rules.md` |
| Validation | `references/validation-rules.md` |
| Capacitor-resistive topology | `references/capacitor-resistive-check.md` when using `TYHydraulics` / `TYHydraulicComponents` or when check/translate/simulate symptoms suggest fluid capacitance/resistance mismatch |
| Repair | `references/error-repair-playbook.md`, then `references/common-errors.md` |
| Acceptance | `references/acceptance-checklist.md`, `references/output-contract.md` |
| Diagram specifics | `references/diagram-layout-rules.md` when the task includes diagram creation or repair |
| Manual lookup | `references/manual-index.md` only when concise references are insufficient |

## Specialized Workflows

- New model from scenario/table/CSV: `workflows/build-from-scenario.md`
- Existing model or diagram repair: `workflows/repair-existing-model.md`
- Official or enterprise example verification: `workflows/verify-example.md`

## Domain Additions

- Identify task type: build, repair, verify example, result review, or guidance only.
- Pick the correct fluid family before building: hydraulic, thermal-hydraulic, pneumatic, gas media, or thermal support.
- Medium choice is structural. Do not continue with an unspecified or wrong medium when pressure, gas, or temperature behavior matters.
- For hydraulic/pneumatic models, verify pressure, flow, displacement, valve state, actuator direction, and boundary/reference completeness.
- For hydraulic models using `TYHydraulics` or `TYHydraulicComponents`, include the capacitor-resistive topology check before long simulation, and after any topology repair involving valves, pumps, pipes, volumes, cavities, or `UseVolume*` switches.
- For thermal-hydraulic models, verify temperature response and heat-port / thermal-boundary assumptions.
- Treat zero flow under expected actuation, unphysical pressure, reversed displacement, NaN/divergence, and missing temperature response as failed verification.
- For diagram tasks, key instances and key wires must be visible and reviewable; parent Gate 6 still controls layout timing.

## Repair Priority

Prefer the shortest blocking chain:

`source/boundary -> library dependency -> component mapping -> parameters -> topology -> capacitor/resistive topology -> medium -> initialization -> translation -> simulation -> result variables -> diagram annotations`

After repair, return to the failed parent Step/Gate. If topology, parameters, or diagram semantics changed, re-run the affected parent chain.

## Delivery Additions

In addition to parent delivery evidence, state:

- Actual TY libraries used, model name/path, topology summary, medium, parameter assumptions, and unresolved `to confirm` items.
- Capacitor-resistive check status when the model uses `TYHydraulics` / `TYHydraulicComponents` or when this check was part of the repair path.
- Verified variables and pass/fail/no-reference judgment.
- Diagram readability for model-creation or diagram-repair tasks.
