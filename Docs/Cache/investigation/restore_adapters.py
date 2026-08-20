#!/usr/bin/env python3
"""
Restore Control/Adapters package with all 52 adapter files
"""
import shutil
from pathlib import Path

# Archive root
archive_adapters = Path('E:/刘致远18001500226/MoSim_Archive/20260818_codex_legacy_architecture/Control_Adapters')

# Target root
target_adapters = Path('Models/MoSimQuadrotorModel/Control/Adapters')

# Create target directory
target_adapters.mkdir(exist_ok=True)

# Copy all .mo files
copied = []
for mo_file in archive_adapters.glob('*.mo'):
    if mo_file.name in ('package.mo', 'package.order'):
        continue

    target_file = target_adapters / mo_file.name
    shutil.copy2(mo_file, target_file)
    copied.append(mo_file.name)

# Create package.mo
pkg_file = target_adapters / 'package.mo'
pkg_file.write_text(
    'within MoSimQuadrotorModel.Control;\n'
    'package Adapters "Controller adapters for boundary integration"\n'
    '  annotation(__MWORKS(hide = false));\n'
    'end Adapters;\n',
    encoding='utf-8'
)

# Create package.order (alphabetically sorted)
order_file = target_adapters / 'package.order'
adapter_names = sorted([Path(f).stem for f in copied])
order_file.write_text('\n'.join(adapter_names) + '\n', encoding='utf-8')

print(f'Successfully restored {len(copied)} adapters')
print(f'Created package.mo and package.order')
