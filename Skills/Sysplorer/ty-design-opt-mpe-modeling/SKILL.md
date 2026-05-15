---
name: ty-design-opt-mpe-modeling
description: >-
  在 Sysplorer 内通过 DesignOptMpe 做参数设计、MPE 参数估计、优化与标定脚本、`run_script` 实验循环。
  不要用于与 DesignOptMpe 无关的 ModelingPy 通用 API 查询（请用 `get_api_document`），也不要用于纯 Modelica / Sysblock 建模范式任务（请先用 `ty-sysplorer-modeling-rules` 再进入领域技能）。
metadata:
  short-description: DesignOptMpe parameter design, MPE, and optimization guidance
  version: 1.0.0
  managed-by: sysplorer-mcp
---

# DesignOptMpe — parameter design, estimation, and optimization

## Scope

- **In scope**: DesignOpt / MPE / parameter estimation / optimization tasks that require the **DesignOptMpe** Python module inside Sysplorer, experiment loops, and integration with Sysplorer models.
- **Out of scope**: Unrelated ModelingPy surface APIs (use `get_api_document`), pure Modelica / Sysblock modeling execution (use domain skills + `modeling_path_router`).

## Hard rules

1. **Session first**: `session_manager(action="health" | "ensure")` before any `run_script` that touches Sysplorer.
2. **Never** call **`ClearAll`** or **`ChangeDirectory`** from scripts or tools; unload with `model_manager(action="unload")` when needed.
3. DesignOptMpe is **not** documented via the main `Help()` namespace—use **`import` + `ListFunctions()` / `help()`** in `run_script`, plus corpus text in `references/` and **`resources_retrieval`** on corpus `design_opt_mpe_api`.

## Tool map

| Need | Tool / action |
|------|----------------|
| Sysplorer readiness | `session_manager` |
| Run estimation / optimization code | `call_code` (`mode="run_script"`) |
| Long docs, FAQs, API tables | `resources_retrieval` with `sources` including **`design_opt_mpe_api`** |
| Model open / save / unload | `model_manager` |
| Check / translate / simulate affected models | `check_model`, `translate_model`, `simulate_model` |

## Execution loop

1. **Clarify goal**: estimation vs design exploration vs optimization; inputs (measurements, parameters bounds).
2. **Pull references**: skim `references/参数估计使用说明.md` for operational flow; `DesignOptMpe.md` for API ordering; demo notes for runnable examples.
3. **Minimal script**: import module, reproduce smallest failing case, print structured status.
4. **Iterate** with `call_code` stdout/stderr; only then widen scope.

## RAG hint

Call `resources_retrieval(action="corpora")` to confirm `design_opt_mpe_api` paths when manifest is deployed; use returned index paths for `action="search"` when you need full-text lookup beyond this skill.
