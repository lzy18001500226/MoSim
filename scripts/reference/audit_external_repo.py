#!/usr/bin/env python3
"""Audit an imported reference repository for reuse risk.

The scanner is intentionally shallow and deterministic. It does not decide
whether a repository is good; it collects the facts needed for a reviewer to
make that decision.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXCLUDES = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "Binaries",
    "Intermediate",
    "Saved",
    "DerivedDataCache",
    "__pycache__",
    "BUILD",
    "build",
    "dist",
}
KEY_EXTENSIONS = {
    ".uproject",
    ".umap",
    ".uasset",
    ".uplugin",
    ".cpp",
    ".h",
    ".hpp",
    ".py",
    ".m",
    ".jl",
    ".md",
    ".rst",
    ".xml",
    ".yaml",
    ".yml",
    ".json",
    ".stl",
    ".obj",
    ".fbx",
    ".urdf",
    ".sdf",
    ".launch",
}
RUNTIME_EXTENSIONS = {
    ".dll",
    ".exe",
    ".lib",
    ".pdb",
    ".pak",
    ".msr",
    ".zip",
    ".7z",
    ".rar",
    ".iso",
}


def project_path(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise SystemExit(f"path must be inside project root: {resolved}") from exc
    return resolved


def iter_files(base: Path, max_files: int) -> Iterable[Path]:
    count = 0
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in DEFAULT_EXCLUDES]
        for filename in filenames:
            path = Path(dirpath) / filename
            yield path
            count += 1
            if count >= max_files:
                return


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def first_existing(base: Path, names: Iterable[str], limit: int = 12) -> list[str]:
    found: list[str] = []
    lowered = {name.lower() for name in names}
    for path in iter_files(base, 20_000):
        if path.name.lower() in lowered:
            found.append(rel(path))
            if len(found) >= limit:
                break
    return found


def audit(base: Path, max_files: int) -> dict:
    files = list(iter_files(base, max_files))
    total_size = 0
    ext_counts: dict[str, int] = {}
    large_files: list[dict] = []
    key_files: dict[str, list[str]] = {
        "unreal_projects": [],
        "unreal_maps": [],
        "unreal_assets": [],
        "unreal_plugins": [],
        "source": [],
        "docs": [],
        "robot_models": [],
        "runtime_binary": [],
    }

    for path in files:
        try:
            size = path.stat().st_size
        except OSError:
            continue
        total_size += size
        ext = path.suffix.lower() or "<none>"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        if size >= 50 * 1024 * 1024:
            large_files.append({"path": rel(path), "size_mb": round(size / 1024 / 1024, 2)})
        if ext == ".uproject":
            key_files["unreal_projects"].append(rel(path))
        elif ext == ".umap":
            key_files["unreal_maps"].append(rel(path))
        elif ext == ".uasset":
            key_files["unreal_assets"].append(rel(path))
        elif ext == ".uplugin":
            key_files["unreal_plugins"].append(rel(path))
        elif ext in {".cpp", ".h", ".hpp", ".cs"}:
            key_files["source"].append(rel(path))
        elif ext in {".md", ".rst", ".pdf"}:
            key_files["docs"].append(rel(path))
        elif ext in {".urdf", ".sdf", ".xacro"}:
            key_files["robot_models"].append(rel(path))
        elif ext in RUNTIME_EXTENSIONS:
            key_files["runtime_binary"].append(rel(path))

    for paths in key_files.values():
        del paths[25:]

    editable_unreal = bool(
        key_files["unreal_projects"]
        and (key_files["unreal_maps"] or key_files["unreal_assets"])
    )
    source_available = bool(key_files["source"])
    runtime_only_risk = bool(key_files["runtime_binary"]) and not source_available

    return {
        "repo_path": rel(base),
        "scanned_files": len(files),
        "total_size_mb_sample": round(total_size / 1024 / 1024, 2),
        "extension_counts_top": sorted(ext_counts.items(), key=lambda kv: kv[1], reverse=True)[:30],
        "metadata_files": first_existing(
            base,
            ["README.md", "README.rst", "LICENSE", "LICENSE.md", "CMakeLists.txt", "package.xml", "pyproject.toml", "package.json"],
        ),
        "key_files": key_files,
        "large_files_50mb_plus": large_files[:80],
        "signals": {
            "editable_unreal_assets": editable_unreal,
            "source_available": source_available,
            "runtime_only_risk": runtime_only_risk,
            "has_files_over_github_hard_limit": any(item["size_mb"] > 100 for item in large_files),
        },
        "recommended_review": [
            "Open README/LICENSE before reuse.",
            "Prefer .uproject/.umap/.uasset plus plugin Source for UE migration.",
            "Ignore runtime/build outputs unless explicitly needed for local execution.",
            "Do not stage files over GitHub's 100 MB hard limit.",
        ],
    }


def write_markdown(data: dict, path: Path) -> None:
    lines = [
        f"# External Repo Audit: `{data['repo_path']}`",
        "",
        "## Summary",
        "",
        f"- Scanned files: {data['scanned_files']}",
        f"- Sample size: {data['total_size_mb_sample']} MB",
    ]
    for key, value in data["signals"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Metadata Files", ""])
    lines.extend(f"- `{item}`" for item in data["metadata_files"] or ["none found"])
    lines.extend(["", "## Key Files", ""])
    for group, paths in data["key_files"].items():
        lines.append(f"### {group}")
        lines.extend(f"- `{item}`" for item in paths[:25] or ["none found"])
        lines.append("")
    lines.extend(["## Large Files >= 50 MB", ""])
    for item in data["large_files_50mb_plus"] or [{"path": "none found", "size_mb": 0}]:
        lines.append(f"- `{item['path']}`: {item['size_mb']} MB")
    lines.extend(["", "## Recommended Review", ""])
    lines.extend(f"- {item}" for item in data["recommended_review"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--max-files", type=int, default=50_000)
    args = parser.parse_args()

    base = project_path(args.path)
    data = audit(base, args.max_files)
    if args.output:
        out = project_path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    if args.markdown:
        write_markdown(data, project_path(args.markdown))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
