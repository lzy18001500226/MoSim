#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick HDF5 structure inspector"""

import h5py
import sys

msr_path = r'C:\Users\HP\Desktop\MoSim\Results\control_platform\phase2_full_48_climbpath\px4ctrl\native_result_g6_20260729_053256_034264\Px4CtrlFormalRunner\Result.msr'

with h5py.File(msr_path, 'r') as f:
    print("=== Variable Index Table ===")
    idx = f['Variable Index Table'][:]
    print(f"Shape: {idx.shape}")
    print(f"First 10 columns:")
    for i in range(min(10, idx.shape[1])):
        print(f"  Col {i}: type={idx[0][i]}, datacol={idx[1][i]}, namepos={idx[2][i]}")

    print("\n=== Variable Name Table ===")
    names = f['Variable Name Table'][0]
    print(f"Length: {len(names)}")
    print(f"First 500 bytes as string:")
    print(bytes(names[:500]).decode('utf-8', errors='replace'))

    print("\n=== Continuous Data Table ===")
    data = f['Continuous Data Table'][:]
    print(f"Shape: {data.shape}")
    print(f"First row (first 10 values): {data[0, :10]}")
