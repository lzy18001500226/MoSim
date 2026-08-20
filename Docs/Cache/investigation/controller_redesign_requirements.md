# Controller Re-Architecture Requirements for Flight Readiness

## Document Purpose

This document specifies the technical requirements for redesigning MoSim quadrotor controllers to achieve flight-ready trajectory tracking performance. The requirements are derived from Phase 5 investigation findings documented in phase5_final_report.md and phase5_architectural_limitation_final.md.

## Problem Statement

Current controllers fail Phase 5 trajectory tracking (0/10 controllers tested with gentle trajectories and increased thrust margins) due to architectural assumptions incompatible with thrust-limited quadrotor operation:

1. **Hover Point Assumption**: Controllers designed assuming hover at mid-range (command ≈ 0.5) with ±50% authority above/below
2. **Reality**: Actual interface provides hover at command = 0.65, leaving only +35% authority above hover
3. **Consequence**: Controllers cannot access upper 30-45% of available thrust range due to internal saturation limits

## Root Cause

From CascadePidCore.mo investigation (representative of cascade-structured controllers):

```modelica
// Line 77: Integral pre-saturation clips accumulator before gain scaling
SysplorerEmbeddedCoder.Discontinuities.Saturation outer_integral_pre_limit(upLimit=0.5,lowLimit=-0.5)

// Line 80: I-term gain applied after saturation
SysplorerEmbeddedCoder.MathOperation.Gain outer_i_term(k=0.48)

// Line 89: Outer command limit (never reached due to pre-saturation)
SysplorerEmbeddedCoder.Discontinuities.Saturation outer_command_limit(upLimit=1.0,lowLimit=-1.0)
```

**Observed Behavior**:
- For tracking errors > 10m, integral saturates at 0.5 within 2 seconds
- I-term contribution: 0.5 × 0.48 = 0.24
- P-term contribution (30m error): 0.288
- Total outer_command: 0.528
- After inner loop: final command = 0.550 (55% of authority)
- **45% of thrust range unused**

## Redesign Requirements

### Requirement 1: Dynamic Hover Point Awareness

**Current State**: Controllers assume hover = command 0.5 (hardcoded design assumption)

**Required State**: Controllers must detect or be calibrated for actual hover command value

**Implementation Options**:
1. **Calibration Parameter**: Add `hover_command_normalized` parameter to controller, passed from GraphicalScalarRotorPreview
2. **Dynamic Detection**: Implement online hover point estimation from steady-state measurements
3. **Relative Command Space**: Redesign controller to work in relative command space [hover - margin, hover + margin] rather than absolute [0, 1]

**Acceptance Criterion**: Controller maintains hover equilibrium with <0.1m steady-state error for any hover command value in [0.3, 0.8]

### Requirement 2: Thrust Authority Awareness

**Current State**: Controllers assume 2-3× gravity thrust authority (flight-proven baseline)

**Required State**: Controllers must know available thrust authority and saturate gracefully

**Implementation Options**:
1. **Authority Parameters**: Pass `max_thrust_ratio` and `min_thrust_ratio` (e.g., 1.15× and 0.85× gravity) to controller
2. **Command Scaling**: Scale controller gains based on available authority above/below hover
3. **Saturation Prediction**: Implement predictive saturation detection and trajectory pre-shaping

**Acceptance Criterion**: Controller uses ≥90% of available thrust authority when tracking errors exceed 10m

### Requirement 3: Redesigned Integral Saturation

**Current State**: Integral pre-limit ±0.5 designed for hover at 0.5, prevents saturation with hover at 0.65

**Required State**: Integral limits scaled relative to available authority and hover point

**Implementation Options**:
1. **Asymmetric Limits**: Different saturation limits above/below hover (e.g., +0.35 above, -0.65 below for hover at 0.65)
2. **Authority-Scaled Limits**: Scale integral limits proportional to available thrust authority
3. **Remove Pre-Saturation**: Saturate only at outer_command_limit, strengthen anti-windup to compensate

**Acceptance Criterion**: Integral can accumulate sufficiently to drive outer_command to within 95% of outer_command_limit

### Requirement 4: Gain Re-Tuning for Thrust-Limited Operation

**Current State**: P/I/D gains tuned assuming aggressive thrust authority

**Required State**: Gains tuned for realistic thrust margins (5-15% above/below hover)

**Implementation Options**:
1. **Manual Tuning**: Use Ziegler-Nichols or similar method with realistic thrust limits
2. **Optimization**: Use trajectory optimization to find gains minimizing tracking error subject to thrust constraints
3. **Gain Scheduling**: Implement gain scheduling based on tracking error magnitude and available authority

**Acceptance Criterion**: Controller achieves <5m tracking error for ClimbTrajectory (1 m/s climb) with 15% thrust margin

### Requirement 5: Predictive Saturation Avoidance

**Current State**: Controllers react to saturation after it occurs, causing limit-cycle behavior

**Required State**: Controllers anticipate saturation and adjust trajectory/gains proactively

**Implementation Options**:
1. **Trajectory Pre-Shaping**: Feed-forward trajectory planner respects thrust authority limits
2. **Gain De-Scheduling**: Reduce gains as command approaches saturation to prevent overshoot
3. **Reference Governor**: External block modulates reference trajectory to maintain controller within non-saturating regime

**Acceptance Criterion**: Controller exhibits monotonic convergence (no oscillations) for step references up to 10m with 15% thrust margin

## Affected Controllers

### High Priority (Cascade Structure, Likely Affected)

Based on Phase 5 testing and architectural similarity:

1. **cascade_pid** - CONFIRMED affected (349m error with 5% margin, 354m with 15% margin)
2. **linear_mpc** - Failed Phase 5 (11.6m error with original trajectory)
3. **mrac** - Failed Phase 5 (12.8m error with original trajectory)
4. **pole_placement_luenberger** - Failed Phase 5 (14.7m error with original trajectory)
5. **adaptive_mpc** - Failed Phase 5 (9.4m error with original trajectory)
6. **super_twisting_smc** - Failed Phase 5 (6.6m error with original trajectory)
7. **backstepping_baseline** - Failed Phase 5 (7.2m error with original trajectory)
8. **dfbc_smooth_robust_bodyrate** - Failed Phase 5 (6.9m error with original trajectory)
9. **lqi_baseline** - Failed Phase 5 (8.5m error with original trajectory)
10. **terminal_smc** - Failed Phase 5 (5.9m error with original trajectory)

### Medium Priority (Passed Phase 5, But May Have Margin Issues)

Controllers that passed with original trajectory but may benefit from redesign:

- **lqr_baseline** - 4.78m error (close to 5m threshold)
- **passivity_based_control** - 4.08m error
- **robust_mpc** - 4.33m error
- **fuzzy_pid** - 4.21m error
- **adaptive_smc** - 4.41m error
- **neural_pid** - 4.17m error

### Low Priority (Passed Phase 5 with Margin)

Controllers with <4m error likely have better thrust authority handling:

- **fixed_awff_pid** - 0.83m error (best performance)
- **explicit_gain_scheduled_mpc** - 0.83m error
- **h2_state_feedback** - 0.99m error
- **dfbc_smooth_robust_attitude** - 1.16m error
- **hinf_hover_wrench** - 1.51m error

## Implementation Plan

### Phase A: Prototype Redesign on CascadePid (3-4 days)

1. **Day 1**: Implement Requirement 1 (dynamic hover point awareness)
   - Add `hover_command_normalized` parameter
   - Redesign outer/inner loop to work relative to hover
   - Initial testing with hover at 0.65

2. **Day 2**: Implement Requirement 3 (redesigned integral saturation)
   - Compute asymmetric integral limits based on hover point
   - Scale limits: upper = (1.0 - hover) × margin_factor, lower = hover × margin_factor
   - Test integral accumulation reaches near-saturation

3. **Day 3**: Implement Requirement 4 (gain re-tuning)
   - Manual tuning with 15% thrust margin constraint
   - Validate no saturation for <10m errors
   - Ensure <5m tracking error on ClimbTrajectory

4. **Day 4**: Implement Requirements 2 & 5 (authority awareness, predictive saturation)
   - Add thrust authority parameters
   - Implement gain scheduling based on command proximity to limits
   - Final validation and documentation

**Deliverable**: CascadePidCoreV2.mo passing Phase 5 with <5m error

### Phase B: Pattern Extraction and Documentation (1 day)

1. Document architectural patterns from CascadePid redesign
2. Identify which patterns apply to each controller family:
   - PID family (cascade_pid, official_pid, fuzzy_pid, neural_pid, gain_scheduled_pid)
   - Backstepping family (backstepping_baseline, adaptive_backstepping)
   - MPC family (linear_mpc, adaptive_mpc, robust_mpc, tube_mpc)
   - SMC family (super_twisting_smc, terminal_smc, integral_smc, adaptive_smc)
3. Create redesign templates for each family

**Deliverable**: Controller redesign pattern library

### Phase C: Batch Redesign (3-5 days)

1. **Days 1-2**: Apply patterns to high-priority controllers (10 controllers)
2. **Day 3**: Apply patterns to medium-priority controllers (6 controllers)
3. **Days 4-5**: Re-run Phase 4 (CheckModel) and Phase 5 (ClimbTrajectory) on all redesigned controllers

**Deliverable**: All high/medium priority controllers passing Phase 5

### Phase D: Validation and Documentation (2 days)

1. **Day 1**: Extended validation
   - Test with multiple trajectory types (climb, descent, hover, step response)
   - Test with various thrust margins (5%, 10%, 15%, 20%)
   - Measure tracking performance vs. original controllers
2. **Day 2**: Documentation
   - Update controller documentation with redesign notes
   - Create migration guide for users with existing tuning
   - Document performance improvements

**Deliverable**: Complete Phase 5 validation report with before/after comparison

## Total Timeline

- **Prototype**: 3-4 days
- **Patterns**: 1 day
- **Batch**: 3-5 days
- **Validation**: 2 days
- **Total**: 9-12 days (~2 weeks)

## Success Criteria

### Minimum Viable (Required for Flight Readiness)

1. ✓ All high-priority controllers (10 controllers) pass Phase 5 (<5m error)
2. ✓ Controllers use ≥90% of available thrust authority when saturating
3. ✓ No limit-cycle behavior (oscillations around unstable equilibrium)
4. ✓ Monotonic convergence for step references <10m

### Target (Desirable for Production)

1. ✓ All medium-priority controllers (6 controllers) pass Phase 5
2. ✓ Tracking error <3m average across all controllers
3. ✓ Controllers maintain performance with 5-20% thrust margin range
4. ✓ Documentation and migration guide complete

### Stretch (Nice-to-Have)

1. ✓ Low-priority controllers improved (error <2m)
2. ✓ Automated gain tuning procedure for new controllers
3. ✓ Real-time saturation prediction and trajectory adaptation

## Risk Mitigation

### Risk 1: Redesigned Controllers Become Unstable

**Likelihood**: Medium (removing integral pre-saturation may cause instability)

**Mitigation**:
- Implement redesign incrementally (one requirement at a time)
- Validate stability at each step before proceeding
- Keep anti-windup mechanisms strong during transition
- Fallback to original design if instability persists after 2-3 iterations

### Risk 2: Gains Cannot Be Found That Satisfy Constraints

**Likelihood**: Low (other controllers already pass Phase 5)

**Mitigation**:
- Study successful controllers (fixed_awff_pid, explicit_gain_scheduled_mpc) for patterns
- Use optimization-based tuning if manual tuning fails
- Accept slightly relaxed criterion (6-7m error) if 5m proves unattainable

### Risk 3: Timeline Exceeds 2 Weeks

**Likelihood**: Medium (unforeseen issues during batch redesign)

**Mitigation**:
- Prioritize high-priority controllers first
- Accept partial completion (10/16 controllers redesigned) if timeline pressured
- Document remaining work clearly for future continuation

## References

- [phase5_final_report.md](C:\Users\HP\Desktop\MoSim\Docs\Cache\investigation\phase5_final_report.md) - Complete Phase 5 investigation summary
- [phase5_architectural_limitation_final.md](C:\Users\HP\Desktop\MoSim\Docs\Cache\investigation\phase5_architectural_limitation_final.md) - Detailed architectural analysis
- [controller_not_saturating_root_cause.md](C:\Users\HP\Desktop\MoSim\Docs\Cache\investigation\controller_not_saturating_root_cause.md) - Root cause with command chain traces
- [CascadePidCore.mo](C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Control\PidFamily\CascadePid\CascadePidCore.mo) - Reference implementation for redesign
- [GraphicalScalarRotorPreview.mo](C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Experiment\Adapters\GraphicalScalarRotorPreview.mo) - Thrust scaling interface specification

---

**Document Date**: 2026-08-19
**Status**: Requirements defined, implementation not started
**Estimated Effort**: 9-12 days (2 weeks)
**Priority**: Future work, out of scope for 2026-08-23 答辩
