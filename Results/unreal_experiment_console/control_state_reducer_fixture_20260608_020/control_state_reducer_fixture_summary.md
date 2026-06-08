# UE 020 Control-State Reducer Fixture Summary

Scope: source-static checker/test/evidence only.

## Result

- Checker: passed
- Focused pytest: 9 passed
- Control descriptors: 7
- Reducer rows: 49
- Runtime ack leaks: 0
- Accepted UI controls enabled now: false

## Matrix Contract

Each 019 control descriptor has these fixture rows:

- `initial_disabled`
- `pending_from_matching_command`
- `accepted_from_authoritative_echo`
- `rejected_from_authoritative_echo`
- `stale_echo_rejected`
- `mismatched_echo_rejected`
- `false_ack_rejected`

Pending state is created only from a matching `mosim.ue_command.v1` request
through `RecordPendingCommandFromPacketJson`. Accepted/rejected state is
eligible only for a matching authoritative `mosim.ue_command_echo.v1` row
through `UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson`.

## False Ack Rejection

The fixture rejects build, UBT, pytest, checker, UDP send, sender success,
`quadrotor.unreal_state`, fixture-only, static catalog, operator-click,
offline, source-level, and MWORKS MCP smoke/preflight rows as live accepted
state.

## Future UI Recommendation

A later separately authorized UI/runtime implementation should bind controls to
this reducer only after live echo transport exists. The minimum future gate is:
matching request id, run id, seq, command wire kind, control descriptor id,
timestamp, authoritative source/ack authority, status, and
`no_pose_overwrite_status=pass`. Stale, mismatched, or false-ack rows must keep
the control pending/disabled or rejected.

## Claim Boundary

This evidence does not prove UE runtime ack, live MWORKS/ROS2 ack, accepted UI,
planner readiness, controller performance, FAST-LIO success, mission success,
or closed loop.
