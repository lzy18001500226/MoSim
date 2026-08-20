# Phase 5 Root Cause: Controller-Plant Interface Mismatch

## Executive Summary

All 15 Phase 4 passing controllers failed Phase 5 simulation with ~12km position error because the controller outputs normalized [0, 1] commands but the plant expects absolute rotor speed in rad/s.

**Controllers command 1.0 thinking it means "100% thrust", but the plant interprets 1.0 as "1.0 rad/s rotor speed" (99.98% thrust loss).**

## Signal Chain Analysis

From CascadePid at t=50s, complete signal tracing from controller output to plant input:

```json
{
  "core.command": 1.0,
  "output_adapter.command": 1.0,
  "output_adapter.rotor_command[1]": 1.0,
  "fault_compensator.command_in[1]": 1.0,
  "fault_compensator.command_out[1]": 1.0,
  "esc.motor_command_raw[1]": 1.0,
  "esc.motor_command[1]": 1.0,
  "motor1.command": 1.0,
  "motor1.command_to_plant": 1.0,
  "plant.rotor_command[1]": 1.0
}
```

**Every component passes 1.0 through unchanged — there is NO scaling layer anywhere in the chain.**

## Controller Output Convention

From CascadePidCore.mo:
- Line 89: `Saturation outer_command_limit(upLimit=1.0, lowLimit=-1.0)`
- Line 163: `Saturation inner_command_limit(upLimit=1.0, lowLimit=-1.0)`

**All 15 controllers saturate their output to [-1, 1] range, expecting this to be a normalized command.**

## Plant Input Convention

From RotorActuatorCore.mo:
- Line 32: `Real motor_command[4](each unit = "rad/s")` — expects ABSOLUTE rotor speed
- Line 61: `der(omega[i]) = (motor_command[i] - omega[i]) / motor_tau[i]` — first-order lag to commanded speed
- Line 62: `nominal_thrust[i] = lift_coefficient * omega[i] * omega[i]` — thrust = Ct × ω²
- Line 13: `hover_motor_speed_cmd = sqrt(mass_kg * gravity_mps2 / (4 * lift_coefficient))` = 64.79 rad/s

**The plant expects rotor_command in rad/s, where hover = 64.79 rad/s.**

## Consequence of Mismatch

At hover (t=0):
- Initial rotor speed: 64.79 rad/s (parameter in RotorActuatorCore line 14-17)
- Controller has not yet commanded anything → motors stay at initial speed
- Thrust per rotor: 0.584 × 64.79² = 2.452 N ✓
- Total thrust: 9.807 N ✓ (correct hover)

At t=10-50s (trajectory tracking):
- Controller commands: 1.0 (thinks: "100% thrust")
- Plant interprets: 1.0 rad/s (absolute speed)
- Rotor dynamics: omega converges from 64.79 → 1.0 rad/s via first-order lag
- Thrust per rotor: 0.584 × 1.0² = 0.000584 N ✗
- Total thrust: 0.002336 N ✗ (99.98% loss)
- Vehicle experiences: 9.807 N gravity - 0.002 N thrust ≈ -9.8 N net force
- Result: free-fall at -9.8 m/s², drops 12250m in 50s

## Missing Scaling Layer

Expected interface chain:
```
Controller → [0,1] → **MISSING SCALER** → [rad/s] → Plant
```

Actual interface chain:
```
Controller → [0,1] → ∅ → Plant expects [rad/s]
```

Components in the chain that do NOT scale:
1. **GraphicalScalarRotorPreview** (line 9): `Gain bridge[4](each k = 1)` — passes through unchanged
2. **ScheduledRotorEfficiencyCompensator**: fault compensation only, no unit conversion
3. **ESCDrive** (line 28): voltage scaling only, no rad/s conversion
4. **RotorCommandChannel** (line 26-29): pass-through only

## Root Cause

**The Runner architecture is missing the normalized-to-rad/s scaling adapter.**

Expected design:
- Controller outputs normalized [0, 1] command
- Adapter scales: `motor_command_rad_s = normalized × hover_speed_cmd`
- Where hover_speed_cmd = 64.79 rad/s for Sunray150
- Plant receives absolute rotor speed in rad/s

Actual implementation:
- Controller outputs [0, 1]
- No scaling layer exists
- Plant receives [0, 1] and interprets as rad/s
- Motors spin at 1 rad/s instead of 64.79 rad/s

## Impact

- **All 15 controllers fail identically** because they share the same normalized output convention
- **Phase 4 CheckModel passed** because it only checks instantiation/compilation, not runtime values
- **Phase 5 simulation runs without error** but produces physically incorrect results
- **Final tracking error ~12km** from 50s of free-fall under near-zero thrust

## Fix Strategy

Add scaling layer between controller and plant:

```modelica
// In GraphicalScalarRotorPreview or new adapter component
parameter Real hover_speed_rad_s = 64.79;  // From profile
rotor_command_rad_s[i] = command_normalized * hover_speed_rad_s;
```

Or modify RotorActuatorCore to accept normalized input:

```modelica
// Change interface from rad/s to normalized [0,1]
Real motor_command_normalized[4](each min=0, each max=1);
Real motor_command_rad_s[4](each unit="rad/s");
motor_command_rad_s[i] = motor_command_normalized[i] * hover_motor_speed_cmd;
der(omega[i]) = (motor_command_rad_s[i] - omega[i]) / motor_tau[i];
```

## Files

- Investigation date: 2026-08-19
- Root cause: Missing normalized-to-rad/s scaling adapter
- Affected: All 15 Phase 4 passing controllers
- Phase 5 pass rate: 0% (0/15)
- Expected fix location: GraphicalScalarRotorPreview.mo or RotorActuatorCore.mo
