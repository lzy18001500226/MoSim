#!/usr/bin/env python3
"""
Manual test script for ThreeUavPx4CtrlOpenBlocksRunner simulation.
Run this directly in Sysplorer to get better error diagnostics.
"""

import sys
import os

# Add Sysplorer Python API path
sysplorer_path = r"D:\Program Files\MWORKS\Sysplorer 2026a\Bin"
if sysplorer_path not in sys.path:
    sys.path.insert(0, sysplorer_path)

import mworks.sysplorer as ModelingPy

def main():
    print("=" * 80)
    print("ThreeUavPx4CtrlOpenBlocksRunner Simulation Test")
    print("=" * 80)

    # Model name
    model_name = 'MoSimQuadrotorModel.Experiment.OpenBlocks.Px4Ctrl.Formation.ThreeUavPx4CtrlOpenBlocksRunner'

    # Check if library is loaded
    print("\n[1/5] Checking if MoSimQuadrotorModel is loaded...")
    if not ModelingPy.ClassExist('MoSimQuadrotorModel'):
        print("  Loading MoSimQuadrotorModel...")
        result = ModelingPy.LoadFile(r'C:\Users\HP\Desktop\MoSim\Models\MoSimQuadrotorModel\package.mo')
        if result:
            print("  ✓ Library loaded successfully")
        else:
            print("  ✗ Failed to load library")
            errors = ModelingPy.GetLastErrors()
            print(f"  Errors: {errors}")
            return False
    else:
        print("  ✓ MoSimQuadrotorModel already loaded")

    # Check model
    print(f"\n[2/5] Checking model: {model_name}")
    result = ModelingPy.CheckModel(model_name)
    errors = ModelingPy.GetLastErrors()
    if result:
        print("  ✓ CheckModel passed")
    else:
        print("  ✗ CheckModel failed")
        print(f"  Errors: {errors}")
        return False

    # Translate model
    print(f"\n[3/5] Translating model...")
    result = ModelingPy.TranslateModel(model_name)
    errors = ModelingPy.GetLastErrors()
    if result:
        print("  ✓ TranslateModel passed")
    else:
        print("  ✗ TranslateModel failed")
        print(f"  Errors: {errors}")
        return False

    # Check CSV files existence
    print(f"\n[4/5] Verifying CSV trajectory files...")
    csv_files = [
        r'C:\Users\HP\Desktop\MoSim\Results\planning\three_uav_open_blocks_mworks_20260720\sysplorer\uav1_reference.csv',
        r'C:\Users\HP\Desktop\MoSim\Results\planning\three_uav_open_blocks_mworks_20260720\sysplorer\uav2_reference.csv',
        r'C:\Users\HP\Desktop\MoSim\Results\planning\three_uav_open_blocks_mworks_20260720\sysplorer\uav3_reference.csv'
    ]
    all_exist = True
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            size_mb = os.path.getsize(csv_file) / (1024 * 1024)
            print(f"  ✓ {os.path.basename(csv_file)} exists ({size_mb:.2f} MB)")
        else:
            print(f"  ✗ {os.path.basename(csv_file)} NOT FOUND")
            all_exist = False

    if not all_exist:
        print("\n  ERROR: Some CSV files are missing!")
        return False

    # Simulate model
    print(f"\n[5/5] Running simulation (stopTime=200s)...")
    print("  This may take several minutes...")

    output_dir = r'C:\Users\HP\Desktop\MoSim\Results\simulation_test'
    os.makedirs(output_dir, exist_ok=True)

    import time
    start_time = time.time()

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

    elapsed = time.time() - start_time

    errors = ModelingPy.GetLastErrors()

    if result:
        print(f"  ✓ Simulation completed in {elapsed:.1f} seconds")

        # Check result file
        result_file = os.path.join(output_dir, model_name.replace('.', '_') + '_res.mat')
        if os.path.exists(result_file):
            file_size_mb = os.path.getsize(result_file) / (1024 * 1024)
            print(f"  ✓ Result file created: {file_size_mb:.2f} MB")

            # Open result and check time
            ModelingPy.OpenResult(result_file)
            time_values = ModelingPy.GetVarValues('Time')
            if len(time_values) > 0:
                actual_end_time = time_values[-1]
                print(f"  ✓ Actual simulation end time: {actual_end_time:.2f} s")

                if actual_end_time >= 199.0:
                    print("\n" + "=" * 80)
                    print("SUCCESS: Simulation reached target stopTime!")
                    print("=" * 80)
                    return True
                else:
                    print(f"\n  WARNING: Simulation stopped early at {actual_end_time:.2f}s")
                    print(f"  Expected: ~200s")
            else:
                print("  ✗ Could not read Time variable from result")
        else:
            print(f"  ✗ Result file not found: {result_file}")
    else:
        print(f"  ✗ Simulation failed after {elapsed:.1f} seconds")
        print(f"  Errors: {errors}")

        # Try to get more diagnostic info
        print("\n  Attempting to read log file...")
        log_file = os.path.join(os.path.dirname(ModelingPy.GetDirectory()), 'LveError.log')
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                if len(lines) > 0:
                    print(f"  Last 20 lines of LveError.log:")
                    for line in lines[-20:]:
                        print(f"    {line.rstrip()}")
                else:
                    print("  LveError.log is empty")
        else:
            print(f"  Log file not found: {log_file}")

    print("\n" + "=" * 80)
    print("Test completed")
    print("=" * 80)
    return result

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
