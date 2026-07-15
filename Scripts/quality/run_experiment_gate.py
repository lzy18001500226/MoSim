"""Run the offline MoSim ExperimentProfile evidence gate pipeline.

This script is an orchestration wrapper around the static tools:

prepare_experiment_run.py -> collect runtime logs/review/tracking with a
RuntimeLogProfile or provide diagnostic tracking.csv -> compute_tracking_metrics.py
-> check_metric_thresholds.py -> check_run_evidence.py

It does not start ROS, Gazebo, PX4, MAVROS, RViz, UE, or MWORKS. Runtime
evidence must be supplied by the caller.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from build_experiment_preflight import (
    DEFAULT_BINDINGS,
    DEFAULT_CATALOG,
    DEFAULT_METRICS_SCHEMA,
    DEFAULT_RUNTIME_LOG_EXPORTS,
    build_preflight_for_path,
    load_catalogs,
)
from build_tracking_csv import DEFAULT_TRACKING_SOURCES, apply_tracking_source_profile
from build_tracking_csv import build_report as build_tracking_alignment_report
from build_tracking_csv import build_tracking_rows, validate_columns as validate_tracking_source_columns
from build_tracking_csv import validate_numeric_tracking, write_tracking_csv
from build_tracking_csv import load_rows as load_tracking_source_rows
from check_metric_thresholds import evaluate_thresholds
from check_run_evidence import validate_run
from collect_runtime_evidence import build_manifest as build_runtime_log_manifest
from collect_runtime_evidence import build_tracking_from_collected
from collect_runtime_evidence import check_profile_compatibility as check_runtime_log_profile_compatibility
from collect_runtime_evidence import collect_artifacts as collect_runtime_artifacts
from collect_runtime_evidence import file_sha256
from collect_runtime_evidence import get_runtime_log_profile, load_runtime_log_profiles
from collect_runtime_evidence import write_review as write_runtime_review
from compute_tracking_metrics import LOCALIZATION_METRICS
from compute_tracking_metrics import REQUIRED_LOCALIZATION_COLUMNS
from compute_tracking_metrics import build_packet as build_metrics_packet
from compute_tracking_metrics import compute as compute_tracking_metrics
from compute_tracking_metrics import compute_localization
from compute_tracking_metrics import load_json as load_metrics_json
from compute_tracking_metrics import read_tracking
from compute_tracking_metrics import read_csv_with_columns as read_localization_csv
from export_runtime_sources import build_runtime_export_manifest
from export_runtime_sources import check_manifest_contract as check_runtime_export_manifest_contract
from export_runtime_sources import check_runtime_log_profile_matches_export_profile
from export_runtime_sources import load_runtime_export_profile
from export_runtime_sources import validate_export_artifact_assignments
from export_runtime_sources import validate_source_files as validate_runtime_export_source_files
from normalize_tracking_csv import DEFAULT_VALUES, build_report as build_normalize_report
from normalize_tracking_csv import load_map_file, load_rows, normalize_rows, parse_assignments, validate_mapping, write_csv
from prepare_experiment_run import DEFAULT_OUTPUT_ROOT, materialize_run, relative_display


ROOT = Path(__file__).resolve().parents[2]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def copy_file(src: Path, dst: Path) -> dict[str, Any]:
    if not src.is_file():
        raise ValueError(f"input file is missing: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != dst.resolve():
        shutil.copy2(src, dst)
    return {
        "source": relative_display(src),
        "destination": relative_display(dst),
        "bytes": dst.stat().st_size,
    }


def copy_evidence_files(inputs: list[str], destination_dir: Path, kind: str) -> list[dict[str, Any]]:
    copied = []
    for value in inputs:
        src = Path(value)
        dst = destination_dir / src.name
        item = copy_file(src, dst)
        if item["bytes"] <= 0:
            raise ValueError(f"{kind} evidence file is empty: {src}")
        copied.append(item)
    return copied


def run_evidence_path(run_dir: Path, manifest: dict[str, Any], key: str, default: str) -> Path:
    value = manifest.get("evidence", {}).get(key, default)
    path = Path(value)
    return path if path.is_absolute() else run_dir / path


def prepare_run(args: argparse.Namespace) -> tuple[dict[str, Any], Path]:
    catalog, bindings, metrics_schema, tracking_sources, runtime_log_exports = load_catalogs(args)
    preflight = build_preflight_for_path(
        Path(args.experiment),
        catalog,
        bindings,
        metrics_schema,
        tracking_sources,
        runtime_log_exports,
        args,
    )
    if not preflight.get("ok"):
        return {
            "ok": False,
            "stage": "preflight",
            "runtime_started": False,
            "errors": preflight.get("errors", []),
            "warnings": preflight.get("warnings", []),
            "preflight": preflight,
        }, Path(args.output_root) / (args.run_id or "unknown")

    report = materialize_run(preflight, Path(args.output_root), args.force)
    return report, Path(args.output_root) / preflight["run_id"]


def provide_tracking(args: argparse.Namespace, run_dir: Path) -> dict[str, Any] | None:
    modes = [bool(args.tracking_csv), bool(args.raw_tracking_csv), bool(args.reference_csv or args.state_csv)]
    if sum(1 for enabled in modes if enabled) > 1:
        raise ValueError("use only one tracking input mode: --tracking-csv, --raw-tracking-csv, or --reference-csv/--state-csv")
    if args.tracking_source_profile and not (args.reference_csv or args.state_csv):
        raise ValueError("--tracking-source-profile only applies with --reference-csv/--state-csv")
    output_path = run_dir / "tracking.csv"
    if args.tracking_csv:
        copied = copy_file(Path(args.tracking_csv), output_path)
        return {"ok": True, "mode": "copy_standard_tracking_csv", **copied}
    if args.raw_tracking_csv:
        input_path = Path(args.raw_tracking_csv)
        input_columns, rows = load_rows(input_path)
        column_map = {**load_map_file(args.map_file), **parse_assignments(args.map, "--map")}
        defaults = {**DEFAULT_VALUES, **parse_assignments(args.default, "--default")}
        validate_mapping(input_columns, column_map, defaults)
        normalized = normalize_rows(rows, column_map, defaults)
        write_csv(output_path, normalized)
        report = build_normalize_report(input_path, output_path, len(normalized), column_map, defaults)
        write_json(run_dir / "normalize_tracking_report.json", report)
        return {"ok": True, "mode": "normalize_raw_tracking_csv", "report": report}
    if args.reference_csv or args.state_csv:
        if not args.reference_csv or not args.state_csv:
            raise ValueError("--reference-csv and --state-csv must be provided together")
        manifest = load_json(run_dir / "RUN_MANIFEST.json")
        experiment_id = manifest.get("run_manifest", {}).get("experiment_profile_id")
        apply_tracking_source_profile(args, experiment_id=experiment_id)
        ref_columns, ref_rows = load_tracking_source_rows(Path(args.reference_csv))
        state_columns, state_rows = load_tracking_source_rows(Path(args.state_csv))
        validate_tracking_source_columns(args, ref_columns, state_columns)
        tracking_rows, row_stats = build_tracking_rows(args, ref_rows, state_rows)
        validate_numeric_tracking(tracking_rows)
        write_tracking_csv(output_path, tracking_rows)
        alignment_args = argparse.Namespace(**vars(args))
        alignment_args.out = str(output_path)
        report = build_tracking_alignment_report(alignment_args, row_stats)
        report["output_csv"] = relative_display(output_path)
        write_json(run_dir / "tracking_alignment_report.json", report)
        return {"ok": True, "mode": "align_reference_state_csv", "report": report}
    return None


def collect_runtime_evidence_for_gate(args: argparse.Namespace, run_dir: Path) -> dict[str, Any]:
    if not args.review_file and not args.review_text:
        raise ValueError("--runtime-log-profile requires --review-file or --review-text")

    manifest = load_json(run_dir / "RUN_MANIFEST.json").get("run_manifest", {})
    experiment_id = manifest.get("experiment_profile_id")
    if not isinstance(experiment_id, str) or not experiment_id:
        raise ValueError("RUN_MANIFEST.json must contain run_manifest.experiment_profile_id")

    export_contract = manifest.get("runtime_export", {})
    runtime_export_profile_id = export_contract.get("runtime_export_profile") if isinstance(export_contract, dict) else None
    if not isinstance(runtime_export_profile_id, str) or not runtime_export_profile_id:
        raise ValueError("RUN_MANIFEST.json must contain run_manifest.runtime_export.runtime_export_profile")
    export_profile = load_runtime_export_profile(Path(args.catalog), runtime_export_profile_id)
    slot_inputs = {
        "reference_csv": args.reference_csv,
        "state_csv": args.state_csv,
        "localization_csv": args.localization_csv,
        "map_summary_json": args.map_summary_json,
        "rviz_screenshot": args.screenshot[0] if args.screenshot else None,
        "ros_log": args.log[0] if args.log else None,
    }
    required_slots = export_profile.get("required_artifact_slots", [])
    assignments = {
        slot: Path(slot_inputs[slot])
        for slot in required_slots
        if slot in slot_inputs and slot_inputs[slot]
    }
    missing_inputs = [slot for slot in required_slots if slot in slot_inputs and not slot_inputs[slot]]
    if missing_inputs:
        cli_flags = {
            "reference_csv": "--reference-csv",
            "state_csv": "--state-csv",
            "localization_csv": "--localization-csv",
            "map_summary_json": "--map-summary-json",
            "rviz_screenshot": "--screenshot",
            "ros_log": "--log",
        }
        raise ValueError(
            "--runtime-log-profile requires "
            + ", ".join(cli_flags.get(slot, slot) for slot in missing_inputs)
        )
    check_runtime_export_manifest_contract(manifest, runtime_export_profile_id, export_profile)
    validate_export_artifact_assignments(export_profile, assignments)
    source_artifacts = validate_runtime_export_source_files(export_profile, assignments)

    profile = get_runtime_log_profile(load_runtime_log_profiles(Path(args.runtime_log_profiles)), args.runtime_log_profile)
    check_runtime_log_profile_compatibility(args.runtime_log_profile, profile, experiment_id)
    check_runtime_log_profile_matches_export_profile(export_profile, args.runtime_log_profile, profile)

    collected = collect_runtime_artifacts(run_dir, profile, assignments, args.force)
    review = write_runtime_review(args, run_dir)
    build_args = argparse.Namespace(**vars(args))
    build_args.build_tracking = True
    tracking = build_tracking_from_collected(
        build_args,
        args.runtime_log_profile,
        profile,
        experiment_id,
        run_dir,
        collected,
    )
    report = build_runtime_log_manifest(build_args, run_dir, manifest, args.runtime_log_profile, profile, collected, review, tracking)
    write_json(run_dir / "runtime_log_manifest.json", report)
    export_report = build_runtime_export_manifest(
        run_dir,
        manifest,
        runtime_export_profile_id,
        export_profile,
        source_artifacts,
        report,
    )
    export_report["runtime_log_report_sha256"] = file_sha256(run_dir / "runtime_log_manifest.json")
    write_json(run_dir / "runtime_export_manifest.json", export_report)
    return {"ok": True, "mode": "collect_runtime_export_profile", "report": export_report}


def compute_metrics(run_dir: Path, metrics_schema_path: Path, settling_tolerance_m: float) -> dict[str, Any] | None:
    manifest_path = run_dir / "RUN_MANIFEST.json"
    load_metrics_json(metrics_schema_path)
    manifest = load_metrics_json(manifest_path)
    required = manifest.get("run_manifest", {}).get("evaluation", {}).get("required_metrics")
    run_manifest = manifest.get("run_manifest", {})
    tracking_path = run_evidence_path(run_dir, run_manifest, "tracking_log", "tracking.csv")
    required_set = set(required or [])
    if required_set and required_set <= LOCALIZATION_METRICS:
        localization_path = run_evidence_path(run_dir, run_manifest, "localization_log", "raw/localization.csv")
        map_summary_path = run_evidence_path(run_dir, run_manifest, "map_summary", "raw/map_summary.json")
        if not localization_path.is_file():
            raise ValueError(f"localization log is missing: {localization_path}")
        localization_rows = read_localization_csv(localization_path, REQUIRED_LOCALIZATION_COLUMNS, "localization")
        metrics = compute_localization(localization_rows, map_summary_path)
        if required:
            metrics = {name: metrics[name] for name in required if name in metrics}
        packet = build_metrics_packet(
            tracking_path if tracking_path.is_file() else None,
            metrics,
            metrics_schema_path,
            manifest,
            localization_path,
            map_summary_path,
        )
    else:
        if not tracking_path.is_file():
            return None
        rows = read_tracking(tracking_path)
        metrics = compute_tracking_metrics(rows, settling_tolerance_m)
        if required:
            metrics = {name: metrics[name] for name in required if name in metrics}
        packet = build_metrics_packet(tracking_path, metrics, metrics_schema_path, manifest)
    write_json(run_dir / "metrics.json", packet)
    return packet


def check_thresholds(run_dir: Path, metrics_schema_path: Path) -> dict[str, Any] | None:
    metrics_path = run_dir / "metrics.json"
    manifest_path = run_dir / "RUN_MANIFEST.json"
    if not metrics_path.is_file():
        return None
    report = evaluate_thresholds(load_json(metrics_path), load_json(manifest_path), load_json(metrics_schema_path))
    write_json(run_dir / "threshold_report.json", report)
    return report


def attach_review_and_evidence(args: argparse.Namespace, run_dir: Path) -> dict[str, Any]:
    attached: dict[str, Any] = {"review": None, "screenshots": [], "logs": []}
    if args.review_file and args.review_text:
        raise ValueError("use only one of --review-file or --review-text")
    if args.review_file:
        attached["review"] = copy_file(Path(args.review_file), run_dir / "review.md")
    elif args.review_text:
        review_path = run_dir / "review.md"
        review_path.write_text(args.review_text.rstrip() + "\n", encoding="utf-8")
        attached["review"] = {"destination": relative_display(review_path), "bytes": review_path.stat().st_size}

    attached["screenshots"] = copy_evidence_files(args.screenshot, run_dir / "screenshots", "screenshot")
    attached["logs"] = copy_evidence_files(args.log, run_dir / "logs", "log")
    return attached


def build_final_report(
    prepare_report: dict[str, Any],
    run_dir: Path,
    tracking_report: dict[str, Any] | None,
    metrics_report: dict[str, Any] | None,
    threshold_report: dict[str, Any] | None,
    attached: dict[str, Any] | None,
    evidence_report: dict[str, Any] | None,
    errors: list[dict[str, str]],
    prepare_only: bool,
) -> dict[str, Any]:
    threshold_accepted = threshold_report.get("accepted") if threshold_report else None
    evidence_ok = evidence_report.get("ok") if evidence_report else None
    accepted = bool(prepare_report.get("ok")) if prepare_only else bool(evidence_ok and threshold_accepted and not errors)
    return {
        "ok": accepted,
        "accepted": accepted,
        "prepare_only": prepare_only,
        "runtime_started": False,
        "run_id": prepare_report.get("run_id"),
        "experiment_id": prepare_report.get("experiment_id"),
        "run_dir": relative_display(run_dir),
        "stages": {
            "prepare": prepare_report,
            "tracking": tracking_report,
            "metrics": None if metrics_report is None else {"ok": True, "path": relative_display(run_dir / "metrics.json")},
            "threshold": threshold_report,
            "attached_evidence": attached,
            "evidence_gate": evidence_report,
        },
        "threshold_accepted": threshold_accepted,
        "evidence_ok": evidence_ok,
        "errors": errors,
        "warnings": prepare_report.get("warnings", []),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", help="ExperimentProfile JSON file")
    parser.add_argument("--run-id", help="Run id to bind into LaunchPlan and RUN_MANIFEST")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Root directory for run packets")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="Profile catalog JSON path")
    parser.add_argument("--runtime-bindings", default=str(DEFAULT_BINDINGS), help="Runtime binding JSON path")
    parser.add_argument("--metrics-schema", default=str(DEFAULT_METRICS_SCHEMA), help="Metrics schema JSON path")
    parser.add_argument(
        "--runtime-log-profiles",
        default=str(DEFAULT_RUNTIME_LOG_EXPORTS),
        help="RuntimeLogProfile registry JSON path",
    )
    parser.add_argument(
        "--runtime-log-exports",
        default=str(DEFAULT_RUNTIME_LOG_EXPORTS),
        help="RuntimeLogProfile registry JSON path used by static ExperimentProfile validation",
    )
    parser.add_argument("--runtime-log-profile", help="Registered RuntimeLogProfile id for collecting runtime artifacts")
    parser.add_argument("--force", action="store_true", help="Overwrite preparation files if the run directory exists")
    parser.add_argument("--prepare-only", action="store_true", help="Only prepare the run packet; do not require runtime evidence")
    parser.add_argument("--tracking-csv", help="Already-standard tracking.csv to copy into the run directory")
    parser.add_argument("--raw-tracking-csv", help="Raw CSV to normalize into tracking.csv")
    parser.add_argument("--map", action="append", default=[], help="Column mapping in standard=input form for --raw-tracking-csv")
    parser.add_argument("--map-file", help="Optional JSON mapping file for --raw-tracking-csv")
    parser.add_argument("--default", action="append", default=[], help="Default value in standard=value form for --raw-tracking-csv")
    parser.add_argument("--reference-csv", help="Reference trajectory CSV to align with --state-csv")
    parser.add_argument("--state-csv", help="State/truth CSV to align with --reference-csv")
    parser.add_argument("--localization-csv", help="FAST-LIO estimate-vs-Gazebo-truth localization CSV")
    parser.add_argument("--map-summary-json", help="FAST-LIO map completeness summary JSON")
    parser.add_argument("--tracking-source-profile", help="Registered TrackingSourceProfile id")
    parser.add_argument(
        "--tracking-sources",
        default=str(DEFAULT_TRACKING_SOURCES),
        help="TrackingSourceProfile registry JSON path",
    )
    parser.add_argument("--ref-time", help="Reference time column")
    parser.add_argument("--ref-x", help="Reference x column")
    parser.add_argument("--ref-y", help="Reference y column")
    parser.add_argument("--ref-z", help="Reference z column")
    parser.add_argument("--state-time", help="State time column")
    parser.add_argument("--state-x", help="State x column")
    parser.add_argument("--state-y", help="State y column")
    parser.add_argument("--state-z", help="State z column")
    parser.add_argument("--phase-column", help="Optional phase column for reference/state alignment")
    parser.add_argument("--phase-source", choices=("reference", "state"))
    parser.add_argument("--default-phase")
    parser.add_argument("--saturated-column", help="Optional saturated column for reference/state alignment")
    parser.add_argument("--saturated-source", choices=("reference", "state"))
    parser.add_argument("--default-saturated")
    parser.add_argument("--max-time-delta-s", type=float)
    parser.add_argument("--settling-tolerance-m", type=float, default=0.05, help="Settling tolerance for computed metrics")
    parser.add_argument("--review-file", help="Review markdown to copy as review.md")
    parser.add_argument("--review-text", help="Review text to write as review.md")
    parser.add_argument("--screenshot", action="append", default=[], help="Nonempty screenshot/review image file to copy")
    parser.add_argument("--log", action="append", default=[], help="Nonempty log file to copy")
    parser.add_argument("--report", help="Optional final JSON report output path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    errors: list[dict[str, str]] = []
    tracking_report = None
    metrics_report = None
    threshold_report = None
    attached = None
    evidence_report = None

    try:
        prepare_report, run_dir = prepare_run(args)
        if not prepare_report.get("ok"):
            final = build_final_report(prepare_report, run_dir, None, None, None, None, None, [], args.prepare_only)
            payload = json.dumps(final, ensure_ascii=False, indent=2)
            if args.report:
                write_json(Path(args.report), final)
            print(payload)
            return 1
        if not args.prepare_only:
            if args.runtime_log_profile:
                tracking_report = collect_runtime_evidence_for_gate(args, run_dir)
            else:
                tracking_report = provide_tracking(args, run_dir)
            metrics_report = compute_metrics(run_dir, Path(args.metrics_schema), args.settling_tolerance_m)
            threshold_report = check_thresholds(run_dir, Path(args.metrics_schema))
            attached = None if args.runtime_log_profile else attach_review_and_evidence(args, run_dir)
            evidence_report = validate_run(run_dir, Path(args.metrics_schema), Path(args.runtime_log_profiles), Path(args.catalog))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append({"code": "RUN-GATE-ERROR", "message": str(exc)})
        prepare_report = locals().get("prepare_report", {"ok": False, "run_id": args.run_id, "errors": errors, "warnings": []})
        run_dir = locals().get("run_dir", Path(args.output_root) / (args.run_id or "unknown"))

    final = build_final_report(
        prepare_report,
        run_dir,
        tracking_report,
        metrics_report,
        threshold_report,
        attached,
        evidence_report,
        errors,
        args.prepare_only,
    )
    if args.report:
        write_json(Path(args.report), final)
    if run_dir.exists():
        write_json(run_dir / "run_gate_report.json", final)
    print(json.dumps(final, ensure_ascii=False, indent=2))
    return 0 if final["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
