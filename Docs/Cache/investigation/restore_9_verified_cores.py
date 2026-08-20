#!/usr/bin/env python3
"""
Restore 9 verified controller cores from archive to new flat structure
"""
import json
import re
from pathlib import Path

# Load catalog to get all scheme_ids
catalog_path = Path('Config/control_platform/control_scheme_catalog.json')
data = json.load(open(catalog_path, encoding='utf-8'))

# Archive root
archive_root = Path('E:/刘致远18001500226/MoSim_Archive/20260818_codex_legacy_architecture/Control_Implementations_Graphical')

# Target root
target_root = Path('Models/MoSimQuadrotorModel/Control')

# Verified 9 cores with actual CoreSysblock.mo files
VERIFIED_CORES = {
    'fixed_awff_pid': 'Graphical/AWFF/AwffFullControllerCoreSysblock.mo',
    'fixed_awff_l1_indi': 'Graphical/AWFF/AwffL1IndiControllerCoreSysblock.mo',
    'fixed_awff_l1_residual': 'Graphical/AWFF/AwffL1ResidualControllerCoreSysblock.mo',
    'fixed_linear_mpc_l1_indi': 'Graphical/LinearMPC/LinearMpcL1IndiControllerCoreSysblock.mo',
    'official_pid': 'Graphical/PID/OfficialPidCoreSysblock.mo',
    'fixed_qp_nmpc_l1_indi_cbf': 'Graphical/QPNMPC/QpNmpcL1IndiCbfControllerCoreSysblock.mo',
}

def scheme_id_to_package_name(scheme_id):
    """Convert scheme_id to PascalCase"""
    parts = scheme_id.split('_')
    special = {
        'pid': 'Pid', 'lqr': 'Lqr', 'lqi': 'Lqi', 'lqg': 'Lqg',
        'h2': 'H2', 'hinf': 'Hinf', 'mrac': 'Mrac', 'ndi': 'Ndi',
        'smc': 'Smc', 'mpc': 'Mpc', 'ilqr': 'Ilqr', 'mppi': 'Mppi',
        'nmpc': 'Nmpc', 'qp': 'Qp', 'se3': 'Se3', 'dfbc': 'Dfbc',
        'rl': 'Rl', 'awff': 'Awff', 'l1': 'L1', 'indi': 'Indi',
        'cbf': 'Cbf', 'fopid': 'Fopid',
    }
    return ''.join([special.get(p, p.capitalize()) for p in parts])

def fix_within_path(content, old_within, new_within):
    """Replace within statement"""
    pattern = r'within\s+' + re.escape(old_within) + r'\s*;'
    replacement = f'within {new_within};'
    return re.sub(pattern, replacement, content, count=1)

if __name__ == '__main__':
    created_packages = []
    failed = []

    for scheme_id, archive_rel in VERIFIED_CORES.items():
        pkg_name = scheme_id_to_package_name(scheme_id)
        archive_path = archive_root / archive_rel

        if not archive_path.exists():
            failed.append((scheme_id, 'Archive file not found'))
            continue

        # Create target package directory
        pkg_dir = target_root / pkg_name
        pkg_dir.mkdir(exist_ok=True)

        # Read source file
        content = archive_path.read_text(encoding='utf-8')

        # Fix within statement
        within_match = re.search(r'within\s+([\w\.]+)\s*;', content)
        if within_match:
            old_within = within_match.group(1)
            new_within = f'MoSimQuadrotorModel.Control.{pkg_name}'
            content = fix_within_path(content, old_within, new_within)

        # Determine target filename (Core.mo)
        target_file = pkg_dir / f'{pkg_name}Core.mo'
        target_file.write_text(content, encoding='utf-8')

        # Create package.mo
        pkg_file = pkg_dir / 'package.mo'
        pkg_file.write_text(
            f'within MoSimQuadrotorModel.Control;\n'
            f'package {pkg_name} "{scheme_id} controller implementation"\n'
            f'  annotation(__MWORKS(hide = false));\n'
            f'end {pkg_name};\n',
            encoding='utf-8'
        )

        # Create package.order
        order_file = pkg_dir / 'package.order'
        order_file.write_text(f'{pkg_name}Core\n', encoding='utf-8')

        created_packages.append(pkg_name)

    print(f'Successfully created {len(created_packages)} verified core packages')
    for pkg in created_packages:
        print(f'  + {pkg}')

    if failed:
        print(f'\nFailed: {len(failed)}')
        for scheme_id, reason in failed:
            print(f'  - {scheme_id}: {reason}')
