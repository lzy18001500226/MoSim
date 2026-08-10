# MoSim Documentation Guide

This directory contains project-owned design, operation, evidence, report, and
reference material. It does not replace the repository [README](../README.md).

## Start Here

| Reader | First path | Then read |
|---|---|---|
| New reviewer | `../README.md` | `Design/赛题.md`, `Design/架构.md`, `Index/simulation_model_structure_index.md` |
| Engineer starting a task | `../AGENTS.md` | `Workflows/new_conversation_context.md`, then only the topic docs named by the current user |
| MWORKS controller task | `Design/架构/01_控制器平台/` | matching `Skills/Mworks/` entry and topic workflow |
| ROS1/Sunray runtime task | `Workflows/sunray_ros1_current_runtime_lane.md` | `Workflows/sunray_ros1_execution_checklist.md` |
| Report or user manual review | `报告/README.md` | `报告/用户手册_正文骨架.md`、`报告/仿真分析报告_正文骨架.md` and the cited evidence bundle |

## Current MoSim And Future CoSim

These two document sets have different responsibilities:

```text
Docs/Design/     Current A8 MoSim architecture, competition scope, interfaces,
                  controller work, evidence requirements, and task roadmap.

Docs/CoSim/      Future multi-vehicle platform blueprint and research.
                  Its three-phase roadmap is preserved future work; it is not
                  a claim that the current MoSim slice is finished.
```

## Directory Map

| Path | Owns | Do not use it for |
|---|---|---|
| `Design/` | stable requirements, architecture, interfaces, algorithm and evidence design | daily progress narration |
| `Workflows/` | repeatable task procedure, inputs, stop conditions, and outputs | historical run logs or report prose |
| `Skills/` | task-family tool guidance and known constraints | routine startup or project status |
| `Index/` | navigation to owners, models, workflows, APIs, and references | duplicate policy or implementation detail |
| `Cache/` | historical plans, superseded docs, research drafts, migration records | current operating rules |
| `MworksDocs/` | curated official MWORKS reference material | project-specific source of truth |
| `报告/` | report sources, figures, templates, and review assets | active runtime evidence by itself |
| `Paper/` | paper/reference writing assets | active engineering workflow |

## Documentation Rules

- One document has one owner and one job. Link to the owner instead of copying
  policy, current status, or experiment conclusions.
- A workflow is for normal project execution and quality gates. A README is for
  people locating and understanding the repository. `Results/` carries evidence.
- Historical material stays readable under `Cache/`, but does not appear in the
  ordinary startup path.
- New external archive batches use the E: root and verification procedure in
  `Workflows/external_archive_policy.md`; `Cache/` is not an archive target.
- Do not create a document for routine progress. Update the owning design,
  workflow, index, result, or board only when its responsibility changes.

Detailed navigation is in `Index/doc_index.md`; repeatable task routing is in
`Index/workflow_index.md`.
