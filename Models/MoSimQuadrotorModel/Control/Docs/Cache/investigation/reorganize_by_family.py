#!/usr/bin/env python3
"""
Reorganize 46 controller packages into family-based directory structure

Target structure:
  Control/
    PidFamily/         (5 controllers: cascade_pid, gain_scheduled_pid, fuzzy_pid, neural_pid, official_pid)
    ClassicRobust/     (13 controllers: fopid, lqr_baseline, lqi_baseline, lqg, h2_state_feedback, etc.)
    SlidingMode/       (7 controllers: integral_smc, terminal_smc, etc.)
    Optimization/      (8 controllers: linear_mpc, robust_mpc, etc.)
    GeometricFlatness/ (6 controllers: se3_basic, dfbc_basic, etc.)
    Learning/          (2 controllers: trained_neural_residual, rl_gain_scheduler)
    IntegratedChains/  (5 controllers: fixed_awff_pid, fixed_awff_l1_residual, etc.)
"""
import json
import shutil
from pathlib import Path

# Load catalog
catalog_path = Path('Config/control_platform/control_scheme_catalog.json')
data = json.load(open(catalog_path, encoding='utf-8'))

control_root = Path('Models/MoSimQuadrotorModel/Control')

# Build mapping from scheme_id to implementation_package
scheme_to_package = {}
for s in data.get('schemes', []):
    if s.get('execution_kind') == 'graphical_control_core':
        scheme_to_package[s['scheme_id']] = s.get('implementation_package', 'Unknown')

# Convert scheme_id to PascalCase (same logic as before)
def scheme_id_to_package_name(scheme_id):
    parts = scheme_id.split('_')
    special = {
        'pid': 'Pid', 'lqr': 'Lqr', 'lqi': 'Lqi', 'lqg': 'Lqg',
        'h2': 'H2', 'hinf': 'Hinf', 'mrac': 'Mrac', 'ndi': 'Ndi',
        'smc': 'Smc', 'mpc': 'Mpc', 'ilqr': 'Ilqr', 'mppi': 'Mppi',
        'nmpc': 'Nmpc', 'se3': 'Se3', 'dfbc': 'Dfbc',
        'rl': 'Rl', 'fopid': 'Fopid',
    }
    return ''.join([special.get(p, p.capitalize()) for p in parts])

# Group controllers by family package
by_family = {}
for scheme_id, family_pkg in scheme_to_package.items():
    if family_pkg not in by_family:
        by_family[family_pkg] = []
    by_family[family_pkg].append(scheme_id)

print(f'Reorganizing {len(scheme_to_package)} controllers into {len(by_family)} family packages\n')

# For each family package
for family_pkg, controllers in by_family.items():
    print(f'{family_pkg} ({len(controllers)} controllers):')

    # Create family package directory
    family_dir = control_root / family_pkg
    family_dir.mkdir(exist_ok=True)

    # Move each controller into family directory
    for scheme_id in controllers:
        pkg_name = scheme_id_to_package_name(scheme_id)
        old_path = control_root / pkg_name
        new_path = family_dir / pkg_name

        if old_path.exists() and old_path != new_path:
            if new_path.exists():
                shutil.rmtree(new_path)
            shutil.move(str(old_path), str(new_path))
            print(f'  - Moved {pkg_name} -> {family_pkg}/{pkg_name}')
        elif new_path.exists():
            print(f'  - Already in place: {family_pkg}/{pkg_name}')
        else:
            print(f'  - WARNING: {pkg_name} not found')

    # Create family package.mo
    family_pkg_file = family_dir / 'package.mo'
    family_pkg_file.write_text(
        f'within MoSimQuadrotorModel.Control;\n'
        f'package {family_pkg} "Controller family: {family_pkg}"\n'
        f'  annotation(__MWORKS(hide = false));\n'
        f'end {family_pkg};\n',
        encoding='utf-8'
    )

    # Create family package.order
    family_order_file = family_dir / 'package.order'
    order_content = '\n'.join([scheme_id_to_package_name(s) for s in sorted(controllers)]) + '\n'
    family_order_file.write_text(order_content, encoding='utf-8')

    # Update within paths in all moved controller files
    for scheme_id in controllers:
        pkg_name = scheme_id_to_package_name(scheme_id)
        core_file = family_dir / pkg_name / f'{pkg_name}Core.mo'

        if core_file.exists():
            content = core_file.read_text(encoding='utf-8')
            # Change: within MoSimQuadrotorModel.Control.XXX;
            # To:     within MoSimQuadrotorModel.Control.FamilyPkg.XXX;
            old_within = f'within MoSimQuadrotorModel.Control.{pkg_name};'
            new_within = f'within MoSimQuadrotorModel.Control.{family_pkg}.{pkg_name};'
            content = content.replace(old_within, new_within, 1)
            core_file.write_text(content, encoding='utf-8')

        # Update package.mo
        pkg_file = family_dir / pkg_name / 'package.mo'
        if pkg_file.exists():
            content = pkg_file.read_text(encoding='utf-8')
            old_within = f'within MoSimQuadrotorModel.Control;'
            new_within = f'within MoSimQuadrotorModel.Control.{family_pkg};'
            content = content.replace(old_within, new_within, 1)
            pkg_file.write_text(content, encoding='utf-8')

print('\n=== Updating Control/package.order ===')

# Update Control/package.order to register family packages instead of individual controllers
control_order = control_root / 'package.order'
new_order = sorted(by_family.keys()) + ['Adapters', 'Allocation', 'Bridges', 'Sysblocks']
control_order.write_text('\n'.join(new_order) + '\n', encoding='utf-8')

print(f'Updated Control/package.order with {len(by_family)} family packages')
print('\nReorganization complete!')
