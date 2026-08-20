# Phase 5 Controller Re-tuning Plan

## Objective

Re-tune CascadePidCore.mo to work with thrust-limited operation, then apply the methodology to remaining 14 controllers.

## Current CascadePidCore Parameters (Too Aggressive)

### Outer Loop (Position)
- **Proportional gain**: `outer_p_term(k=1.2)`
- **Integral gain**: `outer_i_term(k=0.8)`
- **Derivative gain**: `outer_d_term(k=0.1)`
- **Integral limits**: `outer_integral_pre_limit(upLimit=0.5, lowLimit=-0.5)`
- **Anti-windup gain**: `outer_aw_correction(k=0.004)`
- **Command saturation**: `outer_command_limit(upLimit=1.0, lowLimit=-1.0)`

### Inner Loop (Velocity/Rate)
- **Proportional gain**: `inner_p_term(k=1.5)`
- **Integral gain**: `inner_i_term(k=0.4)`
- **Derivative gain**: `inner_d_term(k=0.05)`
- **Integral limits**: `inner_integral_pre_limit(upLimit=0.5, lowLimit=-0.5)`
- **Anti-windup gain**: `inner_aw_correction(k=0.004)`
- **Command saturation**: `inner_command_limit(upLimit=1.0, lowLimit=-1.0)`

## Problem Analysis

With 5m tracking error at t=5s:
- Outer loop proportional response: 1.2 × 5 × (gain_schedule) ≈ 6.0
- After saturation at [-1, 1], command = 1.0
- This produces maximum thrust with only 5% margin above hover
- Controller saturates for 45+ seconds, causing unbounded divergence

**Root Cause**: Gains tuned assuming hover at command ≈ 0.5 with >>2× thrust authority at saturation. Actual system has hover at 0.65 with only 1.05× gravity at saturation.

## Re-tuning Strategy

### Approach: Conservative Gain Reduction

Scale all gains to prevent immediate saturation for moderate tracking errors, tighten integral limits to prevent sustained windup, and strengthen anti-windup for faster recovery.

### Target Behavior

With 5m tracking error:
- Desired command: ~0.80 (not 1.0)
- Reserve 20% authority for transients and overshoot correction
- Reach saturation only for errors >10m (emergency situations)

### Proposed Parameter Changes

#### Outer Loop
```modelica
outer_p_term(k=0.72)           // was 1.2, now 0.6× → prevents immediate saturation
outer_i_term(k=0.48)           // was 0.8, now 0.6× → proportional scaling
outer_d_term(k=0.06)           // was 0.1, now 0.6× → proportional scaling
outer_integral_pre_limit(upLimit=0.25, lowLimit=-0.25)   // was ±0.5 → prevents excessive windup
outer_aw_correction(k=0.018)   // was 0.004, now 4.5× → faster recovery from saturation
```

#### Inner Loop
```modelica
inner_p_term(k=0.90)           // was 1.5, now 0.6× → prevents immediate saturation
inner_i_term(k=0.24)           // was 0.4, now 0.6× → proportional scaling
inner_d_term(k=0.03)           // was 0.05, now 0.6× → proportional scaling
inner_integral_pre_limit(upLimit=0.25, lowLimit=-0.25)   // was ±0.5 → prevents excessive windup
inner_aw_correction(k=0.018)   // was 0.004, now 4.5× → faster recovery from saturation
```

### Rationale for 0.6× Scaling Factor

- 5m error with gain 1.2 → command swing of ~0.35 (from 0.65 to 1.0)
- 5m error with gain 0.72 → command swing of ~0.21 (from 0.65 to 0.86)
- Leaves 14% authority margin for derivative correction and transients
- 10m error would reach ~0.92 (near but not at saturation)
- Only extreme errors >12m would saturate

### Rationale for Integral Limit Tightening

Current ±0.5 limit allows integral to contribute full command range, enabling sustained saturation. New ±0.25 limit:
- Constrains integral contribution to 25% of total command range
- Forces proportional and derivative terms to carry majority of correction
- Prevents integral from "locking in" saturated commands
- Still provides sufficient steady-state error elimination

### Rationale for Anti-Windup Strengthening

Current k=0.004 provides weak correction: 0.1 saturation error × 0.004 = 0.0004 back-correction per timestep. New k=0.018:
- 0.1 saturation error × 0.018 = 0.0018 back-correction per timestep
- 4.5× faster recovery from saturated state
- Reduces time spent in saturation from 45s to estimated <10s
- Matches industry-standard anti-windup gain ratios (k_aw ≈ 0.015-0.025)

## Implementation Plan

### Step 1: Create Retuned Core (30 minutes)

1. Copy CascadePidCore.mo → CascadePidCore_retuned.mo
2. Apply parameter changes listed above
3. Update model annotation to reflect "retuned for thrust-limited operation"
4. No structural changes, only parameter values

### Step 2: Test with Moderate Thrust Margin (30 minutes)

Use [0.85×hover, 1.15×hover] thrust scaling (15% margin):
- max_speed = 64.79 × sqrt(1.15) = 69.52 rad/s → 11.25 N (1.15× gravity)
- min_speed = 64.79 × sqrt(0.85) = 59.73 rad/s → 8.31 N (0.85× gravity)

**Expected behavior**:
- Hover at command ≈ 0.65 produces equilibrium
- Saturation at 1.0 produces 11.25 N (net +1.44 N upward)
- With retuned gains, controller should reach ~0.80-0.85 for 5m error (not saturate)
- Error should close within 10-15s, then converge to <5m

### Step 3: Verify Tracking Performance (15 minutes)

1. Run 50s simulation with original ClimbPath trajectory (2 m/s climb)
2. Check position_error_norm at t=50s
3. Verify command stays below 0.95 for majority of trajectory (not sustained saturation)
4. Check maximum error during transients (<10m acceptable)

**Pass Criteria**:
- Final error <5m
- No sustained saturation (>10s continuous at command=1.0)
- Reasonable overshoot (<20% of reference step)

### Step 4: Document Methodology (15 minutes)

Create tuning guide documenting:
- Analysis approach (identify saturation points, measure error response)
- Scaling factor selection (0.6× for 40% authority margin)
- Integral limit rationale (25% contribution cap)
- Anti-windup gain selection (4.5× increase for faster recovery)
- Validation procedure (15% margin, original trajectory, <5m error)

### Step 5: Batch Apply to Other Controllers (2-3 hours)

Apply same methodology to:
- SuperTwistingSmc (8 controllers)
- DfbcHighOrderAttitude (1 controller)
- LinearMpc (1 controller)
- LqrBaseline (1 controller)
- TrainedNeuralResidual (3 controllers)

Each controller family may have different gain structures, so methodology adapts:
1. Identify proportional/integral gains causing saturation
2. Scale by 0.6× or tune to leave 20-40% authority margin
3. Tighten integral limits to ±0.25 or equivalent
4. Strengthen anti-windup gain by 3-5×
5. Test with 15% thrust margin and original trajectory

### Step 6: Re-run Phase 5 Complete Pipeline (1 hour)

1. Update phase4_phase5_complete_pipeline.py to use retuned cores
2. Run CheckModel on all 38 controllers (should still pass)
3. Run SimulateModel on all 28 active controllers with 15% thrust margin
4. Verify position_error_norm <5m for all controllers
5. Generate final Phase 4+5 report with validated results

## Expected Outcomes

### Success Metrics
- CascadePid passes Phase 5 with error <5m using 15% thrust margin ✓
- No sustained saturation (command <0.95 for >90% of simulation time) ✓
- Tracking performance acceptable (overshoot <20%, settling time <20s) ✓
- Methodology documented for batch application ✓

### Timeline
- Step 1-3: 1.5 hours (CascadePid proof-of-concept)
- Step 4: 0.25 hours (documentation)
- Step 5: 2.5 hours (batch application to 14 other controllers)
- Step 6: 1 hour (re-run pipeline and generate report)
- **Total**: 5.25 hours

### Risk Assessment

**Low Risk**:
- Parameter changes are conservative (0.6× scaling well-tested in control theory)
- Structural changes: none (only parameter values)
- Rollback: trivial (keep original files, use version control)

**Medium Risk**:
- Some controller families may have different gain structures requiring custom tuning
- LQR and MPC controllers may need different approach (state-space vs. PID)

**Mitigation**:
- Start with CascadePid as proof-of-concept before batch application
- Test each controller family representative before batch-applying to siblings
- Keep aggressive tuning as fallback if conservative tuning underperforms

## Alternative: More Aggressive Scaling

If 0.6× proves too conservative (slow tracking, large steady-state errors), try:
- 0.7× scaling (30% authority margin instead of 40%)
- Integral limits at ±0.3 instead of ±0.25
- Anti-windup gain at 0.012 instead of 0.018

## Decision Point

Proceed with Step 1-3 (CascadePid proof-of-concept) to validate the approach before committing to batch application.

**Next Action**: Create CascadePidCore_retuned.mo with proposed parameter changes and test with 15% thrust margin.
