# MathWorks / Simulink to MWORKS Migration Index

> Purpose: reuse mature MATLAB/Simulink agent workflows without pretending MWORKS is MATLAB. Treat MathWorks material as engineering patterns, and verify every API through MWORKS docs or MCP before implementation.

## Source Locations

| Source | Path | Use |
|---|---|---|
| MATLAB agentic toolkit | `Docs/Skills/Matlab/matlab-agentic-toolkit/` | Agent setup patterns, skill catalog style, coding/review/testing workflows |
| MATLAB MCP examples | `Docs/Skills/Matlab/mcp-framework-matlab-production-server/` | MCP wrapper design ideas, function description patterns, tool call discipline |
| MATLAB prompts/rules | `Docs/Skills/Matlab/prompts/`, `Docs/Skills/Matlab/rules/` | Coding standards, performance rules, prompt templates |
| Simulink agentic toolkit | `Docs/Skills/Matlab/simulink-agentic-toolkit/` | Model interaction workflow ideas |
| Simulink skills | `Docs/Skills/Simulink/skills/` | Model context resolution, command-line debugging, profiler analysis ideas |
| Simulink project structure | `Docs/Skills/Simulink/Project-File-Structure-for-Simulink/` | Model/data/doc/test separation pattern |
| MWORKS comparison package | `References/MWORKS高校星火计划资料包/MWORKS与MATLAB功能对照/` | Official MATLAB-to-MWORKS differences and function mapping |

## Converted MWORKS Comparison References

The folder `References/MWORKS高校星火计划资料包/MWORKS与MATLAB功能对照` has been converted into project-local references:

```text
Docs/MworksDocs/converted/matlab_compat/
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
| Simulink Test harness | scenario regression test + metrics threshold | `Docs/Workflows/regression_test.md`, `Docs/Workflows/run_tests.md` |
| MATLAB profiler / timeit | Syslab/Python timing and metrics scripts | explicit timing output, not anecdotal speed claims |
| MATLAB code review skill | project code review workflow | `Docs/Workflows/code_review.md` |

## Rules for Codex

1. Use MathWorks skills as pattern libraries, not as executable truth for MWORKS.
2. Before translating a MATLAB function, check MWORKS/Syslab docs and the MATLAB-to-MWORKS comparison materials.
3. Before translating a Simulink operation, identify whether it belongs in Sysplorer Modelica, Sysblock, Syslab, or project Python.
4. Every translated workflow must end with a project-local artifact: model file, script, scenario YAML, raw CSV, metrics JSON, figure, report paragraph, or test.
5. If a MATLAB/Simulink feature has no MWORKS equivalent, choose a conservative fallback and record the gap in the relevant workflow or report.

## High-Value Skills to Translate First

| Priority | Upstream Skill / Rule | MWORKS Adaptation |
|---|---|---|
| P0 | Simulink interactions | `Docs/Skills/Mworks/mworks-model-context/SKILL.md` |
| P0 | Simulating Simulink models | `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md`, `Docs/Workflows/run_simulation.md`, `Docs/Workflows/read_results.md` |
| P0 | MATLAB coding standards | `Docs/Skills/Mworks/mworks-syslab-porting/SKILL.md`, project Python/Julia script conventions |
| P0 | MATLAB testing | `Docs/Skills/Mworks/mworks-test-quality/SKILL.md`, `Docs/Workflows/regression_test.md`, `Docs/Workflows/run_tests.md` |
| P1 | Simulink debug command line | `Docs/Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` |
| P1 | Solver/profiler analyzer | `Docs/Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` |
| P1 | MATLAB performance optimization | `Docs/Skills/Mworks/mworks-syslab-porting/SKILL.md`, `Docs/Skills/Mworks/mworks-test-quality/SKILL.md` |
| P1 | Report/live-script style presentation | `Docs/Skills/Mworks/mworks-report-visualization/SKILL.md` |
| P2 | MCP wrapper generation | `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md`; only if custom project-local MCP tools are needed later |

## Recommended Next Action

The useful upstream MathWorks/Simulink skills have been collapsed into compact MWORKS project skills under `Docs/Skills/Mworks/`. Do not translate irrelevant upstream skills such as database, RF, wireless, or MATLAB app-building unless a real project feature needs them.
