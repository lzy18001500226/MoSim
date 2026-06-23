# RflySim-like MoSim P0 10h Execution Plan

Status: historical/superseded execution plan, 2026-06-23 CST.

This file is retained for audit only. It must not be used as the current
execution selector. Current Sunray ROS1/Gazebo/RViz work starts from
`Docs/Workflows/sunray_ros1_current_runtime_lane.md`; current architecture and
FAST-LIO state-source promotion rules start from
`Docs/Design/MoSim_FASTLIO定位闭环与规划复现基础方案.md` and
`Docs/Design/MoSim真机化收尾与C++化重构方案.md`.

Origin PMO thread: `019e9868-83ea-70f0-92c5-a3a408bd78c6`.

Goal:

```text
Build the first honest P0 closed-loop path for MoSim:
Factory scene -> UE sensor oracle / ROS2 sensor topics -> FAST-LIO/local map
-> planner/setpoint stream -> 20Hz MWORKS controller -> MWORKS dynamics
-> UE/RViz/evidence feedback.
```

This is a 10h work plan. It does not require blocking on manual review. If
manual review is needed but not returned promptly, record the pending review
packet and continue with headless implementation or evidence checks that do not
depend on the review result.

## 1. Current Inputs

Architecture sources:

- `Docs/Design/架构.md`
- `Docs/Design/11_RflySim式MoSim最小闭环架构审核.md`
- `Docs/Design/cache/pre_rebuild_20260610/09_UE_ROS_MWORKS无人机仿真架构重构.md`
- `Docs/Workflows/unreal_renderer.md`
- `Docs/Workflows/identify_quadrotor_parameters.md`

Returned UE/frontend design:

- `Results/agent_packets/returns/RFLY-MOSIM-AUDIT-UE-FRONTEND-MAP-20260606-001.json`

Planned task packets:

- `Results/agent_packets/tasks/audit/RFLY-MOSIM-AUDIT-ROS-FASTLIO-20260606-001.json`
- `Results/agent_packets/tasks/audit/RFLY-MOSIM-AUDIT-MWORKS-CONTROL-20260606-001.json`
- `Results/agent_packets/tasks/audit/RFLY-MOSIM-AUDIT-PX4-SILHIL-20260606-001.json`
- `Results/agent_packets/tasks/audit/RFLY-MOSIM-AUDIT-EVIDENCE-LOGGING-20260606-001.json`

## 2. 10h Critical Path

| Window | PMO critical path | Parallel work | Exit evidence |
|---|---|---|---|
| 0-1h | Integrate UE return packet, freeze P0 command/echo/run-state fields, update ledger. | Spawn ROS2, MWORKS, Evidence sidecar agents. | updated `PROGRESS.md`, ledger, task packet statuses. |
| 1-3h | Inspect current MWORKS Sunray150 upgrade model/wrapper and MCP health. | ROS2 agent audits FAST-LIO/local-map/planner gate. | model feature matrix and MCP check decision. |
| 3-5h | Implement or tighten project-owned MWORKS wrapper only if current model gap is clear. | Evidence agent drafts `RUN_MANIFEST` and gate checks. | checked Modelica diff or explicit no-edit blocker. |
| 5-7h | Run smallest MWORKS hover/yaw/step check where MCP is healthy. | ROS2 agent returns commands/gaps; UE return is converted into implementation tasks. | `source=MWORKS_MCP` check/smoke evidence or recorded MCP blocker. |
| 7-9h | Compose P0 loop integration plan from returned sidecar packets. | Optional PX4 design audit if time remains. | one P0 execution queue with owners and acceptance gates. |
| 9-10h | Send completion/manual-review sparse Chinese email packet, update docs, run checks, prepare next work item. | Close or checkpoint subagents. | final status packet and recovery instructions. |

## 3. Work Ownership

Main PMO thread owns:

- integration and final authority decisions;
- task ledger and PROGRESS updates;
- MWORKS critical-path edits/checks when needed;
- sparse email milestone/manual-review/blocker notifications;
- rejecting fake point-cloud/grid/keyboard/UE-truth leaks.

Sidecar agents:

| Agent | Scope | Write set | Required return |
|---|---|---|---|
| ROS2-FASTLIO sidecar | topic/timing/FAST-LIO/local-map/planner P0 gate | return packet only unless explicitly upgraded | evidence paths, gap list, next commands. |
| MWORKS-Control sidecar | current wrapper/model gap and smoke strategy | return packet only unless explicitly upgraded | feature matrix, model names, safe edit target. |
| Evidence sidecar | unified run manifest and quality gates | return packet only unless explicitly upgraded | `RUN_MANIFEST` field proposal and checks. |
| PX4-SILHIL sidecar | P1/P2 adapter placement | return packet only, lower priority | adapter contract and blockers. |

## 4. Manual Review Policy

Manual review triggers:

- UE/RViz visual review window is ready after headless gates pass;
- command/echo UI schema needs user product judgement;
- MWORKS native animation/result review is required;
- a blocker changes architecture direction.

If review is needed:

1. Write a review packet under `Results/coagent_gateway/packets/`.
2. Send a sparse Chinese email notification through
   `Scripts/agent/send_gateway_email_alert.py`.
3. Expose origin thread id `019e9868-83ea-70f0-92c5-a3a408bd78c6`.
4. If the user does not answer, record `review_pending` in `PROGRESS.md` and
   continue with headless work that does not depend on the review result.

Do not wait idly for review unless the next action would change product
direction or destroy/overwrite user work.

## 4.1 Department Communication Contract

PMO dispatches only to existing canonical visible department threads unless the
user explicitly approves a new thread. Department threads must return durable
packets under `Results/agent_packets/returns/` or
`Results/agent_packets/blockers/`; chat replies, email, and WeChat messages are
notifications only and are not evidence. Current routine user notification is
sparse Chinese email; WeChat is used only for explicit restored gateway
diagnosis or a user-requested WeChat retry.

Department threads must also plan locally. For every non-trivial task packet,
the target department should derive and report:

```text
department_local_goal
critical_path_steps
parallelizable_slices
subagent_plan
subagent_plan_reason
subagents_used
verification_gates
manual_review_or_blocker_triggers
```

`subagent_plan` is the required scheduling decision and must be one of `used`,
`available_but_not_useful`, `unavailable`, or `unsafe`. This is not a
requirement to use at least one sub-agent. `subagents_used=[]` is acceptable
when the department runtime has no sub-agent surface, no independent slice
exists, or serial execution is safer. If a department uses disposable
sub-agents, they must be bounded, task-local, evidence-returning helpers; they
must not become hidden durable departments or create/fork/rename/archive
visible threads.

Every department task must also declare task-specific infrastructure preflight
and expected engineering outputs. If the preflight fails, the department stops
and returns a blocker instead of continuing domain retries. JSON packets,
ledger rows, and progress notes are control-plane evidence; they do not count
as the engineering deliverable unless the task is explicitly diagnostic,
rule-sync, preflight-drill, dispatch-surface diagnostic, or static inventory.
PMO rejects completed returns that lack domain artifacts, omit the local
plan/sub-agent decision, or turn a real blocker into completed metadata.

Historical department-thread snapshot for this P0 run:

This table is retained as execution-plan history only. For new dispatch,
always use `CoAgent/dispatch/department_threads.json`,
`Docs/Workflows/mainline_operations_board.md`, and
`Docs/Workflows/org_operating_model.md` as the current routing sources.
Do not route new work from this table when a thread title, id, or status has
changed.

| Department | Thread id | Current dispatch rule |
|---|---|---|
| ROS2 Perception, Localization, And Planning Runtime R1 | `019e9c72-ee74-79d1-b9fe-621d3c6fc99e` | Current production ROS2 route. Finish/integrate current 049 callback first-N instrumentation before planner/TF/RViz readiness gates. |
| ROS2 old R2 diagnostic sample | `019e9b85-d4d8-7bf3-8afd-a65697cd3889` | Not production routing. Use only after bounded no-op/dispatch-surface diagnosis and explicit PMO restoration. |
| MWORKS Dynamics And Control Verification R1 | `019e9be5-334b-76b1-93f9-8b02caebf376` | Primary MWORKS dynamics/control/model-integration evidence route. Every business task must include the MWORKS live gate and expected engineering outputs. |
| MWORKS Graphical Model Audit R2 | `019e9999-b0d3-7682-bccd-faef08fcf1df` | Auxiliary route for model organization, graphical simulation interface completeness, connection/layout/readability, and diagram hygiene. Also requires the MWORKS live gate before static or live business work. |
| UE Experiment Console Integration | see current registry | Use current UE R1/R2/R3 rows from the registry for UE operator console, command/echo, fault/wind/controller/planner switching, and manual-review UI tasks. |
| Sunray150 DAE/PBR Asset Optimization | see current registry | Frozen unless the user reopens Sunray/PBR; use current registry only after explicit reopen. |

Only PMO thread `019e9868-83ea-70f0-92c5-a3a408bd78c6` may create, fork,
rename, or archive visible department threads. Other departments may request a
new role through a blocker packet, but must not create or delegate thread
creation.

Archived/superseded threads must not be used for dispatch:

```text
UE old thread:     019e9af5-3768-77b0-aa9d-3c21ea20d99d
Sunray old thread: 019e9af4-6ffc-7db0-a037-187dd3787f2e
```

For each return or blocker packet, PMO decides the next communication action:

```text
manual_review_required=true
  -> PMO writes/sends a sparse email review packet with PMO thread id.
blocker changes architecture or requires user approval
  -> PMO sends sparse email blocker packet and records it in PROGRESS.md.
ordinary file-level audit or smoke completion
  -> PMO records ledger/PROGRESS and continues without interrupting user.
```

## 5. Guardrails

Do not implement or accept:

- fake/static point clouds as localization evidence;
- fake 2D grid map as UAV local 3D map;
- keyboard or mouse pose overwrite as control;
- browser HTML as active point-cloud/map review;
- UE pass/fail judgement for controller or planner;
- UE global map/collision truth as planner input;
- direct official `QuadChassis` baseline edits when a wrapper suffices;
- RflySim/Gazebo sample numbers as Sunray150 identified truth.

## 6. Immediate Next Task

Start with the MWORKS plant side because it is the P0 solver authority:

```text
1. Check MCP health with a minimal Sysplorer probe.
2. Inspect current Sunray150 dynamics upgrade model and evidence.
3. Confirm whether motor lag, yaw reaction torque, and rotor-center moment are
   already present in the project-owned wrapper.
4. If present, run/check the smallest hover/yaw smoke.
5. If absent, patch only the project-owned experimental model and check it.
```

ROS2 and Evidence agents can run in parallel because their outputs inform, but
do not block, the first MWORKS inspection.

## 7. First Checkpoint, 2026-06-06

Sidecar returns:

- ROS2-FASTLIO sidecar reports Factory FAST-LIO Gate B is current-pass for
  manual UE/RViz review readiness, with LiDAR about `9.887Hz`, IMU about
  `198.857Hz`, `/Odometry=80`, `/path=8`, `/cloud_registered=80`, position
  RMSE `0.39454m`, max error `0.611542m`, and yaw RMSE `0.017802rad`.
- The same sidecar reports P0 is still incomplete because the current gate does
  not prove 3D local map/planner review, and planner output is not wired into a
  20Hz MWORKS setpoint adapter.
- MWORKS-Control sidecar confirms the project-owned experimental dynamics has
  motor lag, `Ct * omega^2` thrust, yaw reaction torque, and rotor-center moment;
  official `QuadChassis` still lacks the explicit actuator chain and remains
  unchanged.
- Evidence sidecar confirms the next required artifact is a strict
  `RUN_MANIFEST.json` plus a cross-layer gate. Without it, slice evidence can
  be overclaimed as full closed-loop evidence.

Main-thread MCP checkpoint:

```text
check_model QuadrotorExperiments.Sunray150DynamicsUpgradeHoverSmoke: ok=true
check_model QuadrotorExperiments.Sunray150DynamicsUpgradeYawStepSmoke: ok=true
simulate HoverSmoke dynamics.hover_thrust_error@end:
  1.7763568394002505e-15
simulate YawStepSmoke dynamics.total_moment_body[3]@end:
  0.06147367992970332
```

Updated critical path after checkpoint:

1. Create the P0 `RUN_MANIFEST` schema/checker first, because all later gates
   need one run identity.
2. Add or identify the 20Hz planner-to-MWORKS setpoint adapter and stale-command
   trace.
3. Add a real 3D local map/planner evidence gate; do not treat current FAST-LIO
   Gate B as full P0 acceptance.
4. Use the existing MWORKS dynamics smoke as the actuator-structure baseline
   for wrapper integration; do not edit official `QuadChassis`.

Implemented in this checkpoint:

```text
Config/schemas/mosim_run_manifest_v1.schema.json
Scripts/quality/check_run_manifest.py
Scripts/tests/test_run_manifest_gate.py
```

Validation:

```text
python -m pytest Scripts/tests/test_run_manifest_gate.py -q
python -m json.tool Config/schemas/mosim_run_manifest_v1.schema.json
python Scripts/quality/check_run_manifest.py --help
```

All three checks passed. The checker now rejects common P0 overclaims:

- MWORKS source is not `MWORKS_MCP` or `MWORKS_GUI`;
- planner input uses UE/global truth;
- FAST-LIO/localization claim lacks pass status or exceeds RMSE/max-error
  thresholds;
- planner/closed-loop claim lacks 20Hz setpoint trace;
- planner/closed-loop claim uses an offline UE navigation handoff instead of a
  runtime 20Hz adapter trace with stale-command timeout;
- UE path permits pose overwrite;
- `quality_status=pass` still has blockers.

## 8. Offline Handoff Boundary, 2026-06-06

The current UE navigation/control handoff path is useful, but it is not the P0
runtime adapter:

```text
Scripts/UE5/build_navigation_handoff.py
  -> navigation_control_handoff.json
  -> control_interface_package.json
  -> control_reference.csv
  -> inactive scenario_draft.yaml
```

Those outputs are `offline_ue_navigation_control_interface_package` artifacts.
They can seed a `PlannedQuinticReference` smoke model and help build a
scenario, but they do not prove:

- ROS2 planner output is arriving online;
- setpoints are streamed to MWORKS at 20Hz;
- stale planner commands are detected or rejected;
- MWORKS consumed the trace in the same run as ROS2/FAST-LIO/UE evidence.

The active `RUN_MANIFEST` checker now requires planner/closed-loop claims to
declare:

```text
planner.setpoint_trace_source = RUNTIME_20HZ_ADAPTER
planner.setpoint_adapter_status = pass
planner.setpoint_rate_hz >= 19
planner.stale_command_timeout_s > 0
planner.setpoint_trace = existing artifact path
```

If the trace comes from `control_reference.csv` or another offline handoff,
`quality_status` must remain `smoke_only` or `needs_iteration`, and
`claim_scope` must not include full `planner` or `closed_loop` acceptance.

## 9. Planner Setpoint Adapter Contract, 2026-06-06

The first adapter artifact is now a headless contract script, not a live ROS2
node:

```text
Scripts/ros/planner_setpoint_adapter.py
Scripts/tests/test_planner_setpoint_adapter.py
```

It consumes a runtime-style planner command CSV with:

```text
time, sequence, frame_id, planner_id, trajectory_status,
x, y, z, vx, vy, vz, ax, ay, az, yaw, yaw_rate
```

It writes:

```text
20Hz setpoint trace CSV
accepted/rejected echo JSONL
summary JSON/stdout with:
  setpoint_trace_source = RUNTIME_20HZ_ADAPTER
  setpoint_adapter_status = pass | needs_iteration
  stale_command_timeout_s
  topics_contract:
    input  = /mosim/planner/position_cmd
    output = /mosim/planner/setpoint
    status = /mosim/planner/setpoint_adapter_status
```

Validation already covered:

```text
python -m pytest Scripts/tests/test_planner_setpoint_adapter.py -q
python Scripts/tests/test_planner_setpoint_adapter.py
```

The script rejects wrong frames, non-finite command values, non-monotonic
command time/sequence, and records stale commands as `mode=hold` with
`reject_reason=stale_command`.

Claim boundary:

- This is an executable contract for the future ROS2 adapter.
- It does not publish ROS2 messages.
- It does not prove MWORKS consumed the setpoints in the same live run.
- It can satisfy `RUN_MANIFEST` only after a real runtime planner and MWORKS
  run bind the produced trace under one `run_id`.

Next implementation package:

```text
Scripts/ros/mosim_msgs/msg/PlannerSetpoint.msg
Scripts/ros/mosim_msgs/msg/SetpointAdapterStatus.msg
Scripts/ros/mosim_setpoint_adapter/src/planner_setpoint_adapter_node.cpp
```

Those ROS2 files should preserve the same field names and echo semantics, then
the headless contract can become the regression fixture for the compiled node.

Current ROS2 skeleton:

```text
Scripts/ros/mosim_msgs/
Scripts/ros/mosim_setpoint_adapter/
Scripts/tests/test_ros_setpoint_adapter_contract.py
```

The static contract test checks message fields, package metadata, default
topics, and reject/stale status strings. It does not replace a WSL ROS2
`colcon build` or runtime topic smoke. Run those only in the ROS2 lane after
the local contract remains stable.

## 10. Visible Department Dispatch Checkpoint, 2026-06-06

PMO verified that visible department dispatch is working again through
Codex App `send_message_to_thread`, without hidden background CLI dispatch:

```text
UE target:     MoSim｜UE实验控制台与场景交互部-R1
UE thread id:  019e9b24-50aa-7cd3-9e7c-4c43b224d993
Sunray target: MoSim｜Sunray150资产与PBR审核部
Sunray thread id: 019e9b25-066e-7372-8152-209c2b1322a4
```

Both target task packets were corrected before dispatch so their historical
`target_thread` and `target_thread_id` matched the then-canonical threads.
For new dispatch, use `CoAgent/dispatch/department_threads.json`; Sunray/PBR
remains frozen unless the user explicitly reopens it.

Returned packets:

```text
Results/agent_packets/returns/RFLY-MOSIM-UE-EXPERIMENT-CONSOLE-P0-SLICE-20260606-001.json
Results/agent_packets/returns/RFLY-MOSIM-SUNRAY150-DAE-PBR-AUDIT-20260606-001.json
```

UE result:

- Completed a P0 operator-console shell/contract slice.
- Current UE sender evidence remains source-level command intent only.
- No live UE console, runtime MWORKS/ROS2 ack, planner readiness, or
  closed-loop readiness is claimed.
- Next tasks: UE schema/fixture smoke and MWORKS/ROS2 authoritative command
  echo producer contract.

Sunray/PBR result:

- Completed a file-level component/PBR audit with manual review required.
- Review batches: carbon/standoffs/fasteners, MID-360 housing/window/connector,
  motor/prop/guard, and front-camera/PCB/connectors/cables/battery.
- File-level PNG assets exist, but this is not final visual acceptance.
- The miniloop checker currently fails under Windows-native Codex because the
  texture manifest stores `/mnt/c/...` absolute paths; Windows resolves those
  as `C:\mnt\c\...`, outside the project guard. Fix path normalization before
  treating the miniloop as passed.
- Process correction after user feedback: future department task packets must
  require department-local goal/task-graph/sub-agent planning fields in their
  return/blocker packets. The two packets above were valid returns for this
  dispatch test, but future broad department work should not omit those fields.
