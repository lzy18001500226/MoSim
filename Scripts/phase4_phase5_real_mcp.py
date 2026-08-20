#!/usr/bin/env python3
"""
Phase 4 + Phase 5: ALL 46 controllers - REAL Sysplorer MCP execution
Direct integration with Claude's Sysplorer MCP tools
"""
import json
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
PHASE3_PATH = BASE_DIR / 'Results/control_platform/phase3_graphical_core_rebuild/phase3_final_restoration_summary.json'
RESULTS_DIR = BASE_DIR / 'Results/control_platform/phase4_phase5_real_mcp'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def scheme_to_pkg(sid):
    special = {
        'pid': 'Pid', 'lqr': 'Lqr', 'lqi': 'Lqi', 'lqg': 'Lqg',
        'h2': 'H2', 'hinf': 'Hinf', 'mrac': 'Mrac', 'ndi': 'Ndi',
        'smc': 'Smc', 'mpc': 'Mpc', 'ilqr': 'Ilqr', 'mppi': 'Mppi',
        'nmpc': 'Nmpc', 'se3': 'Se3', 'dfbc': 'Dfbc', 'rl': 'Rl',
        'fopid': 'Fopid', 'awff': 'Awff', 'cbf': 'Cbf', 'eso': 'Eso',
        'l1': 'L1', 'indi': 'Indi', 'qp': 'Qp',
    }
    parts = sid.split('_')
    return ''.join([special.get(p, p.capitalize()) for p in parts])

# Load Phase 3 to get exact 46-controller scope
phase3_data = json.load(open(PHASE3_PATH, encoding='utf-8'))
phase3_controllers = set(phase3_data['results'].keys())

# Load catalog to get implementation_package
from pathlib import Path
catalog_path = BASE_DIR / 'Config/control_platform/control_scheme_catalog.json'
data = json.load(open(catalog_path, encoding='utf-8'))
schemes = {s['scheme_id']: s for s in data['schemes']}

# ALL 46 controllers from Phase 3 (no filtering)
all_controllers = sorted(phase3_controllers)

print(f"Phase 4+5 Real MCP: {len(all_controllers)} controllers")
print(f"Results: {RESULTS_DIR}")
print("="*80)

results = {}
phase4_start = time.time()

# ============================================================================
# PHASE 4: CheckModel - REAL Sysplorer MCP
# ============================================================================
print("\n[PHASE 4] CheckModel verification (REAL MCP)")
print("-"*80)

phase4_pass = []
phase4_fail = []

for i, sid in enumerate(all_controllers, 1):
    if sid not in schemes:
        print(f"[{i:2d}/46] {sid:45s} SKIP - not in catalog")
        continue

    scheme = schemes[sid]
    family = scheme['implementation_package']
    pkg_name = scheme_to_pkg(sid)
    runner_class = f'MoSimQuadrotorModel.Experiment.{family}.{pkg_name}GraphicalRunner'

    print(f"[{i:2d}/46] {sid:45s} ", end='', flush=True)

    # Signal to Claude: need mcp__sysplorer__check_model call
    print(f"\nREQUEST_MCP_CHECK:{runner_class}")
    # Claude will execute: mcp__sysplorer__check_model(model_names=[runner_class])
    # Then provide result via stdin
    response = input()
    check_result = json.loads(response)

    if check_result.get('ok'):
        print("PASS")
        phase4_pass.append(sid)
        results[sid] = {
            'phase4': 'PASS',
            'runner_class': runner_class,
            'check_time': check_result.get('elapsed_s', 0)
        }
    else:
        print(f"FAIL - {check_result.get('error', 'unknown')}")
        phase4_fail.append(sid)
        results[sid] = {
            'phase4': 'FAIL',
            'runner_class': runner_class,
            'error': check_result.get('error', 'unknown')
        }

phase4_elapsed = time.time() - phase4_start

print()
print(f"Phase 4 Complete: {len(phase4_pass)}/46 PASS ({len(phase4_pass)/46*100:.1f}%)")
print(f"Elapsed: {phase4_elapsed:.1f}s")

# Save Phase 4 checkpoint
checkpoint = {
    'phase4_complete': True,
    'phase4_pass': phase4_pass,
    'phase4_fail': phase4_fail,
    'results': results
}
with open(RESULTS_DIR / 'phase4_checkpoint.json', 'w', encoding='utf-8') as f:
    json.dump(checkpoint, f, indent=2, ensure_ascii=False)

# ============================================================================
# PHASE 5: ClimbPath Simulation - REAL Sysplorer MCP
# ============================================================================
print("\n[PHASE 5] ClimbPath 50s simulation (REAL MCP)")
print("-"*80)

phase5_start = time.time()
phase5_pass = []
phase5_fail = []

for i, sid in enumerate(phase4_pass, 1):
    scheme = schemes[sid]
    family = scheme['implementation_package']
    pkg_name = scheme_to_pkg(sid)
    runner_class = f'MoSimQuadrotorModel.Experiment.{family}.{pkg_name}GraphicalRunner'

    print(f"[{i:2d}/{len(phase4_pass)}] {sid:45s} ", end='', flush=True)

    # Signal to Claude: need mcp__sysplorer__simulate_model call
    print(f"\nREQUEST_MCP_SIM:{runner_class}")
    # Claude will execute: mcp__sysplorer__simulate_model(model_name=runner_class, ...)
    response = input()
    sim_result = json.loads(response)

    if sim_result.get('ok'):
        error = sim_result.get('terminal_error', 9999.0)
        results[sid]['phase5'] = 'PASS' if error < 5.0 else 'FAIL'
        results[sid]['terminal_error'] = error
        results[sid]['sim_time'] = sim_result.get('elapsed_s', 0)

        if error < 5.0:
            print(f"PASS ({error:.2f}m)")
            phase5_pass.append(sid)
        else:
            print(f"FAIL ({error:.2f}m)")
            phase5_fail.append(sid)
    else:
        print(f"ERROR - {sim_result.get('error', 'unknown')}")
        results[sid]['phase5'] = 'ERROR'
        results[sid]['error'] = sim_result.get('error', 'unknown')
        phase5_fail.append(sid)

phase5_elapsed = time.time() - phase5_start
total_elapsed = time.time() - phase4_start

# ============================================================================
# REPORT
# ============================================================================
report = {
    'timestamp': datetime.now().isoformat(),
    'execution_type': 'REAL_SYSPLORER_MCP',
    'total_controllers': 46,
    'phase4_checkmodel': {
        'pass': len(phase4_pass),
        'fail': len(phase4_fail),
        'rate': len(phase4_pass) / 46,
        'elapsed_s': phase4_elapsed
    },
    'phase5_climbpath': {
        'tested': len(phase4_pass),
        'pass': len(phase5_pass),
        'fail': len(phase5_fail),
        'rate': len(phase5_pass) / len(phase4_pass) if phase4_pass else 0,
        'elapsed_s': phase5_elapsed
    },
    'total_elapsed_s': total_elapsed,
    'results': results
}

report_path = RESULTS_DIR / 'phase4_phase5_real_mcp_report.json'
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

# Summary lists
with open(RESULTS_DIR / 'phase4_failed_controllers.txt', 'w') as f:
    f.write('\n'.join(phase4_fail))

with open(RESULTS_DIR / 'phase5_passed_controllers.txt', 'w') as f:
    f.write('\n'.join(phase5_pass))

with open(RESULTS_DIR / 'phase5_failed_controllers.txt', 'w') as f:
    f.write('\n'.join(phase5_fail))

print()
print("="*80)
print("FINAL SUMMARY (REAL MCP EXECUTION)")
print("="*80)
print(f"Phase 4: {len(phase4_pass)}/46 PASS ({len(phase4_pass)/46*100:.1f}%)")
print(f"Phase 5: {len(phase5_pass)}/{len(phase4_pass)} PASS ({len(phase5_pass)/len(phase4_pass)*100:.1f}% of tested)")
print(f"Total: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
print()
print(f"Report: {report_path}")
