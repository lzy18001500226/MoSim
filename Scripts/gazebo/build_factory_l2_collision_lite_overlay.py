#!/usr/bin/env python3
"""Build a decimated Factory L2 model overlay for bounded runtime experiments.

The base Factory review bundle keeps the same high-triangle STL under both
``visual`` and ``collision``. This helper leaves that source bundle untouched,
uses Blender to decimate the mesh once, and emits same-named Gazebo models that
can expose it as collision-only or as matching collision and visual geometry.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_MODEL_ROOT = (
    ROOT
    / "Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/models"
)
DEFAULT_BLENDER_EXE = Path(r"D:\Program Files\Blender Foundation\Blender 5.0\blender.exe")


def project_path(value: str | Path) -> Path:
    path = Path(value)
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"path must remain below MoSim: {value}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def read_binary_stl_triangle_count(path: Path) -> int:
    with path.open("rb") as handle:
        header = handle.read(84)
    if len(header) != 84:
        raise ValueError(f"invalid binary STL header: {path}")
    return int.from_bytes(header[80:84], byteorder="little", signed=False)


def collect_models(source_root: Path, requested: list[str]) -> list[dict[str, Any]]:
    requested_set = set(requested)
    if len(requested_set) != len(requested):
        raise ValueError("--model may not repeat a Factory chunk name")
    source_models: list[dict[str, Any]] = []
    for model_dir in sorted(source_root.iterdir()):
        if not model_dir.is_dir() or not re.fullmatch(r"factory_chunk_\d{4}", model_dir.name):
            continue
        if requested_set and model_dir.name not in requested_set:
            continue
        source_sdf = model_dir / "model.sdf"
        meshes = sorted((model_dir / "meshes").glob("*.stl"))
        if not source_sdf.is_file() or len(meshes) != 1:
            raise ValueError(f"unexpected Factory chunk layout: {model_dir}")
        source_models.append(
            {
                "name": model_dir.name,
                "source_mesh": meshes[0],
                "source_triangles": read_binary_stl_triangle_count(meshes[0]),
            }
        )
    missing = requested_set - {entry["name"] for entry in source_models}
    if missing:
        raise ValueError(f"requested Factory chunk is missing: {sorted(missing)}")
    if not source_models:
        raise ValueError(f"no Factory chunks found below {source_root}")
    return source_models


def write_blender_job(script_path: Path, job_path: Path) -> None:
    script_path.write_text(
        """import bpy
import json
from pathlib import Path

job = json.loads(Path(__file__).with_name('blender_decimate_collision_job.json').read_text(encoding='utf-8'))
report = []
for entry in job['entries']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=entry['source_mesh'])
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not meshes:
        raise RuntimeError('STL import created no mesh: ' + entry['source_mesh'])
    for obj in meshes:
        bpy.context.view_layer.objects.active = obj
        modifier = obj.modifiers.new(name='collision_decimate', type='DECIMATE')
        modifier.decimate_type = 'COLLAPSE'
        modifier.ratio = job['ratio']
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    output = Path(entry['output_mesh'])
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.stl_export(
        filepath=str(output),
        export_selected_objects=True,
        apply_modifiers=True,
        ascii_format=False,
    )
    report.append({
        'name': entry['name'],
        'source_triangles': entry['source_triangles'],
        'blender_output_triangles': sum(len(obj.data.polygons) for obj in meshes),
    })
Path(__file__).with_name('blender_decimate_collision_report.json').write_text(
    json.dumps({'entries': report}, indent=2, sort_keys=True) + '\\n', encoding='utf-8'
)
""",
        encoding="utf-8",
    )


def write_model_files(
    model_dir: Path,
    model_name: str,
    collision_mesh_name: str,
    *,
    include_visual: bool,
) -> None:
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "model.config").write_text(
        "<?xml version=\"1.0\" ?><model>"
        f"<name>{model_name}</name><version>1.0</version>"
        "<sdf version=\"1.6\">model.sdf</sdf></model>\n",
        encoding="utf-8",
    )
    sdf = ET.Element("sdf", version="1.6")
    model = ET.SubElement(sdf, "model", name=model_name)
    ET.SubElement(model, "static").text = "true"
    link = ET.SubElement(model, "link", name="collision_lite_link")
    if include_visual:
        visual = ET.SubElement(link, "visual", name="visual_lite")
        visual_geometry = ET.SubElement(visual, "geometry")
        visual_mesh = ET.SubElement(visual_geometry, "mesh")
        ET.SubElement(visual_mesh, "uri").text = f"model://{model_name}/meshes/{collision_mesh_name}"
    collision = ET.SubElement(link, "collision", name="collision_lite")
    geometry = ET.SubElement(collision, "geometry")
    mesh = ET.SubElement(geometry, "mesh")
    ET.SubElement(mesh, "uri").text = f"model://{model_name}/meshes/{collision_mesh_name}"
    ET.indent(sdf, space="  ")
    (model_dir / "model.sdf").write_text(
        "<?xml version=\"1.0\" ?>\n" + ET.tostring(sdf, encoding="unicode") + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-model-root", type=Path, default=DEFAULT_SOURCE_MODEL_ROOT)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--ratio", type=float, default=0.10)
    parser.add_argument(
        "--include-visual",
        action="store_true",
        help="Expose the decimated mesh as a Gazebo visual as well as collision geometry.",
    )
    parser.add_argument("--blender-exe", type=Path, default=DEFAULT_BLENDER_EXE)
    parser.add_argument("--timeout-seconds", type=float, default=3600.0)
    parser.add_argument(
        "--model",
        action="append",
        default=[],
        help="Build only this Factory chunk. Intended for a converter smoke check.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 0.0 < args.ratio < 1.0:
        raise ValueError("--ratio must be in (0, 1)")
    if args.timeout_seconds <= 0:
        raise ValueError("--timeout-seconds must be positive")

    source_root = project_path(args.source_model_root)
    output_root = project_path(args.output_root)
    blender_exe = Path(args.blender_exe)
    if not source_root.is_dir():
        raise FileNotFoundError(f"source model root is missing: {source_root}")
    if not blender_exe.is_file():
        raise FileNotFoundError(f"Blender executable is missing: {blender_exe}")
    if output_root.exists() and any(output_root.iterdir()):
        raise FileExistsError(f"refusing to overwrite nonempty output root: {output_root}")
    output_root.mkdir(parents=True, exist_ok=True)

    source_models = collect_models(source_root, list(args.model))
    ratio_tag = f"{args.ratio * 100:g}".replace(".", "_") + "pct"
    models_root = output_root / "models"
    entries: list[dict[str, Any]] = []
    for entry in source_models:
        collision_name = f"{entry['name']}_collision_{ratio_tag}.stl"
        collision_path = models_root / entry["name"] / "meshes" / collision_name
        entries.append(
            {
                "name": entry["name"],
                "source_mesh": str(entry["source_mesh"]),
                "source_triangles": entry["source_triangles"],
                "output_mesh": str(collision_path),
                "collision_name": collision_name,
            }
        )

    job_path = output_root / "blender_decimate_collision_job.json"
    job_path.write_text(json.dumps({"ratio": args.ratio, "entries": entries}, indent=2) + "\n", encoding="utf-8")
    blender_script = output_root / "blender_decimate_collision_meshes.py"
    write_blender_job(blender_script, job_path)
    log_path = output_root / "blender_decimate_collision.log"
    command = [
        str(blender_exe),
        "--background",
        "--factory-startup",
        "--python",
        str(blender_script),
    ]
    with log_path.open("w", encoding="utf-8", errors="replace", newline="\n") as log_file:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            timeout=args.timeout_seconds,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(f"Blender collision decimation failed; see {log_path}")

    records: list[dict[str, Any]] = []
    for entry in entries:
        collision_path = Path(entry["output_mesh"])
        if not collision_path.is_file() or collision_path.stat().st_size <= 84:
            raise RuntimeError(f"missing collision mesh output: {collision_path}")
        output_triangles = read_binary_stl_triangle_count(collision_path)
        if output_triangles <= 0 or output_triangles > entry["source_triangles"]:
            raise RuntimeError(f"invalid collision triangle count for {entry['name']}: {output_triangles}")
        write_model_files(
            collision_path.parents[1],
            entry["name"],
            entry["collision_name"],
            include_visual=args.include_visual,
        )
        records.append(
            {
                "name": entry["name"],
                "source_mesh": rel(Path(entry["source_mesh"])),
                "collision_mesh": rel(collision_path),
                "source_triangles": entry["source_triangles"],
                "collision_triangles": output_triangles,
                "collision_ratio": round(output_triangles / entry["source_triangles"], 6),
            }
        )

    source_triangles = sum(record["source_triangles"] for record in records)
    collision_triangles = sum(record["collision_triangles"] for record in records)
    manifest = {
        "schema": "mosim.factory_l2_collision_lite_overlay.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_model_root": rel(source_root),
        "overlay_model_root": rel(models_root),
        "decimation_ratio_requested": args.ratio,
        "source_triangle_count": source_triangles,
        "collision_triangle_count": collision_triangles,
        "collision_triangle_ratio": round(collision_triangles / source_triangles, 6),
        "visual_geometry": "matching_decimated_mesh" if args.include_visual else "none",
        "model_count": len(records),
        "models": records,
        "blender_command": command,
        "blender_log": rel(log_path),
        "claim_boundary": [
            "The source Factory world and source meshes are unchanged.",
            (
                "This overlay contains the decimated mesh as both collision and render geometry."
                if args.include_visual
                else "This overlay contains collision geometry only; Gazebo GUI visual fidelity is intentionally out of scope."
            ),
            "Any runtime point clouds and occupancy grids reflect the decimated geometry.",
            "A runtime using this overlay is a real-time performance/display experiment, not full-fidelity collision acceptance.",
        ],
    }
    manifest_path = output_root / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
