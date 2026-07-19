from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts/quality/build_controller_document_evidence_inventory.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "build_controller_document_evidence_inventory", BUILDER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load controller document evidence builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_current_matrix_inventory_has_67_unique_routes() -> None:
    builder = load_builder()
    inventory = builder.build_inventory(builder.DEFAULT_MATRIX)
    summary = inventory["summary"]
    assert summary["row_count"] == 67
    assert summary["unique_controller_count"] == 67
    assert summary["matrix_status_counts"] == {
        "accepted": 27,
        "executed_blocked": 33,
        "not_run": 7,
    }
    assert len(inventory["rows"]) == 67
    assert all(row["next_action"] for row in inventory["rows"])


def test_known_implementation_gaps_remain_blocked() -> None:
    builder = load_builder()
    inventory = builder.build_inventory(builder.DEFAULT_MATRIX)
    rows = {row["controller"]: row for row in inventory["rows"]}
    assert rows["mu_synthesis"]["implementation_blocked"] is True
    assert rows["neural_smc"]["implementation_blocked"] is True
    assert rows["mu_synthesis"]["next_action"] == "bounded_implementation_gap_review"
    assert rows["neural_smc"]["next_action"] == "bounded_implementation_gap_review"


def test_missing_native_result_is_not_promoted() -> None:
    builder = load_builder()
    inventory = builder.build_inventory(builder.DEFAULT_MATRIX)
    for row in inventory["rows"]:
        if not row["native_result_msr"]:
            assert "native_result_msr_live_confirmation" in row["missing_evidence"]


def test_only_exact_certified_profiles_bind_native_results() -> None:
    builder = load_builder()
    inventory = builder.build_inventory(builder.DEFAULT_MATRIX)
    rows = {row["controller"]: row for row in inventory["rows"]}
    for controller in ("official_pid", "pid_indi", "linear_mpc", "awff"):
        assert rows[controller]["native_result_msr"]
    assert not rows["formation_cbf"]["native_result_msr"]
    assert not rows["safety_supervisor_family"]["native_result_msr"]
    assert not rows["fdi_ftc_family"]["native_result_msr"]


def test_cli_writes_json_and_markdown(tmp_path: Path) -> None:
    completed = subprocess.run(
        [sys.executable, str(BUILDER), "--output-dir", str(tmp_path)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["row_count"] == 67
    assert (tmp_path / "CONTROLLER_DOCUMENT_EVIDENCE_INVENTORY.json").is_file()
    assert (tmp_path / "CONTROLLER_DOCUMENT_EVIDENCE_INVENTORY.md").is_file()


if __name__ == "__main__":
    test_current_matrix_inventory_has_67_unique_routes()
    test_known_implementation_gaps_remain_blocked()
    test_missing_native_result_is_not_promoted()
    test_only_exact_certified_profiles_bind_native_results()
    print("[OK] controller document evidence inventory tests")
