from __future__ import annotations

import csv
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/compare_pid_variant_graphical_mil.py"
SPEC = importlib.util.spec_from_file_location("compare_pid_variant_graphical_mil", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_variant(path: Path, value: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["time", *MODULE.OUTPUTS], lineterminator="\n")
        writer.writeheader()
        for index in range(11):
            writer.writerow({"time": index * 0.01, **{name: value for name in MODULE.OUTPUTS}})


def test_compare_accepts_matching_six_variant_trajectories(tmp_path: Path) -> None:
    reference = tmp_path / "reference"
    graphical = tmp_path / "graphical"
    for algorithm_id in MODULE.ALGORITHMS:
        write_variant(reference / f"{algorithm_id}.csv", 1.0)
        write_variant(graphical / f"{algorithm_id}.csv", 1.0)
    payload = MODULE.compare(reference, graphical, 1e-12)
    assert payload["six_variant_graphical_equivalence"] is True


def test_compare_rejects_one_drifting_variant(tmp_path: Path) -> None:
    reference = tmp_path / "reference"
    graphical = tmp_path / "graphical"
    for algorithm_id in MODULE.ALGORITHMS:
        write_variant(reference / f"{algorithm_id}.csv", 1.0)
        write_variant(graphical / f"{algorithm_id}.csv", 2.0 if algorithm_id == "fuzzy_pid" else 1.0)
    payload = MODULE.compare(reference, graphical, 1e-6)
    assert payload["six_variant_graphical_equivalence"] is False
    assert payload["variants"]["fuzzy_pid"]["behavior_equivalence_ok"] is False
