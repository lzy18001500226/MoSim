#!/usr/bin/env python3
"""
Phase 2: Verify Mapper coverage for all 46 controllers
Checks that each scheme_id has a corresponding Adapter in Control/Adapters/
"""
import json
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
CATALOG_PATH = BASE_DIR / 'Config/control_platform/control_scheme_catalog.json'
ADAPTERS_DIR = BASE_DIR / 'Models/MoSimQuadrotorModel/Control/Adapters'

# Load catalog
data = json.load(open(CATALOG_PATH, encoding='utf-8'))
schemes = [s for s in data['schemes']
           if s['execution_kind'] == 'graphical_control_core'
           and s['implementation_status'] == 'implemented']

print("="*80)
print("PHASE 2: Mapper Coverage Verification")
print("="*80)
print(f"Total controllers: {len(schemes)}\n")

# Map scheme_id to expected Adapter naming patterns
def scheme_to_adapter_candidates(scheme_id, boundary):
    """Generate possible Adapter file names for a scheme_id"""
    # Convert scheme_id to PascalCase
    special = {
        'pid': 'Pid', 'lqr': 'Lqr', 'lqi': 'Lqi', 'lqg': 'Lqg',
        'h2': 'H2', 'hinf': 'Hinf', 'mrac': 'Mrac', 'ndi': 'Ndi',
        'smc': 'Smc', 'mpc': 'Mpc', 'ilqr': 'Ilqr', 'mppi': 'Mppi',
        'nmpc': 'Nmpc', 'se3': 'Se3', 'dfbc': 'Dfbc', 'rl': 'Rl',
        'fopid': 'Fopid', 'awff': 'Awff', 'cbf': 'Cbf', 'eso': 'Eso',
        'l1': 'L1', 'indi': 'Indi', 'qp': 'Qp',
    }
    parts = scheme_id.split('_')
    pascal = ''.join([special.get(p, p.capitalize()) for p in parts])

    # Generate boundary-specific suffix
    boundary_suffix_map = {
        'ATTITUDE_THRUST': 'AttitudeThrustAdapter.mo',
        'BODY_RATE_THRUST': 'BodyRateAdapter.mo',
        'ROTOR_COMMAND': 'RotorCommandAdapter.mo',
        'WRENCH': 'Adapter.mo',  # HinfHoverWrench just uses "Adapter.mo"
    }
    suffix = boundary_suffix_map.get(boundary, 'Adapter.mo')

    # Special cases
    if scheme_id == 'official_pid':
        return ['OfficialPIDGraphicalRotorAdapter.mo']
    if scheme_id == 'px4ctrl':
        return ['Px4CtrlAttitudeThrustAdapter.mo']
    if scheme_id == 'linear_mpc' and boundary == 'ROTOR_COMMAND':
        return ['LinearMPCRotorAdapter.mo']

    return [f'{pascal}{suffix}']

# Check coverage
missing = []
covered = []

for scheme in schemes:
    sid = scheme['scheme_id']
    boundary = scheme.get('formal_closed_loop_boundary', 'ATTITUDE_THRUST')

    candidates = scheme_to_adapter_candidates(sid, boundary)
    found = None
    for candidate in candidates:
        if (ADAPTERS_DIR / candidate).exists():
            found = candidate
            break

    if found:
        covered.append((sid, found))
        print(f"[OK]   {sid:45s} → {found}")
    else:
        missing.append((sid, boundary, candidates))
        print(f"[MISS] {sid:45s} {boundary:20s} (expected: {candidates[0]})")

print(f"\n{'='*80}")
print(f"Phase 2 Summary:")
print(f"  - Covered: {len(covered)}/46")
print(f"  - Missing: {len(missing)}/46")

if missing:
    print(f"\nMissing Adapters:")
    for sid, boundary, candidates in missing:
        print(f"  - {sid} ({boundary}): expected {candidates[0]}")
else:
    print(f"\n✓ All 46 controllers have Mapper coverage!")

print(f"{'='*80}")
