from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/mworks/verify_official_pid_golden_equivalence.py"
SPEC = importlib.util.spec_from_file_location("official_pid_golden_equivalence", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _write_csv(path: Path, times: list[float], value_scale: float) -> None:
    fields = ["time", *MODULE.COMPARISON_FIELDS]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for time in times:
            row = {"time": time}
            for index, field in enumerate(MODULE.COMPARISON_FIELDS, start=1):
                row[field] = value_scale * index * time
            writer.writerow(row)


def test_aligned_result_exports_pass(tmp_path: Path) -> None:
    golden_path = tmp_path / "golden.csv"
    formal_path = tmp_path / "formal.csv"
    _write_csv(golden_path, [0.0, 0.01, 0.02], 1.0)
    _write_csv(formal_path, [0.0, 0.002, 0.004, 0.006, 0.008, 0.01, 0.012, 0.014, 0.016, 0.018, 0.02], 1.0)

    summary = MODULE.run_comparison(golden_path, formal_path)

    assert summary["status"] == "pass", summary["failures"]
    assert summary["formal_decimation_stride"] == 5
    assert summary["time_alignment_max_abs_s"] == 0.0


def test_misaligned_result_exports_fail(tmp_path: Path) -> None:
    golden_path = tmp_path / "golden.csv"
    formal_path = tmp_path / "formal.csv"
    _write_csv(golden_path, [0.0, 0.01, 0.02], 1.0)
    _write_csv(formal_path, [0.0, 0.002, 0.004, 0.006, 0.008, 0.011, 0.012, 0.014, 0.016, 0.018, 0.02], 1.0)

    summary = MODULE.run_comparison(golden_path, formal_path)

    assert summary["status"] == "fail"
    assert any("time axes differ" in failure for failure in summary["failures"])
