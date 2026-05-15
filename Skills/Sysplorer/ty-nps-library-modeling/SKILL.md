---
name: ty-nps-library-modeling
description: 使用 Sysplorer 内置商业库 `NPSLibrary` 构建、修复、验证、评审并打包电力电子、电机驱动、源网、故障保护和潮流模型。仅当提示明确提到 `NPSLibrary`，或明确要求将 Sysplorer 内置/商业库用于相关 NPS 任务时使用。仅出现 `Boost`、`Buck`、`DCDC`、`inverter` 或 `motor drive` 等场景词并不足以触发此技能。这是一个领域附加技能，必须仅在 `ty-sysplorer-modeling-rules` 之后使用。
---

# TY NPS Library Modeling

Use this only as a thin domain add-on to `ty-sysplorer-modeling-rules`. The parent skill owns routing, seven gates, layout timing, repair loop, and delivery evidence.

## Minimal Reading

| Need | Read |
|---|---|
| Inputs / contract | `references/standard-input-checklist.md`, `references/input-output-contract.md` |
| Domain rules | `references/nps-domain-rules.md` |
| Component mapping | `references/component-mapping.md` |
| Typical scenarios | `references/nps-typical-scenarios.md` |
| Repair | `references/error-repair-playbook.md`, then `references/nps-common-errors.md` |
| Acceptance | `references/acceptance-checklist.md` |
| Tool mapping | `references/mcp-modeling-toolkit.md` when tool choice is unclear |
| Manual lookup | `references/manual-index.md` only when concise references are insufficient |

## Specialized Workflows

- Scenario build: `workflows/build-from-scenario.md`
- Example/environment verification: `workflows/verify-example.md`
- Existing failed model repair: `workflows/repair-existing-model.md`

## Domain Additions

- Stay inside `NPSLibrary` by default.
- Preserve user-specified topology and key components unless proven incompatible and approved by the user.
- Map main power path first, control chain second; add `Ground / Reference / Powergui / Sensors / Boundary / Result probes` as needed.
- For load-flow tasks, check `LoadFlowBus`, slack/PV/PQ bus definitions, and `Powergui` load-flow initialization.
- For graphical modeling, keep component placement and wiring GUI-editable and reviewable. If GUI-side `call_code` fails, repair the invocation path before considering any fallback.
- For switching/PWM/PLL-dominant models, prefer a discrete baseline unless the scenario requires otherwise; use `step <= T/10` when no stronger rule exists.
- Verify functional correctness, trend reasonableness, numerical acceptability, and reference/engineering expectations.

## Repair Priority

Prefer the shortest blocking chain:

`GUI/call_code invocation -> grounding/reference -> connection completeness -> interface compatibility -> Powergui/load-flow -> initialization -> parameters -> translation -> simulation -> result interpretation`

Do not delete sensors, sources, converters, grounding, or required subsystems just to pass translation.

## Delivery Additions

In addition to parent delivery evidence, state:

- Model structure, component mapping, parameter summary, key assumptions, diagram review, simulation setup, verified variables, and limitations.
- By default, save one final model file; create packaged reports only when explicitly requested.
