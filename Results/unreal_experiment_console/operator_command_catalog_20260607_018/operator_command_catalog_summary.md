# UE 018 Operator Command Catalog Source-Static Gate

Scope: source-static only. No Unreal Editor, UE runtime, Unreal build, sockets,
listeners, timers, Blueprint, UMG, Slate, Web UI, assets, materials, textures,
MWORKS runtime, ROS2 runtime, planner runtime, or accepted-state UI controls
were used.

## Result

- Checker: `ok=true`.
- Focused pytest: `12 passed`.
- Catalog entries: 7.
- Domain owners: MWORKS=3, ROS2=1, UE=1, PMO=2.
- Accepted-state UI: disabled.
- Runtime transport: not implemented.
- Runtime acknowledgement: not claimed.

## Catalog Entries

| command.kind | owner | current wire kind |
|---|---|---|
| `motor_fault.inject_or_clear` | MWORKS | `motor_fault` |
| `disturbance.wind.set_or_clear` | MWORKS | `wind_profile` |
| `controller.switch` | MWORKS | `controller_select` |
| `planner.switch` | ROS2 | `planner_select` |
| `scene_map.switch` | UE | `scene_switch` |
| `experiment.run_control` | PMO | `scenario_reset`, `start_goal_update`, `recording` |
| `manual_review.request` | PMO | `recording` |

## Accepted-State Gate

Every catalog command remains pending/disabled until:

- a matching pending `mosim.ue_command.v1` request is recorded by
  `RecordPendingCommandFromPacketJson`;
- a future authoritative `mosim.ue_command_echo.v1` row passes UE 017 with
  source, ack authority, run/request/seq identity, `time_s`, accepted/rejected
  status, command identity, matching pending request, and
  `no_pose_overwrite_status=pass`;
- false ack sources remain rejected, including build success, UBT success,
  pytest/checker success, sender success, `quadrotor.unreal_state` frames,
  fixture rows, and offline/source/preflight smoke rows.

## Boundary

This gate defines the operator command catalog contract only. It does not
prove live UE runtime acknowledgement, MWORKS downlink, ROS2 runtime ack,
planner readiness, controller performance, FAST-LIO success, mission success,
closed loop, or final UI acceptance.
