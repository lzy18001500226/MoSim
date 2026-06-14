#!/usr/bin/env python3
"""Import the accepted Sunray150 runtime StaticMesh into MoSimSceneLibrary.

The UE playback actor loads the reviewed Sunray visual from:

    /Game/Sunray150/sunray150_with_mid360_textured.sunray150_with_mid360_textured

This helper runs UnrealEditor-Cmd with an Editor Python script so the import is
reproducible and evidence-backed instead of a one-off editor click.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from run_scene_truth_export import (
    ENGINE_ROOT_BY_VERSION,
    resolve_editor_cmd,
    tail_lines,
    to_windows_path,
)


ROOT = Path(__file__).resolve().parents[2]
RENDERER_UPROJECT = ROOT / "UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject"
DEFAULT_SOURCE_FBX = (
    ROOT / "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/sunray150_with_mid360_textured.fbx"
)
DEFAULT_ASSET_PATH = "/Game/Sunray150/sunray150_with_mid360_textured"


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def output_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def write_editor_import_script(
    script_path: Path,
    *,
    source_fbx: Path,
    asset_path: str,
    evidence_path: Path,
) -> None:
    destination_path, asset_name = asset_path.rsplit("/", 1)
    source = f"""
import json
from pathlib import Path
import unreal

source_fbx = Path({to_windows_path(source_fbx)!r})
destination_path = {destination_path!r}
asset_name = {asset_name!r}
asset_path = {asset_path!r}
object_path = asset_path + "." + asset_name
evidence_path = Path({to_windows_path(evidence_path)!r})

if not source_fbx.exists():
    raise RuntimeError("Sunray150 source FBX missing: " + str(source_fbx))

editor_asset_library = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

if not editor_asset_library.does_directory_exist(destination_path):
    editor_asset_library.make_directory(destination_path)

task = unreal.AssetImportTask()
task.filename = str(source_fbx)
task.destination_path = destination_path
task.destination_name = asset_name
task.automated = True
task.save = True
task.replace_existing = True
task.replace_existing_settings = True

import_ui = unreal.FbxImportUI()
import_ui.import_mesh = True
import_ui.import_as_skeletal = False
import_ui.import_materials = True
import_ui.import_textures = True
import_ui.create_physics_asset = False

static_data = unreal.FbxStaticMeshImportData()
static_data.combine_meshes = True
static_data.generate_lightmap_u_vs = True
static_data.auto_generate_collision = True
import_ui.static_mesh_import_data = static_data
task.options = import_ui

asset_tools.import_asset_tasks([task])

imported_paths = [str(obj.get_path_name()) for obj in task.get_objects() if obj]
asset = unreal.load_asset(object_path)
exists = bool(asset)
if exists:
    editor_asset_library.save_asset(object_path, only_if_is_dirty=False)
editor_asset_library.save_directory(destination_path, only_if_is_dirty=False, recursive=True)

bounds = {{}}
if exists:
    for method_name in ("get_bounds", "get_bounding_box"):
        method = getattr(asset, method_name, None)
        if callable(method):
            try:
                value = method()
                bounds[method_name] = str(value)
                break
            except Exception as exc:
                bounds[method_name + "_error"] = str(exc)

asset_data = editor_asset_library.find_asset_data(object_path)
payload = {{
    "schema": "mosim.sunray150_runtime_static_mesh_import.v1",
    "ok": exists,
    "source_fbx": str(source_fbx),
    "destination_path": destination_path,
    "asset_name": asset_name,
    "asset_path": asset_path,
    "object_path": object_path,
    "imported_paths": imported_paths,
    "asset_class": str(asset.get_class().get_name()) if exists else "",
    "asset_data_package_name": str(asset_data.package_name) if asset_data else "",
    "bounds": bounds,
    "claim_boundary": [
        "UE Content StaticMesh import/readiness only.",
        "Not final visual material acceptance.",
        "Not MWORKS/ROS2 controller, planner, runtime, or closed-loop evidence."
    ],
}}
evidence_path.parent.mkdir(parents=True, exist_ok=True)
evidence_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
if not payload["ok"]:
    raise RuntimeError("Sunray150 runtime StaticMesh import failed: " + json.dumps(payload, ensure_ascii=False))
"""
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(source.strip() + "\n", encoding="utf-8")


def build_command(editor_cmd: Path, script_path: Path) -> list[str]:
    return [
        str(editor_cmd),
        to_windows_path(RENDERER_UPROJECT),
        "-run=pythonscript",
        f"-script={to_windows_path(script_path)}",
        "-nosplash",
        "-NoSound",
        "-stdout",
        "-FullStdOutLogOutput",
        "-unattended",
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-fbx", type=Path, default=DEFAULT_SOURCE_FBX)
    parser.add_argument("--asset-path", default=DEFAULT_ASSET_PATH)
    parser.add_argument("--engine-version", default="5.5")
    parser.add_argument("--engine-root", type=Path, default=None)
    parser.add_argument("--editor-cmd", type=Path, default=None)
    parser.add_argument(
        "--script-path",
        type=Path,
        default=ROOT / "Results/tmp/import_sunray150_runtime_static_mesh_editor.py",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=ROOT / "Results/tmp/import_sunray150_runtime_static_mesh_latest.json",
    )
    parser.add_argument("--log-output", type=Path, default=None)
    parser.add_argument("--timeout-seconds", type=float, default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_fbx = args.source_fbx if args.source_fbx.is_absolute() else ROOT / args.source_fbx
    script_path = args.script_path if args.script_path.is_absolute() else ROOT / args.script_path
    evidence_path = args.json_output if args.json_output.is_absolute() else ROOT / args.json_output
    engine_root = args.engine_root or ENGINE_ROOT_BY_VERSION.get(args.engine_version)
    editor_cmd = resolve_editor_cmd(RENDERER_UPROJECT, engine_root, args.editor_cmd)
    write_editor_import_script(
        script_path,
        source_fbx=source_fbx,
        asset_path=args.asset_path,
        evidence_path=evidence_path,
    )
    command = build_command(editor_cmd, script_path)
    payload: dict[str, Any] = {
        "renderer_uproject": rel(RENDERER_UPROJECT),
        "source_fbx": rel(source_fbx),
        "asset_path": args.asset_path,
        "editor_cmd": to_windows_path(editor_cmd),
        "script_path": rel(script_path),
        "json_output": rel(evidence_path),
        "command": command,
        "dry_run": args.dry_run,
    }
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    try:
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=args.timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        if args.log_output:
            log_path = args.log_output if args.log_output.is_absolute() else ROOT / args.log_output
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(output_text(exc.stdout) + output_text(exc.stderr), encoding="utf-8", errors="replace")
            payload["log_output"] = rel(log_path)
            payload["tail"] = tail_lines(log_path, 80)
        payload.update({"ok": False, "reason": "timeout", "timeout_seconds": args.timeout_seconds})
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 124
    if args.log_output:
        log_path = args.log_output if args.log_output.is_absolute() else ROOT / args.log_output
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text((completed.stdout or "") + (completed.stderr or ""), encoding="utf-8", errors="replace")
        payload["log_output"] = rel(log_path)
        payload["tail"] = tail_lines(log_path, 80)
    if evidence_path.exists():
        payload["import_evidence"] = json.loads(evidence_path.read_text(encoding="utf-8"))
    payload["ok"] = completed.returncode == 0 and bool(payload.get("import_evidence", {}).get("ok"))
    payload["returncode"] = completed.returncode
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else completed.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
