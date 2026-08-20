#!/usr/bin/env python3
"""
Fix all Core files missing 'end XXXCore;' statements
Critical bug from Phase 2/3 restoration
"""
from pathlib import Path
import re

BASE = Path('C:/Users/HP/Desktop/MoSim/Models/MoSimQuadrotorModel/Control')

# Find all Core files
core_files = list(BASE.rglob('*Core.mo'))

fixed = 0
already_ok = 0
failed = []

for core_path in core_files:
    content = core_path.read_text(encoding='utf-8')

    # Extract model name from 'model XXXCore' declaration
    model_match = re.search(r'^model\s+(\w+Core)', content, re.MULTILINE)
    if not model_match:
        failed.append((core_path, "No model declaration found"))
        continue

    model_name = model_match.group(1)

    # Check if end statement exists and is correct
    end_pattern = rf'^end\s+{re.escape(model_name)}\s*;'
    if re.search(end_pattern, content, re.MULTILINE):
        already_ok += 1
        continue

    # Add end statement
    # Remove trailing whitespace and ensure exactly one newline before end
    content = content.rstrip() + f'\nend {model_name};\n'

    core_path.write_text(content, encoding='utf-8')
    rel = core_path.relative_to(BASE)
    print(f"[FIX] {rel}")
    fixed += 1

print(f"\n{'='*80}")
print(f"Fixed: {fixed}, Already OK: {already_ok}, Failed: {len(failed)}")
if failed:
    print("\nFailed files:")
    for path, reason in failed:
        print(f"  {path.relative_to(BASE)}: {reason}")
print(f"{'='*80}")
