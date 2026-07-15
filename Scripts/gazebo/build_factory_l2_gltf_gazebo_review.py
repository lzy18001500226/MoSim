#!/usr/bin/env python3
"""Build a Gazebo review bundle from a Factory UE level GLB export.

The generated world references the exported GLB as a static visual/collision
mesh. It is a Scene Base review artifact only; planners must not consume this
mesh as a prior map.
"""

from __future__ import annotations

import argparse
import json
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPORT_ROOT = ROOT / "Results/unreal_scene_mapping/factory_l2_static_import"
DEFAULT_PROJECT_MODEL_ROOT = ROOT / "Config/gazebo/models"
DEFAULT_PROJECT_WORLD_ROOT = ROOT / "Config/gazebo/worlds"


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


def element(parent: ET.Element, tag: str, text: str | None = None, **attrs: str) -> ET.Element:
    child = ET.SubElement(parent, tag, attrs)
    if text is not None:
        child.text = text
    return child


def write_model_config(model_dir: Path, *, model_name: str) -> None:
    (model_dir / "model.config").write_text(
        f'<?xml version="1.0" ?><model><name>{model_name}</name><version>1.0</version>'
        '<sdf version="1.6">model.sdf</sdf></model>\n',
        encoding="utf-8",
    )


def write_model_sdf(model_dir: Path, *, model_name: str, mesh_uri: str, mesh_scale: str, minimal: bool = False) -> None:
    sdf = ET.Element("sdf", version="1.6")
    model = element(sdf, "model", name=model_name)
    element(model, "static", "true")
    link = element(model, "link", name="l" if minimal else "factory_level_link")
    for tag, name in (("visual", "v"), ("collision", "c")):
        item = element(link, tag, name=name if minimal else f"{tag}_mesh")
        geometry = element(item, "geometry")
        mesh = element(geometry, "mesh")
        element(mesh, "uri", mesh_uri)
        if not minimal or mesh_scale != "1 1 1":
            element(mesh, "scale", mesh_scale)
    ET.indent(sdf, space="  ")
    (model_dir / "model.sdf").write_text("<?xml version=\"1.0\" ?>\n" + ET.tostring(sdf, encoding="unicode") + "\n", encoding="utf-8")


def write_world_sdf(world_path: Path, *, model_names: list[str], world_name: str) -> None:
    sdf = ET.Element("sdf", version="1.6")
    world = element(sdf, "world", name=world_name)
    physics = element(world, "physics", name="default_physics", type="ode")
    element(physics, "max_step_size", "0.001")
    element(physics, "real_time_factor", "1.0")
    element(physics, "real_time_update_rate", "1000")
    scene = element(world, "scene")
    element(scene, "ambient", "0.45 0.45 0.45 1")
    element(scene, "background", "0.7 0.72 0.74 1")
    light = element(world, "light", name="sun", type="directional")
    element(light, "cast_shadows", "true")
    element(light, "pose", "0 0 60 0 0 0")
    element(light, "diffuse", "0.85 0.85 0.8 1")
    element(light, "specular", "0.2 0.2 0.2 1")
    element(light, "direction", "-0.45 0.2 -0.87")
    for model_name in model_names:
        include = element(world, "include")
        element(include, "uri", f"model://{model_name}")
    ET.indent(sdf, space="  ")
    world_path.parent.mkdir(parents=True, exist_ok=True)
    world_path.write_text("<?xml version=\"1.0\" ?>\n" + ET.tostring(sdf, encoding="unicode") + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-root", type=Path, default=DEFAULT_EXPORT_ROOT)
    parser.add_argument("--model-name", default="factoryenvironmentcollect_l2_static_glb")
    parser.add_argument("--world-name", default="factoryenvironmentcollect_l2_static_review")
    parser.add_argument("--mesh-scale", default="1 1 1")
    parser.add_argument(
        "--conversion-manifest",
        type=Path,
        default=None,
        help="Optional explicit Blender conversion manifest. Relative paths are resolved under MoSim.",
    )
    parser.add_argument(
        "--review-subdir",
        default="gazebo_review",
        help="Output subdirectory under export root for generated Gazebo review assets.",
    )
    parser.add_argument("--install-project-assets", action="store_true")
    parser.add_argument("--project-model-root", type=Path, default=DEFAULT_PROJECT_MODEL_ROOT)
    parser.add_argument("--project-world-root", type=Path, default=DEFAULT_PROJECT_WORLD_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    export_root = project_path(args.export_root)
    export_manifest = export_root / "manifests" / "unreal_level_gltf_export.json"
    if not export_manifest.exists():
        raise FileNotFoundError(f"missing UE GLB export manifest: {export_manifest}")
    ue_export = read_json(export_manifest)
    if not ue_export.get("ok"):
        raise RuntimeError(f"UE GLB export did not pass: {export_manifest}")
    source_glb = Path(str(ue_export["glb_output"]))
    if not source_glb.is_absolute():
        source_glb = ROOT / source_glb
    if not source_glb.exists() or source_glb.stat().st_size <= 0:
        raise FileNotFoundError(f"missing nonempty GLB: {source_glb}")
    conversion_manifest_path = (
        project_path(args.conversion_manifest)
        if args.conversion_manifest is not None
        else export_root / "manifests" / "blender_chunked_stl_conversion.json"
    )
    conversion_manifest: dict[str, Any] = {}
    source_mesh = source_glb
    source_mesh_kind = "glb"
    chunk_source_paths: list[Path] = []
    if conversion_manifest_path.exists():
        conversion_manifest = read_json(conversion_manifest_path)
        chunks = conversion_manifest.get("chunks", [])
        if conversion_manifest.get("ok") and isinstance(chunks, list) and chunks:
            for chunk in chunks:
                if not isinstance(chunk, dict):
                    continue
                chunk_path = Path(str(chunk.get("path") or ""))
                if chunk_path and not chunk_path.is_absolute():
                    chunk_path = ROOT / chunk_path
                if chunk_path.exists() and chunk_path.stat().st_size > 0:
                    chunk_source_paths.append(chunk_path)
            if len(chunk_source_paths) == len(chunks):
                source_mesh_kind = "chunked_stl"
        if not chunk_source_paths:
            single_stl_manifest_path = export_root / "manifests" / "blender_stl_conversion.json"
            if single_stl_manifest_path.exists():
                conversion_manifest_path = single_stl_manifest_path
                conversion_manifest = read_json(conversion_manifest_path)
                converted_mesh = Path(str(conversion_manifest.get("output_mesh", "")))
                if converted_mesh and not converted_mesh.is_absolute():
                    converted_mesh = ROOT / converted_mesh
                if conversion_manifest.get("ok") and converted_mesh.exists() and converted_mesh.stat().st_size > 0:
                    source_mesh = converted_mesh
                    source_mesh_kind = str(conversion_manifest.get("format") or converted_mesh.suffix.lstrip("."))
    else:
        obj_conversion_manifest_path = export_root / "manifests" / "blender_obj_conversion.json"
        if obj_conversion_manifest_path.exists():
            conversion_manifest_path = obj_conversion_manifest_path
            conversion_manifest = read_json(conversion_manifest_path)
            converted_obj = Path(str(conversion_manifest.get("output_mesh") or conversion_manifest.get("output_obj") or ""))
            if converted_obj and not converted_obj.is_absolute():
                converted_obj = ROOT / converted_obj
            if conversion_manifest.get("ok") and converted_obj.exists() and converted_obj.stat().st_size > 0:
                source_mesh = converted_obj
                source_mesh_kind = str(conversion_manifest.get("format") or "obj")

    review_root = export_root / args.review_subdir
    models_root = review_root / "models"
    if models_root.exists():
        shutil.rmtree(models_root)
    models_root.mkdir(parents=True, exist_ok=True)
    model_dirs: list[Path] = []
    model_names: list[str] = []
    if chunk_source_paths:
        for index, chunk_source in enumerate(chunk_source_paths):
            chunk_model_name = f"factory_chunk_{index:04d}"
            model_dir = models_root / chunk_model_name
            mesh_dir = model_dir / "meshes"
            mesh_dir.mkdir(parents=True, exist_ok=True)
            mesh_path = mesh_dir / chunk_source.name
            shutil.copy2(chunk_source, mesh_path)
            write_model_config(model_dir, model_name=chunk_model_name)
            write_model_sdf(
                model_dir,
                model_name=chunk_model_name,
                mesh_uri=f"model://{chunk_model_name}/meshes/{mesh_path.name}",
                mesh_scale=args.mesh_scale,
                minimal=True,
            )
            model_dirs.append(model_dir)
            model_names.append(chunk_model_name)
    else:
        model_dir = models_root / args.model_name
        mesh_dir = model_dir / "meshes"
        mesh_dir.mkdir(parents=True, exist_ok=True)
        mesh_path = mesh_dir / f"factory_level.{source_mesh.suffix.lstrip('.')}"
        shutil.copy2(source_mesh, mesh_path)
        write_model_config(model_dir, model_name=args.model_name)
        write_model_sdf(
            model_dir,
            model_name=args.model_name,
            mesh_uri=f"model://{args.model_name}/meshes/{mesh_path.name}",
            mesh_scale=args.mesh_scale,
        )
        model_dirs.append(model_dir)
        model_names.append(args.model_name)

    world_path = review_root / "worlds" / f"{args.world_name}.sdf"
    write_world_sdf(world_path, model_names=model_names, world_name=args.world_name)

    installed: dict[str, str] = {}
    if args.install_project_assets:
        project_model_dir = project_path(args.project_model_root) / args.model_name
        if project_model_dir.exists():
            shutil.rmtree(project_model_dir)
        project_model_dir.mkdir(parents=True, exist_ok=True)
        for model_dir in model_dirs:
            shutil.copytree(model_dir, project_model_dir / model_dir.name)
        project_world_path = project_path(args.project_world_root) / f"{args.world_name}.sdf"
        project_world_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(world_path, project_world_path)
        installed = {
            "project_model_dir": rel(project_model_dir),
            "project_world_path": rel(project_world_path),
        }

    manifest = {
        "schema": "mosim.factory_l2_gltf_gazebo_classic_review.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "factory_l2_import_review_required",
        "scene_source_id": ue_export.get("scene_source_id"),
        "map_package": ue_export.get("map_package"),
        "source_glb": rel(source_glb),
        "source_glb_size_bytes": source_glb.stat().st_size,
        "review_mesh_source": rel(chunk_source_paths[0].parent) if chunk_source_paths else rel(source_mesh),
        "review_mesh_kind": source_mesh_kind,
        "review_mesh_size_bytes": sum(path.stat().st_size for path in chunk_source_paths) if chunk_source_paths else source_mesh.stat().st_size,
        "review_mesh_chunk_count": len(model_dirs),
        "conversion_manifest": rel(conversion_manifest_path) if conversion_manifest else "",
        "review_model_dir": rel(models_root),
        "review_model_count": len(model_dirs),
        "review_world_path": rel(world_path),
        "world_name": args.world_name,
        "model_name": args.model_name,
        "world_model_names": model_names,
        "mesh_scale": args.mesh_scale,
        "installed_project_assets": installed,
        "gazebo_open_command_wsl": (
            f"cd /mnt/c/Users/HP/Desktop/MoSim && "
            f"GAZEBO_MODEL_PATH=\"$PWD/{rel(review_root / 'models')}:$GAZEBO_MODEL_PATH\" "
            f"gazebo --verbose \"{rel(world_path)}\""
        ),
        "gazebo_sdf_check_command_wsl": (
            f"cd /mnt/c/Users/HP/Desktop/MoSim && "
            f"GAZEBO_MODEL_PATH=\"$PWD/{rel(review_root / 'models')}:$GAZEBO_MODEL_PATH\" "
            f"gz sdf -v 1.6 -k \"{rel(world_path)}\""
        ),
        "claim_boundary": [
            "Gazebo-only static physical-map review artifact.",
            "Uses UE GLTFExporter level GLB as source mesh; not generated from hand-built proxy geometry.",
            "Gazebo Classic review may use a Blender mesh-format conversion of that same GLB for simulator compatibility.",
            "This is not ROS/PX4/SLAM/planner/runtime success evidence.",
            "Planner_prior_map_access is forbidden; this mesh is a simulation world and validation/review oracle only.",
            "Generated for Gazebo Classic 11 / SDF 1.6, matching the current ROS1 runtime lane.",
        ],
        "known_review_risks": [
            "Mesh collision fidelity in Gazebo depends on simulator mesh-collision support and asset complexity.",
            "Visual material quality is low priority for first review.",
            "The converted review mesh is large because it preserves the exported Factory geometry for first physical-map review.",
        ],
    }
    manifest_path = review_root / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path = review_root / "SUMMARY.md"
    summary_path.write_text(
        "\n".join(
            [
                "# Factory L2 Static Gazebo Review",
                "",
                f"- status: `{manifest['status']}`",
                f"- source GLB: `{manifest['source_glb']}`",
                f"- review mesh: `{manifest['review_mesh_source']}` ({manifest['review_mesh_kind']})",
                f"- review world: `{manifest['review_world_path']}`",
                f"- model: `{manifest['review_model_dir']}`",
                "- claim: Gazebo-only static physical-map review; no ROS/PX4/SLAM success claim.",
                "- planner prior map access: forbidden.",
                "",
                "Open command in Ubuntu-20.04:",
                "",
                "```bash",
                manifest["gazebo_open_command_wsl"],
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
