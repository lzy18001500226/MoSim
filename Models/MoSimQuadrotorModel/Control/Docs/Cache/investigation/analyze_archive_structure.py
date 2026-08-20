#!/usr/bin/env python3
"""
Analyze archive structure to understand restoration pattern for remaining 40 controllers
"""
import json
import re
from pathlib import Path

# Load catalog (use absolute path)
catalog_path = Path('C:/Users/HP/Desktop/MoSim/Config/control_platform/control_scheme_catalog.json')
data = json.load(open(catalog_path, encoding='utf-8'))
cores = [s['scheme_id'] for s in data.get('schemes', [])
         if s.get('execution_kind') == 'graphical_control_core']

# Archive root
archive_root = Path('E:/刘致远18001500226/MoSim_Archive/20260818_codex_legacy_architecture/Control_Implementations_Graphical')

# Already completed in Phase 1
PHASE1_COMPLETED = {
    'official_pid', 'fixed_awff_pid', 'fixed_awff_l1_residual',
    'fixed_awff_l1_indi', 'fixed_linear_mpc_l1_indi', 'fixed_qp_nmpc_l1_indi_cbf'
}

remaining = [s for s in cores if s not in PHASE1_COMPLETED]

print(f'Total cores: {len(cores)}')
print(f'Phase 1 completed: {len(PHASE1_COMPLETED)}')
print(f'Remaining: {len(remaining)}')
print(f'\nRemaining controllers: {remaining}')

# Find all MIL and Sysblock files
mil_files = list(archive_root.glob('**/*_MIL.mo'))
sysblock_files = [f for f in archive_root.glob('**/*_Sysblock.mo')
                  if 'Sysblocks' not in str(f)]  # Exclude base Sysblocks

print(f'\nFound {len(mil_files)} MIL test models')
print(f'Found {len(sysblock_files)} controller-specific Sysblock files')

# Pattern analysis: check a few examples
print('\n=== Pattern Analysis ===')

examples = ['cascade_pid', 'lqr_baseline', 'fopid']
for scheme_id in examples:
    print(f'\n{scheme_id}:')
    # Find matching files
    pattern_upper = scheme_id.upper().replace('_', '_')
    mil_matches = [f for f in mil_files if pattern_upper in f.name.upper()]
    sysblock_matches = [f for f in sysblock_files if 'Classic' in str(f) or 'CFunction' in str(f)]

    print(f'  MIL candidates: {[f.name for f in mil_matches[:3]]}')
    if sysblock_matches:
        print(f'  Sysblock in ClassicRobust: {sysblock_matches[0].name if sysblock_matches else "None"}')
