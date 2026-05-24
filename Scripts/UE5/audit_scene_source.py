#!/usr/bin/env python3
"""Audit UE scene sources for MoSim import, rendering, and planning truth."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENE_ROOT = ROOT / "References" / "UnrealScenes"
DEFAULT_TRUTH_ROOT = ROOT / "UE5/MworksUnrealRenderer/Content/MworksData/scene_truth"
IGNORED_DIRS = {".git", ".svn", ".hg", ".vs", "Binaries", "DerivedDataCache", "Intermediate", "Saved"}
EXPLICIT_TRUTH_SUFFIXES = {".json", ".csv", ".yaml", ".yml", ".pcd", ".ply", ".las", ".laz", ".bin"}
TRUTH_MARKERS = (
    "truth",
    "collision",
    "occupancy",
    "semantic",
    "semantics",
    "navmesh",
    "navigation",
    "sdf",
    "pointcloud",
    "point_cloud",
    "lidar",
    "voxel",
)


def empty_scan() -> dict[str, Any]:
    return {
        "files_seen": 0,
        "dirs_seen": 0,
        "scan_truncated": False,
        "umap_count": 0,
        "umap_samples": [],
        "uasset_count": 0,
        "uasset_samples": [],
        "uplugin_count": 0,
        "uplugin_samples": [],
        "explicit_truth_candidates": [],
        "ue_truth_proxy_candidates": [],
    }


def append_sample(values: list[str], path: Path, sample_limit: int) -> None:
    if len(values) < sample_limit:
        values.append(rel(path))


def scan_project_files(
    project_root: Path,
    *,
    max_files: int = 1600,
    max_dirs: int = 320,
    sample_limit: int = 12,
) -> dict[str, Any]:
    """Scan a UE project once and collect import/render/truth indicators.

    UE sample projects can contain tens of thousands of files. The audit only
    needs a bounded readiness signal, so this intentionally stops early and
    reports scan_truncated instead of repeatedly traversing the same tree.
    """
    result = empty_scan()
    if not project_root.exists():
        return result

    for current, dirs, files in os.walk(project_root):
        dirs[:] = [name for name in dirs if name not in IGNORED_DIRS]
        result["dirs_seen"] += 1
        if result["dirs_seen"] >= max_dirs:
            dirs[:] = []
            result["scan_truncated"] = True

        for filename in files:
            result["files_seen"] += 1
            path = Path(current) / filename
            lower = filename.lower()
            suffix = path.suffix.lower()

            if suffix == ".umap":
                result["umap_count"] += 1
                append_sample(result["umap_samples"], path, sample_limit)
            elif suffix == ".uasset":
                result["uasset_count"] += 1
                append_sample(result["uasset_samples"], path, sample_limit)
            elif suffix == ".uplugin":
                result["uplugin_count"] += 1
                append_sample(result["uplugin_samples"], path, sample_limit)

            if any(marker in lower for marker in TRUTH_MARKERS):
                if suffix in EXPLICIT_TRUTH_SUFFIXES:
                    append_sample(result["explicit_truth_candidates"], path, 40)
                elif suffix in {".uasset", ".umap"}:
                    append_sample(result["ue_truth_proxy_candidates"], path, 40)

            if result["files_seen"] >= max_files:
                result["scan_truncated"] = True
                return result
    return result


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_uproject(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        return {"_read_error": str(exc)}
    return data if isinstance(data, dict) else {"_read_error": "JSON root is not an object"}


def truth_state(scan: dict[str, Any]) -> dict[str, Any]:
    explicit_candidates = sorted(set(scan["explicit_truth_candidates"]))
    ue_proxy_candidates = sorted(set(scan["ue_truth_proxy_candidates"]))
    return {
        "has_explicit_truth_source": bool(explicit_candidates),
        "has_ue_truth_proxy_candidates": bool(ue_proxy_candidates),
        "explicit_truth_candidates": explicit_candidates[:40],
        "ue_truth_proxy_candidates": ue_proxy_candidates[:40],
        "truth_gap": ""
        if explicit_candidates
        else "No explicit planner/collision truth file found; generate occupancy/collision truth from UE assets before planning validation.",
    }


def explicit_scene_truth_files(project_name: str, truth_root: Path = DEFAULT_TRUTH_ROOT) -> list[str]:
    if not truth_root.exists():
        return []
    project_slug = project_name.lower().replace(" ", "_")
    candidates: list[str] = []
    for path in sorted(truth_root.glob("*.json")):
        name = path.name.lower()
        if project_slug in name or name.startswith(project_slug.split("_")[0]):
            candidates.append(rel(path))
    return candidates


def audit_project(
    uproject: Path,
    *,
    max_files: int = 1600,
    max_dirs: int = 320,
    truth_root: Path = DEFAULT_TRUTH_ROOT,
) -> dict[str, Any]:
    project_root = uproject.parent
    data = read_uproject(uproject)
    scan = scan_project_files(project_root, max_files=max_files, max_dirs=max_dirs)
    plugins = [
        plugin.get("Name")
        for plugin in data.get("Plugins", [])
        if isinstance(plugin, dict) and plugin.get("Name")
    ]
    truth = truth_state(scan)
    exported_truth = explicit_scene_truth_files(project_root.name, truth_root)
    if exported_truth:
        truth["has_explicit_truth_source"] = True
        truth["explicit_truth_candidates"] = sorted(set(truth["explicit_truth_candidates"] + exported_truth))[:40]
        truth["truth_gap"] = ""
    editable = uproject.exists() and (project_root / "Content").exists() and scan["uasset_count"] > 0
    renderable_candidate = editable and scan["umap_count"] > 0
    planning_ready = truth["has_explicit_truth_source"]
    return {
        "source_type": "local_unreal_project",
        "name": project_root.name,
        "project_root": rel(project_root),
        "uproject_path": rel(uproject),
        "engine_association": data.get("EngineAssociation", ""),
        "plugins": plugins,
        "files_seen": scan["files_seen"],
        "dirs_seen": scan["dirs_seen"],
        "scan_truncated": scan["scan_truncated"],
        "uplugin_count": scan["uplugin_count"],
        "uplugin_samples": scan["uplugin_samples"],
        "umap_count": scan["umap_count"],
        "umap_samples": scan["umap_samples"],
        "uasset_count": scan["uasset_count"],
        "uasset_samples": scan["uasset_samples"],
        "editable_candidate": editable,
        "renderable_candidate": renderable_candidate,
        "planning_truth_ready": planning_ready,
        "truth": truth,
        "verdict": (
            "ready_for_truth_backed_planning"
            if editable and renderable_candidate and planning_ready
            else "needs_truth_extraction_or_proxy"
            if editable and renderable_candidate
            else "not_import_ready"
        ),
    }


def find_uprojects(scene_root: Path, max_depth: int = 4) -> list[Path]:
    scene_root = scene_root.resolve()
    projects: list[Path] = []
    if not scene_root.exists():
        return projects
    root_parts = len(scene_root.parts)
    for current, dirs, files in os.walk(scene_root):
        current_path = Path(current)
        depth = len(current_path.parts) - root_parts
        dirs[:] = [name for name in dirs if name not in IGNORED_DIRS]
        if depth >= max_depth:
            dirs[:] = []
        for filename in files:
            if filename.endswith(".uproject"):
                projects.append(current_path / filename)
    return sorted(projects)


def audit_scene_root(
    scene_root: Path = DEFAULT_SCENE_ROOT,
    *,
    max_files: int = 1600,
    max_dirs: int = 320,
    truth_root: Path = DEFAULT_TRUTH_ROOT,
) -> list[dict[str, Any]]:
    return [
        audit_project(path, max_files=max_files, max_dirs=max_dirs, truth_root=truth_root)
        for path in find_uprojects(scene_root)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-root", type=Path, default=DEFAULT_SCENE_ROOT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--max-files", type=int, default=1600)
    parser.add_argument("--max-dirs", type=int, default=320)
    parser.add_argument("--truth-root", type=Path, default=DEFAULT_TRUTH_ROOT)
    args = parser.parse_args(argv)
    rows = audit_scene_root(
        args.scene_root,
        max_files=args.max_files,
        max_dirs=args.max_dirs,
        truth_root=args.truth_root,
    )
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"{'verdict':<32} {'maps':<5} {'assets':<7} {'truth':<5} {'trunc':<5} name")
        print("-" * 104)
        for row in rows:
            print(
                f"{row['verdict']:<32} {row['umap_count']:<5} "
                f"{row['uasset_count']:<7} {str(row['planning_truth_ready']):<5} "
                f"{str(row['scan_truncated']):<5} {row['name']}"
            )
            if row["truth"]["truth_gap"]:
                print(f"{'':<32} {'':<5} {'':<7} {'':<5} {'':<5} {row['truth']['truth_gap']}")
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
