# Phase 5 Thrust Diagnosis

## Problem Statement

All 15 Phase 4 passing controllers failed Phase 5 simulation with ~12km final position error. Investigation revealed the vehicle falls -12249m in 50 seconds instead of climbing to +15m.

## Physics Configuration (CORRECT)

From CascadePid simulation at t=50s:

```json
{
  "gravity_direction": [0.0, 0.0, -1.0],
  "gravity_magnitude_mps2": 9.80665,
  "body_mass_kg": 1.0,
  "expected_weight_N": 9.80665
}
```

- Gravity direction: [0, 0, -1] ✓ (downward in world Z)
- Gravity magnitude: 9.80665 m/s² ✓ (standard Earth gravity)
- Body mass: 1.0 kg ✓ (matches profile)
- Expected weight: 9.80665 N ✓

## Actuator Output (CATASTROPHICALLY WRONG)

```json
{
  "wrapper_thrust_N_at_t50": 0.002336,
  "applied_force_z_body_N_at_t50": 0.002336,
  "hover_weight_balance_error_N_at_t50": -9.804314
}
```

- **Wrapper thrust at t=50s: 0.002336 N** ✗
- Applied force Z (body): 0.002336 N ✗
- Hover weight balance error: -9.804 N ✗

## Root Cause: ZERO THRUST PRODUCTION

The rotor actuator system is producing **0.002 N of thrust** when it should be producing **~9.8 N to hover** (1:1 thrust-to-weight ratio at minimum).

- Expected hover thrust: ≥9.8 N (to counteract 9.8 N weight)
- Actual thrust at t=50s: 0.002 N
- **Thrust deficit: 99.976%** — the motors are essentially off

The controller is commanding the motors, but the thrust is not being generated. This explains why the vehicle free-falls at -245 m/s average velocity.

## Position Result (Consequence)

```json
{
  "position_at_t50": [0.004, -0.010, -12249.286]
}
```

With near-zero thrust opposing 9.8 N weight, the vehicle experiences free-fall:
- Z acceleration: -9.8 m/s² (gravity only)
- Z velocity after 50s: -490 m/s
- Z displacement: 0.5 × (-9.8) × 50² = -12250 m ✓

The -12249m result matches free-fall physics precisely.

## Investigation Path

1. ✅ Gravity configuration correct
2. ✅ Body mass correct
3. ✅ Thrust application chain intact (PhysicalWrenchAdapter line 89: `applied_force_body = {0, 0, wrapper.total_thrust}`)
4. ✗ **Rotor wrapper producing zero thrust**

## Rotor Dynamics Investigation

### Motor Command and Speed Timeline

```json
{
  "t0": {
    "rotor_command": [0.6515, 0.6515, 0.6515, 0.6515],
    "rotor_speed_rad_s": [64.79, -64.79, 64.79, -64.79],
    "rotor_thrust_N": [2.452, 2.452, 2.452, 2.452],
    "total_thrust_N": 9.807
  },
  "t10": {
    "rotor_command": [1.0, 1.0, 1.0, 1.0],
    "rotor_speed_rad_s": [1.0, 1.0, 1.0, 1.0],
    "rotor_thrust_N": [0.000584, 0.000584, 0.000584, 0.000584],
    "total_thrust_N": 0.002336
  },
  "t50": {
    "rotor_command": [1.0, 1.0, 1.0, 1.0],
    "rotor_speed_rad_s": [1.0, 1.0, 1.0, 1.0],
    "rotor_thrust_N": [0.000584, 0.000584, 0.000584, 0.000584],
    "total_thrust_N": 0.002336
  }
}
```

### ROOT CAUSE IDENTIFIED: Motor Command Saturation at 1.0 rad/s

**The controller is saturating motor commands at 1.0 rad/s, but the actuator dynamics interpret this as ROTOR SPEED in rad/s, not normalized thrust command.**

From RotorActuatorCore.mo:
- Line 32: `Real motor_command[4](each unit = "rad/s")` — expects SIGNED ROTOR SPEED
- Line 62: `nominal_thrust[i] = lift_coefficient * omega[i] * omega[i]` — thrust ∝ ω²
- Line 61: `der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i]` — first-order lag to commanded speed

At t=0:
- Initial rotor speed: ±64.79 rad/s (hover speed from line 13-17)
- Rotor command: 0.6515 rad/s (WRONG — this is normalized [0,1] command from controller)
- Actual rotor speed after transient: 64.79 rad/s ✓
- Thrust per rotor: 2.452 N ✓
- Total thrust: 9.807 N ✓ (hovers correctly)

At t=10-50:
- Controller commands: 1.0 (thinks it's normalized [0,1] command)
- Rotor dynamics interprets: 1.0 rad/s ABSOLUTE SPEED
- Actual rotor speed converges to: 1.0 rad/s (from 64.79 → 1.0 via first-order lag)
- Thrust per rotor: Ct × 1.0² = 0.000584 N
- Total thrust: 0.002336 N (99.976% loss)

**The controller outputs normalized [0,1] commands, but the plant expects absolute rotor speed in rad/s (nominally ~65 rad/s for hover).**

### Proof from Thrust Equation

Expected hover:
- Hover rotor speed: sqrt(m×g / (4×Ct)) = sqrt(1.0×9.807 / (4×0.584)) = 64.79 rad/s ✓
- Thrust at 64.79 rad/s: 0.584 × 64.79² = 2.452 N per rotor ✓
- Total: 9.807 N ✓

Actual after command=1.0:
- Rotor speed: 1.0 rad/s (interpreted literally)
- Thrust at 1.0 rad/s: 0.584 × 1.0² = 0.000584 N per rotor ✓
- Total: 0.002336 N ✓ (matches measurement)

## Root Cause Summary

**Interface mismatch between controller output and plant input:**
- Controller expects: normalized thrust command [0, 1] → plant scales to rotor speed
- Plant expects: absolute rotor speed in rad/s (physical quantity)
- Consequence: controller command=1.0 is interpreted as 1.0 rad/s instead of 100% thrust (~65 rad/s)

This explains why all 15 controllers fail identically — they all use the same normalized [0,1] command convention, but the Sunray150Assembly rotor_command interface expects absolute speed in rad/s.

## Next Steps

1. Find the interface adapter that should scale normalized [0,1] → absolute rad/s
2. Check if Runner → Sunray150Assembly connection is missing the scaling layer
3. Verify expected input range for `Sunray150Assembly.rotor_command[4]` in specification
4. Fix the interface to accept normalized commands OR add scaling in Runner output

## Files

- Investigation date: 2026-08-19
- Test controller: CascadePid
- Root cause: Controller-plant interface mismatch (normalized [0,1] vs absolute rad/s)
- Expected hover command: ~64.79 rad/s, actual controller output: 1.0
