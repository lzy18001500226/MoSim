#!/usr/bin/env python3
"""完成重命名 - 删除旧目录和文件"""
import shutil
from pathlib import Path

MODELS_DIR = Path('Models/MoSimQuadrotorModel')

# 需要删除的旧目录
OLD_DIRS = [
    MODELS_DIR / 'Control' / 'IntegratedChains' / 'FixedAwffPid',
    MODELS_DIR / 'Control' / 'IntegratedChains' / 'FixedAwffL1Indi',
    MODELS_DIR / 'Control' / 'IntegratedChains' / 'FixedAwffL1Residual',
    MODELS_DIR / 'Control' / 'IntegratedChains' / 'FixedLinearMpcL1Indi',
    MODELS_DIR / 'Control' / 'IntegratedChains' / 'FixedQpNmpcL1IndiCbf',
]

# 需要删除的旧文件
OLD_FILES = [
    # GraphicalRunner
    MODELS_DIR / 'Experiment' / 'IntegratedChains' / 'FixedAwffPidGraphicalRunner.mo',
    MODELS_DIR / 'Experiment' / 'IntegratedChains' / 'FixedAwffL1IndiGraphicalRunner.mo',
    MODELS_DIR / 'Experiment' / 'IntegratedChains' / 'FixedAwffL1ResidualGraphicalRunner.mo',
    MODELS_DIR / 'Experiment' / 'IntegratedChains' / 'FixedLinearMpcL1IndiGraphicalRunner.mo',
    MODELS_DIR / 'Experiment' / 'IntegratedChains' / 'FixedQpNmpcL1IndiCbfGraphicalRunner.mo',
    # FamilyRunner
    MODELS_DIR / 'Experiment' / 'PidFamily' / 'FixedAwffPidFamilyRunner.mo',
    MODELS_DIR / 'Experiment' / 'PidFamily' / 'FixedAwffL1IndiFamilyRunner.mo',
    MODELS_DIR / 'Experiment' / 'PidFamily' / 'FixedAwffL1ResidualFamilyRunner.mo',
    MODELS_DIR / 'Experiment' / 'OptimizationPredictive' / 'FixedLinearMpcL1IndiFamilyRunner.mo',
    MODELS_DIR / 'Experiment' / 'OptimizationPredictive' / 'FixedQpNmpcL1IndiCbfFamilyRunner.mo',
    # Templates
    MODELS_DIR / 'Experiment' / 'Templates' / 'IntegratedChains' / 'FixedAwffPid.mo',
    MODELS_DIR / 'Experiment' / 'Templates' / 'IntegratedChains' / 'FixedAwffL1Indi.mo',
    MODELS_DIR / 'Experiment' / 'Templates' / 'IntegratedChains' / 'FixedAwffL1Residual.mo',
    MODELS_DIR / 'Experiment' / 'Templates' / 'IntegratedChains' / 'FixedLinearMpcL1Indi.mo',
    MODELS_DIR / 'Experiment' / 'Templates' / 'IntegratedChains' / 'FixedQpNmpcL1IndiCbf.mo',
]

print("=== Removing old directories ===")
for old_dir in OLD_DIRS:
    if old_dir.exists():
        shutil.rmtree(old_dir)
        print(f"REMOVED DIR: {old_dir}")
    else:
        print(f"SKIP (not exist): {old_dir}")

print("\n=== Removing old files ===")
for old_file in OLD_FILES:
    if old_file.exists():
        old_file.unlink()
        print(f"REMOVED FILE: {old_file}")
    else:
        print(f"SKIP (not exist): {old_file}")

print("\nDone!")
