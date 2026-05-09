# MathWorks / Simulink to MWORKS Migration Index

> Purpose: reuse mature MATLAB/Simulink agent workflows without pretending MWORKS is MATLAB. Treat MathWorks material as engineering patterns, and verify every API through MWORKS docs or MCP before implementation.

## Source Locations

| Source | Path | Use |
|---|---|---|
| MATLAB agentic toolkit | `Skills/Matlab/matlab-agentic-toolkit/` | Agent setup patterns, skill catalog style, coding/review/testing workflows |
| MATLAB MCP examples | `Skills/Matlab/mcp-framework-matlab-production-server/` | MCP wrapper design ideas, function description patterns, tool call discipline |
| MATLAB prompts/rules | `Skills/Matlab/prompts/`, `Skills/Matlab/rules/` | Coding standards, performance rules, prompt templates |
| Simulink agentic toolkit | `Skills/Matlab/simulink-agentic-toolkit/` | Model interaction workflow ideas |
| Simulink skills | `Skills/Simulink/skills/` | Model context resolution, command-line debugging, profiler analysis ideas |
| Simulink project structure | `Skills/Simulink/Project-File-Structure-for-Simulink/` | Model/data/doc/test separation pattern |
| MWORKS comparison package | `references/MWORKS高校星火计划资料包/MWORKS与MATLAB功能对照/` | Official MATLAB-to-MWORKS differences and function mapping |

## Converted MWORKS Comparison References

The folder `references/MWORKS高校星火计划资料包/MWORKS与MATLAB功能对照` has been converted into project-local references:

```text
docs/mworks/converted/matlab_compat/
  MWORKS与其他科学计算软件对比.md
  MWORKS简介及与MATLAB的对比.md
  MWORKS与MATLAB在线链接.md
```

Use these files before falling back to raw PDFs or online links.

Do not paste large PDFs, screenshots, or full upstream manuals into `AGENTS.md`. The agent only needs:

1. where to look;
2. what not to assume;
3. how to translate a MATLAB/Simulink habit into an MWORKS/Syslab/Sysplorer action;
4. what MCP command verifies the result.

## Migration Principle

| MATLAB / Simulink Pattern | MWORKS Project Equivalent | Verification |
|---|---|---|
| MATLAB script/function | Syslab Julia script or project Python utility | `syslab.evaluate_julia_code`, `python3 -m py_compile`, result files |
| MATLAB toolbox function | Syslab package or Ty library when available | `syslab.detect_syslab_toolboxes`, `syslab.search_syslab_docs` |
| Simulink block diagram | Sysplorer Modelica/Sysblock model | `sysplorer_mcp.check_model` |
| Simulink selected block / current model | Sysplorer opened model/component query | `model_manager.get_components`, `lookup_component`, `get_model_text` |
| Simulink `sim()` + logsout | Sysplorer `simulate_model` + `result_manager` | raw CSV, metrics JSON, MCP JSONL log |
| Data dictionary / model workspace | scenario YAML + controller YAML + Modelica parameters | QA check, scenario config, git diff |
| Simulink Test harness | scenario smoke test + metrics threshold | `workflows/smoke_test.md`, `workflows/regression_test.md` |
| MATLAB profiler / timeit | Syslab/Python timing and metrics scripts | explicit timing output, not anecdotal speed claims |
| MATLAB code review skill | project code review workflow | `workflows/code_review.md` |

## Rules for Codex

1. Use MathWorks skills as pattern libraries, not as executable truth for MWORKS.
2. Before translating a MATLAB function, check MWORKS/Syslab docs and the MATLAB-to-MWORKS comparison materials.
3. Before translating a Simulink operation, identify whether it belongs in Sysplorer Modelica, Sysblock, Syslab, or project Python.
4. Every translated workflow must end with a project-local artifact: model file, script, scenario YAML, raw CSV, metrics JSON, figure, report paragraph, or test.
5. If a MATLAB/Simulink feature has no MWORKS equivalent, choose a conservative fallback and record the gap in the relevant workflow or report.

## High-Value Skills to Translate First

| Priority | Upstream Skill / Rule | MWORKS Adaptation |
|---|---|---|
| P0 | Simulink interactions | Resolve opened Sysplorer model, component, ports, source text |
| P0 | Simulating Simulink models | Run Sysplorer `check_model`, `simulate_model`, result export |
| P0 | MATLAB coding standards | Syslab Julia/Python coding and data-processing standards |
| P0 | MATLAB testing | Project smoke/regression/metrics tests |
| P1 | Simulink debug command line | Sysplorer model introspection + result-variable probing workflow |
| P1 | Solver profiler analyzer | Solver/runtime diagnostics for long or failed MWORKS simulations |
| P1 | MATLAB performance optimization | Syslab/Python vectorization, preallocation, batch metrics |
| P2 | MCP wrapper generation | Only if we need custom project-local MCP tools later |

## Recommended Next Action

Use the converted comparison references to turn high-value MATLAB/Simulink skills into MWORKS-specific workflows. Start with simulation, result reading, plotting, model introspection, and Syslab coding rules.
