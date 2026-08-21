#!/usr/bin/env python3
"""Convert planning CSV to Sysplorer CombiTimeTable format."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT / "Results/planning/three_uav_open_blocks_mworks_20260720/raw"
OUTPUT_DIR = ROOT / "Results/planning/three_uav_open_blocks_mworks_20260720/sysplorer"

def convert_csv(input_path: Path, output_path: Path):
    """Convert standard CSV to Sysplorer format."""
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        data_rows = list(reader)

    rows = len(data_rows)
    cols = len(header)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('#1\n')
        f.write(f'double tab1({rows},{cols})\n')
        for row in data_rows:
            f.write(','.join(row) + '\n')

    print(f"Converted {input_path.name}: {rows} rows x {cols} cols")

def main():
    for uav_id in [1, 2, 3]:
        input_file = INPUT_DIR / f"uav{uav_id}_reference.csv"
        output_file = OUTPUT_DIR / f"uav{uav_id}_reference.csv"
        convert_csv(input_file, output_file)

    print(f"\nOutput directory: {OUTPUT_DIR}")

if __name__ == '__main__':
    main()
