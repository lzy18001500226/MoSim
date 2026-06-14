# UE Runtime Replay Review Packet, 2026-06-12

Status: `review_material_opened_nonfinal`.

This packet records the currently opened UE runtime replay evidence for the
accepted MWORKS single-UAV rotor1-loss run. It is a review aid, not final
visual acceptance and not command-echo runtime acknowledgement.

## Opened Review Material

Primary after-stream window screenshot:

```text
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1105/screenshots_after_stream/101392_0x2AE1882_MoSimSceneLibrary （64-位 Development PCD3D_SM6） .png
```

Supporting capture manifest:

```text
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1105/screenshots_after_stream/capture_manifest.json
```

Supporting runtime summary:

```text
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1105/ue_runtime_replay_probe_summary.json
```

Supporting UE log tail:

```text
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1105/ue_log_tail_after_stream.txt
```

## Current Human-Visible Observation

The opened after-stream main-window screenshot is nonblank and shows the
Factory/Demonstration UE scene rendered in a normal Unreal game window. The
image is suitable for confirming that the UE scene window is visible, the map
is not black, and the capture route produced a readable review image.

The current camera view does not clearly show the Sunray150 UAV body. A
sidecar read-only review reached the same conclusion: the before-stream and
after-stream main-window images support UE runtime window visibility and
factory-scene rendering, but they do not support a human-visible Sunray150
vehicle claim. Therefore these screenshots alone are not enough for final
vehicle visual acceptance, component/material acceptance, trajectory review, or
a human statement that the UAV is visually correct in the scene.

## Log-Supported Runtime Facts

The UE log tail reports:

```text
Quadrotor MWORKS UDP first frame: scene=robust_rotor1_loss15_example1 map=local_factoryenvironmentcollect seq=0
MoSim Sunray first applied frame: scene=robust_rotor1_loss15_example1 map=local_factoryenvironmentcollect seq=0
MoSim Sunray component diagnostic: SunrayDaeDerivedVehicleAfterFirstFrame visible=true hidden_in_game=false ... box_extent=(424.263, 422.542, 318.760) sphere_radius=606.681
```

These log rows support runtime ingestion of the accepted MWORKS state stream
and a nonzero visible Sunray150 component in UE. They do not replace a
human-readable close-up screenshot for final visual acceptance.

## Claim Boundary

- Proves: UE scene rendered, window capture nonblank, runtime replay path
  reached the Factory/Demonstration scene, UE log reports first MWORKS UDP
  frame and Sunray component visibility/nonzero bounds.
- Does not prove: authoritative command echo acknowledgement, final/manual
  visual acceptance, material acceptance, ROS2/FAST-LIO success,
  `planner_ready`, controller performance from UE, multi-UAV readiness, or
  closed-loop success beyond the accepted MWORKS run.

## Next Executable Paths

### Path A: Visual Review Hardening

Goal: produce human-readable screenshots where the Sunray150 UAV body is
clearly visible in the Factory scene.

Required evidence:

```text
before/after capture manifest
main UE window screenshot
UAV-close review screenshot
log tail showing first UDP frame and Sunray first applied frame
review notes stating what is accepted or still unclear
```

Minimum acceptance:

- the map is visible and nonblack;
- the Sunray150 body is visible by eye, not only by log;
- at least one after-stream close or zoomed screenshot shows the vehicle
  clearly;
- preferably include front/side/top or three-quarter views so pillars, distance,
  or scene geometry cannot hide the aircraft;
- for replay-motion claims, include a short frame/sequence/timestamp screenshot
  series or video instead of one static far view;
- primitive/STL fallback is not accepted as the vehicle visual;
- keyboard/camera controls do not move the UAV truth;
- no final material acceptance is claimed unless component close-ups are also
  reviewed.

### Path B: Command-Echo Live Probe

Goal: run exactly one bounded live command-echo probe and validate the
seven-artifact bundle.

Required artifacts:

```text
runtime_probe_manifest.json
pending_request_capture.json
authoritative_echo_capture.json
request_echo_match_report.json
no_pose_overwrite_report.json
false_ack_negative_report.json
timeout_cleanup_manifest.json
```

Minimum acceptance:

- `authoritative_echo_capture.json` source is one of
  `MWORKS_live_downlink`, `ROS2_runtime_echo`, or
  `MWORKS_ROS2_live_downlink`;
- request id, run id, sequence, time, command kind, and status match the
  pending request;
- no pose overwrite or forbidden command path is observed;
- build success, checker success, sender success, UDP send success,
  fixture-only echo, operator intent, and `quadrotor.unreal_state.v1` frames
  are rejected as false ack sources;
- cleanup proves no listener, timer, background loop, or socket remains bound.

Use:

```text
Scripts/UE5/check_ue_runtime_probe_capture_bundle_validator.py --bundle-dir <future_live_bundle_dir>
```

The checker validates the bundle after the future live probe produces files.
It does not itself run UE runtime or create live acknowledgement.
