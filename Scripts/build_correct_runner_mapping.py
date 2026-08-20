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
    "MoSimQuadrotorModel.Experiment.ClassicRobust.AdaptiveBacksteppingGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.ClassicRobust.BacksteppingBaselineGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.ClassicRobust.FeedbackLinearizationGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.ClassicRobust.FopidGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.ClassicRobust.H2StateFeedbackGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.ClassicRobust.HinfHoverWrenchGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.ClassicRobust.LqgGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.ClassicRobust.LqiBaselineGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.ClassicRobust.LqrBaselineGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.ClassicRobust.MracGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.ClassicRobust.NdiGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.ClassicRobust.PassivityBasedControlGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.ClassicRobust.PolePlacementLuenbergerGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.GeometricFlatness.DfbcBasicGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.GeometricFlatness.DfbcHighOrderAttitudeGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.GeometricFlatness.DfbcHighOrderBodyrateGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.GeometricFlatness.DfbcSmoothRobustAttitudeGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.GeometricFlatness.DfbcSmoothRobustBodyrateGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.GeometricFlatness.Se3BasicGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.IntegratedChains.AwffL1IndiGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.IntegratedChains.AwffL1ResidualGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.IntegratedChains.FixedAwffL1IndiGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.IntegratedChains.FixedAwffL1ResidualGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.IntegratedChains.FixedAwffPidGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.IntegratedChains.FixedLinearMpcL1IndiGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.IntegratedChains.FixedQpNmpcL1IndiCbfGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.IntegratedChains.LinearMpcL1IndiGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.IntegratedChains.QpNmpcL1IndiCbfGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.Learning.RlGainSchedulerGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.Learning.TrainedNeuralResidualGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.LinearRobustStateFeedback.H2StateFeedbackGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.LinearRobustStateFeedback.HinfHoverWrenchGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.LinearRobustStateFeedback.LqgGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.LinearRobustStateFeedback.LqiBaselineGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.LinearRobustStateFeedback.LqrBaselineGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.LinearRobustStateFeedback.PolePlacementLuenbergerGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.NonlinearAdaptive.AdaptiveBacksteppingGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.NonlinearAdaptive.BacksteppingBaselineGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.NonlinearAdaptive.FeedbackLinearizationGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.NonlinearAdaptive.MracGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.NonlinearAdaptive.NdiGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.NonlinearAdaptive.PassivityBasedControlGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.Optimization.AdaptiveMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.Optimization.ExplicitGainScheduledMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.Optimization.IlqrGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.Optimization.LinearMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.Optimization.MppiGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.Optimization.NmpcOuterGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.Optimization.RobustMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.Optimization.TubeMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.OptimizationPredictive.AdaptiveMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.OptimizationPredictive.ExplicitGainScheduledMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.OptimizationPredictive.IlqrGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.OptimizationPredictive.LinearMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.OptimizationPredictive.MppiGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.OptimizationPredictive.NmpcOuterGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.OptimizationPredictive.RobustMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.OptimizationPredictive.TubeMpcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.PidFamily.CascadePidGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.PidFamily.FopidGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.PidFamily.FuzzyPidGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.PidFamily.GainScheduledPidGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.PidFamily.NeuralPidGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.PidFamily.OfficialPidGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SlidingMode.AdaptiveSmcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SlidingMode.FuzzySmcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SlidingMode.IntegralSmcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SlidingMode.NonsingularTerminalSmcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SlidingMode.SmcBoundaryLayerGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SlidingMode.SuperTwistingSmcGraphicalRunner",
    "MoSimQuadrotorModel.Experiment.SlidingMode.TerminalSmcGraphicalRunner",
]

# Load catalog
catalog = json.load(open(CATALOG_PATH, encoding='utf-8'))
schemes = {s['scheme_id']: s for s in catalog['schemes']}

# Build runner name index: map simplified names to full class paths
runner_index = {}
for runner in ACTUAL_RUNNERS:
    parts = runner.split('.')
    family = parts[2]
    class_name = parts[3].replace('GraphicalRunner', '')

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
            'cascade_pid': 'MoSimQuadrotorModel.Experiment.PidFamily.CascadePidGraphicalRunner',
            'lqr': 'MoSimQuadrotorModel.Experiment.LinearRobustStateFeedback.LqrBaselineGraphicalRunner',
            'lqi': 'MoSimQuadrotorModel.Experiment.LinearRobustStateFeedback.LqiBaselineGraphicalRunner',
            'h2': 'MoSimQuadrotorModel.Experiment.LinearRobustStateFeedback.H2StateFeedbackGraphicalRunner',
            'hinf': 'MoSimQuadrotorModel.Experiment.LinearRobustStateFeedback.HinfHoverWrenchGraphicalRunner',
            'pid': 'MoSimQuadrotorModel.Experiment.PidFamily.OfficialPidGraphicalRunner',
            'smc': 'MoSimQuadrotorModel.Experiment.SlidingMode.IntegralSmcGraphicalRunner',
            'se3': 'MoSimQuadrotorModel.Experiment.GeometricFlatness.Se3BasicGraphicalRunner',
            'nmpc': 'MoSimQuadrotorModel.Experiment.Optimization.NmpcOuterGraphicalRunner',
            'rl': 'MoSimQuadrotorModel.Experiment.Learning.RlGainSchedulerGraphicalRunner',
            'linear_mpc': 'MoSimQuadrotorModel.Experiment.Optimization.LinearMpcGraphicalRunner',
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
