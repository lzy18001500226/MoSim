# UE 024 Runtime Echo Producer Downlink Gate Summary

Task: RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-PRODUCER-DOWNLINK-GATE-20260608-024

Scope: source-static/build-prep only. No Unreal Editor, UE runtime, runtime probe, socket/listener/timer/background loop, accepted-state UI, MWORKS, ROS2, FAST-LIO, planner, controller, Sunray, References, or Git operation was used.

## Source Patch

- Added source-static authoritative downlink validation methods to `UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent`.
- Future live echo rows must pass validation before reaching `UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson`.
- Required fields before handoff: `schema`, `source`, `ack_authority`, `run_id`, `request_id`, `seq`, `time_s`, `status`, `command.kind` or `command_kind`, and `no_pose_overwrite_status`.
- Accepted source/authority pairs are limited to `MWORKS_live_downlink/MWORKS`, `ROS2_runtime_echo/ROS2`, and `MWORKS_ROS2_live_downlink/MWORKS_ROS2`.
- Forbidden pose command kinds are rejected before state sink: `pose_override`, `teleport`, `set_uav_pose`, `actor_transform`, and `keyboard_pose`.

## Evidence

- `runtime_echo_producer_downlink_gate_source_static.json`: `ok=true`; source-static/build-prep; 34 fixture rows; 3 future authoritative accepted rows; 3 future authoritative rejected rows; 4 non-live rows; 16 false-ack rows; 9 invalid rows; `runtime_ack_leaks=0`; `actual_runtime_claim_rows=0`.
- `pytest_runtime_echo_producer_downlink_gate.xml`: 11 focused tests passed.
- `receiver_shell_static_contract_after_024.json`: receiver-shell regression checker passed.
- `command_echo_runtime_prep_after_024.json`: runtime-prep regression checker passed.
- `pytest_runtime_echo_downlink_regression.xml`: 35 adjacent regression tests passed.

## Build-Prep Boundary

Unreal build was not run in 024. This task prepares the source/static handoff and records the future build surface:

- Build command: `Scripts/UE5/build_unreal_renderer.sh`
- UProject: `UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject`
- Engine association: `5.5`
- Plugin: `UE5/Bridge/QuadrotorMworksBridge.uplugin`
- Module: `QuadrotorMworksBridge`
- Build rule: `UE5/Bridge/Source/QuadrotorMworksBridge/QuadrotorMworksBridge.Build.cs`

The next compile-only task should validate the 024 C++ patch with UnrealBuildTool. Build success must remain compile evidence only, not command ack evidence.

## Future Live Gate

A later authorized live probe may claim runtime command-echo evidence only if it captures an actual runtime-generated `mosim.ue_command_echo.v1` row that matches a pending `mosim.ue_command.v1` request by run/request/seq/command identity, includes `time_s`, has `status=accepted` or `status=rejected`, has an accepted source/authority pair, and has `no_pose_overwrite_status=pass`.

The following remain false-ack sources: build success, UnrealBuildTool success, checker/pytest success, sender `Result.bSent`, UDP send success, fixture rows, static catalog rows, operator click intent, offline/source/preflight rows, and `quadrotor.unreal_state` frames.

## Claim Boundary

024 proves only source-static/build-prep for an authoritative UE command-echo downlink handoff. It does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime ack, accepted UI, `planner_ready`, controller performance, mission success, or `closed_loop`.
