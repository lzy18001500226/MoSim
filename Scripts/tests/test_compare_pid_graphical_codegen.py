from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/compare_pid_graphical_codegen.py"
SPEC = importlib.util.spec_from_file_location("compare_pid_graphical_codegen", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_compare_accepts_matching_outputs(tmp_path: Path) -> None:
    csv_path = tmp_path / "mworks.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["time", *MODULE.OUTPUTS])
        writer.writeheader()
        writer.writerow({"time": 0.0, **{name: 1.0 for name in MODULE.OUTPUTS}})
    json_path = tmp_path / "codegen.json"
    json_path.write_text(json.dumps({"runtime_smoke": {"rows": [{"outputs": {name: 1.0 for name in MODULE.OUTPUTS}}]}}), encoding="utf-8")
    payload = MODULE.compare(csv_path, json_path, 1e-12)
    assert payload["behavior_equivalence_ok"] is True
    assert payload["sample_count"] == 1


def test_compare_rejects_output_drift(tmp_path: Path) -> None:
    csv_path = tmp_path / "mworks.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["time", *MODULE.OUTPUTS])
        writer.writeheader()
        writer.writerow({"time": 0.0, **{name: 1.0 for name in MODULE.OUTPUTS}})
    json_path = tmp_path / "codegen.json"
    json_path.write_text(json.dumps({"runtime_smoke": {"rows": [{"outputs": {name: 2.0 for name in MODULE.OUTPUTS}}]}}), encoding="utf-8")
    payload = MODULE.compare(csv_path, json_path, 1e-6)
    assert payload["behavior_equivalence_ok"] is False
