from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COLLECTOR = ROOT / "Scripts" / "quality" / "collect_runtime_evidence.py"
RUNTIME_LOG_PROFILES = ROOT / "Config" / "profiles" / "runtime_log_exports.json"
RUNTIME_LOG_PROFILE = "px4ctrl_runtime_log_export_v1"


def run_collector(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(COLLECTOR), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def write_run_manifest(run_dir: Path, experiment_id: str = "px4ctrl_takeoff_hover_land_v1") -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "RUN_MANIFEST.json").write_text(
        json.dumps(
            {
                "run_manifest": {
                    "run_id": run_dir.name,
                    "experiment_profile_id": experiment_id,
                    "evidence": {
                        "tracking_log": "tracking.csv",
                        "review": "review.md",
                        "screenshots": "screenshots/",
                        "logs": "logs/",
                    },
                }
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_reference(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "stamp,phase,ref_x,ref_y,ref_z",
                "0.00,takeoff,0,0,0.0",
                "0.10,hover,0,0,1.0",
                "0.20,hover,0,0,1.0",
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
                "0.01,0.001,0.000,0.000,0",
                "0.11,0.004,0.003,0.995,0",
                "0.19,0.003,0.002,0.998,0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_nonempty(path: Path, text: str) -> None:
    path.write_text(text + "\n", encoding="utf-8")


def test_collect_runtime_evidence_copies_artifacts_and_builds_tracking(tmp_path: Path) -> None:
    run_dir = tmp_path / "pytest_collect_runtime"
    write_run_manifest(run_dir)
    reference = tmp_path / "reference.csv"
    state = tmp_path / "state.csv"
    screenshot = tmp_path / "rviz.png"
    log = tmp_path / "ros.log"
    write_reference(reference)
    write_state(state)
    write_nonempty(screenshot, "png fixture bytes")
    write_nonempty(log, "ros log fixture")

    completed = run_collector(
        str(run_dir),
        "--runtime-log-profile",
        RUNTIME_LOG_PROFILE,
        "--artifact",
        f"reference_csv={reference}",
        "--artifact",
        f"state_csv={state}",
        "--artifact",
        f"rviz_screenshot={screenshot}",
        "--artifact",
        f"ros_log={log}",
        "--review-text",
        "px4ctrl runtime evidence reviewed.",
        "--build-tracking",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["runtime_log_profile"] == RUNTIME_LOG_PROFILE
    assert report["tracking"]["tracking_source_profile"] == "px4_mavros_fused_reference_state_csv_v1"
    assert report["tracking"]["aligned_rows"] == 3
    assert (run_dir / "runtime_log_manifest.json").is_file()
    assert (run_dir / "raw" / "reference.csv").is_file()
    assert (run_dir / "raw" / "state.csv").is_file()
    assert (run_dir / "screenshots" / "rviz_review.png").is_file()
    assert (run_dir / "logs" / "ros_runtime.log").is_file()
    assert (run_dir / "review.md").is_file()

    with (run_dir / "tracking.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[1]["phase"] == "hover"
    assert rows[1]["truth_z_m"] == "0.995"


def test_collect_runtime_evidence_rejects_missing_required_artifact(tmp_path: Path) -> None:
    run_dir = tmp_path / "pytest_collect_runtime_missing"
    write_run_manifest(run_dir)
    reference = tmp_path / "reference.csv"
    write_reference(reference)

    completed = run_collector(
        str(run_dir),
        "--runtime-log-profile",
        RUNTIME_LOG_PROFILE,
        "--artifact",
        f"reference_csv={reference}",
    )
    assert completed.returncode == 2
    assert "missing required artifact slot(s)" in completed.stderr


def test_collect_runtime_evidence_rejects_incompatible_profile(tmp_path: Path) -> None:
    run_dir = tmp_path / "pytest_collect_runtime_incompatible"
    write_run_manifest(run_dir, experiment_id="fastlio_independent_eval_figure8_v1")
    profiles = load_json(RUNTIME_LOG_PROFILES)
    profiles["profiles"][RUNTIME_LOG_PROFILE]["compatible_experiment_ids"] = ["px4ctrl_takeoff_hover_land_v1"]
    profiles_path = tmp_path / "runtime_log_exports.json"
    write_json(profiles_path, profiles)

    completed = run_collector(
        str(run_dir),
        "--runtime-log-profile",
        RUNTIME_LOG_PROFILE,
        "--runtime-log-profiles",
        str(profiles_path),
    )
    assert completed.returncode == 2
    assert "not compatible with experiment profile" in completed.stderr
