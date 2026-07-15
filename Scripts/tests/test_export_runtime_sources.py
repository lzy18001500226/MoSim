from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPORTER = ROOT / "Scripts" / "quality" / "export_runtime_sources.py"
RUNTIME_EXPORT_PROFILE = "sunray_px4ctrl_runtime_export_v1"


def run_exporter(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(EXPORTER), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_run_manifest(
    run_dir: Path,
    *,
    experiment_id: str = "px4ctrl_takeoff_hover_land_v1",
    runtime_export_profile: str = RUNTIME_EXPORT_PROFILE,
) -> None:
    write_json(
        run_dir / "RUN_MANIFEST.json",
        {
            "run_manifest": {
                "run_id": run_dir.name,
                "experiment_profile_id": experiment_id,
                "runtime": {
                    "runtime_profile": "sunray_ros1_gazebo_classic_v1",
                    "os": "ubuntu-20.04",
                    "ros": "noetic",
                    "gazebo": "classic",
                },
                "runtime_export": {
                    "runtime_export_profile": runtime_export_profile,
                    "runtime_log_profile": "px4ctrl_runtime_log_export_v1",
                    "tracking_source_profile": "px4_mavros_fused_reference_state_csv_v1",
                    "required_artifact_slots": [
                        "reference_csv",
                        "state_csv",
                        "rviz_screenshot",
                        "ros_log",
                    ],
                },
                "evidence": {
                    "tracking_log": "tracking.csv",
                    "review": "review.md",
                    "screenshots": "screenshots/",
                    "logs": "logs/",
                },
            }
        },
    )


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


def write_bad_reference(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "stamp,phase,ref_x,ref_y",
                "0.00,takeoff,0,0",
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


def write_sources(tmp_path: Path) -> dict[str, Path]:
    reference = tmp_path / "reference.csv"
    state = tmp_path / "state.csv"
    screenshot = tmp_path / "rviz.png"
    log = tmp_path / "ros.log"
    write_reference(reference)
    write_state(state)
    write_nonempty(screenshot, "png fixture bytes")
    write_nonempty(log, "ros log fixture")
    return {
        "reference_csv": reference,
        "state_csv": state,
        "rviz_screenshot": screenshot,
        "ros_log": log,
    }


def artifact_args(sources: dict[str, Path]) -> list[str]:
    args: list[str] = []
    for slot, path in sources.items():
        args.extend(["--artifact", f"{slot}={path}"])
    return args


def test_export_runtime_sources_collects_profile_artifacts_and_builds_tracking(tmp_path: Path) -> None:
    run_dir = tmp_path / "pytest_export_runtime_sources"
    write_run_manifest(run_dir)
    sources = write_sources(tmp_path)

    completed = run_exporter(
        str(run_dir),
        "--runtime-export-profile",
        RUNTIME_EXPORT_PROFILE,
        *artifact_args(sources),
        "--review-text",
        "px4ctrl runtime export reviewed.",
        "--build-tracking",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["runtime_export_profile"] == RUNTIME_EXPORT_PROFILE
    assert report["runtime_log_profile"] == "px4ctrl_runtime_log_export_v1"
    assert report["tracking_source_profile"] == "px4_mavros_fused_reference_state_csv_v1"
    assert [item["slot"] for item in report["source_artifacts"]] == [
        "reference_csv",
        "state_csv",
        "rviz_screenshot",
        "ros_log",
    ]
    assert (run_dir / "runtime_export_manifest.json").is_file()
    assert (run_dir / "runtime_log_manifest.json").is_file()
    assert (run_dir / "raw" / "reference.csv").is_file()
    assert (run_dir / "raw" / "state.csv").is_file()
    assert (run_dir / "screenshots" / "rviz_review.png").is_file()
    assert (run_dir / "logs" / "ros_runtime.log").is_file()
    assert (run_dir / "tracking.csv").is_file()
    assert (run_dir / "review.md").is_file()

    with (run_dir / "tracking.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 3
    assert rows[1]["truth_z_m"] == "0.995"


def test_export_runtime_sources_rejects_missing_required_csv_column(tmp_path: Path) -> None:
    run_dir = tmp_path / "pytest_export_runtime_sources_bad_column"
    write_run_manifest(run_dir)
    sources = write_sources(tmp_path)
    write_bad_reference(sources["reference_csv"])

    completed = run_exporter(
        str(run_dir),
        "--runtime-export-profile",
        RUNTIME_EXPORT_PROFILE,
        *artifact_args(sources),
    )
    assert completed.returncode == 2
    assert "reference_csv is missing required column(s): ref_z" in completed.stderr


def test_export_runtime_sources_rejects_manifest_profile_mismatch(tmp_path: Path) -> None:
    run_dir = tmp_path / "pytest_export_runtime_sources_profile_mismatch"
    write_run_manifest(run_dir, runtime_export_profile="other_runtime_export_profile")
    sources = write_sources(tmp_path)

    completed = run_exporter(
        str(run_dir),
        "--runtime-export-profile",
        RUNTIME_EXPORT_PROFILE,
        *artifact_args(sources),
    )
    assert completed.returncode == 2
    assert "does not match RUN_MANIFEST.json" in completed.stderr
