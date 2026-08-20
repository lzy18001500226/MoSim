# Baseline Revert Failed: Controller Still Broken After Changes

## Executive Summary

After reverting all controller re-tuning changes back to baseline configuration, the simulation **STILL FAILS** with 422m final error and the vehicle falling to Z = -244m instead of climbing. The controller produces only 64.39 rad/s (1.24% thrust deficit), insufficient for hover.

**Critical Finding**: The file reverts were incomplete. Reading CascadePidCore.mo lines 77-98 reveals the changes are **STILL PRESENT**:
- Line 77: `outer_integral_pre_limit(upLimit=0.25,lowLimit=-0.25)` — should be ±0.5
- Line 93: `outer_aw_correction(k=0.018)` — should be 0.004
- Line 97: `outer_integral_final_limit(upLimit=0.25,lowLimit=-0.25)` — should be ±0.5

**Root Cause**: The Edit tool reverts in the previous session did NOT actually change the file content. The file still contains the broken re-tuned parameters.

## Simulation Results (Current Broken State)

```
Time    Position_Z    Reference_Z    Error       Rotor_Command    Status
----    ----------    -----------    -----       -------------    ------
t=0     0.0 m         0 m            0.0 m       63.38 rad/s      Below hover
t=5     -2.46 m       10 m           12.5 m      64.39 rad/s      Below hover ⚠
t=10    -9.49 m       10 m           19.5 m      64.39 rad/s      Below hover ⚠
t=15    -21.98 m      15 m           37.0 m      64.39 rad/s      Below hover ⚠
t=20    -40.55 m      15 m           55.6 m      64.39 rad/s      Below hover ⚠
t=30    -89.44 m      15 m           104 m       64.39 rad/s      Below hover ⚠
t=40    -156.15 m     15 m           171 m       64.39 rad/s      Below hover ⚠
t=50    -244.43 m     15 m           259 m       64.39 rad/s      Below hover ⚠
```

**Final Error: 422.11 m** (threshold: 5 m)
**Pass Status: FAIL** ❌

## Physics Analysis

**Observed rotor command**: 64.39 rad/s
**Required hover speed**: 64.79 rad/s
**Speed deficit**: 0.40 rad/s (0.62%)
**Thrust deficit**: 1.24%

With only 98.76% of required hover thrust:
- Net downward force: 0.1214 N
- Downward acceleration: 0.1214 m/s²
- Position after 50s: -0.5 × 0.1214 × 50² = -151.75 m

Observed -244m is worse, indicating the controller produces even less thrust during transients.

## Why Controller Cannot Reach Hover

With integral limits at ±0.25, the maximum steady-state command the controller can produce is:

```
command = proportional + integral + derivative
        ≈ 0.0 (at equilibrium) + 0.25 (max integral) + 0.0 (steady)
        = 0.25
```

But hover requires command ≈ 0.65, which means the controller needs integral ≈ 0.5 to reach equilibrium.

**With ±0.25 limits**: Controller saturates integral at 0.25, producing command ≈ 0.38
**Required for hover**: Integral must reach ≈ 0.5, command = 0.65

The integral limit of ±0.25 **physically prevents** the controller from accumulating enough action to reach hover thrust.

## File Verification

Reading CascadePidCore.mo confirms the file still contains broken parameters:

```modelica
// Line 77 (outer loop integral pre-limit)
SysplorerEmbeddedCoder.Discontinuities.Saturation outer_integral_pre_limit(upLimit=0.25,lowLimit=-0.25)

// Line 93 (outer loop anti-windup gain)
SysplorerEmbeddedCoder.MathOperation.Gain outer_aw_correction(k=0.018)

// Line 97 (outer loop integral final limit)
SysplorerEmbeddedCoder.Discontinuities.Saturation outer_integral_final_limit(upLimit=0.25,lowLimit=-0.25)
```

**All three parameters are WRONG** — they should be:
- outer_integral_pre_limit: upLimit=0.5, lowLimit=-0.5
- outer_aw_correction: k=0.004
- outer_integral_final_limit: upLimit=0.5, lowLimit=-0.5

## What Went Wrong in Previous Session

The previous session attempted to revert these changes using the Edit tool:

```
Edit: outer_aw_correction(k=0.018) → outer_aw_correction(k=0.004)
Edit: outer_integral_final_limit(upLimit=0.25,lowLimit=-0.25) → outer_integral_final_limit(upLimit=0.5,lowLimit=-0.5)
```

But the Edit tool returned "old_string and new_string are exactly the same" errors, indicating the replacements didn't match the actual file content.

**Likely cause**: The Edit tool was given incorrect old_string values that didn't match the exact whitespace/formatting in the file, so the replacements silently failed.

## Required Fix

Must perform **correct file edits** to restore the three parameters:

1. Line 77: `outer_integral_pre_limit(upLimit=0.25,lowLimit=-0.25)` → `upLimit=0.5,lowLimit=-0.5`
2. Line 93: `outer_aw_correction(k=0.018)` → `k=0.004`
3. Line 97: `outer_integral_final_limit(upLimit=0.25,lowLimit=-0.25)` → `upLimit=0.5,lowLimit=-0.5`

Then reload the model and re-run simulation to verify hover equilibrium is restored.

## Impact on Project Timeline

- **Deadline**: 答辩 2026-08-23 (3 days from now, was 4 days in previous session)
- **Status**: Phase 5 verification blocked by broken controller
- **Time lost**: ~2 hours debugging failed revert attempt
- **Remaining work**: Fix parameters (15 min) + re-run simulation (30 min) + batch test 15 controllers (2 hrs) + report (1 hr) = 4 hours
- **Risk**: Still achievable if fix completes today (2026-08-19)

## Next Steps

1. **Read full outer loop section** of CascadePidCore.mo to get exact formatting for Edit tool
2. **Perform three precise edits** with exact whitespace matching
3. **Force reload** CascadePidCore.mo in Sysplorer to pick up changes
4. **Re-run simulation** and verify position_error_norm <5m with hover equilibrium restored
5. If PASS, proceed to batch test all 15 controllers with gentler trajectory
6. If FAIL, escalate to user for guidance (may need manual file editing)

## Files

- Investigation date: 2026-08-19 02:42
- Model: CascadePidGraphicalRunner with broken controller parameters
- Result: 422m error, vehicle falls to -244m
- Root cause: Incomplete file revert, ±0.25 integral limits still present
- Blocking: Phase 5 verification cannot proceed until baseline configuration restored
