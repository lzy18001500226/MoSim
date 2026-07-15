"""Validate MoSim ExperimentProfile config files.

This checker is intentionally static. It proves that an experiment intent is
well-formed enough to be launched by a future orchestrator; it does not prove
runtime success.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = ROOT / "Config" / "profiles" / "catalog.json"
DEFAULT_EXPERIMENT_DIR = ROOT / "Config" / "profiles" / "experiments"
DEFAULT_RUNTIME_LOG_EXPORTS = ROOT / "Config" / "profiles" / "runtime_log_exports.json"
DEFAULT_TRACKING_SOURCES = ROOT / "Config" / "profiles" / "tracking_sources.json"
DEFAULT_CONTROL_MODULE_REGISTRY = ROOT / "Config" / "control_platform" / "control_module_registry.json"
ACTIVE_PROFILE_STATUSES = {"active", "implemented", "accepted"}
BLOCKED_PROFILE_STATUSES = {"blocked", "archived"}


SLOT_TO_CATALOG_SECTION = {
    "scenario_profile": "scenario_profiles",
    "plant_profile": "plant_profiles",
    "sensor_profile": "sensor_profiles",
    "state_source_profile": "state_source_profiles",
    "height_source_profile": "height_source_profiles",
    "truth_profile": "truth_profiles",
    "frequency_profile": "frequency_profiles",
    "trajectory_profile": "trajectory_profiles",
    "planner_profile": "planner_profiles",
    "controller_profile": "controller_profiles",
    "augmentation_profile": "augmentation_profiles",
    "safety_profile": "safety_profiles",
    "adapter_profile": "adapter_profiles",
    "fault_profile": "fault_profiles",
    "disturbance_profile": "disturbance_profiles",
    "display_profile": "display_profiles",
    "evaluation_profile": "evaluation_profiles",
    "runtime_profile": "runtime_profiles",
    "runtime_export_profile": "runtime_export_profiles",
    "evidence_profile": "evidence_profiles",
}


OPTIONAL_SLOT_TO_CATALOG_SECTION = {
    "localization_eval_profile": "state_source_profiles",
}


REQUIRED_TOP_LEVEL_FIELDS = [
    "id",
    "version",
    "description",
    "goal",
    *SLOT_TO_CATALOG_SECTION.keys(),
]


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def canonical_hash(data: Any) -> str:
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def catalog_entry(catalog: dict[str, Any], section: str, profile_id: str) -> dict[str, Any] | None:
    entries = catalog.get(section)
    if not isinstance(entries, dict):
        return None
    entry = entries.get(profile_id)
    return entry if isinstance(entry, dict) else None


def add_error(errors: list[dict[str, str]], code: str, message: str) -> None:
    errors.append({"code": code, "message": message})


def add_warning(warnings: list[dict[str, str]], code: str, message: str) -> None:
    warnings.append({"code": code, "message": message})


def has_real_source_basis(entry: dict[str, Any]) -> bool:
    source_basis = entry.get("source_basis", [])
    if not isinstance(source_basis, list):
        return False
    return any(
        isinstance(item, str) and item and not item.startswith("pending_")
        for item in source_basis
    )


def rejection_target(error_code: str, profile: dict[str, Any]) -> str | None:
    if error_code.startswith("C-CTRL"):
        return str(profile.get("controller_profile"))
    if error_code.startswith("C-REF"):
        return str(profile.get("controller_profile"))
    if error_code.startswith("C-AUG"):
        return str(profile.get("augmentation_profile"))
    if error_code.startswith("C-OUT"):
        return str(profile.get("adapter_profile"))
    if error_code.startswith("C-STATE"):
        return str(profile.get("state_source_profile"))
    if error_code.startswith("C-TRUTH"):
        return str(profile.get("truth_profile"))
    if error_code.startswith("C-HYBRID"):
        return str(profile.get("height_source_profile"))
    if error_code.startswith("C-SAFE"):
        return str(profile.get("safety_profile"))
    if error_code.startswith("C-SWARM"):
        return str(profile.get("scenario_profile"))
    if error_code.startswith("C-DISPLAY"):
        return str(profile.get("display_profile"))
    if error_code.startswith("C-EVAL"):
        return str(profile.get("evaluation_profile"))
    if error_code.startswith("C-EXPORT"):
        return str(profile.get("runtime_export_profile"))
    if error_code.startswith("C-LOG"):
        return str(profile.get("runtime_export_profile"))
    if error_code.startswith("C-TRACK"):
        return str(profile.get("runtime_export_profile"))
    if error_code.startswith("C-PLAN"):
        return str(profile.get("planner_profile"))
    if error_code.startswith("C-LIO"):
        return str(profile.get("localization_eval_profile"))
    if error_code.startswith("C-TRAJ"):
        return str(profile.get("trajectory_profile"))
    return str(profile.get("id"))


def build_rejection(profile: dict[str, Any], errors: list[dict[str, str]]) -> dict[str, Any] | None:
    if not errors:
        return None
    first = errors[0]
    return {
        "planned_run_id": f"<run_id_for_{profile.get('id', 'unknown_experiment')}>",
        "experiment_profile_id": profile.get("id"),
        "rejected_stage": "compatibility_check",
        "rejected_profile": rejection_target(first["code"], profile),
        "reason_code": first["code"],
        "human_reason": first["message"],
        "safe_alternative_profile": "px4_mavros_fused_v1"
        if first["code"] in {"C-STATE-01", "C-TRUTH-01", "C-HYBRID-01"}
        else None,
        "control_started": False,
    }


def experiment_profile_status(profile: dict[str, Any]) -> str:
    return str(profile.get("profile_status", "active")).strip().lower()


def registry_profiles(registry: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not isinstance(registry, dict):
        return {}
    modules = registry.get("modules")
    if not isinstance(modules, list):
        return {}
    return {
        str(module.get("profile_id")): module
        for module in modules
        if isinstance(module, dict) and module.get("profile_id")
    }


def build_launch_plan_skeleton(
    profile: dict[str, Any],
    resolved: dict[str, dict[str, Any]],
    experiment_hash: str,
) -> dict[str, Any]:
    steps: list[dict[str, Any]] = [
        {
            "id": "gazebo",
            "template": "sunray_gazebo.launch",
            "profile": profile["plant_profile"],
            "expected_backend": resolved["plant_profile"].get("plant_backend"),
        },
        {
            "id": "mavros",
            "template": "mavros_px4.launch",
            "profile": "px4_mavros_v1",
            "expected_state_topic": resolved["state_source_profile"].get("pose_velocity_topic"),
        },
    ]

    if profile["planner_profile"] != "none":
        steps.append(
            {
                "id": "planner",
                "template": "planner_adapter.launch",
                "profile": profile["planner_profile"],
            }
        )

    localization_eval = resolved.get("localization_eval_profile")
    state_source_group = resolved["state_source_profile"].get("group")
    if localization_eval is not None or state_source_group in {"C", "D", "E"}:
        steps.append(
            {
                "id": "fastlio",
                "template": "fastlio_review_or_ekf_bridge.launch",
                "profile": profile.get("localization_eval_profile", profile["state_source_profile"]),
                "mode": "evaluation_only" if localization_eval is not None else "state_source_bridge",
                "frame_semantics": (localization_eval or resolved["state_source_profile"]).get("frame_semantics"),
            }
        )

    steps.extend(
        [
            {
                "id": "trajectory",
                "template": "trajectory_server.launch",
                "profile": profile["trajectory_profile"],
            },
            {
                "id": "controller",
                "template": "controller_host.launch",
                "profile": profile["controller_profile"],
                "output_interface": resolved["controller_profile"].get("output_interface"),
            },
            {
                "id": "adapter",
                "template": "mavros_command_adapter.launch",
                "profile": profile["adapter_profile"],
                "output_backend": resolved["adapter_profile"].get("output_backend"),
            },
            {
                "id": "display",
                "template": "rviz_review.launch",
                "profile": profile["display_profile"],
            },
        ]
    )

    return {
        "launch_plan": {
            "run_id": f"<run_id_for_{profile['id']}>",
            "experiment_profile_id": profile["id"],
            "experiment_profile_hash": experiment_hash,
            "goal": profile.get("goal"),
            "steps": steps,
            "forbidden_claims": profile.get("forbidden_claims", []),
        }
    }


def build_run_manifest_skeleton(
    profile: dict[str, Any],
    resolved: dict[str, dict[str, Any]],
    experiment_hash: str,
) -> dict[str, Any]:
    slots_for_hash = {
        **SLOT_TO_CATALOG_SECTION,
        **{slot: section for slot, section in OPTIONAL_SLOT_TO_CATALOG_SECTION.items() if slot in profile},
    }
    profile_hashes = {
        slot: canonical_hash({"id": profile[slot], "body": resolved[slot]})
        for slot in slots_for_hash
    }
    state_and_truth = {
        "state_source_profile": profile["state_source_profile"],
        "height_source_profile": profile["height_source_profile"],
        "truth_profile": profile["truth_profile"],
        "leaderboard_group": resolved["evaluation_profile"].get("leaderboard_group"),
    }
    if "localization_eval_profile" in profile:
        state_and_truth["localization_eval_profile"] = profile["localization_eval_profile"]
    runtime_export = resolved["runtime_export_profile"]
    controller = resolved["controller_profile"]
    augmentation = resolved["augmentation_profile"]
    runtime_overrides_by_controller = augmentation.get("runtime_core_profile_overrides_by_controller", {})
    runtime_core_override = None
    if isinstance(runtime_overrides_by_controller, dict):
        value = runtime_overrides_by_controller.get(profile["controller_profile"])
        if isinstance(value, str) and value:
            runtime_core_override = value
    if runtime_core_override is None:
        runtime_core_override = augmentation.get("runtime_core_profile_override")

    return {
        "run_manifest": {
            "run_id": f"<run_id_for_{profile['id']}>",
            "experiment_profile_id": profile["id"],
            "experiment_profile_hash": experiment_hash,
            "profile_hashes": profile_hashes,
            "source_state": {
                "git_commit": "<commit-or-dirty>",
                "source_hashes": "<source_hashes.json>",
            },
            "runtime": {
                "runtime_profile": profile["runtime_profile"],
                "os": resolved["runtime_profile"].get("os"),
                "ros": resolved["runtime_profile"].get("ros"),
                "gazebo": resolved["runtime_profile"].get("gazebo"),
            },
            "runtime_export": {
                "runtime_export_profile": profile["runtime_export_profile"],
                "runtime_log_profile": runtime_export.get("runtime_log_profile"),
                "tracking_source_profile": runtime_export.get("tracking_source_profile"),
                "required_artifact_slots": runtime_export.get("required_artifact_slots", []),
            },
            "state_and_truth": state_and_truth,
            "evaluation": {
                "evaluation_profile": profile["evaluation_profile"],
                "required_metrics": resolved["evaluation_profile"].get("metrics", []),
            },
            "controller": {
                "controller_profile": profile["controller_profile"],
                "controller_id": controller.get("controller_id"),
                "controller_family": controller.get("controller_family"),
                "chain_position": controller.get("chain_position"),
                "implementation": controller.get("implementation"),
                "implementation_status": controller.get("implementation_status", "accepted"),
                "g9_task": controller.get("g9_task"),
                "source_basis_required": controller.get("source_basis_required", False),
                "source_basis": controller.get("source_basis", []),
                "mworks_codegen_route": controller.get("mworks_codegen_route"),
                "acceptance_tiers": controller.get("acceptance_tiers", []),
            },
            "augmentation": {
                "augmentation_profile": profile["augmentation_profile"],
                "augmentation_id": augmentation.get("augmentation_id"),
                "module_family": augmentation.get("module_family"),
                "chain_position": augmentation.get("chain_position"),
                "implementation_status": augmentation.get("implementation_status", "accepted"),
                "g9_task": augmentation.get("g9_task"),
                "g10_task": augmentation.get("g10_task"),
                "source_basis_required": augmentation.get("source_basis_required", False),
                "source_basis": augmentation.get("source_basis", []),
                "compatible_controller_profiles": augmentation.get("compatible_controller_profiles", []),
                "runtime_core_profile_override": runtime_core_override,
                "runtime_core_profile_overrides_by_controller": runtime_overrides_by_controller,
                "acceptance_tiers": augmentation.get("acceptance_tiers", []),
            },
            "trajectory_contract": {
                "trajectory_profile": profile["trajectory_profile"],
                "reference_rate_hz": resolved["trajectory_profile"].get("reference_rate_hz"),
                "duration_s": resolved["trajectory_profile"].get("duration_s"),
                "continuity_required": resolved["trajectory_profile"].get("continuity_required", {}),
                "constraints": resolved["trajectory_profile"].get("constraints", {}),
            },
            "evidence": {
                "required_artifacts": resolved["evidence_profile"].get("required_artifacts", []),
                "metrics": "metrics.json",
                "threshold_report": "threshold_report.json",
                "tracking_log": "tracking.csv",
                "localization_log": "raw/localization.csv",
                "map_summary": "raw/map_summary.json",
                "review": "review.md",
            },
            "forbidden_claims": profile.get("forbidden_claims", []),
        }
    }


def validate_experiment(
    path: Path,
    catalog: dict[str, Any],
    tracking_sources: dict[str, Any],
    runtime_log_exports: dict[str, Any] | None = None,
    control_module_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw = load_json(path)
    profile = raw.get("experiment_profile") if isinstance(raw, dict) else None
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if not isinstance(profile, dict):
        add_error(errors, "SCHEMA-ROOT-01", "root object must contain experiment_profile")
        return {
            "path": str(path),
            "ok": False,
            "experiment_id": None,
            "experiment_profile_hash": None,
            "errors": errors,
            "warnings": warnings,
        }

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in profile:
            add_error(errors, "SCHEMA-FIELD-01", f"missing required field: {field}")

    experiment_id = profile.get("id")
    if not isinstance(experiment_id, str) or not experiment_id:
        add_error(errors, "SCHEMA-ID-01", "experiment id must be a non-empty string")

    profile_status = experiment_profile_status(profile)
    if profile_status in BLOCKED_PROFILE_STATUSES:
        add_error(
            errors,
            "PROFILE-STATUS-01",
            f"experiment_profile={experiment_id} has profile_status={profile_status}; it is retained for evidence/audit only and must not enter active launch/preflight batches",
        )
    elif profile_status not in ACTIVE_PROFILE_STATUSES:
        add_error(
            errors,
            "PROFILE-STATUS-02",
            f"experiment_profile={experiment_id} has unsupported profile_status={profile_status}",
        )

    resolved: dict[str, dict[str, Any]] = {}
    for slot, section in SLOT_TO_CATALOG_SECTION.items():
        profile_id = profile.get(slot)
        if not isinstance(profile_id, str) or not profile_id:
            add_error(errors, "SCHEMA-SLOT-01", f"{slot} must be a non-empty registered id")
            continue
        entry = catalog_entry(catalog, section, profile_id)
        if entry is None:
            add_error(errors, "PROFILE-ID-01", f"{slot}={profile_id} is not registered in {section}")
            continue
        resolved[slot] = entry

    for slot, section in OPTIONAL_SLOT_TO_CATALOG_SECTION.items():
        if slot not in profile:
            continue
        profile_id = profile.get(slot)
        if not isinstance(profile_id, str) or not profile_id:
            add_error(errors, "SCHEMA-SLOT-01", f"{slot} must be a non-empty registered id")
            continue
        entry = catalog_entry(catalog, section, profile_id)
        if entry is None:
            add_error(errors, "PROFILE-ID-01", f"{slot}={profile_id} is not registered in {section}")
            continue
        resolved[slot] = entry

    if errors:
        return {
            "path": str(path),
            "ok": False,
            "experiment_id": experiment_id,
            "experiment_profile_hash": canonical_hash(profile),
            "errors": errors,
            "warnings": warnings,
            "profile_rejection": build_rejection(profile, errors),
        }

    controller = resolved["controller_profile"]
    augmentation = resolved["augmentation_profile"]
    trajectory = resolved["trajectory_profile"]
    adapter = resolved["adapter_profile"]
    state_source = resolved["state_source_profile"]
    height_source = resolved["height_source_profile"]
    truth = resolved["truth_profile"]
    planner = resolved["planner_profile"]
    scenario = resolved["scenario_profile"]
    safety = resolved["safety_profile"]
    display = resolved["display_profile"]
    runtime = resolved["runtime_profile"]
    runtime_export = resolved["runtime_export_profile"]
    evaluation = resolved["evaluation_profile"]
    evidence = resolved["evidence_profile"]
    localization_eval = resolved.get("localization_eval_profile")
    required_reference = set(controller.get("required_reference", []))
    provided_reference = set(trajectory.get("provides_reference", []))
    missing_reference = sorted(required_reference - provided_reference)
    if missing_reference:
        add_error(
            errors,
            "C-REF-01",
            "controller requires reference fields not provided by trajectory: "
            + ", ".join(missing_reference),
        )

    controller_status = str(controller.get("implementation_status", "accepted"))
    if controller_status not in {"implemented", "accepted"}:
        add_error(
            errors,
            "C-CTRL-01",
            f"controller_profile={profile['controller_profile']} has implementation_status={controller_status}; "
            "finish source audit, implementation, and interface evidence before using it in an active ExperimentProfile",
        )

    if (
        controller_status in {"implemented", "accepted"}
        and controller.get("source_basis_required")
        and not has_real_source_basis(controller)
    ):
        add_error(
            errors,
            "C-CTRL-02",
            f"controller_profile={profile['controller_profile']} requires source_basis before execution",
        )

    trajectory_rate = trajectory.get("reference_rate_hz")
    expected_rate = resolved["frequency_profile"].get("trajectory_evaluation_rate_hz")
    if trajectory_rate != expected_rate:
        add_error(
            errors,
            "C-TRAJ-01",
            f"trajectory reference_rate_hz={trajectory_rate} does not match frequency trajectory_evaluation_rate_hz={expected_rate}",
        )

    duration_s = trajectory.get("duration_s")
    if not isinstance(duration_s, (int, float)) or duration_s <= 0:
        add_error(errors, "C-TRAJ-02", "trajectory duration_s must be a positive number")

    continuity = trajectory.get("continuity_required")
    if not isinstance(continuity, dict):
        add_error(errors, "C-TRAJ-03", "trajectory must declare continuity_required")
    else:
        source_type = str(trajectory.get("source_type", ""))
        discontinuity_expected = bool(trajectory.get("discontinuity_expected", False))
        if source_type != "analytic_step" and any(value is False for value in continuity.values()):
            add_error(
                errors,
                "C-TRAJ-04",
                "non-step trajectory cannot declare discontinuous position/velocity/acceleration reference",
            )
        if source_type == "analytic_step" and not discontinuity_expected:
            add_error(errors, "C-TRAJ-05", "step trajectory must declare discontinuity_expected=true")

    constraints = trajectory.get("constraints")
    if not isinstance(constraints, dict):
        add_error(errors, "C-TRAJ-06", "trajectory must declare constraints")
    else:
        for field in ("max_velocity_mps", "max_acceleration_mps2", "max_yaw_rate_radps"):
            value = constraints.get(field)
            if not isinstance(value, (int, float)) or value <= 0:
                add_error(errors, "C-TRAJ-07", f"trajectory constraint {field} must be a positive number")

    controller_output = controller.get("output_interface")
    adapter_input = adapter.get("input_interface")
    if controller_output != adapter_input:
        add_error(
            errors,
            "C-OUT-01",
            f"controller output_interface={controller_output} but adapter input_interface={adapter_input}",
        )

    adapter_id = profile["adapter_profile"]
    if adapter_id not in controller.get("compatible_adapters", []):
        add_error(errors, "C-OUT-02", f"adapter {adapter_id} is not listed as controller-compatible")

    safety_id = profile["safety_profile"]
    if safety_id not in controller.get("compatible_safety", []):
        add_error(errors, "C-SAFE-02", f"safety {safety_id} is not listed as controller-compatible")

    augmentation_id = profile["augmentation_profile"]
    if augmentation_id not in controller.get("compatible_augmentations", []):
        add_error(
            errors,
            "C-AUG-01",
            f"augmentation {augmentation_id} is not listed as controller-compatible",
        )
    if augmentation_id != "none":
        augmentation_status = str(augmentation.get("implementation_status", "accepted"))
        if augmentation_status not in {"implemented", "accepted"}:
            add_error(
                errors,
                "C-AUG-02",
                f"augmentation_profile={augmentation_id} has implementation_status={augmentation_status}; "
                "finish source audit, implementation, and interface evidence before using it in an active ExperimentProfile",
            )
        if (
            augmentation_status in {"implemented", "accepted"}
            and augmentation.get("source_basis_required")
            and not has_real_source_basis(augmentation)
        ):
            add_error(
                errors,
                "C-AUG-03",
                f"augmentation_profile={augmentation_id} requires source_basis before execution",
            )

    if not state_source.get("allowed_for_control", False):
        add_error(
            errors,
            "C-STATE-01",
            f"state_source_profile={profile['state_source_profile']} is not allowed for controller state",
        )

    if state_source.get("debug_only") and evaluation.get("leaderboard_group") != "debug":
        add_error(
            errors,
            "C-TRUTH-01",
            "debug-only truth/control state cannot enter a non-debug evaluation group",
        )

    if state_source.get("group") == "E" and height_source.get("height_group") != "hybrid_z":
        add_error(errors, "C-HYBRID-01", "hybrid state source requires a hybrid-Z height_source_profile")

    if evaluation.get("leaderboard_group") == "fastlio_eval_only" and localization_eval is None:
        add_error(errors, "C-LIO-01", "FAST-LIO evaluation-only metrics require localization_eval_profile")

    if localization_eval is not None and not localization_eval.get("allowed_for_control", False):
        add_warning(
            warnings,
            "LIO-EVAL-01",
            "localization_eval_profile is evaluation-only and will not be used as controller state",
        )

    if truth.get("control_input_allowed", False):
        add_error(errors, "C-TRUTH-02", "truth_profile must not be allowed as controller input")

    if planner.get("owns_mavros_control", False):
        add_error(errors, "C-PLAN-01", "planner_profile must not own MAVROS control publishing")

    if safety.get("requires_geofence") and not scenario.get("has_geofence"):
        add_error(errors, "C-SAFE-01", "safety_profile requires geofence but scenario_profile has none")

    if display.get("requires_ue_bridge") and not runtime.get("ue_bridge"):
        add_error(errors, "C-DISPLAY-01", "display_profile requires UE bridge but runtime_profile has none")

    if runtime_export.get("runtime_profile") != profile["runtime_profile"]:
        add_error(
            errors,
            "C-EXPORT-01",
            f"runtime_export_profile expects runtime_profile={runtime_export.get('runtime_profile')} but experiment uses {profile['runtime_profile']}",
        )

    required_export_slots_raw = runtime_export.get("required_artifact_slots")
    required_export_slots = required_export_slots_raw if isinstance(required_export_slots_raw, list) else []
    exported_artifacts = runtime_export.get("exported_artifacts")
    if not isinstance(required_export_slots_raw, list) or not required_export_slots:
        add_error(errors, "C-EXPORT-02", "runtime_export_profile must declare required_artifact_slots")
    if not isinstance(exported_artifacts, dict):
        add_error(errors, "C-EXPORT-03", "runtime_export_profile must declare exported_artifacts")
    else:
        missing_export_slots = sorted(slot for slot in required_export_slots if slot not in exported_artifacts)
        if missing_export_slots:
            add_error(
                errors,
                "C-EXPORT-04",
                "runtime_export_profile missing exported_artifacts for slots: " + ", ".join(missing_export_slots),
            )
        for slot, item in exported_artifacts.items():
            destination = item.get("destination") if isinstance(item, dict) else None
            producer = item.get("producer") if isinstance(item, dict) else None
            command_template = item.get("command_template") if isinstance(item, dict) else None
            if not isinstance(destination, str) or not destination:
                add_error(errors, "C-EXPORT-05", f"runtime export slot {slot} must declare destination")
            if not isinstance(producer, str) or not producer:
                add_error(errors, "C-EXPORT-06", f"runtime export slot {slot} must declare producer")
            if not isinstance(command_template, str) or not command_template:
                add_error(errors, "C-EXPORT-07", f"runtime export slot {slot} must declare command_template")

    runtime_log_profile_id = runtime_export.get("runtime_log_profile")
    if not isinstance(runtime_log_profile_id, str) or not runtime_log_profile_id:
        add_error(errors, "C-EXPORT-08", "runtime_export_profile must bind a runtime_log_profile")
    else:
        runtime_log_profiles = (
            runtime_log_exports.get("profiles")
            if isinstance(runtime_log_exports, dict)
            else None
        )
        runtime_log_profile = (
            runtime_log_profiles.get(runtime_log_profile_id)
            if isinstance(runtime_log_profiles, dict)
            else None
        )
        if runtime_log_exports is not None and not isinstance(runtime_log_profile, dict):
            add_error(errors, "C-LOG-01", f"runtime_log_profile={runtime_log_profile_id} is not registered")
        elif isinstance(runtime_log_profile, dict):
            compatible_experiments = runtime_log_profile.get("compatible_experiment_ids", ["*"])
            if "*" not in compatible_experiments and experiment_id not in compatible_experiments:
                add_error(
                    errors,
                    "C-LOG-02",
                    f"runtime_log_profile={runtime_log_profile_id} is not compatible with experiment {experiment_id}",
                )
            log_tracking_source = runtime_log_profile.get("tracking_source_profile")
            export_tracking_source = runtime_export.get("tracking_source_profile")
            if log_tracking_source != export_tracking_source:
                add_error(
                    errors,
                    "C-LOG-03",
                    f"runtime_log_profile={runtime_log_profile_id} uses tracking_source_profile={log_tracking_source} "
                    f"but runtime_export_profile uses {export_tracking_source}",
                )
            runtime_log_artifacts = runtime_log_profile.get("artifacts")
            if isinstance(runtime_log_artifacts, dict):
                missing_log_slots = sorted(slot for slot in required_export_slots if slot not in runtime_log_artifacts)
                if missing_log_slots:
                    add_error(
                        errors,
                        "C-LOG-04",
                        "runtime_log_profile missing artifacts for runtime export slots: " + ", ".join(missing_log_slots),
                    )

    if not isinstance(runtime_export.get("tracking_source_profile"), str) or not runtime_export.get("tracking_source_profile"):
        add_error(errors, "C-EXPORT-09", "runtime_export_profile must bind a tracking_source_profile")
    else:
        tracking_source_id = runtime_export["tracking_source_profile"]
        tracking_source_profiles = tracking_sources.get("profiles") if isinstance(tracking_sources, dict) else None
        tracking_source = (
            tracking_source_profiles.get(tracking_source_id)
            if isinstance(tracking_source_profiles, dict)
            else None
        )
        if not isinstance(tracking_source, dict):
            add_error(errors, "C-TRACK-01", f"tracking_source_profile={tracking_source_id} is not registered")
        else:
            compatible_experiments = tracking_source.get("compatible_experiment_ids", ["*"])
            if "*" not in compatible_experiments and experiment_id not in compatible_experiments:
                add_error(
                    errors,
                    "C-TRACK-02",
                    f"tracking_source_profile={tracking_source_id} is not compatible with experiment {experiment_id}",
                )

            tracking_state_source = tracking_source.get("state_source_profile")
            if tracking_state_source and tracking_state_source != profile["state_source_profile"]:
                add_error(
                    errors,
                    "C-TRACK-03",
                    f"tracking_source_profile={tracking_source_id} expects state_source_profile={tracking_state_source} "
                    f"but experiment uses {profile['state_source_profile']}",
                )

            tracking_height_source = tracking_source.get("height_source_profile")
            if tracking_height_source and tracking_height_source != profile["height_source_profile"]:
                add_error(
                    errors,
                    "C-TRACK-04",
                    f"tracking_source_profile={tracking_source_id} expects height_source_profile={tracking_height_source} "
                    f"but experiment uses {profile['height_source_profile']}",
                )

            tracking_leaderboard = tracking_source.get("leaderboard_group")
            if tracking_leaderboard and tracking_leaderboard != evaluation.get("leaderboard_group"):
                add_error(
                    errors,
                    "C-TRACK-05",
                    f"tracking_source_profile={tracking_source_id} expects leaderboard_group={tracking_leaderboard} "
                    f"but evaluation uses {evaluation.get('leaderboard_group')}",
                )

            tracking_localization_eval = tracking_source.get("localization_eval_profile")
            experiment_localization_eval = profile.get("localization_eval_profile")
            if tracking_localization_eval != experiment_localization_eval:
                add_error(
                    errors,
                    "C-TRACK-06",
                    f"tracking_source_profile={tracking_source_id} localization_eval_profile={tracking_localization_eval} "
                    f"does not match experiment localization_eval_profile={experiment_localization_eval}",
                )

            if evaluation.get("leaderboard_group") == "fastlio_eval_only" and tracking_source.get("control_state_tracking") is not False:
                add_error(errors, "C-TRACK-07", "FAST-LIO eval-only experiment must use non-control-state tracking semantics")

            if state_source.get("group") == "E" and tracking_source.get("z_source") != "gazebo_rangefinder_surrogate":
                add_error(errors, "C-TRACK-08", "hybrid-Z experiment must use a tracking source with gazebo_rangefinder_surrogate z_source")

    if scenario.get("vehicle_count", 1) > 1 and not runtime.get("multi_uav_namespace_isolation"):
        add_error(errors, "C-SWARM-01", "multi-UAV scenario requires namespace/log isolation in runtime_profile")

    required_artifacts = set(evidence.get("required_artifacts", []))
    if "RUN_MANIFEST.json" not in required_artifacts:
        add_error(errors, "C-EVAL-01", "evidence_profile must require RUN_MANIFEST.json")

    trajectory_goal = trajectory.get("required_for_goal")
    if trajectory_goal and profile.get("goal") != trajectory_goal:
        add_warning(
            warnings,
            "GOAL-01",
            f"trajectory_profile is marked for {trajectory_goal}, but experiment goal is {profile.get('goal')}",
        )

    forbidden_claims = profile.get("forbidden_claims", [])
    if not isinstance(forbidden_claims, list) or not forbidden_claims:
        add_warning(warnings, "CLAIM-01", "experiment profile should declare forbidden_claims")

    registered_modules = registry_profiles(control_module_registry)
    if control_module_registry is not None:
        for slot, expected_kind in (
            ("controller_profile", "nominal_controller"),
            ("augmentation_profile", "augmentation"),
        ):
            profile_id = str(profile[slot])
            if profile_id == "none":
                continue
            registered = registered_modules.get(profile_id)
            if registered is None:
                add_error(errors, "C-REG-01", f"{slot}={profile_id} is not registered in control_module_registry")
                continue
            if registered.get("kind") != expected_kind:
                add_error(
                    errors,
                    "C-REG-02",
                    f"{slot}={profile_id} has registry kind={registered.get('kind')}, expected {expected_kind}",
                )
            if registered.get("selectable") is not True:
                add_error(errors, "C-REG-03", f"{slot}={profile_id} is not selectable in control_module_registry")

    experiment_hash = canonical_hash(profile)

    return {
        "path": str(path),
        "ok": not errors,
        "experiment_id": experiment_id,
        "experiment_profile_hash": experiment_hash,
        "errors": errors,
        "warnings": warnings,
        "profile_rejection": build_rejection(profile, errors),
        "launch_plan_skeleton": None
        if errors
        else build_launch_plan_skeleton(profile, resolved, experiment_hash),
        "run_manifest_skeleton": None
        if errors
        else build_run_manifest_skeleton(profile, resolved, experiment_hash),
    }


def collect_paths(args: argparse.Namespace) -> list[Path]:
    if args.all:
        paths = sorted(DEFAULT_EXPERIMENT_DIR.glob("*.json"))
        if args.include_blocked:
            return paths
        active_paths: list[Path] = []
        for path in paths:
            try:
                raw = load_json(path)
            except ValueError:
                active_paths.append(path)
                continue
            profile = raw.get("experiment_profile") if isinstance(raw, dict) else None
            if not isinstance(profile, dict):
                active_paths.append(path)
                continue
            if experiment_profile_status(profile) in BLOCKED_PROFILE_STATUSES:
                continue
            active_paths.append(path)
        return active_paths
    return [Path(p) for p in args.experiments]


def emit_artifacts(report: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for item in report["results"]:
        experiment_id = item.get("experiment_id") or Path(item["path"]).stem
        if item.get("ok"):
            (output_dir / f"{experiment_id}.launch_plan.skeleton.json").write_text(
                json.dumps(item["launch_plan_skeleton"], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            (output_dir / f"{experiment_id}.RUN_MANIFEST.skeleton.json").write_text(
                json.dumps(item["run_manifest_skeleton"], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        else:
            (output_dir / f"{experiment_id}.profile_rejection.json").write_text(
                json.dumps(item["profile_rejection"], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiments", nargs="*", help="ExperimentProfile JSON files to validate")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="Profile catalog JSON path")
    parser.add_argument("--runtime-log-exports", default=str(DEFAULT_RUNTIME_LOG_EXPORTS), help="RuntimeLogProfile registry JSON path")
    parser.add_argument("--tracking-sources", default=str(DEFAULT_TRACKING_SOURCES), help="TrackingSourceProfile registry JSON path")
    parser.add_argument("--control-module-registry", default=str(DEFAULT_CONTROL_MODULE_REGISTRY), help="ControlModuleRegistry JSON path")
    parser.add_argument("--all", action="store_true", help="Validate all Config/profiles/experiments/*.json")
    parser.add_argument("--include-blocked", action="store_true", help="With --all, include profile_status=blocked/archived audit profiles")
    parser.add_argument("--report", help="Optional JSON validation report output path")
    parser.add_argument("--emit-artifacts-dir", help="Optional directory for launch/manifest/rejection skeletons")
    args = parser.parse_args(argv)

    paths = collect_paths(args)
    if not paths:
        parser.error("provide experiment files or use --all")

    catalog_path = Path(args.catalog)
    try:
        catalog = load_json(catalog_path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        tracking_sources = load_json(Path(args.tracking_sources))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        runtime_log_exports = load_json(Path(args.runtime_log_exports))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    try:
        control_module_registry = load_json(Path(args.control_module_registry))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    results = []
    for path in paths:
        try:
            results.append(
                validate_experiment(
                    path,
                    catalog,
                    tracking_sources,
                    runtime_log_exports,
                    control_module_registry,
                )
            )
        except ValueError as exc:
            results.append(
                {
                    "path": str(path),
                    "ok": False,
                    "experiment_id": None,
                    "experiment_profile_hash": None,
                    "errors": [{"code": "JSON-01", "message": str(exc)}],
                    "warnings": [],
                }
            )

    report = {
        "ok": all(item["ok"] for item in results),
        "catalog": str(catalog_path),
        "runtime_log_exports": str(Path(args.runtime_log_exports)),
        "tracking_sources": str(Path(args.tracking_sources)),
        "control_module_registry": str(Path(args.control_module_registry)),
        "checked_count": len(results),
        "results": results,
    }

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(payload + "\n", encoding="utf-8")
    if args.emit_artifacts_dir:
        emit_artifacts(report, Path(args.emit_artifacts_dir))
    print(payload)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
