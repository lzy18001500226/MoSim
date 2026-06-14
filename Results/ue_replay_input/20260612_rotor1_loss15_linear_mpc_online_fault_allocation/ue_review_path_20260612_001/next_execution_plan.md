# UE Next Execution Plan, 2026-06-12

Status: `ready_for_next_executable_slice`.

This plan resets the UE stage goal after opening the existing review material.
The opened runtime screenshot proves a nonblank Factory/Demonstration UE
window, and the log supports first MWORKS UDP frame plus Sunray150 component
visibility/nonzero bounds. It still does not show the UAV clearly by eye, so it
is not final visual acceptance.

## Goal

Advance UE from nonfinal runtime replay evidence to reviewable visual evidence,
then move to command-echo live evidence only after the visual gate is not
blocked.

Critical path:

```text
1. visual_review_hardening
2. command_echo_live_probe
```

Reason: the current shortest missing evidence is a close or follow-camera
screenshot where the Sunray150 body is plainly visible. Command-echo can wait
until that visual gate is not the obvious blocker.

## Sub-Agent Plan

Disposable sidecar agents were used only for read-only review:

| Role | Scope | Result |
|---|---|---|
| UE evidence reviewer | Current review packet, screenshots, runtime summary, and log tail. | Existing images support scene/window evidence, not final UAV visual acceptance. |
| UE script inventory reviewer | `Scripts/UE5` and relevant UE workflow docs. | Identified Factory UAV platform review and command-echo validator/plan scripts. |
| Claim-boundary reviewer | UE workflow, board, and command-echo hardening evidence. | Confirmed prohibited claims and seven-artifact command-echo minimum. |

No sidecar edited files, ran UE/MWORKS/ROS2, clicked UI, or sent messages.

## Path A: Visual Review Hardening

Purpose: produce human-readable Factory scene screenshots where the Sunray150
UAV body is visible by eye.

Primary script:

```bash
Scripts/UE5/review_factory_uav_platform.sh
```

Documented follow-camera command:

```bash
FOLLOW_UAV_CAMERA=1 STREAM_FPS=60 STREAM_RESAMPLE_HZ=60 STREAM_REPLAY_SPEED=1.0 \
  Scripts/UE5/review_factory_uav_platform.sh
```

If a Factory review window is already open:

```bash
STREAM_ONLY=1 STREAM_MAX_FRAMES=1 STREAM_FPS=6 \
  Scripts/UE5/review_factory_uav_platform.sh
```

Screenshot route:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\tools\capture_window_background.ps1 `
  -TitleRegex "MoSimSceneLibrary" `
  -ProcessRegex "^UnrealEditor$" `
  -OutDir Results\ue_replay_input\20260612_rotor1_loss15_linear_mpc_online_fault_allocation\ue_visual_review_hardening_20260612_001\screenshots `
  -RestoreMinimized
```

Expected outputs:

```text
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_visual_review_hardening_20260612_001/visual_review_manifest.json
Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_visual_review_hardening_20260612_001/screenshots/capture_manifest.json
at least one after-stream close or follow-camera screenshot where the Sunray150 UAV body is visible by eye
UE log tail with first MWORKS UDP frame and Sunray first applied frame
review notes stating whether UAV visibility is accepted or still unclear
```

Stop if the window is missing, UDP port 5005 never appears, the screenshot is
blank/wrong/cropped, the UAV remains unclear after one bounded retry, the log
lacks the expected MWORKS/Sunray diagnostics, or the route would require
keyboard pose, actor transform, map save, asset edit, or any pose override.

Allowed claim after a pass: UE Factory scene rendered, imported Sunray150 is
human-visible in the UE review window, and the accepted MWORKS replay stream
reached the runtime visual path.

Still forbidden after a pass: authoritative command echo acknowledgement,
controller performance from UE, ROS2/FAST-LIO success, `planner_ready`,
multi-UAV readiness, final material acceptance, or closed-loop success beyond
the accepted MWORKS run.

## Path B: Command-Echo Live Probe

Purpose: produce and validate one seven-artifact live command-echo bundle.

Validator:

```text
Scripts/UE5/check_ue_runtime_probe_capture_bundle_validator.py --bundle-dir <future_live_bundle_dir>
```

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

The authoritative echo source must be `MWORKS_live_downlink`,
`ROS2_runtime_echo`, or `MWORKS_ROS2_live_downlink`. Build success, checker
success, sender success, UDP send success, fixture-only echo, operator intent,
and `quadrotor.unreal_state.v1` frames remain false ack sources.

## Current Runtime Observation

During this planning turn, no current `UnrealEditor.exe` process with
`MoSimSceneLibrary.uproject` was found. Therefore this turn did not attempt to
reuse a live review window for new close-up capture.
