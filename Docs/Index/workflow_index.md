# Workflow Index

> Index of repeatable project workflows.

---

## 1. Core Workflows

| Task | Workflow File |
|---|---|
| Debug MCP | `Docs/Workflows/debug_mcp.md` |
| Operate Unreal MCP | `Docs/Workflows/debug_mcp.md#71-unreal-mcp-local-wrapper`, `Docs/Index/api_index.md#5-unreal-mcp-tools` |
| Inspect Epic/Fab/Launcher scene library | `Docs/Workflows/debug_mcp.md#73-epicfab-library-index-mcp`, `Docs/Workflows/unreal_renderer.md#scene-source-selection`, `Scripts/UE5/epic_library_index.py` |
| Build Unreal/RflySim renderer and scene workflow | `Docs/Workflows/unreal_renderer.md` |
| Project structure refactor toward RflySim-like simulator product | `Docs/Workflows/project_structure_refactor.md` |
| Translate MathWorks/Simulink patterns to MWORKS | `Docs/Workflows/translate_mathworks_to_mworks.md` |
| Resolve MWORKS model context | `Docs/Skills/Mworks/mworks-model-context/SKILL.md` |
| Produce MWORKS simulation evidence | `Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md` |
| Port MATLAB/Syslab logic | `Docs/Skills/Mworks/mworks-syslab-porting/SKILL.md` |
| Operate MCP with minimal impact | `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md` |
| Diagnose runtime/model issues | `Docs/Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` |
| Test and review quality gates | `Docs/Skills/Mworks/mworks-test-quality/SKILL.md` |
| Prepare report and replay assets | `Docs/Skills/Mworks/mworks-report-visualization/SKILL.md` |
| Build graphical Sysblock controller | `Docs/Skills/Mworks/mworks-sysblock-graphical-modeling/SKILL.md`, `Docs/Workflows/build_sysblock_graphical_controller.md` |
| Consult official Sysplorer modeling rules | `Docs/Skills/Sysplorer/ty-sysplorer-modeling-rules`, `Docs/Skills/Sysplorer/ty-sysblock-diagram-modeling`, `Docs/Skills/Sysplorer/ty-sysblock-signal-modeling`, `Docs/Skills/Sysplorer/modelica-library-workflow` |
| Main-agent orchestration | `AGENTS.md#331-parallel-agent-rule`, `Docs/Workflows/agent_orchestration.md` |
| Agent organization operating model | `Docs/Workflows/org_operating_model.md` |
| Current project progress and recovery memory | `PROGRESS.md` |
| Sub-agent WAL / run ledger | `Docs/Workflows/agent_task_ledger.md` |
| Interrupted task resume / WAL recovery | `Docs/Workflows/agent_orchestration.md`, `Docs/Workflows/agent_task_ledger.md` |
| External repository audit | `Docs/Workflows/audit_external_repo.md`, `Scripts/reference/audit_external_repo.py` |
| AirSim external repository batch migration | `Docs/Workflows/agent_orchestration.md#51-airsim-batch-migration-with-nested-agents`, `Docs/Workflows/audit_external_repo.md` |
| Docs/Skills/workflow external repo audit | `Docs/Workflows/audit_external_repo.md`, `Docs/Workflows/agent_orchestration.md#7-skills--workflow-runtime-audits` |
| Three-round learn-and-update audit | `Docs/Workflows/audit_external_repo.md`, `Docs/Workflows/agent_orchestration.md#7-skills--workflow-runtime-audits` |
| Recurring external Docs/skills learning | `Docs/Workflows/agent_orchestration.md#71-recurring-learning-owner`, `Docs/Index/external_learning_index.md` |
| Project doctor / self-check | `Scripts/quality/doctor.py`, `Docs/Workflows/pre_submit_check.md`, `Docs/Workflows/debug_mcp.md` |
| Resolve model context workflow | `Docs/Workflows/resolve_model_context.md` |
| Produce simulation evidence workflow | `Docs/Workflows/produce_simulation_evidence.md` |
| Run one simulation | `Docs/Workflows/run_simulation.md` |
| Read simulation results | `Docs/Workflows/read_results.md` |
| Calculate metrics | `Docs/Workflows/calc_metrics.md` |
| Generate report figures | `Docs/Workflows/generate_report_figures.md` |
| Parallel agent execution | `AGENTS.md#331-parallel-agent-rule`, `Docs/Workflows/agent_orchestration.md`, `Docs/Workflows/unreal_renderer.md#long-running-ue5-reconstruction-queue` |
| Persistent long-running agent task ledger | `Docs/Workflows/agent_task_ledger.md` |
| Review Sunray migration source | `Docs/Index/sunray_migration_index.md` |
| Identify Sunray150 quadrotor parameters from PX4 ULog | `Docs/Workflows/identify_quadrotor_parameters.md` |
| Add a controller | `Docs/Workflows/add_controller.md` |
| Build Sysblock graphical controller | `Docs/Workflows/build_sysblock_graphical_controller.md` |
| Code review | `Docs/Workflows/code_review.md` |
| Run tests | `Docs/Workflows/run_tests.md` |
| Regression test | `Docs/Workflows/regression_test.md` |
| Pre-submit check | `Docs/Workflows/pre_submit_check.md` |

---

Doctor and self-check workflows are cheap preflight gates. They do not replace
WAL review, evidence review, or Git/quality review for long-running delegated
tasks.

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
Docs/Workflows/run_simulation.md
Docs/Workflows/calc_metrics.md
Docs/Workflows/generate_report_figures.md
```

Official baseline scenarios are tracked under:

```text
Config/scenarios/official/example1_pid_baseline.yaml
Config/scenarios/official/example2_pid_baseline.yaml
Config/scenarios/official/example3_pid_baseline.yaml
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
Docs/Workflows/add_controller.md
Docs/Workflows/build_sysblock_graphical_controller.md
Docs/Workflows/regression_test.md
Docs/Workflows/code_review.md
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
Docs/Workflows/pre_submit_check.md
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
Docs/Workflows/debug_mcp.md
```

For graphical system model review, use `Docs/Workflows/run_simulation.md` section
“Direct MCP Review For Graphical System Models”. It records the required load
order, the `1401` duplicate-definition trap, and the known embedded graphical
Sysblock multi-input-port limitation.

Official Sysplorer skills in `Docs/Skills/Sysplorer/` are reference material. Project execution should still go through `Docs/Skills/Mworks/` and `Docs/Workflows/`; consult the official skills when a Sysblock/Modelica/hybrid modeling route is unclear.

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
按照 Docs/Workflows/run_simulation.md，使用 Sysplorer MCP 运行 figure8 场景，控制器为 pid_baseline，结果保存到 Results/official/example3_figure8/official_example3_pid_baseline/raw/official_example3_pid_baseline.csv。
```

Bad example:

```text
帮我跑一下仿真。
```

---

## 8. Parallel Agent Workflow

Use parallel agents for RflySim/Unreal/MWORKS work only when the streams are
independent. The main agent remains responsible for integration and final
verification.

| Stream | Typical Task | Output |
|---|---|---|
| Scene research | Compare RflySim/Fab/Gazebo/AirSim scene sources, license limits, file-size risk | Ranked source list and migration notes |
| RflySim smoke | Run local map, vehicle, Mid360/lidar, collision, and point-cloud checks | Small tool patch, smoke log, pass/fail notes |
| MWORKS evidence | Run controller or scenario checks through Sysplorer/Syslab MCP | `Results/` evidence and metrics |
| Documentation | Update architecture, workflow, and acceptance text | `Docs/Design/`, `Docs/`, `Docs/Workflows/` edits |
| Git/quality | Scan large files, inspect diff, run targeted tests, commit/push | Clean Git state or exact blocker |

Rules:

1. Assign disjoint write sets before spawning agents.
2. Keep only one Git/quality agent active.
3. Research agents should not write files unless explicitly assigned.
4. The main agent must review all returned changes before commit.
5. If an agent finds a license, credential, activation, or destructive-action
   issue, it must stop that stream and report the blocker.

Use `Docs/Workflows/agent_orchestration.md` for the full delegation contract and
`Docs/Workflows/agent_task_ledger.md` for persistent recovery state.

---

## 9. Doctor / Self-Check Workflow

Use this before long Git/reference-import/MCP work or when the session state is
unclear:

```bash
python3 Scripts/quality/doctor.py
```

The doctor is intentionally cheap: it checks the project-local Git lock/status,
Git LFS availability, active agent ledger rows, tracked files over the selected
size limit, key workflow files, and MCP wrapper file presence. Live MCP health
still belongs to `/mcp` and `Docs/Workflows/debug_mcp.md`.
