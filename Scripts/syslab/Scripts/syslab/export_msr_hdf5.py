#!/usr/bin/env python
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

REQUIRED_VARS = ['time', 'x', 'y', 'z', 'x_ref', 'y_ref', 'z_ref',
                 'vx', 'vy', 'vz', 'roll', 'pitch', 'yaw',
                 'u1', 'u2', 'u3', 'u4']

BASE_PATH = r'C:\Users\HP\Desktop\MoSim\Results\control_platform\phase2_full_48_climbpath'


def parse_variable_names(f):
    """Parse variable names from MSR file"""
    # Get variable name table (stored as int8 array)
    name_table = f['Variable Name Table'][0]
    name_str = ''.join(chr(c) for c in name_table if c != 0)

    # Split by null terminators or newlines
    names = [n.strip() for n in name_str.split('\x00') if n.strip()]

    # Get variable index table
    index_table = f['Variable Index Table']

    return names, index_table


def find_variable_column(var_name, names, index_table):
    """Find the column index for a variable in the data table"""
    # Try exact match first
    if var_name in names:
        idx = names.index(var_name)
        # index_table[1] contains the column index in data table
        return index_table[1][idx]

    # Try partial match
    for i, name in enumerate(names):
        if var_name in name or name.endswith('.' + var_name):
            return index_table[1][i]

    return None


def export_msr_to_csv(msr_path, csv_path, verbose=False):
    """Read MSR (HDF5) and export to CSV"""
    try:
        with h5py.File(msr_path, 'r') as f:
            # Parse variable names
            names, index_table = parse_variable_names(f)

            if verbose:
                print(f"  Found {len(names)} variables")
                # Print first 20 variables
                print(f"  Sample variables: {names[:20]}")

            # Get continuous data (time-series data)
            data_table = f['Continuous Data Table'][:]

            if verbose:
                print(f"  Data shape: {data_table.shape}")

            # Build DataFrame
            data_dict = {}

            for var in REQUIRED_VARS:
                col_idx = find_variable_column(var, names, index_table)

                if col_idx is not None and col_idx < data_table.shape[1]:
                    data_dict[var] = data_table[:, col_idx]
                    if verbose:
                        print(f"  ✓ {var}: column {col_idx}")
                else:
                    # Use zeros as placeholder
                    if 'time' in data_dict:
                        data_dict[var] = np.zeros(data_table.shape[0])
                    if verbose:
                        print(f"  ✗ {var}: NOT FOUND, using zeros")

            # Create DataFrame
            df = pd.DataFrame(data_dict)

            # Ensure output directory exists
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)

            # Export to CSV
            df.to_csv(csv_path, index=False)

            print(f"  SUCCESS: Exported {len(df)} rows to {os.path.basename(csv_path)}")
            return True

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--explore':
        # Exploration mode with verbose output
        controller = sys.argv[2] if len(sys.argv) > 2 else 'px4ctrl'
        controller_dir = os.path.join(BASE_PATH, controller)
        pattern = os.path.join(controller_dir, 'native_result_g6_*', '*', 'Result.msr')
        msr_files = glob.glob(pattern)

        if msr_files:
            msr_path = msr_files[0]
            print(f"\nExploring: {msr_path}\n")

            with h5py.File(msr_path, 'r') as f:
                names, index_table = parse_variable_names(f)
                print(f"Total variables: {len(names)}\n")
                print("First 50 variables:")
                for i, name in enumerate(names[:50]):
                    print(f"  [{i}] {name}")

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

    print("Starting MSR to CSV batch export via HDF5...")
    print("=" * 60)

    for controller in PASSED_CONTROLLERS:
        print(f"\nProcessing: {controller}")

        # Find MSR file
        controller_dir = os.path.join(BASE_PATH, controller)
        pattern = os.path.join(controller_dir, 'native_result_g6_*', '*', 'Result.msr')
        msr_files = glob.glob(pattern)

        if not msr_files:
            print(f"  ERROR: No MSR file found")
            fail_count += 1
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
    print("Export summary:")
    print(f"  Total: {len(PASSED_CONTROLLERS)}")
    print(f"  Success: {success_count}")
    print(f"  Failed: {fail_count}")


if __name__ == '__main__':
    main()
