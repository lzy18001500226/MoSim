# UE 033 Single Bounded Runtime Probe Plan

- ok: True
- scope: source-static single-bounded-probe plan/readiness
- source_static_plan_ready: True
- runtime_probe_executed: False
- authoritative_runtime_ack_claimable_now: False
- future_probe_attempt_count: 1
- max_timeout_seconds: 60

## Seven Capture Bundle Preconditions

- runtime_probe_manifest.json: Future PMO packet explicitly authorizes exactly one bounded UE runtime/editor probe and records producer identity.
- pending_request_capture.json: Capture the matching mosim.ue_command.v1 request before any echo is accepted or rejected.
- authoritative_echo_capture.json: Capture mosim.ue_command_echo.v1 from an authoritative live source and feed it through the receiver surface Validate/Ingest methods.
- request_echo_match_report.json: Prove pending request identity matches the authoritative echo identity.
- no_pose_overwrite_report.json: Prove the probe did not use keyboard pose, direct Actor transform, teleport, pose_override, set_uav_pose, or UE truth shortcuts.
- false_ack_negative_report.json: Prove build/checker/sender/fixture/operator/static/frame rows were rejected as live command ack.
- timeout_cleanup_manifest.json: Prove the single attempt stayed within timeout and left no listener, timer, background loop, socket, or accepted-state UI running.

## Stop Triggers

- More than one live probe attempt would be required.
- Timeout would exceed 60 seconds or no cleanup manifest can be produced.
- Authoritative producer identity or source/authority pair is missing.
- Pending mosim.ue_command.v1 request capture is missing or mismatched.
- Authoritative mosim.ue_command_echo.v1 capture does not pass through the receiver surface.
- Request/echo identity fields do not match.
- No-pose-overwrite report fails or any forbidden pose shortcut appears.
- False-ack negative report accepts build/checker/sender/fixture/operator/static/frame rows.
- UE runtime/editor, MWORKS, ROS2, planner, controller, or manual review needs exceed the future packet authorization.

## Claim Boundary

- 033 proves only a source-static plan/readiness contract for one future bounded UE runtime command-echo probe.
- 033 does not open Unreal Editor, PIE, standalone runtime, game window, or UE runtime.
- 033 does not run Unreal build, bind sockets, start listeners/timers/threads/background loops, or execute live transport.
- 033 does not edit UE C++ source, Blueprint, UMG, Slate/Web UI, assets, materials, maps, project settings, Sunray/PBR/Blender, MWORKS, ROS2, FAST-LIO, planner, controller, MoSimQuadrotorModel, References, CoAgent runtime, or Git.
- 033 checker/test/static rows, 032 wiring, 031 compile success, 030 source surface, 029 validator success, sender success, fixture rows, operator intent, and quadrotor.unreal_state frames are not live runtime ack.
- A later live probe requires a separate PMO task packet with explicit runtime authorization, one-attempt budget, timeout, cleanup, capture bundle, false-ack negative report, and no-pose-overwrite proof.
- 033 does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime echo, final UI acceptance, planner_ready, FAST-LIO success, controller performance, mission success, or closed_loop.
