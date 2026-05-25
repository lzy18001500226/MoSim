#!/usr/bin/env python3
"""Build and validate the MoSim Unreal scene-source registry.

The registry is the handoff contract between Epic/Fab/library inventory,
editable local Unreal projects, and the MoSim renderer/planner.  It prevents
confusing "asset is visible in Launcher" with "asset is imported, editable, and
has planning truth".
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
from pathlib import Path
from typing import Any

from audit_scene_source import DEFAULT_SCENE_ROOT, DEFAULT_TRUTH_ROOT, audit_scene_root
from epic_library_index import build_inventory
from epic_library_view import merge_library_view
from export_unreal_scene_truth import validate_truth_payload


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json"
RENDERER_CONTENT = ROOT / "UE5/MoSimSceneLibrary/Content"
SCHEMA = "mosim.unreal_scene_source_registry.v1"
FORBIDDEN_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:[\\/]", re.IGNORECASE),
    re.compile(r"/mnt/[a-z]/", re.IGNORECASE),
    re.compile(r"\bUsers[\\/]", re.IGNORECASE),
    re.compile(r"\bAppData\b", re.IGNORECASE),
    re.compile(r"\bProgramData\b", re.IGNORECASE),
)


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def rel_lexical(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def slug(value: str, fallback: str = "scene") -> str:
    text = re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_").lower()
    return text or fallback


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def trim_list(values: list[Any], limit: int = 12) -> list[Any]:
    return values[:limit]


def is_windows_absolute_path(value: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:[\\/]", value))


def project_local_paths(values: list[str], limit: int = 4) -> list[str]:
    paths: list[str] = []
    for value in values:
        if is_windows_absolute_path(str(value)):
            continue
        try:
            path = Path(str(value)).resolve()
        except Exception:
            continue
        try:
            path.relative_to(ROOT)
        except ValueError:
            continue
        paths.append(rel(path))
    return sorted(set(paths))[:limit]


def compact_library_entry(row: dict[str, Any]) -> dict[str, Any]:
    uproject_paths = [str(value) for value in row.get("uproject_paths", [])]
    local_cache_paths = [str(value) for value in row.get("local_cache_paths", [])]
    project_uproject_paths = project_local_paths(uproject_paths, 4)
    project_cache_paths = project_local_paths(local_cache_paths, 4)
    all_project_uproject_paths = project_local_paths(uproject_paths, 10_000)
    all_project_cache_paths = project_local_paths(local_cache_paths, 10_000)
    return {
        "display_name": row.get("display_name", ""),
        "states": sorted(set(row.get("states", []))),
        "versions": sorted(set(row.get("versions", []))),
        "installed_or_cached": bool(row.get("installed_or_cached")),
        "openable_project": bool(row.get("openable_project")),
        "project_local_uproject_paths": project_uproject_paths,
        "project_local_cache_paths": project_cache_paths,
        "external_uproject_path_count": len(uproject_paths) - len(all_project_uproject_paths),
        "external_cache_path_count": len(local_cache_paths) - len(all_project_cache_paths),
    }


def truth_artifacts(row: dict[str, Any]) -> list[str]:
    truth = row.get("truth", {})
    candidates = truth.get("explicit_truth_candidates", [])
    return sorted({str(path) for path in candidates if str(path).endswith(".json")})


def renderer_reuse_metadata(row: dict[str, Any]) -> dict[str, Any]:
    samples = [str(value) for value in row.get("umap_samples", [])]
    for sample in samples:
        parts = list(Path(sample).parts)
        if "Content" not in parts:
            continue
        content_index = parts.index("Content")
        below_content = parts[content_index + 1 :]
        if len(below_content) < 2:
            continue
        top_level = below_content[0]
        renderer_content_root = RENDERER_CONTENT / top_level
        renderer_map_asset = renderer_content_root.joinpath(*below_content[1:])
        renderer_map_package = "/Game/" + "/".join(Path(*below_content).with_suffix("").parts)
        imported = renderer_content_root.exists() and renderer_map_asset.exists()
        return {
            "imported_into_renderer": imported,
            "renderer_reuse_kind": "content_link" if renderer_content_root.is_symlink() else "content_copy" if imported else "",
            "renderer_content_root": rel_lexical(renderer_content_root) if imported else "",
            "renderer_map_asset": rel_lexical(renderer_map_asset) if imported else "",
            "renderer_map_package": renderer_map_package if imported else "",
        }
    return {
        "imported_into_renderer": False,
        "renderer_reuse_kind": "",
        "renderer_content_root": "",
        "renderer_map_asset": "",
        "renderer_map_package": "",
    }


def compact_scene_entry(row: dict[str, Any]) -> dict[str, Any]:
    scene_id = f"local_{slug(str(row.get('name', 'scene')))}"
    artifacts = truth_artifacts(row)
    ready = bool(row.get("editable_candidate") and row.get("renderable_candidate") and row.get("planning_truth_ready"))
    status = "accepted_local_truth_fallback" if ready else "needs_truth_extraction_or_proxy"
    if not row.get("editable_candidate") or not row.get("renderable_candidate"):
        status = "not_import_ready"
    entry = {
        "scene_source_id": scene_id,
        "source_kind": row.get("source_type", "local_unreal_project"),
        "name": row.get("name", ""),
        "status": status,
        "project_root": row.get("project_root", ""),
        "uproject_path": row.get("uproject_path", ""),
        "engine_association": row.get("engine_association", ""),
        "editable_candidate": bool(row.get("editable_candidate")),
        "renderable_candidate": bool(row.get("renderable_candidate")),
        "planning_truth_ready": bool(row.get("planning_truth_ready")),
        "truth_artifacts": artifacts,
        "umap_count": int(row.get("umap_count", 0)),
        "umap_samples": trim_list(row.get("umap_samples", []), 8),
        "uasset_count": int(row.get("uasset_count", 0)),
        "uasset_samples": trim_list(row.get("uasset_samples", []), 8),
        "uplugin_count": int(row.get("uplugin_count", 0)),
        "plugins": trim_list(sorted(set(row.get("plugins", []))), 20),
        "audit_verdict": row.get("verdict", ""),
        "truth_gap": row.get("truth", {}).get("truth_gap", ""),
    }
    entry.update(renderer_reuse_metadata(row))
    return entry


def selected_primary(local_sources: list[dict[str, Any]]) -> str:
    accepted = [source for source in local_sources if source["status"] == "accepted_local_truth_fallback"]
    if not accepted:
        return ""
    derelict = [source for source in accepted if "derelict" in source["scene_source_id"]]
    return (derelict or accepted)[0]["scene_source_id"]


def build_registry(
    *,
    scene_root: Path = DEFAULT_SCENE_ROOT,
    truth_root: Path = DEFAULT_TRUTH_ROOT,
    max_files: int = 1600,
    max_dirs: int = 320,
) -> dict[str, Any]:
    inventory = build_inventory()
    library_rows = [compact_library_entry(row) for row in merge_library_view()]
    audited_scenes = audit_scene_root(scene_root, max_files=max_files, max_dirs=max_dirs, truth_root=truth_root)
    local_sources = [compact_scene_entry(row) for row in audited_scenes]
    primary = selected_primary(local_sources)

    fab_rows = [
        row
        for row in library_rows
        if row["states"]
        and (
            "fab_cached" in row["states"]
            or "account_owned" in row["states"]
            or "vault_cached_project" in row["states"]
            or "vault_cached_asset" in row["states"]
        )
    ]

    return {
        "schema": SCHEMA,
        "generated_at": now_utc(),
        "policy": {
            "active_strategy": "local_editable_fallback_until_fab_import_truth_verified",
            "acceptance_gates": ["import_edit", "render", "planning_truth"],
            "primary_scene_source_id": primary,
        },
        "fab_route": {
            "status": "inventory_visible_not_scene_accepted",
            "reason": (
                "Epic/Fab/Launcher inventory is visible, but no Fab asset is yet proven "
                "to be imported into the MoSim UE project, editable through UE MCP, and "
                "paired with explicit planner truth."
            ),
            "library_summary": inventory.get("summary", {}),
            "candidate_entries": sorted(fab_rows, key=lambda item: item["display_name"].lower()),
        },
        "local_editable_fallback": {
            "status": "active" if primary else "blocked_no_truth_ready_scene",
            "scene_root": rel(scene_root),
            "truth_root": rel(truth_root),
            "scene_sources": sorted(local_sources, key=lambda item: item["name"].lower()),
        },
    }


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} JSON root must be an object")
    return data


def validate_truth_file(path: Path) -> list[str]:
    if not path.exists():
        return [f"truth file not found: {rel(path)}"]
    try:
        payload = load_json(path)
    except Exception as exc:
        return [f"truth file unreadable: {rel(path)}: {exc}"]
    return [f"{rel(path)}: {error}" for error in validate_truth_payload(payload)]


def collect_forbidden_paths(value: Any, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            hits.extend(collect_forbidden_paths(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            hits.extend(collect_forbidden_paths(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        if any(pattern.search(value) for pattern in FORBIDDEN_PATH_PATTERNS):
            hits.append(f"{path}: forbidden external/private path string")
    return hits


def validate_registry(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if registry.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    errors.extend(collect_forbidden_paths(registry))

    policy = registry.get("policy", {})
    if not isinstance(policy, dict):
        errors.append("policy must be an object")
        policy = {}
    primary = str(policy.get("primary_scene_source_id", ""))

    fab_route = registry.get("fab_route", {})
    if not isinstance(fab_route, dict):
        errors.append("fab_route must be an object")
        fab_route = {}
    if fab_route.get("status") == "accepted" and not primary:
        errors.append("fab_route cannot be accepted without a primary scene source")

    fallback = registry.get("local_editable_fallback", {})
    if not isinstance(fallback, dict):
        errors.append("local_editable_fallback must be an object")
        fallback = {}
    sources = fallback.get("scene_sources", [])
    if not isinstance(sources, list):
        errors.append("local_editable_fallback.scene_sources must be a list")
        sources = []
    if not sources:
        errors.append("local_editable_fallback.scene_sources must not be empty")

    source_ids = {str(source.get("scene_source_id", "")) for source in sources if isinstance(source, dict)}
    accepted = [source for source in sources if isinstance(source, dict) and source.get("status") == "accepted_local_truth_fallback"]
    if not accepted:
        errors.append("at least one local scene source must be accepted_local_truth_fallback")
    if primary and primary not in source_ids:
        errors.append(f"primary_scene_source_id not found in scene_sources: {primary}")
    if accepted and not primary:
        errors.append("primary_scene_source_id is required when a local fallback is accepted")

    for source in accepted:
        artifacts = source.get("truth_artifacts", [])
        if not artifacts:
            errors.append(f"{source.get('scene_source_id')}: accepted source requires truth_artifacts")
        for artifact in artifacts:
            errors.extend(validate_truth_file(ROOT / artifact))
        if source.get("imported_into_renderer"):
            for key in ["renderer_content_root", "renderer_map_asset", "renderer_map_package"]:
                if not source.get(key):
                    errors.append(f"{source.get('scene_source_id')}: imported source requires {key}")
            asset = source.get("renderer_map_asset")
            if asset and not (ROOT / str(asset)).exists():
                errors.append(f"{source.get('scene_source_id')}: renderer_map_asset not found: {asset}")
    return errors


def comparable_registry(registry: dict[str, Any]) -> dict[str, Any]:
    comparable = json.loads(json.dumps(registry, ensure_ascii=False))
    comparable.pop("generated_at", None)
    return comparable


def preserve_generated_at_if_unchanged(registry: dict[str, Any], output: Path) -> dict[str, Any]:
    if not output.exists():
        return registry
    try:
        existing = load_json(output)
    except Exception:
        return registry
    if comparable_registry(existing) == comparable_registry(registry):
        registry = dict(registry)
        registry["generated_at"] = existing.get("generated_at", registry["generated_at"])
    return registry


def print_summary(registry: dict[str, Any]) -> None:
    summary = registry.get("fab_route", {}).get("library_summary", {})
    fallback = registry.get("local_editable_fallback", {})
    sources = fallback.get("scene_sources", [])
    print(f"schema: {registry.get('schema')}")
    print(f"fab_status: {registry.get('fab_route', {}).get('status')}")
    print(f"library_summary: {json.dumps(summary, ensure_ascii=False, sort_keys=True)}")
    print(f"fallback_status: {fallback.get('status')}")
    print(f"primary_scene_source_id: {registry.get('policy', {}).get('primary_scene_source_id')}")
    for source in sources:
        print(
            f"- {source.get('scene_source_id')}: {source.get('status')} "
            f"maps={source.get('umap_count')} assets={source.get('uasset_count')} "
            f"truth={len(source.get('truth_artifacts', []))} imported={source.get('imported_into_renderer')}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-root", type=Path, default=DEFAULT_SCENE_ROOT)
    parser.add_argument("--truth-root", type=Path, default=DEFAULT_TRUTH_ROOT)
    parser.add_argument("--max-files", type=int, default=1600)
    parser.add_argument("--max-dirs", type=int, default=320)
    parser.add_argument("--write", type=Path, nargs="?", const=DEFAULT_OUTPUT)
    parser.add_argument("--validate", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.validate:
        registry = load_json(args.validate)
        errors = validate_registry(registry)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            return 1
        print(f"OK: {rel(args.validate)}")
        return 0

    registry = build_registry(
        scene_root=args.scene_root,
        truth_root=args.truth_root,
        max_files=args.max_files,
        max_dirs=args.max_dirs,
    )
    errors = validate_registry(registry)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if args.write:
        registry = preserve_generated_at_if_unchanged(registry, args.write)
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote {rel(args.write)}")
    elif args.json:
        print(json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_summary(registry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
