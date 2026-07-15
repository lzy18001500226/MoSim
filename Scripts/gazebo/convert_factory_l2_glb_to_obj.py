#!/usr/bin/env python3
"""Convert the Factory UE GLB export to a Gazebo Classic friendly mesh.

The source geometry remains the UE GLTFExporter level GLB. This helper only
changes the interchange format through Blender so Gazebo Classic 11 does not
have to parse the original GLB directly.
"""

from __future__ import annotations

import argparse
import json
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


def write_blender_script(script_path: Path, *, source_glb: Path, output_mesh: Path, report_path: Path, fmt: str) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(
        f"""
import json
from pathlib import Path
import bpy

source_glb = Path({str(source_glb)!r})
output_mesh = Path({str(output_mesh)!r})
report_path = Path({str(report_path)!r})
fmt = {fmt!r}

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath=str(source_glb))

mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
for obj in mesh_objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = mesh_objects[0] if mesh_objects else None

output_mesh.parent.mkdir(parents=True, exist_ok=True)
if fmt == "obj":
    result = bpy.ops.wm.obj_export(
        filepath=str(output_mesh),
        export_selected_objects=False,
        apply_modifiers=True,
        export_triangulated_mesh=True,
        export_materials=True,
    )
elif fmt == "stl":
    result = bpy.ops.wm.stl_export(
        filepath=str(output_mesh),
        export_selected_objects=False,
        apply_modifiers=True,
        ascii_format=False,
    )
else:
    raise ValueError("unsupported format: " + fmt)

payload = {{
    "schema": "mosim.factory_l2_blender_mesh_conversion.v1",
    "format": fmt,
    "ok": output_mesh.exists() and output_mesh.stat().st_size > 0,
    "source_glb": str(source_glb),
    "output_mesh": str(output_mesh),
    "output_mesh_size_bytes": output_mesh.stat().st_size if output_mesh.exists() else 0,
    "mesh_object_count": len(mesh_objects),
    "blender_result": [str(x) for x in result],
    "claim_boundary": "Format conversion only; geometry source remains the UE GLTFExporter level GLB.",
}}
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
if not payload["ok"]:
    raise RuntimeError("mesh conversion failed: " + json.dumps(payload, ensure_ascii=False))
""".strip()
        + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-root", type=Path, default=DEFAULT_EXPORT_ROOT)
    parser.add_argument("--blender-exe", type=Path, default=DEFAULT_BLENDER_EXE)
    parser.add_argument("--format", choices=("obj", "stl"), default="stl")
    parser.add_argument("--timeout-seconds", type=float, default=900.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
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

    output_mesh = export_root / "assets" / f"local_factoryenvironmentcollect_level.{args.format}"
    report_path = export_root / "manifests" / f"blender_{args.format}_conversion.json"
    script_path = export_root / "tmp" / f"blender_convert_glb_to_{args.format}.py"
    log_path = export_root / "logs" / f"blender_{args.format}_conversion.log"
    write_blender_script(
        script_path,
        source_glb=source_glb,
        output_mesh=output_mesh,
        report_path=report_path,
        fmt=args.format,
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
        "schema": "mosim.factory_l2_blender_mesh_conversion_command.v1",
        "format": args.format,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "returncode": process.returncode,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "command": command,
        "source_glb": rel(source_glb),
        "output_mesh": rel(output_mesh),
        "report_path": rel(report_path),
        "log_path": rel(log_path),
        "report": report,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if process.returncode == 0 and report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
