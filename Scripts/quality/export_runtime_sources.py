"""Export completed runtime source files according to a RuntimeExportProfile.

This script is offline. It expects ROS/Sunray/Gazebo/RViz runtime artifacts to
already exist as files, validates them against the selected RuntimeExportProfile,
copies them into the run packet, writes runtime_export_manifest.json, and
delegates RuntimeLogProfile collection to collect_runtime_evidence.py. It does
not start ROS, Gazebo, PX4, MAVROS, RViz, UE, or MWORKS.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

from collect_runtime_evidence import DEFAULT_RUNTIME_LOG_EXPORTS
from collect_runtime_evidence import build_manifest as build_runtime_log_manifest
from collect_runtime_evidence import build_tracking_from_collected
from collect_runtime_evidence import check_profile_compatibility as check_runtime_log_profile_compatibility
from collect_runtime_evidence import collect_artifacts
from collect_runtime_evidence import file_sha256, get_runtime_log_profile, load_runtime_log_profiles
from collect_runtime_evidence import load_run_manifest, parse_artifact_assignments, write_json, write_review
from build_tracking_csv import DEFAULT_TRACKING_SOURCES
from prepare_experiment_run import relative_display


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = ROOT / "Config" / "profiles" / "catalog.json"


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"JSON file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON file {path}: {exc}") from exc


def load_runtime_export_profile(catalog_path: Path, profile_id: str) -> dict[str, Any]:
    catalog = load_json(catalog_path)
    profiles = catalog.get("runtime_export_profiles")
    if not isinstance(profiles, dict):
        raise ValueError(f"{catalog_path}: expected runtime_export_profiles object")
    profile = profiles.get(profile_id)
    if not isinstance(profile, dict):
        raise ValueError(f"unknown runtime export profile: {profile_id}")
    if not isinstance(profile.get("exported_artifacts"), dict):
        raise ValueError(f"runtime export profile {profile_id} must contain exported_artifacts object")
    return profile


def check_manifest_contract(manifest: dict[str, Any], profile_id: str, profile: dict[str, Any]) -> None:
    export_contract = manifest.get("runtime_export", {})
    if isinstance(export_contract, dict):
        declared_profile = export_contract.get("runtime_export_profile")
        if declared_profile and declared_profile != profile_id:
            raise ValueError(
                "runtime export profile does not match RUN_MANIFEST.json: "
                f"{profile_id} != {declared_profile}"
            )
        for key in ("runtime_log_profile", "tracking_source_profile"):
            declared_value = export_contract.get(key)
            profile_value = profile.get(key)
            if declared_value and profile_value and declared_value != profile_value:
                raise ValueError(
                    f"{key} does not match RuntimeExportProfile: {declared_value} != {profile_value}"
                )

    manifest_runtime = manifest.get("runtime", {})
    declared_runtime = manifest_runtime.get("runtime_profile") if isinstance(manifest_runtime, dict) else None
    profile_runtime = profile.get("runtime_profile")
    if declared_runtime and profile_runtime and declared_runtime != profile_runtime:
        raise ValueError(
            f"runtime_profile does not match RuntimeExportProfile: {declared_runtime} != {profile_runtime}"
        )


def validate_export_artifact_assignments(profile: dict[str, Any], assignments: dict[str, Path]) -> None:
    exported_artifacts = profile["exported_artifacts"]
    required_slots = profile.get("required_artifact_slots", [])
    if not isinstance(required_slots, list):
        raise ValueError("RuntimeExportProfile required_artifact_slots must be a list")

    unknown_slots = sorted(set(assignments) - set(exported_artifacts))
    if unknown_slots:
        raise ValueError("unknown RuntimeExportProfile artifact slot(s): " + ", ".join(unknown_slots))

    missing = sorted(slot for slot in required_slots if slot not in assignments)
    if missing:
        raise ValueError("missing required RuntimeExportProfile artifact slot(s): " + ", ".join(missing))

    for slot in required_slots:
        spec = exported_artifacts.get(slot)
        if not isinstance(spec, dict):
            raise ValueError(f"required RuntimeExportProfile artifact has no spec: {slot}")
        for field in ("destination", "producer", "command_template"):
            if not spec.get(field):
                raise ValueError(f"RuntimeExportProfile artifact {slot} missing {field}")


def validate_required_columns(slot: str, path: Path, required_columns: list[str]) -> dict[str, Any]:
    if not required_columns:
        return {"required_columns": [], "row_count": None}
    if not path.is_file():
        raise ValueError(f"artifact source is missing: {path}")
    if path.stat().st_size <= 0:
        raise ValueError(f"artifact source is empty: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or [])
        missing = sorted(set(required_columns) - fieldnames)
        if missing:
            raise ValueError(f"artifact {slot} is missing required column(s): " + ", ".join(missing))
        row_count = sum(1 for _ in reader)
    if row_count <= 0:
        raise ValueError(f"artifact {slot} has no data rows: {path}")
    return {"required_columns": required_columns, "row_count": row_count}


def validate_source_files(profile: dict[str, Any], assignments: dict[str, Path]) -> list[dict[str, Any]]:
    exported_artifacts = profile["exported_artifacts"]
    artifacts = []
    for slot, source_path in assignments.items():
        if not source_path.is_file():
            raise ValueError(f"artifact source is missing: {source_path}")
        if source_path.stat().st_size <= 0:
            raise ValueError(f"artifact source is empty: {source_path}")
        spec = exported_artifacts[slot]
        column_report = validate_required_columns(slot, source_path, list(spec.get("required_columns") or []))
        artifacts.append(
            {
                "slot": slot,
                "source": str(source_path),
                "destination": spec.get("destination"),
                "role": spec.get("role"),
                "producer": spec.get("producer"),
                "command_template": spec.get("command_template"),
                "bytes": source_path.stat().st_size,
                "sha256": file_sha256(source_path),
                **column_report,
            }
        )
    return artifacts


def check_runtime_log_profile_matches_export_profile(
    export_profile: dict[str, Any],
    runtime_log_profile_id: str,
    runtime_log_profile: dict[str, Any],
) -> None:
    if export_profile.get("runtime_log_profile") != runtime_log_profile_id:
        raise ValueError(
            "RuntimeLogProfile does not match RuntimeExportProfile: "
            f"{runtime_log_profile_id} != {export_profile.get('runtime_log_profile')}"
        )
    expected_tracking = export_profile.get("tracking_source_profile")
    actual_tracking = runtime_log_profile.get("tracking_source_profile")
    if expected_tracking and actual_tracking and expected_tracking != actual_tracking:
        raise ValueError(
            f"tracking_source_profile mismatch: RuntimeExportProfile {expected_tracking} != RuntimeLogProfile {actual_tracking}"
        )
    export_artifacts = export_profile.get("exported_artifacts", {})
    runtime_artifacts = runtime_log_profile.get("artifacts", {})
    for slot in export_profile.get("required_artifact_slots", []):
        export_destination = export_artifacts.get(slot, {}).get("destination")
        runtime_destination = runtime_artifacts.get(slot, {}).get("destination")
        if export_destination and runtime_destination and export_destination != runtime_destination:
            raise ValueError(
                f"artifact {slot} destination mismatch: RuntimeExportProfile {export_destination} != RuntimeLogProfile {runtime_destination}"
            )


def build_runtime_export_manifest(
    run_dir: Path,
    manifest: dict[str, Any],
    profile_id: str,
    profile: dict[str, Any],
    source_artifacts: list[dict[str, Any]],
    runtime_log_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generator": "Scripts/quality/export_runtime_sources.py",
        "runtime_started": False,
        "run_dir": relative_display(run_dir),
        "run_id": manifest.get("run_id"),
        "experiment_profile_id": manifest.get("experiment_profile_id"),
        "runtime_profile": profile.get("runtime_profile"),
        "runtime_export_profile": profile_id,
        "runtime_log_profile": profile.get("runtime_log_profile"),
        "tracking_source_profile": profile.get("tracking_source_profile"),
        "required_artifact_slots": profile.get("required_artifact_slots", []),
        "required_topics": profile.get("required_topics", []),
        "review_requirements": profile.get("review_requirements", []),
        "source_artifacts": source_artifacts,
        "runtime_log_manifest": relative_display(run_dir / "runtime_log_manifest.json"),
        "runtime_log_report_sha256": None,
        "tracking": runtime_log_report.get("tracking"),
        "warnings": [
            "This is an offline file export/collection manifest; it does not prove runtime execution by itself."
        ],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", help="Existing run packet directory containing RUN_MANIFEST.json")
    parser.add_argument("--runtime-export-profile", required=True, help="Registered RuntimeExportProfile id")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="Profile catalog JSON path")
    parser.add_argument(
        "--runtime-log-profiles",
        default=str(DEFAULT_RUNTIME_LOG_EXPORTS),
        help="RuntimeLogProfile registry JSON path",
    )
    parser.add_argument(
        "--tracking-sources",
        default=str(DEFAULT_TRACKING_SOURCES),
        help="TrackingSourceProfile registry JSON path",
    )
    parser.add_argument("--artifact", action="append", default=[], help="Artifact assignment in slot=path form")
    parser.add_argument("--review-file", help="Completed review markdown to copy to review.md")
    parser.add_argument("--review-text", help="Completed review text to write to review.md")
    parser.add_argument("--build-tracking", action="store_true", help="Build standard tracking.csv from collected CSV slots")
    parser.add_argument("--force", action="store_true", help="Overwrite destination artifacts if they already exist")
    parser.add_argument("--report", help="Optional JSON report output path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        run_dir = Path(args.run_dir)
        manifest = load_run_manifest(run_dir)
        experiment_id = manifest.get("experiment_profile_id")
        if not isinstance(experiment_id, str) or not experiment_id:
            raise ValueError("RUN_MANIFEST.json must contain run_manifest.experiment_profile_id")

        export_profile = load_runtime_export_profile(Path(args.catalog), args.runtime_export_profile)
        check_manifest_contract(manifest, args.runtime_export_profile, export_profile)
        assignments = parse_artifact_assignments(args.artifact)
        validate_export_artifact_assignments(export_profile, assignments)
        source_artifacts = validate_source_files(export_profile, assignments)

        runtime_log_profile_id = export_profile.get("runtime_log_profile")
        if not isinstance(runtime_log_profile_id, str) or not runtime_log_profile_id:
            raise ValueError(f"RuntimeExportProfile {args.runtime_export_profile} must declare runtime_log_profile")
        runtime_log_profiles = load_runtime_log_profiles(Path(args.runtime_log_profiles))
        runtime_log_profile = get_runtime_log_profile(runtime_log_profiles, runtime_log_profile_id)
        check_runtime_log_profile_compatibility(runtime_log_profile_id, runtime_log_profile, experiment_id)
        check_runtime_log_profile_matches_export_profile(export_profile, runtime_log_profile_id, runtime_log_profile)

        collector_args = argparse.Namespace(
            review_file=args.review_file,
            review_text=args.review_text,
            build_tracking=args.build_tracking,
            force=args.force,
            tracking_sources=args.tracking_sources,
        )
        collected = collect_artifacts(run_dir, runtime_log_profile, assignments, args.force)
        review = write_review(collector_args, run_dir)
        tracking = build_tracking_from_collected(
            collector_args,
            runtime_log_profile_id,
            runtime_log_profile,
            experiment_id,
            run_dir,
            collected,
        )
        runtime_log_report = build_runtime_log_manifest(
            collector_args,
            run_dir,
            manifest,
            runtime_log_profile_id,
            runtime_log_profile,
            collected,
            review,
            tracking,
        )
        write_json(run_dir / "runtime_log_manifest.json", runtime_log_report)

        export_report = build_runtime_export_manifest(
            run_dir,
            manifest,
            args.runtime_export_profile,
            export_profile,
            source_artifacts,
            runtime_log_report,
        )
        export_report["runtime_log_report_sha256"] = file_sha256(run_dir / "runtime_log_manifest.json")
        write_json(run_dir / "runtime_export_manifest.json", export_report)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    payload = json.dumps(export_report, ensure_ascii=False, indent=2)
    if args.report:
        write_json(Path(args.report), export_report)
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
