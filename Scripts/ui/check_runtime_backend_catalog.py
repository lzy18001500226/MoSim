#!/usr/bin/env python3
"""Validate QGC's copy-only runtime invocation registry without launching it."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = ROOT / "Config" / "control_platform" / "runtime_backend_catalog.json"
DEFAULT_OPERATOR_PROFILES = ROOT / "Config" / "profiles" / "operator_profiles.json"
DEFAULT_CONTROLLER_SCHEMES = ROOT / "Config" / "control_platform" / "control_scheme_catalog.json"
PREPARE_OPERATOR_RUN = ROOT / "Scripts" / "ui" / "prepare_operator_run.py"
EXPECTED_SCHEMA = "mosim.runtime_backend_catalog.v2"
INVOCATION_SCHEMA = "mosim.operator_invocation.v1"
SAFE_ENVIRONMENT_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SAFE_SHELL_TOKEN = re.compile(r"^[A-Za-z0-9_./:=+\-]+$")
SAFE_TASK_KEY = re.compile(r"^[a-z][a-z0-9_\-]{0,63}$")
MISSION_ADAPTER_MARKERS = (
    "MissionStatusChannel",
    "SafeStopChannel",
    "mission_status.finish",
)
FACTORY_L2_GRAPHICAL_C99_OPERATION = "factory_l2_graphical_px4ctrl_c99_figure8"
FACTORY_L2_FASTLIO_ALIGNMENT_Z_M = 0.035
QGC_DIFF_REALTIME_GOAL_SCRIPT = "Scripts/sunray/run_qgc_diff_realtime_goal_gate.sh"
QGC_REALTIME_GOAL_CONTRACT = {
    "input": "qgc_plan_view",
    "goal_topic": "/move_base_simple/goal",
    "goal_frame": "world",
}
QGC_REALTIME_GOAL_ROUTES = {
    "factory_l2_graphical_px4ctrl_c99_qgc_realtime_goal": {
        "runtime_profile_id": "sunray_ros1_factory_l2_graphical_px4ctrl_c99_qgc_realtime_goal_v1",
        "experiment_profile_id": "px4ctrl_graphical_c99_factory_qgc_realtime_goal_v1",
        "argument": "qgc_realtime_goal",
        "result_gate": "QGC_REALTIME_GOAL_RUNTIME_STATUS.json",
    },
    "factory_l2_graphical_px4ctrl_c99_diff_interactive_goal": {
        "runtime_profile_id": "sunray_ros1_factory_l2_graphical_px4ctrl_c99_diff_interactive_goal_v1",
        "experiment_profile_id": "px4ctrl_graphical_c99_factory_diff_interactive_goal_v1",
        "argument": "interactive_goal",
        "result_gate": "QGC_DIFF_REALTIME_GOAL_RUNTIME_STATUS.json",
    },
}
RVIZ_QGC_DISPLAY_PHASE1_ROUTE = {
    "operation_id": "factory_l2_graphical_px4ctrl_c99_rviz_qgc_display_phase1",
    "runtime_profile_id": "sunray_ros1_factory_l2_graphical_px4ctrl_c99_rviz_qgc_display_phase1_v1",
    "experiment_profile_id": "px4ctrl_graphical_c99_factory_rviz_qgc_display_phase1_v1",
    "argument": "rviz_qgc_display_phase1",
    "result_gate": "RVIZ_QGC_DISPLAY_PHASE1_RUNTIME_STATUS.json",
    "contract": {
        "input": "rviz_2d_nav_goal",
        "goal_topic": "/move_base_simple/goal",
        "goal_frame": "world",
    },
}


def _read_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"json_object_required:{path}")
    return data


def _inside_project(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT)
    except ValueError:
        return False
    return True


def _safe_token(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool)) and bool(SAFE_SHELL_TOKEN.fullmatch(str(value)))


def _validate_operator_contract(identifier: str, contract: Any, errors: list[str]) -> None:
    if not isinstance(contract, dict):
        errors.append(f"operator_contract_missing:{identifier}")
        return

    authority = contract.get("flight_authority")
    if authority not in {"qgc_native_manual", "mission_adapter"}:
        errors.append(f"operator_flight_authority_invalid:{identifier}:{authority}")
        return
    if authority == "qgc_native_manual":
        if contract.get("takeoff_owner") != "qgc_native":
            errors.append(f"manual_takeoff_owner_invalid:{identifier}")
        if contract.get("terminal_ack") != "qgc_vehicle_disarm":
            errors.append(f"manual_terminal_ack_invalid:{identifier}")
        if contract.get("safe_stop") != "qgc_native_land":
            errors.append(f"manual_safe_stop_invalid:{identifier}")
        return

    adapter_text = ""
    adapter_source = contract.get("mission_adapter_source")
    adapter_path = ROOT / str(adapter_source or "")
    if not adapter_path.is_file() or not _inside_project(adapter_path):
        errors.append(f"mission_adapter_source_missing_or_external:{identifier}")
    else:
        adapter_text = adapter_path.read_text(encoding="utf-8")
        for marker in MISSION_ADAPTER_MARKERS:
            if marker not in adapter_text:
                errors.append(f"mission_adapter_marker_missing:{identifier}:{marker}")
    if contract.get("takeoff_owner") != "mission_adapter":
        errors.append(f"automatic_takeoff_owner_invalid:{identifier}")
    if contract.get("terminal_ack") != "mission_status_channel_v1":
        errors.append(f"automatic_terminal_ack_invalid:{identifier}")
    if contract.get("safe_stop") != "safe_stop_channel_v1":
        errors.append(f"automatic_safe_stop_invalid:{identifier}")


def _validate_operator_invocation(identifier: str, invocation: Any, errors: list[str]) -> bool:
    if not isinstance(invocation, dict):
        errors.append(f"operator_invocation_missing:{identifier}")
        return False
    if invocation.get("schema") != INVOCATION_SCHEMA:
        errors.append(f"operator_invocation_schema_invalid:{identifier}")
    unexpected = set(invocation) - {"schema", "shell_environment", "arguments"}
    if unexpected:
        errors.append(f"operator_invocation_unknown_fields:{identifier}:{','.join(sorted(unexpected))}")

    environment = invocation.get("shell_environment")
    if not isinstance(environment, dict):
        errors.append(f"operator_invocation_environment_invalid:{identifier}")
    else:
        for name, value in environment.items():
            if not SAFE_ENVIRONMENT_NAME.fullmatch(str(name)):
                errors.append(f"operator_invocation_environment_name_invalid:{identifier}:{name}")
            if not _safe_token(value):
                errors.append(f"operator_invocation_environment_value_invalid:{identifier}:{name}")

    arguments = invocation.get("arguments")
    if not isinstance(arguments, list) or not arguments:
        errors.append(f"operator_invocation_arguments_missing:{identifier}")
    else:
        for index, value in enumerate(arguments):
            if not _safe_token(value):
                errors.append(f"operator_invocation_argument_invalid:{identifier}:{index}")
    return True


def _numbers_match(left: Any, right: Any) -> bool:
    try:
        return abs(float(left) - float(right)) <= 1e-6
    except (TypeError, ValueError):
        return False


def _validate_factory_l2_fastlio_alignment(
    identifier: str,
    operation_id: str,
    invocation: Any,
    errors: list[str],
) -> None:
    if operation_id != FACTORY_L2_GRAPHICAL_C99_OPERATION:
        return
    environment = invocation.get("shell_environment") if isinstance(invocation, dict) else None
    if not isinstance(environment, dict):
        return

    required = (
        "SUNRAY_UAV_INIT_X",
        "SUNRAY_UAV_INIT_Y",
        "FASTLIO_ALIGNMENT_ORIGIN_X",
        "FASTLIO_ALIGNMENT_ORIGIN_Y",
        "FASTLIO_ALIGNMENT_ORIGIN_Z",
    )
    missing = [name for name in required if name not in environment]
    for name in missing:
        errors.append(f"factory_l2_fastlio_alignment_origin_missing:{identifier}:{name}")
    if missing:
        return

    if not _numbers_match(
        environment["SUNRAY_UAV_INIT_X"], environment["FASTLIO_ALIGNMENT_ORIGIN_X"]
    ):
        errors.append(f"factory_l2_fastlio_alignment_origin_x_mismatch:{identifier}")
    if not _numbers_match(
        environment["SUNRAY_UAV_INIT_Y"], environment["FASTLIO_ALIGNMENT_ORIGIN_Y"]
    ):
        errors.append(f"factory_l2_fastlio_alignment_origin_y_mismatch:{identifier}")
    if not _numbers_match(environment["FASTLIO_ALIGNMENT_ORIGIN_Z"], FACTORY_L2_FASTLIO_ALIGNMENT_Z_M):
        errors.append(f"factory_l2_fastlio_alignment_origin_z_mismatch:{identifier}")
    if environment.get("ORCHESTRATOR_REQUIRE_ACTUATOR_TELEMETRY") != "false":
        errors.append(f"factory_l2_graphical_c99_no_fault_actuator_readiness_must_be_disabled:{identifier}")


def _validate_qgc_realtime_goal_route(identifier: str, entry: dict[str, Any], errors: list[str]) -> None:
    expected = QGC_REALTIME_GOAL_ROUTES.get(str(entry.get("operation_id", "")))
    if expected is None:
        return
    if identifier != expected["runtime_profile_id"]:
        errors.append(f"qgc_realtime_goal_runtime_profile_mismatch:{identifier}")
    if entry.get("experiment_profile_ids") != [expected["experiment_profile_id"]]:
        errors.append(f"qgc_realtime_goal_experiment_profile_mismatch:{identifier}")
    if entry.get("controller_ids") != ["px4ctrl"] or entry.get("vehicle_counts") != [1]:
        errors.append(f"qgc_realtime_goal_vehicle_or_controller_mismatch:{identifier}")
    if entry.get("project_script") != QGC_DIFF_REALTIME_GOAL_SCRIPT:
        errors.append(f"qgc_realtime_goal_wrapper_mismatch:{identifier}")
    invocation = entry.get("operator_invocation")
    if not isinstance(invocation, dict) or invocation.get("arguments") != [expected["argument"]]:
        errors.append(f"qgc_realtime_goal_invocation_mismatch:{identifier}")
    if entry.get("result_gate") != expected["result_gate"]:
        errors.append(f"qgc_realtime_goal_result_gate_mismatch:{identifier}")
    if entry.get("realtime_goal") != QGC_REALTIME_GOAL_CONTRACT:
        errors.append(f"qgc_realtime_goal_contract_mismatch:{identifier}")


def _validate_rviz_qgc_display_phase1_route(identifier: str, entry: dict[str, Any], errors: list[str]) -> None:
    if entry.get("operation_id") != RVIZ_QGC_DISPLAY_PHASE1_ROUTE["operation_id"]:
        return
    expected = RVIZ_QGC_DISPLAY_PHASE1_ROUTE
    if identifier != expected["runtime_profile_id"]:
        errors.append(f"rviz_qgc_display_phase1_runtime_profile_mismatch:{identifier}")
    if entry.get("experiment_profile_ids") != [expected["experiment_profile_id"]]:
        errors.append(f"rviz_qgc_display_phase1_experiment_profile_mismatch:{identifier}")
    if entry.get("controller_ids") != ["px4ctrl"] or entry.get("vehicle_counts") != [1]:
        errors.append(f"rviz_qgc_display_phase1_vehicle_or_controller_mismatch:{identifier}")
    if entry.get("project_script") != QGC_DIFF_REALTIME_GOAL_SCRIPT:
        errors.append(f"rviz_qgc_display_phase1_wrapper_mismatch:{identifier}")
    invocation = entry.get("operator_invocation")
    if not isinstance(invocation, dict) or invocation.get("arguments") != [expected["argument"]]:
        errors.append(f"rviz_qgc_display_phase1_invocation_mismatch:{identifier}")
    if entry.get("result_gate") != expected["result_gate"]:
        errors.append(f"rviz_qgc_display_phase1_result_gate_mismatch:{identifier}")
    if entry.get("realtime_goal") != expected["contract"]:
        errors.append(f"rviz_qgc_display_phase1_contract_mismatch:{identifier}")


def _operator_mode_matches_contract(mode: str, contract: Any) -> bool:
    if not isinstance(contract, dict):
        return False
    if mode == "qgc_manual":
        return contract.get("flight_authority") == "qgc_native_manual"
    if mode == "mission_adapter":
        return contract.get("flight_authority") == "mission_adapter"
    return False


def _load_controller_scheme_ids(path: Path, errors: list[str]) -> set[str]:
    try:
        catalog = _read_object(path)
    except (OSError, ValueError, json.JSONDecodeError):
        errors.append("controller_scheme_catalog_missing_or_invalid")
        return set()
    if catalog.get("schema") != "mosim.control_profile_catalog.v2":
        errors.append(f"controller_scheme_catalog_schema_invalid:{catalog.get('schema', '')}")
    schemes = catalog.get("schemes")
    if not isinstance(schemes, list) or not schemes:
        errors.append("controller_scheme_catalog_entries_missing")
        return set()
    identifiers: set[str] = set()
    for scheme in schemes:
        scheme_id = str(scheme.get("scheme_id", "")) if isinstance(scheme, dict) else ""
        if not scheme_id or scheme_id in identifiers:
            errors.append(f"controller_scheme_id_duplicate_or_missing:{scheme_id}")
        identifiers.add(scheme_id)
    declared_count = catalog.get("frozen_scheme_count")
    if declared_count != len(identifiers):
        errors.append(f"controller_scheme_count_mismatch:{declared_count}:{len(identifiers)}")
    return identifiers


def check(
    catalog_path: Path,
    operator_profiles_path: Path = DEFAULT_OPERATOR_PROFILES,
    controller_schemes_path: Path = DEFAULT_CONTROLLER_SCHEMES,
) -> dict[str, Any]:
    catalog = _read_object(catalog_path)
    operator_catalog = _read_object(operator_profiles_path)
    errors: list[str] = []
    controller_scheme_ids = _load_controller_scheme_ids(controller_schemes_path, errors)
    identifiers: set[str] = set()
    operations: set[str] = set()
    backends_by_profile: dict[str, list[dict[str, Any]]] = {}

    if not PREPARE_OPERATOR_RUN.is_file() or not _inside_project(PREPARE_OPERATOR_RUN):
        errors.append("operator_run_prepare_tool_missing")

    if catalog.get("schema") != EXPECTED_SCHEMA:
        errors.append(f"runtime_catalog_schema_invalid:{catalog.get('schema', '')}")
    if int(catalog.get("version", 0)) < 4:
        errors.append(f"runtime_catalog_version_invalid:{catalog.get('version', '')}")

    entries = catalog.get("runtime_profiles")
    if not isinstance(entries, list) or not entries:
        errors.append("runtime_profiles_missing")
        entries = []

    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("runtime_profile_not_object")
            continue
        identifier = str(entry.get("runtime_profile_id", ""))
        if not identifier or identifier in identifiers:
            errors.append(f"duplicate_or_missing_runtime_profile_id:{identifier}")
        identifiers.add(identifier)
        operation_id = str(entry.get("operation_id", ""))
        if not operation_id or operation_id in operations:
            errors.append(f"duplicate_or_missing_operation_id:{operation_id}")
        operations.add(operation_id)

        if entry.get("launcher") != "wsl_project_script":
            errors.append(f"unsupported_launcher:{identifier}")
        if "command" in entry or "arguments" in entry:
            errors.append(f"arbitrary_command_surface_forbidden:{identifier}")
        script_text = str(entry.get("project_script", ""))
        script_path = ROOT / script_text
        if not script_text.endswith((".sh", ".ps1")) or not script_path.is_file() or not _inside_project(script_path):
            errors.append(f"project_script_missing_or_external:{identifier}")
        if not entry.get("experiment_profile_ids") or not entry.get("controller_ids"):
            errors.append(f"profile_or_controller_allowlist_missing:{identifier}")
        vehicle_counts = entry.get("vehicle_counts")
        if not isinstance(vehicle_counts, list) or not set(vehicle_counts) <= {1, 3}:
            errors.append(f"unaccepted_vehicle_scale:{identifier}")

        _validate_operator_contract(identifier, entry.get("operator_contract"), errors)
        _validate_factory_l2_fastlio_alignment(
            identifier, operation_id, entry.get("operator_invocation"), errors
        )
        _validate_qgc_realtime_goal_route(identifier, entry, errors)
        _validate_rviz_qgc_display_phase1_route(identifier, entry, errors)
        for profile_id in entry.get("experiment_profile_ids", []):
            profile_path = ROOT / "Config" / "profiles" / "experiments" / f"{profile_id}.json"
            if not profile_path.is_file():
                errors.append(f"experiment_profile_missing:{identifier}:{profile_id}")
                continue
            profile = _read_object(profile_path).get("experiment_profile", {})
            if profile.get("id") != profile_id:
                errors.append(f"experiment_profile_id_mismatch:{identifier}:{profile_id}")
            declared_count = profile.get("vehicle_count", 1)
            if not isinstance(declared_count, int) or declared_count not in vehicle_counts:
                errors.append(f"experiment_vehicle_count_mismatch:{identifier}:{profile_id}:{declared_count}")
            backends_by_profile.setdefault(str(profile_id), []).append(entry)

    profiles = operator_catalog.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        errors.append("operator_profile_catalog_missing")
        profiles = []
    seen_operator_profiles: set[str] = set()
    published_controller_scheme_ids: set[str] = set()
    enabled_controller_scheme_ids: set[str] = set()
    enabled_count = 0
    enabled_invocation_count = 0
    operator_publication_matrix: list[dict[str, Any]] = []
    for item in profiles:
        if not isinstance(item, dict):
            errors.append("operator_profile_not_object")
            continue
        profile_id = str(item.get("profile_id", ""))
        if not profile_id or profile_id in seen_operator_profiles:
            errors.append(f"duplicate_or_missing_operator_profile_id:{profile_id}")
        seen_operator_profiles.add(profile_id)
        profile_path = ROOT / str(item.get("profile_path", ""))
        if not profile_path.is_file() or not _inside_project(profile_path):
            errors.append(f"operator_profile_path_missing_or_external:{profile_id}")
            continue
        experiment = _read_object(profile_path).get("experiment_profile", {})
        if experiment.get("id") != profile_id:
            errors.append(f"operator_profile_id_mismatch:{profile_id}:{experiment.get('id', '')}")
        if item.get("enabled") is True and experiment.get("profile_status") == "blocked":
            errors.append(f"operator_profile_enabled_while_experiment_blocked:{profile_id}")

        controller_scheme_id = str(item.get("controller_scheme_id", ""))
        if not controller_scheme_id:
            errors.append(f"operator_profile_controller_scheme_missing:{profile_id}")
        elif controller_scheme_id not in controller_scheme_ids:
            errors.append(f"operator_profile_controller_scheme_unknown:{profile_id}:{controller_scheme_id}")
        else:
            published_controller_scheme_ids.add(controller_scheme_id)
            if item.get("enabled") is True:
                enabled_controller_scheme_ids.add(controller_scheme_id)
        task_key = str(item.get("task_key", ""))
        if not SAFE_TASK_KEY.fullmatch(task_key):
            errors.append(f"operator_profile_task_key_invalid:{profile_id}:{task_key}")

        matches = backends_by_profile.get(profile_id, [])
        if not matches:
            errors.append(f"operator_profile_runtime_missing:{profile_id}")
            continue
        if len(matches) != 1:
            errors.append(f"operator_profile_runtime_ambiguous:{profile_id}")
            continue
        backend = matches[0]
        if experiment.get("vehicle_count", 1) not in backend.get("vehicle_counts", []):
            errors.append(f"operator_profile_vehicle_count_mismatch:{profile_id}")
        mode = str(item.get("operator_mode", ""))
        if not _operator_mode_matches_contract(mode, backend.get("operator_contract")):
            errors.append(f"operator_profile_authority_mismatch:{profile_id}:{mode}")

        invocation = backend.get("operator_invocation")
        operator_contract = backend.get("operator_contract")
        operator_contract = operator_contract if isinstance(operator_contract, dict) else {}
        backend_vehicle_counts = backend.get("vehicle_counts")
        matrix_vehicle_count = experiment.get("vehicle_count")
        if (
            not isinstance(matrix_vehicle_count, int)
            and isinstance(backend_vehicle_counts, list)
            and len(backend_vehicle_counts) == 1
        ):
            matrix_vehicle_count = backend_vehicle_counts[0]
        operator_publication_matrix.append(
            {
                "experiment_profile_id": profile_id,
                "publication_state": "enabled" if item.get("enabled") is True else "disabled",
                "disabled_reason": str(item.get("disabled_reason", "")),
                "experiment_profile_status": str(experiment.get("profile_status", "not_declared")),
                "vehicle_count": matrix_vehicle_count,
                "operator_mode": mode,
                "runtime_profile_id": str(backend.get("runtime_profile_id", "")),
                "operation_id": str(backend.get("operation_id", "")),
                "flight_authority": str(operator_contract.get("flight_authority", "")),
                "evidence_classification": "source_static_only",
            }
        )
        if item.get("enabled") is True:
            enabled_count += 1
            if _validate_operator_invocation(str(backend.get("runtime_profile_id", "")), invocation, errors):
                enabled_invocation_count += 1
            serialized = json.dumps(
                {"project_script": backend.get("project_script"), "operator_invocation": invocation},
                ensure_ascii=False,
            ).lower()
            if any(
                forbidden in serialized
                for forbidden in (
                    "run_orchestrated_runtime",
                    "orchestrator_client",
                    "run_qgc_with_ue",
                    "attach_orchestrated_displays",
                )
            ):
                errors.append(f"operator_invocation_forbidden_runtime_owner:{profile_id}")
        elif invocation is not None:
            _validate_operator_invocation(str(backend.get("runtime_profile_id", "")), invocation, errors)

    for profile_id in sorted(backends_by_profile):
        if profile_id not in seen_operator_profiles:
            errors.append(f"runtime_profile_not_operator_published:{profile_id}")

    return {
        "schema": "mosim.runtime_backend_source_gate.v2",
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "runtime_profile_count": len(identifiers),
        "operator_profile_count": len(seen_operator_profiles),
        "enabled_operator_profile_count": enabled_count,
        "enabled_operator_invocation_count": enabled_invocation_count,
        "operator_publication_matrix": operator_publication_matrix,
        "controller_scheme_count": len(controller_scheme_ids),
        "published_controller_scheme_count": len(published_controller_scheme_ids),
        "enabled_controller_scheme_count": len(enabled_controller_scheme_ids),
        "shared_gazebo_px4_touched": False,
        "actual_end_to_end_runtime_accepted": False,
        "claim_ceiling": "Copy-only QGC invocation contract and source allowlist; no runtime launch, readiness, controller, planner, or flight acceptance was performed.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--operator-profiles", type=Path, default=DEFAULT_OPERATOR_PROFILES)
    parser.add_argument("--controller-schemes", type=Path, default=DEFAULT_CONTROLLER_SCHEMES)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = check(
        args.catalog,
        operator_profiles_path=args.operator_profiles,
        controller_schemes_path=args.controller_schemes,
    )
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
