# tube_mpc Optimization Success Report

## Date: 2026-08-19 06:54

## Optimization Result
**SUCCESS**: Error reduced from 7.68m to 1.86m (75.8% improvement) - **PASS**

## Root Cause
Original diagnosis stated GraphicalAccelerationRotorPreview adapter was incomplete with collective_thrust connected to zero.y (constant 0). This was CORRECT:

**Original Configuration (TubeMpcGraphicalRunner.mo line 73)**:
```modelica
connect(zero.y, output_adapter.collective_thrust)
```
- Line 16: `Modelica.Blocks.Sources.Constant zero(k = 0)`
- collective_thrust = 0 → no hover thrust baseline → quadrotor cannot maintain altitude

## Fix Applied
Modified `Models/MoSimQuadrotorModel/Experiment/OptimizationPredictive/TubeMpcGraphicalRunner.mo`:

**Line 16**: Renamed zero constant to hover_thrust
```modelica
// BEFORE:
Modelica.Blocks.Sources.Constant zero(k = 0)
// AFTER:
Modelica.Blocks.Sources.Constant hover_thrust(k = 0.37)
```

**Line 73**: Updated connection to use hover_thrust
```modelica
// BEFORE:
connect(zero.y, output_adapter.collective_thrust)
// AFTER:
connect(hover_thrust.y, output_adapter.collective_thrust)
```

## Verification Through Sysplorer
1. **Reload**: File reloaded with `force_reload=true`
2. **CheckModel**: PASS (1.058s)
3. **Phase 5 Pipeline**: Error 1.86m < 5m threshold - **PASS**

## Analysis
Tube MPC uses:
- Model Predictive Control with tube-based robust constraint handling
- Acceleration command interface (acceleration_x/y/z outputs)
- Requires collective_thrust baseline for hover

The 7.68m → 1.86m improvement confirms:
- Original diagnosis was CORRECT: collective_thrust=0 was the root cause
- Without hover thrust baseline, MPC acceleration commands cannot maintain altitude
- With correct hover_thrust=0.37, controller achieves excellent 1.86m error

## Comparison with explicit_gain_scheduled_mpc
- **explicit_gain_scheduled_mpc**: Had hover_thrust.y=0.37 connected (line 22-23 in ExplicitGainScheduledMpcGraphicalRunner.mo) → worked with cache clearing only
- **tube_mpc**: Had zero.y=0 connected → required actual code fix to add hover thrust
- Both use GraphicalAccelerationRotorPreview adapter, but only tube_mpc had wrong thrust connection

## Key Lesson
The GraphicalAccelerationRotorPreview adapter requires BOTH acceleration commands AND collective_thrust baseline:
- Acceleration commands (x/y/z) provide differential control for attitude/position
- collective_thrust provides the baseline hover thrust (~0.37 for Sunray150 at m=1.0, g=9.80665)
- Without collective_thrust baseline, acceleration-only commands cannot maintain altitude

This is different from GraphicalAttitudeThrustRotorPreview which computes total thrust from attitude angles.

---
**Status**: ✅ Optimization complete and verified
**Controllers optimized so far**: 7/11 attempted
- trained_neural_residual: SUCCESS (6.93m → 3.34m)
- rl_gain_scheduler: FAIL (7.33m → 9.99m)
- official_pid: SUCCESS (8.90m → 2.65m)
- fopid: SUCCESS (14.12m → 1.52m)
- dfbc_smooth_robust_attitude: SUCCESS (5.30m → 4.20m)
- explicit_gain_scheduled_mpc: SUCCESS (7.45m → 2.91m)
- tube_mpc: SUCCESS (7.68m → 1.86m)
