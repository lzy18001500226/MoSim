# UE 032 Runtime Echo Receiver Capture Bundle Wiring

- ok: True
- scope: source-static wiring/checker
- source_static_wiring_ready: True
- runtime_probe_executed: False
- authoritative_runtime_ack_claimable_now: False

## Wiring Matrix

- runtime_probe_manifest.json: future probe identity and source/authority metadata; not ingested by the receiver component
- pending_request_capture.json: precondition only; receiver surface must not synthesize or parse pending mosim.ue_command.v1 requests
- authoritative_echo_capture.json: future authoritative mosim.ue_command_echo.v1 payload enters through Validate/Ingest receiver methods
- request_echo_match_report.json: receiver sink path is not enough by itself; future bundle must prove pending/echo identity match
- no_pose_overwrite_report.json: receiver surface must contain no pose shortcuts and future echo must include no_pose_overwrite_status=pass
- false_ack_negative_report.json: receiver wiring must reject build/checker/sender/fixture/operator/frame/static rows as live ack
- timeout_cleanup_manifest.json: source-static receiver has no listener/timer/socket cleanup burden; future probe still must prove cleanup

## Matrix Summary

- capture_artifact_rows: 7
- false_ack_negative_rows: 26
- direct_receiver_input_rows: 1
- runtime_ack_leaks_now: 0
- live_transport_evidence_rows: 0
- authoritative_runtime_ack_claimable_now: False

## Claim Boundary

- 032 proves only source-static wiring between the compiled UE receiver surface and the 029 capture-bundle validator contract.
- 032 does not open Unreal Editor, PIE, standalone runtime, or UE runtime.
- 032 does not run Unreal build, bind sockets, start listeners/timers/background loops, or execute live transport.
- 032 does not edit UE C++ source, Blueprint, UMG, assets, materials, maps, project settings, Sunray/PBR/Blender, MWORKS, ROS2, FAST-LIO, planner, controller, MoSimQuadrotorModel, References, CoAgent runtime, or Git.
- 032 checker/test/static rows, 031 compile success, 030 source surface, 029 validator success, sender success, fixture rows, operator intent, and quadrotor.unreal_state frames are not live runtime ack.
- 032 does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime echo, final UI acceptance, planner_ready, FAST-LIO success, controller performance, mission success, or closed_loop.
