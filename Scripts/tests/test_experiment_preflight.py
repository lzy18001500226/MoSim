from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = ROOT / "Scripts" / "quality" / "build_experiment_preflight.py"
CATALOG = ROOT / "Config" / "profiles" / "catalog.json"
BINDINGS = ROOT / "Config" / "profiles" / "runtime_bindings.json"
METRICS = ROOT / "Config" / "profiles" / "metrics_schema.json"
VALID_PROFILE = ROOT / "Config" / "profiles" / "experiments" / "fastlio_independent_eval_figure8_v1.json"
G10C_DFBC_INDI_PROFILE = ROOT / "Config" / "profiles" / "experiments" / "g10c_dfbc_smooth_robust_indi_figure8_v1.json"
G96_BODYRATE_BLOCKED_EXPERIMENT = ROOT / "Config" / "profiles" / "experiments" / "g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_preflight(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PREFLIGHT), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_experiment_preflight_accepts_current_profiles() -> None:
    completed = run_preflight("--all")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["checked_count"] >= 7
    result_ids = {result["experiment_id"] for result in report["results"]}
    assert "g10c_dfbc_smooth_robust_no_indi_figure8_v1" not in result_ids
    assert "g10c_dfbc_smooth_robust_indi_figure8_v1" not in result_ids
    assert "g10c_official_pid_no_indi_figure8_v1" not in result_ids
    assert "g10c_official_pid_indi_figure8_v1" not in result_ids
    assert "g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1" not in result_ids
    assert "g96_dfbc_smooth_robust_bodyrate_figure8_v1" not in result_ids
    for result in report["results"]:
        assert result["ok"] is True
        assert result["launch_plan"]["launch_plan"]["run_id"].startswith("dryrun_")
        assert result["run_manifest_template"]["run_manifest"]["launch_plan_hash"]
        assert result["run_manifest_template"]["run_manifest"]["evidence"]["result_root"].startswith("Results/runs/")
        assert result["runtime_export_contract"]["runtime_export_profile"]
        assert result["runtime_export_contract"]["required_artifacts"]


def test_experiment_preflight_rejects_blocked_g10_augmentation_profile() -> None:
    completed = run_preflight(str(G10C_DFBC_INDI_PROFILE), "--run-id", "dryrun_g10c_indi_test")
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    result = report["results"][0]
    assert result["ok"] is False
    assert result["run_id"] == "dryrun_g10c_indi_test"
    assert result["stage"] == "profile_validation"
    assert any(error["code"] == "PROFILE-STATUS-01" for error in result["errors"])
    assert result["profile_rejection"]["control_started"] is False


def test_experiment_preflight_rejects_explicit_blocked_profile() -> None:
    completed = run_preflight(str(G96_BODYRATE_BLOCKED_EXPERIMENT))
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    result = report["results"][0]
    assert result["ok"] is False
    assert result["stage"] == "profile_validation"
    assert any(error["code"] == "PROFILE-STATUS-01" for error in result["errors"])


def test_experiment_preflight_rejects_missing_runtime_binding(tmp_path: Path) -> None:
    bindings = load_json(BINDINGS)
    bindings["template_bindings"].pop("fastlio_review_or_ekf_bridge.launch")
    bindings_path = tmp_path / "runtime_bindings.json"
    write_json(bindings_path, bindings)

    completed = run_preflight("--runtime-bindings", str(bindings_path), str(VALID_PROFILE))
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    result = report["results"][0]
    assert result["ok"] is False
    assert any(error["code"] == "P-BIND-01" for error in result["errors"])


def test_experiment_preflight_rejects_missing_metric_definition(tmp_path: Path) -> None:
    metrics = load_json(METRICS)
    metrics["metric_definitions"].pop("ate")
    metrics_path = tmp_path / "metrics_schema.json"
    write_json(metrics_path, metrics)

    completed = run_preflight("--metrics-schema", str(metrics_path), str(VALID_PROFILE))
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    result = report["results"][0]
    assert result["ok"] is False
    assert any(error["code"] == "P-METRIC-01" for error in result["errors"])
