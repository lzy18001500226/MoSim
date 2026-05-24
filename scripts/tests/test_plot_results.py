#!/usr/bin/env python3
"""Regression checks for report figure generation."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]


def remove_tree(path: Path) -> None:
    if not path.exists():
        return
    for item in sorted(path.glob("**/*"), key=lambda value: len(value.parts), reverse=True):
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            item.rmdir()
    path.rmdir()


def test_plot_results_generates_fault_diagnostics() -> None:
    temp_dir = ROOT / ".tmp" / f"plot_{uuid4().hex}"
    try:
        raw = temp_dir / "raw.csv"
        metrics = temp_dir / "metrics.json"
        figures = temp_dir / "figures"
        temp_dir.mkdir(parents=True)
        with raw.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(
                [
                    "time",
                    "x",
                    "y",
                    "z",
                    "x_ref",
                    "y_ref",
                    "z_ref",
                    "eta_hat1",
                    "eta_hat2",
                    "eta_hat3",
                    "eta_hat4",
                    "fault_index",
                ]
            )
            for index in range(11):
                t = index * 0.1
                writer.writerow([t, t, 0, 1, t, 0, 1, 1 - 0.01 * index, 1, 1, 1, 1 if index >= 3 else 0])
        metrics.write_text(
            json.dumps(
                {
                    "position_rmse_m": 0.01,
                    "max_position_error_m": 0.02,
                    "steady_state_error_m": 0.01,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "results" / "plot_results.py"),
                str(raw),
                str(figures),
                "--metrics",
                str(metrics),
                "--title-prefix",
                "fixture",
                "--file-prefix",
                "fixture",
            ],
            cwd=ROOT,
            check=True,
        )
        expected = [
            "fixture_eta_hat_diagnostics.svg",
            "fixture_fault_index_diagnostics.svg",
            "fixture_figure_manifest.md",
        ]
        missing = [name for name in expected if not (figures / name).exists()]
        if missing:
            raise AssertionError(f"Missing generated figures: {', '.join(missing)}")
        manifest = (figures / "fixture_figure_manifest.md").read_text(encoding="utf-8")
        for name in expected[:2]:
            if name not in manifest:
                raise AssertionError(f"Manifest missing {name}")
    finally:
        remove_tree(temp_dir)
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()
