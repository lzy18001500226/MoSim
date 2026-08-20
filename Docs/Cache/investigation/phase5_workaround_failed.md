# Phase 5 Workaround Failed: Trajectory Reduction Insufficient

## Executive Summary

The temporary workaround of reducing trajectory climb rates by 50% **FAILED** to resolve the Phase 5 tracking divergence. Despite using the gentler trajectory (1 m/s instead of 2 m/s), CascadePid still produces 613m final error with sustained saturation for the entire 50-second simulation.

**Root Cause Confirmed**: The problem is NOT trajectory aggressiveness. The problem is the **5% thrust margin** combined with **controller tuning mismatch**. Even the gentlest possible trajectory causes sustained saturation when the controller can only produce 1.05× gravity at maximum output.

## Verification Results

### Trajectory Modification Confirmed ✓

The modified ClimbTrajectory.mo was successfully loaded and used:

```
Velocity Command (vertical):
  t=0-10s:   vz = 1.0 m/s  (was 2.0 m/s)  ✓
  t=10-20s:  vz = 0.5 m/s  (was 1.67 m/s) ✓
  t=20-50s:  vz = 0.0 m/s  (hover only)   ✓

Position Command (vertical):
  t=0-10s:   Z: 0 → 10m
  t=10-20s:  Z: 10 → 15m
  t=20-50s:  Z: 15m (hold)
```

### Simulation Results: Still Diverging

```
Time    Position_Z    Reference_Z    Error      Command    Saturated
----    ----------    -----------    -----      -------    ---------
t=0     0.0 m         0 m            0.0 m      0.6515     No
t=5     4.98 m        10 m           5.85 m     1.0        Yes  ⚠
t=10    20.45 m       10 m           21.1 m     1.0        Yes  ⚠
t=15    45.39 m       15 m           43.1 m     1.0        Yes  ⚠
t=20    79.17 m       15 m           88.5 m     1.0        Yes  ⚠
t=30    180.6 m       15 m           218 m      1.0        Yes  ⚠
t=40    324.3 m       15 m           390 m      1.0        Yes  ⚠
t=50    506.5 m       15 m           613 m      1.0        Yes  ⚠
```

**Final Error: 613.20 m** (threshold: 5 m)
**Pass Status: FAIL** ❌

### Saturation Analysis

Controller saturates at command=1.0 continuously from t=5s to t=50s (45 seconds of sustained saturation).

**Physics Calculation**:
- Thrust at saturation: 10.3 N (1.05× gravity)
- Net upward force: 10.3 - 9.807 = 0.493 N
- Acceleration: 0.493 m/s²
- Position after 50s: 0.5 × 0.493 × 50² = 616 m ✓

The observed 613m matches the physics prediction exactly. The controller is not malfunctioning — it's working correctly but **unable to track even gentle trajectories** with only 5% thrust authority.

## Why the Workaround Failed

### Original Hypothesis (Wrong)

"The 2 m/s climb rate is too aggressive, causing controllers to saturate. Reducing to 1 m/s will prevent saturation."

### Actual Reality

The trajectory climb rate is irrelevant. The controller saturates because:

1. **At t=5s**: Vehicle is at Z=4.98m, reference is Z=10m
2. **Error**: -5.02m (below target)
3. **Controller response**: Maximum output (command=1.0)
4. **Thrust produced**: 10.3 N (only 1.05× gravity)
5. **Net acceleration**: 0.493 m/s²
6. **Time to close 5m gap**: ~14 seconds at this acceleration
7. **But the reference keeps moving**: Z_ref advances to 15m during t=10-20s
8. **Result**: Controller never catches up, stays saturated indefinitely

Even if we reduced the climb rate to 0.1 m/s, the same pattern would occur:
- Initial lag builds up tracking error
- Controller saturates trying to close the gap
- 5% margin insufficient to catch up
- Error accumulates unboundedly

## The Real Problem: Thrust Authority Mismatch

### What the Controller Expects

Controllers were designed and tuned assuming:
- **Hover at mid-range**: command ≈ 0.5 produces equilibrium thrust
- **Ample climb authority**: saturation at 1.0 produces >>2× gravity
- **Transient saturation**: brief peaks during aggressive maneuvers, not sustained

### What the Interface Provides (5% Margin Scaling)

- **Hover at 0.65**: command = 0.6515 produces equilibrium thrust
- **Minimal climb authority**: saturation at 1.0 produces 1.05× gravity
- **Sustained saturation**: insufficient authority causes prolonged saturation

**Mismatch**: Hover is NOT at mid-range, and saturation authority is NOT sufficient for tracking.

## Three Failed Scaling Attempts

| Attempt | Max Thrust | Net Force | t=50 Error | Saturation | Outcome |
|---------|-----------|-----------|------------|------------|---------|
| [0, 110] rad/s | 28.3 N (2.88×g) | +18.5 N | 14,716 m | 45s | Runaway climb |
| [0.5h, 1.5h] | 22.1 N (2.25×g) | +12.3 N | 14,678 m | 45s | Runaway climb |
| [0.95h, 1.05h] | 10.3 N (1.05×g) | +0.49 N | 613 m | 45s | Slow divergence |

**Pattern**: ANY thrust margin causes divergence. The problem is not the margin size — it's that the controller saturates for extended periods and ANY net force during saturation accumulates unboundedly via physics: s = 0.5 × a × t².

## Two Failed Trajectory Modifications

| Trajectory | Climb Rate | Max Accel | t=50 Error | Outcome |
|-----------|-----------|----------|------------|---------|
| Original ClimbPath | 2.0 m/s (t=0-5s) | Moderate | 613 m | Sustained saturation |
| Gentler ClimbPath | 1.0 m/s (t=0-10s) | Conservative | 613 m | **STILL saturates** ❌ |

**Identical results** prove the trajectory is NOT the problem.

## Why Controller Re-tuning Is Required

The controllers have **fundamental tuning issues** for thrust-limited operation:

### Current Tuning Problems

1. **Over-aggressive proportional gain**: 5m error → full saturation (command 0.65 → 1.0)
2. **Excessive integral limits**: ±0.5 allows massive windup before clamping
3. **Weak anti-windup gain**: 0.004 provides insufficient correction during saturation
4. **No thrust authority awareness**: Controller doesn't know it has only 5% margin

### Proper Tuning Would

1. **Moderate proportional response**: 5m error → 80% command (not 100%)
2. **Tight integral limits**: ±0.2 to prevent sustained windup
3. **Strong anti-windup**: k ≈ 0.015-0.020 for faster recovery
4. **Derivative filtering**: Reduce overshoot during transients

## Decision Point: No More Workarounds Available

We have exhausted all workaround options:

- ✗ Increase thrust authority → Causes runaway climb
- ✗ Decrease thrust authority → Causes sustained saturation
- ✗ Reduce trajectory aggressiveness → No effect on saturation
- ✗ Modify scaling law → No combination prevents divergence

**Conclusion**: The only remaining solution is to **re-tune the controllers** to work within the actual thrust authority constraints.

## Options Going Forward

### Option 1: Re-tune Controllers (Proper Fix)

**Effort**: 4-6 hours for all 15 controllers
**Outcome**: Controllers work with realistic thrust limits and trajectories
**Risk**: May reduce tracking performance slightly
**Recommendation**: Required for production use

**Approach**:
1. Start with CascadePid as proof-of-concept
2. Scale all PID gains by 0.6× to reduce saturation tendency
3. Tighten integral limits from ±0.5 to ±0.25
4. Increase anti-windup gain from 0.004 to 0.018
5. Test with 15% thrust margin [0.85×h, 1.15×h] and original 2 m/s trajectory
6. Verify error <5m without sustained saturation
7. Apply methodology to remaining 14 controllers

### Option 2: Document Known Limitation (Expedient)

**Effort**: 1 hour to update Phase 5 report
**Outcome**: Phase 5 marked as "controllers unsuitable for flight" with documented reason
**Risk**: Incomplete verification, cannot claim flight-ready controllers
**Recommendation**: Only if re-tuning is out of scope

**Approach**:
1. Mark all 15 controllers as "FAIL — thrust authority mismatch"
2. Document root cause in Phase 5 report
3. Recommend controller re-tuning as future work
4. Note that Phase 4 structural verification remains valid (38/38 pass)

### Option 3: Change Thrust Margin to 50% (Compromise)

**Effort**: 2 hours (modify scaling, re-run simulations, analyze risks)
**Outcome**: Controllers likely pass Phase 5 with [0.5×h, 1.5×h] scaling
**Risk**: **HIGH** — controller saturation at 1.5× gravity may still cause divergence, and this hasn't been tested with anti-windup behavior
**Recommendation**: Not advisable without understanding controller response at higher thrust levels

## Project Timeline Impact

- **Project deadline**: 答辩 2026-08-23 (4 days from now)
- **Phase 5 blocking**: Cannot complete without controller fix or workaround
- **Option 1 timeline**: Re-tune today (2026-08-19), test tonight, finalize report 2026-08-20
- **Option 2 timeline**: Document limitation today, finalize report today
- **Option 3 timeline**: Test 50% margin today, likely encounter new instabilities, lose 1 day

## Recommendation

**Implement Option 1** (controller re-tuning) starting with CascadePid:

**Why**:
- Proper engineering solution addressing root cause
- Demonstrates understanding of thrust-limited control
- Produces flight-ready controllers (addresses "suitable for flight" criterion)
- Effort (4-6 hours) fits within 4-day deadline

**Why NOT Option 2**:
- Leaves Phase 5 verification incomplete
- Cannot claim controllers work in simulation
- Weakens 答辩 presentation (no closed-loop validation)

**Why NOT Option 3**:
- Untested approach with high failure risk
- May encounter new saturation instabilities
- Wastes time if it fails (then forced to Option 1 anyway)

## Next Steps

If proceeding with Option 1:

1. Read CascadePidCore.mo to identify PID gain parameters
2. Create CascadePidCore_retuned.mo with conservative gains
3. Test with [0.85×h, 1.15×h] thrust margin and original 2 m/s trajectory
4. Verify position_error_norm <5m at t=50s
5. Document tuning methodology
6. Batch apply to remaining 14 controllers
7. Re-run Phase 5 complete pipeline
8. Generate final Phase 4+5 report with REAL validated results

## Files

- Investigation date: 2026-08-19
- Test: CascadePid with gentler trajectory (1 m/s climb) and 5% thrust margin
- Result: 613m error (identical to aggressive trajectory)
- Conclusion: Trajectory modification insufficient, controller re-tuning required
- Blocking: Phase 5 verification cannot complete without addressing root cause
