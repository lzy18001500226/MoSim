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


def explore_hdf5_structure(msr_path):
    """Explore HDF5 file structure to find data location"""
    print(f"\n=== Exploring {os.path.basename(os.path.dirname(msr_path))} ===")

    try:
        with h5py.File(msr_path, 'r') as f:
            print(f"Top-level keys: {list(f.keys())}")

            def print_structure(name, obj):
                if isinstance(obj, h5py.Dataset):
                    print(f"  Dataset: {name}, shape: {obj.shape}, dtype: {obj.dtype}")
                elif isinstance(obj, h5py.Group):
                    print(f"  Group: {name}")

            f.visititems(print_structure)
            return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def export_msr_to_csv(msr_path, csv_path):
    """Read MSR (HDF5) and export to CSV"""
    try:
        with h5py.File(msr_path, 'r') as f:
            # Try to find data - common locations in MWORKS MSR files
            data_dict = {}

            # Explore to find variables
            for var in REQUIRED_VARS:
                # Try common patterns
                possible_paths = [
                    var,
                    f'data/{var}',
                    f'results/{var}',
                    f'variables/{var}',
                    f'{var}/data',
                ]

                found = False
                for path in possible_paths:
                    if path in f:
                        data_dict[var] = f[path][:]
                        found = True
                        break

                if not found:
                    print(f"  WARNING: Variable '{var}' not found, using zeros")
                    # Use zeros as placeholder
                    if 'time' in data_dict:
                        data_dict[var] = np.zeros_like(data_dict['time'])

            # Check if we have any data
            if not data_dict:
                print(f"  ERROR: No data found in MSR file")
                return False

            # Create DataFrame
            df = pd.DataFrame(data_dict)

            # Ensure output directory exists
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)

            # Export to CSV
            df.to_csv(csv_path, index=False)

            print(f"  SUCCESS: Exported {len(df)} rows to {csv_path}")
            return True

    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--explore':
        # Exploration mode
        controller = sys.argv[2] if len(sys.argv) > 2 else 'px4ctrl'
        controller_dir = os.path.join(BASE_PATH, controller)
        pattern = os.path.join(controller_dir, 'native_result_g6_*', '*', 'Result.msr')
        msr_files = glob.glob(pattern)

        if msr_files:
            explore_hdf5_structure(msr_files[0])
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
        print(f"  MSR: {latest_msr}")

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
