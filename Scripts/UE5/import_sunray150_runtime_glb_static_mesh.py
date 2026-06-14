#!/usr/bin/env python3
"""Import the accepted Sunray150 Blender GLB into UE for runtime review.

The FBX route can preserve slot names while dropping Blender material node
effects. This helper uses the GLB exported from the accepted audit .blend so
PBR-style texture/material data has the best chance of reaching UE intact.
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
DEFAULT_SOURCE_GLB = (
    ROOT / "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/sunray150_with_mid360_textured.glb"
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
    source_glb: Path,
    asset_path: str,
    evidence_path: Path,
) -> None:
    destination_path, asset_name = asset_path.rsplit("/", 1)
    source = f"""
import json
from pathlib import Path
import unreal

source_glb = Path({to_windows_path(source_glb)!r})
destination_path = {destination_path!r}
asset_name = {asset_name!r}
asset_path = {asset_path!r}
object_path = asset_path + "." + asset_name
evidence_path = Path({to_windows_path(evidence_path)!r})

if not source_glb.exists():
    raise RuntimeError("Sunray150 source GLB missing: " + str(source_glb))

asset_lib = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

if not asset_lib.does_directory_exist(destination_path):
    asset_lib.make_directory(destination_path)

task = unreal.AssetImportTask()
task.filename = str(source_glb)
task.destination_path = destination_path
task.destination_name = asset_name
task.automated = True
task.save = True
task.replace_existing = True
task.replace_existing_settings = False

asset_tools.import_asset_tasks([task])

imported_paths = [str(obj.get_path_name()) for obj in task.get_objects() if obj]
asset = unreal.load_asset(object_path)
exists = bool(asset)
if exists:
    asset_lib.save_asset(object_path, only_if_is_dirty=False)
asset_lib.save_directory(destination_path, only_if_is_dirty=False, recursive=True)

slots = []
if exists:
    try:
        static_materials = list(asset.get_editor_property("static_materials"))
    except Exception:
        static_materials = []
    for idx, entry in enumerate(static_materials):
        mat = getattr(entry, "material_interface", None)
        slots.append({{
            "index": idx,
            "slot_name": str(getattr(entry, "material_slot_name", "")),
            "material_name": str(mat.get_name()) if mat else "",
            "material_path": str(mat.get_path_name()) if mat else "",
        }})

payload = {{
    "schema": "mosim.sunray150_runtime_glb_import.v1",
    "ok": exists,
    "source_glb": str(source_glb),
    "destination_path": destination_path,
    "asset_name": asset_name,
    "asset_path": asset_path,
    "object_path": object_path,
    "imported_paths": imported_paths,
    "asset_class": str(asset.get_class().get_name()) if exists else "",
    "material_slot_count": len(slots),
    "slots": slots,
    "claim_boundary": [
        "UE GLB StaticMesh import/readiness only.",
        "Preserves accepted Blender visual route better than the fallback FBX/material rebuild route.",
        "Still requires runtime screenshot and user visual review before final material acceptance."
    ],
}}
evidence_path.parent.mkdir(parents=True, exist_ok=True)
evidence_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
if not payload["ok"]:
    raise RuntimeError("Sunray150 runtime GLB import failed: " + json.dumps(payload, ensure_ascii=False))
"""
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(source.strip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-glb", type=Path, default=DEFAULT_SOURCE_GLB)
    parser.add_argument("--asset-path", default=DEFAULT_ASSET_PATH)
    parser.add_argument("--engine-version", default="5.5")
    parser.add_argument("--engine-root", type=Path, default=None)
    parser.add_argument("--editor-cmd", type=Path, default=None)
    parser.add_argument(
        "--script-path",
        type=Path,
        default=ROOT / "Results/tmp/import_sunray150_runtime_glb_static_mesh_editor.py",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=ROOT / "Results/tmp/import_sunray150_runtime_glb_static_mesh_latest.json",
    )
    parser.add_argument("--log-output", type=Path, default=None)
    parser.add_argument("--timeout-seconds", type=float, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_glb = args.source_glb if args.source_glb.is_absolute() else ROOT / args.source_glb
    script_path = args.script_path if args.script_path.is_absolute() else ROOT / args.script_path
    evidence_path = args.json_output if args.json_output.is_absolute() else ROOT / args.json_output
    engine_root = args.engine_root or ENGINE_ROOT_BY_VERSION.get(args.engine_version)
    editor_cmd = resolve_editor_cmd(RENDERER_UPROJECT, engine_root, args.editor_cmd)
    write_editor_import_script(
        script_path,
        source_glb=source_glb,
        asset_path=args.asset_path,
        evidence_path=evidence_path,
    )
    command = [
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
    payload: dict[str, Any] = {
        "renderer_uproject": rel(RENDERER_UPROJECT),
        "source_glb": rel(source_glb),
        "asset_path": args.asset_path,
        "editor_cmd": to_windows_path(editor_cmd),
        "script_path": rel(script_path),
        "json_output": rel(evidence_path),
        "command": command,
    }
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
