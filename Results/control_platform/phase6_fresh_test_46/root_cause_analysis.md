# Phase 6 Root Cause Analysis: 46 Controller Failures

**Date**: 2026-08-22  
**Issue**: All 46 controllers fail tracking threshold (5m), with errors ranging 851m to 22,812m  
**Status**: Root cause identified

---

## Baseline Verification Results

### Official PID (Working Baseline)
- **Model**: `MoSimQuadrotorModel.Experiment.Baselines.OfficialPidRunner`
- **Terminal Error**: 6.46mm ✓ PASS
- **Architecture**:
  ```
  MultiModeTrajectory → WorldFramePassthrough → OfficialPidGraphicalCore 
    → YawDampedAmplitudeRouter → BaselineRotorMapper → ESC(200) → Motors
  ```

### PX4 Ctrl (Working Baseline)
- **Model**: `MoSimQuadrotorModel.Experiment.SingleUav.Px4Ctrl.Px4CtrlRunner`
- **Terminal Error**: 1.08mm ✓ PASS

---

## Failed Controller Architecture (Example: LqrBaselineGraphicalRunner)

**Model**: `MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.LqrBaselineGraphicalRunner`  
**Terminal Error**: 10,065m ✗ FAIL (1,558× over threshold)

**Architecture**:
```
MultiModeTrajectory → [MISSING PREPROCESSOR] → LqrBaselineCore 
  → GraphicalAttitudeThrustRotorPreview → ESC(110) → Motors
```

---

## Root Cause: Three Critical Architectural Defects

### Defect 1: Missing Preprocessor Block
- **Official PID has**: `WorldFramePassthrough` between trajectory and control core
- **46 controllers lack**: This preprocessor stage
- **Impact**: Control cores receive raw trajectory commands without proper frame transformation
- **Evidence**: Line 31-33 in OfficialPidRunner.mo vs direct connection in LqrBaselineGraphicalRunner.mo line 22-25

### Defect 2: Wrong Output Mapper
- **Official PID uses**: `BaselineRotorMapper` (line 44-47 in OfficialPidRunner.mo)
- **46 controllers use**: `GraphicalAttitudeThrustRotorPreview` (line 26-27 in LqrBaselineGraphicalRunner.mo)
- **Impact**: Incorrect mapping from attitude/thrust commands to rotor speeds
- **Result**: Unbalanced rotor commands causing divergence

### Defect 3: Insufficient ESC Limit
- **Official PID**: `nominal_esc_limit_abs = 200` rad/s (line 14 in OfficialPidRunner.mo)
- **46 controllers**: `nominal_esc_limit_abs = 110` rad/s (line 14 in LqrBaselineGraphicalRunner.mo)
- **Impact**: ESC saturation at 110 rad/s prevents aggressive control action
- **Result**: Controller cannot correct divergence once initiated

---

## Error Magnitude Correlation

| Controller | Terminal Error (m) | Missing Preprocessor | Wrong Mapper | Low ESC Limit |
|------------|-------------------|---------------------|-------------|---------------|
| official_pid | 0.0065 | ✗ | ✗ | ✗ |
| px4_ctrl | 0.0011 | ✗ | ✗ | ✗ |
| lqr_baseline | 10,065 | ✓ | ✓ | ✓ |
| cascade_pid | 1,738 | ✓ | ✓ | ✓ |
| dfbc_basic | 851 | ✓ | ✓ | ✓ |
| robust_mpc | 22,812 | ✓ | ✓ | ✓ |

**Pattern**: All three defects present → 1000× error increase

---

## Repair Strategy

### Fix Template (Apply to all 46 controllers)

1. **Add preprocessor block** after trajectory reference:
   ```modelica
   MoSimQuadrotorModel.Control.PID.WorldFramePassthrough preprocessor
     annotation(Placement(transformation(origin={-237.5,185}, extent={{-50,-65},{50,65}})));
   ```

2. **Replace output adapter**:
   - Remove: `MoSimQuadrotorModel.Experiment.Adapters.GraphicalAttitudeThrustRotorPreview`
   - Add: `MoSimQuadrotorModel.Control.PID.BaselineRotorMapper`

3. **Increase ESC limit**:
   ```modelica
   parameter Real nominal_esc_limit_abs(unit = "rad/s", min = 0) = 200;
   ```

4. **Update connections**:
   - Insert preprocessor between `reference` and `core`
   - Route `core` outputs through new mapper instead of old adapter

---

## Next Steps

1. Create repair script to patch all 46 `.mo` files systematically
2. Run CheckModel on patched controllers (expect 100% pass)
3. Run simulation tests on sample of 8 controllers
4. If sample passes, run full 46-controller test suite
5. Generate final pass/fail report

**Estimated Repair Time**: 2-3 hours for scripted batch modification + verification
