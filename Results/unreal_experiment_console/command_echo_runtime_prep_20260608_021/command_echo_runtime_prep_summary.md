# UE 021 Command Echo Runtime Prep Gate

## Scope

- Task: `RFLY-MOSIM-UE-CONSOLE-COMMAND-ECHO-RUNTIME-PREP-GATE-20260608-021`
- Scope classification: `source-static/build-prep`
- Unreal Editor, PIE, UE runtime, sockets/listeners/timers/background loops, UMG/Blueprint/Slate/Web UI, and Unreal build were not started.
- This evidence prepares a later authoritative `mosim.ue_command_echo.v1` live probe. It is not live runtime ack evidence.

## Source Prep

- Updated source anchor: `UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleStateComponent.cpp`
- Changed methods:
  - `ApplyCommandEchoJson`
  - anonymous namespace helper functions
- Added guards:
  - non-smoke echo rows must include numeric `time_s`
  - non-smoke echo rows must match an authoritative source/authority pair:
    - `MWORKS_live_downlink` + `MWORKS`
    - `ROS2_runtime_echo` + `ROS2`
    - `MWORKS_ROS2_live_downlink` + `MWORKS_ROS2`
  - `accepted_as_runtime_ack` requires non-smoke source and `status=accepted`
  - authoritative `status=rejected` may update rejected state but cannot mark runtime accepted
  - smoke/offline/source/preflight labels remain `smoke_only` and `accepted_as_runtime_ack=false`

## Matrix Evidence

- Checker: `Scripts/UE5/check_ue_console_command_echo_runtime_prep_gate.py`
- Evidence: `command_echo_runtime_prep_gate_source_static.json`
- Result: `ok=true`
- Control descriptors: 7
- Matrix rows: 168
- Valid future authoritative accepted echo rows: 7
- Authoritative rejected rows: 7
- Missing timestamp rows: 7
- Wrong authority rows: 7
- No matching pending rows: 7
- Command identity mismatch rows: 7
- No-pose failure rows: 7
- Non-live rows: 28
- False-ack rows: 84
- Runtime-prep leaks: 0
- Actual runtime/UI leaks: 0

## Verification

- Focused 021 pytest: `10 passed`
- Regression pytest: `35 passed`
- Static regression checkers after the patch:
  - `console_state_contract_after_runtime_prep.json`: `ok=true`
  - `disabled_state_contract_after_runtime_prep.json`: `ok=true`
  - `control_state_reducer_after_runtime_prep.json`: `ok=true`
  - `receiver_shell_static_contract_after_runtime_prep.json`: `ok=true`

## Build Prep Surface

- UProject: `UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject`
- Engine association: `5.5`
- Plugin: `UE5/Bridge/QuadrotorMworksBridge.uplugin`
- Module: `QuadrotorMworksBridge`
- Build rules: `UE5/Bridge/Source/QuadrotorMworksBridge/QuadrotorMworksBridge.Build.cs`
- Future build command: `Scripts/UE5/build_unreal_renderer.sh`
- Future build gate must treat build success only as compile evidence, not command ack.

## Future Live Probe Recommendation

A separately authorized runtime/editor task should provide:

- pending `mosim.ue_command.v1` request identity: `run_id`, `request_id`, `seq`, command kind, and timestamp
- live `mosim.ue_command_echo.v1` row from an authoritative producer
- matching source and `ack_authority`
- `time_s`
- `status=accepted` or `status=rejected`
- command identity matching the pending request
- `no_pose_overwrite_status=pass`
- negative rows for build/checker/sender/fixture/static/frame/non-live sources

## Claim Boundary

UE 021 proves only source-static/build-prep readiness for a future command-echo runtime gate. It does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime ack, accepted UI, planner readiness, FAST-LIO success, controller performance, mission success, or closed loop.
