# 15% Thrust Margin Test: Still Fails with 354m Error

## Executive Summary

Testing with 15% thrust margin [0.85×hover, 1.15×hover] **STILL FAILS** with 354m final error. Despite increasing available thrust authority from 1.05× gravity to 1.15× gravity, the controller exhibits oscillatory instability and slow divergence.

**Critical Finding**: The controller produces 65.10 rad/s (0.95% thrust surplus above hover), which is **LESS** than the expected maximum of 69.52 rad/s at saturation. The controller is NOT fully saturating, suggesting the problem is not insufficient thrust authority but rather **controller instability** or **incorrect thrust scaling implementation**.

## Simulation Results (15% Thrust Margin)

```
Time    Position_Z    Reference_Z    Error      Rotor_Command    Avg_Velocity
----    ----------    -----------    -----      -------------    ------------
t=0     0.0 m         0 m            0.0 m      60.43 rad/s      N/A
t=1     -0.43 m       2 m            2.4 m      64.37 rad/s      -0.43 m/s
t=2     -1.05 m       4 m            5.0 m      65.10 rad/s      -0.62 m/s
t=3     -1.58 m       6 m            7.6 m      65.10 rad/s      -0.53 m/s
t=4     -2.04 m       8 m            10.0 m     65.10 rad/s      -0.46 m/s
t=5     -2.44 m       10 m           12.4 m     65.10 rad/s      -0.40 m/s
t=10    -4.49 m       10 m           14.5 m     65.10 rad/s      -0.41 m/s
t=15    -6.91 m       15 m           21.9 m     65.10 rad/s      -0.49 m/s
t=20    -10.50 m      15 m           25.5 m     65.10 rad/s      -0.72 m/s
t=25    -13.05 m      15 m           28.0 m     65.10 rad/s      -0.51 m/s
t=30    -13.89 m      15 m           28.9 m     65.10 rad/s      -0.17 m/s
t=35    -13.53 m      15 m           28.5 m     65.10 rad/s      +0.07 m/s ⚠
t=40    -13.98 m      15 m           29.0 m     65.10 rad/s      -0.09 m/s
t=45    -15.05 m      15 m           30.1 m     65.10 rad/s      -0.21 m/s
t=50    -15.73 m      15 m           30.7 m     65.10 rad/s      -0.14 m/s
```

**Final Error: 353.98 m** (threshold: 5 m)
**Pass Status: FAIL** ❌

## Anomalous Behavior

### 1. Controller NOT Saturating at Maximum Thrust

**Expected behavior** with 15% margin:
- Max rotor speed: 64.79 × sqrt(1.15) = 69.52 rad/s
- Max thrust: 11.25 N (1.15× gravity)
- Controller should saturate at 69.52 rad/s for large errors

**Observed behavior**:
- Rotor command plateaus at 65.10 rad/s from t=2s onward
- This is only 0.47% above hover (64.79 rad/s)
- **NOT CLOSE** to the expected saturation at 69.52 rad/s
- Controller has 4.42 rad/s (6.4%) of unused thrust authority

### 2. Oscillatory Descent Pattern

Position shows damped oscillation:
- t=0-20s: Steady descent (accelerating downward)
- t=20-30s: Deceleration phase (descent slowing)
- t=30-35s: Brief **ASCENT** (+0.07 m/s upward velocity)
- t=35-50s: Descent resumes with oscillations

This pattern indicates:
- Controller integral windup during initial descent
- Anti-windup correction causes brief reversal
- System never reaches stable equilibrium
- Slow divergence continues

### 3. Physics Mismatch

With constant 65.10 rad/s thrust:
- Thrust produced: 9.8998 N (0.95% above gravity)
- Net upward force: 0.0928 N
- Upward acceleration: 0.0928 m/s²
- **Expected position at t=50s**: +115.97 m (upward climb)
- **Actual position at t=50s**: -15.73 m (descent)

**Discrepancy: 131.7 m**

This proves the system is NOT behaving according to simple constant-thrust physics. The controller is actively modulating thrust in response to error, but the control law is producing instability rather than convergence.

## Comparison: 5% vs 15% Margin

| Metric | 5% Margin | 15% Margin | Change |
|--------|-----------|------------|--------|
| Rotor command | 64.93 rad/s | 65.10 rad/s | +0.17 rad/s |
| Thrust surplus | 0.44% | 0.95% | +0.51% |
| Final Z position | -51.00 m | -15.73 m | +35.27 m (better) |
| Final error | 349.39 m | 353.98 m | +4.59 m (worse) |
| Max available thrust | 10.30 N (1.05×g) | 11.25 N (1.15×g) | +0.95 N |
| Used thrust | 10.35 N | 9.90 N | -0.45 N (LESS) |
| Pass status | FAIL | FAIL | No change |

**Key observation**: Increasing available thrust authority by 10% resulted in the controller using **LESS** thrust (9.90 N vs 10.35 N). This suggests the problem is not thrust authority but **controller gain mismatch** or **scaling interface implementation error**.

## Root Cause Hypotheses

### Hypothesis 1: GraphicalScalarRotorPreview Scaling Error

The thrust margin modification may not be working as intended. Let me verify the scaling formula:

```modelica
parameter Real max_speed_rad_s = hover_speed_rad_s * sqrt(1.0 + climb_margin_ratio)
parameter Real min_speed_rad_s = hover_speed_rad_s * sqrt(1.0 - descent_margin_ratio)
```

With climb_margin_ratio = 0.15:
- max_speed = 64.79 × sqrt(1.15) = 69.52 rad/s ✓ (correct formula)
- min_speed = 64.79 × sqrt(0.85) = 59.73 rad/s ✓ (correct formula)

The mapping should be:
- command = 0.0 → 59.73 rad/s
- command = 1.0 → 69.52 rad/s
- command = 0.65 (hover) → should produce 64.79 rad/s

**Verification needed**: Is the linear interpolation working correctly?

### Hypothesis 2: Controller Gains Too Conservative

The controller produces only 65.10 rad/s when errors are 10-30m. With aggressive PID tuning, a 12m error should drive the controller to saturation (command = 1.0 → 69.52 rad/s).

Current gains (from CascadePidCore.mo):
- outer_p_term(k=1.2)
- outer_i_term(k=0.8)
- inner_p_term(k=1.5)
- inner_i_term(k=0.4)

These gains were designed for hover at command ≈ 0.5. With hover shifted to command ≈ 0.65, the controller's effective gain is reduced by the remaining authority margin.

### Hypothesis 3: Integral Windup Preventing Convergence

Despite anti-windup gain k=0.004, the controller exhibits oscillatory behavior indicating windup is not fully suppressed. The integral accumulates during initial descent, then anti-windup slowly backs it off, causing position oscillation around an unstable equilibrium.

### Hypothesis 4: Gentler Trajectory Still Too Aggressive

Even at 1 m/s climb rate, the controller cannot catch up during t=0-10s, establishing a 14.5m tracking deficit. Subsequent oscillations never recover from this initial error.

## Diagnostic Actions Required

### Action 1: Verify Thrust Scaling Implementation (CRITICAL)

Check if GraphicalScalarRotorPreview actually implements the linear scaling correctly. The fact that the controller plateaus at 65.10 rad/s (not 69.52 rad/s) suggests either:
1. The scaling formula is wrong
2. The controller is not commanding saturation (command < 1.0)
3. There's a hidden saturation block between controller and rotor preview

**Next step**: Read the complete GraphicalScalarRotorPreview.mo to verify the scaling equation, then query the controller's output command (not rotor_command) to see if it's actually saturating at 1.0.

### Action 2: Test with Maximum Thrust Authority (50% Margin)

If 15% margin produces 65.10 rad/s instead of 69.52 rad/s, try 50% margin [0.5×hover, 1.5×hover]:
- Max rotor speed: 64.79 × sqrt(1.50) = 79.33 rad/s
- Max thrust: 14.70 N (1.50× gravity)
- Max upward acceleration: 4.93 m/s²

If the controller still plateaus at ~65 rad/s with 50% margin, this proves the problem is NOT thrust authority but controller implementation.

### Action 3: Test with Static Hover Command

Remove the trajectory entirely and command constant hover:
- Set position_ref = [0, 0, 0] (no climb)
- Run for 50s
- Check if controller converges to Z=0 with minimal error

If the controller cannot hold static hover, the problem is fundamental instability, not trajectory tracking.

### Action 4: Inspect Cascade Structure for Hidden Saturations

The cascade PID has two control loops (outer position → inner velocity). If the outer loop saturates at command=1.0 but this is fed to the inner loop which also has gain scaling, the final rotor command may never reach the scaling interface's maximum.

## Decision Point: Three Paths Forward

### Path A: Debug Thrust Scaling Implementation (1-2 hours)

1. Read complete GraphicalScalarRotorPreview.mo
2. Verify linear interpolation formula
3. Query controller's normalized command output (before scaling)
4. If command < 1.0, diagnose why controller isn't saturating
5. If command = 1.0 but rotor_command < max_speed, fix scaling bug

**Outcome if successful**: Controllers may pass with 15% margin
**Risk**: May discover deeper architectural issues

### Path B: Test 50% Thrust Margin (30 minutes)

1. Set climb_margin_ratio = 0.50
2. Re-run simulation
3. Check if controller finally uses full authority
4. If still fails, proves problem is not thrust authority

**Outcome**: Diagnostic clarity, not a solution
**Risk**: May still fail, wasting time

### Path C: Accept Phase 5 Failure and Document (1 hour)

1. Document that controllers fail Phase 5 with 5% and 15% margins
2. Root cause: architectural mismatch between controller design assumptions and thrust-limited interface
3. Recommendation: full controller redesign out of scope
4. Mark Phase 5 as "BLOCKED - requires controller re-architecture"

**Outcome**: Phase 5 documented as incomplete
**Risk**: Cannot claim "controllers validated for flight" in 答辩

## Recommended Next Step

**Execute Path A** (debug thrust scaling) because:
1. The 65.10 rad/s plateau is anomalous and suggests a fixable bug
2. Only 1-2 hours investment to diagnose
3. If successful, unblocks Phase 5 completion
4. If unsuccessful, provides clear evidence for Path C

**Specific next action**: Read GraphicalScalarRotorPreview.mo lines 20-26 to verify the speed_range calculation and the actual connection between `command` input and `rotor_command[i]` outputs.

## Files

- Investigation date: 2026-08-19 02:47
- Configuration: Baseline CascadePidCore + 15% thrust margin [0.85×hover, 1.15×hover] + 1 m/s trajectory
- Result: 354m error, vehicle oscillates around -15m final position
- Anomaly: Controller plateaus at 65.10 rad/s instead of expected 69.52 rad/s saturation
- Next action: Debug thrust scaling implementation to understand why full authority is not used
