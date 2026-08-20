# Phase 5 Position Connection Bug Investigation

## Problem Summary

All 15 passing controllers from Phase 4 failed Phase 5 simulation with ~12km final position error. Root cause: `plant.position` output connector is **not** propagating actual vehicle position to the Runner's `position[3]` variable.

## Evidence

### Reference Trajectory (Correct)
At t=50s, ClimbTrajectory (scenario_mode=0):
- `reference.position_command = [10.0, 10.0, 15.0]` ✓
- `position_ref = [10.0, 10.0, 15.0]` ✓

### Actual Position (WRONG)
At t=50s:
- `position = [0.003, -0.010, -12249.27]` ✗
- X and Y near zero (should be 10m)
- Z = -12249m (should be 15m)

### Position Error
- `position_error_norm = 12264.29m` 
- Error = sqrt((10-0)^2 + (10-0)^2 + (15-(-12249))^2) ≈ 12264m ✓ (calculation is correct)

## Root Cause

From `CascadePidGraphicalRunner.mo:104`:
```modelica
position = plant.position;
```

From `Sunray150Assembly.mo:40-43`:
```modelica
Modelica.Blocks.Interfaces.RealOutput position[3] 
  annotation(Placement(
    transformation(origin = {220, 85}, extent = {{-10, -10}, {10, 10}}),
    iconTransformation(origin = {100, 80}, extent = {{-5, -5}, {5, 5}})));
```

The `plant.position` output connector is **declared** but **never assigned** in the Sunray150Assembly equation section. The multibody component `physical.body` has internal state `r_0` (world-frame position), but this is not exposed through the output connector.

## Impact

- Phase 4: 15/41 controllers PASS CheckModel (36.6%)
- Phase 5: 0/15 controllers PASS simulation (0%)
- **All 15 simulations ran successfully**, but position feedback was disconnected
- Controllers commanded aircraft correctly, but the error metric is meaningless

## Root Cause Analysis

### Connection Chain Verified
1. `Sunray150Assembly.mo:126`: `position = sensors.PosMea;` ✓
2. `Sensors.mo:75-78`: `connect(absolutePosition1.r, PosMea)` ✓
3. `sensors.PosMea[1..3]` at t=50s = `[0.003, -0.010, -12249.27]` (WRONG)
4. `physical.body.r_0[1..3]` at t=50s = `[0.003, -0.010, -12249.27]` (SAME WRONG VALUE)

### Multibody Integration Failure
- Initial position (t=0): `[0, 0, 0]` ✓
- Final position (t=50): `[0.003, -0.010, -12249.27]` ✗
- Expected final position: `[10, 10, 15]`
- **Z-axis fell 12249 meters in 50 seconds** = -244.98 m/s average velocity

The multibody `Body` component's position integrator diverged. The vehicle's actual dynamics simulation is **catastrophically wrong** — the aircraft is not tracking the reference trajectory at all; it's free-falling at ~25× gravity.

### Hypothesis
Either:
1. Rotor thrust forces are not being applied to the multibody body
2. Gravity is being applied with wrong sign or magnitude
3. Mass/inertia parameters are orders of magnitude off
4. Integration tolerance/method is unstable for this system

This is NOT a signal connection bug — it's a **physics simulation divergence**.

## Next Steps

1. Check `Sunray150Assembly.mo` for rotor thrust application to `physical.body`
2. Verify gravity direction and magnitude in multibody world
3. Check if mass/inertia are reasonable (m=1kg, Ixx=0.01 kg·m²)
4. Try tighter integration tolerance or different solver method
5. Instrument rotor thrust values to see if control commands reach actuators

## Files

- Issue discovered: 2026-08-19
- Root cause: Multibody dynamics simulation divergence (z-axis free-fall at -245 m/s)
- Affected models: All 15 Phase 4 passing controllers
- Investigation script: Phase 5 batch simulation via MCP
