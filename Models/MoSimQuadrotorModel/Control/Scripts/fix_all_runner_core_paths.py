#!/usr/bin/env python3
"""
Fix all Runner files to call correct Core paths
Replace 'Control.Implementations.XXX.MoSim_YYY_GRAPHICAL_MIL' with 'Control.Family.Controller.ControllerCore'
"""
import re
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
EXPERIMENT_ROOT = BASE_DIR / 'Models/MoSimQuadrotorModel/Experiment'

# Controller family mapping
FAMILY_MAP = {
    # PidFamily (5)
    'cascade_pid': ('PidFamily', 'CascadePid'),
    'gain_scheduled_pid': ('PidFamily', 'GainScheduledPid'),
    'fuzzy_pid': ('PidFamily', 'FuzzyPid'),
    'neural_pid': ('PidFamily', 'NeuralPid'),
    'official_pid': ('Px4Ctrl', None),  # Special case

    # ClassicRobust (13)
    'lqr_baseline': ('ClassicRobust', 'LqrBaseline'),
    'lqi_baseline': ('ClassicRobust', 'LqiBaseline'),
    'lqg': ('ClassicRobust', 'Lqg'),
    'h2_state_feedback': ('ClassicRobust', 'H2StateFeedback'),
    'hinf_hover_wrench': ('ClassicRobust', 'HinfHoverWrench'),
    'pole_placement_luenberger': ('ClassicRobust', 'PolePlacementLuenberger'),
    'backstepping_baseline': ('ClassicRobust', 'BacksteppingBaseline'),
    'adaptive_backstepping': ('ClassicRobust', 'AdaptiveBackstepping'),
    'feedback_linearization': ('ClassicRobust', 'FeedbackLinearization'),
    'mrac': ('ClassicRobust', 'Mrac'),
    'ndi': ('ClassicRobust', 'Ndi'),
    'passivity_based_control': ('ClassicRobust', 'PassivityBasedControl'),
    'fopid': ('ClassicRobust', 'Fopid'),

    # SlidingMode (6)
    'integral_smc': ('SlidingMode', 'IntegralSmc'),
    'terminal_smc': ('SlidingMode', 'TerminalSmc'),
    'nonsingular_terminal_smc': ('SlidingMode', 'NonsingularTerminalSmc'),
    'super_twisting_smc': ('SlidingMode', 'SuperTwistingSmc'),
    'adaptive_smc': ('SlidingMode', 'AdaptiveSmc'),
    'fuzzy_smc': ('SlidingMode', 'FuzzySmc'),

    # Optimization (7)
    'linear_mpc': ('Optimization', 'LinearMpc'),
    'robust_mpc': ('Optimization', 'RobustMpc'),
    'adaptive_mpc': ('Optimization', 'AdaptiveMpc'),
    'tube_mpc': ('Optimization', 'TubeMpc'),
    'explicit_gain_scheduled_mpc': ('Optimization', 'ExplicitGainScheduledMpc'),
    'ilqr': ('Optimization', 'Ilqr'),
    'mppi': ('Optimization', 'Mppi'),

    # GeometricFlatness (4)
    'dfbc_high_order_attitude': ('GeometricFlatness', 'DfbcHighOrderAttitude'),
    'dfbc_high_order_bodyrate': ('GeometricFlatness', 'DfbcHighOrderBodyrate'),
    'dfbc_smooth_robust_attitude': ('GeometricFlatness', 'DfbcSmoothRobustAttitude'),
    'dfbc_smooth_robust_bodyrate': ('GeometricFlatness', 'DfbcSmoothRobustBodyrate'),

    # Learning (2)
    'trained_neural_residual': ('Learning', 'TrainedNeuralResidual'),
    'rl_gain_scheduler': ('Learning', 'RlGainScheduler'),

    # IntegratedChains (1)
    'fixed_awff_pid': ('IntegratedChains', 'FixedAwffPid'),
}

def snake_to_pascal(name):
    return ''.join(word.capitalize() for word in name.split('_'))

print("Fix Runner Core Paths")
print(f"{'='*80}\n")

fixed = 0
skipped = 0

for controller, (family, subpkg) in FAMILY_MAP.items():
    pascal_name = snake_to_pascal(controller)

    # Find Runner file
    runner_candidates = list(EXPERIMENT_ROOT.rglob(f'{pascal_name}GraphicalRunner.mo'))

    if not runner_candidates:
        print(f"[SKIP] {controller:40s} Runner not found")
        skipped += 1
        continue

    runner_path = runner_candidates[0]
    content = runner_path.read_text(encoding='utf-8')

    # Build correct Core path
    if controller == 'official_pid':
        correct_core = 'MoSimQuadrotorModel.Control.Px4Ctrl.Px4CtrlBaselineCore'
    else:
        correct_core = f'MoSimQuadrotorModel.Control.{family}.{subpkg}.{pascal_name}Core'

    # Find current core declaration
    core_match = re.search(
        r'(MoSimQuadrotorModel\.Control\.\S+)\s+core',
        content
    )

    if not core_match:
        print(f"[WARN] {controller:40s} No core declaration found")
        continue

    current_core = core_match.group(1)

    # Check if already correct
    if current_core == correct_core:
        skipped += 1
        continue

    # Replace
    content = content.replace(current_core, correct_core)
    runner_path.write_text(content, encoding='utf-8')

    rel_path = str(runner_path.relative_to(EXPERIMENT_ROOT))
    print(f"[FIX]  {rel_path:60s}")
    print(f"       OLD: {current_core}")
    print(f"       NEW: {correct_core}")
    fixed += 1

print(f"\n{'='*80}")
print(f"Fixed {fixed} Runner files, skipped {skipped}")
print(f"{'='*80}")
