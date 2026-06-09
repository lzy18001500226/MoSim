# UE 035 Producer/Capture/Cleanup Route Contract

- ok: True
- scope: source-static producer/capture/cleanup route contract
- source_static_route_contract_ready: True
- runtime_route_ready_now: False
- live_attempt_consumed: False
- runtime_probe_executed: False

## Route Readiness Matrix

- authoritative_producer_identity -> runtime_probe_manifest.json: contract_defined_now=True, current_runtime_ready=False
- pending_request_capture -> pending_request_capture.json: contract_defined_now=True, current_runtime_ready=False
- authoritative_echo_capture -> authoritative_echo_capture.json: contract_defined_now=True, current_runtime_ready=False
- request_echo_identity_match -> request_echo_match_report.json: contract_defined_now=True, current_runtime_ready=False
- no_pose_overwrite_proof -> no_pose_overwrite_report.json: contract_defined_now=True, current_runtime_ready=False
- false_ack_negative_proof -> false_ack_negative_report.json: contract_defined_now=True, current_runtime_ready=False
- timeout_cleanup_proof -> timeout_cleanup_manifest.json: contract_defined_now=True, current_runtime_ready=False

## Future Preconditions

- PMO explicitly authorizes a single bounded UE runtime/editor probe after this contract is implemented as live routes.
- A producer route supplies source/ack_authority plus producer_surface/producer_instance_id/capture_session_id/transport_capture_id.
- A pending mosim.ue_command.v1 request is captured before any echo is ingested.
- A runtime mosim.ue_command_echo.v1 row from an allowed source/authority pair is captured and fed through the receiver surface.
- Request/echo identity match passes for run_id/request_id/seq/time_s/command kind/status.
- No-pose-overwrite proof passes and no forbidden pose shortcut is observed.
- False-ack negative report rejects static/build/checker/sender/operator/fixture/frame rows.
- Timeout cleanup manifest proves one attempt, timeout <= 60 seconds, retry_count=0, and no leftover socket/listener/timer/thread/background loop/accepted UI.

## Claim Boundary

- 035 proves only a source/static producer/capture/cleanup route contract for a future bounded UE runtime command-echo probe.
- 035 does not open Unreal Editor, PIE, standalone runtime, game window, or UE runtime.
- 035 does not run Unreal build, bind sockets, start listeners/timers/threads/background loops, or execute live transport.
- 035 does not edit UE C++ source, Blueprint, UMG, Slate/Web UI, assets, materials, maps, project settings, Sunray/PBR/Blender, MWORKS, ROS2, FAST-LIO, planner, controller, MoSimQuadrotorModel, References, CoAgent runtime, or Git.
- 035 checker/test/static rows, 034 preflight blocker, 033 readiness, 032 wiring, 031 compile success, 030 source surface, 029 validator success, sender success, fixture rows, operator intent, and quadrotor.unreal_state frames are not live runtime ack.
- 034 remains the latest bounded live preflight and records live_attempt_consumed=false and runtime_probe_executed=false.
- 035 does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime echo, final UI acceptance, planner_ready, FAST-LIO success, controller performance, mission success, or closed_loop.
