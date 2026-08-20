# Phase 5 Root Cause: Architectural Mismatch Between Controller Design and Interface

## Executive Summary

All 15 controllers fail Phase 5 with unbounded position divergence (500m-15km errors) because they were **designed for a different interface contract** than what GraphicalScalarRotorPreview provides.

**The controllers expect**: normalized command [0, 1] → thrust range [descent, aggressive_climb] where hover ≈ 0.5 (center of range)

**The interface provides**: normalized command [0, 1] → rotor speed [min_speed, max_speed] with no constraint on where hover falls

**Result**: Any scaling that gives sufficient climb authority causes runaway when the controller saturates.

## The Fundamental Conflict

### Controller Behavior (Observed)

From CascadePidCore.mo signal analysis:
- Hover initialization: command = 0.65 (not 0.5)
- During 2 m/s climb tracking: command = 1.0 (saturated)
- Saturation duration: t=5s to t=50s (45 seconds)
- Anti-windup active: integral clamped at 0.498 ≈ 0.5 limit ✓
- Controller behaving correctly given its design

### Scaling Options Tested

| Scaling Range | Hover Cmd | Sat. Thrust | Net Force | t=50 Error |
|--------------|-----------|-------------|-----------|------------|
| [0, 110] rad/s | 0.59 | 28.3 N | +18.5 N | 14,716 m |
| [0.5×h, 1.5×h] | 0.65 | 22.1 N | +12.3 N | 14,678 m |
| [0.8×h, 1.2×h] | 0.65 | 14.1 N | +4.3 N | 5,172 m |
| [0.95×h, 1.05×h] | 0.65 | 10.3 N | +0.49 N | 613 m |

**Pattern**: Every scaling gives hover at command ≈ 0.65, meaning saturation at 1.0 produces excess thrust. Even 5% margin accumulates to 600m+ error over 45s of saturation.

### Reference Trajectory (ClimbPath)

```
t=0-5s:   Z: 0 → 10m   (2 m/s climb, moderate)
t=5-15s:  Z: 10 → 15m  (1 m/s climb, gentle)
t=15-50s: Z: 15m       (hover, stationary)
X,Y: slow 1 m/s translation starting t=20s
```

**This is NOT an aggressive trajectory.** A properly tuned controller should track 2 m/s vertical with <20% saturation duty cycle.

## Why The Controller Saturates

From t=5s trajectory analysis with 5% margin:
- Reference: Z = 10m
- Actual: Z = 4.98m
- Error: -5.02m (below target)
- Controller response: command = 1.0 (maximum)

The controller goes to max thrust trying to close a 5m error, but max thrust (10.3 N) only produces 0.49 N net upward force. At this rate:
- Required time to close 5m gap: 5m / (0.49 N / 1 kg / 2) ≈ 20 seconds
- But the trajectory keeps moving: Z_ref advances from 10m → 15m during t=5-15s
- Controller never catches up, stays saturated

## Root Cause Analysis

The controllers were designed and tuned for an interface where:
1. **Hover is at mid-range** (command ≈ 0.5)
2. **Saturation provides >>2× hover thrust** (enough to track aggressive maneuvers)
3. **Saturation is TRANSIENT** (occurs only during brief peaks, not sustained)

GraphicalScalarRotorPreview cannot satisfy all three simultaneously:
- If hover is at 0.5 → saturation at 1.0 gives 2× hover thrust → runaway
- If hover is at 0.65 and saturation gives 1.05× hover → insufficient climb authority → prolonged saturation → still runaway

## The Real Problem: Controller Tuning

The controllers are **too aggressive for thrust-limited operation**:

From CascadePidCore.mo:
- Outer loop proportional gain: produces command swing from 0.65 → 1.0 for 5m error
- Integral limit: 0.5 (very permissive, allows sustained saturation)
- Anti-windup gain: 0.004 (weak correction, slow to back off)

For comparison, a well-tuned thrust-limited controller would:
- Reach 80% command (not 100%) for a 5m tracking error
- Have tighter integral limits (±0.2) to prevent sustained saturation
- Have stronger anti-windup (k ≈ 0.02) to recover faster

## Why Phase 4 Passed but Phase 5 Failed

**Phase 4 (CheckModel)**: Only checks model structure, no simulation
- All controllers instantiate correctly ✓
- No runtime behavior tested

**Phase 5 (Simulation)**: 50s trajectory tracking
- Exposes sustained saturation behavior
- Reveals thrust authority mismatch
- Controllers diverge unboundedly

## Correct Solution Paths

### Option A: Re-tune Controllers (Recommended)

Modify CascadePidCore.mo (and similar for other 14 controllers):
1. Reduce proportional gains by 30-50% to prevent immediate saturation
2. Tighten integral limits from ±0.5 to ±0.2
3. Increase anti-windup gain from 0.004 to 0.015-0.020
4. Add derivative filtering to reduce overshoot

**Pros**: Controllers become usable for real flight with thrust limits
**Cons**: Requires careful re-tuning, may reduce tracking performance

### Option B: Change Interface Contract

Modify GraphicalScalarRotorPreview to accept command range [-1, +1]:
- command = -1.0 → descent thrust (e.g. 0.5× hover)
- command = 0.0 → hover thrust
- command = +1.0 → max thrust (e.g. 2× hover)

**Pros**: Hover centered at zero, symmetric authority
**Cons**: Requires controller modifications (change saturation limits), breaks existing calibration

### Option C: Use Non-Linear Scaling

Map [0, 1] → [0, max] with non-linear function that puts hover at 0.5:
```
rotor_speed = sqrt(command) × max_speed
```

**Pros**: Maintains [0,1] interface, centers hover
**Cons**: Non-intuitive, complicates analysis, still doesn't fix over-aggressive tuning

## Recommendation

**Implement Option A** for CascadePid as proof-of-concept:
1. Scale all PID gains by 0.6
2. Change integral limits to ±0.25
3. Set anti-windup gain to 0.018
4. Test with 15% thrust margin [0.85×h, 1.15×h]

If this achieves <5m error, document the tuning methodology and apply to remaining 14 controllers.

## Impact on Project Timeline

- Phase 4 results: Valid (38/38 controllers pass CheckModel) ✓
- Phase 5 results: All current data INVALID (shows architectural mismatch, not controller quality)
- Required work: Re-tune one controller → verify → batch apply → re-run Phase 5 → generate valid report
- Estimated effort: 4-6 hours for full re-tuning campaign

## Files

- Investigation date: 2026-08-19
- Root cause: Controller tuning assumes hover at mid-range with >2× thrust authority
- Evidence: 5 scaling experiments all diverge due to prolonged saturation
- Blocking issue: Cannot complete Phase 5 verification without controller re-tuning
