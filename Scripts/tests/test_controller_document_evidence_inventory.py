from __future__ import annotations

import importlib.util
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts/quality/build_controller_document_evidence_inventory.py"
PID_BATCH = (
    ROOT
    / "Results/control_platform/controller_document_evidence_20260720/P1_PID"
    / "P1_PID_MWORKS_RESULT_SCREENSHOT_BATCH.json"
)
LINEAR_ROBUST_BATCH = (
    ROOT
    / "Results/control_platform/controller_document_evidence_20260720/P2_LINEAR_ROBUST"
    / "P2_LINEAR_ROBUST_MWORKS_RESULT_SCREENSHOT_BATCH.json"
)
SLIDING_MODE_BATCH = (
    ROOT
    / "Results/control_platform/controller_document_evidence_20260720/P3_SLIDING_MODE"
    / "P3_SLIDING_MODE_MWORKS_RESULT_SCREENSHOT_BATCH.json"
)
MPC_BATCH = (
    ROOT
    / "Results/control_platform/controller_document_evidence_20260720/P4_MPC"
    / "P4_MPC_MWORKS_RESULT_SCREENSHOT_BATCH.json"
)
ENHANCEMENT_BATCH = (
    ROOT
    / "Results/control_platform/controller_document_evidence_20260720/P5_ENHANCEMENT"
    / "P5_ENHANCEMENT_MWORKS_EVIDENCE_BATCH.json"
)
SAFETY_BATCH = (
    ROOT
    / "Results/control_platform/controller_document_evidence_20260720/P6_SAFETY"
    / "P6_SAFETY_MWORKS_EVIDENCE_BATCH.json"
)
FTC_BATCH = (
    ROOT
    / "Results/control_platform/controller_document_evidence_20260720/P7_FTC"
    / "P7_FTC_MWORKS_EVIDENCE_BATCH.json"
)


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


def test_pid_result_screenshot_batch_is_discoverable() -> None:
    builder = load_builder()
    inventory = builder.build_inventory(builder.DEFAULT_MATRIX)
    rows = {row["controller"]: row for row in inventory["rows"]}
    for controller in (
        "cascade_pid",
        "anti_windup",
        "feedforward_profile",
        "gain_scheduled_pid",
        "fuzzy_pid",
        "neural_pid",
    ):
        assert rows[controller]["result_viewer_screenshots"]


def test_pid_result_screenshots_match_manifest_hash_and_dimensions() -> None:
    batch = json.loads(PID_BATCH.read_text(encoding="utf-8"))
    assert batch["status"] == "passed"
    assert len(batch["rows"]) == 6
    for row in batch["rows"]:
        path = ROOT / row["screenshot"]
        payload = path.read_bytes()
        assert hashlib.sha256(payload).hexdigest().upper() == row["screenshot_sha256"]
        assert payload[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", payload[16:24])
        assert (width, height) == (1708, 921)
        assert row["historical_metric_match"] is True


def test_linear_robust_result_screenshot_batch_is_discoverable() -> None:
    builder = load_builder()
    inventory = builder.build_inventory(builder.DEFAULT_MATRIX)
    rows = {row["controller"]: row for row in inventory["rows"]}
    for controller in (
        "lqg",
        "feedback_linearization",
        "passivity_based_control",
        "adaptive_backstepping",
    ):
        assert rows[controller]["result_viewer_screenshots"]


def test_linear_robust_screenshots_match_manifest_hash_and_dimensions() -> None:
    batch = json.loads(LINEAR_ROBUST_BATCH.read_text(encoding="utf-8"))
    assert batch["status"] == "passed"
    assert len(batch["rows"]) == 4
    for row in batch["rows"]:
        path = ROOT / row["screenshot"]
        payload = path.read_bytes()
        assert hashlib.sha256(payload).hexdigest().upper() == row["screenshot_sha256"]
        assert payload[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", payload[16:24])
        assert (width, height) == (1708, 921)
        assert row["historical_metric_match"] is True


def test_sliding_mode_result_screenshot_batch_is_discoverable() -> None:
    builder = load_builder()
    inventory = builder.build_inventory(builder.DEFAULT_MATRIX)
    rows = {row["controller"]: row for row in inventory["rows"]}
    for controller in (
        "integral_smc",
        "terminal_smc",
        "nonsingular_terminal_smc",
        "super_twisting_smc",
        "adaptive_smc",
        "fuzzy_smc",
    ):
        assert rows[controller]["result_viewer_screenshots"]


def test_sliding_mode_screenshots_match_manifest_hash_and_dimensions() -> None:
    batch = json.loads(SLIDING_MODE_BATCH.read_text(encoding="utf-8"))
    assert batch["status"] == "passed"
    assert len(batch["rows"]) == 6
    for row in batch["rows"]:
        path = ROOT / row["screenshot"]
        payload = path.read_bytes()
        assert hashlib.sha256(payload).hexdigest().upper() == row["screenshot_sha256"]
        assert payload[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", payload[16:24])
        assert (width, height) == (1708, 921)
        assert row["historical_metric_match"] is True


def test_mpc_result_screenshot_batch_is_discoverable() -> None:
    builder = load_builder()
    inventory = builder.build_inventory(builder.DEFAULT_MATRIX)
    rows = {row["controller"]: row for row in inventory["rows"]}
    for controller in (
        "linear_mpc",
        "robust_mpc",
        "adaptive_mpc",
        "tube_mpc",
        "explicit_gain_scheduled_mpc",
        "ilqr",
        "mppi",
    ):
        assert rows[controller]["result_viewer_screenshots"]


def test_mpc_screenshots_match_manifest_hash_and_dimensions() -> None:
    batch = json.loads(MPC_BATCH.read_text(encoding="utf-8"))
    assert batch["status"] == "passed"
    assert len(batch["rows"]) == 7
    for row in batch["rows"]:
        path = ROOT / row["screenshot"]
        payload = path.read_bytes()
        assert hashlib.sha256(payload).hexdigest().upper() == row["screenshot_sha256"]
        assert payload[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", payload[16:24])
        assert (width, height) == (1708, 921)
        assert row["historical_metric_match"] is True


def test_enhancement_evidence_batch_is_discoverable() -> None:
    builder = load_builder()
    inventory = builder.build_inventory(builder.DEFAULT_MATRIX)
    rows = {row["controller"]: row for row in inventory["rows"]}
    for controller in (
        "l1_adaptive",
        "awff",
        "complete_adrc",
        "standardized_indi",
        "parameter_scheduling",
        "ilc",
    ):
        assert rows[controller]["graphical_model_screenshots"]
        assert rows[controller]["result_viewer_screenshots"]


def test_enhancement_evidence_matches_manifest_hash_and_dimensions() -> None:
    batch = json.loads(ENHANCEMENT_BATCH.read_text(encoding="utf-8"))
    assert batch["status"] == "passed_with_documented_limitations"
    assert len(batch["rows"]) == 6
    for row in batch["rows"]:
        for key, dimensions in (
            ("graphical_screenshot", (1800, 1000)),
            ("result_screenshot", (1708, 921)),
        ):
            path = ROOT / row[key]
            payload = path.read_bytes()
            assert hashlib.sha256(payload).hexdigest().upper() == row[f"{key}_sha256"]
            assert payload[:8] == b"\x89PNG\r\n\x1a\n"
            width, height = struct.unpack(">II", payload[16:24])
            assert (width, height) == dimensions
        assert row["check_model"] is True
        assert row["simulate_model"] is True


def test_safety_family_evidence_is_discoverable() -> None:
    builder = load_builder()
    inventory = builder.build_inventory(builder.DEFAULT_MATRIX)
    row = {item["controller"]: item for item in inventory["rows"]}[
        "safety_supervisor_family"
    ]
    assert row["graphical_model_screenshots"]
    assert row["result_viewer_screenshots"]
    assert not row["native_result_msr"]


def test_safety_family_evidence_matches_manifest_hash_and_dimensions() -> None:
    batch = json.loads(SAFETY_BATCH.read_text(encoding="utf-8"))
    assert batch["status"] == "passed_with_documented_boundaries"
    assert len(batch["family_modes"]) == 7
    assert batch["seven_mode_authorities"]["runtime_acknowledged_mode_count"] == 7
    cases = (
        (
            batch["graphical_fixture"]["screenshot"],
            batch["graphical_fixture"]["screenshot_sha256"],
            (1800, 1000),
        ),
        (
            batch["representative_execution"]["result_screenshot"],
            batch["representative_execution"]["result_screenshot_sha256"],
            (1708, 921),
        ),
    )
    for relative_path, expected_hash, expected_dimensions in cases:
        payload = (ROOT / relative_path).read_bytes()
        assert hashlib.sha256(payload).hexdigest().upper() == expected_hash
        assert payload[:8] == b"\x89PNG\r\n\x1a\n"
        assert struct.unpack(">II", payload[16:24]) == expected_dimensions
    assert batch["representative_execution"]["historical_mil_row_match"] is True


def test_ftc_family_report_evidence_matches_manifest() -> None:
    batch = json.loads(FTC_BATCH.read_text(encoding="utf-8"))
    assert batch["status"] == "passed_with_documented_boundaries"
    assert len(batch["family_modes"]) == 6
    assert batch["runtime_authority"]["effectiveness"] == 0.65
    assert batch["runtime_authority"]["generated_takeover_applied"] is True
    cases = (
        (
            batch["graphical_fixture"]["screenshot"],
            batch["graphical_fixture"]["screenshot_sha256"],
            (1800, 1000),
        ),
        (
            batch["representative_execution"]["result_screenshot"],
            batch["representative_execution"]["result_screenshot_sha256"],
            (1708, 921),
        ),
    )
    for relative_path, expected_hash, expected_dimensions in cases:
        payload = (ROOT / relative_path).read_bytes()
        assert hashlib.sha256(payload).hexdigest().upper() == expected_hash
        assert payload[:8] == b"\x89PNG\r\n\x1a\n"
        assert struct.unpack(">II", payload[16:24]) == expected_dimensions
    assert batch["native_result_msr"] is None


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
    test_pid_result_screenshot_batch_is_discoverable()
    test_pid_result_screenshots_match_manifest_hash_and_dimensions()
    test_linear_robust_result_screenshot_batch_is_discoverable()
    test_linear_robust_screenshots_match_manifest_hash_and_dimensions()
    test_sliding_mode_result_screenshot_batch_is_discoverable()
    test_sliding_mode_screenshots_match_manifest_hash_and_dimensions()
    test_mpc_result_screenshot_batch_is_discoverable()
    test_mpc_screenshots_match_manifest_hash_and_dimensions()
    test_enhancement_evidence_batch_is_discoverable()
    test_enhancement_evidence_matches_manifest_hash_and_dimensions()
    print("[OK] controller document evidence inventory tests")
