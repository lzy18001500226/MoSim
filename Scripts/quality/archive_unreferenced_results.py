#!/usr/bin/env python3
"""Archive verified untracked Results directories under the canonical external root.

This is deliberately narrower than a generic cleanup tool.  It accepts only
untracked directories under ``Results/``, copies them to a new external archive
directory, verifies every file by SHA-256 twice, removes only the verified
source data, and leaves a small source-location tombstone.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from external_archive_root import validate_external_archive_destination


ROOT = Path(__file__).resolve().parents[2]
TOMBSTONE_NAME = "ARCHIVED_EXTERNALLY.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-id", required=True)
    parser.add_argument(
        "--destination",
        required=True,
        type=Path,
        help=r"archive batch directly under E:\刘致远18001500226\MoSim_Archive",
    )
    parser.add_argument(
        "--source",
        action="append",
        required=True,
        help="Repository-relative untracked Results directory. Repeat for each root.",
    )
    parser.add_argument(
        "--audit-note",
        default="",
        help="Human-readable dependency-audit conclusion retained in the external manifest.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Copy, verify, remove source data, and leave tombstones. Omit for a dry run.",
    )
    parser.add_argument(
        "--resume-staging",
        type=Path,
        help="Resume an already copied staging directory after re-verifying it. Requires --apply.",
    )
    parser.add_argument(
        "--finalize-existing",
        action="store_true",
        help=(
            "Finalize selected source roots from an existing verified archive without copying "
            "them again. Requires --apply and an existing destination."
        ),
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_source(value: str) -> Path:
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or relative.parts[:1] != ("Results",):
        raise ValueError(f"source must be a repository-relative Results directory: {value}")
    resolved = (ROOT / relative).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"source escapes repository: {value}") from exc
    if not resolved.is_dir():
        raise ValueError(f"source directory does not exist: {value}")
    return resolved


def resolve_destination(value: Path, *, must_exist: bool = False) -> Path:
    return validate_external_archive_destination(
        value,
        repository_root=ROOT,
        must_exist=must_exist,
    )


def resolve_staging(value: Path, destination: Path) -> Path:
    staging = value.expanduser().resolve()
    if not staging.is_dir():
        raise ValueError(f"staging directory does not exist: {staging}")
    if staging.parent != destination.parent:
        raise ValueError("staging directory must share the archive destination parent")
    expected_prefix = f".{destination.name}.staging-"
    if not staging.name.startswith(expected_prefix):
        raise ValueError(f"staging directory must start with {expected_prefix!r}")
    return staging


def ensure_untracked(source: Path) -> None:
    result = subprocess.run(
        ["git", "ls-files", "--", source.relative_to(ROOT).as_posix()],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    if result.stdout.strip():
        raise ValueError(f"refusing tracked source directory: {source.relative_to(ROOT)}")


def collect_records(sources: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for source in sources:
        for path in sorted(source.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"refusing symlinked archive entry: {path}")
            if path.is_file():
                relative = path.relative_to(ROOT).as_posix()
                records.append(
                    {
                        "source_relpath": relative,
                        "archive_relpath": relative,
                        "size_bytes": path.stat().st_size,
                        "sha256": sha256(path),
                    }
                )
    return records


def verify_records(base: Path, records: list[dict[str, Any]]) -> None:
    for record in records:
        candidate = base / record["archive_relpath"]
        if not candidate.is_file():
            raise ValueError(f"missing file during verification: {record['archive_relpath']}")
        if candidate.stat().st_size != record["size_bytes"]:
            raise ValueError(f"size mismatch during verification: {record['archive_relpath']}")
        if sha256(candidate) != record["sha256"]:
            raise ValueError(f"SHA-256 mismatch during verification: {record['archive_relpath']}")


def write_metadata(destination: Path, payload: dict[str, Any]) -> Path:
    manifest = destination / "ARCHIVE_MANIFEST.json"
    manifest.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    sums = [f"{record['sha256']}  {record['archive_relpath']}" for record in payload["files"]]
    (destination / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
    (destination / "ARCHIVE_README.md").write_text(
        "# MoSim Local Archive\n\n"
        "This archive contains local untracked Results data removed only after a SHA-256 verified copy.\n"
        "See ARCHIVE_MANIFEST.json and SHA256SUMS.txt for exact provenance.\n",
        encoding="utf-8",
    )
    return manifest


def write_tombstone(source: Path, archive_id: str, destination: Path) -> None:
    source.mkdir(parents=True, exist_ok=True)
    (source / TOMBSTONE_NAME).write_text(
        "# Archived Local Results\n\n"
        f"The prior untracked local data was archived as `{archive_id}` at:\n\n"
        f"`{destination}`\n\n"
        "The external archive was SHA-256 verified before source data removal.\n",
        encoding="utf-8",
    )


def records_for_source(records: list[dict[str, Any]], source: Path) -> list[dict[str, Any]]:
    prefix = source.relative_to(ROOT).as_posix().rstrip("/") + "/"
    selected = [record for record in records if record["source_relpath"].startswith(prefix)]
    if not selected:
        raise ValueError(f"existing archive contains no files for source: {source.relative_to(ROOT)}")
    return selected


def ensure_source_matches_records(source: Path, expected: list[dict[str, Any]]) -> None:
    current = collect_records([source])
    current_signature = [
        (record["source_relpath"], record["size_bytes"], record["sha256"])
        for record in current
    ]
    expected_signature = [
        (record["source_relpath"], record["size_bytes"], record["sha256"])
        for record in expected
    ]
    if current_signature != expected_signature:
        raise ValueError(
            f"source no longer matches the existing verified archive: {source.relative_to(ROOT)}"
        )


def source_removal_state(
    source_paths: list[str],
    *,
    error: str | None = None,
    failed_source: str | None = None,
) -> dict[str, Any]:
    removed: list[str] = []
    retained: list[str] = []
    missing_without_tombstone: list[str] = []
    for relative in source_paths:
        source = ROOT / relative
        if (source / TOMBSTONE_NAME).is_file():
            removed.append(relative)
        elif source.exists():
            retained.append(relative)
        else:
            missing_without_tombstone.append(relative)
    state: dict[str, Any] = {
        "status": "completed"
        if not retained and not missing_without_tombstone
        else "partially_completed",
        "updated_at_utc": utc_now(),
        "removed_data_roots": removed,
        "retained_source_roots": retained,
        "missing_without_tombstone_roots": missing_without_tombstone,
        "tombstone_name": TOMBSTONE_NAME,
    }
    if error:
        state["error"] = error
    if failed_source:
        state["failed_source_root"] = failed_source
    return state


def finalize_existing_archive(
    args: argparse.Namespace,
    sources: list[Path],
    destination: Path,
) -> int:
    manifest_path = destination / "ARCHIVE_MANIFEST.json"
    if not manifest_path.is_file():
        raise ValueError(f"existing archive has no manifest: {manifest_path}")
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("archive_id") != args.archive_id:
        raise ValueError("archive id does not match the existing manifest")
    source_paths = payload.get("source_paths")
    records = payload.get("files")
    if not isinstance(source_paths, list) or not isinstance(records, list):
        raise ValueError("existing archive manifest is missing source_paths or files")
    requested_paths = [source.relative_to(ROOT).as_posix() for source in sources]
    unknown = sorted(set(requested_paths) - set(source_paths))
    if unknown:
        raise ValueError(f"sources are not present in existing archive: {', '.join(unknown)}")
    verify_records(destination, records)

    for source in sources:
        if (source / TOMBSTONE_NAME).exists():
            raise ValueError(f"source was already removed and tombstoned: {source.relative_to(ROOT)}")
        expected = records_for_source(records, source)
        verify_records(ROOT, expected)
        ensure_source_matches_records(source, expected)

    for source in sources:
        try:
            shutil.rmtree(source)
            write_tombstone(source, args.archive_id, destination)
        except OSError as exc:
            payload["source_removal"] = source_removal_state(
                source_paths,
                error=str(exc),
                failed_source=source.relative_to(ROOT).as_posix(),
            )
            payload["dependency_audit"] = args.audit_note or payload.get(
                "dependency_audit", "No audit note supplied."
            )
            write_metadata(destination, payload)
            raise OSError(f"source archive removal incomplete: {exc}") from exc

    payload["source_removal"] = source_removal_state(source_paths)
    if args.audit_note:
        payload["dependency_audit"] = args.audit_note
    write_metadata(destination, payload)
    summary = {
        "ok": True,
        "dry_run": False,
        "archive_id": args.archive_id,
        "destination": str(destination),
        "source_changed": True,
        "finalized_source_roots": requested_paths,
        "source_removal": payload["source_removal"],
        "archive_manifest": str(manifest_path),
        "archive_manifest_sha256": sha256(manifest_path),
    }
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0


def main() -> int:
    args = parse_args()
    try:
        if args.resume_staging is not None and not args.apply:
            raise ValueError("--resume-staging requires --apply")
        if args.finalize_existing and not args.apply:
            raise ValueError("--finalize-existing requires --apply")
        if args.finalize_existing and args.resume_staging is not None:
            raise ValueError("--finalize-existing cannot be combined with --resume-staging")
        sources = [resolve_source(value) for value in args.source]
        if len({source.resolve() for source in sources}) != len(sources):
            raise ValueError("duplicate source directory")
        for source in sources:
            ensure_untracked(source)
        destination = resolve_destination(args.destination, must_exist=args.finalize_existing)
        if args.finalize_existing:
            return finalize_existing_archive(args, sources, destination)
        records = collect_records(sources)
        summary: dict[str, Any] = {
            "ok": True,
            "dry_run": not args.apply,
            "archive_id": args.archive_id,
            "destination": str(destination),
            "source_paths": [source.relative_to(ROOT).as_posix() for source in sources],
            "file_count": len(records),
            "total_bytes": sum(record["size_bytes"] for record in records),
            "source_changed": False,
        }
        if not args.apply:
            print(json.dumps(summary, ensure_ascii=True, indent=2))
            return 0

        destination.parent.mkdir(parents=True, exist_ok=True)
        if args.resume_staging is not None:
            staging = resolve_staging(args.resume_staging, destination)
            verify_records(staging, records)
        else:
            staging = destination.parent / f".{destination.name}.staging-{os.getpid()}"
            if staging.exists():
                raise ValueError(f"archive staging already exists: {staging}")
            staging.mkdir()
            for source in sources:
                target = staging / source.relative_to(ROOT)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(source, target, copy_function=shutil.copy2)
            verify_records(staging, records)
        # Do not remove data if an active process changed it during copying.
        verify_records(ROOT, records)
        payload: dict[str, Any] = {
            "schema_version": "1.0",
            "archive_id": args.archive_id,
            "created_at_utc": utc_now(),
            "archive_mode": "copy_verify_then_remove_untracked_sources",
            "source_repository": str(ROOT),
            "source_paths": summary["source_paths"],
            "file_count": len(records),
            "total_bytes": summary["total_bytes"],
            "files": records,
            "dependency_audit": args.audit_note or "No audit note supplied.",
            "source_removal": {"status": "pending", "tombstone_name": TOMBSTONE_NAME},
        }
        write_metadata(staging, payload)
        staging.replace(destination)

        for source in sources:
            try:
                shutil.rmtree(source)
                write_tombstone(source, args.archive_id, destination)
            except OSError as exc:
                payload["source_removal"] = source_removal_state(
                    payload["source_paths"],
                    error=str(exc),
                    failed_source=source.relative_to(ROOT).as_posix(),
                )
                write_metadata(destination, payload)
                raise OSError(f"source archive removal incomplete: {exc}") from exc
        payload["source_removal"] = source_removal_state(payload["source_paths"])
        manifest_path = write_metadata(destination, payload)
        summary.update(
            {
                "dry_run": False,
                "source_changed": True,
                "removed_data_roots": payload["source_removal"]["removed_data_roots"],
                "archive_manifest": str(manifest_path),
                "archive_manifest_sha256": sha256(manifest_path),
            }
        )
        print(json.dumps(summary, ensure_ascii=True, indent=2))
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
