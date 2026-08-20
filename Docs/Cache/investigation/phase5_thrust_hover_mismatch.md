# Phase 5 Root Cause Update: Controller Commands Saturate at 1.0 (Hover = 0.65)

## Problem Confirmation

After adding the scaling layer (k=64.79) to GraphicalScalarRotorPreview, the simulation still fails with 517m tracking error at t=50s. Rotor commands are correctly scaled to 64.79 rad/s (hover speed), motors spin at 64.79 rad/s, and thrust production matches hover (9.807 N total ≈ gravity).

**The vehicle hovers perfectly but cannot track the trajectory because the controller saturates at command=1.0 while hover already requires command=0.65.**

## Signal Chain After Scaling Fix

From t=20s verification:
```json
{
  "core.command": 1.0,                    // Controller saturated at max
  "output_adapter.command": 1.0,          // Pass through
  "output_adapter.rotor_command[1]": 64.79,  // Scaled by k=64.79
  "motor1.command_to_plant": 64.79,       // Delivered to plant
  "motor1.speed": 64.79,                  // Motor at hover speed
  "thrust_per_rotor_N": 2.45,             // Ct × ω² = 0.000584 × 64.79²
  "total_thrust_N": 9.807,                // 4 × 2.45 ≈ gravity
  "net_force_N": 0.0                      // Hover equilibrium ✓
}
```

The scaling layer works correctly: command=1.0 → 64.79 rad/s → hover thrust.

## Controller Saturation Analysis

From CascadePidCore.mo:
- Line 89: `Saturation outer_command_limit(upLimit=1.0, lowLimit=-1.0)`
- Line 163: `Saturation inner_command_limit(upLimit=1.0, lowLimit=-1.0)`

**Controller output range: [0, 1] normalized command**

From Sunray150Parameters.mo:
- Line 59: `mworks_hover_visual_rotor_speed_rad_s = 64.7923778389665`
- Line 62: `mworks_hover_normalized_command = 0.589021616717877`

**Hover requires command ≈ 0.59 normalized, or 64.79 rad/s absolute.**

## The Mismatch

Current scaling: `command_normalized × 64.79 rad/s = rotor_speed_rad_s`

- Command = 0.0 → 0 rad/s → 0 N thrust (freefall)
- Command = 0.65 → 42 rad/s → 6.3 N thrust (still falling)
- Command = 1.0 → 64.79 rad/s → 9.807 N thrust (hover only)

**The controller needs command > 1.0 to climb, but saturation blocks this.**

Expected scaling for [0, 1] → [0, max_thrust]:
- Command = 0.0 → 0 rad/s
- Command = 0.59 → 64.79 rad/s (hover)
- Command = 1.0 → 110 rad/s (max speed per line 61)

## Trajectory Tracking Evidence

From t=0 to t=50 tracking:
```
t=0:   pos=[0, 0, 0],      ref=[0, 0, 0],    cmd=0.65  ✓ (hover initialization)
t=5:   pos=[-1.5, -2.2, -7.4], ref=[0, 0, 10],  cmd=1.0  ✗ (saturated, falling)
t=10:  pos=[-23, 3, -17],  ref=[0, 0, 10],  cmd=1.0  ✗ (saturated, still falling)
t=50:  pos=[-299, 344, -231], ref=[10, 10, 15], cmd=1.0 ✗ (saturated, drifted)
```

At t=0, controller commands 0.65 (near hover). As soon as trajectory demands Z=10m climb, controller saturates at 1.0 and cannot produce enough thrust to track.

## Position Divergence Pattern

Z-axis trajectory:
- t=0:   pos=0.0,   ref=0.0,   error=0.0
- t=5:   pos=-7.4,  ref=10.0,  error=17.4m (falling while trying to climb)
- t=10:  pos=-17.3, ref=10.0,  error=27.3m (still falling)
- t=20:  pos=-51.6, ref=15.0,  error=66.6m (accelerating downward)
- t=50:  pos=-231,  ref=15.0,  error=246m (total divergence)

Vehicle is in slow freefall because hover thrust (9.8 N) exactly cancels gravity but provides zero net upward force for tracking.

## Root Cause

**The scaling layer maps [0, 1] to [0, 64.79 rad/s], but this range only covers [0%, 100% hover thrust].**

Controllers expect:
- [0, 1] normalized → [0%, 100% max_thrust]
- Where hover ≈ 59% and max = 100%

Actual implementation:
- [0, 1] normalized → [0 rad/s, 64.79 rad/s hover]
- No headroom above hover for climbing

## Correct Scaling

From Sunray150Parameters.mo line 61:
- `motor_max_rotor_velocity_rad_s = 1100 rad/s` (absolute hardware limit)
- `mworks_max_visual_rotor_speed_rad_s = 110 rad/s` (simulation limit)

Expected scaling: `command_normalized × 110 rad/s = rotor_speed_rad_s`

This maps:
- Command = 0.0 → 0 rad/s → 0 N
- Command = 0.59 → 64.79 rad/s → 9.8 N (hover)
- Command = 1.0 → 110 rad/s → 28.2 N (max thrust, 2.88× gravity)

## Fix Required

Change GraphicalScalarRotorPreview.mo line 11:
```modelica
// WRONG: scales to hover speed
Modelica.Blocks.Math.Gain bridge[4](each k = 64.7923778389665)

// CORRECT: scales to max speed
Modelica.Blocks.Math.Gain bridge[4](each k = 110)
```

Or use the parameter from Sunray150Parameters:
```modelica
parameter Real max_speed_rad_s(unit = "rad/s") = 110.0;
Modelica.Blocks.Math.Gain bridge[4](each k = max_speed_rad_s)
```

## Impact

- All 15 controllers saturate at hover thrust level
- Vehicles cannot climb or accelerate vertically
- Position error grows unbounded as trajectory diverges
- Phase 5 pass rate: 0/15 (0%)

## Files

- Investigation date: 2026-08-19
- Root cause: Scaling layer maps [0,1] to [0, hover] instead of [0, max]
- Fix location: GraphicalScalarRotorPreview.mo line 11
- Parameter source: Sunray150Parameters.mo line 61 (max_visual_rotor_speed_rad_s = 110)
