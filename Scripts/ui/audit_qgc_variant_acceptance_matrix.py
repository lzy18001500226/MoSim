#!/usr/bin/env python3
"""Build an evidence-bounded QGC single, multi-UAV, and Diff variant matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = ROOT / "Config" / "control_platform" / "runtime_backend_catalog.json"
DEFAULT_OPERATOR_PROFILES = ROOT / "Config" / "profiles" / "operator_profiles.json"
DEFAULT_DIFF_REVIEW = (
    ROOT
    / "Results"
    / "sunray_ros1"
    / "factory_l2_c99_diff_single_and_swarm_review_20260806"
    / "FACTORY_L2_C99_DIFF_SINGLE_AND_SWARM_REVIEW.json"
)
SINGLE_PROFILE_ID = "px4ctrl_graphical_c99_factory_figure8_v1"
MULTI_PROFILE_ID = "factory_l2_three_uav_swarm_formation_v1"


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"path_outside_project:{path}")
    return resolved


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_object(path: Path) -> dict[str, Any]:
    resolved = project_path(path)
    data = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"json_object_required:{relative(resolved)}")
    return data


def profile_by_id(profiles: list[Any], profile_id: str) -> dict[str, Any]:
    for profile in profiles:
        if isinstance(profile, dict) and profile.get("profile_id") == profile_id:
            return profile
    raise ValueError(f"operator_profile_missing:{profile_id}")


def backend_by_profile(entries: list[Any], profile_id: str) -> dict[str, Any]:
    matches = [
        entry
        for entry in entries
        if isinstance(entry, dict) and profile_id in entry.get("experiment_profile_ids", [])
    ]
    if len(matches) != 1:
        raise ValueError(f"runtime_backend_missing_or_ambiguous:{profile_id}:{len(matches)}")
    return matches[0]


def contains_diff(value: Any) -> bool:
    if isinstance(value, str):
        return "diff" in value.lower()
    if isinstance(value, list):
        return any(contains_diff(item) for item in value)
    if isinstance(value, dict):
        return any(contains_diff(item) for item in value.values())
    return False


def build_single_variant(
    run_dir: Path,
    profile: dict[str, Any],
    backend: dict[str, Any],
) -> dict[str, Any]:
    manifest_path = run_dir / "RUN_MANIFEST.json"
    runtime_status_path = run_dir / "RUNTIME_STATUS.json"
    telemetry_path = run_dir / "telemetry.json"
    manifest = read_object(manifest_path)
    runtime_status = read_object(runtime_status_path)
    telemetry = read_object(telemetry_path)
    map_state = telemetry.get("map_state")
    map_state = map_state if isinstance(map_state, dict) else {}
    map_data = map_state.get("map")
    map_data = map_data if isinstance(map_data, dict) else {}
    transport = map_state.get("transport")
    transport = transport if isinstance(transport, dict) else {}
    operator_status = telemetry.get("operator_runtime_status")
    operator_status = operator_status if isinstance(operator_status, dict) else {}
    coordinate_evidence = telemetry.get("operator_map_coordinate_evidence")
    coordinate_evidence = coordinate_evidence if isinstance(coordinate_evidence, dict) else {}

    run_id = str(manifest.get("run_id", ""))
    identity_checks = {
        "manifest_profile_matches_qgc_publication": manifest.get("experiment_profile_id")
        == profile.get("profile_id"),
        "manifest_backend_matches_qgc_publication": manifest.get("runtime_profile_id")
        == backend.get("runtime_profile_id"),
        "runtime_status_run_matches_manifest": runtime_status.get("run_id") == run_id,
        "telemetry_run_matches_manifest": telemetry.get("run_id") == run_id,
        "telemetry_profile_matches_manifest": operator_status.get("experiment_profile_id")
        == manifest.get("experiment_profile_id"),
        "telemetry_backend_matches_manifest": operator_status.get("controller_backend")
        == manifest.get("controller_backend"),
        "map_coordinate_evidence_verified": coordinate_evidence.get("status") == "verified",
        "map_contract_verified": map_data.get("coordinate_contract_status") == "verified",
        "live_ros1_transport": transport.get("mode") == "live_ros1",
        "live_transport_received_frames": isinstance(transport.get("sequence"), int)
        and transport["sequence"] > 0,
    }
    transport_observed = all(identity_checks.values())
    runtime_state = str(runtime_status.get("status", "missing"))
    mission_status = "blocked" if runtime_state != "passed" else "pending_qgc_visual_evidence"
    return {
        "variant_id": "qgc_single_graphical_c99",
        "order": 1,
        "qgc_publication": {
            "profile_id": profile.get("profile_id"),
            "publication_state": "enabled" if profile.get("enabled") is True else "disabled",
            "runtime_profile_id": backend.get("runtime_profile_id"),
            "operation_id": backend.get("operation_id"),
            "flight_authority": backend.get("operator_contract", {}).get("flight_authority"),
        },
        "evidence": {
            "classification": "source_static_plus_live_result_context",
            "run_dir": relative(run_dir),
            "run_id": run_id,
            "runtime_status": runtime_state,
            "runtime_reason_code": runtime_status.get("reason_code", ""),
            "realtime_transport_status": "observed" if transport_observed else "not_proven",
            "identity_checks": identity_checks,
            "qgc_visual_evidence": {
                "status": "not_collected",
                "reason": "The run proves ROS1/PX4/MAVROS to sidecar telemetry transport, not a rendered QGC window review.",
            },
        },
        "acceptance_status": mission_status,
        "blockers": []
        if mission_status == "pending_qgc_visual_evidence"
        else [
            "single_qgc_formal_runtime_not_passed",
            "qgc_visual_evidence_not_collected",
        ],
        "does_not_prove": [
            "QGC visual rendering acceptance",
            "controller performance when runtime_status is blocked",
            "multi-UAV or Diff-Planner acceptance",
        ],
    }


def build_multi_variant(profile: dict[str, Any], backend: dict[str, Any]) -> dict[str, Any]:
    published = profile.get("enabled") is True
    return {
        "variant_id": "qgc_three_uav_formation",
        "order": 2,
        "qgc_publication": {
            "profile_id": profile.get("profile_id"),
            "publication_state": "enabled" if published else "disabled",
            "disabled_reason": profile.get("disabled_reason", ""),
            "runtime_profile_id": backend.get("runtime_profile_id"),
            "operation_id": backend.get("operation_id"),
            "vehicle_counts": backend.get("vehicle_counts", []),
            "flight_authority": backend.get("operator_contract", {}).get("flight_authority"),
        },
        "evidence": {
            "classification": "source_static_only",
            "runtime_status": backend.get("status", ""),
        },
        "acceptance_status": "not_published" if not published else "requires_independent_live_gate",
        "blockers": (
            ["qgc_three_uav_profile_disabled:" + str(profile.get("disabled_reason", ""))]
            if not published
            else ["single_qgc_closure_must_pass_before_multi_uav_qgc_live_gate"]
        ),
        "does_not_prove": [
            "three-UAV runtime acceptance",
            "formation-controller or separation-metric acceptance",
            "QGC flight authority",
        ],
    }


def build_diff_variant(
    profiles: list[Any], entries: list[Any], diff_review: dict[str, Any], diff_review_path: Path
) -> dict[str, Any]:
    diff_profiles = [profile for profile in profiles if contains_diff(profile)]
    diff_entries = [entry for entry in entries if contains_diff(entry)]
    publication_absent = not diff_profiles and not diff_entries
    review_status = str(diff_review.get("status", "missing"))
    return {
        "variant_id": "qgc_diff_variants",
        "order": 3,
        "qgc_publication": {
            "operator_profiles": [profile.get("profile_id") for profile in diff_profiles if isinstance(profile, dict)],
            "runtime_profiles": [entry.get("runtime_profile_id") for entry in diff_entries if isinstance(entry, dict)],
            "publication_state": "absent" if publication_absent else "source_present_requires_qgc_audit",
        },
        "external_runtime_evidence": {
            "classification": "separate_ros1_runtime_result",
            "review_path": relative(diff_review_path),
            "review_status": review_status,
            "single_uav_status": diff_review.get("single_uav", {}).get("status"),
            "multi_uav_status": diff_review.get("multi_uav", {}).get("status"),
        },
        "acceptance_status": "not_published" if publication_absent else "requires_qgc_specific_audit",
        "blockers": (
            ["no_qgc_operator_profile_or_runtime_backend_for_diff_variants"]
            if publication_absent
            else ["diff_qgc_source_present_but_not_accepted_by_this_matrix"]
        ),
        "does_not_prove": [
            "QGC command publication or visual display",
            "QGC ownership of any Diff-Planner mission",
            "generalized Diff-Planner or swarm safety",
        ],
    }


def build_matrix(
    *,
    qgc_run_dir: Path,
    diff_review_path: Path,
    catalog_path: Path = DEFAULT_CATALOG,
    operator_profiles_path: Path = DEFAULT_OPERATOR_PROFILES,
) -> dict[str, Any]:
    catalog = read_object(catalog_path)
    operator_catalog = read_object(operator_profiles_path)
    profiles = operator_catalog.get("profiles")
    entries = catalog.get("runtime_profiles")
    if catalog.get("schema") != "mosim.runtime_backend_catalog.v2":
        raise ValueError("runtime_backend_catalog_schema_invalid")
    if not isinstance(profiles, list) or not isinstance(entries, list):
        raise ValueError("operator_profile_or_runtime_entries_invalid")

    single = build_single_variant(
        project_path(qgc_run_dir),
        profile_by_id(profiles, SINGLE_PROFILE_ID),
        backend_by_profile(entries, SINGLE_PROFILE_ID),
    )
    multi = build_multi_variant(
        profile_by_id(profiles, MULTI_PROFILE_ID),
        backend_by_profile(entries, MULTI_PROFILE_ID),
    )
    diff_path = project_path(diff_review_path)
    diff = build_diff_variant(profiles, entries, read_object(diff_path), diff_path)
    variants = [single, multi, diff]
    blockers = [
        f"{variant['variant_id']}:{blocker}"
        for variant in variants
        for blocker in variant["blockers"]
    ]
    return {
        "schema": "mosim.qgc_variant_acceptance_matrix.v1",
        "status": "passed" if not blockers else "blocked",
        "claim_boundary": (
            "This matrix compares QGC publication and evidence states. It does not turn a "
            "separate ROS1 runtime result, source check, telemetry file, or QGC screenshot into "
            "a different acceptance class."
        ),
        "variants": variants,
        "blockers": blockers,
        "next_gate": (
            "Capture a QGC visual review tied to a single run whose formal runtime status is passed."
            if blockers
            else "Independent multi-UAV and Diff QGC live gates remain separately required."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qgc-run-dir", type=Path, required=True)
    parser.add_argument("--diff-review", type=Path, default=DEFAULT_DIFF_REVIEW)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--operator-profiles", type=Path, default=DEFAULT_OPERATOR_PROFILES)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_matrix(
        qgc_run_dir=args.qgc_run_dir,
        diff_review_path=args.diff_review,
        catalog_path=args.catalog,
        operator_profiles_path=args.operator_profiles,
    )
    output = project_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
