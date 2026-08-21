#!/usr/bin/env python3
"""Quick test of LQR baseline controller"""
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path('C:/Users/HP/Desktop/MoSim')
SYSPLORER = r'D:\Program Files\MWORKS\Sysplorer 2026a\Bin64\mworks.exe'

model_path = 'MoSimQuadrotorModel.Experiment.SingleUav.ClassicRobust.LqrBaselineGraphicalRunner'

print("=" * 80)
print("Testing LQR Baseline Controller")
print("=" * 80)

# Change to Models directory
import os
os.chdir(BASE_DIR / 'Models')

# Build command
cmd = [
    SYSPLORER,
    '-batch',
    '-eval',
    f'OpenModel("{model_path}"); SimulateModel("{model_path}"); exit();'
]

print(f"\nRunning: {model_path}")
print(f"Command: {' '.join(cmd)}")

try:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,  # 5 minute timeout
        cwd=str(BASE_DIR / 'Models')
    )

    print(f"\nReturn code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT:\n{result.stdout[:1000]}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr[:1000]}")

    sys.exit(result.returncode)

except subprocess.TimeoutExpired:
    print("\nERROR: Simulation timed out after 5 minutes")
    sys.exit(1)
except Exception as e:
    print(f"\nERROR: {e}")
    sys.exit(1)
