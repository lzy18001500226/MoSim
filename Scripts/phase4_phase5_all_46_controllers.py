#!/usr/bin/env python3
"""
Phase 4 + Phase 5: ALL 46 controllers (no filtering)
- Phase 4: Sysploper CheckModel verification
- Phase 5: 50s ClimbPath simulation
"""
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
CATALOG_PATH = BASE_DIR / 'Config/control_platform/control_scheme_catalog.json'
PHASE3_PATH = BASE_DIR / 'Results/control_platform/phase3_graphical_core_rebuild/phase3_final_restoration_summary.json'
RESULTS_DIR = BASE_DIR / 'Results/control_platform/phase4_phase5_all_46'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Launch MCP driver subprocess
mcp_driver = subprocess.Popen(
    ['D:/Dev/Anaconda3/python.exe', 'Scripts/sysplorer_mcp_driver.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

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

# Load catalog and Phase 3 results
catalog_data = json.load(open(CATALOG_PATH, encoding='utf-8'))
schemes = {s['scheme_id']: s for s in catalog_data['schemes']}

phase3_data = json.load(open(PHASE3_PATH, encoding='utf-8'))
phase3_controllers = set(phase3_data['results'].keys())

# ALL 46 controllers from Phase 1-3 restoration (no filtering by PASS/SKIP status)
all_controllers = sorted(phase3_controllers)

print(f"Phase 4+5 Pipeline: ALL {len(all_controllers)} controllers")
print(f"Results: {RESULTS_DIR}")
print("="*80)

results = {}
phase4_start = time.time()

# ============================================================================
# PHASE 4: CheckModel
# ============================================================================
print("\n[PHASE 4] CheckModel verification")
print("-"*80)

phase4_pass = []
phase4_fail = []

for i, sid in enumerate(all_controllers, 1):
    scheme = schemes[sid]
    family = scheme['implementation_package']
    pkg_name = scheme_to_pkg(sid)

    runner_class = f'MoSimQuadrotorModel.Experiment.{family}.{pkg_name}GraphicalRunner'

    print(f"[{i:2d}/46] {sid:45s} ", end='', flush=True)

    # CheckModel via MCP driver subprocess
    mcp_driver.stdin.write(f"CHECK:{runner_class}\n")
    mcp_driver.stdin.flush()
    response = mcp_driver.stdout.readline()
    check_result = json.loads(response)

    if check_result.get('ok'):
        print("PASS")
        phase4_pass.append(sid)
        results[sid] = {
            'phase4': 'PASS',
            'check_time': check_result.get('elapsed_s', 0)
        }
    else:
        print(f"FAIL - {check_result.get('error', 'unknown')}")
        phase4_fail.append(sid)
        results[sid] = {
            'phase4': 'FAIL',
            'error': check_result.get('error', 'unknown')
        }

phase4_elapsed = time.time() - phase4_start

print()
print(f"Phase 4 Complete: {len(phase4_pass)}/46 PASS ({len(phase4_pass)/46*100:.1f}%)")
print(f"Elapsed: {phase4_elapsed:.1f}s")

# ============================================================================
# PHASE 5: ClimbPath Simulation (only controllers that passed Phase 4)
# ============================================================================
print("\n[PHASE 5] ClimbPath 50s simulation")
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

    # Simulate via MCP driver subprocess
    mcp_driver.stdin.write(f"SIM:{runner_class}\n")
    mcp_driver.stdin.flush()
    response = mcp_driver.stdout.readline()
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

report_path = RESULTS_DIR / 'phase4_phase5_all_46_report.json'
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
print("FINAL SUMMARY")
print("="*80)
print(f"Phase 4: {len(phase4_pass)}/46 PASS ({len(phase4_pass)/46*100:.1f}%)")
print(f"Phase 5: {len(phase5_pass)}/{len(phase4_pass)} PASS ({len(phase5_pass)/len(phase4_pass)*100:.1f}% of tested)")
print(f"Total: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
print()
print(f"Report: {report_path}")

# Cleanup MCP driver subprocess
mcp_driver.stdin.close()
mcp_driver.terminate()
mcp_driver.wait()
