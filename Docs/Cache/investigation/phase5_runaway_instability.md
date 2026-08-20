# Phase 5 Runaway Instability After Scaling Fix

## Problem Statement

After fixing GraphicalScalarRotorPreview scaling from 64.79 (hover) to 110.0 (max), the simulation produces **runaway instability** instead of tracking the 15m altitude reference. Vehicle climbs to 21,636m at t=50s (final error 21,729m) instead of converging to the target.

## Scaling Fix Verification ✓

The scaling layer now works correctly:

```json
{
  "t20_controller_command": 1.0,
  "t20_rotor_command_rad_s": 110.0,
  "t20_motor_speed_rad_s": 110.0,
  "t20_thrust_per_rotor_N": 7.066,
  "t20_total_thrust_N": 28.266,
  "gravity_N": 9.807,
  "thrust_to_weight_ratio": 2.882
}
```

- Controller saturates at command = 1.0 ✓
- Scaling layer outputs: 1.0 × 110 = 110 rad/s ✓
- Motors spin at: 110 rad/s ✓
- Thrust production: 0.000584 × 110² × 4 = 28.27 N ✓
- T/W ratio: 2.88× gravity ✓

**The scaling fix works as designed.**

## Divergence Pattern

### Position Trajectory (Z-axis)

```
t=0:   Z = 0.0 m       (reference: 0 m)     error = 0 m
t=5:   Z = 207 m       (reference: 10 m)    error = 197 m
t=10:  Z = 851 m       (reference: 10 m)    error = 841 m
t=20:  Z = 3,411 m     (reference: 15 m)    error = 3,396 m
t=30:  Z = 7,750 m     (reference: 15 m)    error = 7,735 m
t=40:  Z = 13,814 m    (reference: 15 m)    error = 13,799 m
t=50:  Z = 21,636 m    (reference: 15 m)    error = 21,621 m
```

### Acceleration Analysis

Expected net acceleration at full thrust (t=5 to t=50):
```
a_z = (F_thrust - F_gravity) / m
    = (28.266 - 9.807) / 1.0
    = 18.459 m/s²
```

Position check with constant acceleration:
```
Z(t) = 0.5 × a × t²
Z(5s) = 0.5 × 18.459 × 5² = 230.7 m  (actual: 207 m ✓)
Z(10s) = 0.5 × 18.459 × 10² = 922.9 m (actual: 851 m ✓)
Z(50s) = 0.5 × 18.459 × 50² = 23,074 m (actual: 21,636 m ✓)
```

**The vehicle is accelerating at ~18.5 m/s² upward continuously from t=0 to t=50.**

### XY Position Divergence

```
t=0:   (X, Y) = (0, 0)
t=5:   (X, Y) = (-16, -10)
t=10:  (X, Y) = (-79, 53)
t=20:  (X, Y) = (-246, 233)
t=30:  (X, Y) = (-516, 575)
t=40:  (X, Y) = (-894, 1052)
t=50:  (X, Y) = (-1346, 1689)
```

XY error grows from 19m at t=5 to 2,179m at t=50.

### Attitude Oscillations

```
Roll/Pitch remain small: < 0.35°
Yaw oscillates: 2.81° (t=5) → -2.44° (t=30) → 2.13° (t=50)
```

Attitude control is working (small angles), but position control has failed.

## Root Cause Analysis

### Controller Saturation

Controller saturates at command = 1.0 starting from t=5s and remains saturated throughout the entire 50s simulation. This is **anti-windup failure**:

1. At t=0: hover equilibrium, command ≈ 0.65
2. At t=5: trajectory demands Z=10m climb, error builds rapidly
3. Controller saturates at command = 1.0 (max output)
4. Vehicle climbs at 2.88× gravity acceleration
5. Position error grows unbounded: 207m → 21,636m
6. **Controller cannot reduce thrust** because it's already at maximum output

### Missing Feedback Loop

The cascade PID expects to modulate thrust bidirectionally around hover:
- Command < 0.59: descend (thrust < gravity)
- Command = 0.59: hover (thrust = gravity)
- Command > 0.59: climb (thrust > gravity)

But once saturated at 1.0, the controller loses authority:
- **Cannot increase thrust** (already at max)
- **Cannot decrease thrust** (output can only go down from 1.0, but integral windup prevents this)

The vehicle overshoots massively because:
1. Initial climb demand → controller saturates at max thrust
2. Vehicle accelerates at 18.5 m/s² upward
3. By t=5, already 197m above reference and still accelerating
4. Controller integral term winds up trying to correct the growing error
5. Even when position exceeds reference, integral windup keeps command at 1.0
6. No negative feedback can bring thrust back down to hover level

## Comparison with Original Hover-Scaled System

### Old System (k=64.79, hover-limited)

```
Command = 1.0 → 64.79 rad/s → 9.807 N thrust
Result: Vehicle hovers (0 net force), cannot climb
Error at t=50: -517m (fell below reference)
Problem: Insufficient thrust authority for tracking
```

### New System (k=110, max thrust)

```
Command = 1.0 → 110 rad/s → 28.266 N thrust
Result: Vehicle rockets upward at 18.5 m/s², cannot stop
Error at t=50: +21,621m (climbed far above reference)
Problem: Excessive thrust authority + integral windup
```

## Fundamental Issue: Interface Contract Mismatch

The controller was designed expecting:
- Output range [0, 1] maps to [0%, 100%] of **usable thrust range**
- Where "usable" means: enough headroom above hover for tracking, but not excessive

Current mapping [0, 1] → [0, 110 rad/s]:
- Command = 0.0 → 0 N (0% thrust, freefall)
- Command = 0.59 → 9.8 N (100% of gravity, hover)
- Command = 1.0 → 28.3 N (288% of gravity, **excessive**)

Expected mapping [0, 1] → [hover_min, hover_max]:
- Command = 0.0 → ~50% hover thrust (controlled descent)
- Command = 0.5 → 100% hover thrust (equilibrium)
- Command = 1.0 → ~150% hover thrust (moderate climb)

## Why This Wasn't Caught Earlier

1. **Phase 4 CheckModel**: Only verifies instantiation/compilation, not runtime behavior ✓
2. **Original hover-scale bug**: Masked the control authority problem (couldn't climb at all)
3. **No intermediate testing**: Went directly from "can't hover" to "max thrust" without checking control loop stability

## Correct Fix Strategy

**Option 1: Bias + Reduced Gain Scaling**

Map [0, 1] controller output to [hover-20%, hover+30%] thrust range:

```modelica
parameter Real hover_speed_rad_s = 64.79;
parameter Real min_speed_rad_s = hover_speed_rad_s * 0.8;  // 51.83 rad/s
parameter Real max_speed_rad_s = hover_speed_rad_s * 1.3;  // 84.23 rad/s
parameter Real speed_range = max_speed_rad_s - min_speed_rad_s;  // 32.4 rad/s

// Scaling with bias
rotor_speed[i] = min_speed_rad_s + command * speed_range;
```

This ensures:
- Command = 0.0 → 51.83 rad/s → 6.3 N (64% of hover, controlled descent)
- Command = 0.5 → 68.03 rad/s → 10.8 N (110% of hover, mild climb)
- Command = 1.0 → 84.23 rad/s → 16.5 N (168% of hover, moderate climb)

**Option 2: Nonlinear Scaling Around Hover**

Use quadratic mapping concentrated around hover point:

```modelica
parameter Real hover_cmd_normalized = 0.5;  // Hover at mid-range
parameter Real hover_speed_rad_s = 64.79;
parameter Real speed_range = 30.0;  // ±15 rad/s around hover

// Quadratic scaling for finer control near hover
Real normalized_deviation = command - hover_cmd_normalized;
rotor_speed[i] = hover_speed_rad_s + normalized_deviation * speed_range;
```

**Option 3: Fix Controller Anti-Windup**

The CascadePidCore likely has broken integral anti-windup when output saturates. The integral term should stop accumulating when the output hits limits, but it continues winding up, preventing the controller from backing off.

Check CascadePidCore.mo for proper anti-windup implementation on both outer and inner loops.

## Anti-Windup Analysis

Verified anti-windup implementation in CascadePidCore.mo:

- Line 89: `outer_command_limit(upLimit=1.0, lowLimit=-1.0)` — output saturation
- Line 91-94: `outer_saturation_error` → `outer_aw_correction(k=0.004)` — anti-windup feedback
- Line 97-98: `outer_integral_final_limit(upLimit=0.5, lowLimit=-0.5)` — integral clamping
- Lines 163-172: Same structure for inner loop

Anti-windup signals during runaway climb:

```json
{
  "t5": {
    "unsaturated_cmd": 1.0,
    "saturated_cmd": 0.88,
    "final_cmd": 1.0,
    "integral_state": 0.49822,
    "saturation_error": -0.12,
    "is_saturated": true
  },
  "t50": {
    "unsaturated_cmd": 1.0,
    "saturated_cmd": 0.88,
    "final_cmd": 1.0,
    "integral_state": 0.49822,
    "saturation_error": -0.12,
    "is_saturated": true
  }
}
```

**Anti-windup is working correctly:**
- Integral state clamps at 0.498 ≈ 0.5 limit ✓
- Saturation error is detected: -0.12 (unsaturated > saturated) ✓
- Correction gain k=0.004 applied to prevent further windup ✓

**The problem is NOT anti-windup failure.** The controller is behaving correctly given the excessive thrust authority.

## Revised Root Cause

The fundamental issue is **thrust range mismatch**:

1. Controller designed for [0, 1] → [descent_thrust, climb_thrust]
2. Current mapping: [0, 1] → [0 N, 28.3 N] = [0%, 288% of hover]
3. Controller has no way to command "maintain altitude" without integral windup

At hover initialization (t=0):
- Command = 0.65 produces 64.79 rad/s → 9.8 N (equilibrium)
- But this is **not** a steady-state operating point
- Integral state = 0.004 (near zero)

At trajectory tracking (t=5+):
- Reference demands climb from Z=0 to Z=10m
- Controller increases command toward 1.0
- Produces 110 rad/s → 28.3 N → 18.5 m/s² upward
- Vehicle overshoots massively before controller can react
- Integral winds up to +0.498 trying to correct
- But reducing command from 1.0 would require **negative** position error
- Since error is always positive (vehicle above reference), command stays at 1.0

## Recommended Next Steps

1. **Implement Option 1** (bias + reduced gain) as the correct fix
2. **Map [0, 1] to [0.5×hover, 1.5×hover]** = [32.4, 97.2 rad/s]
   - Command = 0.0 → 32.4 rad/s → 2.45 N (25% of hover, controlled descent)
   - Command = 0.5 → 64.79 rad/s → 9.8 N (hover equilibrium)
   - Command = 1.0 → 97.2 rad/s → 22.0 N (225% of hover, moderate climb)
3. **Test with CascadePid** to verify stability
4. **Batch re-run all 15 controllers** if successful
5. **Document the interface contract** for future controller development

## Files

- Investigation date: 2026-08-19
- Test controller: CascadePid
- Symptom: 21,636m altitude at t=50 (reference: 15m)
- Root cause: Max thrust scaling (110 rad/s) + integral windup → runaway climb
- Fix: Bias + reduced gain scaling around hover point
