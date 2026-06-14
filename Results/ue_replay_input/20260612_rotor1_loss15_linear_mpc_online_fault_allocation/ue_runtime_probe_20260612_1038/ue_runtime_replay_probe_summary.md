# UE Runtime Replay Probe Summary

Status: `runtime_ingest_pass_visual_uav_hidden_fix_needed`

## Passed

- UE game window launched and Factory scene is visible.
- `quadrotor.unreal_state.v1` first frame was received by UE.
- Sunray playback actor applied the first frame.

## Blocking Visual Gap

Sunray visual component is still hidden at runtime: `SunrayDaeDerivedVehicleAfterFirstFrame visible=false hidden_in_game=true`. Fix this before claiming visual replay acceptance.

## Evidence

- Launch: `Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1038/ue_runtime_launch_manifest.json`
- Stream log: `Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1038/stream_unreal_udp_120frames.log`
- UE log tail: `Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1038/ue_log_tail_after_stream.txt`
- Screenshot after stream: `Results/ue_replay_input/20260612_rotor1_loss15_linear_mpc_online_fault_allocation/ue_runtime_probe_20260612_1038/screenshots_after_stream/94848_0xA70B38_MoSimSceneLibrary （64-位 Development PCD3D_SM6） .png`
