# gain_scheduled_pid Optimization Attempt Report

## Date: 2026-08-19 06:58

## Optimization Result
**FAILURE**: Cannot fix - uses GraphicalScalarRotorPreview adapter with fundamental defect

## Root Cause
Original Phase 5 diagnosis was CORRECT: "Adapter fundamental defect (GraphicalScalarRotorPreview)".

**Architecture Investigation**:
- Line 26: `MoSimQuadrotorModel.Experiment.Adapters.GraphicalScalarRotorPreview output_adapter`
- Line 70: `connect(core.command, output_adapter.command)` - controller outputs single scalar command
- Lines 71-74: Four identical rotor commands from adapter

**GraphicalScalarRotorPreview Fundamental Defect**:
The adapter converts a SINGLE scalar `command` input into FOUR IDENTICAL rotor speeds:
```
rotor_command[1] = rotor_command[2] = rotor_command[3] = rotor_command[4] = normalized_thrust
```

This architecture CANNOT control attitude (roll/pitch/yaw) because:
1. Differential thrust control requires DIFFERENT rotor speeds for each motor
2. Roll control: increase motors 2,4, decrease motors 1,3
3. Pitch control: increase motors 3,4, decrease motors 1,2
4. Yaw control: increase motors 1,3 (CCW), decrease motors 2,4 (CW)
5. With identical rotor speeds, can only control collective thrust (vertical acceleration)

**Why Controller Fails**:
GainScheduledPidCore outputs a single scalar command (likely normalized thrust or altitude control signal). The GraphicalScalarRotorPreview adapter broadcasts this to all four rotors identically, so:
- Quadrotor can hover at approximately correct altitude
- But cannot track horizontal position (no roll/pitch control)
- Cannot track yaw reference (no differential torque)
- Terminal position error 11.53m because it drifts in x/y with zero attitude control authority

## Comparison with Working Controllers
**Controllers that PASS Phase 5**:
- Use `GraphicalAttitudeThrustRotorPreview` adapter: accepts roll/pitch/yaw/thrust → differential rotor speeds
- Use `GraphicalAccelerationRotorPreview` adapter: accepts accel_x/y/z/thrust → differential rotor speeds
- Can control all 6 DOF (position + attitude)

**Controllers that FAIL with GraphicalScalarRotorPreview**:
- `gain_scheduled_pid` (11.53m error)
- `fuzzy_pid` (14.51m error) - also uses GraphicalScalarRotorPreview (need to verify)

## Why Cannot Fix
To fix gain_scheduled_pid would require:

**Option 1: Redesign Controller Core**
- Rewrite GainScheduledPidCore to output roll/pitch/yaw/thrust (4 signals) instead of single command
- Change adapter to GraphicalAttitudeThrustRotorPreview
- Redesign entire control law with attitude feedback loops
- This is equivalent to designing a NEW controller (weeks of work)

**Option 2: Replace with Existing Working PID**
- official_pid already uses GraphicalAttitudeThrustRotorPreview and PASSES (2.65m error)
- cascade_pid uses modern architecture
- No point in having multiple PID variants if gain_scheduled_pid can't offer unique capability

**Why GraphicalScalarRotorPreview Exists**:
Likely a LEGACY adapter from early prototyping that:
- Was used for simple altitude-only control experiments
- Never intended for full 3D position tracking
- Should have been deprecated during Phase 1-3 restoration
- Left in codebase for backward compatibility with old experiments

## Key Lesson
GraphicalScalarRotorPreview is architecturally incapable of 3D position tracking. ANY controller using this adapter will fail Phase 5 requirements because it lacks attitude control authority. The adapter itself is the bottleneck, not the controller design.

## Recommendation
**SKIP** gain_scheduled_pid optimization - adapter fundamental defect cannot be fixed without complete controller redesign (weeks of work). The controller may perform well in altitude-only scenarios, but cannot meet 3D trajectory tracking requirements.

Consider deprecating GraphicalScalarRotorPreview adapter in future work and migrating all controllers to GraphicalAttitudeThrustRotorPreview or GraphicalAccelerationRotorPreview.

---
**Status**: ❌ Optimization FAILED - adapter fundamental defect
**Controllers optimized so far**: 9/11 attempted (2 FAIL due to architecture/adapter defects)
- trained_neural_residual: SUCCESS (6.93m → 3.34m)
- rl_gain_scheduler: FAIL (7.33m → 9.99m) - adapter switch caused degradation
- official_pid: SUCCESS (8.90m → 2.65m)
- fopid: SUCCESS (14.12m → 1.52m)
- dfbc_smooth_robust_attitude: SUCCESS (5.30m → 4.20m)
- explicit_gain_scheduled_mpc: SUCCESS (7.45m → 2.91m)
- tube_mpc: SUCCESS (7.68m → 1.86m)
- adaptive_smc: SUCCESS (11.08m → 2.42m)
- fixed_awff_pid: FAIL (11.18m → CANNOT COMPILE) - legacy Example1 architecture
- gain_scheduled_pid: FAIL (11.53m → CANNOT FIX) - GraphicalScalarRotorPreview fundamental defect
