# UE Runtime Replay Probe Summary

Status: `runtime_ingest_and_visual_uav_visible_pass`

## Proven

- Imported the accepted Sunray150 FBX into UE Content as `/Game/Sunray150/sunray150_with_mid360_textured`.
- Launched UE runtime process `101392` with the Factory/Demonstration map.
- Captured nonempty UE window screenshots before and after streaming.
- Streamed `120` MWORKS frames from the accepted rotor1-loss run to `udp://127.0.0.1:5005`.
- UE log confirms the first MWORKS UDP frame was received.
- UE log confirms `MoSim Sunray first applied frame`.
- UE log confirms `SunrayDaeDerivedVehicleAfterFirstFrame visible=true hidden_in_game=false` with nonzero bounds.

## Evidence

- Import JSON: `Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/sunray150_runtime_static_mesh_import_20260612_1100.json`
- Launch manifest: `Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1105/ue_runtime_launch_manifest.json`
- Stream log: `Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1105/stream_unreal_udp_120frames.log`
- UE log tail: `Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1105/ue_log_tail_after_stream.txt`
- Screenshot manifests:
  - `Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1105/screenshots/capture_manifest.json`
  - `Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1105/screenshots_after_stream/capture_manifest.json`

## Boundary

This is UE visual/replay runtime evidence only. It is not authoritative UE command echo ack, ROS2 planner readiness, FAST-LIO evidence, final material acceptance, controller-performance evidence, or multi-UAV formation readiness.
