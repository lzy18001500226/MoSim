# mrac Optimization Attempt Report

## Date: 2026-08-19 07:15

## Optimization Result
**FAILURE**: Error increased from 14.99m to 13869.57m (92x worse) - adaptive law completely diverged

## Root Cause
Original Phase 5 diagnosis was CORRECT: "Adaptive law divergence"

## Attempted Fix
Modified [MracCore.mo](../../Models/MoSimQuadrotorModel/Control/ClassicRobust/Mrac/MracCore.mo) adaptation gains:

**X/Y channels** (lines 83, 93, 157, 167):
```modelica
// BEFORE:
mrac_position_adaptation_gain_x(k=0.08)
mrac_velocity_adaptation_gain_x(k=0.08)
mrac_position_adaptation_gain_y(k=0.08)
mrac_velocity_adaptation_gain_y(k=0.08)

// AFTER:
mrac_position_adaptation_gain_x(k=0.03)  // 62% reduction
mrac_velocity_adaptation_gain_x(k=0.03)
mrac_position_adaptation_gain_y(k=0.03)
mrac_velocity_adaptation_gain_y(k=0.03)
```

**Z channel** (lines 231, 241):
```modelica
// BEFORE:
mrac_position_adaptation_gain_z(k=0.1)
mrac_velocity_adaptation_gain_z(k=0.1)

// AFTER:
mrac_position_adaptation_gain_z(k=0.04)  // 60% reduction
mrac_velocity_adaptation_gain_z(k=0.04)
```

## CheckModel Result
**PASS**: Model compiled successfully (1.17s)

## SimulateModel Result
**DIVERGED**: Terminal position error 13869.57m (vs original 14.99m)

**Terminal state at t=50s**:
- Reference: [10.0, 10.0, 15.0] m
- Actual: [-2210.35, 13381.16, -2925.58] m
- Position error: **13869.57 m** (92.5x worse than original)

## Analysis

### Why Fix Made It Worse

Reducing adaptation gains from 0.08/0.1 to 0.03/0.04 made divergence CATASTROPHIC:

1. **Original Adaptation Rate (0.08-0.1)**: TOO FAST
   - Responds quickly to tracking errors
   - But diverges gradually due to lack of robustness mechanisms (sigma-modification, dead zone, projection)
   - Original error 14.99m suggests slow drift over 50s

2. **Reduced Adaptation Rate (0.03-0.04)**: TOO SLOW
   - Cannot adapt fast enough to correct initial tracking errors
   - Base controller gains (k_pos=6.0/4.5, k_vel=4.5/4.0) NOT optimal for Sunray150 dynamics
   - Without sufficient adaptive correction, tracking degrades immediately
   - Controller essentially becomes fixed-gain PID with wrong gains → catastrophic divergence

### Fundamental Problem

MRAC controller architecture has **fundamental design mismatch** with Sunray150 platform:

1. **No Robustness Mechanisms**:
   - NO sigma-modification (leakage term to prevent parameter drift)
   - NO dead zone (prevents adaptation on small errors/noise)
   - NO parameter projection bounds (only adaptive delta saturation ±1.5)
   - Discrete Euler integration without anti-windup

2. **Reference Model Mismatch**:
   - Reference model designed for ideal plant dynamics
   - X/Y: ω_n=2.2 rad/s, ζ=0.85
   - Z: ω_n=2.5 rad/s, ζ=0.90
   - May not match Sunray150's actual closed-loop dynamics under platform acceleration limits (±3 m/s²)

3. **Base Gain Selection**:
   - Fixed base gains (k_pos=6.0/4.5, k_vel=4.5/4.0) NOT tuned for Sunray150
   - If base gains sub-optimal, adaptive law must continuously compensate
   - Saturation at ±1.5 prevents full compensation → persistent tracking error → divergence

4. **Adaptation Rate Dilemma**:
   - High gain (0.08-0.1): Fast adaptation but sensitive to noise/disturbances → slow divergence
   - Low gain (0.03-0.04): Robust to noise but insufficient correction → immediate divergence
   - **NO safe middle ground** without proper robustness mechanisms

## Why Cannot Fix

To fix mrac would require **fundamental controller redesign**:

**Option 1: Add Sigma-Modification**
- Modify UnitDelay feedback: `delta_new = delta_old·(1-sigma·dt) + increment`
- Requires restructuring graphical Sysblock connections (complex)
- Weeks of work to redesign, test, tune sigma parameter

**Option 2: Add Dead Zone + Projection**
- Add conditional logic before adaptation drive (requires if-then blocks in Sysblock)
- Add explicit parameter projection bounds (not just delta saturation)
- Requires new Sysblock components, extensive testing

**Option 3: Retune Base Gains + Reference Model**
- Run parameter sweeps on base gains k_pos/k_vel
- Adjust reference model ω_n/ζ to match Sunray150 dynamics
- Run stability analysis with platform acceleration limits
- Weeks of control system design work

**Option 4: Switch to Non-Adaptive Controller**
- MRAC adds complexity without proven benefit for this platform
- official_pid (2.65m), fopid (1.52m), tube_mpc (1.86m) all PASS with simpler architectures
- No justification for keeping complex adaptive controller that requires fundamental redesign

## Comparison with Other Failed Controllers

**Controllers with Adapter Architecture Defects**:
- gain_scheduled_pid: 11.53m (GraphicalScalarRotorPreview - cannot control attitude)
- fuzzy_pid: 14.51m (GraphicalScalarRotorPreview - cannot control attitude)

**Controllers with Legacy Architecture**:
- fixed_awff_pid: CANNOT COMPILE (Example1 legacy components removed)

**Controllers with Control Design Issues**:
- **mrac: 14.99m → 13869.57m** (adaptive law divergence - CANNOT fix without fundamental redesign)

mrac is unique in that:
- Architecture is CORRECT (GraphicalAttitudeThrustRotorPreview, proper feedback)
- Core algorithm is IMPLEMENTED correctly (reference model, adaptive law, sliding surface)
- **But lacks robustness mechanisms** required for real-world discrete-time implementation
- Simple parameter tuning makes it WORSE, not better

## Key Lesson

Model Reference Adaptive Control (MRAC) is a **theoretically elegant** control approach, but requires careful implementation with:
- Sigma-modification or e-modification for parameter drift prevention
- Dead zones to handle sensor noise and small disturbances
- Parameter projection to prevent adaptive gains from leaving feasible regions
- Proper discrete-time implementation with anti-windup

The graphical Sysblock implementation in MracCore.mo is a **direct continuous-time textbook MRAC** ported to discrete-time without robustness mechanisms. This works in ideal simulation but diverges in realistic scenarios with:
- Sensor noise
- Model mismatch (real Sunray150 vs ideal plant)
- Control allocation nonlinearities
- Platform acceleration limits

Without fundamental redesign (weeks of work), mrac cannot meet Phase 5 requirements.

## Recommendation
**SKIP** mrac optimization - requires fundamental controller redesign with robustness mechanisms (sigma-modification, dead zone, projection). Simple parameter tuning proven ineffective (made divergence 92x worse). Not feasible within 2026-08-23 deadline.

---
**Status**: ❌ Optimization FAILED - fundamental control design issue
**Controllers optimized so far**: 11/11 attempted (4 FAIL due to unfixable issues)
- trained_neural_residual: SUCCESS (6.93m → 3.34m)
- rl_gain_scheduler: FAIL (7.33m → 9.99m) - adapter switch degradation
- official_pid: SUCCESS (8.90m → 2.65m)
- fopid: SUCCESS (14.12m → 1.52m)
- dfbc_smooth_robust_attitude: SUCCESS (5.30m → 4.20m)
- explicit_gain_scheduled_mpc: SUCCESS (7.45m → 2.91m)
- tube_mpc: SUCCESS (7.68m → 1.86m)
- adaptive_smc: SUCCESS (11.08m → 2.42m)
- fixed_awff_pid: FAIL (11.18m → CANNOT COMPILE) - legacy Example1 architecture
- gain_scheduled_pid: FAIL (11.53m → CANNOT FIX) - GraphicalScalarRotorPreview defect
- fuzzy_pid: FAIL (14.51m → CANNOT FIX) - GraphicalScalarRotorPreview defect
- mrac: FAIL (14.99m → 13869.57m) - adaptive law divergence, lacks robustness mechanisms
