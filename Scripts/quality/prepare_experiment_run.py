"""Materialize a MoSim ExperimentProfile run-prep directory.

This script is intentionally offline. It validates and preflights exactly one
ExperimentProfile, then writes a formal run preparation packet under the
selected output root. It does not start ROS, Gazebo, PX4, MAVROS, RViz, UE, or
MWORKS, and it does not create placeholder runtime evidence such as tracking.csv,
metrics.json, screenshots, logs, or review.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_experiment_preflight import (
    DEFAULT_BINDINGS,
    DEFAULT_CATALOG,
    DEFAULT_METRICS_SCHEMA,
    DEFAULT_RUNTIME_LOG_EXPORTS,
    DEFAULT_TRACKING_SOURCES,
    build_preflight_for_path,
    load_catalogs,
)
from check_experiment_profile import canonical_hash


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "runs"
IGNORED_HASH_DIRS = {".git", "__pycache__", ".pytest_cache", "build", "devel", "install", "logs"}
IGNORED_HASH_SUFFIXES = {".bag", ".db3", ".log", ".tmp", ".pyc", ".png", ".jpg", ".jpeg", ".avi", ".mp4"}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative_display(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def add_error(errors: list[dict[str, str]], code: str, message: str) -> None:
    errors.append({"code": code, "message": message})


def run_git(args: list[str]) -> str | None:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def iter_hashable_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        return []
    files: list[Path] = []
    for child in sorted(path.rglob("*")):
        if not child.is_file():
            continue
        relative_parts = set(child.relative_to(path).parts)
        if relative_parts & IGNORED_HASH_DIRS:
            continue
        if child.suffix.lower() in IGNORED_HASH_SUFFIXES:
            continue
        files.append(child)
    return files


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_source_path(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    files = iter_hashable_files(resolved)
    if resolved.is_file():
        return {
            "path": relative_display(resolved),
            "type": "file",
            "exists": True,
            "sha256": file_sha256(resolved),
            "file_count": 1,
            "total_bytes": resolved.stat().st_size,
        }
    if not resolved.exists():
        return {
            "path": relative_display(resolved),
            "type": "missing",
            "exists": False,
            "sha256": None,
            "file_count": 0,
            "total_bytes": 0,
        }

    entries = []
    total_bytes = 0
    for file_path in files:
        total_bytes += file_path.stat().st_size
        entries.append(
            {
                "path": str(file_path.relative_to(resolved)).replace("\\", "/"),
                "sha256": file_sha256(file_path),
            }
        )
    return {
        "path": relative_display(resolved),
        "type": "directory",
        "exists": True,
        "sha256": canonical_hash(entries),
        "file_count": len(entries),
        "total_bytes": total_bytes,
    }


def collect_source_paths(preflight: dict[str, Any]) -> list[Path]:
    paths: list[Path] = [
        resolve_project_path(preflight["path"]),
        DEFAULT_CATALOG,
        DEFAULT_BINDINGS,
        DEFAULT_METRICS_SCHEMA,
        DEFAULT_RUNTIME_LOG_EXPORTS,
        DEFAULT_TRACKING_SOURCES,
    ]
    manifest = preflight["run_manifest_template"]["run_manifest"]
    for key in ("runtime_bindings", "metrics_schema", "runtime_log_exports", "tracking_sources"):
        value = manifest.get(key)
        if isinstance(value, str):
            paths.append(resolve_project_path(value))
    for check in preflight.get("runtime_checks", []):
        for value in check.get("required_paths", []):
            paths.append(resolve_project_path(value))

    deduped: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path.resolve())
        if key not in seen:
            seen.add(key)
            deduped.append(path)
    return deduped


def build_source_hash_packet(preflight: dict[str, Any]) -> dict[str, Any]:
    source_paths = collect_source_paths(preflight)
    git_commit = run_git(["rev-parse", "HEAD"])
    git_status = run_git(["status", "--porcelain", "--"] + [relative_display(path) for path in source_paths])
    sources = [hash_source_path(path) for path in source_paths]
    return {
        "schema_version": 1,
        "generator": "Scripts/quality/prepare_experiment_run.py",
        "run_id": preflight["run_id"],
        "experiment_id": preflight["experiment_id"],
        "git": {
            "commit": git_commit or "unknown",
            "dirty": bool(git_status),
            "status_porcelain": git_status or "",
        },
        "hash_policy": {
            "ignored_dirs": sorted(IGNORED_HASH_DIRS),
            "ignored_suffixes": sorted(IGNORED_HASH_SUFFIXES),
        },
        "sources": sources,
        "aggregate_sha256": canonical_hash(sources),
    }


def bind_source_state(preflight: dict[str, Any], source_hashes_path: Path, source_hash_packet: dict[str, Any]) -> dict[str, Any]:
    manifest_packet = deepcopy(preflight["run_manifest_template"])
    manifest = manifest_packet["run_manifest"]
    manifest["source_state"] = {
        "git_commit": source_hash_packet["git"]["commit"],
        "git_dirty": source_hash_packet["git"]["dirty"],
        "source_hashes": relative_display(source_hashes_path),
        "source_hashes_sha256": canonical_hash(source_hash_packet),
        "source_hashes_aggregate_sha256": source_hash_packet["aggregate_sha256"],
    }
    return manifest_packet


def build_operator_checklist(preflight: dict[str, Any]) -> str:
    launch_plan = preflight["launch_plan"]["launch_plan"]
    runtime_checks = preflight.get("runtime_checks", [])
    runtime_export = preflight.get("runtime_export_contract", {})
    lines = [
        "# Operator Checklist",
        "",
        f"Run ID: `{preflight['run_id']}`",
        f"ExperimentProfile: `{preflight['experiment_id']}`",
        "",
        "This packet is a pre-run preparation artifact. It is not runtime evidence.",
        "",
        "## Before Launch",
        "",
        "- Confirm `preflight.json` has `ok=true`.",
        "- Confirm `LaunchPlan.json` and `RUN_MANIFEST.json` belong to this run_id.",
        "- Confirm runtime source paths listed below exist in the active ROS1/Sunray lane.",
        "- Confirm `source_hashes.json` records the exact source tree used for this run.",
        "- Do not change controller, state source, adapter, plant, or truth profile after launch.",
        "",
        "## Runtime Templates",
        "",
    ]
    checks_by_template = {item.get("template"): item for item in runtime_checks}
    for step in launch_plan.get("steps", []):
        template = step.get("template")
        check = checks_by_template.get(template, {})
        lines.append(f"- `{step.get('id')}`: template `{template}`, profile `{step.get('profile')}`")
        for required in check.get("required_paths", []):
            lines.append(f"  - required path: `{required}`")
    lines.extend(
        [
            "",
            "## After Run",
            "",
            f"- Use RuntimeExportProfile `{runtime_export.get('runtime_export_profile')}`.",
            f"- Collect with RuntimeLogProfile `{runtime_export.get('runtime_log_profile')}`.",
            f"- Build tracking with TrackingSourceProfile `{runtime_export.get('tracking_source_profile')}`.",
            "- Export the required artifacts below before running the evidence gate.",
            "",
            "## Required Runtime Exports",
            "",
        ]
    )
    for artifact in runtime_export.get("required_artifacts", []):
        lines.append(
            f"- `{artifact.get('slot')}` -> `{artifact.get('destination')}` "
            f"from `{artifact.get('producer')}`"
        )
        command_template = artifact.get("command_template")
        if command_template:
            lines.append(f"  - export note: {command_template}")
        required_columns = artifact.get("required_columns") or []
        if required_columns:
            lines.append("  - required columns: " + ", ".join(f"`{column}`" for column in required_columns))
    review_requirements = runtime_export.get("review_requirements", [])
    if review_requirements:
        lines.extend(["", "## RViz Review Requirements", ""])
        for requirement in review_requirements:
            lines.append(f"- {requirement}")
    lines.extend(
        [
            "",
            "## Final Evidence Gate",
            "",
            "- Compute `metrics.json` from `tracking.csv`.",
            "- Write factual `review.md` after inspecting the run.",
            "- Run `python Scripts/quality/check_run_evidence.py <run_dir>` before review.",
            "",
        ]
    )
    return "\n".join(lines)


def build_commands_doc(preflight: dict[str, Any], run_dir: Path) -> str:
    launch_plan = preflight["launch_plan"]["launch_plan"]
    runtime_export = preflight.get("runtime_export_contract", {})
    export_artifacts = runtime_export.get("required_artifacts", [])
    run_dir_display = relative_display(run_dir)
    artifact_args = " ".join(
        f"--artifact {artifact.get('slot')}=<path-to-{artifact.get('slot')}>"
        for artifact in export_artifacts
    )
    lines = [
        "# Run Commands",
        "",
        "These are orchestration templates, not proof that runtime was started.",
        "Only run them when the live ROS1/Sunray/Gazebo/PX4 scope is explicitly open.",
        "",
        "## Static Checks",
        "",
        "```powershell",
        f"python Scripts/quality/build_experiment_preflight.py --run-id {preflight['run_id']} {preflight['path']}",
        f"python Scripts/quality/check_run_evidence.py {run_dir_display}",
        "```",
        "",
        "## LaunchPlan Template Order",
        "",
    ]
    for index, step in enumerate(launch_plan.get("steps", []), start=1):
        lines.append(
            f"{index}. `{step.get('id')}` -> `{step.get('template')}` "
            f"with profile `{step.get('profile')}`"
        )
    lines.extend(
        [
            "",
            "## Runtime Export Contract",
            "",
            f"RuntimeExportProfile: `{runtime_export.get('runtime_export_profile')}`",
            f"RuntimeLogProfile: `{runtime_export.get('runtime_log_profile')}`",
            f"TrackingSourceProfile: `{runtime_export.get('tracking_source_profile')}`",
            "",
            "Required export slots:",
            "",
        ]
    )
    for artifact in export_artifacts:
        lines.append(
            f"- `{artifact.get('slot')}` -> `{artifact.get('destination')}` "
            f"from `{artifact.get('producer')}`"
        )
        command_template = artifact.get("command_template")
        if command_template:
            lines.append(f"  - {command_template}")
    lines.extend(
        [
            "",
            "Collect exported runtime evidence into the run packet:",
            "",
            "```powershell",
            f"python Scripts/quality/export_runtime_sources.py {run_dir_display} --runtime-export-profile {runtime_export.get('runtime_export_profile')} {artifact_args} --review-file <review.md> --build-tracking --force",
            "```",
            "",
            "## Metrics",
            "",
            "```powershell",
            f"python Scripts/quality/compute_tracking_metrics.py {run_dir_display}/tracking.csv --manifest {run_dir_display}/RUN_MANIFEST.json --out {run_dir_display}/metrics.json",
            f"python Scripts/quality/check_metric_thresholds.py {run_dir_display}/metrics.json --manifest {run_dir_display}/RUN_MANIFEST.json --report {run_dir_display}/threshold_report.json",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def build_review_template(preflight: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Review Template",
            "",
            f"Run ID: `{preflight['run_id']}`",
            f"ExperimentProfile: `{preflight['experiment_id']}`",
            "",
            "Replace this template with `review.md` only after a real run.",
            "",
            "## Evidence Observed",
            "",
            "- RViz point cloud / trajectory:",
            "- Gazebo visual state:",
            "- Logs checked:",
            "- Metrics checked:",
            "",
            "## Result",
            "",
            "- Accepted / rejected:",
            "- Reason:",
            "",
        ]
    )


def materialize_run(preflight: dict[str, Any], output_root: Path, force: bool) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    run_id = preflight["run_id"]
    run_dir = output_root / run_id

    if run_dir.exists() and not force:
        add_error(errors, "RUN-PREP-01", f"run directory already exists: {run_dir}")
        return {
            "ok": False,
            "run_id": run_id,
            "run_dir": str(run_dir),
            "runtime_started": False,
            "errors": errors,
            "warnings": [],
        }

    run_dir.mkdir(parents=True, exist_ok=True)
    created_dirs = []
    for dirname in ("screenshots", "logs", "raw"):
        directory = run_dir / dirname
        directory.mkdir(exist_ok=True)
        created_dirs.append(relative_display(directory))

    source_hashes_path = run_dir / "source_hashes.json"
    source_hash_packet = build_source_hash_packet(preflight)
    run_manifest = bind_source_state(preflight, source_hashes_path, source_hash_packet)

    files = {
        "LaunchPlan.json": preflight["launch_plan"],
        "RUN_MANIFEST.json": run_manifest,
        "preflight.json": preflight,
        "source_hashes.json": source_hash_packet,
    }
    written_files: list[str] = []
    for filename, payload in files.items():
        path = run_dir / filename
        write_json(path, payload)
        written_files.append(relative_display(path))

    text_files = {
        "operator_checklist.md": build_operator_checklist(preflight),
        "commands.md": build_commands_doc(preflight, run_dir),
        "review.template.md": build_review_template(preflight),
    }
    for filename, text in text_files.items():
        path = run_dir / filename
        path.write_text(text, encoding="utf-8")
        written_files.append(relative_display(path))

    warnings = []
    if force:
        warnings.append(
            {
                "code": "RUN-PREP-FORCE",
                "message": "existing preparation files may have been overwritten; runtime evidence files were not deleted",
            }
        )

    return {
        "ok": True,
        "run_id": run_id,
        "experiment_id": preflight["experiment_id"],
        "run_dir": relative_display(run_dir),
        "runtime_started": False,
        "evidence_complete": False,
        "written_files": written_files,
        "created_dirs": created_dirs,
        "missing_after_run": [
            "runtime_export_manifest.json",
            "runtime_log_manifest.json",
            "tracking.csv",
            "metrics.json",
            "threshold_report.json",
            "review.md",
            "screenshots/*",
            "logs/*",
        ],
        "errors": [],
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", help="ExperimentProfile JSON file")
    parser.add_argument("--run-id", help="Run id to bind into LaunchPlan and RUN_MANIFEST")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Root directory for run packets")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="Profile catalog JSON path")
    parser.add_argument("--runtime-bindings", default=str(DEFAULT_BINDINGS), help="Runtime binding JSON path")
    parser.add_argument("--metrics-schema", default=str(DEFAULT_METRICS_SCHEMA), help="Metrics schema JSON path")
    parser.add_argument("--runtime-log-exports", default=str(DEFAULT_RUNTIME_LOG_EXPORTS), help="RuntimeLogProfile registry JSON path")
    parser.add_argument("--tracking-sources", default=str(DEFAULT_TRACKING_SOURCES), help="TrackingSourceProfile registry JSON path")
    parser.add_argument("--force", action="store_true", help="Overwrite preparation files if the run directory exists")
    parser.add_argument("--report", help="Optional JSON report output path")
    args = parser.parse_args(argv)

    try:
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
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not preflight.get("ok"):
        report = {
            "ok": False,
            "stage": "preflight",
            "runtime_started": False,
            "errors": preflight.get("errors", []),
            "warnings": preflight.get("warnings", []),
            "preflight": preflight,
        }
        payload = json.dumps(report, ensure_ascii=False, indent=2)
        if args.report:
            Path(args.report).write_text(payload + "\n", encoding="utf-8")
        print(payload)
        return 1

    report = materialize_run(preflight, Path(args.output_root), args.force)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
