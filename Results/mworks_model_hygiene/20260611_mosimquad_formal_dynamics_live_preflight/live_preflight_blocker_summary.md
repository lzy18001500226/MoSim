# Formal Dynamics Live Preflight Blocker

Status: `blocked_by_upgrade_model_surface`

The first live attempt reached Sysplorer but did not reach `check_model`.

## Blocker

- blocked operation: `model_manager.load_file Models/MoSimQuadrotorModel/package.mo`
- surface: `upgrade_model_modal_or_progress_window`
- reason: Top-level MoSimQuadrotorModel load entered a broad package/dependency load and exposed an unknown MWORKS '升级模型' window; MCP session probe then timed out. No click/confirm/close/restart was performed.

## Evidence

- initial sentinel: `Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_live_preflight/sentinel_before_minimal_retry_20260611_234254.json`
- post-timeout sentinel: `Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_live_preflight/sentinel_after_load_timeout_20260611_231549.json`
- current upgrade classifier sentinel: `Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_live_preflight/current_gui_sentinel_after_upgrade_classifier_20260611_234725.json`
- current classifier: `{'status': 'incident_detected', 'error_kind': 'gui_blocked', 'license_state_hint': 'upgrade_model_surface_blocked', 'upgrade_model_window_count': 1, 'all_window_license_gate': 'blocked'}`
- main-window capture manifest: `Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_live_preflight/window_capture_20260611_231614/capture_manifest.json`
- upgrade-window capture manifest: `Results/mworks_model_hygiene/20260611_mosimquad_formal_dynamics_live_preflight/upgrade_window_capture_20260611_231717/capture_manifest.json`

## Next Strategy

- Use `model.live_load_strategy: minimal_dynamics_only` for formal Dynamics diagnostic smoke scenarios.
- Do not auto-click or close the upgrade-model window.
- Do not claim runtime success until a future live task reaches `check_model`, `SimulateModel`, and result-variable probes.

## Scenarios

- `Config/scenarios/diagnostics/mosimquad_dynamics_hover_smoke.yaml` -> `MoSimQuadrotorModel.Dynamics.HoverSmoke` strategy=`minimal_dynamics_only`
- `Config/scenarios/diagnostics/mosimquad_dynamics_physical_wrench_hover_smoke.yaml` -> `MoSimQuadrotorModel.Dynamics.PhysicalWrenchHoverSmoke` strategy=`minimal_dynamics_only`
- `Config/scenarios/diagnostics/mosimquad_dynamics_physical_wrench_yaw_step_smoke.yaml` -> `MoSimQuadrotorModel.Dynamics.PhysicalWrenchYawStepSmoke` strategy=`minimal_dynamics_only`
- `Config/scenarios/diagnostics/mosimquad_dynamics_rotor_effectiveness_smoke.yaml` -> `MoSimQuadrotorModel.Dynamics.RotorEffectivenessSmoke` strategy=`minimal_dynamics_only`
- `Config/scenarios/diagnostics/mosimquad_dynamics_wrapper_hover_smoke.yaml` -> `MoSimQuadrotorModel.Dynamics.WrapperHoverSmoke` strategy=`minimal_dynamics_only`
- `Config/scenarios/diagnostics/mosimquad_dynamics_wrapper_yaw_step_smoke.yaml` -> `MoSimQuadrotorModel.Dynamics.WrapperYawStepSmoke` strategy=`minimal_dynamics_only`
- `Config/scenarios/diagnostics/mosimquad_dynamics_yaw_step_smoke.yaml` -> `MoSimQuadrotorModel.Dynamics.YawStepSmoke` strategy=`minimal_dynamics_only`
