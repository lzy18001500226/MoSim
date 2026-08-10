#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Direct HDF5 reader for MWORKS MSR files
Export to CSV format for Julia plotting scripts
"""

import h5py
import numpy as np
import pandas as pd
import os
import glob
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PASSED_CONTROLLERS = [
    'adaptive_backstepping', 'adaptive_smc', 'backstepping_baseline',
    'dfbc_basic', 'dfbc_high_order_body_rate', 'dfbc_high_order',
    'dfbc_smooth_robust_body_rate', 'dfbc_smooth_robust',
    'explicit_gain_scheduled_mpc', 'feedback_linearization',
    'fuzzy_smc', 'h_2_state_feedback', 'ilqr', 'integral_smc',
    'lqg', 'lqi', 'lqr_baseline', 'mppi', 'ndi',
    'nonsingular_terminal_smc', 'official_pid',
    'official_pid_yaw_authority_mapped', 'passivity_based_control',
    'px4ctrl', 'robust_mpc', 'se_3_basic', 'terminal_smc', 'tube_mpc'
]

# Mapping from required CSV columns to MSR variable names
VAR_MAPPING = {
    'x': 'controller.position_mea[1]',
    'y': 'controller.position_mea[2]',
    'z': 'controller.position_mea[3]',
    'x_ref': 'controller.position_ref[1]',
    'y_ref': 'controller.position_ref[2]',
    'z_ref': 'controller.position_ref[3]',
    'vx': 'controller.velocity_mea[1]',
    'vy': 'controller.velocity_mea[2]',
    'vz': 'controller.velocity_mea[3]',
    'roll': 'controller.roll_mea',
    'pitch': 'controller.pitch_mea',
    'yaw': 'controller.yaw_mea',
    'u1': 'plant.physical.wrapper.motor_command[1]',
    'u2': 'plant.physical.wrapper.motor_command[2]',
    'u3': 'plant.physical.wrapper.motor_command[3]',
    'u4': 'plant.physical.wrapper.motor_command[4]',
}

BASE_PATH = r'C:\Users\HP\Desktop\MoSim\Results\control_platform\phase2_full_48_climbpath'


def parse_msr_structure(f):
    """Parse MSR file and build variable name to data mapping"""
    # Parse variable names (null-byte separated)
    name_bytes = bytes(f['Variable Name Table'][0])
    var_names = [n.decode('utf-8', errors='ignore')
                 for n in name_bytes.split(b'\x00')
                 if n]

    # Get animation data (has more columns and includes time series)
    anim_data = f['Animation Data Table'][:]
    anim_idx = f['Animation Index Table'][:]

    # Build mapping: variable name -> (data_array, column_index)
    var_to_data = {}

    # Parse animation index
    for i in range(anim_idx.shape[1]):
        var_num = anim_idx[2][i]
        col = anim_idx[1][i]

        if 0 <= var_num < len(var_names) and col < anim_data.shape[1]:
            name = var_names[var_num]
            var_to_data[name] = anim_data[:, col]

    return var_to_data, var_names


def export_msr_to_csv(msr_path, csv_path, verbose=False):
    """Read MSR (HDF5) and export to CSV"""
    try:
        with h5py.File(msr_path, 'r') as f:
            var_to_data, all_vars = parse_msr_structure(f)

            if verbose:
                print(f"\n  Total variables: {len(all_vars)}")
                print(f"  Variables with data: {len(var_to_data)}")

            # Get time array (column 0 of animation data)
            anim_data = f['Animation Data Table'][:]
            time_data = anim_data[:, 0]

            # Build DataFrame
            data_dict = {'time': time_data}

            if verbose:
                print(f"\n  Data length: {len(time_data)} rows")
                print(f"\n  Searching for required variables:")

            for csv_col, msr_var in VAR_MAPPING.items():
                if msr_var in var_to_data:
                    data_dict[csv_col] = var_to_data[msr_var]
                    if verbose:
                        print(f"    [OK] {csv_col:10s} <- {msr_var}")
                else:
                    # Use zeros as placeholder
                    data_dict[csv_col] = np.zeros(len(time_data))
                    if verbose:
                        print(f"    [--] {csv_col:10s} -> NOT FOUND (zeros)")

            # Create DataFrame
            df = pd.DataFrame(data_dict)

            # Ensure output directory exists
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)

            # Export to CSV
            df.to_csv(csv_path, index=False)

            print(f"  SUCCESS: {len(df)} rows -> {os.path.basename(csv_path)}")
            return True

    except Exception as e:
        print(f"  ERROR: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--explore':
        # Exploration mode
        controller = sys.argv[2] if len(sys.argv) > 2 else 'px4ctrl'
        controller_dir = os.path.join(BASE_PATH, controller)
        pattern = os.path.join(controller_dir, 'native_result_g6_*', '*', 'Result.msr')
        msr_files = glob.glob(pattern)

        if msr_files:
            msr_path = msr_files[0]
            print(f"\nExploring: {controller}")

            # Try export with verbose
            output_dir = os.path.join(controller_dir, 'raw')
            csv_path = os.path.join(output_dir, 'test_export.csv')
            export_msr_to_csv(msr_path, csv_path, verbose=True)
        else:
            print(f"No MSR file found for {controller}")
        return

    # Batch export mode
    success_count = 0
    fail_count = 0
    missing_count = 0

    print("Starting MSR to CSV batch export...")
    print("=" * 60)

    for controller in PASSED_CONTROLLERS:
        print(f"\n{controller}")

        # Find MSR file
        controller_dir = os.path.join(BASE_PATH, controller)
        pattern = os.path.join(controller_dir, 'native_result_g6_*', '*', 'Result.msr')
        msr_files = glob.glob(pattern)

        if not msr_files:
            print(f"  SKIP: No MSR file")
            missing_count += 1
            continue

        # Take the latest
        latest_msr = max(msr_files, key=os.path.getmtime)

        # Prepare output path
        output_dir = os.path.join(controller_dir, 'raw')
        csv_path = os.path.join(output_dir, 'climbpath50s.csv')

        # Export
        if export_msr_to_csv(latest_msr, csv_path):
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total:   {len(PASSED_CONTROLLERS)}")
    print(f"  Success: {success_count}")
    print(f"  Failed:  {fail_count}")
    print(f"  Missing: {missing_count}")


if __name__ == '__main__':
    main()
