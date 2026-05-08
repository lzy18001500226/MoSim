#!/usr/bin/env python3
"""Regression checks for experiment summary generation."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    temp_dir = ROOT / ".tmp" / f"summary_{uuid4().hex}"
    try:
        csv_path = temp_dir / "experiment_summary.csv"
        md_path = temp_dir / "experiment_summary.md"
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "summarize_experiments.py"),
                "--csv",
                str(csv_path.relative_to(ROOT)),
                "--markdown",
                str(md_path.relative_to(ROOT)),
                "--include-metrics-glob",
                "results/metrics/smoke_*.json",
            ],
            cwd=ROOT,
            check=True,
        )
        with csv_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        if len(rows) < 6:
            raise AssertionError(f"Expected at least 6 scenario rows, got {len(rows)}")
        if not any(row["status"] == "pending" for row in rows):
            raise AssertionError("Expected pending scenarios before full baseline simulation")
        if not any(row["experiment_id"] == "smoke_official_example1_pid_baseline" for row in rows):
            raise AssertionError("Expected smoke metrics evidence row")
        if "Experiment Summary" not in md_path.read_text(encoding="utf-8"):
            raise AssertionError("Markdown summary header missing")
    finally:
        if temp_dir.exists():
            for item in sorted(temp_dir.glob("*"), reverse=True):
                item.unlink()
            temp_dir.rmdir()
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()

    print("[OK] experiment summary regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
