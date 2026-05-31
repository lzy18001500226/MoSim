#!/usr/bin/env python3
"""MoSim live Unreal Editor MCP server.

This MCP owns the live Unreal Editor automation boundary: project context,
editor listener health, and future AssetRegistry/actor/viewport/truth-export
operations. Epic/Fab/Launcher inventory stays in mosim-epic.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[5]
SCRIPTS_UE5 = ROOT / "Scripts" / "UE5"
if str(SCRIPTS_UE5) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_UE5))

from audit_scene_source import audit_project, find_uprojects
from plan_scene_truth_export import plan_exports
from probe_unreal_editor_mcp_tools import (
    default_host as live_editor_default_host,
    run_probe as run_reversible_actor_probe,
    unique_actor_name_from_user_value,
)
from probe_unreal_mcp_listener import default_hosts, probe


RENDERER = ROOT / "UE5" / "MoSimSceneLibrary"
UPROJECT = RENDERER / "MoSimSceneLibrary.uproject"
DEFAULT_ENGINE = RENDERER / "Config" / "DefaultEngine.ini"
CONTENT_ROOT = RENDERER / "Content"
SAVED_LOGS = RENDERER / "Saved" / "Logs"
SCENE_ROOT = ROOT / "References" / "UnrealScenes"
TRUTH_ROOT = RENDERER / "Content" / "MworksData" / "scene_truth"
BRIDGE_PLUGIN = ROOT / "UE5" / "Bridge" / "QuadrotorMworksBridge.uplugin"
MCP_PROJECT = ROOT / "Docs" / "Skills" / "Unreal" / "mosim-unreal"
LEGACY_FLOPPERAM_WRAPPER = MCP_PROJECT / "wrappers" / "legacy_flopperam_wsl.sh"
THIS_WRAPPER = MCP_PROJECT / "wrappers" / "mosim-unreal.sh"
ASSET_SUFFIXES = {".uasset", ".umap"}
IGNORED_SCAN_DIRS = {"Binaries", "DerivedDataCache", "Intermediate", "Saved", ".git", ".svn", ".hg"}

TOOLSET = [
    "ue_health",
    "project_context",
    "editor_listener_health",
    "asset_search",
    "list_maps",
    "current_level_summary",
    "find_level_actors",
    "reversible_actor_probe",
    "scene_source_status",
    "scene_truth_export_plan",
    "editor_log_summary",
    "tool_boundary",
]

BUFFER_SIZE = 8192
REDACTION_PATTERNS = (
    (re.compile(r"UserID=[^&\\s]+", re.IGNORECASE), "UserID=<redacted>"),
    (re.compile(r"SessionID=[^&\\s]+", re.IGNORECASE), "SessionID=<redacted>"),
    (re.compile(r"EpicAccountId[:=][A-Za-z0-9|._-]+", re.IGNORECASE), "EpicAccountId=<redacted>"),
    (re.compile(r"LoginId[:=][A-Za-z0-9|._-]+", re.IGNORECASE), "LoginId=<redacted>"),
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


def redact_text(text: str) -> str:
    redacted = text
    for pattern, replacement in REDACTION_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def clamp_int(value: int, *, minimum: int, maximum: int) -> int:
    try:
        integer = int(value)
    except (TypeError, ValueError):
        integer = minimum
    return max(minimum, min(maximum, integer))


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{rel(path)} JSON root is not an object")
    return payload


def parse_ini_section_keys(path: Path) -> dict[str, dict[str, str]]:
    sections: dict[str, dict[str, str]] = {}
    current = ""
    if not path.exists():
        return sections
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith(";") or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            sections.setdefault(current, {})
            continue
        if current and "=" in line:
            key, value = line.split("=", 1)
            sections[current][key.strip()] = value.strip()
    return sections


def package_from_content_path(path: Path, content_root: Path = CONTENT_ROOT) -> str:
    try:
        relative = path.relative_to(content_root)
    except ValueError:
        return ""
    return "/Game/" + relative.with_suffix("").as_posix()


def normalize_map_package(value: str) -> str:
    value = value.strip().strip('"').strip("'")
    if not value.startswith("/Game/"):
        return ""
    package, _, asset_name = value.rpartition(".")
    if package and asset_name and package.rsplit("/", 1)[-1] == asset_name:
        return package
    return value


def query_tokens(query: str) -> list[str]:
    raw = query.strip()
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", raw)
    tokens = [token.lower() for token in re.split(r"[^A-Za-z0-9]+", spaced) if len(token) >= 3]
    compounds = {
        "forklift": ("fork", "lift"),
        "collision": ("collision",),
        "demonstration": ("demonstration",),
        "derelictcorridor": ("derelict", "corridor"),
    }
    expanded: list[str] = []
    for token in tokens:
        expanded.append(token)
        for compound, parts in compounds.items():
            if compound in token and token != compound:
                expanded.extend(parts)
    deduped: list[str] = []
    for token in expanded:
        if token not in deduped:
            deduped.append(token)
    return deduped


def preferred_asset_roots(
    root: Path,
    suffixes: set[str] | None,
    query_lower: str = "",
    query: str = "",
) -> list[Path]:
    common_roots = [
        "Maps",
        "Levels",
        "Meshes",
        "Blueprints",
        "Materials",
        "Textures",
        "Fx",
        "Audio",
        "Sequences",
        "DerelictCorridor",
    ]
    priority: list[Path] = []
    if suffixes != {".umap"}:
        tokens = query_tokens(query or query_lower)
        if root.exists() and tokens:
            for child in sorted(root.iterdir(), key=lambda item: item.name.lower()):
                if not child.is_dir() or child.name in IGNORED_SCAN_DIRS:
                    continue
                child_name = child.name.lower()
                if any(token in child_name or child_name in token for token in tokens):
                    priority.append(child)
                for current, dirs, _files in os.walk(child, followlinks=True):
                    dirs[:] = [name for name in dirs if name not in IGNORED_SCAN_DIRS]
                    current_path = Path(current)
                    depth = len(current_path.parts) - len(child.parts)
                    if depth >= 2:
                        dirs[:] = []
                    for name in list(dirs):
                        lower = name.lower()
                        if any(token in lower or lower in token for token in tokens):
                            priority.append(current_path / name)
        for name in common_roots:
            candidate = root / name
            if candidate.exists():
                priority.append(candidate)
        priority.append(root)
        return dedupe_paths(priority)

    for candidate in (root / "Maps", root / "Levels"):
        if candidate.exists():
            priority.append(candidate)
    if root.exists():
        for child in sorted(root.iterdir(), key=lambda item: item.name.lower()):
            if not child.is_dir() or child.name in IGNORED_SCAN_DIRS:
                continue
            for nested_name in ("Maps", "Levels"):
                nested = child / nested_name
                if nested.exists():
                    priority.append(nested)
    priority.append(root)
    return dedupe_paths(priority)


def dedupe_paths(paths: list[Path]) -> list[Path]:
    deduped: list[Path] = []
    seen: set[str] = set()
    for candidate in paths:
        key = candidate.as_posix().lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(candidate)
    return deduped


def walk_unreal_assets(
    root: Path,
    *,
    limit: int = 100,
    scan_limit: int = 5000,
    suffixes: set[str] | None = None,
    query_lower: str = "",
    query: str = "",
) -> tuple[list[Path], bool]:
    if not root.exists():
        return [], False
    results: list[Path] = []
    truncated = False
    seen_dirs: set[Path] = set()
    seen_files: set[Path] = set()
    suffixes = suffixes or ASSET_SUFFIXES
    assets_seen = 0
    for scan_root in preferred_asset_roots(root, suffixes, query_lower, query):
        for current, dirs, files in os.walk(scan_root, followlinks=True):
            try:
                current_real = Path(current).resolve()
            except OSError:
                current_real = Path(current)
            if current_real in seen_dirs:
                dirs[:] = []
                continue
            seen_dirs.add(current_real)
            filtered_dirs: list[str] = []
            for name in dirs:
                if name in IGNORED_SCAN_DIRS:
                    continue
                child = Path(current) / name
                try:
                    child_real = child.resolve()
                except OSError:
                    child_real = child
                if child_real in seen_dirs:
                    continue
                filtered_dirs.append(name)
            dirs[:] = sorted(filtered_dirs, key=lambda name: asset_dir_priority(name, query or query_lower))
            for filename in sorted(files):
                path = Path(current) / filename
                if path.suffix.lower() not in suffixes:
                    continue
                assets_seen += 1
                if assets_seen > scan_limit:
                    truncated = True
                    return results, truncated
                try:
                    file_real = path.resolve()
                except OSError:
                    file_real = path
                if file_real in seen_files:
                    continue
                seen_files.add(file_real)
                if query_lower and query_lower not in asset_search_haystack(path):
                    continue
                results.append(path)
                if exact_asset_query_match(path, query):
                    return results, truncated
                if len(results) >= limit:
                    truncated = True
                    return results, truncated
    return results, truncated


def asset_dir_priority(name: str, query_lower: str) -> tuple[int, str]:
    lower = name.lower()
    tokens = query_tokens(query_lower)
    if tokens and any(token in lower or lower in token for token in tokens):
        return (0, lower)
    preferred = {
        "maps": 1,
        "levels": 1,
        "meshes": 2,
        "blueprints": 3,
        "materials": 4,
        "textures": 5,
        "fx": 6,
        "audio": 7,
        "sequences": 8,
        "derelictcorridor": 9,
    }
    return (preferred.get(lower, 20), lower)


def asset_search_haystack(path: Path) -> str:
    asset_class = "World" if path.suffix.lower() == ".umap" else "UnknownAsset"
    return " ".join(
        [
            path.stem,
            rel_lexical(path),
            package_from_content_path(path),
            asset_class,
        ]
    ).lower()


def normalized_asset_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def exact_asset_query_match(path: Path, query: str) -> bool:
    if not query:
        return False
    query_name = normalized_asset_name(Path(query).stem)
    return bool(query_name and query_name == normalized_asset_name(path.stem))


def asset_record(path: Path) -> dict[str, Any]:
    package = package_from_content_path(path)
    asset_class = "World" if path.suffix.lower() == ".umap" else "UnknownAsset"
    return {
        "name": path.stem,
        "path": rel_lexical(path),
        "package": package,
        "asset_class": asset_class,
        "suffix": path.suffix.lower(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
    }


def asset_search_payload(
    query: str = "",
    suffix: str = "",
    limit: int = 100,
    scan_limit: int = 5000,
) -> dict[str, Any]:
    requested_limit = limit
    requested_scan_limit = scan_limit
    limit = clamp_int(limit, minimum=1, maximum=500)
    scan_limit = clamp_int(scan_limit, minimum=100, maximum=10000)
    query_lower = query.lower().strip()
    suffix_lower = suffix.lower().strip()
    if suffix_lower and not suffix_lower.startswith("."):
        suffix_lower = f".{suffix_lower}"
    requested_suffixes = {suffix_lower} if suffix_lower else None
    files, truncated = walk_unreal_assets(
        CONTENT_ROOT,
        limit=limit,
        scan_limit=scan_limit,
        suffixes=requested_suffixes,
        query_lower=query_lower,
        query=query,
    )
    matches: list[dict[str, Any]] = []
    for path in files:
        record = asset_record(path)
        if suffix_lower and record["suffix"] != suffix_lower:
            continue
        matches.append(record)
        if len(matches) >= limit:
            break
    return {
        "schema": "mosim.unreal_mcp.asset_search.v1",
        "content_root": rel(CONTENT_ROOT),
        "query": query,
        "suffix": suffix_lower,
        "requested_limit": requested_limit,
        "effective_limit": limit,
        "requested_scan_limit": requested_scan_limit,
        "scan_limit": scan_limit,
        "scan_truncated": truncated,
        "returned": len(matches),
        "assets": matches,
    }


def configured_map_packages() -> dict[str, str]:
    sections = parse_ini_section_keys(DEFAULT_ENGINE)
    maps = sections.get("/Script/EngineSettings.GameMapsSettings", {})
    return {
        key: normalize_map_package(value)
        for key, value in maps.items()
        if key.endswith("Map") and normalize_map_package(value)
    }


def list_maps_payload(query: str = "", limit: int = 100, scan_limit: int = 5000) -> dict[str, Any]:
    requested_limit = limit
    limit = clamp_int(limit, minimum=1, maximum=500)
    configured = configured_map_packages()
    payload = asset_search_payload(query=query, suffix=".umap", limit=limit, scan_limit=scan_limit)
    configured_values = set(configured.values())
    maps: list[dict[str, Any]] = []
    for record in payload["assets"]:
        package = str(record.get("package", ""))
        roles = [key for key, value in configured.items() if value == package]
        record = dict(record)
        record["configured_roles"] = roles
        record["is_configured_default"] = package in configured_values
        maps.append(record)
    maps.sort(key=lambda item: (not item["is_configured_default"], item["path"]))
    return {
        "schema": "mosim.unreal_mcp.list_maps.v1",
        "renderer_project": rel(UPROJECT),
        "configured_maps": configured,
        "requested_limit": requested_limit,
        "effective_limit": limit,
        "scan_truncated": payload["scan_truncated"],
        "returned": len(maps),
        "maps": maps,
    }


def windows_unreal_installs() -> list[dict[str, str]]:
    roots = [
        Path("/mnt/d/Program Files/Epic Games"),
        Path("/mnt/c/Program Files/Epic Games"),
    ]
    installs: list[dict[str, str]] = []
    for root in roots:
        if not root.exists():
            continue
        for candidate in sorted(root.glob("UE_*")):
            binary_dir = candidate / "Engine" / "Binaries" / "Win64"
            editor = binary_dir / "UnrealEditor.exe"
            if not editor.exists():
                editor = binary_dir / "UE4Editor.exe"
            if editor.exists():
                installs.append({"version_dir": candidate.name, "editor": rel(editor)})
    return installs


def project_context_payload() -> dict[str, Any]:
    uproject = read_json(UPROJECT) if UPROJECT.exists() else {}
    engine_sections = parse_ini_section_keys(DEFAULT_ENGINE)
    plugins = uproject.get("Plugins", []) if isinstance(uproject, dict) else []
    plugin_names = [
        str(item.get("Name"))
        for item in plugins
        if isinstance(item, dict) and item.get("Name")
    ]
    maps = engine_sections.get("/Script/EngineSettings.GameMapsSettings", {})
    return {
        "schema": "mosim.unreal_mcp.project_context.v1",
        "root": rel(ROOT),
        "renderer_project": rel(UPROJECT),
        "renderer_exists": UPROJECT.exists(),
        "bridge_plugin": rel(BRIDGE_PLUGIN),
        "bridge_plugin_exists": BRIDGE_PLUGIN.exists(),
        "engine_association": uproject.get("EngineAssociation", ""),
        "additional_plugin_directories": uproject.get("AdditionalPluginDirectories", []),
        "enabled_plugins": plugin_names,
        "game_default_map": maps.get("GameDefaultMap", ""),
        "editor_startup_map": maps.get("EditorStartupMap", ""),
        "local_unreal_installs": windows_unreal_installs(),
        "content_root": rel(CONTENT_ROOT),
        "content_root_exists": CONTENT_ROOT.exists(),
        "saved_logs": rel(SAVED_LOGS),
        "saved_logs_exists": SAVED_LOGS.exists(),
    }


def editor_listener_health_payload(
    timeout: float = 1.0,
    host: str | None = None,
    port: int = 55557,
) -> dict[str, Any]:
    hosts = default_hosts(host)
    results = [probe(candidate, port, timeout) for candidate in hosts]
    return {
        "schema": "mosim.unreal_mcp.editor_listener_health.v1",
        "ok": any(result.ok for result in results),
        "port": port,
        "hosts": [
            {
                "host": result.host,
                "ok": result.ok,
                "error": result.error,
            }
            for result in results
        ],
    }


def receive_unreal_json(sock: socket.socket, timeout_seconds: float) -> dict[str, Any]:
    sock.settimeout(timeout_seconds)
    chunks: list[bytes] = []
    deadline = time.monotonic() + timeout_seconds
    while True:
        if time.monotonic() > deadline:
            raise TimeoutError("Timed out waiting for complete JSON response from Unreal")
        chunk = sock.recv(BUFFER_SIZE)
        if not chunk:
            if not chunks:
                raise ConnectionError("Unreal closed the socket before returning data")
            break
        chunks.append(chunk)
        data = b"".join(chunks)
        try:
            return json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return json.loads(b"".join(chunks).decode("utf-8"))


def send_unreal_command(
    command: str,
    params: dict[str, Any] | None = None,
    *,
    host: str | None = None,
    port: int = 55557,
    timeout: float = 10.0,
) -> dict[str, Any]:
    hosts = default_hosts(host)
    if not hosts:
        raise RuntimeError("No Unreal host candidate found. Set host or UNREAL_HOST.")
    errors: list[str] = []
    payload = json.dumps({"type": command, "params": params or {}}).encode("utf-8")
    for candidate in hosts:
        try:
            with socket.create_connection((candidate, port), timeout=timeout) as sock:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.sendall(payload)
                response = receive_unreal_json(sock, timeout)
            if response.get("status") == "error":
                raise RuntimeError(str(response.get("error") or response))
            response.setdefault("_mosim_host", candidate)
            return response
        except Exception as exc:  # pragma: no cover - depends on editor state.
            errors.append(f"{candidate}:{port} -> {type(exc).__name__}: {exc}")
    raise RuntimeError("; ".join(errors))


def response_result(response: dict[str, Any]) -> dict[str, Any]:
    result = response.get("result")
    return result if isinstance(result, dict) else response


def current_level_name(response: dict[str, Any]) -> str:
    queue: list[Any] = [response_result(response)]
    keys = (
        "level",
        "level_name",
        "current_level",
        "currentLevel",
        "map",
        "map_name",
        "current_map",
        "currentMap",
        "world",
        "world_name",
        "worldName",
        "persistent_level",
        "persistentLevel",
    )
    while queue:
        item = queue.pop(0)
        if isinstance(item, dict):
            for key in keys:
                value = item.get(key)
                if isinstance(value, str) and value:
                    return value
            queue.extend(item.values())
        elif isinstance(item, list):
            queue.extend(item)
    return ""


def actor_preview(actor: Any) -> dict[str, Any]:
    if not isinstance(actor, dict):
        return {"raw_type": type(actor).__name__}
    preview: dict[str, Any] = {}
    for key in (
        "name",
        "label",
        "actor_label",
        "type",
        "class",
        "path",
        "location",
        "rotation",
        "scale",
    ):
        if key in actor:
            preview[key] = actor[key]
    if not preview:
        for key, value in list(actor.items())[:8]:
            if isinstance(value, (str, int, float, bool, type(None), list, dict)):
                preview[key] = value
    return preview


def actors_from_response(response: dict[str, Any]) -> list[Any]:
    result = response_result(response)
    actors = result.get("actors")
    return actors if isinstance(actors, list) else []


def current_level_summary_payload(
    timeout: float = 10.0,
    host: str | None = None,
    port: int = 55557,
    sample_limit: int = 20,
) -> dict[str, Any]:
    requested_sample_limit = sample_limit
    sample_limit = clamp_int(sample_limit, minimum=1, maximum=200)
    try:
        response = send_unreal_command(
            "get_actors_in_level",
            host=host,
            port=port,
            timeout=timeout,
        )
    except Exception as exc:
        return {
            "schema": "mosim.unreal_mcp.current_level_summary.v1",
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "hint": "Open MoSimSceneLibrary in Unreal Editor with the UnrealMCP listener enabled.",
        }
    actors = actors_from_response(response)
    return {
        "schema": "mosim.unreal_mcp.current_level_summary.v1",
        "ok": True,
        "host": response.get("_mosim_host", ""),
        "port": port,
        "current_level": current_level_name(response),
        "actor_count": len(actors),
        "requested_sample_limit": requested_sample_limit,
        "effective_sample_limit": sample_limit,
        "actors_sample": [actor_preview(actor) for actor in actors[:sample_limit]],
    }


def find_level_actors_payload(
    pattern: str,
    timeout: float = 10.0,
    host: str | None = None,
    port: int = 55557,
    limit: int = 50,
) -> dict[str, Any]:
    requested_limit = limit
    limit = clamp_int(limit, minimum=1, maximum=200)
    try:
        response = send_unreal_command(
            "find_actors_by_name",
            {"pattern": pattern},
            host=host,
            port=port,
            timeout=timeout,
        )
    except Exception as exc:
        return {
            "schema": "mosim.unreal_mcp.find_level_actors.v1",
            "ok": False,
            "pattern": pattern,
            "error": f"{type(exc).__name__}: {exc}",
        }
    actors = actors_from_response(response)
    return {
        "schema": "mosim.unreal_mcp.find_level_actors.v1",
        "ok": True,
        "host": response.get("_mosim_host", ""),
        "port": port,
        "pattern": pattern,
        "requested_limit": requested_limit,
        "effective_limit": limit,
        "returned": min(len(actors), limit),
        "actor_count": len(actors),
        "actors": [actor_preview(actor) for actor in actors[:limit]],
    }


def health_payload(timeout: float = 1.0, host: str | None = None, port: int = 55557) -> dict[str, Any]:
    context = project_context_payload()
    return {
        "schema": "mosim.unreal_mcp.health.v1",
        "mcp_server": "mosim-unreal",
        "server_scope": "Live Unreal Editor automation boundary",
        "toolset": TOOLSET,
        "project_ok": bool(context["renderer_exists"] and context["bridge_plugin_exists"]),
        "context": context,
        "listener": editor_listener_health_payload(timeout=timeout, host=host, port=port),
        "legacy_flopperam_wrapper": rel(LEGACY_FLOPPERAM_WRAPPER),
        "legacy_flopperam_wrapper_exists": LEGACY_FLOPPERAM_WRAPPER.exists(),
        "current_wrapper": rel(THIS_WRAPPER),
    }


def compact_map_record(record: dict[str, Any], *, tag_limit: int = 6) -> dict[str, Any]:
    return {
        "package": record.get("package", ""),
        "path": record.get("path", ""),
        "role": record.get("role", ""),
        "score": record.get("score", 0),
        "tags": list(record.get("tags", []))[:tag_limit],
    }


def compact_scene_source_row(row: dict[str, Any], *, map_limit: int = 3) -> dict[str, Any]:
    if row.get("error"):
        return {
            "name": row.get("name", ""),
            "uproject_path": row.get("uproject") or row.get("uproject_path", ""),
            "error": row.get("error", ""),
        }

    plugins = list(row.get("plugins", []))
    truth = row.get("truth", {}) if isinstance(row.get("truth"), dict) else {}
    explicit_truth = list(truth.get("explicit_truth_candidates", []))
    proxy_truth = list(truth.get("ue_truth_proxy_candidates", []))
    maps = [
        compact_map_record(record)
        for record in list(row.get("recommended_review_maps", []))[: max(map_limit, 0)]
        if isinstance(record, dict)
    ]
    return {
        "name": row.get("name", ""),
        "source_type": row.get("source_type", ""),
        "project_root": row.get("project_root", ""),
        "uproject_path": row.get("uproject_path", ""),
        "engine_association": row.get("engine_association", ""),
        "verdict": row.get("verdict", ""),
        "editable_candidate": bool(row.get("editable_candidate")),
        "renderable_candidate": bool(row.get("renderable_candidate")),
        "planning_truth_ready": bool(row.get("planning_truth_ready")),
        "umap_count": row.get("umap_count", 0),
        "uasset_count": row.get("uasset_count", 0),
        "scan_truncated": bool(row.get("scan_truncated")),
        "plugins_sample": plugins[:12],
        "plugins_truncated": len(plugins) > 12,
        "recommended_review_maps": maps,
        "truth": {
            "has_explicit_truth_source": bool(truth.get("has_explicit_truth_source")),
            "has_ue_truth_proxy_candidates": bool(truth.get("has_ue_truth_proxy_candidates")),
            "explicit_truth_candidates": explicit_truth[:5],
            "ue_truth_proxy_candidates": proxy_truth[:5],
            "truth_gap": truth.get("truth_gap", ""),
        },
    }


def scene_source_status_payload(
    query: str = "",
    limit: int = 20,
    *,
    detail: bool = False,
    map_limit: int = 3,
) -> dict[str, Any]:
    requested_limit = limit
    requested_map_limit = map_limit
    limit = clamp_int(limit, minimum=1, maximum=3 if detail else 50)
    map_limit = clamp_int(map_limit, minimum=0, maximum=12)
    query_lower = query.lower().strip()
    rows: list[dict[str, Any]] = []
    for uproject in find_uprojects(SCENE_ROOT):
        if query_lower and query_lower not in uproject.parent.name.lower():
            continue
        try:
            row = audit_project(uproject)
        except Exception as exc:  # pragma: no cover - defensive report path.
            row = {
                "name": uproject.parent.name,
                "uproject": rel(uproject),
                "error": f"{type(exc).__name__}: {exc}",
            }
        rows.append(row if detail else compact_scene_source_row(row, map_limit=map_limit))
        if len(rows) >= limit:
            break
    return {
        "schema": "mosim.unreal_mcp.scene_source_status.v1",
        "scene_root": rel(SCENE_ROOT),
        "query": query,
        "detail": detail,
        "requested_limit": requested_limit,
        "effective_limit": limit,
        "requested_map_limit": requested_map_limit,
        "map_limit": map_limit,
        "returned": len(rows),
        "sources": rows,
    }


def reversible_actor_probe_payload(
    *,
    actor_name_prefix: str = "",
    execute: bool = False,
    timeout: float = 30.0,
    host: str | None = None,
    port: int = 55557,
    allow_entry_map: bool = False,
    allow_unknown_map: bool = False,
) -> dict[str, Any]:
    actor_name = unique_actor_name_from_user_value(actor_name_prefix or None)
    plan: dict[str, Any] = {
        "schema": "mosim.unreal_mcp.reversible_actor_probe.v1",
        "execute": execute,
        "host_candidates": default_hosts(host),
        "port": port,
        "actor_name": actor_name,
        "safeguards": [
            "creates a uniquely named temporary StaticMeshActor",
            "moves only that temporary actor",
            "deletes the temporary actor before returning",
            "does not save the level",
            "refuses /Engine/Maps/Entry unless allow_entry_map=true",
            "refuses unknown current map unless allow_unknown_map=true",
        ],
    }
    if not execute:
        return {
            **plan,
            "ok": True,
            "status": "planned_only",
            "next_step": "Call again with execute=true only after a real review map is loaded in Unreal Editor.",
        }

    try:
        resolved_host = live_editor_default_host(host)
        evidence = run_reversible_actor_probe(
            resolved_host,
            port,
            actor_name,
            timeout,
            allow_entry_map=allow_entry_map,
            allow_unknown_map=allow_unknown_map,
        )
    except Exception as exc:
        return {
            **plan,
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
        }

    return {
        **plan,
        **evidence,
        "ok": bool(evidence.get("ok")),
        "execute": True,
        "status": "executed",
    }


def scene_truth_export_plan_payload(query: str = "", limit: int = 20) -> dict[str, Any]:
    plans = plan_exports(SCENE_ROOT, TRUTH_ROOT, query=query)
    return {
        "schema": "mosim.unreal_mcp.scene_truth_export_plan.v1",
        "scene_root": rel(SCENE_ROOT),
        "truth_root": rel(TRUTH_ROOT),
        "query": query,
        "returned": min(len(plans), limit),
        "plans": plans[:limit],
    }


def editor_log_summary_payload(lines: int = 120) -> dict[str, Any]:
    requested_lines = lines
    lines = clamp_int(lines, minimum=1, maximum=300)
    logs = sorted(SAVED_LOGS.glob("*.log"), key=lambda path: path.stat().st_mtime, reverse=True) if SAVED_LOGS.exists() else []
    latest = logs[0] if logs else None
    text_lines: list[str] = []
    if latest:
        text_lines = latest.read_text(encoding="utf-8", errors="replace").splitlines()[-max(lines, 1) :]
    severity_markers = {
        "errors": ("error:", "fatal error", "exception_access_violation", "ensure condition failed"),
        "warnings": ("warning:", "logwindows: failed", "missing", "could not be found"),
    }
    lowered = [line.lower() for line in text_lines]
    return {
        "schema": "mosim.unreal_mcp.editor_log_summary.v1",
        "log_dir": rel(SAVED_LOGS),
        "latest_log": rel(latest) if latest else "",
        "available_logs": [rel(path) for path in logs[:10]],
        "requested_lines": requested_lines,
        "effective_lines": lines,
        "tail_line_count": len(text_lines),
        "counts": {
            key: sum(1 for line in lowered if any(marker in line for marker in markers))
            for key, markers in severity_markers.items()
        },
        "tail": [redact_text(line) for line in text_lines],
    }


def boundary_payload() -> dict[str, Any]:
    return {
        "schema": "mosim.unreal_mcp.boundary.v1",
        "mosim-unreal": {
            "owns": [
                "running UE Editor health and project context",
                "editor listener reachability",
                "bounded local Content scene/asset queries",
                "live read-only actor and current-level queries",
                "planned-only or explicitly executed reversible actor probe",
                "redacted editor log diagnostics",
                "scene-truth export planning",
                "future persistent actor/material/Blueprint/map edits",
                "future viewport capture and scene-truth export execution",
            ],
            "does_not_own": [
                "Epic/Fab account inventory",
                "Launcher downloads",
                "Marketplace license decisions",
                "raw account cache reading",
            ],
        },
        "mosim-epic": {
            "owns": [
                "sanitized Epic/Fab/Launcher inventory",
                "scene-source candidate selection",
                "scene-source registry and acceptance gates",
                "truth-export planning for local editable scenes",
            ],
            "does_not_own": [
                "live editor object graph edits",
                "viewport capture",
                "PIE/runtime control",
            ],
        },
    }


def serve() -> int:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError:
        print(
            "Missing MCP Python SDK. Run with: uv run --with mcp python "
            "Docs/Skills/Unreal/mosim-unreal/mcp/server.py serve",
            file=sys.stderr,
        )
        return 2

    mcp = FastMCP("mosim-unreal")

    @mcp.tool()
    def ue_health(timeout_seconds: float = 1.0, host: str = "", port: int = 55557) -> dict[str, Any]:
        """Check MoSim UE project files and the current editor-side listener."""
        return health_payload(timeout=timeout_seconds, host=host or None, port=port)

    @mcp.tool()
    def project_context() -> dict[str, Any]:
        """Return MoSimSceneLibrary project metadata, plugins, maps, and engine installs."""
        return project_context_payload()

    @mcp.tool()
    def editor_listener_health(
        timeout_seconds: float = 1.0,
        host: str = "",
        port: int = 55557,
    ) -> dict[str, Any]:
        """Check whether the UE Editor-side TCP listener is reachable from WSL."""
        return editor_listener_health_payload(timeout=timeout_seconds, host=host or None, port=port)

    @mcp.tool()
    def asset_search(query: str = "", suffix: str = "", limit: int = 100) -> dict[str, Any]:
        """Search MoSimSceneLibrary Content for local .uasset/.umap files."""
        return asset_search_payload(query=query, suffix=suffix, limit=limit)

    @mcp.tool()
    def list_maps(query: str = "", limit: int = 100) -> dict[str, Any]:
        """List local MoSimSceneLibrary .umap files and configured default maps."""
        return list_maps_payload(query=query, limit=limit)

    @mcp.tool()
    def current_level_summary(
        timeout_seconds: float = 10.0,
        host: str = "",
        port: int = 55557,
        sample_limit: int = 20,
    ) -> dict[str, Any]:
        """Read the current level name and actor sample from a live UE Editor."""
        return current_level_summary_payload(
            timeout=timeout_seconds,
            host=host or None,
            port=port,
            sample_limit=sample_limit,
        )

    @mcp.tool()
    def find_level_actors(
        pattern: str,
        timeout_seconds: float = 10.0,
        host: str = "",
        port: int = 55557,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Find actors in the live UE level by name pattern without modifying the map."""
        return find_level_actors_payload(
            pattern=pattern,
            timeout=timeout_seconds,
            host=host or None,
            port=port,
            limit=limit,
        )

    @mcp.tool()
    def reversible_actor_probe(
        execute: bool = False,
        actor_name_prefix: str = "",
        timeout_seconds: float = 30.0,
        host: str = "",
        port: int = 55557,
        allow_entry_map: bool = False,
        allow_unknown_map: bool = False,
    ) -> dict[str, Any]:
        """Plan or execute a temporary spawn/move/delete actor probe without saving the map."""
        return reversible_actor_probe_payload(
            actor_name_prefix=actor_name_prefix,
            execute=execute,
            timeout=timeout_seconds,
            host=host or None,
            port=port,
            allow_entry_map=allow_entry_map,
            allow_unknown_map=allow_unknown_map,
        )

    @mcp.tool()
    def scene_source_status(
        query: str = "",
        limit: int = 20,
        detail: bool = False,
        map_limit: int = 3,
    ) -> dict[str, Any]:
        """Audit local editable scene-source candidates under References/UnrealScenes with compact output by default."""
        return scene_source_status_payload(query=query, limit=limit, detail=detail, map_limit=map_limit)

    @mcp.tool()
    def scene_truth_export_plan(query: str = "", limit: int = 20) -> dict[str, Any]:
        """Plan Editor Python commands for collision/planning-truth export."""
        return scene_truth_export_plan_payload(query=query, limit=limit)

    @mcp.tool()
    def editor_log_summary(lines: int = 120) -> dict[str, Any]:
        """Return a bounded tail and severity counts from the latest UE project log."""
        return editor_log_summary_payload(lines=lines)

    @mcp.tool()
    def tool_boundary() -> dict[str, Any]:
        """Explain the split between mosim-unreal and mosim-epic."""
        return boundary_payload()

    mcp.run()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "serve",
            "dump-health",
            "dump-context",
            "dump-listener",
            "dump-assets",
            "dump-maps",
            "dump-level",
            "dump-actors",
            "dump-reversible-probe",
            "dump-scene-sources",
            "dump-truth-plan",
            "dump-log",
            "dump-boundary",
            "dump-tools",
        ),
        nargs="?",
        default="serve",
    )
    parser.add_argument("--timeout", type=float, default=1.0)
    parser.add_argument("--host", default="")
    parser.add_argument("--port", type=int, default=55557)
    parser.add_argument("--query", default="")
    parser.add_argument("--suffix", default="")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--lines", type=int, default=120)
    parser.add_argument("--pattern", default="*")
    parser.add_argument("--detail", action="store_true")
    parser.add_argument("--map-limit", type=int, default=3)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--actor-name-prefix", default="")
    parser.add_argument("--allow-entry-map", action="store_true")
    parser.add_argument("--allow-unknown-map", action="store_true")
    args = parser.parse_args(argv)

    if args.command == "serve":
        return serve()

    payload: Any
    if args.command == "dump-health":
        payload = health_payload(timeout=args.timeout, host=args.host or None, port=args.port)
    elif args.command == "dump-context":
        payload = project_context_payload()
    elif args.command == "dump-listener":
        payload = editor_listener_health_payload(timeout=args.timeout, host=args.host or None, port=args.port)
    elif args.command == "dump-assets":
        payload = asset_search_payload(query=args.query, suffix=args.suffix, limit=args.limit)
    elif args.command == "dump-maps":
        payload = list_maps_payload(query=args.query, limit=args.limit)
    elif args.command == "dump-level":
        payload = current_level_summary_payload(
            timeout=args.timeout,
            host=args.host or None,
            port=args.port,
            sample_limit=args.limit,
        )
    elif args.command == "dump-actors":
        payload = find_level_actors_payload(
            pattern=args.pattern,
            timeout=args.timeout,
            host=args.host or None,
            port=args.port,
            limit=args.limit,
        )
    elif args.command == "dump-reversible-probe":
        payload = reversible_actor_probe_payload(
            actor_name_prefix=args.actor_name_prefix,
            execute=args.execute,
            timeout=args.timeout,
            host=args.host or None,
            port=args.port,
            allow_entry_map=args.allow_entry_map,
            allow_unknown_map=args.allow_unknown_map,
        )
    elif args.command == "dump-scene-sources":
        payload = scene_source_status_payload(
            query=args.query,
            limit=args.limit,
            detail=args.detail,
            map_limit=args.map_limit,
        )
    elif args.command == "dump-truth-plan":
        payload = scene_truth_export_plan_payload(query=args.query, limit=args.limit)
    elif args.command == "dump-log":
        payload = editor_log_summary_payload(lines=args.lines)
    elif args.command == "dump-boundary":
        payload = boundary_payload()
    else:
        payload = {"schema": "mosim.unreal_mcp.tools.v1", "tools": TOOLSET}

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
