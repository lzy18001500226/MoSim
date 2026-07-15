from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_experiment_profile.py"
CATALOG = ROOT / "Config" / "profiles" / "catalog.json"
RUNTIME_LOG_EXPORTS = ROOT / "Config" / "profiles" / "runtime_log_exports.json"
TRACKING_SOURCES = ROOT / "Config" / "profiles" / "tracking_sources.json"
VALID_PROFILE = ROOT / "Config" / "profiles" / "experiments" / "px4ctrl_takeoff_hover_land_v1.json"
FASTLIO_EVAL_PROFILE = ROOT / "Config" / "profiles" / "experiments" / "fastlio_independent_eval_figure8_v1.json"
FASTLIO_HYBRID_PROFILE = ROOT / "Config" / "profiles" / "experiments" / "fastlio_hybrid_z_figure8_v1.json"
G9_OFFICIAL_PID_EXPERIMENT = ROOT / "Config" / "profiles" / "experiments" / "g9_official_pid_figure8_v1.json"
G10C_DFBC_NO_INDI_EXPERIMENT = ROOT / "Config" / "profiles" / "experiments" / "g10c_dfbc_smooth_robust_no_indi_figure8_v1.json"
G10C_DFBC_INDI_EXPERIMENT = ROOT / "Config" / "profiles" / "experiments" / "g10c_dfbc_smooth_robust_indi_figure8_v1.json"
G10C_OFFICIAL_PID_BLOCKED_EXPERIMENT = ROOT / "Config" / "profiles" / "experiments" / "g10c_official_pid_indi_figure8_v1.json"
G9_SE3_BASIC_CANDIDATE = ROOT / "Config" / "profiles" / "candidates" / "g9_se3_basic_figure8_candidate_v1.json"
G9_PID_INDI_CANDIDATE = ROOT / "Config" / "profiles" / "candidates" / "g9_pid_indi_figure8_candidate_v1.json"
G96_BODYRATE_BLOCKED_EXPERIMENT = ROOT / "Config" / "profiles" / "experiments" / "g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_checker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def base_case(tmp_path: Path) -> tuple[Path, Path, dict, dict]:
    catalog = load_json(CATALOG)
    profile = load_json(VALID_PROFILE)
    catalog_path = tmp_path / "catalog.json"
    profile_path = tmp_path / "experiment.json"
    return catalog_path, profile_path, catalog, profile


def write_case(catalog_path: Path, profile_path: Path, catalog: dict, profile: dict) -> None:
    write_json(catalog_path, catalog)
    write_json(profile_path, profile)


def assert_rejected(completed: subprocess.CompletedProcess[str], code: str) -> None:
    assert completed.returncode == 1, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    result = report["results"][0]
    assert result["ok"] is False
    assert any(error["code"] == code for error in result["errors"]), result
    rejection = result["profile_rejection"]
    assert rejection["reason_code"] == code
    assert rejection["control_started"] is False


def test_experiment_profile_validator_accepts_current_px4ctrl_profiles() -> None:
    completed = run_checker("--all")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["runtime_log_exports"] == str(RUNTIME_LOG_EXPORTS)
    assert report["tracking_sources"] == str(TRACKING_SOURCES)
    assert report["checked_count"] >= 4
    results_by_id = {result["experiment_id"]: result for result in report["results"]}
    for result in report["results"]:
        assert result["launch_plan_skeleton"]["launch_plan"]["experiment_profile_hash"]
        assert result["run_manifest_skeleton"]["run_manifest"]["profile_hashes"]
        assert result["run_manifest_skeleton"]["run_manifest"]["runtime_export"]["runtime_export_profile"]
        assert result["profile_rejection"] is None
    assert (
        results_by_id["px4ctrl_takeoff_hover_land_v1"]["run_manifest_skeleton"]["run_manifest"]["runtime_export"]["tracking_source_profile"]
        == "px4_mavros_fused_reference_state_csv_v1"
    )
    assert (
        results_by_id["fastlio_independent_eval_figure8_v1"]["run_manifest_skeleton"]["run_manifest"]["runtime_export"]["tracking_source_profile"]
        == "fastlio_eval_reference_state_csv_v1"
    )
    assert (
        results_by_id["fastlio_px4_ekf_ab_figure8_v1"]["run_manifest_skeleton"]["run_manifest"]["runtime_export"]["tracking_source_profile"]
        == "fastlio_px4_ekf_fused_reference_state_csv_v1"
    )
    assert (
        results_by_id["fastlio_hybrid_z_figure8_v1"]["run_manifest_skeleton"]["run_manifest"]["runtime_export"]["tracking_source_profile"]
        == "fastlio_xy_yaw_gazebo_z_reference_state_csv_v1"
    )
    assert "g10c_dfbc_smooth_robust_no_indi_figure8_v1" not in results_by_id
    assert "g10c_dfbc_smooth_robust_indi_figure8_v1" not in results_by_id
    assert "g10c_official_pid_no_indi_figure8_v1" not in results_by_id
    assert "g10c_official_pid_indi_figure8_v1" not in results_by_id
    assert "g96_dfbc_smooth_robust_bodyrate_takeoff_hover_land_v1" not in results_by_id
    assert "g96_dfbc_smooth_robust_bodyrate_figure8_v1" not in results_by_id


def test_validator_rejects_explicit_blocked_experiment_profile() -> None:
    completed = run_checker(str(G96_BODYRATE_BLOCKED_EXPERIMENT))
    assert_rejected(completed, "PROFILE-STATUS-01")


def test_validator_rejects_legacy_official_pid_g10c_profile() -> None:
    completed = run_checker(str(G10C_OFFICIAL_PID_BLOCKED_EXPERIMENT))
    assert_rejected(completed, "PROFILE-STATUS-01")


def test_run_manifest_skeleton_includes_controller_metadata() -> None:
    completed = run_checker(str(VALID_PROFILE))
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    manifest = report["results"][0]["run_manifest_skeleton"]["run_manifest"]
    controller = manifest["controller"]

    assert controller["controller_profile"] == "px4ctrl_attitude_thrust_v1"
    assert controller["controller_id"] == "px4ctrl"
    assert controller["controller_family"] == "px4ctrl"
    assert controller["chain_position"] == "nominal_outer_loop"
    assert controller["implementation"] == "cpp"
    assert controller["implementation_status"] == "accepted"
    assert controller["g9_task"] == "baseline"
    assert controller["source_basis_required"] is False
    assert controller["acceptance_tiers"] == ["PASS", "REPORT", "CANDIDATE"]


def test_run_manifest_skeleton_includes_g9_official_pid_metadata() -> None:
    completed = run_checker(str(G9_OFFICIAL_PID_EXPERIMENT))
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    manifest = report["results"][0]["run_manifest_skeleton"]["run_manifest"]
    controller = manifest["controller"]

    assert controller["controller_profile"] == "official_pid_attitude_thrust_v1"
    assert controller["controller_id"] == "official_pid"
    assert controller["controller_family"] == "pid"
    assert controller["chain_position"] == "nominal_position_velocity_outer_loop"
    assert controller["implementation"] == "cpp_attitude_thrust_backend_mworks_codegen_pending"
    assert controller["implementation_status"] == "implemented"
    assert controller["g9_task"] == "G9-A"
    assert controller["source_basis_required"] is True
    assert "Results/g9/official_pid_attitude_thrust_v1/source_audit/controller_source_audit.json" in controller["source_basis"]
    assert "Results/g9/official_pid_attitude_thrust_v1/g9a_static_gate_20260629_131642/RUN_MANIFEST.json" in controller["source_basis"]


def test_validator_accepts_retained_g9_controller_candidate_after_implementation() -> None:
    completed = run_checker(str(G9_SE3_BASIC_CANDIDATE))
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    result = report["results"][0]
    controller = result["run_manifest_skeleton"]["run_manifest"]["controller"]

    assert result["ok"] is True
    assert result["profile_rejection"] is None
    assert controller["controller_profile"] == "se3_basic_attitude_thrust_v1"
    assert controller["implementation_status"] == "implemented"
    assert "G9-B accepted" in result["launch_plan_skeleton"]["launch_plan"]["forbidden_claims"]
    assert "MWORKS generated controller accepted" in result["launch_plan_skeleton"]["launch_plan"]["forbidden_claims"]


def test_validator_accepts_retained_g9_augmentation_candidate_after_implementation() -> None:
    completed = run_checker(str(G9_PID_INDI_CANDIDATE))
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    result = report["results"][0]
    manifest = result["run_manifest_skeleton"]["run_manifest"]

    assert result["ok"] is True
    assert result["profile_rejection"] is None
    assert manifest["controller"]["controller_profile"] == "official_pid_attitude_thrust_v1"
    assert manifest["controller"]["implementation_status"] == "implemented"
    assert "G9-E accepted" in result["launch_plan_skeleton"]["launch_plan"]["forbidden_claims"]
    assert "INDI independent nominal controller" in result["launch_plan_skeleton"]["launch_plan"]["forbidden_claims"]


def test_run_manifest_skeleton_includes_g10_augmentation_metadata() -> None:
    completed = run_checker(str(G10C_DFBC_INDI_EXPERIMENT))
    assert completed.returncode != 0
    report = json.loads(completed.stdout)
    result = report["results"][0]
    assert result["profile_rejection"]["reason_code"] == "PROFILE-STATUS-01"

    assert result["ok"] is False
    assert "launch_plan_skeleton" not in result
    assert "run_manifest_skeleton" not in result


def test_run_manifest_skeleton_preserves_g10_no_indi_pair_metadata() -> None:
    completed = run_checker(str(G10C_DFBC_NO_INDI_EXPERIMENT))
    assert completed.returncode != 0
    report = json.loads(completed.stdout)
    result = report["results"][0]
    assert result["profile_rejection"]["reason_code"] == "PROFILE-STATUS-01"

    assert result["ok"] is False
    assert "launch_plan_skeleton" not in result
    assert "run_manifest_skeleton" not in result


def test_validator_rejects_missing_jerk_snap_reference(tmp_path: Path) -> None:
    catalog_path, profile_path, catalog, profile = base_case(tmp_path)
    catalog["controller_profiles"]["dfbc_full_attitude_thrust_v1"] = {
        **catalog["controller_profiles"]["px4ctrl_attitude_thrust_v1"],
        "controller_id": "dfbc_full",
        "required_reference": ["position", "velocity", "acceleration", "jerk", "snap", "yaw"],
    }
    profile["experiment_profile"]["controller_profile"] = "dfbc_full_attitude_thrust_v1"
    write_case(catalog_path, profile_path, catalog, profile)

    completed = run_checker("--catalog", str(catalog_path), str(profile_path))
    assert_rejected(completed, "C-REF-01")


def test_validator_rejects_implemented_controller_without_real_source_basis(tmp_path: Path) -> None:
    catalog_path, profile_path, catalog, profile = base_case(tmp_path)
    catalog["controller_profiles"]["implemented_without_source_v1"] = {
        **catalog["controller_profiles"]["px4ctrl_attitude_thrust_v1"],
        "controller_id": "implemented_without_source",
        "implementation_status": "implemented",
        "source_basis_required": True,
        "source_basis": ["pending_g9_source_audit"],
    }
    profile["experiment_profile"]["controller_profile"] = "implemented_without_source_v1"
    write_case(catalog_path, profile_path, catalog, profile)

    completed = run_checker("--catalog", str(catalog_path), str(profile_path))
    assert_rejected(completed, "C-CTRL-02")


def test_validator_rejects_trajectory_rate_mismatch(tmp_path: Path) -> None:
    catalog_path, profile_path, catalog, profile = base_case(tmp_path)
    catalog["trajectory_profiles"]["takeoff_hover_land_v1"]["reference_rate_hz"] = 50
    write_case(catalog_path, profile_path, catalog, profile)

    completed = run_checker("--catalog", str(catalog_path), str(profile_path))
    assert_rejected(completed, "C-TRAJ-01")


def test_validator_rejects_non_step_discontinuous_trajectory(tmp_path: Path) -> None:
    catalog_path, profile_path, catalog, profile = base_case(tmp_path)
    catalog["trajectory_profiles"]["takeoff_hover_land_v1"]["continuity_required"]["velocity"] = False
    write_case(catalog_path, profile_path, catalog, profile)

    completed = run_checker("--catalog", str(catalog_path), str(profile_path))
    assert_rejected(completed, "C-TRAJ-04")


def test_validator_accepts_fastlio_eval_only_as_parallel_localization_source() -> None:
    completed = run_checker(str(FASTLIO_EVAL_PROFILE))
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    result = report["results"][0]
    assert result["ok"] is True
    assert any(warning["code"] == "LIO-EVAL-01" for warning in result["warnings"])

    manifest = result["run_manifest_skeleton"]["run_manifest"]
    assert manifest["state_and_truth"]["state_source_profile"] == "px4_mavros_fused_v1"
    assert manifest["state_and_truth"]["localization_eval_profile"] == "fastlio_eval_only_v1"
    assert manifest["state_and_truth"]["leaderboard_group"] == "fastlio_eval_only"

    steps = result["launch_plan_skeleton"]["launch_plan"]["steps"]
    fastlio_steps = [step for step in steps if step["id"] == "fastlio"]
    assert fastlio_steps
    assert fastlio_steps[0]["mode"] == "evaluation_only"


def test_validator_rejects_runtime_export_missing_required_slot(tmp_path: Path) -> None:
    catalog_path, profile_path, catalog, profile = base_case(tmp_path)
    export_profile = catalog["runtime_export_profiles"]["sunray_px4ctrl_runtime_export_v1"]
    export_profile["required_artifact_slots"].append("missing_slot")
    write_case(catalog_path, profile_path, catalog, profile)

    completed = run_checker("--catalog", str(catalog_path), str(profile_path))
    assert_rejected(completed, "C-EXPORT-04")


def test_validator_rejects_unregistered_runtime_log_profile(tmp_path: Path) -> None:
    catalog_path, profile_path, catalog, profile = base_case(tmp_path)
    catalog["runtime_export_profiles"]["sunray_px4ctrl_runtime_export_v1"][
        "runtime_log_profile"
    ] = "missing_runtime_log_profile_v1"
    write_case(catalog_path, profile_path, catalog, profile)

    completed = run_checker("--catalog", str(catalog_path), str(profile_path))
    assert_rejected(completed, "C-LOG-01")


def test_validator_rejects_tracking_source_state_mismatch(tmp_path: Path) -> None:
    catalog = load_json(CATALOG)
    profile = load_json(FASTLIO_HYBRID_PROFILE)
    runtime_log_exports = load_json(RUNTIME_LOG_EXPORTS)
    tracking_sources = load_json(TRACKING_SOURCES)
    tracking = tracking_sources["profiles"]["fastlio_px4_ekf_fused_reference_state_csv_v1"]
    tracking["compatible_experiment_ids"].append("fastlio_hybrid_z_figure8_v1")
    catalog["runtime_export_profiles"]["sunray_fastlio_hybrid_z_runtime_export_v1"][
        "tracking_source_profile"
    ] = "fastlio_px4_ekf_fused_reference_state_csv_v1"
    runtime_log_exports["profiles"]["fastlio_hybrid_z_runtime_log_export_v1"][
        "tracking_source_profile"
    ] = "fastlio_px4_ekf_fused_reference_state_csv_v1"
    tracking_sources_path = tmp_path / "tracking_sources.json"
    runtime_log_exports_path = tmp_path / "runtime_log_exports.json"
    catalog_path = tmp_path / "catalog.json"
    profile_path = tmp_path / "experiment.json"
    write_case(catalog_path, profile_path, catalog, profile)
    write_json(runtime_log_exports_path, runtime_log_exports)
    write_json(tracking_sources_path, tracking_sources)

    completed = run_checker(
        "--catalog",
        str(catalog_path),
        "--runtime-log-exports",
        str(runtime_log_exports_path),
        "--tracking-sources",
        str(tracking_sources_path),
        str(profile_path),
    )
    assert_rejected(completed, "C-TRACK-03")


def test_validator_rejects_fastlio_eval_tracking_as_control_state(tmp_path: Path) -> None:
    tracking_sources = load_json(TRACKING_SOURCES)
    tracking_sources["profiles"]["fastlio_eval_reference_state_csv_v1"]["control_state_tracking"] = True
    tracking_sources_path = tmp_path / "tracking_sources.json"
    write_json(tracking_sources_path, tracking_sources)

    completed = run_checker("--tracking-sources", str(tracking_sources_path), str(FASTLIO_EVAL_PROFILE))
    assert_rejected(completed, "C-TRACK-07")


def test_validator_rejects_hybrid_z_tracking_without_gazebo_z_source(tmp_path: Path) -> None:
    tracking_sources = load_json(TRACKING_SOURCES)
    tracking_sources["profiles"]["fastlio_xy_yaw_gazebo_z_reference_state_csv_v1"]["z_source"] = "fastlio_height"
    tracking_sources_path = tmp_path / "tracking_sources.json"
    write_json(tracking_sources_path, tracking_sources)

    completed = run_checker("--tracking-sources", str(tracking_sources_path), str(FASTLIO_HYBRID_PROFILE))
    assert_rejected(completed, "C-TRACK-08")


def test_validator_rejects_body_rate_controller_with_attitude_adapter(tmp_path: Path) -> None:
    catalog_path, profile_path, catalog, profile = base_case(tmp_path)
    catalog["controller_profiles"]["body_rate_controller_v1"] = {
        **catalog["controller_profiles"]["px4ctrl_attitude_thrust_v1"],
        "controller_id": "body_rate_test",
        "output_interface": "BODY_RATE_THRUST",
        "compatible_adapters": ["mavros_attitude_thrust_v1"],
    }
    profile["experiment_profile"]["controller_profile"] = "body_rate_controller_v1"
    write_case(catalog_path, profile_path, catalog, profile)

    completed = run_checker("--catalog", str(catalog_path), str(profile_path))
    assert_rejected(completed, "C-OUT-01")


def test_validator_rejects_fastlio_eval_only_as_controller_state(tmp_path: Path) -> None:
    catalog_path, profile_path, catalog, profile = base_case(tmp_path)
    profile["experiment_profile"]["state_source_profile"] = "fastlio_eval_only_v1"
    write_case(catalog_path, profile_path, catalog, profile)

    completed = run_checker("--catalog", str(catalog_path), str(profile_path))
    assert_rejected(completed, "C-STATE-01")


def test_validator_rejects_gazebo_truth_debug_state_in_formal_leaderboard(tmp_path: Path) -> None:
    catalog_path, profile_path, catalog, profile = base_case(tmp_path)
    profile["experiment_profile"]["state_source_profile"] = "gazebo_truth_debug_state_v1"
    write_case(catalog_path, profile_path, catalog, profile)

    completed = run_checker("--catalog", str(catalog_path), str(profile_path))
    assert_rejected(completed, "C-TRUTH-01")


def test_validator_rejects_swarm_without_namespace_isolation(tmp_path: Path) -> None:
    catalog_path, profile_path, catalog, profile = base_case(tmp_path)
    catalog["scenario_profiles"]["swarm_two_uav_v1"] = {
        **catalog["scenario_profiles"]["sunray150_empty_lab_v1"],
        "vehicle_count": 2,
    }
    profile["experiment_profile"]["scenario_profile"] = "swarm_two_uav_v1"
    write_case(catalog_path, profile_path, catalog, profile)

    completed = run_checker("--catalog", str(catalog_path), str(profile_path))
    assert_rejected(completed, "C-SWARM-01")


def test_validator_rejects_ue_display_without_runtime_bridge(tmp_path: Path) -> None:
    catalog_path, profile_path, catalog, profile = base_case(tmp_path)
    catalog["display_profiles"]["ue_required_v1"] = {
        "display_backend": ["ue"],
        "requires_ue_bridge": True,
    }
    profile["experiment_profile"]["display_profile"] = "ue_required_v1"
    write_case(catalog_path, profile_path, catalog, profile)

    completed = run_checker("--catalog", str(catalog_path), str(profile_path))
    assert_rejected(completed, "C-DISPLAY-01")


def test_validator_emits_static_skeleton_artifacts(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifacts"
    completed = run_checker(str(VALID_PROFILE), "--emit-artifacts-dir", str(artifact_dir))
    assert completed.returncode == 0, completed.stdout + completed.stderr

    launch_plan = artifact_dir / "px4ctrl_takeoff_hover_land_v1.launch_plan.skeleton.json"
    manifest = artifact_dir / "px4ctrl_takeoff_hover_land_v1.RUN_MANIFEST.skeleton.json"
    assert launch_plan.is_file()
    assert manifest.is_file()

    launch_payload = load_json(launch_plan)
    manifest_payload = load_json(manifest)
    assert launch_payload["launch_plan"]["experiment_profile_id"] == "px4ctrl_takeoff_hover_land_v1"
    assert manifest_payload["run_manifest"]["forbidden_claims"]
    assert manifest_payload["run_manifest"]["evaluation"]["required_metrics"]
    assert manifest_payload["run_manifest"]["trajectory_contract"]["reference_rate_hz"] == 100
    assert manifest_payload["run_manifest"]["runtime_export"]["runtime_log_profile"] == "px4ctrl_runtime_log_export_v1"
