#!/usr/bin/env python3
"""Scan all Sysblocks files and their usage across the codebase"""

import os
import re
from pathlib import Path

# Get all files in Sysblocks
sysblocks_dir = Path('Models/MoSimQuadrotorModel/Control/Sysblocks')
sysblocks_files = [f.stem for f in sysblocks_dir.glob('*.mo') if f.stem != 'package']

# Categorize files
graphical_files = []
equation_files = []
other_files = []

for fname in sysblocks_files:
    if 'Graphical' in fname:
        graphical_files.append(fname)
    elif 'Equation' in fname:
        equation_files.append(fname)
    else:
        other_files.append(fname)

print("=" * 80)
print("SYSBLOCKS FOLDER ANALYSIS")
print("=" * 80)
print(f"\nTotal files: {len(sysblocks_files)}")
print(f"  - Graphical (keep): {len(graphical_files)}")
print(f"  - Equation (archive): {len(equation_files)}")
print(f"  - Other (need review): {len(other_files)}")

# Scan for references
print("\n" + "=" * 80)
print("SCANNING REFERENCES TO SYSBLOCKS FILES")
print("=" * 80)

search_dirs = [
    'Models/MoSimQuadrotorModel/Control',
    'Models/MoSimQuadrotorModel/Experiment'
]

for sysblock in sysblocks_files[:10]:  # Sample first 10 to avoid timeout
    refs = []
    for search_dir in search_dirs:
        try:
            result = os.popen(f'grep -r "Sysblocks.{sysblock}" {search_dir} --include="*.mo" 2>/dev/null').read()
            if result.strip():
                refs.extend(result.strip().split('\n'))
        except:
            pass
    
    if refs:
        print(f"\n{sysblock}:")
        for ref in refs[:3]:  # Show first 3 references
            parts = ref.split(':')
            if len(parts) >= 2:
                file_path = parts[0].replace('Models/MoSimQuadrotorModel/', '')
                print(f"  - {file_path}")
        if len(refs) > 3:
            print(f"  ... and {len(refs) - 3} more references")

print("\n" + "=" * 80)
print("FILES TO ARCHIVE (Equation versions):")
print("=" * 80)
for eq in equation_files:
    print(f"  - {eq}.mo")

print("\n" + "=" * 80)
print("FILES TO MIGRATE (Graphical versions):")
print("=" * 80)
for gr in graphical_files:
    print(f"  - {gr}.mo")

print("\n" + "=" * 80)
print("FILES NEEDING REVIEW:")
print("=" * 80)
for oth in other_files:
    print(f"  - {oth}.mo")

