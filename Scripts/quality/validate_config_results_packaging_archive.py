#!/usr/bin/env python3
"""Validate the non-destructive Config/Results packaging archive manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "Docs" / "Design" / "config_results_packaging_archive_manifest_20260731.json"
SECTIONS = ("source_release", "evidence_bundles", "archive_candidates", "owner_locked")
ALLOWED_ACTIONS = {
    "keep_in_source_release",
    "keep_in_evidence_bundle",
    "retain_immutable_history",
    "archive_candidate_after_dependency_audit",
    "child_manifest_required",
    "exclude_from_source_release",
    "owner_locked",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, help="Optional JSON validation report path.")
    return parser.parse_args()


def as_repo_path(value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"path must be repository-relative: {value}")
    return ROOT / candidate


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read manifest {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("manifest root must be an object")
    return data


def validate_entry(section: str, entry: Any, errors: list[str], checked_paths: list[str]) -> None:
    if not isinstance(entry, dict):
        errors.append(f"{section}: entry is not an object")
        return
    entry_id = entry.get("id")
    action = entry.get("action")
    paths = entry.get("paths")
    if not isinstance(entry_id, str) or not entry_id:
        errors.append(f"{section}: missing non-empty id")
    if action not in ALLOWED_ACTIONS:
        errors.append(f"{section}:{entry_id or '<unknown>'}: unsupported action {action!r}")
    if not isinstance(paths, list) or not paths or not all(isinstance(item, str) and item for item in paths):
        errors.append(f"{section}:{entry_id or '<unknown>'}: paths must be a non-empty string list")
        return
    for item in paths:
        try:
            resolved = as_repo_path(item)
        except ValueError as exc:
            errors.append(f"{section}:{entry_id or '<unknown>'}: {exc}")
            continue
        checked_paths.append(item)
        if not resolved.exists():
            errors.append(f"{section}:{entry_id or '<unknown>'}: missing path {item}")
    reason = entry.get("reason")
    preconditions = entry.get("preconditions")
    if not isinstance(reason, str) or len(reason.strip()) < 12:
        errors.append(f"{section}:{entry_id or '<unknown>'}: reason is too short")
    if not isinstance(preconditions, list) or not preconditions or not all(isinstance(item, str) and item for item in preconditions):
        errors.append(f"{section}:{entry_id or '<unknown>'}: preconditions must be a non-empty string list")
    if action == "owner_locked" and not isinstance(entry.get("owner"), str):
        errors.append(f"{section}:{entry_id or '<unknown>'}: owner_locked entry needs an owner")


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    errors: list[str] = []
    checked_paths: list[str] = []
    try:
        manifest = load_manifest(manifest_path)
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if manifest.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    if manifest.get("scope") != "non_destructive_config_results_packaging_audit":
        errors.append("scope must declare the non-destructive packaging audit")
    if manifest.get("non_destructive") is not True:
        errors.append("non_destructive must be true")
    if not isinstance(manifest.get("explicitly_not_authorized"), list):
        errors.append("explicitly_not_authorized must be a list")

    entry_count = 0
    for section in SECTIONS:
        entries = manifest.get(section)
        if not isinstance(entries, list) or not entries:
            errors.append(f"{section} must be a non-empty list")
            continue
        for entry in entries:
            entry_count += 1
            validate_entry(section, entry, errors, checked_paths)

    legacy_candidate = next(
        (
            entry
            for entry in manifest.get("archive_candidates", [])
            if isinstance(entry, dict) and entry.get("id") == "legacy_example1_robustness_pair"
        ),
        None,
    )
    if not isinstance(legacy_candidate, dict) or "Results/robustness" not in legacy_candidate.get("paths", []):
        errors.append("legacy Example1 robustness batch must remain an explicit archive candidate")

    report = {
        "manifest": manifest_path.relative_to(ROOT).as_posix() if manifest_path.is_relative_to(ROOT) else str(manifest_path),
        "entry_count": entry_count,
        "checked_path_count": len(checked_paths),
        "non_destructive": manifest.get("non_destructive"),
        "ok": not errors,
        "errors": errors,
    }
    if args.output:
        output_path = args.output if args.output.is_absolute() else ROOT / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    if errors:
        print(json.dumps(report, indent=2, ensure_ascii=True), file=sys.stderr)
        return 1
    print(
        "PASS: Config/Results packaging archive manifest "
        f"validated ({entry_count} entries, {len(checked_paths)} existing paths, non-destructive)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
