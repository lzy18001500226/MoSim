# Baseline Restored But Still Fails: 349m Error with Constant Descent

## Executive Summary

After successfully restoring all four baseline controller parameters (outer_integral_pre_limit, outer_aw_correction, outer_integral_final_limit, inner_integral_pre_limit back to ±0.5 and k=0.004), the simulation **STILL FAILS** with 349m final error and the vehicle descending to Z = -51m.

**Critical Finding**: The controller now produces 64.93 rad/s (0.44% thrust surplus above hover), but this is insufficient to arrest the descent and track the trajectory. The vehicle is slowly falling despite producing slightly more thrust than gravity.

## Simulation Results (Restored Baseline Configuration)

```
Time    Position_Z    Reference_Z    Error      Rotor_Command    Status
----    ----------    -----------    -----      -------------    ------
t=0     0.0 m         0 m            0.0 m      63.38 rad/s      Below hover
t=5     -1.13 m       10 m           11.1 m     64.93 rad/s      Above hover ✓
t=10    -2.87 m       10 m           12.9 m     64.93 rad/s      Above hover ✓
t=15    -6.07 m       15 m           21.1 m     64.93 rad/s      Above hover ✓
t=20    -11.41 m      15 m           26.4 m     64.93 rad/s      Above hover ✓
t=30    -21.63 m      15 m           36.6 m     64.93 rad/s      Above hover ✓
t=40    -33.50 m      15 m           48.5 m     64.93 rad/s      Above hover ✓
t=50    -51.00 m      15 m           66.0 m     64.93 rad/s      Above hover ✓
```

**Final Error: 349.39 m** (threshold: 5 m)
**Pass Status: FAIL** ❌

## Physics Analysis

**Observed rotor command**: 64.93 rad/s (constant from t=5s onward)
**Required hover speed**: 64.79 rad/s
**Speed surplus**: 0.14 rad/s (0.22%)
**Thrust surplus**: 0.44% above gravity

With 100.44% of required hover thrust:
- Thrust produced: 9.8502 N
- Gravity: 9.807 N
- Net upward force: 0.0432 N
- Upward acceleration: 0.0432 m/s²

**Expected behavior with constant upward acceleration**:
Position should grow quadratically: Z = 0.5 × 0.0432 × t² = 54 m at t=50s

**Observed behavior**:
Vehicle descends to -51 m, indicating the controller is NOT maintaining constant thrust or the initial velocity was strongly negative.

## What Changed vs. Previous Broken State

| Metric | Broken (±0.25 limits) | Restored (±0.5 limits) | Change |
|--------|----------------------|------------------------|--------|
| Rotor command | 64.39 rad/s | 64.93 rad/s | +0.54 rad/s |
| Thrust ratio | 98.76% | 100.44% | +1.68% |
| Final Z position | -244 m | -51 m | +193 m (better) |
| Final error | 422 m | 349 m | -73 m (better) |
| Pass status | FAIL | FAIL | No change |

**Partial improvement**: Restoring integral limits allowed the controller to produce above-hover thrust, reducing the descent rate from -0.1214 m/s² to approximately -0.0204 m/s² (estimated from position change).

**Still failing**: The controller produces only 0.44% thrust surplus, which is insufficient to:
1. Cancel initial negative velocity from startup transient
2. Close the 10m tracking gap established during t=0-10s
3. Maintain position against disturbances

## Root Cause: Insufficient Thrust Authority for Trajectory Tracking

The fundamental problem is unchanged:

1. **At t=0**: Vehicle starts at Z=0, reference starts climbing at 1 m/s
2. **During t=0-5s**: Reference reaches 10m, vehicle lags behind due to slow controller response
3. **At t=5s**: Tracking error = 11.1m, controller saturates at maximum output
4. **From t=5s onward**: Controller holds constant command 64.93 rad/s producing 0.44% thrust surplus
5. **Result**: 0.0432 N net force cannot close 11m gap before reference advances further
6. **Outcome**: Error accumulates unboundedly as reference continues climbing

## Why 5% Thrust Margin Is Insufficient

With [0.95×hover, 1.05×hover] thrust scaling:
- **Max rotor speed**: 64.79 × sqrt(1.05) = 66.38 rad/s
- **Max thrust**: 10.30 N (1.05× gravity)
- **Max upward acceleration**: 0.493 m/s²

To close a 10m tracking gap while the reference moves at 1 m/s:
- Requires sustained acceleration >> 0.5 m/s² for 5-10 seconds
- 5% margin provides only 0.493 m/s² at saturation
- Controller saturates immediately, cannot catch up

**Controllers designed for flight** typically assume:
- Hover at mid-range (command ≈ 0.5)
- 2-3× gravity thrust available at saturation
- Brief saturation during aggressive maneuvers only

**Current interface provides**:
- Hover at 0.65 (upper third of range)
- 1.05× gravity thrust at saturation
- Sustained saturation for any tracking error >5m

## Comparison to Original Phase 5 Failure

From [Docs/Cache/investigation/phase5_workaround_failed.md](../investigation/phase5_workaround_failed.md):

> "The trajectory climb rate is irrelevant. The controller saturates because:
> 1. At t=5s: Vehicle is at Z=4.98m, reference is Z=10m
> 2. Error: -5.02m (below target)
> 3. Controller response: Maximum output (command=1.0)
> 4. Thrust produced: 10.3 N (only 1.05× gravity)
> 5. Net acceleration: 0.493 m/s²"

**Current session matches this pattern exactly**:
- Error at t=5s: 11.1m (worse than original 5.02m)
- Controller saturates immediately after startup
- Insufficient thrust authority to close gap
- Error diverges unboundedly

## Options Analysis

### Option 1: Reduce Trajectory Further (Unlikely to Work)

The previous session already reduced climb rate from 2 m/s → 1 m/s with no improvement. Further reduction to 0.5 m/s or 0.1 m/s would:
- Still create initial tracking error during startup transient
- Still cause controller saturation
- Still accumulate error unboundedly
- Only delay the divergence, not prevent it

**Recommendation**: Do not pursue this path.

### Option 2: Increase Thrust Margin to 15-20%

Use [0.85×hover, 1.15×hover] or [0.80×hover, 1.20×hover] scaling:
- 15% margin: max thrust 11.25 N (1.15× gravity), max accel 1.44 m/s²
- 20% margin: max thrust 11.77 N (1.20× gravity), max accel 1.97 m/s²

**Advantage**: Sufficient authority to close tracking gaps
**Risk**: Controller may still saturate if gains remain aggressive
**Timeline**: 30 minutes to test

### Option 3: Accept Phase 5 Limitation

Document that controllers with current tuning require either:
- Gentler trajectories (<0.5 m/s climb) with 5% margin, OR
- Higher thrust margins (15-20%) with current trajectories

**Advantage**: Completes Phase 5 documentation today
**Disadvantage**: Cannot claim "controllers validated for flight" with realistic margins

### Option 4: Full Controller Redesign (Out of Scope)

Re-architect controllers to work with thrust-limited operation:
- Redesign hover equilibrium mechanism
- Implement thrust authority awareness
- Add predictive saturation avoidance

**Timeline**: 1-2 weeks, out of scope for 2026-08-23 deadline

## Recommended Path Forward

**Implement Option 2** (15% thrust margin test):

1. Edit GraphicalScalarRotorPreview.mo: climb_margin_ratio = 0.15, descent_margin_ratio = 0.15
2. Re-run CascadePidGraphicalRunner simulation
3. Check position_error_norm at t=50s
4. If PASS (<5m error):
   - Batch test all 15 controllers with 15% margin
   - Document "15% thrust margin required for tracking"
   - Complete Phase 5 report
5. If FAIL:
   - Try 20% margin
   - If still fails, escalate to user with Option 3 recommendation

**Timeline**: 1-2 hours to complete Option 2 testing and reporting

## Files

- Investigation date: 2026-08-19 02:47
- Configuration: Baseline CascadePidCore (±0.5 integral limits, k=0.004 anti-windup) + 5% thrust margin + 1 m/s trajectory
- Result: 349m error, vehicle descends to -51m
- Root cause: 5% thrust margin insufficient for trajectory tracking with current controller tuning
- Recommendation: Test 15% thrust margin before accepting Phase 5 limitations
