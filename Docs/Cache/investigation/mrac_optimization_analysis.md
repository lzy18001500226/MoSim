# mrac Optimization Analysis

## Date: 2026-08-19 07:15

## Controller Architecture Analysis

**MracGraphicalRunner.mo**: Uses GraphicalAttitudeThrustRotorPreview adapter (CORRECT)
**MracCore.mo**: 917-line Sysblock implementation with comprehensive MRAC design

### MRAC Control Structure

**Reference Model** (Lines 43-217):
- Second-order reference model for x/y/z position tracking
- Reference model parameters:
  - X/Y: k_position=4.84, k_damping=-3.74 (ω_n ≈ 2.2 rad/s, ζ ≈ 0.85)
  - Z: k_position=6.25, k_damping=-4.5 (ω_n ≈ 2.5 rad/s, ζ ≈ 0.90)
- Discrete-time integration with dt input

**Adaptive Law** (Lines 48-98, 122-172, 196-246):
- Sliding surface design: s = λ·e_pos + e_vel
  - X/Y: λ=3.0 (sliding surface slope)
  - Z: λ=2.25 (different dynamics for vertical channel)
- Adaptation gains:
  - X/Y position: **k=0.08** (lines 83, 157)
  - X/Y velocity: **k=0.08** (lines 93, 167)
  - Z position: **k=0.1** (line 231)
  - Z velocity: **k=0.1** (line 241)
- **Saturation limits**: ±1.5 on adaptive deltas (lines 87, 97, 161, 171, 235, 245)
- **NO projection bounds on UnitDelay states** (initCond=0.0 only)
- **NO dead zone** in adaptation law
- **NO sigma-modification** for robustness

**Controller Gains** (Lines 99-114):
- Base gains:
  - X: k_pos=6.0, k_vel=4.5
  - Y: k_pos=6.0, k_vel=4.5
  - Z: k_pos=4.5, k_vel=4.0
- Effective gains = base_gain + adaptive_delta
- Adaptive deltas saturated but base gains are constants (no overall gain limits)

### Identified Issues Leading to Divergence

1. **High Adaptation Rate (0.08-0.1)** with NO Robustness Mechanisms:
   - Adaptation gains 0.08-0.1 with dt=0.004s → 0.00032-0.0004 per step
   - Over 50s simulation: potential drift of ±8 (0.0004*20000 steps)
   - Saturation at ±1.5 limits adaptive deltas but doesn't prevent slow integration windup
   - NO sigma-modification (leakage term) to bound parameter drift
   - NO dead zone to prevent adaptation on small errors (sensor noise, disturbances)

2. **Asymmetric Reference Model Parameters**:
   - X/Y channels: ω_n=2.2, ζ=0.85 (slower, critically damped)
   - Z channel: ω_n=2.5, ζ=0.90 (faster, more damped)
   - Different sliding surface slopes (3.0 vs 2.25)
   - May cause adaptive law to fight control allocation in coupled system

3. **No Parameter Projection Bounds**:
   - Adaptive deltas saturated at ±1.5
   - But effective gains = 6.0 + adaptive_delta can range [4.5, 7.5] for position
   - If base gains are NOT optimal for Sunray150 dynamics, adaptive law may saturate trying to compensate
   - NO explicit bounds on effective gain total (only on delta)

4. **Discrete Euler Integration Without Anti-Windup**:
   - UnitDelay blocks with simple Euler: x[k+1] = x[k] + dx·dt
   - If adaptation law saturates for extended periods, integral action still accumulates in UnitDelay states
   - NO anti-windup mechanism on adaptive delta integrators

## Root Cause Hypothesis

MRAC controller designed for continuous-time ideal plant with perfect feedback. When applied to:
- Discrete-time simulation (dt=0.004s, 50s duration = 12500 steps)
- Platform acceleration limits (±3 m/s² vs controller designed for higher)
- Sensor noise, model mismatch, control allocation nonlinearities

The adaptive law without robustness mechanisms (sigma-modification, dead zone, projection) DIVERGES:
- Small persistent tracking errors → continuous adaptation
- No leakage term → adaptive deltas drift toward saturation
- Saturation at ±1.5 maintained for extended time
- Effective gains hit sub-optimal regions → tracking degrades → error 14.99m

## Proposed Fix Strategy

**Option 1: Reduce Adaptation Gains** (Conservative, High Success Probability)
- Reduce X/Y gains from 0.08 → **0.03** (62% reduction)
- Reduce Z gains from 0.1 → **0.04** (60% reduction)
- Slower adaptation → less susceptible to noise/disturbances
- May reduce steady-state tracking accuracy but prevent divergence

**Option 2: Add Sigma-Modification** (Theoretically Correct, Moderate Complexity)
- Add leakage term: delta_new = delta_old·(1 - sigma·dt) + adaptation_increment
- Sigma=0.01-0.05 typical
- Requires modifying UnitDelay feedback connections (complex in graphical Sysblock)

**Option 3: Add Dead Zone** (Simple, May Help)
- Only adapt when |sliding_surface| > threshold (e.g., 0.1)
- Prevents adaptation on small errors
- Requires adding conditional logic before adaptation drive

**RECOMMENDATION**: Try Option 1 first (reduce adaptation gains to 0.03/0.04). Simple parameter change, high probability of stabilizing the adaptive law without divergence. If successful error < 5m, document and move on. If still fails, Option 1 combined with Option 3 (dead zone threshold=0.05).

---
**Status**: Analysis complete - ready to attempt fix
**Next Step**: Modify MracCore.mo lines 83, 93, 157, 167, 231, 241 to reduce adaptation gains
