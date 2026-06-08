# UE 013 Receiver Shell Build Preflight

Scope: source-static/build-preflight only.

This evidence closes the 013 preflight from existing static outputs. It does
not open Unreal Editor, run UnrealBuildTool, edit UE C++/Blueprint/UMG/assets,
bind sockets, or prove a live runtime acknowledgement.

## Existing Evidence

- `receiver_shell_static_contract_regression.json`: `ok=true`,
  `checker_only_contract=true`, `receiver_shell_cpp_implemented=false`,
  `runtime_receiver_implemented=false`, `ui_accepted_state_controls_enabled=false`,
  `runtime_ack_leaks=0`, `actual_receiver_sink_leaks=0`.
- `pytest_receiver_shell_static_contract.xml`: 9 pytest cases, 0 failures,
  0 errors, 0 skipped.
- `live_receiver_boundary_static_regression.json`: current live echo receiver
  is absent; existing UDP receiver remains `quadrotor.unreal_state` frame/status
  only; future echo receiver must be a separate project-owned component.
- `console_state_contract_static_regression.json`: pending rows originate from
  `mosim.ue_command.v1`; accepted/rejected rows originate from matching
  `mosim.ue_command_echo.v1`; sender remains sender-only.
- `disabled_state_contract_static_regression.json`: non-live rows stay disabled
  with no runtime ack leaks.
- `live_echo_acceptance_fixture_static_regression.json`: future accepted rows
  require authoritative source, command id, timestamp/status identity, and
  no-pose-overwrite pass; smoke/preflight rows do not become runtime accepted.

## Build Surface

- Project: `UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject`
- Engine association: `5.5`
- Plugin: `UE5/Bridge/QuadrotorMworksBridge.uplugin`
- Runtime module: `QuadrotorMworksBridge`
- Module dependencies already include `Json`, `JsonUtilities`, `Networking`,
  and `Sockets` in `QuadrotorMworksBridge.Build.cs`.
- Existing build wrapper for a future PMO-authorized build gate:
  `Scripts/UE5/build_unreal_renderer.sh`

Future build command, not executed in 013:

```bash
Scripts/UE5/build_unreal_renderer.sh
```

When invoking Windows UBT from WSL, pass the `.uproject` as a Windows path, or
use the wrapper above.

## Source Anchors

- State component:
  `UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksExperimentConsoleStateComponent.h`
  and
  `UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleStateComponent.cpp`
- Pending request API:
  `UQuadrotorMworksExperimentConsoleStateComponent::RecordPendingCommandFromPacketJson`
- Echo sink API:
  `UQuadrotorMworksExperimentConsoleStateComponent::ApplyCommandEchoJson`
- Frame/status receiver:
  `UQuadrotorMworksUdpReceiverComponent`, restricted to
  `quadrotor.unreal_state.*` frame/status packets and not a command ack source.
- Command sender:
  `UQuadrotorMworksUdpCommandSenderComponent`, sender-only for
  `mosim.ue_command.v1`; `Result.bSent` remains transport send status, not ack.

## Minimal Next C++ Slice

Only a future PMO implementation task should edit source. The smallest safe
receiver-shell implementation slice is:

- Add
  `UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.h`
- Add
  `UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.cpp`
- Keep it separate from `UQuadrotorMworksUdpReceiverComponent` and
  `UQuadrotorMworksUdpCommandSenderComponent`.
- Accept only `mosim.ue_command_echo.v1` payloads from a future authorized
  transport surface.
- Route validated echo JSON only to
  `UQuadrotorMworksExperimentConsoleStateComponent::ApplyCommandEchoJson`.
- Do not treat UDP send success, `Result.bSent`, `quadrotor.unreal_state.*`,
  fixture-only rows, source/offline/preflight rows, or no-pose-overwrite
  failures as runtime accepted ack.
- Do not expose keyboard/mouse/Actor transform pose control.

## Acceptance Gates For Later Tasks

1. Static checker detects the new component and confirms it is separate from
   the frame receiver and sender.
2. Checker confirms only `mosim.ue_command_echo.v1` is accepted by the receiver
   shell and that the only state sink is `ApplyCommandEchoJson`.
3. Checker confirms non-live labels remain `quality_status=smoke_only` and
   `accepted_as_runtime_ack=false`.
4. Focused pytest covers accepted, rejected, stale/orphan/mismatched, missing
   timestamp/command id, wrong authority, sender-only success, and
   `quadrotor.unreal_state.*` negative cases.
5. A later build task runs the Unreal build wrapper and archives the build log.
6. Runtime ack claims remain blocked until a separate authorized live transport
   task produces command/echo/provenance evidence.

## Claim Boundary

013 is build-preflight planning and static evidence only. It does not prove
live UE runtime ack, live MWORKS downlink, ROS2 runtime ack, accepted UI
binding, planner readiness, closed loop, controller performance, FAST-LIO
success, localization quality, mission success, or final UI acceptance.
