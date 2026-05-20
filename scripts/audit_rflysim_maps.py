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


def extract_refs(path: Path, limit: int = 80) -> list[str]:
    refs: set[str] = set()
    data = path.read_bytes()
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


def audit(rflysim_project: Path) -> dict:
    content = rflysim_project / "Content"
    uproject = rflysim_project / "RflySim3D.uproject"
    descriptor = read_json(uproject)
    plugins = descriptor.get("Plugins", [])

    maps = []
    for path in sorted(content.rglob("*.umap")):
        rel = path.relative_to(content).as_posix()
        refs = extract_refs(path)
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
    for suffix in ("*.fbx", "*.obj", "*.dae", "*.stl", "*.ply", "*.glb", "*.gltf"):
        loose_meshes.extend(path.relative_to(content).as_posix() for path in content.rglob(suffix))

    return {
        "rflysim_project": str(rflysim_project),
        "engine_association": descriptor.get("EngineAssociation"),
        "module_names": [module.get("Name") for module in descriptor.get("Modules", [])],
        "enabled_plugins": [plugin.get("Name") for plugin in plugins if plugin.get("Enabled")],
        "map_count": len(maps),
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
        f"- Loose mesh count: `{data.get('loose_mesh_count')}`",
        f"- Conclusion: {data['direct_use_conclusion']}",
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
    args = parser.parse_args()

    if not args.rflysim_project.exists():
        raise FileNotFoundError(args.rflysim_project)

    data = audit(args.rflysim_project)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(data, args.md_output)
    print(f"[OK] wrote {args.json_output}")
    print(f"[OK] wrote {args.md_output}")
    print(data["direct_use_conclusion"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
