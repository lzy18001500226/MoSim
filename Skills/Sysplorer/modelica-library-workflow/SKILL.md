---
name: modelica-library-workflow
description: 构建、修复、扩展、规范化、评审、本地化并准备交付 Modelica 库或 Modelica 模型。仅在处理具体的库/模型工作流任务时使用此技能，例如包结构规范化、示例/测试、图形修复、本地化、评审或交付准备。这是一个工作流附加技能，必须仅在 `ty-sysplorer-modeling-rules` 之后使用。
---

# Modelica Library Workflow

Use this only as a thin add-on to `ty-sysplorer-modeling-rules`. The parent skill owns routing, seven gates, layout timing, repair loop, and delivery evidence. This skill adds library/package workflow details.

## When To Use

- Use for concrete create, repair, extend, normalize, review, localize, or delivery tasks on a Modelica library or model.
- Use for `TYComponentsTemplate`, similar templates, existing skeletons, package normalization, examples/tests, diagram repair, or Chinese localization.
- Do not use for pure theory, pure API lookup, or broad discussion without a concrete artifact objective.

## Minimal Reading

Read only what the task needs:

| Need | Read |
|---|---|
| Task classification | `references/requirement-mapper.md` |
| Template/top package design | `references/template-package-scheme.md` |
| Cross-domain package names | `references/cross-domain-business-package-strategy.md` |
| Minimum runnable validation | `references/executor-base.md` |
| Static checklist / common mistakes | `references/workflow-checklist.md`, `references/common-errors.md` |
| Acceptance / delivery | `references/acceptance-checklist.md`, `references/input-output-contract.md` |

## Specialized Workflows

Prefer these when they match exactly:

| Workflow | Path |
|---|---|
| Build from template | `workflows/build-from-template.md` |
| Extend existing library | `workflows/extend-existing-library.md` |
| Review existing library | `workflows/review-existing-library.md` |
| Normalize structure | `workflows/normalize-library-structure.md` |
| Chinese localization | `workflows/chinese-localization.md` |
| Repair diagram annotations | `workflows/repair-diagram-annotations.md` |

## Domain Additions

- Keep `package.mo` and `package.order` synchronized.
- Preserve `Interfaces`, `Utilities`, `Sources`, and `Sensors` as shared layers when the template or project structure supports them.
- Keep `Examples` and `Tests` separate: examples show usage, tests verify behavior.
- Do not use official examples as renamed deliverables; use them as reference or validation baselines.
- For diagram-related work, parent Gate 6 still decides layout timing and re-check requirements.

## Delivery Additions

In addition to parent delivery evidence, state:

- Completion level: `plan-complete`, `files-modified`, `structure-level-verified`, or `run-level-verified`.
- Package-structure decisions, common-layer decisions, localization scope, diagram status, validation depth, and remaining risks.
- Use templates only when the user explicitly asks for packaged documentation.
