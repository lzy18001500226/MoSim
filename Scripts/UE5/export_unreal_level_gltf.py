#!/usr/bin/env python3
"""Export a loaded Unreal level to glTF/GLB through UE's GLTFExporter plugin.

This is an orchestration wrapper. The actual scene export runs inside
UnrealEditor-Cmd via the official GLTFExporter plugin and does not save or
modify the source project.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_scene_truth_export import ENGINE_ROOT_BY_VERSION, resolve_editor_cmd, tail_lines, to_windows_path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENE_REGISTRY = ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json"
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping/factory_l2_static_import"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def source_by_id(registry: dict[str, Any], scene_source_id: str) -> dict[str, Any]:
    sources = registry.get("local_editable_fallback", {}).get("scene_sources", [])
    for source in sources if isinstance(sources, list) else []:
        if isinstance(source, dict) and source.get("scene_source_id") == scene_source_id:
            return source
    raise ValueError(f"scene_source_id not found: {scene_source_id}")


def write_editor_export_script(
    *,
    script_path: Path,
    map_package: str,
    glb_output: Path,
    json_output: Path,
    scene_source_id: str,
    claim_boundary: str,
) -> None:
    source = f"""
import json
from pathlib import Path
import unreal

scene_source_id = {scene_source_id!r}
map_package = {map_package!r}
glb_output = Path({to_windows_path(glb_output)!r})
json_output = Path({to_windows_path(json_output)!r})
claim_boundary = {claim_boundary!r}

def call_if_available(owner, name, *args):
    fn = getattr(owner, name, None)
    if callable(fn):
        return fn(*args)
    return None

loaded = False
level_editor_subsystem_class = getattr(unreal, "LevelEditorSubsystem", None)
get_editor_subsystem = getattr(unreal, "get_editor_subsystem", None)
if level_editor_subsystem_class and callable(get_editor_subsystem):
    subsystem = get_editor_subsystem(level_editor_subsystem_class)
    load_level = getattr(subsystem, "load_level", None)
    if callable(load_level):
        loaded = bool(load_level(map_package))
if not loaded:
    ell = getattr(unreal, "EditorLevelLibrary", None)
    load_level = getattr(ell, "load_level", None) if ell else None
    if callable(load_level):
        loaded = bool(load_level(map_package))
if not loaded:
    raise RuntimeError("Unable to load map package: " + map_package)

world = None
if level_editor_subsystem_class and callable(get_editor_subsystem):
    subsystem = get_editor_subsystem(level_editor_subsystem_class)
    get_world = getattr(subsystem, "get_editor_world", None)
    if callable(get_world):
        world = get_world()
if world is None:
    ell = getattr(unreal, "EditorLevelLibrary", None)
    get_world = getattr(ell, "get_editor_world", None) if ell else None
    if callable(get_world):
        world = get_world()
if world is None:
    raise RuntimeError("Unable to read editor world after loading: " + map_package)

actors = []
actor_subsystem_class = getattr(unreal, "EditorActorSubsystem", None)
if actor_subsystem_class and callable(get_editor_subsystem):
    actor_subsystem = get_editor_subsystem(actor_subsystem_class)
    get_actors = getattr(actor_subsystem, "get_all_level_actors", None)
    if callable(get_actors):
        actors = list(get_actors())
if not actors:
    ell = getattr(unreal, "EditorLevelLibrary", None)
    get_actors = getattr(ell, "get_all_level_actors", None) if ell else None
    if callable(get_actors):
        actors = list(get_actors())

options = unreal.GLTFExportOptions()
for prop, value in {{
    "export_uniform_scale": 0.01,
    "export_cameras": False,
    "export_lights": False,
    "export_hidden_in_game": True,
    "export_source_model": False,
    "export_vertex_colors": False,
    "export_vertex_skin_weights": False,
}}.items():
    try:
        options.set_editor_property(prop, value)
    except Exception:
        pass

glb_output.parent.mkdir(parents=True, exist_ok=True)
errors = []
task = unreal.AssetExportTask()
task.set_editor_property("automated", True)
task.set_editor_property("errors", errors)
task.set_editor_property("filename", str(glb_output))
task.set_editor_property("ignore_object_list", [])
task.set_editor_property("object", world)
task.set_editor_property("options", options)
task.set_editor_property("prompt", False)
task.set_editor_property("replace_identical", True)
task.set_editor_property("selected", False)
task.set_editor_property("use_file_archive", False)
task.set_editor_property("write_empty_files", False)
exporter = None
try:
    exporter = unreal.GLTFLevelExporter()
    task.set_editor_property("exporter", exporter)
except Exception:
    pass
ok = bool(unreal.Exporter.run_asset_export_task(task))
payload = {{
    "schema": "mosim.unreal_level_gltf_export.v1",
    "ok": ok,
    "scene_source_id": scene_source_id,
    "map_package": map_package,
    "world_name": str(call_if_available(world, "get_path_name") or call_if_available(world, "get_name") or world),
    "actor_count": len(actors),
    "glb_output": str(glb_output),
    "glb_exists": glb_output.exists(),
    "glb_size_bytes": glb_output.stat().st_size if glb_output.exists() else 0,
    "exporter": str(exporter) if exporter else "",
    "messages": {{
        "errors": [str(x) for x in errors],
    }},
    "claim_boundary": claim_boundary,
}}
json_output.parent.mkdir(parents=True, exist_ok=True)
json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
if not ok or not glb_output.exists() or glb_output.stat().st_size <= 0:
    raise RuntimeError("GLTF level export failed: " + json.dumps(payload, ensure_ascii=False))
"""
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(source.strip() + "\n", encoding="utf-8")


def run_command(command: list[str], *, log_output: Path, timeout_seconds: float | None) -> int:
    log_output.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    with log_output.open("w", encoding="utf-8", errors="replace", newline="\n") as log_file:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        assert process.stdout is not None
        try:
            for line in process.stdout:
                log_file.write(line)
                log_file.flush()
                if timeout_seconds is not None and time.monotonic() - start > timeout_seconds:
                    process.kill()
                    process.wait(timeout=10)
                    return 124
            return process.wait()
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=10)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-source-id", default="local_factoryenvironmentcollect")
    parser.add_argument("--registry", type=Path, default=DEFAULT_SCENE_REGISTRY)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--engine-root", type=Path, default=None)
    parser.add_argument("--editor-cmd", type=Path, default=None)
    parser.add_argument("--timeout-seconds", type=float, default=900.0)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = read_json(project_path(args.registry))
    source = source_by_id(registry, args.scene_source_id)
    uproject_value = source.get("source_project") or source.get("uproject_path")
    if not uproject_value:
        raise ValueError(f"{args.scene_source_id} has no source_project/uproject_path")
    uproject_path = project_path(str(uproject_value))
    map_package = str(source.get("source_map_package") or source.get("renderer_map_package") or "")
    if not map_package:
        raise ValueError(f"{args.scene_source_id} has no source_map_package/renderer_map_package")

    output_root = project_path(args.output_root)
    glb_output = output_root / "assets" / f"{args.scene_source_id}_level.glb"
    json_output = output_root / "manifests" / "unreal_level_gltf_export.json"
    script_path = output_root / "tmp" / "unreal_level_gltf_export_batch.py"
    log_output = output_root / "logs" / "unreal_level_gltf_export.log"
    claim_boundary = (
        "UE official GLTFExporter level export only; no Gazebo/PX4/ROS/SLAM runtime "
        "success is implied by this asset export."
    )
    write_editor_export_script(
        script_path=script_path,
        map_package=map_package,
        glb_output=glb_output,
        json_output=json_output,
        scene_source_id=args.scene_source_id,
        claim_boundary=claim_boundary,
    )
    editor_cmd = resolve_editor_cmd(uproject_path, args.engine_root or ENGINE_ROOT_BY_VERSION.get("5.5"), args.editor_cmd)
    command = [
        str(editor_cmd),
        to_windows_path(uproject_path),
        map_package,
        "-run=pythonscript",
        f"-script={to_windows_path(script_path)}",
        "-nosplash",
        "-NoSound",
        "-stdout",
        "-FullStdOutLogOutput",
        "-unattended",
        "-EnablePlugins=GLTFExporter,EditorScriptingUtilities,PythonScriptPlugin",
    ]
    payload: dict[str, Any] = {
        "schema": "mosim.unreal_level_gltf_export_command.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scene_source_id": args.scene_source_id,
        "source_project": rel(uproject_path),
        "map_package": map_package,
        "editor_cmd": to_windows_path(editor_cmd),
        "batch_script": rel(script_path),
        "glb_output": rel(glb_output),
        "json_output": rel(json_output),
        "log_output": rel(log_output),
        "command": command,
        "dry_run": not args.run,
    }
    if not args.run:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    rc = run_command(command, log_output=log_output, timeout_seconds=args.timeout_seconds)
    payload["returncode"] = rc
    payload["log_tail"] = tail_lines(log_output, 80)
    if json_output.exists():
        payload["export_manifest"] = read_json(json_output)
        manifest = payload["export_manifest"]
        if (
            isinstance(manifest, dict)
            and manifest.get("ok")
            and manifest.get("glb_exists")
            and int(manifest.get("glb_size_bytes") or 0) > 0
            and rc != 0
        ):
            payload["returncode_note"] = (
                "Unreal commandlet exported a nonempty GLB and wrote ok=true, "
                "then returned nonzero during Python/Editor shutdown. Treat the "
                "asset export as usable but keep the log as a shutdown-crash warning."
            )
            rc = 0
            payload["returncode"] = rc
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
