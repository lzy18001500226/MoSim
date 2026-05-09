# Workflow Index

> Index of repeatable project workflows.

---

## 1. Core Workflows

| Task | Workflow File |
|---|---|
| Debug MCP | `workflows/debug_mcp.md` |
| Translate MathWorks/Simulink patterns to MWORKS | `workflows/translate_mathworks_to_mworks.md` |
| Resolve MWORKS model context | `Skills/Mworks/mworks-model-context/SKILL.md` |
| Produce MWORKS simulation evidence | `Skills/Mworks/mworks-simulation-evidence/SKILL.md` |
| Port MATLAB/Syslab logic | `Skills/Mworks/mworks-syslab-porting/SKILL.md` |
| Operate MCP with minimal impact | `Skills/Mworks/mworks-mcp-operations/SKILL.md` |
| Diagnose runtime/model issues | `Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` |
| Test and review quality gates | `Skills/Mworks/mworks-test-quality/SKILL.md` |
| Prepare report and replay assets | `Skills/Mworks/mworks-report-visualization/SKILL.md` |
| Resolve model context workflow | `workflows/resolve_model_context.md` |
| Produce simulation evidence workflow | `workflows/produce_simulation_evidence.md` |
| Run one simulation | `workflows/run_simulation.md` |
| Read simulation results | `workflows/read_results.md` |
| Calculate metrics | `workflows/calc_metrics.md` |
| Generate report figures | `workflows/generate_report_figures.md` |
| Add a controller | `workflows/add_controller.md` |
| Code review | `workflows/code_review.md` |
| Run tests | `workflows/run_tests.md` |
| Smoke test | `workflows/smoke_test.md` |
| Regression test | `workflows/regression_test.md` |
| Pre-submit check | `workflows/pre_submit_check.md` |

---

## 2. Recommended Development Order

```text
debug_mcp
  → run_simulation
  → read_results
  → calc_metrics
  → generate_report_figures
  → code_review
  → run_tests
  → pre_submit_check
```

---

## 3. Scenario Development Workflow

For every new scenario:

```text
1. Add scenario config.
2. Generate reference trajectory.
3. Run PID baseline if applicable.
4. Run optimized controller.
5. Export raw results.
6. Compute metrics.
7. Generate figures.
8. Update report table.
```

Related files:

```text
workflows/run_simulation.md
workflows/calc_metrics.md
workflows/generate_report_figures.md
```

Official baseline scenarios are tracked under:

```text
scenarios/official/example1_pid_baseline.yaml
scenarios/official/example2_pid_baseline.yaml
scenarios/official/example3_pid_baseline.yaml
```

These map directly to `QuadrotorModel.Examples.Example1/2/3`. When Sysplorer
MCP is available, run these first before custom controllers so the official PID
baseline is reproducible.

---

## 4. Controller Development Workflow

For every new controller:

```text
1. Define controller interface.
2. Implement controller module.
3. Run interface test.
4. Run hover smoke test.
5. Run figure8 short test.
6. Compare with baseline.
7. Save metrics and figures.
8. Update algorithm docs.
```

Related files:

```text
workflows/add_controller.md
workflows/smoke_test.md
workflows/regression_test.md
workflows/code_review.md
```

---

## 5. Report Preparation Workflow

```text
1. Confirm all reported scenarios have metrics.
2. Confirm all figures are saved.
3. Confirm captions and references are ready.
4. Confirm screenshots for installation and MCP are collected.
5. Run pre-submit check.
6. Export user manual PDF.
7. Export simulation report PDF.
8. Record demo video.
```

Related file:

```text
workflows/pre_submit_check.md
```

---

## 6. MCP Troubleshooting Workflow

If tools are missing:

```text
1. Check /mcp.
2. Check codex mcp list --json.
3. Check wrapper scripts.
4. Check ~/.codex/config.toml.
5. Remove Windows-side conflicting MCP config.
6. Restart Codex.
7. Check logs.
```

Related file:

```text
workflows/debug_mcp.md
```

---

## 7. Automation Strategy

Use Codex prompts with:

```text
goal
input file
MCP tool
output path
validation criteria
```

Good example:

```text
按照 workflows/run_simulation.md，使用 Sysplorer MCP 运行 figure8 场景，控制器为 pid_baseline，结果保存到 results/raw/figure8_pid.csv。
```

Bad example:

```text
帮我跑一下仿真。
```
