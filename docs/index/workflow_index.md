# Workflow Index

> Index of repeatable project workflows.

---

## 1. Core Workflows

| Task | Workflow File |
|---|---|
| Debug MCP | `workflows/debug_mcp.md` |
| Operate Unreal MCP | `workflows/debug_mcp.md#71-unreal-mcp-local-wrapper`, `docs/index/api_index.md#5-unreal-mcp-tools` |
| Build Unreal/RflySim renderer and scene workflow | `workflows/unreal_renderer.md` |
| Translate MathWorks/Simulink patterns to MWORKS | `workflows/translate_mathworks_to_mworks.md` |
| Resolve MWORKS model context | `Skills/Mworks/mworks-model-context/SKILL.md` |
| Produce MWORKS simulation evidence | `Skills/Mworks/mworks-simulation-evidence/SKILL.md` |
| Port MATLAB/Syslab logic | `Skills/Mworks/mworks-syslab-porting/SKILL.md` |
| Operate MCP with minimal impact | `Skills/Mworks/mworks-mcp-operations/SKILL.md` |
| Diagnose runtime/model issues | `Skills/Mworks/mworks-runtime-diagnostics/SKILL.md` |
| Test and review quality gates | `Skills/Mworks/mworks-test-quality/SKILL.md` |
| Prepare report and replay assets | `Skills/Mworks/mworks-report-visualization/SKILL.md` |
| Build graphical Sysblock controller | `Skills/Mworks/mworks-sysblock-graphical-modeling/SKILL.md`, `workflows/build_sysblock_graphical_controller.md` |
| Consult official Sysplorer modeling rules | `Skills/Sysplorer/ty-sysplorer-modeling-rules`, `Skills/Sysplorer/ty-sysblock-diagram-modeling`, `Skills/Sysplorer/ty-sysblock-signal-modeling`, `Skills/Sysplorer/modelica-library-workflow` |
| Main-agent orchestration | `AGENTS.md#331-parallel-agent-rule`, `workflows/agent_orchestration.md` |
| Current project progress and recovery memory | `PROGRESS.md` |
| Sub-agent WAL / run ledger | `workflows/agent_task_ledger.md` |
| Interrupted task resume / WAL recovery | `workflows/agent_orchestration.md`, `workflows/agent_task_ledger.md` |
| External repository audit | `workflows/audit_external_repo.md`, `scripts/audit_external_repo.py` |
| AirSim external repository batch migration | `workflows/agent_orchestration.md#51-airsim-batch-migration-with-nested-agents`, `workflows/audit_external_repo.md` |
| Skills/workflow external repo audit | `workflows/audit_external_repo.md`, `workflows/agent_orchestration.md#7-skills--workflow-runtime-audits` |
| Three-round learn-and-update audit | `workflows/audit_external_repo.md`, `workflows/agent_orchestration.md#7-skills--workflow-runtime-audits` |
| Recurring external docs/skills learning | `workflows/agent_orchestration.md#71-recurring-learning-owner`, `docs/index/external_learning_index.md` |
| Project doctor / self-check | `scripts/doctor.py`, `workflows/pre_submit_check.md`, `workflows/debug_mcp.md` |
| Resolve model context workflow | `workflows/resolve_model_context.md` |
| Produce simulation evidence workflow | `workflows/produce_simulation_evidence.md` |
| Run one simulation | `workflows/run_simulation.md` |
| Read simulation results | `workflows/read_results.md` |
| Calculate metrics | `workflows/calc_metrics.md` |
| Generate report figures | `workflows/generate_report_figures.md` |
| Parallel agent execution | `AGENTS.md#331-parallel-agent-rule`, `workflows/agent_orchestration.md`, `workflows/unreal_renderer.md#long-running-ue5-reconstruction-queue` |
| Persistent long-running agent task ledger | `workflows/agent_task_ledger.md` |
| Review Sunray migration source | `docs/index/sunray_migration_index.md` |
| Identify Sunray150 quadrotor parameters from PX4 ULog | `workflows/identify_quadrotor_parameters.md` |
| Add a controller | `workflows/add_controller.md` |
| Build Sysblock graphical controller | `workflows/build_sysblock_graphical_controller.md` |
| Code review | `workflows/code_review.md` |
| Run tests | `workflows/run_tests.md` |
| Regression test | `workflows/regression_test.md` |
| Pre-submit check | `workflows/pre_submit_check.md` |

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
workflows/build_sysblock_graphical_controller.md
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

For graphical system model review, use `workflows/run_simulation.md` section
“Direct MCP Review For Graphical System Models”. It records the required load
order, the `1401` duplicate-definition trap, and the known embedded graphical
Sysblock multi-input-port limitation.

Official Sysplorer skills in `Skills/Sysplorer/` are reference material. Project execution should still go through `Skills/Mworks/` and `workflows/`; consult the official skills when a Sysblock/Modelica/hybrid modeling route is unclear.

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
按照 workflows/run_simulation.md，使用 Sysplorer MCP 运行 figure8 场景，控制器为 pid_baseline，结果保存到 results/official/example3_figure8/official_example3_pid_baseline/raw/official_example3_pid_baseline.csv。
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
| MWORKS evidence | Run controller or scenario checks through Sysplorer/Syslab MCP | `results/` evidence and metrics |
| Documentation | Update architecture, workflow, and acceptance text | `Design/`, `docs/`, `workflows/` edits |
| Git/quality | Scan large files, inspect diff, run targeted tests, commit/push | Clean Git state or exact blocker |

Rules:

1. Assign disjoint write sets before spawning agents.
2. Keep only one Git/quality agent active.
3. Research agents should not write files unless explicitly assigned.
4. The main agent must review all returned changes before commit.
5. If an agent finds a license, credential, activation, or destructive-action
   issue, it must stop that stream and report the blocker.

Use `workflows/agent_orchestration.md` for the full delegation contract and
`workflows/agent_task_ledger.md` for persistent recovery state.

---

## 9. Doctor / Self-Check Workflow

Use this before long Git/reference-import/MCP work or when the session state is
unclear:

```bash
python3 scripts/doctor.py
```

The doctor is intentionally cheap: it checks the project-local Git lock/status,
Git LFS availability, active agent ledger rows, tracked files over the selected
size limit, key workflow files, and MCP wrapper file presence. Live MCP health
still belongs to `/mcp` and `workflows/debug_mcp.md`.
