#!/usr/bin/env python3
"""Copy one approved Config/Results archive candidate outside the repository.

The tool is deliberately copy-only. It never removes or changes the source
paths, refuses a destination inside the repository, and refuses to overwrite
an existing archive destination.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "Docs" / "Design" / "config_results_packaging_archive_manifest_20260731.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, help="archive_candidates[].id from the audit manifest")
    parser.add_argument("--destination", required=True, type=Path, help="new external archive directory")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, type=Path)
    parser.add_argument("--apply", action="store_true", help="perform the copy; omit for a hash-only dry run")
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_candidate(manifest_path: Path, candidate_id: str) -> dict[str, Any]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidates = data.get("archive_candidates")
    if not isinstance(candidates, list):
        raise ValueError("archive manifest has no archive_candidates list")
    for candidate in candidates:
        if isinstance(candidate, dict) and candidate.get("id") == candidate_id:
            if candidate.get("action") != "archive_candidate_after_dependency_audit":
                raise ValueError(f"candidate {candidate_id!r} is not copy-archive eligible")
            paths = candidate.get("paths")
            if not isinstance(paths, list) or not paths or not all(isinstance(path, str) and path for path in paths):
                raise ValueError(f"candidate {candidate_id!r} has invalid paths")
            return candidate
    raise ValueError(f"archive candidate not found: {candidate_id}")


def repo_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"source path must be repository-relative: {value}")
    resolved = ROOT / path
    if not resolved.is_dir():
        raise ValueError(f"source path must be an existing directory: {value}")
    return resolved


def external_destination(value: Path) -> Path:
    destination = value.expanduser().resolve(strict=False)
    root = ROOT.resolve()
    try:
        destination.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("archive destination must be outside the repository")
    if destination.exists():
        raise ValueError(f"archive destination already exists: {destination}")
    if destination.name in {"", ".", ".."}:
        raise ValueError("archive destination must name a new directory")
    return destination


def collect_records(source_paths: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for source_root in source_paths:
        files = sorted(path for path in source_root.rglob("*") if path.is_file())
        for file_path in files:
            if file_path.is_symlink():
                raise ValueError(f"refusing symlinked archive file: {file_path}")
            relative = file_path.relative_to(ROOT).as_posix()
            records.append(
                {
                    "source_relpath": relative,
                    "archive_relpath": relative,
                    "size_bytes": file_path.stat().st_size,
                    "sha256": sha256(file_path),
                }
            )
    return records


def write_archive_metadata(staging: Path, candidate: dict[str, Any], records: list[dict[str, Any]], destination: Path) -> None:
    manifest = {
        "schema_version": "1.0",
        "archive_id": candidate["id"],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "copy_mode": "copy_only_sources_retained",
        "source_repository": str(ROOT),
        "archive_destination": str(destination),
        "source_paths": candidate["paths"],
        "file_count": len(records),
        "total_bytes": sum(record["size_bytes"] for record in records),
        "files": records,
    }
    (staging / "ARCHIVE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    checksum_lines = [f"{record['sha256']}  {record['archive_relpath']}" for record in records]
    (staging / "SHA256SUMS.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    readme = "\n".join(
        [
            "# MoSim Historical Archive",
            "",
            f"Archive candidate: `{candidate['id']}`",
            "",
            "This directory is a verified copy. The original files remain in the MoSim repository.",
            "See ARCHIVE_MANIFEST.json and SHA256SUMS.txt for the source-relative inventory.",
            "Do not treat this archive as current release evidence without its source/result binding.",
            "",
        ]
    )
    (staging / "ARCHIVE_README.md").write_text(readme, encoding="utf-8")


def copy_and_verify(source_paths: list[Path], records: list[dict[str, Any]], candidate: dict[str, Any], destination: Path) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    staging = destination.parent / f".{destination.name}.staging-{stamp}-{os.getpid()}"
    if staging.exists():
        raise ValueError(f"staging path already exists: {staging}")
    staging.mkdir()
    try:
        for source_root in source_paths:
            target_root = staging / source_root.relative_to(ROOT)
            target_root.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source_root, target_root, copy_function=shutil.copy2)
        mismatches: list[str] = []
        for record in records:
            copied = staging / record["archive_relpath"]
            if not copied.is_file():
                mismatches.append(f"missing copied file: {record['archive_relpath']}")
            elif copied.stat().st_size != record["size_bytes"]:
                mismatches.append(f"size mismatch: {record['archive_relpath']}")
            elif sha256(copied) != record["sha256"]:
                mismatches.append(f"sha256 mismatch: {record['archive_relpath']}")
        if mismatches:
            raise ValueError("archive verification failed: " + "; ".join(mismatches[:8]))
        write_archive_metadata(staging, candidate, records, destination)
        staging.rename(destination)
    except Exception as exc:
        raise RuntimeError(f"archive copy failed; staging retained at {staging}: {exc}") from exc
    manifest_path = destination / "ARCHIVE_MANIFEST.json"
    return {
        "ok": True,
        "archive_path": str(destination),
        "archive_manifest": str(manifest_path),
        "archive_manifest_sha256": sha256(manifest_path),
        "file_count": len(records),
        "total_bytes": sum(record["size_bytes"] for record in records),
        "source_changed": False,
    }


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    try:
        candidate = load_candidate(manifest_path, args.candidate)
        source_paths = [repo_path(value) for value in candidate["paths"]]
        destination = external_destination(args.destination)
        records = collect_records(source_paths)
        summary = {
            "ok": True,
            "dry_run": not args.apply,
            "candidate": candidate["id"],
            "source_paths": candidate["paths"],
            "destination": str(destination),
            "file_count": len(records),
            "total_bytes": sum(record["size_bytes"] for record in records),
            "source_changed": False,
        }
        if args.apply:
            summary = copy_and_verify(source_paths, records, candidate, destination)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
