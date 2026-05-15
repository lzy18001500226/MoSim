---
name: ty-thermofluid-modeling
description: 在 Sysplorer 中构建、修复、验证、评审并打包热流体、换热、空气处理、通风、HVAC 和环境控制模型。仅当提示明确提到 `TYMedia`、`TYThermoFluidSys` 或 `TYAirTreatmentAndVentilation`，或明确要求将 Sysplorer 内置/商业库用于相关热流体、换热、空气处理、通风、HVAC 或环境控制任务时使用。这是一个领域附加技能，必须仅在 `ty-sysplorer-modeling-rules` 之后使用。
---

# TY Thermofluid Modeling

Use this only as a thin domain add-on to `ty-sysplorer-modeling-rules`. The parent skill owns routing, seven gates, layout timing, repair loop, and delivery evidence.

## Minimal Reading

| Need | Read |
|---|---|
| Requirement classification | `references/requirement-map.md` |
| Library / component mapping | `references/library-selection.md`, `references/component-map.md` |
| Media | `references/media-selection.md` |
| Parameters / modeling rules | `references/parameter-rules.md`, `references/modeling-rules.md` |
| Validation | `references/validation-rules.md` |
| Repair | `references/common-errors.md` |
| Acceptance | `references/acceptance-checklist.md`, `references/output-contract.md` |
| Manual lookup | `references/manual-index.md` only when concise references are insufficient |

## Specialized Workflows

- Build from scenario: `workflows/build-from-scenario.md`
- Repair existing model: `workflows/repair-existing-model.md`
- Verify example or existing model: `workflows/verify-example.md`

## Domain Additions

- Identify task type: new build, repair, example validation, or result review.
- Choose media and phase assumptions before committing topology.
- Build the minimum energy/fluid path first, then add controls, sensors, and secondary loops.
- State actual libraries and actual media used.
- Verify pressure, temperature, flow, humidity, enthalpy, heat-transfer rate, compressor power, COP, or user-specified metrics as applicable.
- Treat wrong medium, missing boundary/reference, impossible pressure/temperature, divergence, and unverified key variables as failed verification.
- For diagram tasks, parent Gate 6 still controls layout timing and re-check requirements.

## Repair Priority

Prefer the shortest blocking chain:

`medium selection -> boundary/reference -> topology -> parameters -> discretization/resistance organization -> initialization -> translation -> simulation -> result interpretation`

Preserve existing valid structure and return to the failed parent Step/Gate after repair.

## Delivery Additions

In addition to parent delivery evidence, state:

- Temporary assumptions, media assumptions, remaining risks, unresolved items, and next-step recommendations.
- If delivering a library, state the top-level package and bound dependencies.
