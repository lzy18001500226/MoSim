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
PX4CTRL_HYBRID_HOVER_PROFILE = ROOT / "Config" / "profiles" / "experiments" / "px4ctrl_takeoff_hover_land_v1.json"
TRACKING_SOURCES = ROOT / "Config" / "profiles" / "tracking_sources.json"
RUNTIME_LOG_EXPORTS = ROOT / "Config" / "profiles" / "runtime_log_exports.json"
FUEL_BLOCKED_EXPERIMENT = ROOT / "Config" / "profiles" / "experiments" / "factory_l2_fuel_fixed64_exploration_v1.json"
FORMATION_BLOCKED_EXPERIMENT = ROOT / "Config" / "profiles" / "experiments" / "factory_l2_three_uav_swarm_formation_v1.json"


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
    assert "factory_l2_fuel_fixed64_exploration_v1" not in result_ids
    assert "factory_l2_three_uav_swarm_formation_v1" not in result_ids
    for result in report["results"]:
        assert result["ok"] is True
        assert result["launch_plan"]["launch_plan"]["run_id"].startswith("dryrun_")
        assert result["run_manifest_template"]["run_manifest"]["launch_plan_hash"]
        assert result["run_manifest_template"]["run_manifest"]["evidence"]["result_root"].startswith("Results/runs/")
        assert result["runtime_export_contract"]["runtime_export_profile"]
        assert result["runtime_export_contract"]["required_artifacts"]
        for runtime_check in result["runtime_checks"]:
            assert all(not path.startswith("References/") for path in runtime_check["required_paths"])


def test_px4ctrl_hover_profile_declares_the_source_local_hybrid_state_chain() -> None:
    profile = load_json(PX4CTRL_HYBRID_HOVER_PROFILE)["experiment_profile"]

    assert profile["state_source_profile"] == "fastlio_xy_yaw_gazebo_z_v1"
    assert profile["height_source_profile"] == "hybrid_gazebo_z_surrogate_v1"
    assert profile["runtime_export_profile"] == "sunray_fastlio_hybrid_z_runtime_export_v1"
    assert "GPS/barometer localization baseline equivalence" in profile["forbidden_claims"]


def test_px4ctrl_hybrid_hover_cannot_select_legacy_gps_rangefinder_exports() -> None:
    experiment_id = "px4ctrl_takeoff_hover_land_v1"
    tracking_profiles = load_json(TRACKING_SOURCES)["profiles"]
    runtime_log_profiles = load_json(RUNTIME_LOG_EXPORTS)["profiles"]

    assert experiment_id in tracking_profiles["fastlio_xy_yaw_gazebo_z_reference_state_csv_v1"]["compatible_experiment_ids"]
    assert experiment_id not in tracking_profiles["px4ctrl_reference_state_csv_v1"]["compatible_experiment_ids"]
    assert experiment_id not in tracking_profiles["px4_mavros_fused_reference_state_csv_v1"]["compatible_experiment_ids"]
    assert experiment_id in runtime_log_profiles["fastlio_hybrid_z_runtime_log_export_v1"]["compatible_experiment_ids"]
    assert experiment_id not in runtime_log_profiles["px4ctrl_runtime_log_export_v1"]["compatible_experiment_ids"]


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


def test_experiment_preflight_rejects_historical_factory_profiles() -> None:
    for profile_path in (FUEL_BLOCKED_EXPERIMENT, FORMATION_BLOCKED_EXPERIMENT):
        completed = run_preflight(str(profile_path))
        assert completed.returncode == 1, completed.stdout + completed.stderr
        report = json.loads(completed.stdout)
        result = report["results"][0]
        assert result["ok"] is False
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
