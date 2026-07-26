#!/usr/bin/env python3
"""Run and certify one generated offline MWORKS composition profile."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.mworks import generate_offline_profile_wrapper as generator


SMOKE_SCRIPT = ROOT / "Scripts" / "mworks" / "run_sysplorer_mcp_smoke.py"
BASE_MODEL_FILES = [
    ROOT / "Models" / "MoSimQuadrotorModel" / "package.mo",
]
VARIABLE_OVERRIDES = {
    "x": "position[1]",
    "y": "position[2]",
    "z": "position[3]",
    "x_ref": "position_ref[1]",
    "y_ref": "position_ref[2]",
    "z_ref": "position_ref[3]",
    "roll": "attitude[1]",
    "pitch": "attitude[2]",
    "yaw": "attitude[3]",
    "u1": "rotor_command[1]",
    "u2": "rotor_command[2]",
    "u3": "rotor_command[3]",
    "u4": "rotor_command[4]",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def sanitize_json_value(value: Any) -> Any:
    """Convert non-finite metrics to strict-JSON null values."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: sanitize_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [sanitize_json_value(item) for item in value]
    return value


def write_strict_json(path: Path, value: Any) -> None:
    cleaned = sanitize_json_value(value)
    path.write_text(
        json.dumps(cleaned, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def decode_response_payload(record: dict[str, Any]) -> dict[str, Any]:
    result = record.get("result")
    if not isinstance(result, dict):
        return {}
    content = result.get("content")
    if not isinstance(content, list) or not content:
        return {}
    text = content[0].get("text") if isinstance(content[0], dict) else None
    if not isinstance(text, str):
        return {}
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def parse_mcp_log(path: Path) -> dict[str, bool]:
    requests: dict[int, dict[str, Any]] = {}
    status = {
        "model_loaded": False,
        "check_model": False,
        "simulate_model": False,
        "open_result": False,
        "create_plot": False,
        "open_model": False,
        "create_animation": False,
        "session_shutdown": False,
    }
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        request_id = record.get("id")
        if record.get("direction") == "request" and isinstance(request_id, int):
            requests[request_id] = record.get("params", {})
            continue
        if record.get("direction") != "response" or not isinstance(request_id, int):
            continue
        request = requests.get(request_id, {})
        name = request.get("name")
        arguments = request.get("arguments", {})
        payload = decode_response_payload(record)
        if name == "model_manager" and arguments.get("action") == "load_file":
            status["model_loaded"] = status["model_loaded"] or bool(payload.get("ok"))
        elif name == "check_model":
            status["check_model"] = bool(payload.get("ok"))
        elif name == "simulate_model":
            status["simulate_model"] = bool(payload.get("ok"))
        elif name == "call_code":
            run_result = payload.get("run_script_result", {})
            if not isinstance(run_result, dict):
                continue
            if "simulate" in run_result:
                status["simulate_model"] = bool(run_result.get("simulate"))
            status["open_result"] = status["open_result"] or bool(run_result.get("open_result"))
            status["create_plot"] = status["create_plot"] or bool(run_result.get("create_plot"))
            status["open_model"] = status["open_model"] or bool(
                run_result.get("open_model_diagram") or run_result.get("open_model")
            )
            status["create_animation"] = status["create_animation"] or bool(run_result.get("create_animation"))
        elif name == "session_manager" and arguments.get("action") == "shutdown":
            exit_api = payload.get("exit_api", {})
            status["session_shutdown"] = bool(payload.get("ok")) and (
                not isinstance(exit_api, dict) or bool(exit_api.get("ok", True))
            )
    return status


def build_smoke_command(
    profile: dict[str, Any], run_dir: Path, *, keep_session_open: bool = False
) -> list[str]:
    model_name = profile["generated_model_name"]
    command = [
        sys.executable,
        str(SMOKE_SCRIPT),
        "--model-file",
        str(BASE_MODEL_FILES[0]),
    ]
    if profile.get("execution_kind") != "direct_model":
        command.extend(["--extra-model-file", str(run_dir / "GeneratedProfile.mo")])
    command.extend([
        "--model-name", model_name,
        "--target-time", f"0,{profile.get('stop_time_s', 50)}",
        "--raw-output", str(run_dir / "raw" / "result.csv"),
        "--metrics-json", str(run_dir / "metrics" / "metrics.json"),
        "--log-output", str(run_dir / "logs" / "mcp.jsonl"),
        "--native-result-dir", str(run_dir / "native_result"),
        "--scene-id", str(profile["scenario_id"]),
        "--controller-id", str(profile["controller_id"]),
        "--gui-reset-windows",
    ])
    if not keep_session_open:
        command.append("--shutdown-session")
    variable_overrides = profile.get("variable_overrides", VARIABLE_OVERRIDES)
    for alias, variable in variable_overrides.items():
        command.extend(["--override-variable", f"{alias}={variable}"])
    for alias, variable in profile.get("extra_variables", {
        "position_error_norm": "position_error_norm",
        "rotor_speed_1": "rotor_speed[1]",
    }).items():
        command.extend(["--extra-variable", f"{alias}={variable}"])
    return command


def csv_summary(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) <= 10:
        raise ValueError("raw_result_has_too_few_rows")
    last = rows[-1]
    rotor_speed_text = last.get("rotor_speed_1", "").strip()
    summary = {
        "row_count": len(rows),
        "end_time_s": float(last["time"]),
        "position_end_m": [float(last["x"]), float(last["y"]), float(last["z"])],
        "position_ref_end_m": [float(last["x_ref"]), float(last["y_ref"]), float(last["z_ref"])],
        "position_error_norm_end_m": float(last["position_error_norm"]),
        "attitude_end_rad": [float(last["roll"]), float(last["pitch"]), float(last["yaw"])],
        "rotor_speed_1_end_rad_s": float(rotor_speed_text) if rotor_speed_text else None,
        **({"formation_error_end_m": float(last["formation_error_m"])} if "formation_error_m" in last else {}),
        **({"min_inter_uav_distance_end_m": float(last["min_inter_uav_distance_m"])} if "min_inter_uav_distance_m" in last else {}),
    }
    if "formation_error_m" in last:
        summary["max_formation_error_m"] = max(float(row["formation_error_m"]) for row in rows)
    if "min_inter_uav_distance_m" in last:
        summary["min_inter_uav_distance_m"] = min(float(row["min_inter_uav_distance_m"]) for row in rows)
    return summary


def resolve_native_result(run_dir: Path, model_name: str) -> Path:
    preferred = run_dir / "native_result" / model_name / "Result.msr"
    if preferred.is_file():
        return preferred
    # Sysplorer stores direct-model results under the unqualified class name,
    # while generated wrappers already use an unqualified model name.
    short_name = model_name.rsplit(".", 1)[-1]
    short_path = run_dir / "native_result" / short_name / "Result.msr"
    if short_path.is_file():
        return short_path
    manifest_path = run_dir / "native_result" / "native_result_manifest.json"
    if not manifest_path.is_file():
        return preferred
    manifest = read_json(manifest_path)
    value = manifest.get("native_result_file_windows") or manifest.get("native_result_file")
    if not isinstance(value, str) or not value:
        return preferred
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    candidate = candidate.resolve()
    results_root = (ROOT / "Results").resolve()
    if not candidate.is_relative_to(results_root):
        raise ValueError("native_result_manifest_outside_results")
    return candidate


def write_certification(run_dir: Path, profile: dict[str, Any]) -> dict[str, Any]:
    source_model = (
        ROOT / profile["source_model_file"]
        if profile.get("execution_kind") == "direct_model"
        else run_dir / "GeneratedProfile.mo"
    )
    raw = run_dir / "raw" / "result.csv"
    metrics_path = run_dir / "metrics" / "metrics.json"
    log = run_dir / "logs" / "mcp.jsonl"
    result = resolve_native_result(run_dir, profile["generated_model_name"])
    required = [source_model, raw, metrics_path, log, result]
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing_certification_artifacts: {missing}")
    mcp_status = parse_mcp_log(log)
    metrics = sanitize_json_value(read_json(metrics_path))
    write_strict_json(metrics_path, metrics)
    raw_summary = csv_summary(raw)
    max_position_error = metrics.get("max_position_error_m")
    max_tilt = metrics.get("max_tilt_rad")
    bounded_closed_loop = (
        math.isfinite(raw_summary["position_error_norm_end_m"])
        and raw_summary["position_error_norm_end_m"] <= 1.0
        and isinstance(max_position_error, (int, float))
        and math.isfinite(max_position_error)
        and max_position_error <= 5.0
        and isinstance(max_tilt, (int, float))
        and math.isfinite(max_tilt)
        and max_tilt <= 1.2
    )
    if profile.get("vehicle_count") == 3:
        formation_error = raw_summary.get("max_formation_error_m")
        min_distance = raw_summary.get("min_inter_uav_distance_m")
        bounded_closed_loop = (
            bounded_closed_loop
            and isinstance(formation_error, (int, float))
            and math.isfinite(formation_error)
            and formation_error <= 1.0
            and isinstance(min_distance, (int, float))
            and math.isfinite(min_distance)
            and min_distance >= 0.5
        )
    acceptance = {
        "model_loaded": mcp_status["model_loaded"],
        "check_model": mcp_status["check_model"],
        "simulate_model": mcp_status["simulate_model"],
        "raw_result_valid": metrics.get("valid") is True and metrics.get("nan_count") == 0,
        "native_result_present": result.stat().st_size > 0,
        "result_window_opened": mcp_status["open_result"],
        "plot_window_opened": mcp_status["create_plot"],
        "model_window_opened": mcp_status["open_model"],
        "animation_window_opened": mcp_status["create_animation"],
        "bounded_closed_loop": bounded_closed_loop,
    }
    accepted = all(acceptance.values())
    record = {
        "schema": "mosim.offline_profile_certification.v1",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "run_id": profile["run_id"],
        "profile_id": profile["profile_id"],
        "profile_kind": profile["profile_kind"],
        "controller_id": profile["controller_id"],
        "scenario_id": profile["scenario_id"],
        "output_variant": profile["output_variant"],
        "status": "accepted" if accepted else "blocked",
        "acceptance": acceptance,
        "animation_acceptance_rule": "CreateAnimation succeeds and the native animation window opens; playback is not required.",
        "session_cleanup": {
            "policy": "Certification runs request GUI reset and dedicated-session shutdown after evidence capture.",
            "shutdown_recorded": mcp_status["session_shutdown"],
        },
        "raw_summary": raw_summary,
        "selected_metrics": {
            key: metrics.get(key)
            for key in (
                "position_rmse_m", "steady_state_error_m", "max_position_error_m",
                "settling_time_s", "max_tilt_rad", "constraint_violation_count",
            )
        },
        "artifacts": {
            "model_source": source_model.relative_to(ROOT).as_posix(),
            "model_source_sha256": sha256(source_model),
            "raw_csv": raw.relative_to(ROOT).as_posix(),
            "raw_csv_sha256": sha256(raw),
            "metrics_json": metrics_path.relative_to(ROOT).as_posix(),
            "mcp_log": log.relative_to(ROOT).as_posix(),
            "native_result": result.relative_to(ROOT).as_posix(),
            "native_result_sha256": sha256(result),
        },
        "claim_boundary": (
            "Real offline MWORKS model/check/simulation/result/animation evidence only. "
            "It is not PX4, Gazebo, ROS1, mworks_live, or flight evidence."
        ),
    }
    output = run_dir / "CERTIFICATION.json"
    record = sanitize_json_value(record)
    write_strict_json(output, record)
    return record


def prepare_direct_profile(catalog: dict[str, Any], profile_id: str, run_id: str) -> dict[str, Any]:
    source = next(
        (item for item in catalog["certified_profiles"] if item.get("profile_id") == profile_id),
        None,
    )
    if not source or source.get("execution_kind") != "direct_model":
        raise ValueError("direct_certified_profile_not_found")
    run_dir = generator.OUTPUT_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    model_name = str(source["direct_model"])
    profile = {
        **source,
        "run_id": run_id,
        "profile_kind": "certified",
        "generated_model_name": model_name,
        "source_model_file": str(source["direct_model_file"]),
        "variable_overrides": {
            "x": "sensors1_1.PosMea[1]",
            "y": "sensors1_1.PosMea[2]",
            "z": "sensors1_1.PosMea[3]",
            "x_ref": "leader_x_ref",
            "y_ref": "leader_y_ref",
            "z_ref": "leader_z_ref",
            "roll": "sensors1_1.AngleMea[1]",
            "pitch": "sensors1_1.AngleMea[2]",
            "yaw": "sensors1_1.AngleMea[3]",
            "u1": "motor1_hover_sum.y",
            "u2": "motor2_hover_sum.y",
            "u3": "motor3_hover_sum.y",
            "u4": "motor4_hover_sum.y",
        },
        "extra_variables": {
            "position_error_norm": "formation_error_m",
            "rotor_speed_1": "actuator1_1.dcpm.wMechanical",
            "formation_error_m": "formation_error_m",
            "min_inter_uav_distance_m": "min_inter_uav_distance_m",
        },
    }
    generator.write_json(run_dir / "PROFILE.json", profile)
    return profile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certified-profile-id")
    parser.add_argument("--request-json", type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--reuse-generated", action="store_true")
    parser.add_argument("--record-only", action="store_true")
    parser.add_argument("--keep-session-open", action="store_true")
    args = parser.parse_args()
    if bool(args.certified_profile_id) == bool(args.request_json):
        parser.error("provide exactly one of --certified-profile-id or --request-json")

    run_dir = generator.OUTPUT_ROOT / args.run_id
    if not args.reuse_generated:
        catalog = generator.read_json(generator.CATALOG_PATH)
        certified = next(
            (item for item in catalog["certified_profiles"] if item.get("profile_id") == args.certified_profile_id),
            None,
        ) if args.certified_profile_id else None
        if certified and certified.get("execution_kind") == "direct_model":
            profile = prepare_direct_profile(catalog, args.certified_profile_id, args.run_id)
        else:
            request = (
                generator.certified_request(catalog, args.certified_profile_id, args.run_id)
                if args.certified_profile_id
                else generator.read_json(args.request_json)
            )
            request["run_id"] = args.run_id
            profile = generator.generate(request)
    else:
        profile = read_json(run_dir / "PROFILE.json")

    if not args.record_only:
        completed = subprocess.run(
            build_smoke_command(profile, run_dir, keep_session_open=args.keep_session_open),
            cwd=ROOT,
            text=True,
        )
        if completed.returncode != 0:
            return completed.returncode
    record = write_certification(run_dir, profile)
    print(json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if record["status"] == "accepted" else 2


if __name__ == "__main__":
    raise SystemExit(main())
