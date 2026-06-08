# UE 017 Live Echo Producer/Consumer Gate Summary

Scope: source-static/runtime-preflight only.

## Result

- Checker: passed.
- Focused pytest: passed, 14 tests.
- Runtime receiver implemented: false.
- Accepted-state UI controls enabled: false.
- Runtime ack leaks: 0.
- Actual receiver sink leaks: 0.

## Producer/Consumer Gate

The first authoritative live command-echo gate is now explicit in
`live_echo_producer_consumer_gate` inside the checker report.

Authoritative future producers:

- `MWORKS_live_downlink` with `ack_authority=MWORKS`.
- `ROS2_runtime_echo` with `ack_authority=ROS2`.
- `MWORKS_ROS2_live_downlink` with `ack_authority=MWORKS_ROS2`.

Consumer sink:

- `UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson`.

Receiver shell entry:

- `UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.ApplyCommandEchoJsonToState`.

Pending precondition:

- A matching UE command request must already be recorded through
  `RecordPendingCommandFromPacketJson` from `mosim.ue_command.v1`.

## Required Future Runtime Evidence

A later live task must provide all of the following before accepted-state UI can
be enabled:

- Actual receipt of `mosim.ue_command_echo.v1` through an authorized live
  transport.
- Authoritative `source` and matching `ack_authority`.
- `run_id`, `request_id`, `seq`, and command kind identity.
- `time_s`.
- `status=accepted` or `status=rejected`.
- Matching pending `mosim.ue_command.v1` request.
- `no_pose_overwrite_status=pass`.

## False Ack Rejections

The gate keeps these out of live command ack:

- Build or UBT success: `015_build_gate_passed`, `UnrealBuildTool_success`,
  `build_success`, `cli_build_success`.
- Sender success: `udp_send_success`, `sender_result_bSent`.
- Frame/status rows: `quadrotor.unreal_state.v1`,
  `quadrotor.unreal_state.frame`.
- Fixture-only rows: `fixture_only_007`, `fixture_only_008`,
  `fixture_only_010`, `fixture_only_011`.
- Source/offline/preflight rows: `offline_adapter_smoke`,
  `source_level_smoke`, `MWORKS_MCP_result_adapter_smoke`,
  `MWORKS_MCP_runtime_adapter_preflight`.
- Invalid live rows with missing identity, missing timestamp, no pending match,
  command mismatch, wrong authority, or no-pose-overwrite failure.
- Rejected authoritative echo rows must not mark runtime accepted.

## Evidence

- `producer_consumer_gate_static_contract.json`
- `pytest_receiver_shell_static_contract_producer_consumer_gate.txt`
- `pytest_receiver_shell_static_contract_producer_consumer_gate.xml`

## Claim Boundary

This evidence defines an executable source-static producer/consumer gate. It
does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime ack,
accepted-state UI behavior, planner readiness, controller performance, mission
success, or closed loop.
