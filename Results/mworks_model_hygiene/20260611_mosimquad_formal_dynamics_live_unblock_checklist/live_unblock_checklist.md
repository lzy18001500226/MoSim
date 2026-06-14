# Formal Dynamics Live Unblock Checklist

Status: `blocked_needs_user_or_pmo_ui_decision`
Unblock state: `blocked_needs_user_or_pmo_ui_decision`
Reason: current MWORKS surface still reports upgrade_model_surface_blocked

This is a static/read-only checklist. It does not call MWORKS, Sysplorer, MCP, `check_model`, `SimulateModel`, or any GUI/window action.

## Operator Checklist

- If the upgrade-model surface is still present, stop live smoke and ask PMO/user for a UI decision.
- After the surface is cleared by an authorized owner, collect a fresh sentinel or foreground/maximized target-main-window evidence.
- Run the static readiness guard again before any live smoke command.
- Run the future live command only with no GUI result viewer and no GUI open flags.
- After live output exists, run the result-acceptance checker before using any result in a report or controller claim.

## Stop Conditions

- 升级模型 or any model-upgrade/progress modal remains visible
- login, activation, authorization, license, demo, mixed-license, GUI error-report, crash, save, restart, or unknown window
- classifier output is missing, stale, or not explicitly clean

## Allowed Command After Fresh Clean Evidence

```powershell
D:\Dev\Anaconda3\python.exe Scripts/mworks/run_mworks_batch.py --no-gui-result-viewer --no-gui-open Config/scenarios/diagnostics/mosimquad_dynamics_hover_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_physical_wrench_hover_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_physical_wrench_yaw_step_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_rotor_effectiveness_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_wrapper_hover_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_wrapper_yaw_step_smoke.yaml Config/scenarios/diagnostics/mosimquad_dynamics_yaw_step_smoke.yaml
```

## Claim Boundary

- This checklist is an executable gate for future live work only.
- It does not prove live load, check_model, SimulateModel, result variables, controller performance, mission success, or closed_loop.
- It does not authorize automatic GUI clicking, closing, restart, login, save, or model-upgrade confirmation.

## Findings

- none
