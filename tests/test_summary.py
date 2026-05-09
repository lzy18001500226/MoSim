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
            raise AssertionError(f"Expected at least 6 real evidence rows, got {len(rows)}")
        if "evidence_level" not in rows[0]:
            raise AssertionError("Expected evidence_level column")
        if not any(row["evidence_level"] == "real_sysplorer_mcp_full_baseline" for row in rows):
            raise AssertionError("Expected full baseline Sysplorer MCP evidence")
        if any(row["source"] == "offline_script" for row in rows):
            raise AssertionError("Offline script evidence should not be included in the real evidence summary")
        if any(row["evidence_level"].startswith("offline_") for row in rows):
            raise AssertionError("Offline evidence levels should not be included in the real evidence summary")
        markdown = md_path.read_text(encoding="utf-8")
        if "Experiment Summary" not in markdown:
            raise AssertionError("Markdown summary header missing")
        if "Evidence Levels" not in markdown:
            raise AssertionError("Markdown evidence section missing")
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
