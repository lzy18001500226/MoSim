#!/usr/bin/env python3
"""Copy one approved Config/Results archive candidate to the canonical external root.

The tool is deliberately copy-only. It never removes or changes the source
paths, refuses a destination inside the repository, and refuses to overwrite
an existing archive destination.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import shutil
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from external_archive_root import validate_external_archive_destination


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "Docs" / "Design" / "架构" / "03_测试调参与证据" / "交付与审计" / "config_results_packaging_archive_manifest_20260731.json"
FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
LX_SYMLINK_REPARSE_TAG = 0xA000001D
LX_SYMLINK_POLICY = "record_lx_symlink_metadata"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, help="archive_candidates[].id from the audit manifest")
    parser.add_argument(
        "--destination",
        required=True,
        type=Path,
        help=r"new batch directly under E:\刘致远18001500226\MoSim_Archive",
    )
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
    return validate_external_archive_destination(value, repository_root=ROOT)


def format_reparse_tag(value: int) -> str:
    return f"0x{value:08x}"


def configured_reparse_points(candidate: dict[str, Any], source_paths: list[Path]) -> dict[str, dict[str, str]]:
    policy = candidate.get("reparse_point_policy")
    configured = candidate.get("reparse_points")
    if policy is None and configured is None:
        return {}
    if policy != LX_SYMLINK_POLICY:
        raise ValueError(f"unsupported reparse-point policy: {policy!r}")
    if not isinstance(configured, list) or not configured:
        raise ValueError("LX_SYMLINK metadata mode requires a non-empty reparse_points list")

    allowed_roots = [source.resolve() for source in source_paths]
    entries: dict[str, dict[str, str]] = {}
    for item in configured:
        if not isinstance(item, dict):
            raise ValueError("reparse-point metadata entry must be an object")
        expected = {
            key: item.get(key)
            for key in ("source_relpath", "reparse_tag", "reparse_data_sha256", "target")
        }
        if not all(isinstance(value, str) and value for value in expected.values()):
            raise ValueError("reparse-point metadata entries need source_relpath, reparse_tag, reparse_data_sha256, and target")
        source_relpath = expected["source_relpath"]
        path = Path(source_relpath)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"invalid reparse-point source path: {source_relpath}")
        resolved = (ROOT / path).resolve(strict=False)
        if not any(resolved.is_relative_to(root) for root in allowed_roots):
            raise ValueError(f"reparse-point is outside the candidate source roots: {source_relpath}")
        if expected["reparse_tag"] != format_reparse_tag(LX_SYMLINK_REPARSE_TAG):
            raise ValueError(f"unsupported reparse-point tag declaration: {expected['reparse_tag']}")
        digest = expected["reparse_data_sha256"]
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest.lower()):
            raise ValueError(f"invalid reparse-point payload SHA-256: {source_relpath}")
        if source_relpath in entries:
            raise ValueError(f"duplicate reparse-point metadata entry: {source_relpath}")
        entries[source_relpath] = expected
    return entries


def iter_source_entries(source_root: Path):
    pending = [source_root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as scan:
            entries = sorted(scan, key=lambda entry: entry.name)
        for entry in entries:
            path = Path(entry.path)
            try:
                status = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise ValueError(f"cannot inspect archive entry: {path}: {exc}") from exc
            yield path, status
            if (
                not (getattr(status, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT)
                and entry.is_dir(follow_symlinks=False)
            ):
                pending.append(path)


def read_reparse_buffer(path: Path) -> bytes:
    if os.name != "nt":
        raise ValueError(f"cannot read Windows reparse metadata outside Windows: {path}")

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_file = kernel32.CreateFileW
    create_file.argtypes = [
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
    ]
    create_file.restype = ctypes.c_void_p
    handle = create_file(
        str(path),
        0,
        0x00000007,
        None,
        3,
        0x02200000,
        None,
    )
    invalid_handle = ctypes.c_void_p(-1).value
    if handle == invalid_handle:
        raise OSError(ctypes.get_last_error(), f"cannot open reparse point: {path}")
    try:
        buffer = ctypes.create_string_buffer(16 * 1024)
        returned = ctypes.c_uint32()
        ok = kernel32.DeviceIoControl(
            handle,
            0x000900A8,
            None,
            0,
            buffer,
            len(buffer),
            ctypes.byref(returned),
            None,
        )
        if not ok:
            raise OSError(ctypes.get_last_error(), f"cannot read reparse metadata: {path}")
        return buffer.raw[: returned.value]
    finally:
        kernel32.CloseHandle(handle)


def parse_reparse_buffer(buffer: bytes) -> tuple[int, bytes]:
    if len(buffer) < 8:
        raise ValueError("reparse metadata buffer is too short")
    tag, payload_size = struct.unpack_from("<IH", buffer)
    end = 8 + payload_size
    if end > len(buffer):
        raise ValueError("reparse metadata buffer is truncated")
    return tag, buffer[8:end]


def lx_symlink_metadata(
    path: Path,
    status: os.stat_result,
    expected: dict[str, str],
) -> dict[str, Any]:
    tag, payload = parse_reparse_buffer(read_reparse_buffer(path))
    source_relpath = path.relative_to(ROOT).as_posix()
    actual_tag = getattr(status, "st_reparse_tag", 0)
    if tag != actual_tag or tag != LX_SYMLINK_REPARSE_TAG:
        raise ValueError(f"unsupported or inconsistent reparse-point tag: {source_relpath}")
    if len(payload) < 4:
        raise ValueError(f"LX_SYMLINK metadata is too short: {source_relpath}")
    version = struct.unpack_from("<I", payload)[0]
    try:
        target = payload[4:].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"LX_SYMLINK target is not UTF-8: {source_relpath}") from exc
    payload_sha256 = hashlib.sha256(payload).hexdigest()
    if (
        expected["reparse_tag"] != format_reparse_tag(tag)
        or expected["reparse_data_sha256"] != payload_sha256
        or expected["target"] != target
    ):
        raise ValueError(f"reparse-point metadata differs from its approved declaration: {source_relpath}")
    return {
        "source_relpath": source_relpath,
        "reparse_tag": format_reparse_tag(tag),
        "reparse_data_size_bytes": len(payload),
        "reparse_data_sha256": payload_sha256,
        "lx_symlink_version": version,
        "target": target,
    }


def collect_records(source_paths: list[Path], candidate: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    expected_reparse_points = configured_reparse_points(candidate, source_paths)
    records: list[dict[str, Any]] = []
    reparse_records: list[dict[str, Any]] = []
    for source_root in source_paths:
        for file_path, status in iter_source_entries(source_root):
            relative = file_path.relative_to(ROOT).as_posix()
            if getattr(status, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT:
                expected = expected_reparse_points.pop(relative, None)
                if expected is None:
                    raise ValueError(f"refusing undeclared reparse-point archive entry: {file_path}")
                reparse_records.append(lx_symlink_metadata(file_path, status, expected))
                continue
            if not file_path.is_file():
                continue
            records.append(
                {
                    "source_relpath": relative,
                    "archive_relpath": relative,
                    "size_bytes": status.st_size,
                    "sha256": sha256(file_path),
                }
            )
    if expected_reparse_points:
        missing = ", ".join(sorted(expected_reparse_points))
        raise ValueError(f"declared reparse-point metadata was not found: {missing}")
    return records, reparse_records


def write_reparse_point_metadata(staging: Path, candidate: dict[str, Any], records: list[dict[str, Any]]) -> Path | None:
    if not records:
        return None
    path = staging / "REPARSE_POINTS.json"
    payload = {
        "schema_version": "1.0",
        "archive_id": candidate["id"],
        "handling": LX_SYMLINK_POLICY,
        "source_content_copied": False,
        "reparse_points": records,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return path


def write_archive_metadata(
    staging: Path,
    candidate: dict[str, Any],
    records: list[dict[str, Any]],
    reparse_records: list[dict[str, Any]],
    destination: Path,
) -> None:
    reparse_manifest = write_reparse_point_metadata(staging, candidate, reparse_records)
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
    if reparse_manifest is not None:
        manifest.update(
            {
                "reparse_point_policy": LX_SYMLINK_POLICY,
                "reparse_point_count": len(reparse_records),
                "reparse_point_manifest": reparse_manifest.name,
                "reparse_point_manifest_sha256": sha256(reparse_manifest),
            }
        )
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


def copy_and_verify(
    source_paths: list[Path],
    records: list[dict[str, Any]],
    reparse_records: list[dict[str, Any]],
    candidate: dict[str, Any],
    destination: Path,
) -> dict[str, Any]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    staging = destination.parent / f".{destination.name}.staging-{stamp}-{os.getpid()}"
    if staging.exists():
        raise ValueError(f"staging path already exists: {staging}")
    staging.mkdir()
    try:
        for source_root in source_paths:
            (staging / source_root.relative_to(ROOT)).mkdir(parents=True, exist_ok=True)
        for record in records:
            source = ROOT / record["source_relpath"]
            target = staging / record["archive_relpath"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
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
        write_archive_metadata(staging, candidate, records, reparse_records, destination)
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
        "reparse_point_count": len(reparse_records),
        "source_changed": False,
    }


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    try:
        candidate = load_candidate(manifest_path, args.candidate)
        source_paths = [repo_path(value) for value in candidate["paths"]]
        destination = external_destination(args.destination)
        records, reparse_records = collect_records(source_paths, candidate)
        summary = {
            "ok": True,
            "dry_run": not args.apply,
            "candidate": candidate["id"],
            "source_paths": candidate["paths"],
            "destination": str(destination),
            "file_count": len(records),
            "total_bytes": sum(record["size_bytes"] for record in records),
            "reparse_point_count": len(reparse_records),
            "source_changed": False,
        }
        if args.apply:
            summary = copy_and_verify(source_paths, records, reparse_records, candidate, destination)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
