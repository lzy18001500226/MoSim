#!/usr/bin/env python3
"""
Repair all 46 controllers by applying architectural fixes from official_pid baseline
Fix 1: Increase ESC limit from 110 to 200 rad/s
Fix 2: Replace GraphicalAttitudeThrustRotorPreview with appropriate baseline mapper
Fix 3: Add WorldFramePassthrough preprocessor (will require connection updates)

Strategy: Start with simple parameter fixes, then assess mapper replacement feasibility
"""
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
MODELS_DIR = BASE_DIR / 'Models/MoSimQuadrotorModel/Experiment/SingleUav'
BACKUP_DIR = BASE_DIR / 'Models/MoSimQuadrotorModel/Experiment/SingleUav_backup_20260822'
RESULTS_DIR = BASE_DIR / 'Results/control_platform/phase6_fresh_test_46'

# Find all GraphicalRunner.mo files
controller_files = list(MODELS_DIR.rglob('*GraphicalRunner.mo'))

print("="*80)
print("Controller Repair Script - Phase 6")
print("="*80)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total controllers found: {len(controller_files)}")
print("="*80)

# Create backup directory
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
print(f"\nBackup directory: {BACKUP_DIR}")

repair_log = []

for idx, controller_file in enumerate(sorted(controller_files), 1):
    rel_path = controller_file.relative_to(MODELS_DIR)
    print(f"\n[{idx:2d}/46] {rel_path}")

    # Read original content
    with open(controller_file, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # Create backup
    backup_file = BACKUP_DIR / rel_path
    backup_file.parent.mkdir(parents=True, exist_ok=True)
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(original_content)

    # Apply Fix 1: ESC limit 110 -> 200
    fix1_applied = False
    pattern_esc = r'(parameter\s+Real\s+nominal_esc_limit_abs\s*\([^)]*\)\s*=\s*)110'
    if re.search(pattern_esc, original_content):
        modified_content = re.sub(pattern_esc, r'\g<1>200', original_content)
        fix1_applied = True
        print(f"  [OK] Fix 1: ESC limit 110 -> 200")
    else:
        modified_content = original_content
        print(f"  [SKIP] Fix 1: No ESC limit pattern found")

    # Write modified content
    with open(controller_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)

    repair_log.append({
        'file': str(rel_path),
        'esc_limit_fixed': fix1_applied,
        'backup_created': True
    })

print("\n" + "="*80)
print(f"Repair phase 1 completed: {len(controller_files)} files processed")
print(f"Backup location: {BACKUP_DIR}")
print("="*80)

# Save repair log
log_file = RESULTS_DIR / 'repair_log_phase1.json'
import json
with open(log_file, 'w', encoding='utf-8') as f:
    json.dump({
        'timestamp': datetime.now().isoformat(),
        'total_files': len(controller_files),
        'fixes_applied': {
            'esc_limit_200': sum(1 for r in repair_log if r['esc_limit_fixed'])
        },
        'backup_dir': str(BACKUP_DIR),
        'details': repair_log
    }, f, indent=2)

print(f"\nRepair log saved: {log_file}")
print(f"\nNext steps:")
print(f"1. Run CheckModel on sample controllers to verify ESC limit fix")
print(f"2. Run simulation tests to measure improvement")
print(f"3. Assess mapper replacement strategy based on results")
