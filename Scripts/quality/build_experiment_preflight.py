"""Build MoSim ExperimentProfile dry-run preflight packets.

This script is intentionally static. It validates an ExperimentProfile, checks
that declared runtime templates have project-local source bindings, verifies
that requested metrics are defined, and emits LaunchPlan / RunManifest
templates. It does not start ROS, Gazebo, PX4, MAVROS, RViz, or MWORKS.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from check_experiment_profile import (
    DEFAULT_CATALOG,
    DEFAULT_EXPERIMENT_DIR,
    DEFAULT_RUNTIME_LOG_EXPORTS,
    DEFAULT_TRACKING_SOURCES,
    canonical_hash,
    catalog_entry,
    collect_paths,
    load_json,
    validate_experiment,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BINDINGS = ROOT / "Config" / "profiles" / "runtime_bindings.json"
DEFAULT_METRICS_SCHEMA = ROOT / "Config" / "profiles" / "metrics_schema.json"


def add_error(errors: list[dict[str, str]], code: str, message: str) -> None:
    errors.append({"code": code, "message": message})


def load_catalogs(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        load_json(Path(args.catalog)),
        load_json(Path(args.runtime_bindings)),
        load_json(Path(args.metrics_schema)),
        load_json(Path(args.tracking_sources)),
        load_json(Path(args.runtime_log_exports)),
    )


def run_id_for(profile_id: str, requested: str | None) -> str:
    return requested or f"dryrun_{profile_id}"


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def bind_run_id(payload: dict[str, Any], run_id: str) -> dict[str, Any]:
    bound = deepcopy(payload)
    if "launch_plan" in bound:
        bound["launch_plan"]["run_id"] = run_id
    if "run_manifest" in bound:
        bound["run_manifest"]["run_id"] = run_id
    return bound


def expand_manifest(
    manifest_payload: dict[str, Any],
    run_id: str,
    launch_plan_hash: str,
    metrics_schema_path: Path,
    runtime_bindings_path: Path,
    runtime_log_exports_path: Path,
    tracking_sources_path: Path,
) -> dict[str, Any]:
    manifest = bind_run_id(manifest_payload, run_id)
    body = manifest["run_manifest"]
    result_root = f"Results/runs/{run_id}"
    body["launch_plan_hash"] = launch_plan_hash
    body["runtime_bindings"] = display_path(runtime_bindings_path)
    body["metrics_schema"] = display_path(metrics_schema_path)
    body["runtime_log_exports"] = display_path(runtime_log_exports_path)
    body["tracking_sources"] = display_path(tracking_sources_path)
    body["evidence"]["result_root"] = result_root
    body["evidence"]["launch_plan"] = "LaunchPlan.json"
    body["evidence"]["run_manifest"] = "RUN_MANIFEST.json"
    body["evidence"]["metrics"] = "metrics.json"
    body["evidence"]["threshold_report"] = "threshold_report.json"
    body["evidence"]["tracking_log"] = "tracking.csv"
    body["evidence"]["localization_log"] = "raw/localization.csv"
    body["evidence"]["map_summary"] = "raw/map_summary.json"
    body["evidence"]["review"] = "review.md"
    body["evidence"]["screenshots"] = "screenshots/"
    body["evidence"]["logs"] = "logs/"
    return manifest


def check_runtime_bindings(
    launch_plan: dict[str, Any],
    bindings: dict[str, Any],
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    template_bindings = bindings.get("template_bindings", {})
    for step in launch_plan["launch_plan"]["steps"]:
        template = step.get("template")
        binding = template_bindings.get(template)
        step_errors: list[dict[str, str]] = []
        required_paths: list[str] = []
        if not isinstance(binding, dict):
            add_error(step_errors, "P-BIND-01", f"no runtime binding registered for template {template}")
        else:
            required_paths = list(binding.get("required_paths", []))
            for relative in required_paths:
                if not (ROOT / relative).exists():
                    add_error(step_errors, "P-PATH-01", f"required path does not exist: {relative}")
        checks.append(
            {
                "step_id": step.get("id"),
                "template": template,
                "ok": not step_errors,
                "required_paths": required_paths,
                "errors": step_errors,
            }
        )
    return checks


def check_metrics(
    profile: dict[str, Any],
    catalog: dict[str, Any],
    metrics_schema: dict[str, Any],
) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    evaluation = catalog_entry(catalog, "evaluation_profiles", profile["evaluation_profile"]) or {}
    definitions = metrics_schema.get("metric_definitions", {})
    for metric in evaluation.get("metrics", []):
        if metric not in definitions:
            add_error(errors, "P-METRIC-01", f"metric is not defined in metrics schema: {metric}")
    return errors


def check_fastlio_state_gate(profile: dict[str, Any], catalog: dict[str, Any]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    state_source = catalog_entry(catalog, "state_source_profiles", profile["state_source_profile"]) or {}
    group = state_source.get("group")
    if group == "D" and not state_source.get("requires_px4_ekf_external_odometry"):
        add_error(errors, "P-LIO-01", "FAST-LIO PX4 EKF branch must declare requires_px4_ekf_external_odometry")
    if group == "E" and not state_source.get("requires_hybrid_height"):
        add_error(errors, "P-LIO-02", "Hybrid-Z branch must declare requires_hybrid_height")
    if profile.get("localization_eval_profile"):
        localization_eval = catalog_entry(catalog, "state_source_profiles", profile["localization_eval_profile"]) or {}
        if localization_eval.get("allowed_for_control", False):
            add_error(errors, "P-LIO-03", "localization_eval_profile must not be control-enabled")
    return errors


def build_runtime_export_contract(profile: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    export_profile_id = profile["runtime_export_profile"]
    export_profile = catalog_entry(catalog, "runtime_export_profiles", export_profile_id) or {}
    exported_artifacts = export_profile.get("exported_artifacts", {})
    required_slots = export_profile.get("required_artifact_slots", [])
    artifacts = []
    if isinstance(exported_artifacts, dict):
        for slot in required_slots:
            spec = exported_artifacts.get(slot, {})
            artifacts.append(
                {
                    "slot": slot,
                    "role": spec.get("role"),
                    "destination": spec.get("destination"),
                    "producer": spec.get("producer"),
                    "command_template": spec.get("command_template"),
                    "required_columns": spec.get("required_columns", []),
                }
            )
    return {
        "runtime_export_profile": export_profile_id,
        "runtime_log_profile": export_profile.get("runtime_log_profile"),
        "tracking_source_profile": export_profile.get("tracking_source_profile"),
        "required_artifacts": artifacts,
        "required_topics": export_profile.get("required_topics", []),
        "review_requirements": export_profile.get("review_requirements", []),
    }


def build_preflight_for_path(
    path: Path,
    catalog: dict[str, Any],
    bindings: dict[str, Any],
    metrics_schema: dict[str, Any],
    tracking_sources: dict[str, Any],
    runtime_log_exports: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    validation = validate_experiment(path, catalog, tracking_sources, runtime_log_exports)
    experiment_id = validation.get("experiment_id") or path.stem
    run_id = run_id_for(str(experiment_id), args.run_id)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = list(validation.get("warnings", []))

    if not validation.get("ok"):
        return {
            "ok": False,
            "path": str(path),
            "experiment_id": experiment_id,
            "run_id": run_id,
            "stage": "profile_validation",
            "errors": validation.get("errors", []),
            "warnings": warnings,
            "profile_rejection": validation.get("profile_rejection"),
        }

    profile = load_json(path)["experiment_profile"]
    launch_plan = bind_run_id(validation["launch_plan_skeleton"], run_id)
    launch_plan_hash = canonical_hash(launch_plan["launch_plan"])
    run_manifest = expand_manifest(
        validation["run_manifest_skeleton"],
        run_id,
        launch_plan_hash,
        Path(args.metrics_schema),
        Path(args.runtime_bindings),
        Path(args.runtime_log_exports),
        Path(args.tracking_sources),
    )
    runtime_checks = check_runtime_bindings(launch_plan, bindings)
    for check in runtime_checks:
        errors.extend(check["errors"])
    errors.extend(check_metrics(profile, catalog, metrics_schema))
    errors.extend(check_fastlio_state_gate(profile, catalog))
    runtime_export_contract = build_runtime_export_contract(profile, catalog)

    return {
        "ok": not errors,
        "path": str(path),
        "experiment_id": experiment_id,
        "run_id": run_id,
        "stage": "dry_run_preflight",
        "errors": errors,
        "warnings": warnings,
        "launch_plan_hash": launch_plan_hash,
        "runtime_checks": runtime_checks,
        "runtime_export_contract": runtime_export_contract,
        "launch_plan": launch_plan,
        "run_manifest_template": run_manifest,
    }


def emit_preflight_artifacts(report: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for item in report["results"]:
        experiment_id = item.get("experiment_id") or Path(item["path"]).stem
        (output_dir / f"{experiment_id}.preflight.json").write_text(
            json.dumps(item, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if item.get("ok"):
            (output_dir / f"{experiment_id}.LaunchPlan.json").write_text(
                json.dumps(item["launch_plan"], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            (output_dir / f"{experiment_id}.RUN_MANIFEST.template.json").write_text(
                json.dumps(item["run_manifest_template"], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiments", nargs="*", help="ExperimentProfile JSON files to preflight")
    parser.add_argument("--all", action="store_true", help="Preflight all Config/profiles/experiments/*.json")
    parser.add_argument("--include-blocked", action="store_true", help="With --all, include profile_status=blocked/archived audit profiles")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="Profile catalog JSON path")
    parser.add_argument("--runtime-bindings", default=str(DEFAULT_BINDINGS), help="Runtime binding JSON path")
    parser.add_argument("--metrics-schema", default=str(DEFAULT_METRICS_SCHEMA), help="Metrics schema JSON path")
    parser.add_argument("--runtime-log-exports", default=str(DEFAULT_RUNTIME_LOG_EXPORTS), help="RuntimeLogProfile registry JSON path")
    parser.add_argument("--tracking-sources", default=str(DEFAULT_TRACKING_SOURCES), help="TrackingSourceProfile registry JSON path")
    parser.add_argument("--run-id", help="Optional run id. Use only with one experiment for deterministic output.")
    parser.add_argument("--report", help="Optional JSON preflight report output path")
    parser.add_argument("--emit-artifacts-dir", help="Optional directory for preflight/LaunchPlan/RunManifest artifacts")
    args = parser.parse_args(argv)

    paths = collect_paths(args)
    if not paths:
        parser.error("provide experiment files or use --all")
    if args.run_id and len(paths) != 1:
        parser.error("--run-id can only be used with exactly one experiment")

    try:
        catalog, bindings, metrics_schema, tracking_sources, runtime_log_exports = load_catalogs(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    results = [
        build_preflight_for_path(path, catalog, bindings, metrics_schema, tracking_sources, runtime_log_exports, args)
        for path in paths
    ]
    report = {
        "ok": all(item["ok"] for item in results),
        "checked_count": len(results),
        "catalog": str(Path(args.catalog)),
        "runtime_bindings": str(Path(args.runtime_bindings)),
        "metrics_schema": str(Path(args.metrics_schema)),
        "runtime_log_exports": str(Path(args.runtime_log_exports)),
        "tracking_sources": str(Path(args.tracking_sources)),
        "results": results,
    }

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(payload + "\n", encoding="utf-8")
    if args.emit_artifacts_dir:
        emit_preflight_artifacts(report, Path(args.emit_artifacts_dir))
    print(payload)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
