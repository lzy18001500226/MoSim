#!/usr/bin/env python3
"""
Phase 3: Restore remaining 12 failed controllers
- 6 with P9/G9 archive files (rl_gain_scheduler, trained_neural_residual, nmpc_outer, smc_boundary_layer, se3_basic, dfbc_basic)
- 1 official_pid (use OfficialPidSysblockCore.mo, 41KB)
- 5 IntegratedChains (use AWFFCoreSysblock.mo as template for fixed_awff_pid, mark others as skip)
"""
import json
import re
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
CATALOG_PATH = BASE_DIR / 'Config/control_platform/control_scheme_catalog.json'
ARCHIVE_ROOT = Path('E:/刘致远18001500226/MoSim_Archive/20260818_codex_legacy_architecture/Control_Implementations_Graphical')
TARGET_ROOT = BASE_DIR / 'Models/MoSimQuadrotorModel/Control'

# Mapping for 12 controllers
ARCHIVE_MAPPING = {
    # P9/G9 archive files (6 controllers)
    'rl_gain_scheduler': 'Learning/MoSim_P9_RL_GAIN_SCHEDULER_GRAPHICAL_MIL.mo',
    'trained_neural_residual': 'Learning/MoSim_P9_TRAINED_NEURAL_RESIDUAL_GRAPHICAL_MIL.mo',
    'nmpc_outer': 'Optimization/MoSim_G9_NMPC_OUTER_GRAPHICAL_OVERVIEW.mo',
    'smc_boundary_layer': 'SlidingMode/MoSim_G9_SMC_BOUNDARY_LAYER_GRAPHICAL_OVERVIEW.mo',
    'se3_basic': 'GeometricFlatness/MoSim_G9_SE3_GRAPHICAL_OVERVIEW.mo',
    'dfbc_basic': 'GeometricFlatness/MoSim_G9_DFBC_GRAPHICAL_OVERVIEW.mo',

    # official_pid (1 controller, use 41KB Sysblock implementation)
    'official_pid': 'Graphical/PID/OfficialPidSysblockCore.mo',
}

# IntegratedChains - only restore fixed_awff_pid, others need special handling
AWFF_TEMPLATE = 'Graphical/ProjectOwned/AWFFCoreSysblock.mo'

def scheme_to_pkg(sid):
    """scheme_id to PascalCase package name"""
    special = {
        'pid': 'Pid', 'lqr': 'Lqr', 'lqi': 'Lqi', 'lqg': 'Lqg',
        'h2': 'H2', 'hinf': 'Hinf', 'mrac': 'Mrac', 'ndi': 'Ndi',
        'smc': 'Smc', 'mpc': 'Mpc', 'ilqr': 'Ilqr', 'mppi': 'Mppi',
        'nmpc': 'Nmpc', 'se3': 'Se3', 'dfbc': 'Dfbc', 'rl': 'Rl',
        'fopid': 'Fopid', 'awff': 'Awff', 'cbf': 'Cbf', 'eso': 'Eso',
        'l1': 'L1', 'indi': 'Indi', 'qp': 'Qp',
    }
    parts = sid.split('_')
    return ''.join([special.get(p, p.capitalize()) for p in parts])

# Load catalog
data = json.load(open(CATALOG_PATH, encoding='utf-8'))
schemes = {s['scheme_id']: s for s in data['schemes']
           if s['execution_kind'] == 'graphical_control_core'
           and s['implementation_status'] == 'implemented'}

print("="*80)
print("PHASE 3: Restore remaining 12 failed controllers")
print("="*80)

# Verify archive files
missing = []
for sid, rel_path in ARCHIVE_MAPPING.items():
    src = ARCHIVE_ROOT / rel_path
    if not src.exists():
        missing.append(f"  - {sid}: {rel_path}")

if missing:
    print("ERROR: Archive files not found:")
    print('\n'.join(missing))
    exit(1)

success = 0
failed = 0
skipped = 0

# Process 7 controllers with archive mappings
for sid, rel_path in ARCHIVE_MAPPING.items():
    scheme = schemes[sid]
    family = scheme['implementation_package']
    pkg_name = scheme_to_pkg(sid)

    src_path = ARCHIVE_ROOT / rel_path
    src_content = src_path.read_text(encoding='utf-8')

    # Find model declaration
    model_match = re.search(r'model\s+(\w+)', src_content)
    if not model_match:
        print(f"[FAIL] {sid:45s} NO MODEL DECLARATION")
        failed += 1
        continue

    orig_name = model_match.group(1)

    # Transform: rename to XXXCore, update within path
    new_content = src_content.replace(
        f'model {orig_name}',
        f'model {pkg_name}Core'
    )
    new_content = re.sub(
        r'within [^;]+;',
        f'within MoSimQuadrotorModel.Control.{family}.{pkg_name};',
        new_content
    )

    # Write to target
    target_dir = TARGET_ROOT / family / pkg_name
    target_dir.mkdir(parents=True, exist_ok=True)
    core_path = target_dir / f'{pkg_name}Core.mo'
    core_path.write_text(new_content, encoding='utf-8')

    size_kb = len(new_content) / 1024
    print(f"[OK]   {sid:45s} → {family}/{pkg_name}  {size_kb:6.1f}KB")
    success += 1

# Handle fixed_awff_pid specially
sid = 'fixed_awff_pid'
if sid in schemes:
    scheme = schemes[sid]
    family = scheme['implementation_package']
    pkg_name = scheme_to_pkg(sid)

    src_path = ARCHIVE_ROOT / AWFF_TEMPLATE
    src_content = src_path.read_text(encoding='utf-8')

    # Transform AWFFCoreSysblock to FixedAwffPidCore
    new_content = src_content.replace(
        'model AWFFCoreSysblock',
        f'model {pkg_name}Core'
    )
    new_content = re.sub(
        r'within [^;]+;',
        f'within MoSimQuadrotorModel.Control.{family}.{pkg_name};',
        new_content
    )

    target_dir = TARGET_ROOT / family / pkg_name
    target_dir.mkdir(parents=True, exist_ok=True)
    core_path = target_dir / f'{pkg_name}Core.mo'
    core_path.write_text(new_content, encoding='utf-8')

    size_kb = len(new_content) / 1024
    print(f"[OK]   {sid:45s} → {family}/{pkg_name}  {size_kb:6.1f}KB (AWFF template)")
    success += 1

# Skip remaining 4 IntegratedChains (need complex extraction)
REMAINING_INTEGRATED = [
    'fixed_awff_l1_residual',
    'fixed_awff_l1_indi',
    'fixed_linear_mpc_l1_indi',
    'fixed_qp_nmpc_l1_indi_cbf'
]
for sid in REMAINING_INTEGRATED:
    print(f"[SKIP] {sid:45s} (IntegratedChains - requires complex extraction)")
    skipped += 1

print(f"\n{'='*80}")
print(f"Phase 3 Restoration: {success} success, {failed} failed, {skipped} skipped")
print(f"Total restored: {success}/12")
print(f"{'='*80}")
