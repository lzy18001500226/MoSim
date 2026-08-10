#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Detailed HDF5 structure inspector"""

import h5py
import sys

msr_path = r'C:\Users\HP\Desktop\MoSim\Results\control_platform\phase2_full_48_climbpath\px4ctrl\native_result_g6_20260729_053256_034264\Px4CtrlFormalRunner\Result.msr'

with h5py.File(msr_path, 'r') as f:
    print("=== Variable Index Table ===")
    idx = f['Variable Index Table'][:]
    print(f"Shape: {idx.shape}")
    print(f"\nRow 0 (type): {idx[0, :20]}")
    print(f"Row 1 (datacol): {idx[1, :20]}")
    print(f"Row 2 (namepos): {idx[2, :20]}")
    print(f"Row 3 (???): {idx[3, :20]}")

    print("\n=== Try to find 'time' variable ===")
    name_bytes = bytes(f['Variable Name Table'][0])
    name_str = name_bytes.decode('utf-8', errors='ignore')

    # Show where 'time' appears in the string
    time_pos = name_str.find('time')
    if time_pos >= 0:
        print(f"'time' found at byte position: {time_pos}")
        print(f"Context: ...{name_str[max(0, time_pos-30):time_pos+50]}...")

        # Find which index entry points to this
        for i in range(idx.shape[1]):
            if idx[2][i] == time_pos or idx[2][i] == time_pos + 1:
                print(f"\nIndex entry {i}:")
                print(f"  type={idx[0][i]}, datacol={idx[1][i]}, namepos={idx[2][i]}, len/end={idx[3][i]}")
