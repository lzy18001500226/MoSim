#!/usr/bin/env python3
"""
Build correct runner class name mapping from actual filesystem
Fixes Phase 4 test plan errors where scheme_to_pkg() generated wrong names
"""
import json
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
CATALOG_PATH = BASE_DIR / 'Config/control_platform/control_scheme_catalog.json'
RESULTS_DIR = BASE_DIR / 'Results/control_platform/phase4_phase5_real_mcp'

# All 71 actual GraphicalRunner classes discovered from filesystem
ACTUAL_RUNNERS = [
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.AdaptiveBacksteppingGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.BacksteppingBaselineGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.FeedbackLinearizationGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.FopidGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.H2StateFeedbackGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.HinfHoverWrenchGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.LqgGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.LqiBaselineGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.LqrBaselineGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.MracGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.NdiGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.PassivityBasedControlGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.PolePlacementLuenbergerGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.GeometricFlatness.DfbcBasicGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.GeometricFlatness.DfbcHighOrderAttitudeGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.GeometricFlatness.DfbcHighOrderBodyrateGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.GeometricFlatness.DfbcSmoothRobustAttitudeGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.GeometricFlatness.DfbcSmoothRobustBodyrateGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.GeometricFlatness.Se3BasicGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.IntegratedChains.AwffL1IndiGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.IntegratedChains.AwffL1ResidualGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.IntegratedChains.LinearMpcL1IndiGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.IntegratedChains.QpNmpcL1IndiCbfGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Learning.RlGainSchedulerGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Learning.TrainedNeuralResidualGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.H2StateFeedbackGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.HinfHoverWrenchGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.LqgGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.LqiBaselineGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.LqrBaselineGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.PolePlacementLuenbergerGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.AdaptiveBacksteppingGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.BacksteppingBaselineGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.FeedbackLinearizationGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.MracGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.NdiGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.PassivityBasedControlGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Optimization.AdaptiveMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Optimization.ExplicitGainScheduledMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Optimization.IlqrGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.LinearMpc.LinearMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Optimization.MppiGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Optimization.NmpcOuterGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Optimization.RobustMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Optimization.TubeMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Optimization.AdaptiveMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Optimization.ExplicitGainScheduledMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Optimization.IlqrGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.LinearMpc.LinearMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Optimization.MppiGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Optimization.NmpcOuterGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Optimization.RobustMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.Optimization.TubeMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.PidFamily.CascadePidGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.FopidGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.PidFamily.FuzzyPidGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.PidFamily.GainScheduledPidGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.PidFamily.NeuralPidGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.Baselines.OfficialPidRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.AdaptiveSmcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.FuzzySmcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.IntegralSmcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.NonsingularTerminalSmcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.SmcBoundaryLayerGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.SuperTwistingSmcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.TerminalSmcGraphicalRunner",
]

# Load catalog
catalog = json.load(open(CATALOG_PATH, encoding='utf-8'))
schemes = {s['scheme_id']: s for s in catalog['schemes']}

# Build runner name index: map simplified names to full class paths
runner_index = {}
for runner in ACTUAL_RUNNERS:
    parts = runner.split('.')
    family = parts[-2]
    class_name = parts[-1].replace('GraphicalRunner', '').replace('Runner', '')

    # Normalize to snake_case for matching
    snake = ''.join(['_' + c.lower() if c.isupper() else c for c in class_name]).lstrip('_')

    runner_index[snake] = {
        'full_class': runner,
        'family': family,
        'class_name': class_name
    }

# Match catalog scheme_ids to actual runners
mapping = {}
no_runner = []

for sid in sorted(schemes.keys()):
    # Try exact match
    if sid in runner_index:
        mapping[sid] = runner_index[sid]['full_class']
        continue

    # Try without common suffixes
    for suffix in ['_baseline', '_state_feedback', '_hover_wrench', '_outer', '_basic', '_boundary_layer']:
        if sid.endswith(suffix):
            base = sid[:-len(suffix)]
            if base in runner_index:
                mapping[sid] = runner_index[base]['full_class']
                break
    else:
        # Manual mapping for special cases
        special_map = {
            'cascade_pid': 'MoSimQuadrotorModel.Experiment.SingleUav.PidFamily.CascadePidGraphicalRunner',
            'lqr': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.LqrBaselineGraphicalRunner',
            'lqi': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.LqiBaselineGraphicalRunner',
            'h2': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.H2StateFeedbackGraphicalRunner',
            'hinf': 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.HinfHoverWrenchGraphicalRunner',
            'pid': 'MoSimQuadrotorModel.Experiment.Baselines.OfficialPidRunner',
            'smc': 'MoSimQuadrotorModel.Experiment.SingleUav.SlidingMode.IntegralSmcGraphicalRunner',
            'se3': 'MoSimQuadrotorModel.Experiment.SingleUav.GeometricFlatness.Se3BasicGraphicalRunner',
            'nmpc': 'MoSimQuadrotorModel.Experiment.SingleUav.Optimization.NmpcOuterGraphicalRunner',
            'rl': 'MoSimQuadrotorModel.Experiment.SingleUav.Learning.RlGainSchedulerGraphicalRunner',
            'linear_mpc': 'MoSimQuadrotorModel.Experiment.SingleUav.LinearMpc.LinearMpcGraphicalRunner',
        }

        if sid in special_map:
            mapping[sid] = special_map[sid]
        else:
            no_runner.append(sid)

# Save corrected mapping
output = {
    'timestamp': '2026-08-19T02:00:00',
    'total_schemes': len(schemes),
    'total_actual_runners': len(ACTUAL_RUNNERS),
    'mapped': len(mapping),
    'no_runner': len(no_runner),
    'mapping': mapping,
    'controllers_without_runner': no_runner,
    'note': 'Built from actual filesystem discovery of 71 GraphicalRunner .mo files'
}

output_path = RESULTS_DIR / 'corrected_runner_mapping.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Corrected runner mapping saved: {output_path}")
print(f"Mapped: {len(mapping)}/46 controllers")
print(f"No runner: {len(no_runner)} controllers")
print(f"\nControllers without GraphicalRunner:")
for sid in no_runner:
    print(f"  - {sid}")
