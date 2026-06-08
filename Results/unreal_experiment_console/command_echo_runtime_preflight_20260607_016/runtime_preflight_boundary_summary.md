# UE 016 Command Echo Runtime Preflight Boundary Summary

Scope: source-static/runtime-preflight only. Unreal Editor, UE runtime, sockets,
listeners, timers, background receive loops, Blueprint/UMG/assets/project
settings, MWORKS, ROS2, RViz2, FAST-LIO, and planner runtime were not used.

## Result

- Static checker passed with `ok=true`.
- The 014 C++ source-static receiver shell is present.
- Runtime receiver implementation is still absent.
- Accepted-state UI controls remain disabled/not enabled by this task.
- No live UE runtime acknowledgement is claimed.

## Source Anchors

- Receiver shell:
  `UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.h`
  and
  `UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.cpp`.
- State sink:
  `UQuadrotorMworksExperimentConsoleStateComponent::ApplyCommandEchoJson`.
- Pending precondition:
  `UQuadrotorMworksExperimentConsoleStateComponent::RecordPendingCommandFromPacketJson`.
- Frame/status receiver remains
  `UQuadrotorMworksUdpReceiverComponent` for `quadrotor.unreal_state.*` only.
- Command sender remains
  `UQuadrotorMworksUdpCommandSenderComponent` for `mosim.ue_command.v1` only.

## Static Matrix

The checker matrix has 28 rows:

- 3 future-authoritative rows are contract-eligible only after a separately
  authorized runtime receiver exists.
- 4 non-live rows remain not accepted as runtime ack.
- 14 forbidden ack-source rows remain not accepted as runtime ack, including
  015 build success, UnrealBuildTool success, UDP send success, sender result
  success, fixture-only rows, and `quadrotor.unreal_state.*`.
- 6 invalid live rows remain not accepted as runtime ack.
- 1 rejected authoritative row does not mark runtime accepted.
- Runtime ack leaks: 0.
- Actual receiver sink leaks: 0.

## Future Live Task Recommendation

The next live task must be separately authorized as runtime work. It should
produce all of the following before accepted-state UI can be enabled:

- A live transport surface that receives only `mosim.ue_command_echo.v1`.
- A producer provenance row from `MWORKS_live_downlink`,
  `ROS2_runtime_echo`, or `MWORKS_ROS2_live_downlink` with matching
  `ack_authority`.
- Matching `run_id`, `request_id`, and `seq` against a pending UE command
  request recorded by the state component.
- A timestamp field and command identity.
- `status=accepted` or `status=rejected`.
- `no_pose_overwrite_status=pass`.
- Runtime evidence showing the receiver calls only
  `ApplyCommandEchoJson` after validation.
- Negative evidence that build success, UDP send success, frame/status
  downlink, fixture/source/preflight rows, and no-pose-overwrite failures do
  not enable runtime accepted state.

Any need to open Unreal Editor, start runtime, bind ports, implement sockets,
or enable accepted-state UI belongs to a later explicitly authorized task.
