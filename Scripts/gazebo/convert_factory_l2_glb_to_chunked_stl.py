#!/usr/bin/env python3
"""Convert the Factory UE GLB export into chunked STL meshes for Gazebo Classic.

Gazebo Classic / libsdformat can crash when asked to parse the full Factory
scene as one giant mesh. This helper keeps the UE GLTFExporter GLB as the
geometry source, then exports selected object batches as STL chunks through
Blender for a more stable static review world.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPORT_ROOT = ROOT / "Results/unreal_scene_mapping/factory_l2_static_import"
DEFAULT_BLENDER_EXE = Path(r"D:\Program Files\Blender Foundation\Blender 5.0\blender.exe")


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
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def write_blender_script(
    script_path: Path,
    *,
    source_glb: Path,
    chunk_dir: Path,
    report_path: Path,
    chunk_size: int,
    exclude_name_regex: list[str],
) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(
        f"""
import json
import re
from pathlib import Path
import bpy

source_glb = Path({str(source_glb)!r})
chunk_dir = Path({str(chunk_dir)!r})
report_path = Path({str(report_path)!r})
chunk_size = {chunk_size!r}
exclude_name_regex = {exclude_name_regex!r}
exclude_patterns = [re.compile(pattern) for pattern in exclude_name_regex]

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath=str(source_glb))

all_mesh_objects = sorted([obj for obj in bpy.context.scene.objects if obj.type == "MESH"], key=lambda obj: obj.name)
excluded_objects = [
    obj
    for obj in all_mesh_objects
    if any(pattern.search(obj.name) for pattern in exclude_patterns)
]
mesh_objects = [
    obj
    for obj in all_mesh_objects
    if obj not in excluded_objects
]
chunk_dir.mkdir(parents=True, exist_ok=True)
for old in chunk_dir.glob("factory_chunk_*.stl"):
    old.unlink()

chunks = []
for chunk_index, start in enumerate(range(0, len(mesh_objects), chunk_size)):
    group = mesh_objects[start:start + chunk_size]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in group:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = group[0] if group else None
    out = chunk_dir / f"factory_chunk_{{chunk_index:04d}}.stl"
    result = bpy.ops.wm.stl_export(
        filepath=str(out),
        export_selected_objects=True,
        apply_modifiers=True,
        ascii_format=False,
    )
    chunks.append({{
        "chunk_index": chunk_index,
        "object_count": len(group),
        "mesh_names_sample": [obj.name for obj in group[:8]],
        "path": str(out),
        "size_bytes": out.stat().st_size if out.exists() else 0,
        "result": [str(x) for x in result],
        "ok": out.exists() and out.stat().st_size > 0,
    }})

payload = {{
    "schema": "mosim.factory_l2_blender_chunked_stl_conversion.v1",
    "ok": bool(chunks) and all(chunk["ok"] for chunk in chunks),
    "source_glb": str(source_glb),
    "chunk_dir": str(chunk_dir),
    "chunk_size": chunk_size,
    "exclude_name_regex": exclude_name_regex,
    "excluded_mesh_object_count": len(excluded_objects),
    "excluded_mesh_names": [obj.name for obj in excluded_objects],
    "all_mesh_object_count": len(all_mesh_objects),
    "mesh_object_count": len(mesh_objects),
    "chunk_count": len(chunks),
    "total_chunk_size_bytes": sum(chunk["size_bytes"] for chunk in chunks),
    "chunks": chunks,
    "claim_boundary": "Chunked STL conversion only; geometry source remains the UE GLTFExporter level GLB.",
}}
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
if not payload["ok"]:
    raise RuntimeError("chunked STL conversion failed: " + json.dumps(payload, ensure_ascii=False))
""".strip()
        + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-root", type=Path, default=DEFAULT_EXPORT_ROOT)
    parser.add_argument("--blender-exe", type=Path, default=DEFAULT_BLENDER_EXE)
    parser.add_argument("--chunk-size", type=int, default=128)
    parser.add_argument(
        "--chunk-dir-name",
        default="chunked_stl",
        help="Subdirectory under assets/ for STL chunks. Use a different name for clean/audit runs.",
    )
    parser.add_argument(
        "--report-name",
        default="blender_chunked_stl_conversion.json",
        help="Manifest filename under manifests/.",
    )
    parser.add_argument(
        "--script-name",
        default="blender_convert_glb_to_chunked_stl.py",
        help="Generated Blender script filename under tmp/.",
    )
    parser.add_argument(
        "--log-name",
        default="blender_chunked_stl_conversion.log",
        help="Blender log filename under logs/.",
    )
    parser.add_argument(
        "--exclude-name-regex",
        action="append",
        default=[],
        help="Exclude mesh objects whose Blender object name matches this regex. Repeatable.",
    )
    parser.add_argument("--timeout-seconds", type=float, default=1800.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.chunk_size <= 0:
        raise ValueError("--chunk-size must be positive")
    export_root = project_path(args.export_root)
    export_manifest = read_json(export_root / "manifests" / "unreal_level_gltf_export.json")
    source_glb = Path(str(export_manifest["glb_output"]))
    if not source_glb.is_absolute():
        source_glb = ROOT / source_glb
    if not source_glb.exists() or source_glb.stat().st_size <= 0:
        raise FileNotFoundError(f"missing nonempty GLB: {source_glb}")
    blender_exe = Path(args.blender_exe)
    if not blender_exe.exists():
        raise FileNotFoundError(f"missing Blender executable: {blender_exe}")

    for pattern in args.exclude_name_regex:
        re.compile(pattern)

    chunk_dir = export_root / "assets" / args.chunk_dir_name
    report_path = export_root / "manifests" / args.report_name
    script_path = export_root / "tmp" / args.script_name
    log_path = export_root / "logs" / args.log_name
    write_blender_script(
        script_path,
        source_glb=source_glb,
        chunk_dir=chunk_dir,
        report_path=report_path,
        chunk_size=args.chunk_size,
        exclude_name_regex=list(args.exclude_name_regex),
    )

    command = [
        str(blender_exe),
        "--background",
        "--factory-startup",
        "--python",
        str(script_path),
    ]
    started = time.monotonic()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", errors="replace", newline="\n") as log_file:
        process = subprocess.run(
            command,
            cwd=ROOT,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            timeout=args.timeout_seconds,
            check=False,
        )
    report = read_json(report_path) if report_path.exists() else {}
    payload = {
        "schema": "mosim.factory_l2_blender_chunked_stl_conversion_command.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "returncode": process.returncode,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "command": command,
        "source_glb": rel(source_glb),
        "chunk_dir": rel(chunk_dir),
        "report_path": rel(report_path),
        "log_path": rel(log_path),
        "report": report,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if process.returncode == 0 and report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
