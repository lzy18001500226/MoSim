# Workflow Index

> Entry index for the active MoSim documentation set. An index points to an
> owner; it does not authorize live work. Start from the current user's direct
> request, then load only the workflow that matches that task.

## Start And Govern

| Need | Owner |
|---|---|
| Orient a new task | `Docs/Workflows/new_conversation_context.md` |
| Keep work task-local | `Docs/Workflows/single_thread_operating_model.md` |
| Read historical project status | `Docs/Workflows/mainline_operations_board.md` (explicit request only) |
| Place, compress, or archive documentation | `Docs/Workflows/documentation_governance.md` |
| Promote/reject session history | `Docs/Workflows/session_memory_migration.md` |
| Close a changed task or final package | `Docs/Workflows/pre_submit_check.md` |
| Reproduce a release, code-delivery hash, or package boundary | `Docs/Workflows/RELEASE_CHECKLIST.md` |
| Trace an old AgentOS packet only | `Docs/Workflows/agent_task_ledger.md` |

## Current Phase 1

| Need | Owner |
|---|---|
| Run the approved 46-route minimum-closure matrix | `Docs/Workflows/run_simulation.md`; `Scripts/mworks/run_phase1_minimum_closure.py`; `Scripts/tests/test_phase1_minimum_closure.py` |
| Interpret controller evidence boundaries and later gates | `Docs/Workflows/controller_evidence_closeout.md` |
| Read the older G6 execution contract only when it applies | `Docs/Workflows/g6_controller_experiment_execution.md` |

## Model And Evidence Work

| Need | Owner |
|---|---|
| Resolve a model, port, parameter, or replacement target | `Docs/Workflows/resolve_model_context.md` |
| Add or promote a controller | `Docs/Workflows/add_controller.md` |
| Build or repair graphical Sysblock topology | `Docs/Workflows/build_sysblock_graphical_controller.md` |
| Run one MWORKS simulation | `Docs/Workflows/run_simulation.md` |
| Produce labeled MWORKS evidence | `Docs/Workflows/produce_simulation_evidence.md` |
| Read results, calculate metrics, or generate figures | `Docs/Workflows/read_results.md`; `Docs/Workflows/calc_metrics.md`; `Docs/Workflows/generate_report_figures.md` |
| Generate controller code and connect it to runtime gates | `Docs/Workflows/mworks_codegen_controller_runtime.md` |
| Identify Sunray150 parameters | `Docs/Workflows/identify_quadrotor_parameters.md` |
| Run tests, regression, or review | `Docs/Workflows/run_tests.md`; `Docs/Workflows/regression_test.md`; `Docs/Workflows/code_review.md` |

## Documentation And Release Work

| Need | Owner |
|---|---|
| Build or validate a template-based Word report or handbook | `Docs/Workflows/template_based_word_export.md`; `Docs/Skills/Report/template-based-word-export/SKILL.md` |

## Runtime And Display Work

| Need | Owner |
|---|---|
| Current ROS1/Sunray/Gazebo/PX4/RViz lane | `Docs/Workflows/sunray_ros1_current_runtime_lane.md`; `Docs/Workflows/sunray_ros1_execution_checklist.md` |
| Bounded Factory scene-to-Sunray integration | `Docs/Workflows/factory_sunray_integration_gate.md` |
| Fixed Factory three-UAV formation operation | `Docs/Workflows/sunray_factory_three_uav_self_service.md` |
| QGC and Flight Console operator surface | `Docs/Workflows/qgc_ue_operator_startup.md` |
| UE-to-Gazebo static scene import | `Docs/Workflows/ue_to_gazebo_static_scene_import.md` |
| UE/frontend rendering and mapping-window boundary | `Docs/Workflows/unreal_renderer.md`; `Docs/Workflows/unreal_mapping_window_research.md` |
| MWORKS telemetry display scope | `Docs/Workflows/mworks_live_telemetry_scope.md` |

## Tooling And Reference Work

| Need | Owner |
|---|---|
| Diagnose a configured MCP server | `Docs/Workflows/debug_mcp.md` |
| Govern MCPs, hooks, plugins, and reference assets | `Docs/Workflows/tooling_assets_governance.md` |
| Audit or refresh an external repository snapshot | `Docs/Workflows/audit_external_repo.md`; `Docs/Workflows/reference_snapshot_update.md` |
| Translate a MathWorks/Simulink pattern to MWORKS | `Docs/Workflows/translate_mathworks_to_mworks.md` |

## Conditional Or Non-Current Entries

| Entry | Status |
|---|---|
| `Docs/Workflows/controller_family_gazebo_final_acceptance.md` | Closed with blockers; use only for its explicit trace-back. |
| `Docs/Workflows/g9_mworks_generated_runtime_closeout.md` | Dated task-specific plan; not the current Phase 1 route. |
| `Docs/Workflows/model_studio_offline_expansion_goal.md` | Historical design/backlog reference; not an execution selector. |
| `Docs/Workflows/project_structure_refactor.md` | User-frozen; do not execute its phases. |
| `Docs/Workflows/ros2_runtime_setup.md` | Historical/future fail-closed stub. |
| `Docs/Workflows/agent_task_ledger.md` | Legacy trace-back stub, not ordinary startup context. |

## Archived Material

These files are deliberately outside `Docs/Workflows/` and must not select
current work:

- `Docs/Cache/pre_submit_detail.md`: detailed final-package reference.
- `Docs/Cache/workflow_history/competition_gap_inventory_20260715.md`: dated
  gap snapshot.
- `Docs/Cache/workflow_history/controller_document_evidence_capture_20260720.md`:
  historical controller-capture contract.
- `Docs/Cache/workflow_history/classic_controller_family_closeout.md`:
  historical controller closeout.
- `Docs/Cache/workflow_history/factory_l2_full_system_validation_plan.md`:
  dated Factory F1-F8 plan.

Vendor and reference skill directories are governed separately by
`Docs/Workflows/tooling_assets_governance.md`; this index does not promote them
into routine project workflows.
