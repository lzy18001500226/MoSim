# UE 036 Producer/Capture/Cleanup Implementation Surface

- ok: True
- source_static_implementation_surface_ready: True
- runtime_route_ready_now: False
- live_attempt_consumed: False
- runtime_probe_executed: False

## Implementation Surface Rows

- pending_request_capture -> BuildPendingRequestCaptureJson -> pending_request_capture.json: declared=True, defined=True, runtime_ready=False
- runtime_probe_manifest -> BuildRuntimeProbeManifestJson -> runtime_probe_manifest.json: declared=True, defined=True, runtime_ready=False
- authoritative_echo_capture -> BuildAuthoritativeEchoCaptureJson -> authoritative_echo_capture.json: declared=True, defined=True, runtime_ready=False
- request_echo_match_report -> BuildRequestEchoMatchReportJson -> request_echo_match_report.json: declared=True, defined=True, runtime_ready=False
- no_pose_overwrite_report -> BuildNoPoseOverwriteReportJson -> no_pose_overwrite_report.json: declared=True, defined=True, runtime_ready=False
- false_ack_negative_report -> BuildFalseAckNegativeReportJson -> false_ack_negative_report.json: declared=True, defined=True, runtime_ready=False
- timeout_cleanup_manifest -> BuildTimeoutCleanupManifestJson -> timeout_cleanup_manifest.json: declared=True, defined=True, runtime_ready=False

## Future Live Probe Preconditions

- PMO explicitly authorizes a single bounded UE runtime/editor probe after the source/static surface receives an executable live producer route.
- A producer instance supplies source/ack_authority plus producer_surface/producer_instance_id/capture_session_id/transport_capture_id.
- BuildPendingRequestCaptureJson captures a mosim.ue_command.v1 pending request before any echo is ingested.
- BuildAuthoritativeEchoCaptureJson captures a mosim.ue_command_echo.v1 row from an allowed source/authority pair.
- BuildRequestEchoMatchReportJson reports matching run_id/request_id/seq/time_s/command kind/status.
- BuildNoPoseOverwriteReportJson and BuildFalseAckNegativeReportJson reject pose shortcuts and static/build/checker/sender/operator/fixture/frame rows.
- BuildTimeoutCleanupManifestJson proves timeout <= 60 seconds, attempt=1, retry=0, cleanup complete, and no leftover runtime loop/socket/listener/timer/accepted UI.

## Claim Boundary

- 036 proves only source/static implementation-surface materialization for future producer/capture/cleanup artifacts.
- 036 does not open Unreal Editor, PIE, standalone runtime, game window, or UE runtime.
- 036 does not run Unreal build, bind sockets, start listeners/timers/threads/background loops, or execute live transport.
- 036 does not edit Blueprint, UMG, Slate/Web UI, assets, materials, maps, project settings, Sunray/PBR/Blender, MWORKS, ROS2, FAST-LIO, planner, controller, MoSimQuadrotorModel, References, CoAgent runtime, Codex App private state, visible-thread lifecycle, or Git.
- 036 checker/test/static rows, source-static implementation methods, sender packet construction, fixture rows, operator intent, build success, and quadrotor.unreal_state frames are not live runtime ack.
- 034 remains the latest bounded live preflight and records live_attempt_consumed=false and runtime_probe_executed=false.
- 036 does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime echo, final UI acceptance, planner_ready, FAST-LIO success, controller performance, mission success, or closed_loop.
