#!/usr/bin/env python3
"""Verify a copy-only component payload without changing either source tree."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path
from typing import Iterable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--exclude-dir", action="append", default=[])
    parser.add_argument("--exclude-dir-relpath", action="append", default=[])
    parser.add_argument("--exclude-file-glob", action="append", default=[])
    parser.add_argument("--exclude-file-relpath", action="append", default=[])
    parser.add_argument("--allow-target-extra-relpath", action="append", default=[])
    parser.add_argument("--allow-target-excluded-relpath", action="append", default=[])
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_excluded_file(name: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(name, pattern) for pattern in patterns)


def inventory(
    root: Path,
    excluded_dirs: set[str],
    excluded_dir_relpaths: set[str],
    excluded_file_globs: list[str],
    excluded_file_relpaths: set[str],
) -> tuple[dict[str, str], list[str]]:
    entries: dict[str, str] = {}
    excluded_entries: list[str] = []

    for directory, directory_names, file_names in os.walk(root, followlinks=False):
        current = Path(directory)
        directory_names[:] = sorted(directory_names)
        retained_dirs: list[str] = []
        for name in directory_names:
            candidate = current / name
            relative = candidate.relative_to(root).as_posix()
            if name in excluded_dirs or relative in excluded_dir_relpaths:
                excluded_entries.append(relative + "/")
                continue
            if candidate.is_symlink():
                raise ValueError(f"symlinked_directory_not_supported:{relative}")
            retained_dirs.append(name)
        directory_names[:] = retained_dirs

        for name in sorted(file_names):
            candidate = current / name
            relative = candidate.relative_to(root).as_posix()
            if relative in excluded_file_relpaths or is_excluded_file(name, excluded_file_globs):
                excluded_entries.append(relative)
                continue
            if candidate.is_symlink():
                raise ValueError(f"symlinked_file_not_supported:{relative}")
            entries[relative] = sha256_file(candidate)

    return entries, sorted(excluded_entries)


def manifest_sha256(entries: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for relative, file_hash in sorted(entries.items()):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    target = args.target.resolve()
    errors: list[str] = []
    if not source.is_dir():
        errors.append(f"source_missing:{source}")
    if not target.is_dir():
        errors.append(f"target_missing:{target}")
    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        return 2

    try:
        source_entries, source_excluded = inventory(
            source,
            set(args.exclude_dir),
            set(args.exclude_dir_relpath),
            args.exclude_file_glob,
            set(args.exclude_file_relpath),
        )
        target_entries, target_excluded = inventory(
            target,
            set(args.exclude_dir),
            set(args.exclude_dir_relpath),
            args.exclude_file_glob,
            set(args.exclude_file_relpath),
        )
    except ValueError as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        return 2

    source_paths = set(source_entries)
    target_paths = set(target_entries)
    allowed_target_extras = set(args.allow_target_extra_relpath)
    allowed_target_excluded = set(args.allow_target_excluded_relpath)
    target_excluded_paths = {entry.rstrip("/") for entry in target_excluded}
    missing = sorted(source_paths - target_paths)
    extra = sorted(target_paths - source_paths - allowed_target_extras)
    missing_allowed_extras = sorted(allowed_target_extras - target_paths)
    unexpected_target_excluded = sorted(target_excluded_paths - allowed_target_excluded)
    missing_allowed_target_excluded = sorted(
        allowed_target_excluded - target_excluded_paths
    )
    changed = sorted(
        relative
        for relative in source_paths & target_paths
        if source_entries[relative] != target_entries[relative]
    )
    target_payload_entries = {
        relative: file_hash
        for relative, file_hash in target_entries.items()
        if relative not in allowed_target_extras
    }
    valid = (
        not missing
        and not extra
        and not missing_allowed_extras
        and not unexpected_target_excluded
        and not missing_allowed_target_excluded
        and not changed
    )
    payload = {
        "valid": valid,
        "source": str(source),
        "target": str(target),
        "excluded_dirs": sorted(set(args.exclude_dir)),
        "excluded_dir_relpaths": sorted(set(args.exclude_dir_relpath)),
        "excluded_file_globs": args.exclude_file_glob,
        "excluded_file_relpaths": sorted(set(args.exclude_file_relpath)),
        "allowed_target_extra_relpaths": sorted(allowed_target_extras),
        "allowed_target_excluded_relpaths": sorted(allowed_target_excluded),
        "source_file_count": len(source_entries),
        "target_payload_file_count": len(target_payload_entries),
        "target_metadata_file_count": len(target_entries) - len(target_payload_entries),
        "source_tree_sha256": manifest_sha256(source_entries),
        "target_tree_sha256": manifest_sha256(target_payload_entries),
        "source_excluded_entry_count": len(source_excluded),
        "target_excluded_entry_count": len(target_excluded),
        "unexpected_target_excluded_count": len(unexpected_target_excluded),
        "missing_allowed_target_excluded_count": len(missing_allowed_target_excluded),
        "missing_count": len(missing),
        "extra_count": len(extra),
        "missing_allowed_extra_count": len(missing_allowed_extras),
        "changed_count": len(changed),
        "missing_examples": missing[:20],
        "extra_examples": extra[:20],
        "missing_allowed_extra_examples": missing_allowed_extras[:20],
        "changed_examples": changed[:20],
        "target_excluded_examples": target_excluded[:20],
        "unexpected_target_excluded_examples": unexpected_target_excluded[:20],
        "missing_allowed_target_excluded_examples": missing_allowed_target_excluded[:20],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
