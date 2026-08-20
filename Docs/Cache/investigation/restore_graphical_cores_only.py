#!/usr/bin/env python3
"""
Phase 1: Restore 9 real graphical CoreSysblock files only
"""
import re
from pathlib import Path

# Archive root
archive_root = Path('E:/刘致远18001500226/MoSim_Archive/20260818_codex_legacy_architecture/Control_Implementations_Graphical')

# Target root
target_root = Path('Models/MoSimQuadrotorModel/Control')

# Mapping: scheme_id -> (PascalCase package name, archive relative path)
GRAPHICAL_CORES = {
    'fixed_awff_pid': ('FixedAwffPid', 'Graphical/AWFF/AwffFullControllerCoreSysblock.mo'),
    'fixed_awff_l1_indi': ('FixedAwffL1Indi', 'Graphical/AWFF/AwffL1IndiControllerCoreSysblock.mo'),
    'fixed_awff_l1_residual': ('FixedAwffL1Residual', 'Graphical/AWFF/AwffL1ResidualControllerCoreSysblock.mo'),
    'fixed_linear_mpc_l1_indi': ('FixedLinearMpcL1Indi', 'Graphical/LinearMPC/LinearMpcL1IndiControllerCoreSysblock.mo'),
    'official_pid': ('OfficialPid', 'Graphical/PID/OfficialPidCoreSysblock.mo'),
    'fixed_qp_nmpc_l1_indi_cbf': ('FixedQpNmpcL1IndiCbf', 'Graphical/QPNMPC/QpNmpcL1IndiCbfControllerCoreSysblock.mo'),
}

def fix_within_path(content, old_within, new_within):
    """Replace within statement"""
    pattern = r'within\s+' + re.escape(old_within) + r'\s*;'
    replacement = f'within {new_within};'
    return re.sub(pattern, replacement, content, count=1)

def fix_extends_paths(content):
    """Fix extends statements that reference old Implementations structure"""
    # Fix: Control.Implementations.Sysblocks -> Control.Sysblocks
    content = re.sub(
        r'MoSimQuadrotorModel\.Control\.Implementations\.Sysblocks',
        'MoSimQuadrotorModel.Control.Sysblocks',
        content
    )
    return content

def rename_model(content, new_model_name):
    """Rename model definition to match new Core naming"""
    # Match: model OldName "description" at the beginning
    pattern = r'(model\s+)\w+(\s+"[^"]*")'
    replacement = r'\g<1>' + new_model_name + r'\g<2>'
    content = re.sub(pattern, replacement, content, count=1)

    # Match: end OldName; at the very end (last occurrence)
    # Split by lines and replace only the last 'end XXX;'
    lines = content.split('\n')
    for i in range(len(lines) - 1, -1, -1):
        if re.match(r'end\s+\w+\s*;', lines[i].strip()):
            lines[i] = f'end {new_model_name};'
            break

    return '\n'.join(lines)

if __name__ == '__main__':
    restored = []
    failed = []

    for scheme_id, (pkg_name, archive_rel) in GRAPHICAL_CORES.items():
        archive_path = archive_root / archive_rel

        if not archive_path.exists():
            failed.append((scheme_id, f'Archive not found: {archive_path}'))
            continue

        # Package directory should already exist from previous script
        pkg_dir = target_root / pkg_name
        if not pkg_dir.exists():
            failed.append((scheme_id, f'Package directory not found: {pkg_dir}'))
            continue

        # Read source
        content = archive_path.read_text(encoding='utf-8')

        # Fix within statement
        within_match = re.search(r'within\s+([\w\.]+)\s*;', content)
        if within_match:
            old_within = within_match.group(1)
            new_within = f'MoSimQuadrotorModel.Control.{pkg_name}'
            content = fix_within_path(content, old_within, new_within)

        # Fix extends paths to Sysblocks
        content = fix_extends_paths(content)

        # Rename model to XXXCore
        new_model_name = f'{pkg_name}Core'
        content = rename_model(content, new_model_name)

        # Write to Core file (overwrite incorrect MIL content)
        target_file = pkg_dir / f'{pkg_name}Core.mo'
        target_file.write_text(content, encoding='utf-8')

        restored.append(pkg_name)

    print(f'Successfully restored {len(restored)} graphical cores:')
    for name in restored:
        print(f'  - {name}')

    if failed:
        print(f'\nFailed: {len(failed)}')
        for scheme_id, reason in failed:
            print(f'  - {scheme_id}: {reason}')
