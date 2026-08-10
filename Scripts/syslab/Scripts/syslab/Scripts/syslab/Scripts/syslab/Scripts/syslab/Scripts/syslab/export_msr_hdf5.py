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

REQUIRED_VARS = ['time', 'x', 'y', 'z', 'x_ref', 'y_ref', 'z_ref',
                 'vx', 'vy', 'vz', 'roll', 'pitch', 'yaw',
                 'u1', 'u2', 'u3', 'u4']

BASE_PATH = r'C:\Users\HP\Desktop\MoSim\Results\control_platform\phase2_full_48_climbpath'


def parse_variable_info(f):
    """Parse variable names and column mapping from MSR file"""
    # Get the raw bytes and decode
    name_bytes = bytes(f['Variable Name Table'][0])
    name_str = name_bytes.decode('utf-8', errors='ignore')

    # Split by spaces to get individual variable names
    var_names = [n.strip() for n in name_str.split() if n.strip()]

    # Get index table
    # Row 0: variable type
    # Row 1: column index in data table
    # Row 2: variable number (1-indexed)
    index_table = f['Variable Index Table'][:]

    # Build variable info list
    var_info = []
    for i in range(index_table.shape[1]):
        var_type = int(index_table[0][i])
        col_idx = int(index_table[1][i])
        var_num = int(index_table[2][i])

        # var_num is 1-indexed, convert to 0-indexed for array access
        name_idx = var_num - 1

        if 0 <= name_idx < len(var_names):
            var_info.append({
                'name': var_names[name_idx],
                'type': var_type,
                'col': col_idx
            })

    return var_info


def find_variable(var_name, var_info, var_type=1):
    """Find variable info by name (type 1 = continuous)"""
    # Filter by type first
    candidates = [v for v in var_info if v['type'] == var_type]

    # Try exact match
    for v in candidates:
        if v['name'] == var_name:
            return v

    # Try suffix match (e.g., "quadrotor.x" matches "x")
    for v in candidates:
        if v['name'].endswith('.' + var_name):
            return v

    # Try contains
    for v in candidates:
        if var_name.lower() in v['name'].lower():
            return v

    return None


def export_msr_to_csv(msr_path, csv_path, verbose=False):
    """Read MSR (HDF5) and export to CSV"""
    try:
        with h5py.File(msr_path, 'r') as f:
            # Parse variable info
            var_info = parse_variable_info(f)

            if verbose:
                print(f"\n  Total variables: {len(var_info)}")
                # Show continuous variables
                cont_vars = [v for v in var_info if v['type'] == 1]
                print(f"  Continuous variables: {len(cont_vars)}")
                print(f"\n  Sample continuous variables:")
                for v in cont_vars[:20]:
                    print(f"    [col {v['col']:3d}] {v['name']}")

            # Get continuous data table
            data_table = f['Continuous Data Table'][:]

            if verbose:
                print(f"\n  Data table shape: {data_table.shape}")
                print(f"\n  Searching for required variables:")

            # Build DataFrame
            data_dict = {}

            for req_var in REQUIRED_VARS:
                var = find_variable(req_var, var_info, var_type=1)

                if var and var['col'] < data_table.shape[1]:
                    data_dict[req_var] = data_table[:, var['col']]
                    if verbose:
                        print(f"    [OK] {req_var:10s} -> col {var['col']:3d} ({var['name']})")
                else:
                    # Use zeros as placeholder
                    data_dict[req_var] = np.zeros(data_table.shape[0])
                    if verbose:
                        print(f"    [--] {req_var:10s} -> NOT FOUND (zeros)")

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
