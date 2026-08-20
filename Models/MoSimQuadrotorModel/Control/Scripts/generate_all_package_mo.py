#!/usr/bin/env python3
"""
Generate package.mo for all controller subdirectories based on actual Core files
"""
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
CONTROL_ROOT = BASE_DIR / 'Models/MoSimQuadrotorModel/Control'

# Find all Core files and extract their parent directories
core_files = list(CONTROL_ROOT.rglob('*Core.mo'))

created = 0
for core_path in core_files:
    ctrl_dir = core_path.parent
    package_file = ctrl_dir / 'package.mo'

    # Skip if package.mo already exists
    if package_file.exists():
        continue

    # Extract family and controller name
    relative = ctrl_dir.relative_to(CONTROL_ROOT)
    parts = relative.parts

    if len(parts) == 1:
        # Direct under Control (like Px4Ctrl, PID)
        family = 'Control'
        ctrl_name = parts[0]
        within_stmt = f'within MoSimQuadrotorModel.Control;'
    elif len(parts) == 2:
        # Under a family (like PidFamily/CascadePid)
        family = parts[0]
        ctrl_name = parts[1]
        within_stmt = f'within MoSimQuadrotorModel.Control.{family};'
    else:
        print(f"[SKIP] Unexpected path depth: {relative}")
        continue

    content = f'''{within_stmt}
package {ctrl_name} "{ctrl_name} controller package"
end {ctrl_name};
'''

    package_file.write_text(content, encoding='utf-8')
    print(f"[CREATE] {relative}/package.mo")
    created += 1

print(f"\n{'='*80}")
print(f"Created {created} package.mo files")
print(f"{'='*80}")
