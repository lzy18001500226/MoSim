#!/usr/bin/env python3
"""
Fix nested end statements in Core files
Pattern: files have both 'end XXXCore;' and 'end MoSim_XXX;'
Need to remove the outer wrong end statement
"""
import re
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
CONTROL_ROOT = BASE_DIR / 'Models/MoSimQuadrotorModel/Control'

core_files = list(CONTROL_ROOT.rglob('*Core.mo'))

print(f"Found {len(core_files)} Core files")
print(f"{'='*80}\n")

fixed = 0
skipped = 0

for core_path in core_files:
    content = core_path.read_text(encoding='utf-8')
    expected_name = core_path.stem

    # Find all end statements
    end_matches = list(re.finditer(r'\bend\s+(\w+)\s*;', content))

    if len(end_matches) < 2:
        skipped += 1
        continue

    # Check last end statement
    last_end = end_matches[-1]
    last_end_name = last_end.group(1)

    if last_end_name == expected_name:
        skipped += 1
        continue

    # Remove the wrong outer end statement
    content = content[:last_end.start()] + content[last_end.end():]
    content = content.rstrip() + '\n'

    core_path.write_text(content, encoding='utf-8')

    rel_path = str(core_path.relative_to(CONTROL_ROOT))
    print(f"[FIX]  {rel_path:60s} removed outer 'end {last_end_name};'")
    fixed += 1

print(f"\n{'='*80}")
print(f"Fixed {fixed} files, skipped {skipped}")
print(f"{'='*80}")
