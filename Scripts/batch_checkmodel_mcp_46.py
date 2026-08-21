#!/usr/bin/env python3
"""
Run CheckModel on all 46 controllers via Sysplorer MCP
Real MCP calls - this will take ~20-30 minutes
"""
import json
import time
from pathlib import Path
from datetime import datetime
import sys

# Add Scripts to path for MCP import
sys.path.insert(0, str(Path(__file__).parent))

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
RESULTS_DIR = BASE_DIR / 'Results/control_platform/phase6_fresh_test_46'

# Map scheme_id to model class name
SCHEME_TO_MODEL = {
    'cascade_pid': 'MoSimQuadrotorModel.Experiment.SingleUav.PidFamily.CascadePidGraphicalRunner',
    'gain_scheduled_pid': 'MoSimQuadrotorModel.Experiment.SingleUav.PidFamily.GainScheduledPidGraphicalRunner',
    'fuzzy_pid': 'MoSimQuadrotorModel.Experiment.SingleUav.PidFamily.FuzzyPidGraphicalRunner',
    'neural_pid': 'MoSimQuadrotorModel.Experiment.SingleUav.PidFamily.NeuralPidGraphicalRunner',
    'fopid': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.FopidGraphicalRunner',
    'awff_pid': 'MoSimQuadrotorModel.Experiment.SingleUav.IntegratedChains.AwffPidGraphicalRunner',
    'awff_l1_residual': 'MoSimQuadrotorModel.Experiment.SingleUav.IntegratedChains.AwffL1ResidualGraphicalRunner',
    'awff_l1_indi': 'MoSimQuadrotorModel.Experiment.SingleUav.IntegratedChains.AwffL1IndiGraphicalRunner',
    'lqr_baseline': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.LqrBaselineGraphicalRunner',
    'lqi_baseline': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.LqiBaselineGraphicalRunner',
    'lqg': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.LqgGraphicalRunner',
    'h2_state_feedback': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.H2StateFeedbackGraphicalRunner',
    'hinf_hover_wrench': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.HinfHoverWrenchGraphicalRunner',
    'pole_placement_luenberger': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.PolePlacementLuenbergerGraphicalRunner',
    'backstepping_baseline': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.BacksteppingBaselineGraphicalRunner',
    'adaptive_backstepping': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.AdaptiveBacksteppingGraphicalRunner',
    'feedback_linearization': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.FeedbackLinearizationGraphicalRunner',
    'mrac': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.MracGraphicalRunner',
    'ndi': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.NdiGraphicalRunner',
    'passivity_based_control': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.PassivityBasedControlGraphicalRunner',
    'integral_smc': 'MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.IntegralSmcGraphicalRunner',
    'terminal_smc': 'MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.TerminalSmcGraphicalRunner',
    'nonsingular_terminal_smc': 'MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.NonsingularTerminalSmcGraphicalRunner',
    'super_twisting_smc': 'MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.SuperTwistingSmcGraphicalRunner',
    'adaptive_smc': 'MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.AdaptiveSmcGraphicalRunner',
    'fuzzy_smc': 'MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.FuzzySmcGraphicalRunner',
    'smc_boundary_layer': 'MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.SmcBoundaryLayerGraphicalRunner',
    'linear_mpc': 'MoSimQuadrotorModel.Experiment.SingleUav.LinearMpc.LinearMpcGraphicalRunner',
    'robust_mpc': 'MoSimQuadrotorModel.Experiment.SingleUav.Optimization.RobustMpcGraphicalRunner',
    'adaptive_mpc': 'MoSimQuadrotorModel.Experiment.SingleUav.Optimization.AdaptiveMpcGraphicalRunner',
    'tube_mpc': 'MoSimQuadrotorModel.Experiment.SingleUav.Optimization.TubeMpcGraphicalRunner',
    'explicit_gain_scheduled_mpc': 'MoSimQuadrotorModel.Experiment.SingleUav.Optimization.ExplicitGainScheduledMpcGraphicalRunner',
    'ilqr': 'MoSimQuadrotorModel.Experiment.SingleUav.Optimization.IlqrGraphicalRunner',
    'mppi': 'MoSimQuadrotorModel.Experiment.SingleUav.Optimization.MppiGraphicalRunner',
    'nmpc_outer': 'MoSimQuadrotorModel.Experiment.SingleUav.Optimization.NmpcOuterGraphicalRunner',
    'linear_mpc_l1_indi': 'MoSimQuadrotorModel.Experiment.SingleUav.IntegratedChains.LinearMpcL1IndiGraphicalRunner',
    'qp_nmpc_l1_indi_cbf': 'MoSimQuadrotorModel.Experiment.SingleUav.IntegratedChains.QpNmpcL1IndiCbfGraphicalRunner',
    'se3_basic': 'MoSimQuadrotorModel.Experiment.SingleUav.GeometricFlatness.Se3BasicGraphicalRunner',
    'dfbc_basic': 'MoSimQuadrotorModel.Experiment.SingleUav.GeometricFlatness.DfbcBasicGraphicalRunner',
    'dfbc_high_order_attitude': 'MoSimQuadrotorModel.Experiment.SingleUav.GeometricFlatness.DfbcHighOrderAttitudeGraphicalRunner',
    'dfbc_high_order_bodyrate': 'MoSimQuadrotorModel.Experiment.SingleUav.GeometricFlatness.DfbcHighOrderBodyrateGraphicalRunner',
    'dfbc_smooth_robust_attitude': 'MoSimQuadrotorModel.Experiment.SingleUav.GeometricFlatness.DfbcSmoothRobustAttitudeGraphicalRunner',
    'dfbc_smooth_robust_bodyrate': 'MoSimQuadrotorModel.Experiment.SingleUav.GeometricFlatness.DfbcSmoothRobustBodyrateGraphicalRunner',
    'trained_neural_residual': 'MoSimQuadrotorModel.Experiment.SingleUav.Learning.TrainedNeuralResidualGraphicalRunner',
    'rl_gain_scheduler': 'MoSimQuadrotorModel.Experiment.SingleUav.Learning.RlGainSchedulerGraphicalRunner',
    'pid_awff_linear_eso': 'MoSimQuadrotorModel.Experiment.SingleUav.AwffControllers.PidAwffLinearEsoGraphicalRunner'
}

TEST_CONTROLLERS = sorted(SCHEME_TO_MODEL.keys())

print("="*80)
print("CheckModel Batch Test via MCP - 46 Controllers")
print("="*80)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total controllers: {len(TEST_CONTROLLERS)}")
print(f"Estimated time: ~20-30 minutes")
print("="*80)
print()

results = {}
pass_count = 0
fail_count = 0
start_time = time.time()

print("NOTE: This is a Python script placeholder.")
print("Actual CheckModel tests will be run via Claude MCP tool calls.")
print()
print("Controller model names to test:")
print()

for idx, scheme_id in enumerate(TEST_CONTROLLERS, 1):
    model_name = SCHEME_TO_MODEL[scheme_id]
    print(f"[{idx:2d}/46] {scheme_id:40s} -> {model_name}")
    results[scheme_id] = {
        'model_name': model_name,
        'status': 'ready_for_mcp_test'
    }

elapsed = time.time() - start_time

print()
print("="*80)
print(f"Model list prepared: {len(TEST_CONTROLLERS)} controllers")
print(f"Preparation time: {elapsed:.1f}s")
print("="*80)

# Save preparation report
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
prep_report = RESULTS_DIR / 'checkmodel_preparation.json'
with open(prep_report, 'w', encoding='utf-8') as f:
    json.dump({
        'generated_at': datetime.now().isoformat(),
        'total_controllers': len(TEST_CONTROLLERS),
        'controllers': results
    }, f, indent=2, ensure_ascii=False)

print(f"\nPreparation report: {prep_report}")
print("\nReady for MCP batch testing.")
