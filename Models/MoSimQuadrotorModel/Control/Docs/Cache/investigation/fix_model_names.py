#!/usr/bin/env python3
"""
Fix model names in 11 controller cores that still use old Sysblock naming
"""
import re
from pathlib import Path

target_root = Path('Models/MoSimQuadrotorModel/Control')

# List of packages needing fix
PACKAGES = [
    'AdaptiveBackstepping', 'BacksteppingBaseline', 'FeedbackLinearization',
    'H2StateFeedback', 'HinfHoverWrench', 'Lqg', 'LqiBaseline', 'Mrac',
    'Ndi', 'PassivityBasedControl', 'PolePlacementLuenberger'
]

def rename_model(content, new_model_name):
    """Rename model to XXXCore"""
    # Match: model OldName "description"
    pattern = r'(model\s+)\w+(\s+"[^"]*")'
    replacement = r'\g<1>' + new_model_name + r'\g<2>'
    content = re.sub(pattern, replacement, content, count=1)

    # Match: end OldName; at the very end (last occurrence)
    lines = content.split('\n')
    for i in range(len(lines) - 1, -1, -1):
        if re.match(r'end\s+\w+\s*;', lines[i].strip()):
            lines[i] = f'end {new_model_name};'
            break

    return '\n'.join(lines)

if __name__ == '__main__':
    fixed = []

    for pkg in PACKAGES:
        core_file = target_root / pkg / f'{pkg}Core.mo'
        if not core_file.exists():
            print(f'SKIP: {core_file} does not exist')
            continue

        content = core_file.read_text(encoding='utf-8')

        # Check if already correct
        if f'model {pkg}Core' in content:
            print(f'SKIP: {pkg} already has correct model name')
            continue

        # Fix model name
        new_content = rename_model(content, f'{pkg}Core')

        # Write back
        core_file.write_text(new_content, encoding='utf-8')
        fixed.append(pkg)
        print(f'FIXED: {pkg}')

    print(f'\nTotal fixed: {len(fixed)}')
