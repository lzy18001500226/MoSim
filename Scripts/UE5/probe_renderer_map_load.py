#!/usr/bin/env python3
"""Verify that the MoSim renderer project can load the linked scene-source map.

This runs UnrealEditor-Cmd against `UE5/MworksUnrealRenderer` and loads the map
package recorded in the scene-source registry. It writes a small JSON evidence
file through Editor Python and exits without saving the map.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from run_scene_truth_export import ENGINE_ROOT_BY_VERSION, quote, resolve_editor_cmd, to_windows_path


ROOT = Path(__file__).resolve().parents[2]
RENDERER_UPROJECT = ROOT / "UE5/MworksUnrealRenderer/MworksUnrealRenderer.uproject"
SCENE_SOURCE_REGISTRY = ROOT / "UE5/MworksUnrealRenderer/Content/MworksData/scene_source_registry.json"


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{rel(path)} must be a JSON object")
    return payload


def source_by_id(registry: dict[str, Any], source_id: str) -> dict[str, Any]:
    sources = registry.get("local_editable_fallback", {}).get("scene_sources", [])
    for source in sources if isinstance(sources, list) else []:
        if isinstance(source, dict) and source.get("scene_source_id") == source_id:
            return source
    raise ValueError(f"scene source not found: {source_id}")


def write_probe_script(script_path: Path, output_path: Path, scene_source_id: str, map_package: str) -> None:
    source = f"""
import json
from pathlib import Path
import unreal

scene_source_id = {scene_source_id!r}
map_package = {map_package!r}
output_path = Path({to_windows_path(output_path)!r})

ok = bool(unreal.EditorLevelLibrary.load_level(map_package))
world = unreal.EditorLevelLibrary.get_editor_world()
level_name = ""
if world:
    for method_name in ("get_map_name", "get_path_name", "get_name"):
        method = getattr(world, method_name, None)
        if callable(method):
            try:
                level_name = str(method())
                if level_name:
                    break
            except Exception:
                pass
actors = unreal.EditorLevelLibrary.get_all_level_actors() if world else []
loaded_expected_map = "DerelictCorridor" in level_name
has_scene_content = len(actors) > 0
payload = {{
    "ok": ok and loaded_expected_map and has_scene_content,
    "load_level_returned": ok,
    "loaded_expected_map": loaded_expected_map,
    "has_scene_content": has_scene_content,
    "scene_source_id": scene_source_id,
    "map_package": map_package,
    "level_name": level_name,
    "actor_count": len(actors),
    "project_dir": unreal.Paths.project_dir(),
}}
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
if not payload["ok"]:
    raise RuntimeError("renderer did not load expected scene map/content: " + json.dumps(payload, ensure_ascii=False))
"""
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(source.strip() + "\n", encoding="utf-8")


def build_command(editor_cmd: Path, script_path: Path, map_package: str) -> list[str]:
    return [
        str(editor_cmd),
        to_windows_path(RENDERER_UPROJECT),
        map_package,
        "-run=pythonscript",
        f"-script={to_windows_path(script_path)}",
        "-nosplash",
        "-NoSound",
        "-stdout",
        "-FullStdOutLogOutput",
        "-unattended",
        "-NoShaderCompile",
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-source-id", default="local_derelictcorridormegascans")
    parser.add_argument("--engine-version", default="5.7")
    parser.add_argument("--engine-root", type=Path, default=None)
    parser.add_argument("--editor-cmd", type=Path, default=None)
    parser.add_argument("--script-path", type=Path, default=ROOT / "Results/tmp/renderer_map_load_probe.py")
    parser.add_argument("--json-output", type=Path, default=ROOT / "Results/tmp/renderer_map_load_probe_latest.json")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = load_json(SCENE_SOURCE_REGISTRY)
    source = source_by_id(registry, args.scene_source_id)
    map_package = str(source.get("renderer_map_package", ""))
    if not map_package:
        raise ValueError(f"{args.scene_source_id} has no renderer_map_package")
    map_asset = source.get("renderer_map_asset")
    if not map_asset or not (ROOT / str(map_asset)).exists():
        raise FileNotFoundError(f"renderer_map_asset missing: {map_asset}")
    engine_root = args.engine_root or ENGINE_ROOT_BY_VERSION.get(args.engine_version)
    editor_cmd = resolve_editor_cmd(RENDERER_UPROJECT, engine_root, args.editor_cmd)
    output_path = args.json_output if args.json_output.is_absolute() else ROOT / args.json_output
    script_path = args.script_path if args.script_path.is_absolute() else ROOT / args.script_path
    write_probe_script(script_path, output_path, args.scene_source_id, map_package)
    command = build_command(editor_cmd, script_path, map_package)
    payload = {
        "scene_source_id": args.scene_source_id,
        "renderer_uproject": rel(RENDERER_UPROJECT),
        "renderer_map_asset": str(map_asset),
        "renderer_map_package": map_package,
        "editor_cmd": to_windows_path(editor_cmd),
        "script_path": rel(script_path),
        "json_output": rel(output_path),
        "command": command,
        "dry_run": args.dry_run,
    }
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if completed.stdout:
        print(completed.stdout)
    if completed.stderr:
        print(completed.stderr)
    if completed.returncode != 0:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return completed.returncode
    evidence = load_json(output_path)
    evidence.update({key: payload[key] for key in ["renderer_uproject", "renderer_map_asset", "renderer_map_package"]})
    output_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
