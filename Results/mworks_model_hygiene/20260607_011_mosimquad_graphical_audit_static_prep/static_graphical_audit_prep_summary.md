# 011 Static Graphical Audit Prep

Request: `PMO-MWORKS-R2-MOSIMQUAD-GRAPHICAL-AUDIT-STATIC-PREP-20260607-011`

## Summary

- Formal root category count: 11.
- Candidate count: 126.
- Ready for serialized live audit: 109.
- Needs static fix first: 0.
- Blocked by missing source: 0.
- Low priority/package-browser-only: 17.
- External standard library base `Modelica.Icons.Package` is not counted as missing project source.
- Dynamics queue includes current formal entries only; old Sunray150* source-file names are not treated as formal candidates unless wrapped by MoSimQuadrotorModel.Dynamics.

## Highest Priority Live Audit Queue Heads

- 001 `MoSimQuadrotorModel.Controllers` -> ready_for_live_audit / P1 / package_browser_root
- 002 `MoSimQuadrotorModel.Dynamics` -> ready_for_live_audit / P1 / package_browser_root
- 003 `MoSimQuadrotorModel.Formation` -> ready_for_live_audit / P1 / package_browser_root
- 004 `MoSimQuadrotorModel.Missions` -> ready_for_live_audit / P1 / package_browser_root
- 005 `MoSimQuadrotorModel.Planning` -> ready_for_live_audit / P1 / package_browser_root
- 006 `MoSimQuadrotorModel.Robustness` -> ready_for_live_audit / P1 / package_browser_root
- 007 `MoSimQuadrotorModel.SceneTrace` -> ready_for_live_audit / P1 / package_browser_root
- 008 `MoSimQuadrotorModel.Support` -> ready_for_live_audit / P1 / package_browser_root
- 009 `MoSimQuadrotorModel.System` -> ready_for_live_audit / P1 / package_browser_root
- 010 `MoSimQuadrotorModel.Baseline` -> low_priority / P2 / package_browser_root
- 011 `MoSimQuadrotorModel.LegacyCompatibility` -> low_priority / P3 / package_browser_root
- 012 `MoSimQuadrotorModel.Baseline.OfficialExample1` -> ready_for_live_audit / P1 / graphical_high_priority
- 013 `MoSimQuadrotorModel.Baseline.OfficialExample2` -> ready_for_live_audit / P1 / graphical_high_priority
- 014 `MoSimQuadrotorModel.Baseline.OfficialExample3` -> ready_for_live_audit / P1 / graphical_high_priority
- 015 `MoSimQuadrotorModel.Baseline.OfficialQuadChassis` -> ready_for_live_audit / P1 / graphical_high_priority
- 016 `MoSimQuadrotorModel.Controllers.AWFFPidBlocks` -> ready_for_live_audit / P1 / graphical_high_priority
- 017 `MoSimQuadrotorModel.Controllers.DemosAndSIL` -> ready_for_live_audit / P1 / graphical_high_priority
- 018 `MoSimQuadrotorModel.Controllers.FaultAllocationControllers` -> ready_for_live_audit / P1 / graphical_high_priority
- 019 `MoSimQuadrotorModel.Controllers.InnovationControllers` -> ready_for_live_audit / P1 / graphical_high_priority
- 020 `MoSimQuadrotorModel.Controllers.LinearMPCControllers` -> ready_for_live_audit / P1 / graphical_high_priority

## Boundary

- Static source inventory only; no MWORKS/Sysplorer/Syslab GUI, screenshots, MCP, check_model, simulation, Smart Layout, or diagram writeback was used.
- This does not claim package-browser acceptance, wiring/layout acceptance, controller performance, planner readiness, runtime ack, mission success, or closed_loop.
