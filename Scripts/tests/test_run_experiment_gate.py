from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUN_GATE = ROOT / "Scripts" / "quality" / "run_experiment_gate.py"
VALID_PROFILE = ROOT / "Config" / "profiles" / "experiments" / "px4ctrl_takeoff_hover_land_v1.json"
FASTLIO_PROFILE = ROOT / "Config" / "profiles" / "experiments" / "fastlio_independent_eval_figure8_v1.json"
TRACKING_SOURCES = ROOT / "Config" / "profiles" / "tracking_sources.json"
TRACKING_PROFILE = "px4_mavros_fused_reference_state_csv_v1"
RUNTIME_LOG_PROFILE = "px4ctrl_runtime_log_export_v1"
FASTLIO_RUNTIME_LOG_PROFILE = "fastlio_eval_runtime_log_export_v1"


def run_gate(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUN_GATE), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def write_tracking(path: Path, high_error: bool = False) -> None:
    hover_z = "1.200" if high_error else "0.995"
    path.write_text(
        "\n".join(
            [
                "time_s,phase,ref_x_m,ref_y_m,ref_z_m,truth_x_m,truth_y_m,truth_z_m,saturated",
                "0.00,takeoff,0,0,0.0,0.000,0.000,0.000,0",
                "0.01,takeoff,0,0,0.5,0.005,0.000,0.490,0",
                f"0.02,hover,0,0,1.0,0.004,0.003,{hover_z},0",
                f"0.03,hover,0,0,1.0,0.004,0.003,{hover_z},0",
                f"0.04,hover,0,0,1.0,0.003,0.002,{hover_z},0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_reference(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "stamp,phase,ref_x,ref_y,ref_z",
                "0.00,takeoff,0,0,0.0",
                "0.01,takeoff,0,0,0.5",
                "0.02,hover,0,0,1.0",
                "0.03,hover,0,0,1.0",
                "0.04,hover,0,0,1.0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_state(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "stamp,x,y,z,saturated",
                "0.000,0.000,0.000,0.000,0",
                "0.012,0.005,0.000,0.490,0",
                "0.021,0.004,0.003,0.995,0",
                "0.031,0.004,0.003,0.995,0",
                "0.039,0.003,0.002,0.995,0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_evidence_files(tmp_path: Path) -> tuple[Path, Path]:
    screenshot = tmp_path / "rviz.png"
    log = tmp_path / "ros.log"
    screenshot.write_text("nonempty screenshot fixture\n", encoding="utf-8")
    log.write_text("nonempty log fixture\n", encoding="utf-8")
    return screenshot, log


def write_localization(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "stamp,seq,estimate_x,estimate_y,estimate_z,truth_x,truth_y,truth_z,estimate_vx,estimate_vy,estimate_vz,truth_vx,truth_vy,truth_vz,estimate_yaw_rad,truth_yaw_rad,delay_s",
                "0.00,20,0.000,0.000,0.000,0.000,0.000,0.000,0.00,0.00,0.00,0.00,0.00,0.00,0.000,0.000,0.010",
                "0.01,21,0.006,0.001,0.489,0.005,0.000,0.490,0.50,0.01,49.0,0.50,0.00,49.0,0.001,0.000,0.012",
                "0.02,22,0.005,0.004,0.994,0.004,0.003,0.995,0.00,0.01,50.5,0.00,0.00,50.5,0.002,0.000,0.011",
                "0.03,23,0.005,0.004,0.994,0.004,0.003,0.995,0.00,0.00,0.0,0.00,0.00,0.0,0.002,0.000,0.010",
                "0.04,24,0.004,0.003,0.994,0.003,0.002,0.995,0.00,0.00,0.0,0.00,0.00,0.0,0.002,0.000,0.010",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_map_summary(path: Path) -> None:
    path.write_text('{"map_completeness": 0.91}\n', encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_run_experiment_gate_prepare_only_materializes_packet(tmp_path: Path) -> None:
    run_id = "pytest_run_gate_prepare_only"
    completed = run_gate(
        str(VALID_PROFILE),
        "--run-id",
        run_id,
        "--output-root",
        str(tmp_path),
        "--prepare-only",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    run_dir = tmp_path / run_id
    assert report["ok"] is True
    assert report["prepare_only"] is True
    assert report["runtime_started"] is False
    assert (run_dir / "RUN_MANIFEST.json").is_file()
    assert (run_dir / "source_hashes.json").is_file()
    assert not (run_dir / "metrics.json").exists()


def test_run_experiment_gate_rejects_standard_tracking_without_runtime_log_manifest(tmp_path: Path) -> None:
    run_id = "pytest_run_gate_standard_without_runtime_manifest"
    tracking = tmp_path / "tracking_input.csv"
    write_tracking(tracking)
    screenshot, log = write_evidence_files(tmp_path)

    completed = run_gate(
        str(VALID_PROFILE),
        "--run-id",
        run_id,
        "--output-root",
        str(tmp_path),
        "--tracking-csv",
        str(tracking),
        "--review-text",
        "px4ctrl takeoff hover land evidence review.",
        "--screenshot",
        str(screenshot),
        "--log",
        str(log),
    )
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["accepted"] is False
    evidence_errors = report["stages"]["evidence_gate"]["errors"]
    assert any(error["code"] in {"R-ARTIFACT-01", "R-RUNTIME-JSON-01"} for error in evidence_errors)


def test_run_experiment_gate_accepts_reference_state_logs(tmp_path: Path) -> None:
    run_id = "pytest_run_gate_reference_state"
    reference = tmp_path / "reference.csv"
    state = tmp_path / "state.csv"
    write_reference(reference)
    write_state(state)
    screenshot, log = write_evidence_files(tmp_path)

    completed = run_gate(
        str(VALID_PROFILE),
        "--run-id",
        run_id,
        "--output-root",
        str(tmp_path),
        "--reference-csv",
        str(reference),
        "--state-csv",
        str(state),
        "--tracking-source-profile",
        TRACKING_PROFILE,
        "--runtime-log-profile",
        RUNTIME_LOG_PROFILE,
        "--review-text",
        "px4ctrl takeoff hover land evidence review.",
        "--screenshot",
        str(screenshot),
        "--log",
        str(log),
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    run_dir = tmp_path / run_id
    assert report["accepted"] is True
    assert report["stages"]["tracking"]["mode"] == "collect_runtime_export_profile"
    assert report["stages"]["tracking"]["report"]["tracking"]["tracking_source_profile"] == TRACKING_PROFILE
    assert (run_dir / "tracking_alignment_report.json").is_file()
    assert (run_dir / "runtime_export_manifest.json").is_file()
    assert (run_dir / "runtime_log_manifest.json").is_file()


def test_run_experiment_gate_rejects_incompatible_tracking_source_profile(tmp_path: Path) -> None:
    run_id = "pytest_run_gate_incompatible_tracking_source"
    reference = tmp_path / "reference.csv"
    state = tmp_path / "state.csv"
    write_reference(reference)
    write_state(state)
    tracking_sources = json.loads(TRACKING_SOURCES.read_text(encoding="utf-8"))
    tracking_sources["profiles"][TRACKING_PROFILE]["compatible_experiment_ids"] = ["px4ctrl_takeoff_hover_land_v1"]
    tracking_sources_path = tmp_path / "tracking_sources.json"
    write_json(tracking_sources_path, tracking_sources)

    completed = run_gate(
        str(FASTLIO_PROFILE),
        "--run-id",
        run_id,
        "--output-root",
        str(tmp_path),
        "--reference-csv",
        str(reference),
        "--state-csv",
        str(state),
        "--tracking-source-profile",
        TRACKING_PROFILE,
        "--tracking-sources",
        str(tracking_sources_path),
    )
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["accepted"] is False
    assert "not compatible with experiment profile" in report["errors"][0]["message"]


def test_run_experiment_gate_rejects_threshold_failure(tmp_path: Path) -> None:
    run_id = "pytest_run_gate_threshold_fail"
    tracking = tmp_path / "tracking_input.csv"
    write_tracking(tracking, high_error=True)
    screenshot, log = write_evidence_files(tmp_path)

    completed = run_gate(
        str(VALID_PROFILE),
        "--run-id",
        run_id,
        "--output-root",
        str(tmp_path),
        "--tracking-csv",
        str(tracking),
        "--review-text",
        "px4ctrl takeoff hover land evidence review.",
        "--screenshot",
        str(screenshot),
        "--log",
        str(log),
    )
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["accepted"] is False
    assert report["threshold_accepted"] is False
    assert any(error["code"] == "T-FAIL-01" for error in report["stages"]["threshold"]["errors"])


def test_run_experiment_gate_accepts_fastlio_eval_localization_packet(tmp_path: Path) -> None:
    run_id = "pytest_run_gate_fastlio_eval"
    reference = tmp_path / "reference.csv"
    state = tmp_path / "state.csv"
    localization = tmp_path / "localization.csv"
    map_summary = tmp_path / "map_summary.json"
    write_reference(reference)
    write_state(state)
    write_localization(localization)
    write_map_summary(map_summary)
    screenshot, log = write_evidence_files(tmp_path)

    completed = run_gate(
        str(FASTLIO_PROFILE),
        "--run-id",
        run_id,
        "--output-root",
        str(tmp_path),
        "--reference-csv",
        str(reference),
        "--state-csv",
        str(state),
        "--localization-csv",
        str(localization),
        "--map-summary-json",
        str(map_summary),
        "--runtime-log-profile",
        FASTLIO_RUNTIME_LOG_PROFILE,
        "--review-text",
        "FAST-LIO eval-only evidence reviewed; controller state remains PX4/MAVROS fused.",
        "--screenshot",
        str(screenshot),
        "--log",
        str(log),
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    run_dir = tmp_path / run_id
    assert report["accepted"] is True
    assert report["threshold_accepted"] is True
    assert (run_dir / "raw" / "localization.csv").is_file()
    assert (run_dir / "raw" / "map_summary.json").is_file()
    metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    assert "ate" in metrics["metrics"]
    assert "rmse" not in metrics["metrics"]
