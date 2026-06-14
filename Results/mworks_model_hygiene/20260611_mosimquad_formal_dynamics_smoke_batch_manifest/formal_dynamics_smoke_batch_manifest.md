# MoSimQuadrotorModel Formal Dynamics Smoke Batch Manifest

Status: `passed`

Static-only manifest. It prepares the future live batch command but does not call MWORKS, Sysplorer, MCP, `check_model`, or `SimulateModel`.

## Scenario Files

- `Config/scenarios/diagnostics/mosimquad_dynamics_hover_smoke.yaml`
- `Config/scenarios/diagnostics/mosimquad_dynamics_physical_wrench_hover_smoke.yaml`
- `Config/scenarios/diagnostics/mosimquad_dynamics_physical_wrench_yaw_step_smoke.yaml`
- `Config/scenarios/diagnostics/mosimquad_dynamics_rotor_effectiveness_smoke.yaml`
- `Config/scenarios/diagnostics/mosimquad_dynamics_wrapper_hover_smoke.yaml`
- `Config/scenarios/diagnostics/mosimquad_dynamics_wrapper_yaw_step_smoke.yaml`
- `Config/scenarios/diagnostics/mosimquad_dynamics_yaw_step_smoke.yaml`

## Future Live Command

```powershell
D:\Dev\Anaconda3\python.exe Scripts/mworks/run_mworks_batch.py --no-gui-result-viewer --no-gui-open Config/scenarios/diagnostics/mosimquad_dynamics_hover_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_physical_wrench_hover_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_physical_wrench_yaw_step_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_rotor_effectiveness_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_wrapper_hover_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_wrapper_yaw_step_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_yaw_step_smoke.yaml
```

## Dry Run Command

```powershell
D:\Dev\Anaconda3\python.exe Scripts/mworks/run_mworks_batch.py --dry-run --no-gui-result-viewer --no-gui-open Config/scenarios/diagnostics/mosimquad_dynamics_hover_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_physical_wrench_hover_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_physical_wrench_yaw_step_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_rotor_effectiveness_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_wrapper_hover_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_wrapper_yaw_step_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_yaw_step_smoke.yaml
```

## Preconditions

- User or PMO explicitly authorizes live MWORKS/Sysplorer/Syslab execution.
- CoAgentOps/PMO or the live task provides a current non-blocking MWORKS activation/window preflight.
- Stop before execution on demo, login, activation, authorization, GUI error-report, mixed license, visible unknown, unavailable, or unknown state.
- The runner must consume model.live_load_strategy=minimal_dynamics_only, or the task must use an explicitly reviewed native MCP minimal-loading sequence.
- All formal check_model targets in the 024 live-gate plan pass before treating SimulateModel outputs as evidence.

## Claim Boundary

- This manifest prepares a future live batch command only.
- It does not run or prove MWORKS load, check_model, SimulateModel, result variables, controller performance, mission success, or closed_loop.
- RotorEffectivenessSmoke remains a single-rotor effectiveness observability smoke, not controller robustness acceptance.
