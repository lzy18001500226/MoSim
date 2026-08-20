#!/usr/bin/env python3
"""Phase 2: Verify Mapper coverage for all 46 controllers (corrected version)"""
import json
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
CATALOG_PATH = BASE_DIR / 'Config/control_platform/control_scheme_catalog.json'
ADAPTERS_DIR = BASE_DIR / 'Models/MoSimQuadrotorModel/Control/Adapters'

data = json.load(open(CATALOG_PATH, encoding='utf-8'))
schemes = [s for s in data['schemes']
           if s['execution_kind'] == 'graphical_control_core'
           and s['implementation_status'] == 'implemented']

print("="*80)
print("PHASE 2: Mapper Coverage Verification (Corrected)")
print("="*80)
print(f"Total controllers: {len(schemes)}\n")

# Manual mapping based on actual Adapter filenames
ADAPTER_MAPPING = {
    # ROTOR_COMMAND boundary (5 controllers)
    'fixed_awff_pid': 'AwffPidRotorCommandAdapter.mo',
    'fixed_awff_l1_residual': 'AwffL1ResidualRotorCommandAdapter.mo',
    'fixed_awff_l1_indi': 'AwffL1IndiRotorCommandAdapter.mo',
    'fixed_linear_mpc_l1_indi': 'LinearMpcL1IndiRotorCommandAdapter.mo',
    'fixed_qp_nmpc_l1_indi_cbf': 'QpNmpcL1IndiCbfRotorCommandAdapter.mo',
    'official_pid': 'OfficialPIDGraphicalRotorAdapter.mo',

    # BODY_RATE_THRUST boundary (2 controllers)
    'dfbc_high_order_bodyrate': 'DfbcHighOrderBodyRateAdapter.mo',
    'dfbc_smooth_robust_bodyrate': 'DfbcSmoothRobustBodyRateAdapter.mo',

    # WRENCH boundary (1 controller)
    'hinf_hover_wrench': 'HinfHoverWrenchAdapter.mo',

    # Special cases with exact filenames
    'lqi_baseline': 'LqiAttitudeThrustAdapter.mo',
    'dfbc_high_order_attitude': 'DfbcHighOrderAttitudeThrustAdapter.mo',
    'dfbc_smooth_robust_attitude': 'DfbcSmoothRobustAttitudeThrustAdapter.mo',
}

def scheme_to_adapter_name(scheme_id):
    """Convert scheme_id to expected Adapter filename"""
    if scheme_id in ADAPTER_MAPPING:
        return ADAPTER_MAPPING[scheme_id]

    # Default pattern: PascalCase + AttitudeThrustAdapter.mo
    special = {
        'pid': 'Pid', 'lqr': 'Lqr', 'lqi': 'Lqi', 'lqg': 'Lqg',
        'h2': 'H2', 'hinf': 'Hinf', 'mrac': 'Mrac', 'ndi': 'Ndi',
        'smc': 'Smc', 'mpc': 'Mpc', 'ilqr': 'Ilqr', 'mppi': 'Mppi',
        'nmpc': 'Nmpc', 'se3': 'Se3', 'dfbc': 'Dfbc', 'rl': 'Rl',
        'fopid': 'Fopid', 'awff': 'Awff', 'cbf': 'Cbf', 'eso': 'Eso',
    }
    parts = scheme_id.split('_')
    pascal = ''.join([special.get(p, p.capitalize()) for p in parts])
    return f'{pascal}AttitudeThrustAdapter.mo'

missing = []
covered = []

for scheme in schemes:
    sid = scheme['scheme_id']
    expected = scheme_to_adapter_name(sid)

    if (ADAPTERS_DIR / expected).exists():
        covered.append((sid, expected))
        print(f"[OK]   {sid:45s} → {expected}")
    else:
        missing.append((sid, expected))
        print(f"[MISS] {sid:45s} expected: {expected}")

print(f"\n{'='*80}")
print(f"Phase 2 Summary: Covered {len(covered)}/46, Missing {len(missing)}/46")
if not missing:
    print("✓ All 46 controllers have Mapper coverage!")
else:
    print(f"\nMissing Adapters ({len(missing)}):")
    for sid, expected in missing:
        print(f"  - {sid:45s} → {expected}")
print(f"{'='*80}")
