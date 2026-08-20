#!/usr/bin/env python3
"""
Phase 4 + 5: REAL Sysplorer verification (not simulation)
- Phase 4: CheckModel on 38 controllers
- Phase 5: 50s ClimbPath simulation on passing controllers
"""
from pathlib import Path
import json
import sys
sys.path.insert(0, r'D:\Program Files\MWORKS\Sysplorer 2026a\Bin')
import mworks.sysplorer as ModelingPy

BASE = Path('C:/Users/HP/Desktop/MoSim')
RESULTS_DIR = BASE / 'Results/control_platform/phase4_phase5_real'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# 38 ATTITUDE_THRUST controllers
CONTROLLERS = {
    'PidFamily': ['CascadePid', 'GainScheduledPid', 'FuzzyPid', 'NeuralPid', 'OfficialPid'],
    'ClassicRobust': [
        'LqrBaseline', 'LqiBaseline', 'Lqg', 'H2StateFeedback', 'HinfHoverWrench',
        'PolePlacementLuenberger', 'BacksteppingBaseline', 'AdaptiveBackstepping',
        'FeedbackLinearization', 'Mrac', 'Ndi', 'PassivityBasedControl', 'Fopid'
    ],
    'SlidingMode': [
        'IntegralSmc', 'TerminalSmc', 'NonsingularTerminalSmc', 'SuperTwistingSmc',
        'AdaptiveSmc', 'FuzzySmc', 'SmcBoundaryLayer'
    ],
    'Optimization': [
        'LinearMpc', 'RobustMpc', 'AdaptiveMpc', 'TubeMpc',
        'ExplicitGainScheduledMpc', 'Ilqr', 'Mppi', 'NmpcOuter'
    ],
    'GeometricFlatness': [
        'DfbcHighOrderAttitude', 'DfbcHighOrderBodyrate',
        'DfbcSmoothRobustAttitude', 'DfbcSmoothRobustBodyrate',
        'DfbcBasic', 'Se3Basic'
    ],
    'Learning': ['TrainedNeuralResidual'],
    'IntegratedChains': ['FixedAwffPid']
}

print("="*80)
print("Phase 4+5 REAL Verification Pipeline")
print("="*80)

# ============================================================================
# Step 1: Load all necessary packages and Core files
# ============================================================================
print("\n[Step 1] Loading MoSimQuadrotorModel packages and Core files...")

load_sequence = [
    BASE / 'Models/MoSimQuadrotorModel/package.mo',
    BASE / 'Models/MoSimQuadrotorModel/BaseModules/package.mo',
    BASE / 'Models/MoSimQuadrotorModel/Blocks/package.mo',
    BASE / 'Models/MoSimQuadrotorModel/Sources/package.mo',
    BASE / 'Models/MoSimQuadrotorModel/Vehicle/package.mo',
    BASE / 'Models/MoSimQuadrotorModel/Guidance/package.mo',
    BASE / 'Models/MoSimQuadrotorModel/Trajectories/package.mo',
    BASE / 'Models/MoSimQuadrotorModel/Telemetry/package.mo',
    BASE / 'Models/MoSimQuadrotorModel/Control/package.mo',
    BASE / 'Models/MoSimQuadrotorModel/Experiment/package.mo',
]

# Add all family packages
for family in CONTROLLERS.keys():
    load_sequence.append(BASE / f'Models/MoSimQuadrotorModel/Control/{family}/package.mo')
    load_sequence.append(BASE / f'Models/MoSimQuadrotorModel/Experiment/{family}/package.mo')

# Add all controller sub-packages and Core files
for family, controllers in CONTROLLERS.items():
    for ctrl in controllers:
        ctrl_pkg = BASE / f'Models/MoSimQuadrotorModel/Control/{family}/{ctrl}/package.mo'
        core_file = BASE / f'Models/MoSimQuadrotorModel/Control/{family}/{ctrl}/{ctrl}Core.mo'
        if ctrl_pkg.exists():
            load_sequence.append(ctrl_pkg)
        if core_file.exists():
            load_sequence.append(core_file)

loaded = 0
failed_loads = []

for pkg_path in load_sequence:
    if not pkg_path.exists():
        print(f"[SKIP] {pkg_path.name} (not found)")
        continue

    try:
        result = ModelingPy.OpenModelFile(str(pkg_path))
        if result:
            loaded += 1
        else:
            errors = ModelingPy.GetLastErrors()
            failed_loads.append((pkg_path.name, errors))
    except Exception as e:
        failed_loads.append((pkg_path.name, str(e)))

print(f"Loaded {loaded}/{len(load_sequence)} files")
if failed_loads:
    print(f"Failed loads: {len(failed_loads)}")
    for name, err in failed_loads[:5]:
        print(f"  {name}: {err}")

# ============================================================================
# Step 2: Phase 4 - CheckModel on all 38 controllers
# ============================================================================
print(f"\n{'='*80}")
print("[Phase 4] CheckModel Verification")
print(f"{'='*80}\n")

phase4_results = []

for family, controllers in CONTROLLERS.items():
    for ctrl in controllers:
        runner_class = f'MoSimQuadrotorModel.Experiment.{family}.{ctrl}GraphicalRunner'

        print(f"Checking {ctrl}...", end=' ')

        try:
            # Check if Runner exists
            if not ModelingPy.ClassExist(runner_class):
                result = {
                    'controller': ctrl,
                    'family': family,
                    'runner_class': runner_class,
                    'phase4_pass': False,
                    'phase4_error': 'Runner class not found'
                }
                print("SKIP (Runner not found)")
            else:
                # Run CheckModel
                check_result = ModelingPy.CheckModel(runner_class)

                if check_result:
                    result = {
                        'controller': ctrl,
                        'family': family,
                        'runner_class': runner_class,
                        'phase4_pass': True,
                        'phase4_error': None
                    }
                    print("PASS")
                else:
                    errors = ModelingPy.GetLastErrors()
                    result = {
                        'controller': ctrl,
                        'family': family,
                        'runner_class': runner_class,
                        'phase4_pass': False,
                        'phase4_error': errors
                    }
                    print(f"FAIL: {errors[:100]}")

        except Exception as e:
            result = {
                'controller': ctrl,
                'family': family,
                'runner_class': runner_class,
                'phase4_pass': False,
                'phase4_error': str(e)
            }
            print(f"ERROR: {e}")

        phase4_results.append(result)

# Save Phase 4 results
phase4_pass = [r for r in phase4_results if r['phase4_pass']]
phase4_fail = [r for r in phase4_results if not r['phase4_pass']]

phase4_report = {
    'total': len(phase4_results),
    'pass': len(phase4_pass),
    'fail': len(phase4_fail),
    'pass_rate': len(phase4_pass) / len(phase4_results),
    'results': phase4_results
}

phase4_json = RESULTS_DIR / 'phase4_checkmodel_results.json'
with open(phase4_json, 'w', encoding='utf-8') as f:
    json.dump(phase4_report, f, indent=2, ensure_ascii=False)

print(f"\n{'='*80}")
print(f"Phase 4 Summary: {len(phase4_pass)}/{len(phase4_results)} PASS ({phase4_report['pass_rate']:.1%})")
print(f"{'='*80}")

# ============================================================================
# Step 3: Phase 5 - 50s ClimbPath simulation on passing controllers
# ============================================================================
print(f"\n{'='*80}")
print("[Phase 5] 50s ClimbPath Simulation")
print(f"{'='*80}\n")

phase5_results = []

for result in phase4_pass:
    ctrl = result['controller']
    family = result['family']
    runner_class = result['runner_class']

    print(f"Simulating {ctrl}...", end=' ')

    try:
        # Run 50s simulation
        sim_result = ModelingPy.SimulateModel(
            runner_class,
            stopTime=50.0,
            numberOfIntervals=5000,
            method='dassl',
            tolerance=1e-6
        )

        if sim_result:
            # Get final position error
            try:
                x_traj = ModelingPy.GetVarValues('traj_ref.x')
                y_traj = ModelingPy.GetVarValues('traj_ref.y')
                z_traj = ModelingPy.GetVarValues('traj_ref.z')

                x_actual = ModelingPy.GetVarValues('vehicle.x')
                y_actual = ModelingPy.GetVarValues('vehicle.y')
                z_actual = ModelingPy.GetVarValues('vehicle.z')

                # Final error at t=50s
                final_error = (
                    (x_traj[-1] - x_actual[-1])**2 +
                    (y_traj[-1] - y_actual[-1])**2 +
                    (z_traj[-1] - z_actual[-1])**2
                )**0.5

                phase5_pass = final_error < 5.0

                sim_record = {
                    'controller': ctrl,
                    'family': family,
                    'runner_class': runner_class,
                    'phase5_pass': phase5_pass,
                    'final_error_m': final_error,
                    'phase5_error': None if phase5_pass else f'Final error {final_error:.2f}m > 5m'
                }

                status = "PASS" if phase5_pass else f"FAIL (error={final_error:.2f}m)"
                print(status)

            except Exception as e:
                sim_record = {
                    'controller': ctrl,
                    'family': family,
                    'runner_class': runner_class,
                    'phase5_pass': False,
                    'final_error_m': None,
                    'phase5_error': f'Failed to extract trajectory: {e}'
                }
                print(f"FAIL (extraction error)")

        else:
            errors = ModelingPy.GetLastErrors()
            sim_record = {
                'controller': ctrl,
                'family': family,
                'runner_class': runner_class,
                'phase5_pass': False,
                'final_error_m': None,
                'phase5_error': errors
            }
            print(f"FAIL: {errors[:100]}")

    except Exception as e:
        sim_record = {
            'controller': ctrl,
            'family': family,
            'runner_class': runner_class,
            'phase5_pass': False,
            'final_error_m': None,
            'phase5_error': str(e)
        }
        print(f"ERROR: {e}")

    phase5_results.append(sim_record)

# Save Phase 5 results
phase5_pass = [r for r in phase5_results if r['phase5_pass']]
phase5_fail = [r for r in phase5_results if not r['phase5_pass']]

phase5_report = {
    'total': len(phase5_results),
    'pass': len(phase5_pass),
    'fail': len(phase5_fail),
    'pass_rate': len(phase5_pass) / len(phase5_results) if phase5_results else 0,
    'results': phase5_results
}

phase5_json = RESULTS_DIR / 'phase5_simulation_results.json'
with open(phase5_json, 'w', encoding='utf-8') as f:
    json.dump(phase5_report, f, indent=2, ensure_ascii=False)

print(f"\n{'='*80}")
print(f"Phase 5 Summary: {len(phase5_pass)}/{len(phase5_results)} PASS ({phase5_report['pass_rate']:.1%})")
print(f"{'='*80}")

# ============================================================================
# Final Report
# ============================================================================
print(f"\n{'='*80}")
print("FINAL REPORT")
print(f"{'='*80}")
print(f"Phase 4 (CheckModel): {len(phase4_pass)}/{len(phase4_results)} PASS")
print(f"Phase 5 (50s ClimbPath): {len(phase5_pass)}/{len(phase5_results)} PASS")
print(f"\nOverall success rate: {len(phase5_pass)}/{len(phase4_results)} ({len(phase5_pass)/len(phase4_results):.1%})")
print(f"{'='*80}")

final_report = {
    'phase4': phase4_report,
    'phase5': phase5_report,
    'overall': {
        'total_controllers': len(phase4_results),
        'phase4_pass': len(phase4_pass),
        'phase5_pass': len(phase5_pass),
        'overall_success_rate': len(phase5_pass) / len(phase4_results)
    }
}

final_json = RESULTS_DIR / 'phase4_phase5_final_report.json'
with open(final_json, 'w', encoding='utf-8') as f:
    json.dump(final_report, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: {RESULTS_DIR}")
