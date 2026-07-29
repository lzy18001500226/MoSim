from __future__ import annotations

import json
import math
from pathlib import Path

from Scripts.mworks import run_offline_profile_certification as certification


def write_log(path: Path) -> None:
    records = [
        {"direction": "request", "id": 1, "params": {"name": "model_manager", "arguments": {"action": "load_file"}}},
        {"direction": "response", "id": 1, "result": {"content": [{"text": json.dumps({"ok": True})}]}},
        {"direction": "request", "id": 2, "params": {"name": "check_model", "arguments": {}}},
        {"direction": "response", "id": 2, "result": {"content": [{"text": json.dumps({"ok": True})}]}},
        {"direction": "request", "id": 3, "params": {"name": "call_code", "arguments": {}}},
        {"direction": "response", "id": 3, "result": {"content": [{"text": json.dumps({"ok": True, "run_script_result": {"simulate": True}})}]}},
        {"direction": "request", "id": 4, "params": {"name": "call_code", "arguments": {}}},
        {"direction": "response", "id": 4, "result": {"content": [{"text": json.dumps({"ok": True, "run_script_result": {"open_result": True, "create_plot": True, "open_model_diagram": True, "create_animation": True}})}]}},
        {"direction": "request", "id": 5, "params": {"name": "session_manager", "arguments": {"action": "shutdown"}}},
        {"direction": "response", "id": 5, "result": {"content": [{"text": json.dumps({"ok": True, "exit_api": {"ok": True}})}]}},
    ]
    path.write_text("\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8")


def test_parse_mcp_log_reads_real_nested_status(tmp_path: Path) -> None:
    log = tmp_path / "mcp.jsonl"
    write_log(log)
    status = certification.parse_mcp_log(log)
    assert all(status.values())


def test_build_command_keeps_generated_wrapper_and_result_under_run_dir(tmp_path: Path) -> None:
    profile = {
        "generated_model_name": "MoSimGenerated_test_v1",
        "scenario_id": "climb",
        "controller_id": "official_pid",
    }
    command = certification.build_smoke_command(profile, tmp_path)
    text = " ".join(command)
    assert str(tmp_path / "GeneratedProfile.mo") in text
    assert str(tmp_path / "native_result") in text
    assert "--gui-reset-windows" in command
    assert "--shutdown-session" in command
    assert "position_error_norm=position_error_norm" in command


def test_build_command_supports_direct_three_uav_profile(tmp_path: Path) -> None:
    profile = {
        "generated_model_name": "MoSimQuadrotorModel.Guidance.Formation.Scenarios.Model",
        "execution_kind": "direct_model",
        "scenario_id": "formation",
        "controller_id": "linear_mpc",
        "stop_time_s": 80,
        "variable_overrides": {"x": "leader_x"},
        "extra_variables": {"formation_error_m": "formation_error_m"},
    }
    command = certification.build_smoke_command(profile, tmp_path)
    text = " ".join(command)
    assert str(tmp_path / "GeneratedProfile.mo") not in text
    assert "--target-time 0,80" in text
    assert "x=leader_x" in text
    assert "formation_error_m=formation_error_m" in text


def test_csv_summary_exposes_terminal_state_for_bounded_gate(tmp_path: Path) -> None:
    raw = tmp_path / "result.csv"
    header = "time,x,y,z,x_ref,y_ref,z_ref,roll,pitch,yaw,u1,u2,u3,u4,position_error_norm,rotor_speed_1\n"
    rows = [f"{index},0,0,1,0,0,1,0,0,0,1,-1,1,-1,0,54\n" for index in range(11)]
    raw.write_text(header + "".join(rows), encoding="utf-8")
    summary = certification.csv_summary(raw)
    assert summary["row_count"] == 11
    assert summary["position_error_norm_end_m"] == 0


def test_csv_summary_allows_blank_optional_rotor_speed(tmp_path: Path) -> None:
    raw = tmp_path / "result.csv"
    header = "time,x,y,z,x_ref,y_ref,z_ref,roll,pitch,yaw,u1,u2,u3,u4,position_error_norm,rotor_speed_1\n"
    rows = [f"{index},0,0,1,0,0,1,0,0,0,1,-1,1,-1,0,\n" for index in range(11)]
    raw.write_text(header + "".join(rows), encoding="utf-8")
    summary = certification.csv_summary(raw)
    assert summary["rotor_speed_1_end_rad_s"] is None


def test_csv_summary_aggregates_three_uav_gate_values(tmp_path: Path) -> None:
    raw = tmp_path / "result.csv"
    header = (
        "time,x,y,z,x_ref,y_ref,z_ref,roll,pitch,yaw,u1,u2,u3,u4,"
        "position_error_norm,rotor_speed_1,formation_error_m,min_inter_uav_distance_m\n"
    )
    rows = [
        f"{index},0,0,1,0,0,1,0,0,0,1,-1,1,-1,0,54,{index / 100},{1.5 - index / 100}\n"
        for index in range(11)
    ]
    raw.write_text(header + "".join(rows), encoding="utf-8")
    summary = certification.csv_summary(raw)
    assert summary["max_formation_error_m"] == 0.1
    assert summary["min_inter_uav_distance_m"] == 1.4


def test_resolve_native_result_accepts_project_results_manifest(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(certification, "ROOT", tmp_path)
    run_dir = tmp_path / "Results" / "mworks_generated_profiles" / "run-v1"
    manifest_dir = run_dir / "native_result"
    cached = tmp_path / "Results" / "native_result_cache" / "run-v1" / "Model" / "Result.msr"
    manifest_dir.mkdir(parents=True)
    cached.parent.mkdir(parents=True)
    cached.write_bytes(b"msr")
    (manifest_dir / "native_result_manifest.json").write_text(
        json.dumps({"native_result_file_windows": str(cached)}), encoding="utf-8"
    )
    assert certification.resolve_native_result(run_dir, "Model") == cached.resolve()


def test_resolve_native_result_accepts_direct_model_short_name(tmp_path: Path) -> None:
    run_dir = tmp_path / "run-v1"
    result = run_dir / "native_result" / "FormationModel" / "Result.msr"
    result.parent.mkdir(parents=True)
    result.write_bytes(b"msr")
    assert certification.resolve_native_result(
        run_dir,
        "MoSimQuadrotorModel.Guidance.Formation.Scenarios.FormationModel",
    ) == result


def test_resolve_native_result_rejects_manifest_outside_results(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(certification, "ROOT", tmp_path)
    run_dir = tmp_path / "Results" / "mworks_generated_profiles" / "run-v1"
    manifest_dir = run_dir / "native_result"
    outside = tmp_path / "outside" / "Result.msr"
    manifest_dir.mkdir(parents=True)
    outside.parent.mkdir(parents=True)
    outside.write_bytes(b"msr")
    (manifest_dir / "native_result_manifest.json").write_text(
        json.dumps({"native_result_file_windows": str(outside)}), encoding="utf-8"
    )
    try:
        certification.resolve_native_result(run_dir, "Model")
    except ValueError as error:
        assert str(error) == "native_result_manifest_outside_results"
    else:
        raise AssertionError("outside native result path was accepted")


def test_write_strict_json_converts_non_finite_values_to_null(tmp_path: Path) -> None:
    output = tmp_path / "strict.json"
    certification.write_strict_json(
        output,
        {"finite": 1.5, "nan": math.nan, "nested": [math.inf, -math.inf]},
    )
    text = output.read_text(encoding="utf-8")
    assert "NaN" not in text
    assert "Infinity" not in text
    assert json.loads(text) == {"finite": 1.5, "nan": None, "nested": [None, None]}
