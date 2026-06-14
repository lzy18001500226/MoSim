# Rotor Effectiveness Static Checker Alignment

Date: 2026-06-11 CST

Status: passed static validation.

## Scope

This slice aligned the current Sunray150/RflySim-style rotor-effectiveness
source with the project static validators and tests.

No live MWORKS, Sysplorer, Syslab, MCP, `check_model`, `SimulateModel`, ROS2,
UE, GUI operation, visible-thread dispatch, controller-performance check, or
closed-loop claim was performed.

## Source Changes

- `Models/QuadrotorExperiments/DynamicsUpgrade/Sunray150ActuatorMappedWrapperSurface.mo`
  now forwards `minimum_thrust_effectiveness` and
  `minimum_reaction_moment_effectiveness` from `WrapperSurface`.
- `Scripts/mworks/validate_mosimquad_wrapper_surface.py` now checks
  effectiveness-aware command-side thrust and yaw reaction equations.
- `Scripts/mworks/validate_mosimquad_actuator_mapped_wrapper_surface.py` now
  checks the wrapper effectiveness monitors and actuator-mapped pass-through.
- `Scripts/tests/test_sunray150_dynamics_upgrade_model.py` now reads the real
  dynamics implementation file and treats the top-level package as a
  compatibility alias.

## Evidence Outputs

- `Results/mworks_model_hygiene/20260608_026_mosimquad_wrapper_surface_formal_source_surface/static_validation_summary.json`
- `Results/mworks_model_hygiene/20260609_030_mosimquad_actuator_mapped_wrapper_formal_source_surface_backup/static_validation_summary.json`
- `Results/mworks_model_hygiene/20260608_025_mosimquad_rotor_actuator_core_formal_source_surface/static_validation_summary.json`
- `Results/mworks_model_hygiene/20260608_023_mosimquad_formal_smoke_surface_static_prep/static_validation_summary.json`

## Checks

- `python -m pytest Scripts/tests/test_sunray150_dynamics_upgrade_model.py`
- `python Scripts/tests/test_mosimquad_wrapper_surface.py`
- `python Scripts/tests/test_mosimquad_actuator_mapped_wrapper_surface.py`
- `python Scripts/tests/test_mosimquad_rotor_actuator_core_surface.py`
- `python Scripts/mworks/validate_mosimquad_wrapper_surface.py`
- `python Scripts/mworks/validate_mosimquad_actuator_mapped_wrapper_surface.py`
- `python Scripts/mworks/validate_mosimquad_rotor_actuator_core_surface.py`
- `python Scripts/mworks/validate_mosimquad_formal_smoke_surface.py`
- exact old-anchor search over `Scripts/mworks` and `Scripts/tests`
- touched-path `git diff --check`

## Claim Boundary

The current source and static validators are aligned for per-rotor thrust
effectiveness and reaction-moment effectiveness. Live model acceptance still
requires explicit authorization for MWORKS activation/window precheck,
`check_model`, and the nominal hover/yaw/effectiveness smoke simulation slice.
