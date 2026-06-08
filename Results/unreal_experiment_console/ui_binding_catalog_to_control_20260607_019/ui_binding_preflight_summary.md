# UE Console UI Binding Catalog-To-Control Preflight 019

Scope: source-static UI/control binding preflight only.

Result: passed.

Engineering evidence:

- Checker: `Scripts/UE5/check_ue_console_ui_binding_preflight.py`
- Focused tests: `Scripts/tests/test_ue_console_ui_binding_preflight.py`
- Checker output: `Results/unreal_experiment_console/ui_binding_catalog_to_control_20260607_019/ui_binding_preflight_source_static.json`
- Pytest JUnit: `Results/unreal_experiment_console/ui_binding_catalog_to_control_20260607_019/pytest_ui_binding_preflight.xml`
- Pytest stdout: `Results/unreal_experiment_console/ui_binding_catalog_to_control_20260607_019/pytest_ui_binding_preflight.txt`

Catalog-to-control descriptors:

| Command kind | Control descriptor | Default state | Current wire support | Claim boundary |
|---|---|---|---|---|
| `motor_fault.inject_or_clear` | `fault_motor_control` | `disabled_pending_authoritative_echo` | `motor_fault` | UE displays/request state only; MWORKS owns dynamics/control effect and metrics. |
| `disturbance.wind.set_or_clear` | `wind_disturbance_control` | `disabled_pending_authoritative_echo` | `wind_profile` | UE visualizes intent only; MWORKS owns physics truth and controller effect. |
| `controller.switch` | `controller_switch_control` | `disabled_pending_authoritative_echo` | `controller_select` | UE exposes operator choice only; MWORKS owns controller execution and performance evidence. |
| `planner.switch` | `planner_switch_control` | `disabled_pending_authoritative_echo` | `planner_select` | UE exposes operator choice only; ROS2/RViz2 owns planner topic/runtime evidence. |
| `scene_map.switch` | `scene_map_switch_control` | `disabled_pending_authoritative_echo` | `scene_switch` | UE owns rendering scene/map selection and sensor-oracle context; it must not feed global truth map to planner. |
| `experiment.run_control` | `experiment_run_control` | `disabled_pending_authoritative_echo` | `scenario_reset`, `start_goal_update`, `recording` | Run control coordinates surfaces; it does not prove controller/planner success. |
| `manual_review.request` | `manual_review_request_control` | `disabled_pending_authoritative_echo` | `recording` | Manual review opens or reports evidence; it is not automated acceptance. |

Accepted-state precondition:

- A matching pending `mosim.ue_command.v1` request must be recorded by `RecordPendingCommandFromPacketJson`.
- A future authoritative `mosim.ue_command_echo.v1` row must satisfy the UE 017 gate through `UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson`.
- Required evidence includes source, ack_authority, run_id, request_id, seq, time_s, status accepted/rejected, command identity, matching pending request, and `no_pose_overwrite_status=pass`.

Rejected as live ack:

- Build or UnrealBuildTool success.
- Checker or pytest success.
- UDP send success or sender `Result.bSent`.
- `quadrotor.unreal_state` frame/status rows.
- Fixture-only, static catalog, operator-click, offline/source/preflight smoke rows.

Boundary:

019 does not implement UE UI, Blueprint, UMG, Slate, Web UI, runtime transport,
socket/listener/timer/background loop, accepted-state UI, live UE ack,
MWORKS/ROS2 ack, planner readiness, controller performance, mission success, or
closed loop.
