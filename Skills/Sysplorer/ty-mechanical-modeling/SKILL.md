---
name: ty-mechanical-modeling
description: 在 Sysplorer 中构建、修复、验证、评审并打包 TY/同元机械系统模型。仅当提示明确提到 `TYDriveline`、`TYFlexBody`、`TYContact`、`TYMechanics`、`TYMultibody`、`TYDriveline3D` 或 `TYMechanics2D`，或明确要求将 Sysplorer 内置/商业库用于机械任务时使用。这是一个领域附加技能，必须仅在 `ty-sysplorer-modeling-rules` 之后使用。
---

# TY Mechanical Modeling

Use this only as a thin domain add-on to `ty-sysplorer-modeling-rules`. The parent skill owns routing, seven gates, layout timing, repair loop, and delivery evidence.

## Minimal Reading

| Need | Read |
|---|---|
| Requirement classification | `references/requirement-map.md` |
| Component mapping | `references/component-map.md` |
| Parameters | `references/parameter-rules.md` |
| Validation | `references/validation-rules.md` |
| Repair | `references/common-errors.md`, then `references/error-repair-playbook.md` |
| Acceptance | `references/acceptance-checklist.md` |
| Sparse input | `templates/scenarios/user-input-minimum-form.md` |

## Specialized Workflows

- New TY mechanical model: `workflows/build-from-scenario.md`
- Existing model repair: `workflows/repair-existing-model.md`
- Example validation: `workflows/verify-example.md`

## Domain Additions

- Identify task type: new TY mechanical model, repair, example validation, or result review.
- Identify motion dimension: 1D, 2D, or 3D; this drives library choice.
- For multibody models, ensure `TYMultibody.World` or equivalent world/reference component exists.
- For planar closed-loop mechanisms, use and report the cut joint strategy.
- Build the smallest checkable mechanical loop before adding losses, contact, flexible bodies, monitoring, or extra operating cases.
- Query real component parameters before assigning values.
- Verify displacement, velocity, angular velocity, force, torque, reaction force, contact force, penetration, pose, joint variables, constraint reaction, deformation, or modal response as applicable.
- For multibody deliverables, open animation and judge assembly motion, loop closure, body pose, joint motion, interference, and abnormal jumps.

## Repair Priority

Prefer the shortest blocking chain:

`TY library boundary -> world/reference -> structural connection -> parameters -> initialization/constraints -> solver -> result interpretation`

Preserve existing valid structure and return to the failed parent Step/Gate after repair.

## Delivery Additions

In addition to parent delivery evidence, state:

- TY sub-library boundary, selected components, parameter sources, completed verification actions, verified variables, and known risks.
- Substitution reason and expected impact for any TY component substitution.
- Cut joint details for planar closed loops.
- Animation status and animation-based judgment for multibody models.
