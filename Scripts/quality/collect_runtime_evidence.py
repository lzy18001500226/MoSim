"""Collect completed runtime artifacts into a MoSim run packet.

This collector is offline. It copies caller-provided logs, screenshots, CSV
exports, and review text into an existing Results/runs/<run_id> directory,
writes runtime_log_manifest.json, and can build standard tracking.csv from
reference/state CSV logs. It does not start ROS, Gazebo, PX4, MAVROS, RViz,
UE, or MWORKS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from build_tracking_csv import DEFAULT_TRACKING_SOURCES, apply_tracking_source_profile
from build_tracking_csv import build_report as build_tracking_alignment_report
from build_tracking_csv import build_tracking_rows, validate_columns as validate_tracking_source_columns
from build_tracking_csv import load_rows as load_tracking_source_rows
from build_tracking_csv import validate_numeric_tracking, write_tracking_csv
from prepare_experiment_run import relative_display


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNTIME_LOG_EXPORTS = ROOT / "Config" / "profiles" / "runtime_log_exports.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_runtime_log_profiles(path: Path) -> dict[str, Any]:
    try:
        packet = load_json(path)
    except FileNotFoundError as exc:
        raise ValueError(f"runtime log profile file is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"runtime log profile file is invalid JSON: {path}: {exc}") from exc
    profiles = packet.get("profiles")
    if not isinstance(profiles, dict):
        raise ValueError(f"{path}: expected top-level profiles object")
    return profiles


def get_runtime_log_profile(profiles: dict[str, Any], profile_id: str) -> dict[str, Any]:
    profile = profiles.get(profile_id)
    if not isinstance(profile, dict):
        raise ValueError(f"unknown runtime log profile: {profile_id}")
    if not isinstance(profile.get("artifacts"), dict):
        raise ValueError(f"runtime log profile {profile_id} must contain artifacts object")
    return profile


def load_run_manifest(run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / "RUN_MANIFEST.json"
    if not manifest_path.is_file():
        raise ValueError(f"RUN_MANIFEST.json is missing in run directory: {run_dir}")
    packet = load_json(manifest_path)
    manifest = packet.get("run_manifest")
    if not isinstance(manifest, dict):
        raise ValueError(f"RUN_MANIFEST.json must contain run_manifest object: {manifest_path}")
    return manifest


def check_profile_compatibility(profile_id: str, profile: dict[str, Any], experiment_id: str) -> None:
    compatible_ids = profile.get("compatible_experiment_ids", ["*"])
    if "*" not in compatible_ids and experiment_id not in compatible_ids:
        raise ValueError(f"runtime log profile {profile_id} is not compatible with experiment profile {experiment_id}")


def parse_artifact_assignments(values: list[str]) -> dict[str, Path]:
    artifacts: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"--artifact expects slot=path, got: {value}")
        slot, raw_path = value.split("=", 1)
        slot = slot.strip()
        if not slot:
            raise ValueError(f"--artifact has empty slot name: {value}")
        if slot in artifacts:
            raise ValueError(f"duplicate artifact slot: {slot}")
        artifacts[slot] = Path(raw_path)
    return artifacts


def copy_artifact(src: Path, dst: Path, force: bool) -> dict[str, Any]:
    if not src.is_file():
        raise ValueError(f"artifact source is missing: {src}")
    if src.stat().st_size <= 0:
        raise ValueError(f"artifact source is empty: {src}")
    if dst.exists() and not force:
        raise ValueError(f"destination already exists; use --force to overwrite: {dst}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != dst.resolve():
        shutil.copy2(src, dst)
    return {
        "source": str(src),
        "destination": relative_display(dst),
        "bytes": dst.stat().st_size,
        "sha256": file_sha256(dst),
    }


def collect_artifacts(
    run_dir: Path,
    profile: dict[str, Any],
    assignments: dict[str, Path],
    force: bool,
) -> list[dict[str, Any]]:
    artifact_specs = profile["artifacts"]
    unknown_slots = sorted(set(assignments) - set(artifact_specs))
    if unknown_slots:
        raise ValueError("unknown artifact slot(s): " + ", ".join(unknown_slots))

    missing = [
        slot
        for slot, spec in artifact_specs.items()
        if spec.get("required", False) and slot not in assignments
    ]
    if missing:
        raise ValueError("missing required artifact slot(s): " + ", ".join(sorted(missing)))

    collected = []
    for slot, src in assignments.items():
        spec = artifact_specs[slot]
        destination = spec.get("destination")
        if not isinstance(destination, str) or not destination:
            raise ValueError(f"artifact slot {slot} must define destination")
        copied = copy_artifact(src, run_dir / destination, force)
        collected.append(
            {
                "slot": slot,
                "kind": spec.get("kind"),
                "role": spec.get("role"),
                "required": bool(spec.get("required", False)),
                **copied,
            }
        )
    return collected


def write_review(args: argparse.Namespace, run_dir: Path) -> dict[str, Any] | None:
    if args.review_file and args.review_text:
        raise ValueError("use only one of --review-file or --review-text")
    if not args.review_file and not args.review_text:
        return None
    review_path = run_dir / "review.md"
    if review_path.exists() and not args.force:
        raise ValueError(f"destination already exists; use --force to overwrite: {review_path}")
    if args.review_file:
        return copy_artifact(Path(args.review_file), review_path, args.force)
    review_path.write_text(args.review_text.rstrip() + "\n", encoding="utf-8")
    return {
        "source": "inline_review_text",
        "destination": relative_display(review_path),
        "bytes": review_path.stat().st_size,
        "sha256": file_sha256(review_path),
    }


def artifact_destination(collected: list[dict[str, Any]], slot: str) -> Path:
    for item in collected:
        if item.get("slot") == slot:
            return ROOT / item["destination"]
    raise ValueError(f"tracking artifact slot was not collected: {slot}")


def build_tracking_from_collected(
    args: argparse.Namespace,
    profile_id: str,
    profile: dict[str, Any],
    experiment_id: str,
    run_dir: Path,
    collected: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not args.build_tracking:
        return None
    tracking_source_profile = profile.get("tracking_source_profile")
    if not isinstance(tracking_source_profile, str) or not tracking_source_profile:
        raise ValueError(f"runtime log profile {profile_id} does not declare tracking_source_profile")

    reference_slot = profile.get("tracking_reference_slot", "reference_csv")
    state_slot = profile.get("tracking_state_slot", "state_csv")
    reference_csv = artifact_destination(collected, reference_slot)
    state_csv = artifact_destination(collected, state_slot)
    output_path = run_dir / "tracking.csv"

    alignment_args = argparse.Namespace(
        reference_csv=str(reference_csv),
        state_csv=str(state_csv),
        out=str(output_path),
        tracking_source_profile=tracking_source_profile,
        tracking_sources=str(Path(args.tracking_sources)),
        ref_time=None,
        ref_x=None,
        ref_y=None,
        ref_z=None,
        state_time=None,
        state_x=None,
        state_y=None,
        state_z=None,
        phase_column=None,
        phase_source=None,
        default_phase=None,
        saturated_column=None,
        saturated_source=None,
        default_saturated=None,
        max_time_delta_s=None,
    )
    apply_tracking_source_profile(alignment_args, experiment_id=experiment_id)
    ref_columns, ref_rows = load_tracking_source_rows(reference_csv)
    state_columns, state_rows = load_tracking_source_rows(state_csv)
    validate_tracking_source_columns(alignment_args, ref_columns, state_columns)
    tracking_rows, row_stats = build_tracking_rows(alignment_args, ref_rows, state_rows)
    validate_numeric_tracking(tracking_rows)
    write_tracking_csv(output_path, tracking_rows)
    report = build_tracking_alignment_report(alignment_args, row_stats)
    report["output_csv"] = relative_display(output_path)
    write_json(run_dir / "tracking_alignment_report.json", report)
    return {
        "ok": True,
        "tracking_source_profile": tracking_source_profile,
        "reference_slot": reference_slot,
        "state_slot": state_slot,
        "tracking_csv": relative_display(output_path),
        "tracking_alignment_report": relative_display(run_dir / "tracking_alignment_report.json"),
        "aligned_rows": row_stats.get("aligned_rows"),
    }


def build_manifest(
    args: argparse.Namespace,
    run_dir: Path,
    manifest: dict[str, Any],
    profile_id: str,
    profile: dict[str, Any],
    collected: list[dict[str, Any]],
    review: dict[str, Any] | None,
    tracking: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generator": "Scripts/quality/collect_runtime_evidence.py",
        "runtime_started": False,
        "run_dir": relative_display(run_dir),
        "run_id": manifest.get("run_id"),
        "experiment_profile_id": manifest.get("experiment_profile_id"),
        "runtime_log_profile": profile_id,
        "runtime_log_profile_description": profile.get("description"),
        "artifacts": collected,
        "review": review,
        "tracking": tracking,
        "warnings": [],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", help="Existing Results/runs/<run_id> directory")
    parser.add_argument("--runtime-log-profile", required=True, help="Registered RuntimeLogProfile id")
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
        profiles = load_runtime_log_profiles(Path(args.runtime_log_profiles))
        profile = get_runtime_log_profile(profiles, args.runtime_log_profile)
        check_profile_compatibility(args.runtime_log_profile, profile, experiment_id)
        assignments = parse_artifact_assignments(args.artifact)
        collected = collect_artifacts(run_dir, profile, assignments, args.force)
        review = write_review(args, run_dir)
        tracking = build_tracking_from_collected(
            args,
            args.runtime_log_profile,
            profile,
            experiment_id,
            run_dir,
            collected,
        )
        report = build_manifest(args, run_dir, manifest, args.runtime_log_profile, profile, collected, review, tracking)
        write_json(run_dir / "runtime_log_manifest.json", report)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        write_json(Path(args.report), report)
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
