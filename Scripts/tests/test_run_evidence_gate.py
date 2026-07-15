from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREPARE = ROOT / "Scripts" / "quality" / "prepare_experiment_run.py"
EXPORTER = ROOT / "Scripts" / "quality" / "export_runtime_sources.py"
COMPUTE = ROOT / "Scripts" / "quality" / "compute_tracking_metrics.py"
THRESHOLDS = ROOT / "Scripts" / "quality" / "check_metric_thresholds.py"
CHECK_RUN = ROOT / "Scripts" / "quality" / "check_run_evidence.py"
VALID_PROFILE = ROOT / "Config" / "profiles" / "experiments" / "px4ctrl_takeoff_hover_land_v1.json"
RUNTIME_EXPORT_PROFILE = "sunray_px4ctrl_runtime_export_v1"
RUNTIME_LOG_PROFILE = "px4ctrl_runtime_log_export_v1"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
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
                "0.012,0.005,0.000,0.480,0",
                "0.021,0.010,0.000,0.990,0",
                "0.031,0.008,0.006,0.995,0",
                "0.039,0.004,0.003,1.000,0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def make_run_dir(tmp_path: Path) -> Path:
    run_id = "pytest_px4ctrl_takeoff_hover_land"
    prepared = run_cmd(str(PREPARE), str(VALID_PROFILE), "--run-id", run_id, "--output-root", str(tmp_path))
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    run_dir = tmp_path / run_id
    source_dir = tmp_path / "runtime_sources"
    source_dir.mkdir()
    reference = source_dir / "reference.csv"
    state = source_dir / "state.csv"
    screenshot = source_dir / "rviz.png"
    log = source_dir / "ros.log"
    write_reference(reference)
    write_state(state)
    screenshot.write_text("nonempty screenshot placeholder\n", encoding="utf-8")
    log.write_text("nonempty log placeholder\n", encoding="utf-8")
    collected = run_cmd(
        str(EXPORTER),
        str(run_dir),
        "--runtime-export-profile",
        RUNTIME_EXPORT_PROFILE,
        "--artifact",
        f"reference_csv={reference}",
        "--artifact",
        f"state_csv={state}",
        "--artifact",
        f"rviz_screenshot={screenshot}",
        "--artifact",
        f"ros_log={log}",
        "--review-text",
        "px4ctrl takeoff hover land evidence review.",
        "--build-tracking",
    )
    assert collected.returncode == 0, collected.stdout + collected.stderr

    metrics = run_cmd(
        str(COMPUTE),
        str(run_dir / "tracking.csv"),
        "--manifest",
        str(run_dir / "RUN_MANIFEST.json"),
        "--out",
        str(run_dir / "metrics.json"),
    )
    assert metrics.returncode == 0, metrics.stdout + metrics.stderr
    threshold = run_cmd(
        str(THRESHOLDS),
        str(run_dir / "metrics.json"),
        "--manifest",
        str(run_dir / "RUN_MANIFEST.json"),
        "--report",
        str(run_dir / "threshold_report.json"),
    )
    assert threshold.returncode == 0, threshold.stdout + threshold.stderr
    return run_dir


def test_run_evidence_gate_accepts_complete_run_packet(tmp_path: Path) -> None:
    run_dir = make_run_dir(tmp_path)
    completed = run_cmd(str(CHECK_RUN), str(run_dir))
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["tracking_rows"] == 5
    assert report["threshold_accepted"] is True
    metrics = load_json(run_dir / "metrics.json")
    assert metrics["metrics"]["rmse"]["unit"] == "m"
    assert metrics["metrics"]["saturation_ratio"]["value"] == 0
    assert (run_dir / "runtime_export_manifest.json").is_file()


def test_run_evidence_gate_rejects_missing_runtime_export_manifest(tmp_path: Path) -> None:
    run_dir = make_run_dir(tmp_path)
    (run_dir / "runtime_export_manifest.json").unlink()

    completed = run_cmd(str(CHECK_RUN), str(run_dir))
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert any(error["code"] == "R-EXPORT-JSON-01" for error in report["errors"])


def test_run_evidence_gate_rejects_runtime_export_profile_mismatch(tmp_path: Path) -> None:
    run_dir = make_run_dir(tmp_path)
    export_manifest = load_json(run_dir / "runtime_export_manifest.json")
    export_manifest["runtime_export_profile"] = "wrong_runtime_export_profile"
    write_json(run_dir / "runtime_export_manifest.json", export_manifest)

    completed = run_cmd(str(CHECK_RUN), str(run_dir))
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert any(error["code"] == "R-EXPORT-03" for error in report["errors"])


def test_run_evidence_gate_rejects_missing_runtime_export_source_slot(tmp_path: Path) -> None:
    run_dir = make_run_dir(tmp_path)
    export_manifest = load_json(run_dir / "runtime_export_manifest.json")
    export_manifest["source_artifacts"] = [
        item for item in export_manifest["source_artifacts"] if item["slot"] != "ros_log"
    ]
    write_json(run_dir / "runtime_export_manifest.json", export_manifest)

    completed = run_cmd(str(CHECK_RUN), str(run_dir))
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert any(error["code"] == "R-EXPORT-ARTIFACT-05" for error in report["errors"])


def test_run_evidence_gate_rejects_runtime_export_source_hash_mismatch(tmp_path: Path) -> None:
    run_dir = make_run_dir(tmp_path)
    source_reference = tmp_path / "runtime_sources" / "reference.csv"
    source_reference.write_text(source_reference.read_text(encoding="utf-8") + "0.05,hover,0,0,1.0\n", encoding="utf-8")

    completed = run_cmd(str(CHECK_RUN), str(run_dir))
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert any(error["code"] == "R-EXPORT-ARTIFACT-10" for error in report["errors"])


def test_run_evidence_gate_rejects_missing_required_metric(tmp_path: Path) -> None:
    run_dir = make_run_dir(tmp_path)
    metrics = load_json(run_dir / "metrics.json")
    metrics["metrics"].pop("rmse")
    write_json(run_dir / "metrics.json", metrics)

    completed = run_cmd(str(CHECK_RUN), str(run_dir))
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is False
    assert any(error["code"] == "R-METRIC-03" for error in report["errors"])


def test_run_evidence_gate_rejects_forbidden_review_claim(tmp_path: Path) -> None:
    run_dir = make_run_dir(tmp_path)
    (run_dir / "review.md").write_text("This run proves FAST-LIO closed-loop localization.\n", encoding="utf-8")

    completed = run_cmd(str(CHECK_RUN), str(run_dir))
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert any(error["code"] == "R-CLAIM-01" for error in report["errors"])


def test_run_evidence_gate_rejects_manifest_placeholders(tmp_path: Path) -> None:
    run_dir = make_run_dir(tmp_path)
    manifest = load_json(run_dir / "RUN_MANIFEST.json")
    manifest["run_manifest"]["source_state"]["git_commit"] = "<commit-or-dirty>"
    write_json(run_dir / "RUN_MANIFEST.json", manifest)

    completed = run_cmd(str(CHECK_RUN), str(run_dir))
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert any(error["code"] == "R-PLACEHOLDER-01" for error in report["errors"])


def test_run_evidence_gate_rejects_gitkeep_only_screenshots(tmp_path: Path) -> None:
    run_dir = make_run_dir(tmp_path)
    for child in (run_dir / "screenshots").iterdir():
        child.unlink()
    (run_dir / "screenshots" / ".gitkeep").write_text("", encoding="utf-8")

    completed = run_cmd(str(CHECK_RUN), str(run_dir))
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert any(error["code"] == "R-DIR-02" for error in report["errors"])
