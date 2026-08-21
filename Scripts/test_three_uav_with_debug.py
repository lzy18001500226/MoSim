#!/usr/bin/env python3
"""
Test ThreeUavPx4CtrlOpenBlocksRunner with debug info enabled.
"""
import sys
import os

# Add Sysplorer Python API path
sysplorer_path = r"D:\Program Files\MWORKS\Sysplorer 2026a\Bin"
if sysplorer_path not in sys.path:
    sys.path.insert(0, sysplorer_path)

import mworks.sysplorer as ModelingPy

def main():
    model_name = 'MoSimQuadrotorModel.Experiment.OpenBlocks.Px4Ctrl.Formation.ThreeUavPx4CtrlOpenBlocksRunner'

    print("Loading library...")
    if not ModelingPy.ClassExist('MoSimQuadrotorModel'):
        ModelingPy.LoadFile(r'C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\package.mo')

    print("Checking model...")
    ModelingPy.CheckModel(model_name)

    print("Translating model with debug options...")
    # Enable debug information
    ModelingPy.SetCompilerSettings({
        'includeCallInError': True,
        'debugInfo': True
    })

    result = ModelingPy.TranslateModel(model_name)
    if not result:
        print(f"TranslateModel failed: {ModelingPy.GetLastErrors()}")
        return False

    print("Running simulation (200s)...")
    output_dir = r'C:\Users\HP\Desktop\MoSim\Results\simulation_test_debug'
    os.makedirs(output_dir, exist_ok=True)

    result = ModelingPy.SimulateModel(
        modelName=model_name,
        startTime=0.0,
        stopTime=200.0,
        interval=0.01,
        tolerance=1e-6,
        algo='Dassl',
        storeDouble=True,
        path=output_dir
    )

    print(f"SimulateModel result: {result}")
    errors = ModelingPy.GetLastErrors()
    print(f"Errors: {errors}")

    # Check log file
    log_file = os.path.join(output_dir, 'MWSolverLog.txt')
    if os.path.exists(log_file):
        print("\nLast 50 lines of MWSolverLog.txt:")
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for line in lines[-50:]:
                print(line.rstrip())

    return result

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
