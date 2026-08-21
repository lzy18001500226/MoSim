#!/usr/bin/env python3
"""
Update formal_closed_loop_harness_map.json with correct Runner paths
Remove "fixed_" prefix from IntegratedChains scheme_ids
"""
import json
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
HARNESS_PATH = BASE_DIR / 'Config/control_platform/formal_closed_loop_harness_map.json'

# Load harness map
data = json.load(open(HARNESS_PATH, encoding='utf-8'))

# Build actual Runner file mapping (without fixed_ prefix)
runner_map = {
    # PidFamily
    'cascade_pid': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/PidFamily/CascadePidGraphicalRunner.mo',
    'gain_scheduled_pid': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/PidFamily/GainScheduledPidGraphicalRunner.mo',
    'fuzzy_pid': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/PidFamily/FuzzyPidGraphicalRunner.mo',
    'neural_pid': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/PidFamily/NeuralPidGraphicalRunner.mo',
    'official_pid': 'Models/MoSimQuadrotorModel/Experiment/Baselines/OfficialPidRunner.mo',

    # ClassicRobust
    'lqr_baseline': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/ClassicRobust/LqrBaselineGraphicalRunner.mo',
    'lqi_baseline': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/ClassicRobust/LqiBaselineGraphicalRunner.mo',
    'lqg': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/ClassicRobust/LqgGraphicalRunner.mo',
    'h2_state_feedback': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/ClassicRobust/H2StateFeedbackGraphicalRunner.mo',
    'hinf_hover_wrench': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/ClassicRobust/HinfHoverWrenchGraphicalRunner.mo',
    'pole_placement_luenberger': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/ClassicRobust/PolePlacementLuenbergerGraphicalRunner.mo',
    'backstepping_baseline': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/ClassicRobust/BacksteppingBaselineGraphicalRunner.mo',
    'adaptive_backstepping': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/ClassicRobust/AdaptiveBacksteppingGraphicalRunner.mo',
    'feedback_linearization': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/ClassicRobust/FeedbackLinearizationGraphicalRunner.mo',
    'mrac': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/ClassicRobust/MracGraphicalRunner.mo',
    'ndi': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/ClassicRobust/NdiGraphicalRunner.mo',
    'passivity_based_control': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/ClassicRobust/PassivityBasedControlGraphicalRunner.mo',
    'fopid': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/ClassicRobust/FopidGraphicalRunner.mo',

    # SlidingMode
    'integral_smc': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/SlidingMode/IntegralSmcGraphicalRunner.mo',
    'terminal_smc': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/SlidingMode/TerminalSmcGraphicalRunner.mo',
    'nonsingular_terminal_smc': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/SlidingMode/NonsingularTerminalSmcGraphicalRunner.mo',
    'super_twisting_smc': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/SlidingMode/SuperTwistingSmcGraphicalRunner.mo',
    'adaptive_smc': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/SlidingMode/AdaptiveSmcGraphicalRunner.mo',
    'fuzzy_smc': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/SlidingMode/FuzzySmcGraphicalRunner.mo',
    'smc_boundary_layer': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/SlidingMode/SmcBoundaryLayerGraphicalRunner.mo',

    # Optimization
    'linear_mpc': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/LinearMpc/LinearMpcGraphicalRunner.mo',
    'robust_mpc': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/Optimization/RobustMpcGraphicalRunner.mo',
    'adaptive_mpc': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/Optimization/AdaptiveMpcGraphicalRunner.mo',
    'tube_mpc': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/Optimization/TubeMpcGraphicalRunner.mo',
    'explicit_gain_scheduled_mpc': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/Optimization/ExplicitGainScheduledMpcGraphicalRunner.mo',
    'ilqr': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/Optimization/IlqrGraphicalRunner.mo',
    'mppi': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/Optimization/MppiGraphicalRunner.mo',
    'nmpc_outer': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/Optimization/NmpcOuterGraphicalRunner.mo',

    # GeometricFlatness
    'dfbc_high_order_attitude': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/GeometricFlatness/DfbcHighOrderAttitudeGraphicalRunner.mo',
    'dfbc_high_order_bodyrate': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/GeometricFlatness/DfbcHighOrderBodyrateGraphicalRunner.mo',
    'dfbc_smooth_robust_attitude': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/GeometricFlatness/DfbcSmoothRobustAttitudeGraphicalRunner.mo',
    'dfbc_smooth_robust_bodyrate': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/GeometricFlatness/DfbcSmoothRobustBodyrateGraphicalRunner.mo',
    'dfbc_basic': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/GeometricFlatness/DfbcBasicGraphicalRunner.mo',
    'se3_basic': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/GeometricFlatness/Se3BasicGraphicalRunner.mo',

    # Learning
    'trained_neural_residual': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/Learning/TrainedNeuralResidualGraphicalRunner.mo',
    'rl_gain_scheduler': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/Learning/RlGainSchedulerGraphicalRunner.mo',

    # IntegratedChains (cleaned scheme_ids without fixed_ prefix)
    'awff_pid': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/IntegratedChains/AwffPidGraphicalRunner.mo',
    'awff_l1_indi': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/IntegratedChains/AwffL1IndiGraphicalRunner.mo',
    'awff_l1_residual': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/IntegratedChains/AwffL1ResidualGraphicalRunner.mo',
    'linear_mpc_l1_indi': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/IntegratedChains/LinearMpcL1IndiGraphicalRunner.mo',
    'qp_nmpc_l1_indi_cbf': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/IntegratedChains/QpNmpcL1IndiCbfGraphicalRunner.mo',

    # AwffControllers
    'pid_awff_linear_eso': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/AwffControllers/PidAwffLinearEsoGraphicalRunner.mo',

    # Px4Ctrl
    'px4ctrl': 'Models/MoSimQuadrotorModel/Experiment/SingleUav/Px4Ctrl/Px4CtrlRunner.mo'
}

print("="*80)
print("更新 formal_closed_loop_harness_map.json")
print("="*80)

# Step 1: Rename scheme_ids (remove fixed_ prefix)
renamed_schemes = []
for scheme in data['schemes']:
    old_id = scheme['scheme_id']
    if old_id.startswith('fixed_'):
        new_id = old_id.replace('fixed_', '', 1)
        scheme['scheme_id'] = new_id
        renamed_schemes.append((old_id, new_id))
        print(f"[RENAME] {old_id} -> {new_id}")

print(f"\n重命名: {len(renamed_schemes)} 个 scheme_id")

# Step 2: Update Runner file paths
updated_count = 0
for scheme in data['schemes']:
    sid = scheme['scheme_id']

    if sid in runner_map:
        actual_runner = runner_map[sid]
        actual_class = actual_runner.replace('Models/', '').replace('.mo', '').replace('/', '.')

        # Update current_model_file
        scheme['current_model_file'] = actual_runner
        scheme['current_model_class'] = actual_class

        # Update canonical_closed_loop_harness if exists
        if scheme.get('canonical_closed_loop_harness'):
            scheme['canonical_closed_loop_harness']['public_entry_file'] = actual_runner
            scheme['canonical_closed_loop_harness']['public_entry_class'] = actual_class

        # Update topology_review_target
        if scheme.get('topology_review_target'):
            scheme['topology_review_target']['model_file'] = actual_runner
            scheme['topology_review_target']['model_class'] = actual_class
            scheme['topology_review_target']['declared_model_class'] = actual_class

        updated_count += 1
        print(f"[OK] {sid:40s} -> .../{Path(actual_runner).name}")

print(f"\n路径更新: {updated_count}/48 个控制器")

# Step 3: Update family_pools in measured_family_selection
if 'measured_family_selection' in data and 'family_pools' in data['measured_family_selection']:
    for pool in data['measured_family_selection']['family_pools']:
        updated_ids = []
        for old_id in pool['candidate_scheme_ids']:
            new_id = old_id.replace('fixed_', '', 1) if old_id.startswith('fixed_') else old_id
            updated_ids.append(new_id)
        pool['candidate_scheme_ids'] = updated_ids

print("\nfamily_pools 中的 scheme_id 已同步更新")

# Save updated harness map
with open(HARNESS_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n[OK] 已保存到: {HARNESS_PATH}")
print("="*80)
