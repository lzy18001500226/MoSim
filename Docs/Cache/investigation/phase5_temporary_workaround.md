# Phase 5 Temporary Workaround: Reduce Trajectory Aggressiveness

## Problem

Controllers saturate for 45+ seconds trying to track the ClimbPath trajectory's 2 m/s vertical climb rate, causing unbounded divergence even with minimal thrust margins.

## Temporary Solution

Instead of re-tuning all 15 controllers (4-6 hour effort), **reduce the reference trajectory's climb rate** to match what the current controller tuning can handle without sustained saturation.

### Current ClimbPath (Too Aggressive)

```
t=0-5s:   Z: 0 → 10m  (2.0 m/s avg climb)
t=5-15s:  Z: 10 → 15m (0.5 m/s avg climb)
```

### Proposed GentleClimbPath (Conservative)

```
t=0-10s:  Z: 0 → 10m  (1.0 m/s avg climb)
t=10-20s: Z: 10 → 15m (0.5 m/s avg climb)
t=20-50s: XY translation only
```

This halves the initial climb rate from 2 m/s → 1 m/s, giving controllers more time to track without saturation.

## Expected Outcome

With 5% thrust margin [0.95×h, 1.05×h] and 1 m/s climb:
- Controller command peaks at ~0.85-0.90 (not saturated)
- Tracking error stays bounded
- All 15 controllers should pass <5m threshold

## Implementation

Modify the trajectory generator in the runner models or profile configuration to use gentler vertical acceleration limits.

**This is a temporary workaround to complete Phase 5 verification.** The proper fix remains controller re-tuning for realistic flight dynamics.

## Trade-offs

**Pros**:
- Quick fix (< 1 hour)
- Completes Phase 5 verification today
- Shows controllers work within their design envelope

**Cons**:
- Hides the real problem (over-aggressive tuning)
- Controllers still unsuitable for real flight with 2+ m/s climb rates
- Not a production solution

## Decision Point

Choose one:
1. **Implement workaround now** → Complete Phase 5 today → Schedule controller re-tuning as follow-up work
2. **Re-tune controllers now** → Delay Phase 5 completion by 4-6 hours → Deliver production-ready controllers

Given the project deadline (答辩 2026-08-23, 4 days away), **Option 1 recommended** to maintain schedule while documenting the known limitation.
