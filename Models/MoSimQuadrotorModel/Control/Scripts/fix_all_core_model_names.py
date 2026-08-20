#!/usr/bin/env python3
"""
Fix all Core model names to match filename
Replace 'end MoSim_XXX_GRAPHICAL_MIL;' with 'end XXXCore;'
"""
import re
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
CONTROL_ROOT = BASE_DIR / 'Models/MoSimQuadrotorModel/Control'

# Find all Core files
core_files = list(CONTROL_ROOT.rglob('*Core.mo'))

print(f"Found {len(core_files)} Core files")
print(f"{'='*80}\n")

fixed = 0
skipped = 0

for core_path in core_files:
    content = core_path.read_text(encoding='utf-8')

    # Extract expected model name from filename
    expected_name = core_path.stem  # e.g., 'BacksteppingBaselineCore'

    # Find current end statement
    end_match = re.search(r'\bend\s+(\w+)\s*;', content)
    if not end_match:
        print(f"[WARN] {core_path.relative_to(CONTROL_ROOT)}: no end statement")
        continue

    current_end_name = end_match.group(1)

    # Check if already correct
    if current_end_name == expected_name:
        skipped += 1
        continue

    # Fix end line only (model declaration line is already correct)
    content = re.sub(
        r'\bend\s+' + re.escape(current_end_name) + r'\s*;',
        f'end {expected_name};',
        content
    )

    # Write back
    core_path.write_text(content, encoding='utf-8')

    rel_path = str(core_path.relative_to(CONTROL_ROOT))
    print(f"[FIX]  {rel_path:60s} {current_end_name} → {expected_name}")
    fixed += 1

print(f"\n{'='*80}")
print(f"Fixed {fixed} files, skipped {skipped} (already correct)")
print(f"{'='*80}")
