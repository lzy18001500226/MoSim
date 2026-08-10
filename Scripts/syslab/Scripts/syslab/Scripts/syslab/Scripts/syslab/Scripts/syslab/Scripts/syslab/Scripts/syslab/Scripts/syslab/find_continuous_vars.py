#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Find actual continuous variables"""

import h5py

msr_path = r'C:\Users\HP\Desktop\MoSim\Results\control_platform\phase2_full_48_climbpath\px4ctrl\native_result_g6_20260729_053256_034264\Px4CtrlFormalRunner\Result.msr'

with h5py.File(msr_path, 'r') as f:
    # Get variable names
    name_bytes = bytes(f['Variable Name Table'][0])
    name_str = name_bytes.decode('utf-8', errors='ignore')
    var_names = [n.strip() for n in name_str.split() if n.strip()]

    print(f"Total variable names: {len(var_names)}")

    # Get index table
    idx = f['Variable Index Table'][:]

    # Get continuous data shape
    data = f['Continuous Data Table'][:]
    print(f"Continuous data shape: {data.shape}")

    # Find continuous variables (type 1) with valid column indices
    print(f"\nContinuous variables (datacol < {data.shape[1]}):")

    continuous_vars = []
    for i in range(idx.shape[1]):
        var_type = idx[0][i]
        datacol = idx[1][i]
        var_num = idx[2][i] - 1  # Convert to 0-indexed

        if var_type == 1 and datacol < data.shape[1] and 0 <= var_num < len(var_names):
            continuous_vars.append((var_names[var_num], datacol))

    print(f"Found {len(continuous_vars)} continuous variables")
    print("\nFirst 30:")
    for name, col in continuous_vars[:30]:
        print(f"  [col {col:3d}] {name}")

    # Search for required variables
    print("\nSearching for required variables:")
    required = ['time', 'x', 'y', 'z', 'x_ref', 'y_ref', 'z_ref',
                'vx', 'vy', 'vz', 'roll', 'pitch', 'yaw',
                'u1', 'u2', 'u3', 'u4']

    for req in required:
        found = [(name, col) for name, col in continuous_vars if req in name.lower()]
        if found:
            print(f"  {req:10s}: {found[0]}")
        else:
            print(f"  {req:10s}: NOT FOUND")
