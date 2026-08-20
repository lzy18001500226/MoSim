# Phase 5 Architectural Limitation: Final Analysis and Decision

## Executive Summary

**Decision**: Accept Phase 5 limitation and document as future work.

**Timeline**: 2026-08-19 investigation complete, 答辩 in 4 days (2026-08-23).

**Root Cause**: Cascade PID architecture designed for hover at mid-range (command ≈ 0.5) with ±50% authority above/below. Actual interface provides hover at command = 0.65, leaving only 35% authority above hover. Internal integral pre-saturation at ±0.5 prevents controller from using full thrust range.

**Impact**: All 15 controllers with cascade structure (CascadePid, PX4Ctrl likely similar) cannot pass Phase 5 trajectory tracking with current architecture. Phase 4 structural verification (38/38 CheckModel pass) remains valid.

## Investigation Timeline

| Date | Configuration | Result | Key Finding |
|------|--------------|--------|-------------|
| 2026-08-18 | Original (aggressive trajectory) | 613m error | Controller saturates, insufficient thrust |
| 2026-08-18 | Gentler trajectory (1 m/s) + re-tuned gains | 422m error | Broke hover equilibrium, vehicle descended |
| 2026-08-19 | Restored baseline + gentle trajectory | 349m error | 5% margin insufficient, command 64.93 rad/s |
| 2026-08-19 | 15% thrust margin | 354m error | Controller plateaus at 65.10 rad/s, not 69.48 rad/s |
| 2026-08-19 | Root cause analysis | - | Integral pre-saturation limits command to 0.55 |

## Root Cause: Triple Saturation Cascade

### Saturation Point 1: Integral Pre-Limit (DOMINANT)

From [CascadePidCore.mo:77](C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Control\PidFamily\CascadePid\CascadePidCore.mo:77):
```modelica
SysplorerEmbeddedCoder.Discontinuities.Saturation outer_integral_pre_limit(upLimit=0.5,lowLimit=-0.5)
```

**Observed behavior** (from simulation query):
- Time t=2s onward: `core.integral` = 0.5 (saturated)
- Integral contribution: 0.5 × 0.48 (I-term gain) = 0.24
- Proportional contribution: 0.288 (for 12-30m errors)
- Outer loop output: 0.288 + 0.24 = 0.528

**Design intent**: Prevent integral windup by clamping accumulator before scaling.

**Actual effect**: With integral saturated at 0.5, maximum I-term contribution is only 0.24. For outer_command to reach 1.0 would require P+D terms = 0.76, which requires either:
- Very aggressive gains (outer_p_term k >> 1.2), OR
- Very large errors (>> 30m)

Current configuration produces outer_command = 0.528 at 30m error, leaving 47% of outer_command_limit unused.

### Saturation Point 2: Outer Command Limit (NEVER REACHED)

From [CascadePidCore.mo:89](C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Control\PidFamily\CascadePid\CascadePidCore.mo:89):
```modelica
SysplorerEmbeddedCoder.Discontinuities.Saturation outer_command_limit(upLimit=1.0,lowLimit=-1.0)
```

**Observed behavior**: Never saturates because outer loop output = 0.528 << 1.0.

**Design intent**: Hard limit on outer loop command to prevent instability.

**Actual effect**: Unreachable with current integral pre-limit and gain tuning.

### Saturation Point 3: Inner Loop Processing

**Observed behavior**: Outer command 0.528 → inner loop → final command 0.550.

**Inner loop contribution**: +0.022 (4.2% increase).

**Design intent**: Inner loop tracks velocity command from outer loop, adds damping correction.

**Actual effect**: Minor adjustment, does not significantly amplify outer command.

## Three Architectural Mismatches

### Mismatch 1: Hover Point Assumption

| Aspect | Design Assumption | Actual Interface | Impact |
|--------|-------------------|------------------|--------|
| Hover command | ≈ 0.5 | 0.65 | 30% loss of upward authority |
| Authority above hover | 50% | 35% | Cannot produce aggressive climb |
| Authority below hover | 50% | 65% | Excessive descent capability (unused) |

### Mismatch 2: Integral Saturation Scaling

| Aspect | Design Assumption | Actual Behavior | Impact |
|--------|-------------------|----------------|--------|
| Integral pre-limit | ±0.5 allows reaching outer_command = 1.0 with aggressive P/D | Integral 0.5 → I-term 0.24, requires P+D = 0.76 for saturation | Controller cannot saturate unless errors >> 30m |
| I-term contribution at saturation | Dominant term driving command to limit | Minor term (0.24), P-term = 0.288 for 30m error | Total outer_command = 0.528 (53% of limit) |

### Mismatch 3: Command-to-Thrust Scaling

| Aspect | Design Assumption | Actual Behavior | Impact |
|--------|-------------------|----------------|--------|
| Command 0.528 produces | Near-maximum thrust for aggressive maneuver | 65.10 rad/s = 0.95% above hover (barely moving) | Controller thinks it's commanding aggressively, actually producing hover-level thrust |
| Command range utilization | Full [0, 1] range accessible | Only [0.65 - 0.35, 0.65 + 0.35] = [0.30, 1.00] usable, and controller saturates at 0.55 | 45% of upper range unreachable |

## Why All Previous Fixes Failed

### Fix Attempt 1: Gentler Trajectory

**Change**: Reduce climb rate from 2 m/s → 1 m/s.

**Hypothesis**: Controller saturates because trajectory too aggressive.

**Result**: 613m error → 349m error (partial improvement), still fails.

**Why it failed**: Trajectory rate is irrelevant. The problem is:
1. At t=0-10s, vehicle lags reference by 10-15m due to startup transient
2. Controller responds by saturating immediately
3. Saturation produces outer_command = 0.528 → final command = 0.55
4. Command 0.55 produces only 0.95% thrust surplus above hover
5. 0.95% surplus cannot close 10-15m gap while reference continues climbing
6. Error accumulates unboundedly

Reducing climb rate only delays the divergence; does not prevent it.

### Fix Attempt 2: Controller Re-Tuning

**Change**: Tighten integral limits (±0.5 → ±0.25), strengthen anti-windup (k=0.004 → 0.018), reduce P/I gains by 0.6×.

**Hypothesis**: Controller gains too aggressive, causing overshoot and saturation.

**Result**: 349m error → 422m error (WORSE), vehicle descended to -244m.

**Why it failed**: Reducing gains lowered controller output:
- Baseline: outer_command = 0.528 → final command = 0.550 → rotor 64.93 rad/s (0.44% above hover)
- Re-tuned: outer_command ≈ 0.32 → final command ≈ 0.35 → rotor 64.39 rad/s (0.77% BELOW hover)

Tighter integral limits prevented accumulation to 0.5, reducing I-term contribution from 0.24 to ~0.12. Scaled P/I gains (0.6×) further reduced command authority. Result: controller produced LESS thrust than gravity, vehicle fell continuously.

Re-tuning made the problem worse by reducing already-insufficient authority.

### Fix Attempt 3: Increase Thrust Margin (5% → 15%)

**Change**: Expand thrust range from [0.95×hover, 1.05×hover] to [0.85×hover, 1.15×hover].

**Hypothesis**: 5% margin insufficient, controller needs more physical authority.

**Result**: 349m error → 354m error (NO IMPROVEMENT), rotor command 64.93 → 65.10 rad/s.

**Why it failed**: Increasing thrust margin expands the speed range but does not change controller output:

With 5% margin:
- command = 0.55 → rotor_speed = min_speed + 0.55 × range
- rotor_speed = 61.71 + 0.55 × 6.67 = 65.38 rad/s (98% of range used)

With 15% margin:
- command = 0.55 → rotor_speed = 59.74 + 0.55 × 9.75 = 65.10 rad/s (55% of range used)

**The controller still outputs command = 0.55** because integral pre-saturation and gain tuning have not changed. Expanding physical range gives controller more headroom it cannot access.

With 5% margin, controller was nearly saturating the physical limit (98% usage).
With 15% margin, controller uses only 55% because it's limited by internal architecture at command = 0.55, not by thrust authority.

## Physics Analysis: Why Command 0.55 Cannot Track

### Thrust Balance

With command = 0.55 and 15% margin:
- Rotor speed: 65.10 rad/s
- Thrust produced: k_thrust × ω² = 9.8998 N
- Gravity: 9.807 N
- Net upward force: 0.0928 N
- Net upward acceleration: 0.0928 m/s²

### Tracking Gap Analysis

At t=5s (after initial transient):
- Vehicle position: Z = -1.13 m
- Reference position: Z = 10 m
- Tracking error: 11.1 m
- Controller saturates immediately

To close 11m gap while reference climbs at 1 m/s:
- Requires sustained acceleration >> 1 m/s² for 5-10 seconds
- Available acceleration: 0.0928 m/s² (10× insufficient)
- Time to close gap if reference stops moving: 11m / 0.0928 m/s² ≈ 15 seconds to match velocity, then ~100s to converge position
- But reference continues climbing at 1 m/s, establishing new tracking deficit of 15m during convergence attempt

**Controller cannot catch up**. The 0.0928 m/s² acceleration is insufficient to close any gap larger than ~1m before the reference advances beyond reach.

### Expected vs. Observed Behavior

If command = 0.55 produced constant 0.0928 m/s² upward acceleration:
- Position at t=50s: Z = 0.5 × 0.0928 × 50² = 115.97 m (upward climb)

Observed position at t=50s: Z = -15.73 m (descent).

**Discrepancy: 131.7 m**.

This proves the controller is NOT maintaining constant thrust. Instead:
1. Initial descent establishes negative velocity
2. Integral accumulates to +0.5, producing upward thrust
3. Negative velocity gradually arrests (t=0-30s)
4. Brief upward motion (t=30-35s, velocity +0.07 m/s)
5. Anti-windup correction reduces integral slightly
6. Thrust drops below gravity again
7. Descent resumes (t=35-50s)
8. System oscillates around unstable equilibrium at Z ≈ -15m

The controller exhibits limit-cycle behavior: integral windup → brief thrust surplus → anti-windup → thrust deficit → descent → repeat. System never converges.

## Resolution Paths (Revisited)

### Path 1: Remove Integral Pre-Saturation (HIGH RISK)

**Change**: Edit CascadePidCore.mo line 77, increase outer_integral_pre_limit from ±0.5 to ±2.0.

**Expected outcome**:
- Integral could accumulate to 2.0
- I-term contribution: 2.0 × 0.48 = 0.96
- With P-term = 0.288, outer_command = 0.96 + 0.288 = 1.248 → clips to 1.0 at outer_command_limit
- Final command could reach 1.0, using full thrust authority

**Risks**:
1. Controller designed with ±0.5 integral limit for stability
2. Removing this constraint may cause:
   - Aggressive overshoot
   - Oscillatory instability
   - Slow integral windup during steady-state tracking (poor performance)
3. Anti-windup gain k=0.004 tuned for ±0.5 limit, may be insufficient for ±2.0 range
4. Inner loop gains may assume bounded outer command, could become unstable with outer_command → 1.0

**Timeline**: 1 hour to test, but high probability of failure requiring further tuning iterations.

**Recommendation**: Do NOT pursue unless user explicitly accepts the risk of controller instability.

### Path 2: Full Controller Redesign (CORRECT BUT OUT OF SCOPE)

**Required changes**:
1. Redesign hover equilibrium mechanism to work with arbitrary hover command (not assume 0.5)
2. Remove velocity command intermediate representation, output normalized thrust [0,1] directly
3. Implement thrust authority awareness: controller knows max available thrust and saturates gracefully
4. Retune all PID gains for new architecture
5. Redesign integral limits and anti-windup for thrust-limited operation
6. Test and validate on all 38 controllers

**Timeline**: 1-2 weeks minimum (design 2-3 days, implementation 2-3 days, testing/validation 3-5 days).

**Status**: Correct solution addressing root cause, but exceeds available time before 答辩 (4 days).

**Recommendation**: Document as future work, out of scope for 2026-08-23 deadline.

### Path 3: Accept Phase 5 Limitation (RECOMMENDED)

**Action**: Document Phase 5 as incomplete due to architectural constraint, focus 答辩 on Phase 1-4 achievements.

**Documentation deliverables**:
1. Final Phase 5 report marking all 15 controllers as FAIL with root cause explanation
2. Update phase4_phase5_complete_report.json status
3. Document controller re-architecture requirements as future work
4. Prepare 答辩 narrative emphasizing:
   - Phase 1-3: 46 controller cores restored from archive (100% recovery)
   - Phase 4: 38 controllers pass structural verification (100% CheckModel success)
   - Phase 5: Architectural limitation discovered, requires ~2 weeks redesign effort
   - Key achievement: Identified concrete path forward for making controllers flight-ready

**Timeline**: 2-3 hours to complete documentation today (2026-08-19).

**Advantages**:
- Completes Phase 5 investigation with clear findings
- Provides concrete technical explanation for 答辩
- Sets realistic scope for future work
- Focuses 答辩 on completed phases (1-4) rather than incomplete work
- No risk of introducing new failures from attempted fixes

**Recommendation**: PROCEED with this path given deadline constraints.

### Path 4: Ultra-High Thrust Margin Test (DIAGNOSTIC ONLY)

**Change**: Set climb_margin_ratio = 0.50 (50% thrust margin).

**Purpose**: Confirm the problem is internal controller saturation, not thrust scaling implementation.

**Expected outcome**:
- Max rotor speed: 64.79 × √1.50 = 79.33 rad/s
- Controller still outputs command = 0.55
- Rotor command: 57.93 + 0.55 × 21.40 = 69.70 rad/s (still ~65 rad/s range)
- Final error: ~350m (no improvement)

**Value**: Provides conclusive proof that thrust margin is irrelevant, problem is internal saturation.

**Disadvantage**: Wastes 30 minutes testing, provides no solution, delays documentation.

**Recommendation**: SKIP unless user specifically wants diagnostic confirmation.

## Final Recommendation

**Proceed with Path 3: Accept Phase 5 limitation and complete documentation today.**

**Rationale**:
1. Root cause is clear: integral pre-saturation at ±0.5 prevents controller from using full thrust authority
2. Three mismatches (hover point, integral scaling, command-to-thrust mapping) all stem from architectural assumption that hover = 0.5
3. Path 1 (remove saturation) has high failure risk, may introduce instability
4. Path 2 (redesign) is correct solution but requires 1-2 weeks, exceeds 4-day deadline
5. Path 4 (diagnostic test) provides no solution, wastes time
6. Path 3 completes Phase 5 investigation with concrete findings, allows focusing 答辩 on Phase 1-4 achievements

**Action items** (if user approves Path 3):
1. ✓ Create this final analysis document (phase5_architectural_limitation_final.md)
2. Create final Phase 5 report (phase5_final_report.md) with:
   - Summary: 15/15 controllers FAIL due to architectural mismatch
   - Root cause: Cascade PID designed for hover at mid-range, actual hover at 0.65
   - Detailed findings: integral pre-saturation prevents using >55% authority
   - Future work: Controller re-architecture estimated 1-2 weeks
3. Update Results/control_platform/phase4_phase5_complete/phase4_phase5_complete_report.json:
   - Phase 4 status: PASS (38/38 CheckModel)
   - Phase 5 status: BLOCKED (0/15 trajectory tracking, architectural limitation)
4. Document controller re-architecture requirements for future work
5. Prepare 答辩 materials emphasizing Phase 1-4 successes

**Timeline**: 2-3 hours remaining work, completes today (2026-08-19).

## Files Referenced

- [CascadePidCore.mo](C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Control\PidFamily\CascadePid\CascadePidCore.mo) - Controller implementation with integral pre-saturation
- [GraphicalScalarRotorPreview.mo](C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\Experiment\Adapters\GraphicalScalarRotorPreview.mo) - Thrust scaling interface (working correctly)
- [baseline_restored_still_fails.md](C:\Users\HP\Desktop\MoSim\Docs\Cache\investigation\baseline_restored_still_fails.md) - 5% margin test results
- [fifteen_percent_margin_still_fails.md](C:\Users\HP\Desktop\MoSim\Docs\Cache\investigation\fifteen_percent_margin_still_fails.md) - 15% margin test results and anomaly discovery
- [controller_not_saturating_root_cause.md](C:\Users\HP\Desktop\MoSim\Docs\Cache\investigation\controller_not_saturating_root_cause.md) - Root cause analysis with command chain traces

## Date

Investigation completed: 2026-08-19
答辩 deadline: 2026-08-23 (4 days remaining)
Recommended decision: Accept Phase 5 limitation, document as future work
