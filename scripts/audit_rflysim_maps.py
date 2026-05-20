#!/usr/bin/env python3
"""Audit local RflySim3D maps for UE5 migration planning.

This script is read-only for the RflySim installation. It summarizes map files,
basic dependencies encoded in .umap byte strings, plugin/version requirements,
and likely migration risk. It intentionally does not copy assets.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RFLYSIM = Path("/mnt/d/PX4PSP/RflySim3D/RflySim3D")
DEFAULT_JSON = ROOT / "results" / "rflysim" / "rflysim_map_audit.json"
DEFAULT_MD = ROOT / "results" / "rflysim" / "rflysim_map_audit.md"
DEFAULT_REF_SCAN_MB = 8

REF_RE = re.compile(
    rb"/Game/[A-Za-z0-9_./\-\x80-\xff]+"
    rb"|/Script/[A-Za-z0-9_./\-\x80-\xff]+"
    rb"|/Rfly3DSimPlugin/[A-Za-z0-9_./\-\x80-\xff]+"
    rb"|/CesiumForUnreal/[A-Za-z0-9_./\-\x80-\xff]+"
    rb"|/TwinmotionToUnrealContent/[A-Za-z0-9_./\-\x80-\xff]+"
)


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def extract_refs(path: Path, limit: int = 80, scan_bytes: int | None = None) -> list[str]:
    refs: set[str] = set()
    if scan_bytes is None:
        data = path.read_bytes()
    else:
        with path.open("rb") as handle:
            data = handle.read(scan_bytes)
    for match in REF_RE.findall(data):
        text = match.decode("utf-8", errors="ignore").strip("\x00\r\n\t ")
        if text:
            refs.add(text)
    return sorted(refs)[:limit]


def classify_map(rel: str, refs: list[str]) -> tuple[str, str]:
    ref_text = "\n".join(refs)
    if "/Script/CesiumRuntime" in ref_text or "/CesiumForUnreal/" in ref_text:
        return "P2", "Cesium/geospatial dependency"
    if rel.startswith(("OldFactory/", "ModularNeighborhood/", "Grasslands/", "Vision/")):
        return "P0", "matches target demo scenes"
    if rel.startswith(("RobotMissionChallenge/", "MountainTerrain/", "ExhibitionHall/")):
        return "P1", "useful scene family"
    if rel.startswith(("MatchScene", "SimulationScenario/", "CameraRoom/")):
        return "P1", "challenge/indoor candidate"
    return "P2", "needs manual review"


def audit(
    rflysim_project: Path,
    ref_scan_mb: int = DEFAULT_REF_SCAN_MB,
    scan_loose_meshes: bool = False,
) -> dict:
    content = rflysim_project / "Content"
    uproject = rflysim_project / "RflySim3D.uproject"
    descriptor = read_json(uproject)
    plugins = descriptor.get("Plugins", [])
    project_source = rflysim_project / "Source"
    project_binaries = rflysim_project / "Binaries"
    plugin_source_files = list((rflysim_project / "Plugins").glob("*/Source/**/*.Build.cs"))
    plugin_binary_files = list((rflysim_project / "Plugins").glob("*/Binaries/**/*.dll"))
    runtime_exe = project_binaries / "Win64" / "RflySim3D.exe"
    project_modules = [module.get("Name") for module in descriptor.get("Modules", []) if module.get("Name")]
    project_module_status = []
    for module_name in project_modules:
        project_module_status.append(
            {
                "module": module_name,
                "source_build_cs": str(project_source / module_name / f"{module_name}.Build.cs"),
                "has_source_build_cs": (project_source / module_name / f"{module_name}.Build.cs").exists(),
                "win64_dll": str(project_binaries / "Win64" / f"{module_name}.dll"),
                "has_win64_dll": (project_binaries / "Win64" / f"{module_name}.dll").exists(),
            }
        )

    plugin_status = []
    for plugin_descriptor in sorted((rflysim_project / "Plugins").glob("*/*.uplugin")):
        plugin_root = plugin_descriptor.parent
        plugin_data = read_json(plugin_descriptor)
        modules = [module.get("Name") for module in plugin_data.get("Modules", []) if module.get("Name")]
        module_status = []
        for module_name in modules:
            module_status.append(
                {
                    "module": module_name,
                    "source_build_cs": str(plugin_root / "Source" / module_name / f"{module_name}.Build.cs"),
                    "has_source_build_cs": (plugin_root / "Source" / module_name / f"{module_name}.Build.cs").exists(),
                    "win64_dll": str(plugin_root / "Binaries" / "Win64" / f"UE4Editor-{module_name}.dll"),
                    "has_win64_dll": (
                        plugin_root / "Binaries" / "Win64" / f"UE4Editor-{module_name}.dll"
                    ).exists(),
                }
            )
        plugin_status.append(
            {
                "plugin": plugin_data.get("FriendlyName") or plugin_descriptor.stem,
                "descriptor": str(plugin_descriptor),
                "engine_version": plugin_data.get("EngineVersion"),
                "can_contain_content": plugin_data.get("CanContainContent"),
                "modules": module_status,
            }
        )

    if plugin_source_files or plugin_binary_files:
        editor_source_conclusion = (
            "Potential editor-source candidate: plugin source or plugin binaries were found. "
            "Open only a scratch copy and verify manually."
        )
    elif runtime_exe.exists() and not project_source.exists():
        editor_source_conclusion = (
            "Packaged/runtime install: RflySim3D.exe exists, but editable project/plugin source "
            "and plugin binaries are not present. Do not open this .uproject as a UE Editor "
            "source project; use the runtime as reference and rebuild scenes in the project-owned UE5 renderer."
        )
    else:
        editor_source_conclusion = (
            "Editor-source status is unclear. Inspect Source/, Plugins/*/Source, and "
            "Plugins/*/Binaries before opening in Unreal Editor."
        )

    maps = []
    scan_bytes = None if ref_scan_mb <= 0 else ref_scan_mb * 1024 * 1024
    for path in sorted(content.rglob("*.umap")):
        rel = path.relative_to(content).as_posix()
        refs = extract_refs(path, scan_bytes=scan_bytes)
        priority, reason = classify_map(rel, refs)
        maps.append(
            {
                "relative_path": rel,
                "size_bytes": path.stat().st_size,
                "priority": priority,
                "priority_reason": reason,
                "ref_count_sampled": len(refs),
                "reference_sample": refs[:16],
            }
        )

    loose_meshes = []
    loose_mesh_scan_status = "skipped"
    if scan_loose_meshes:
        suffixes = {".fbx", ".obj", ".dae", ".stl", ".ply", ".glb", ".gltf"}
        loose_meshes = [
            path.relative_to(content).as_posix()
            for path in content.rglob("*")
            if path.is_file() and path.suffix.lower() in suffixes
        ]
        loose_mesh_scan_status = "scanned"

    return {
        "rflysim_project": str(rflysim_project),
        "engine_association": descriptor.get("EngineAssociation"),
        "module_names": [module.get("Name") for module in descriptor.get("Modules", [])],
        "enabled_plugins": [plugin.get("Name") for plugin in plugins if plugin.get("Enabled")],
        "has_project_source_dir": project_source.exists(),
        "has_project_runtime_exe": runtime_exe.exists(),
        "project_module_status": project_module_status,
        "plugin_status": plugin_status,
        "plugin_source_file_count": len(plugin_source_files),
        "plugin_binary_file_count": len(plugin_binary_files),
        "editor_source_conclusion": editor_source_conclusion,
        "reference_scan_mb": ref_scan_mb,
        "map_count": len(maps),
        "loose_mesh_scan_status": loose_mesh_scan_status,
        "loose_mesh_count": len(loose_meshes),
        "loose_mesh_sample": sorted(loose_meshes)[:40],
        "direct_use_conclusion": (
            "Not drop-in for UE5.7: RflySim maps are UE4.27 .umap/.uasset assets "
            "with project/plugin dependencies. Use as migration source only."
        ),
        "maps": maps,
    }


def write_markdown(data: dict, path: Path) -> None:
    lines = [
        "# RflySim Map Audit",
        "",
        f"- Project: `{data['rflysim_project']}`",
        f"- EngineAssociation: `{data.get('engine_association')}`",
        f"- Map count: `{data.get('map_count')}`",
        f"- Loose mesh scan: `{data.get('loose_mesh_scan_status')}`",
        f"- Loose mesh count: `{data.get('loose_mesh_count')}`",
        f"- Conclusion: {data['direct_use_conclusion']}",
        f"- Editor source conclusion: {data['editor_source_conclusion']}",
        f"- Project source dir: `{data.get('has_project_source_dir')}`",
        f"- Runtime executable: `{data.get('has_project_runtime_exe')}`",
        f"- Plugin source files: `{data.get('plugin_source_file_count')}`",
        f"- Plugin binary files: `{data.get('plugin_binary_file_count')}`",
        f"- Reference scan MB per map: `{data.get('reference_scan_mb')}`",
        "",
        "## Project Modules",
        "",
        "| Module | Source Build.cs | Win64 DLL |",
        "| --- | --- | --- |",
    ]
    for item in data.get("project_module_status", []):
        lines.append(
            f"| `{item['module']}` | `{item['has_source_build_cs']}` | `{item['has_win64_dll']}` |"
        )

    lines += [
        "",
        "## Plugin Module Availability",
        "",
        "| Plugin | Engine | Content | Modules | Missing Source/DLL? |",
        "| --- | --- | --- | --- | --- |",
    ]
    for plugin in data.get("plugin_status", []):
        modules = ", ".join(f"`{module['module']}`" for module in plugin.get("modules", [])) or "`none`"
        missing = []
        for module in plugin.get("modules", []):
            if not module.get("has_source_build_cs") and not module.get("has_win64_dll"):
                missing.append(module["module"])
        lines.append(
            f"| `{plugin['plugin']}` | `{plugin.get('engine_version')}` | "
            f"`{plugin.get('can_contain_content')}` | {modules} | "
            f"{', '.join(f'`{name}`' for name in missing) if missing else '`none`'} |"
        )

    lines += [
        "",
        "## Enabled Plugins",
        "",
    ]
    for name in data.get("enabled_plugins", []):
        lines.append(f"- `{name}`")
    lines += [
        "",
        "## Map Candidates",
        "",
        "| Priority | Map | Size KB | Reason | Reference sample |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for item in data["maps"]:
        sample = "<br>".join(f"`{ref}`" for ref in item["reference_sample"][:4])
        lines.append(
            f"| {item['priority']} | `{item['relative_path']}` | "
            f"{item['size_bytes'] / 1024:.1f} | {item['priority_reason']} | {sample} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rflysim-project", type=Path, default=DEFAULT_RFLYSIM)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-output", type=Path, default=DEFAULT_MD)
    parser.add_argument(
        "--ref-scan-mb",
        type=int,
        default=DEFAULT_REF_SCAN_MB,
        help="Maximum MB to scan per .umap for dependency strings; <=0 scans full files.",
    )
    parser.add_argument(
        "--scan-loose-meshes",
        action="store_true",
        help="Also scan Content recursively for loose mesh formats. Slower on RflySim installs.",
    )
    args = parser.parse_args()

    if not args.rflysim_project.exists():
        raise FileNotFoundError(args.rflysim_project)

    data = audit(
        args.rflysim_project,
        ref_scan_mb=args.ref_scan_mb,
        scan_loose_meshes=args.scan_loose_meshes,
    )
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(data, args.md_output)
    print(f"[OK] wrote {args.json_output}")
    print(f"[OK] wrote {args.md_output}")
    print(data["direct_use_conclusion"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
