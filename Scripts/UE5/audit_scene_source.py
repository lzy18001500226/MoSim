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
DEFAULT_MAP_KEYS = ("GameDefaultMap", "EditorStartupMap", "ServerDefaultMap")


def empty_scan() -> dict[str, Any]:
    return {
        "files_seen": 0,
        "dirs_seen": 0,
        "scan_truncated": False,
        "umap_count": 0,
        "umap_samples": [],
        "umap_records": [],
        "uasset_count": 0,
        "uasset_samples": [],
        "uplugin_count": 0,
        "uplugin_samples": [],
        "explicit_truth_candidates": [],
        "ue_truth_proxy_candidates": [],
    }


def package_from_content_path(path: Path) -> str:
    parts = list(path.parts)
    if "Content" not in parts:
        return ""
    below_content = parts[parts.index("Content") + 1 :]
    if not below_content:
        return ""
    return "/Game/" + "/".join(Path(*below_content).with_suffix("").parts)


def normalize_map_package(value: str) -> str:
    value = value.strip().strip('"').strip("'")
    if not value.startswith("/Game/"):
        return ""
    package, _, asset_name = value.rpartition(".")
    if package and asset_name and package.rsplit("/", 1)[-1] == asset_name:
        return package
    return value


def read_default_map_packages(project_root: Path) -> dict[str, str]:
    config = project_root / "Config" / "DefaultEngine.ini"
    packages: dict[str, str] = {}
    if not config.exists():
        return packages
    try:
        lines = config.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError:
        return packages
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ";")) or "=" not in stripped:
            continue
        key, raw_value = stripped.split("=", 1)
        key = key.strip()
        if key not in DEFAULT_MAP_KEYS:
            continue
        package = normalize_map_package(raw_value)
        if package:
            packages[key] = package
    return packages


def map_file_from_package(project_root: Path, package: str) -> Path | None:
    if not package.startswith("/Game/"):
        return None
    candidate = project_root / "Content" / (package.removeprefix("/Game/") + ".umap")
    return candidate if candidate.exists() else None


def classify_umap(path: Path, default_map_packages: dict[str, str] | None = None) -> dict[str, Any]:
    """Classify a .umap as a likely review scene or a component map.

    Fab/sample projects often include hundreds of assembly maps.  For MoSim we
    need the playable/reviewable level first, not every PLBP/Asmbly asset.
    """
    lower_parts = [part.lower() for part in path.parts]
    stem = path.stem.lower()
    package = package_from_content_path(path)
    default_map_packages = default_map_packages or {}
    content_index = lower_parts.index("content") if "content" in lower_parts else -1
    below_content = lower_parts[content_index + 1 :] if content_index >= 0 else []
    immediate_parent = lower_parts[-2] if len(lower_parts) >= 2 else ""
    direct_content_map = len(below_content) == 1
    direct_maps_dir = immediate_parent in {"maps", "levels"}
    component_dir_parts = {
        "plbps",
        "asmbly",
        "assemblies",
        "previewer",
        "packed",
        "packedlevels",
        "mass",
    }
    score = 0
    tags: list[str] = []

    default_roles = [key for key, value in default_map_packages.items() if value == package]
    if "GameDefaultMap" in default_roles:
        score += 120
        tags.append("game_default_map")
    if "EditorStartupMap" in default_roles:
        score += 90
        tags.append("editor_startup_map")
    if "ServerDefaultMap" in default_roles:
        score += 20
        tags.append("server_default_map")

    if direct_content_map:
        score += 70
        tags.append("direct_content_map")
    if direct_maps_dir:
        score += 50
        tags.append("direct_maps_or_levels_dir")
    elif "levels" in lower_parts or "maps" in lower_parts:
        score += 40
        tags.append("level_or_maps_dir")
    if stem in {"main", "mainmap"}:
        score += 35
        tags.append("main_map")
    if "env" in stem or "environment" in stem:
        score += 25
        tags.append("environment")
    if "startup" in stem:
        score -= 35
        tags.append("startup")
    if "assetzoo" in stem or "asset_zoo" in stem:
        score -= 50
        tags.append("asset_zoo")
    if any(part in component_dir_parts for part in lower_parts):
        score -= 80
        tags.append("component_or_preview")
    if any(token in stem for token in ("floor", "door", "window", "module", "assembly", "asmbl")):
        score -= 20
        tags.append("asset_piece")

    if score >= 45:
        role = "primary_review_candidate"
    elif score >= 15:
        role = "secondary_review_candidate"
    elif "startup" in tags:
        role = "startup_or_bootstrap"
    elif "asset_zoo" in tags:
        role = "asset_zoo"
    else:
        role = "component_map"

    return {
        "path": rel(path),
        "package": package,
        "role": role,
        "score": score,
        "tags": tags,
    }


def append_sample(values: list[str], path: Path, sample_limit: int) -> None:
    if len(values) < sample_limit:
        values.append(rel(path))


def scan_project_umaps(project_root: Path, *, sample_limit: int = 12, record_limit: int = 600) -> dict[str, Any]:
    """Scan maps independently so large asset projects do not hide the main level.

    The bounded general scan is useful for quick readiness signals, but map
    selection is critical enough that it should not stop just because thousands
    of textures or meshes appear before the primary `.umap`.
    """
    result = {"umap_count": 0, "umap_samples": [], "umap_records": [], "umap_record_truncated": False}
    if not project_root.exists():
        return result
    default_map_packages = read_default_map_packages(project_root)
    seen: set[Path] = set()

    def add_map(path: Path) -> None:
        resolved = path.resolve()
        if resolved in seen:
            return
        seen.add(resolved)
        result["umap_count"] += 1
        append_sample(result["umap_samples"], path, sample_limit)
        if len(result["umap_records"]) < record_limit:
            result["umap_records"].append(classify_umap(path, default_map_packages))
        else:
            result["umap_record_truncated"] = True

    for package in default_map_packages.values():
        map_file = map_file_from_package(project_root, package)
        if map_file:
            add_map(map_file)

    content_root = project_root / "Content"
    priority_roots = [
        content_root,
        content_root / "Maps",
        content_root / "Levels",
    ]
    if content_root.exists():
        for child in content_root.iterdir():
            if child.is_dir() and child.name.lower() in {"maps", "levels"}:
                priority_roots.append(child)
            for nested_name in ("Maps", "Levels"):
                nested = child / nested_name
                if nested.is_dir():
                    priority_roots.append(nested)

    dirs_seen = 0
    for root in dict.fromkeys(priority_roots):
        if not root.exists():
            continue
        for current, dirs, files in os.walk(root):
            dirs[:] = [name for name in dirs if name not in IGNORED_DIRS]
            dirs_seen += 1
            if dirs_seen > 160:
                dirs[:] = []
                result["umap_record_truncated"] = True
                break
            if Path(current) == content_root:
                dirs[:] = [name for name in dirs if name.lower() in {"maps", "levels"}]
            if any(part.lower() in {"asmbly", "plbps", "previewer", "packed", "packedlevels", "mass"} for part in Path(current).parts):
                dirs[:] = []
                continue
            for filename in files:
                if not filename.lower().endswith(".umap"):
                    continue
                path = Path(current) / filename
                add_map(path)
        if result["umap_record_truncated"] and len(result["umap_records"]) >= record_limit:
            break
    return result


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
                if len(result["umap_records"]) < 240:
                    result["umap_records"].append(classify_umap(path))
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
    map_scan = scan_project_umaps(project_root)
    scan["umap_count"] = map_scan["umap_count"]
    scan["umap_samples"] = map_scan["umap_samples"]
    scan["umap_records"] = map_scan["umap_records"]
    if map_scan["umap_record_truncated"]:
        scan["scan_truncated"] = True
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
    recommended_maps = sorted(
        scan["umap_records"],
        key=lambda record: (int(record.get("score", 0)), str(record.get("path", ""))),
        reverse=True,
    )[:12]
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
        "recommended_review_maps": recommended_maps,
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
    parser.add_argument("--maps", action="store_true", help="Print ranked candidate review maps for each project.")
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
    elif args.maps:
        print(f"{'score':>5} {'role':<28} {'scene':<34} package")
        print("-" * 120)
        for row in rows:
            for record in row.get("recommended_review_maps", [])[:8]:
                print(
                    f"{int(record.get('score', 0)):>5} "
                    f"{str(record.get('role', '')):<28} "
                    f"{row['name']:<34} "
                    f"{record.get('package')}"
                )
                print(f"{'':>5} {'':<28} {'':<34} {record.get('path')}")
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
