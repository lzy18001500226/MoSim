#!/usr/bin/env python3
"""Create a migration checklist for one audited RflySim scene.

The output is a small plan for manual/UE-editor work. It never copies RflySim
assets and never modifies an external RflySim installation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = (
    ROOT
    / "unreal"
    / "MworksUnrealRenderer"
    / "Content"
    / "MworksData"
    / "rflysim_scene_registry.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "results" / "rflysim"


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def game_root(ref: str) -> str | None:
    if not ref.startswith("/Game/"):
        return None
    parts = ref.split("/")
    if len(parts) < 3 or not parts[2]:
        return None
    return f"/Game/{parts[2]}"


def content_path_for_game_root(source_project: str, root: str) -> str:
    return str(Path(source_project) / "Content" / root.removeprefix("/Game/"))


def build_plan(registry: dict, scene_id: str) -> dict:
    scene = next((item for item in registry.get("scenes", []) if item.get("scene_id") == scene_id), None)
    if scene is None:
        available = ", ".join(item.get("scene_id", "<missing>") for item in registry.get("scenes", []))
        raise KeyError(f"Unknown scene_id {scene_id!r}. Available: {available}")

    refs = scene.get("reference_sample", [])
    roots = sorted({root for ref in refs if (root := game_root(ref))})
    map_root = game_root(f"/Game/{scene['relative_path'].split('/')[0]}/dummy")
    if map_root and map_root not in roots:
        roots.insert(0, map_root)

    source_project = registry.get("source_project", "")
    source_content_roots = [content_path_for_game_root(source_project, root) for root in roots]
    direct_editor_blockers = registry.get("direct_editor_open_blockers", [])

    return {
        "schema": "quadrotor.rflysim_scene_migration_plan.v1",
        "scene_id": scene_id,
        "priority": scene.get("priority"),
        "purpose": scene.get("purpose"),
        "source_project": source_project,
        "source_engine_association": registry.get("source_engine_association"),
        "target_engine_association": registry.get("target_engine_association"),
        "direct_use_supported": False,
        "direct_editor_open_supported": registry.get("direct_editor_open_supported", False),
        "direct_editor_open_blockers": direct_editor_blockers[:20],
        "source_map": scene.get("relative_path"),
        "suggested_temp_project": "D:/UE_MigrationScratch/QuadrotorRflySimSceneProbe",
        "target_project": "unreal/MworksUnrealRenderer/MworksUnrealRenderer.uproject",
        "source_game_roots": roots,
        "source_content_roots": source_content_roots,
        "reference_sample": refs,
        "acceptance": [
            "scene opens in a temporary Unreal conversion project with no missing core geometry",
            "selected assets can be migrated into a project-owned UE5 test project without proprietary runtime dependency",
            "visual scale is measured against MWORKS meters and stored as a scene profile transform",
            "collision proxies are derived as simple boxes/convex hulls and linked to world_geometry ids",
            "MWORKS UDP playback drives UAV pose, motor visuals, radar sector, local plan, and trail without feeding data back",
            "no .pak, installer, engine binary, or unclear-license asset is committed",
        ],
        "manual_steps": [
            "do not open the original RflySim UE project as the main route while direct_editor_open_supported is false",
            "if a diagnostic editor test is still needed, copy the RflySim UE project to the suggested temporary path outside this repo",
            "record every missing project module, plugin module, asset, and incompatible-engine warning from the temporary copy",
            "migrate only the required source content roots into a disposable UE5 test project, never into the final renderer first",
            "extract or author simplified collision proxies for visible obstacles, walls, gates, and terrain",
            "update the project-owned scene registry entry from audit_only to migrated_tested only after visual and collision checks pass",
        ],
        "stop_conditions": [
            "project module or plugin module source/DLL remains missing and the scene requires that module",
            "required proprietary plugin is unavailable",
            "the map opens only in the packaged RflySim runtime",
            "core scene geometry is missing after migration",
            "asset size or license makes repository tracking impossible",
            "collision truth cannot be approximated without changing planner assumptions",
        ],
    }


def write_markdown(plan: dict, path: Path) -> None:
    lines = [
        f"# RflySim Scene Migration Plan: {plan['scene_id']}",
        "",
        f"- Priority: `{plan['priority']}`",
        f"- Purpose: {plan['purpose']}",
        f"- Source map: `{plan['source_map']}`",
        f"- Source engine: `{plan['source_engine_association']}`",
        f"- Target engine: `{plan['target_engine_association']}`",
        f"- Direct use supported: `{str(plan['direct_use_supported']).lower()}`",
        f"- Direct editor open supported: `{str(plan['direct_editor_open_supported']).lower()}`",
        "",
        "## Source Content Roots",
        "",
    ]
    for root, path_text in zip(plan["source_game_roots"], plan["source_content_roots"]):
        lines.append(f"- `{root}` -> `{path_text}`")

    lines += ["", "## Acceptance", ""]
    for item in plan["acceptance"]:
        lines.append(f"- {item}")

    if plan.get("direct_editor_open_blockers"):
        lines += ["", "## Direct Editor Open Blockers", ""]
        for item in plan["direct_editor_open_blockers"]:
            lines.append(f"- {item}")

    lines += ["", "## Manual Steps", ""]
    for index, item in enumerate(plan["manual_steps"], start=1):
        lines.append(f"{index}. {item}")

    lines += ["", "## Stop Conditions", ""]
    for item in plan["stop_conditions"]:
        lines.append(f"- {item}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_review_checklist(plan: dict, path: Path) -> None:
    lines = [
        f"# Manual UE Migration Review: {plan['scene_id']}",
        "",
        "Fill this checklist while inspecting the temporary Unreal conversion project.",
        "Do not copy assets into the competition repo until every blocking item is resolved.",
        "",
        "## Scene Open Result",
        "",
        "| Item | Result | Notes |",
        "| --- | --- | --- |",
        "| Temporary project path | TODO | `D:/UE_MigrationScratch/QuadrotorRflySimSceneProbe` or equivalent |",
        f"| Source map opens | TODO | `{plan['source_map']}` |",
        "| Missing plugin warning | TODO | list exact plugin names or `none` |",
        "| Missing asset warning | TODO | list exact assets or `none` |",
        "| Core geometry visible | TODO | floor/walls/ring/terrain as applicable |",
        "| Materials acceptable | TODO | transparent/black/missing material issues |",
        "| Scale checked | TODO | compare one known dimension to MWORKS meters |",
        "| Coordinate direction checked | TODO | X/Y/Z and handedness notes |",
        "",
        "## Migration Package Readiness",
        "",
        "| Item | Result | Notes |",
        "| --- | --- | --- |",
        "| Candidate content roots copied to staging only | TODO | not directly into `Content/` |",
        "| `scene_asset_registry.json` created | TODO | must follow project schema |",
        "| Collision proxies authored | TODO | every obstacle-like visible asset has proxy |",
        "| Package checker passed | TODO | run `check_unreal_migration_package.py` |",
        "| No `.pak`/installer/engine binary | TODO | required |",
        "| No single file >100 MB | TODO | required before Git |",
        "| License status recorded | TODO | `permitted` or `pending_review`, never blank |",
        "",
        "## Playback Readiness",
        "",
        "| Item | Result | Notes |",
        "| --- | --- | --- |",
        "| `map_id` selected | TODO | must match registry scene/map id |",
        "| UAV scale and color acceptable | TODO | body, arms, propellers visible |",
        "| Propeller RPM visual works | TODO | no static propellers unless source has no RPM |",
        "| Local plan and trail visible | TODO | starts at UAV center |",
        "| Radar sector visible | TODO | FOV/radius/yaw follows packet |",
        "| Follow camera usable | TODO | no constant manual drag required |",
        "",
        "## Decision",
        "",
        "| Decision | Value |",
        "| --- | --- |",
        "| Import into project-owned UE5 renderer? | TODO yes/no |",
        "| Reason | TODO |",
        "| Next action | TODO |",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--scene-id", default="rflysim_vision_ring")
    parser.add_argument(
        "--scene-ids",
        default="",
        help="Comma-separated scene ids. Overrides --scene-id when non-empty.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    registry = load_json(args.registry)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    scene_ids = [item.strip() for item in args.scene_ids.split(",") if item.strip()] or [args.scene_id]
    for scene_id in scene_ids:
        plan = build_plan(registry, scene_id)
        json_path = args.output_dir / f"{scene_id}_migration_plan.json"
        md_path = args.output_dir / f"{scene_id}_migration_plan.md"
        checklist_path = args.output_dir / f"{scene_id}_manual_review_checklist.md"
        json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_markdown(plan, md_path)
        write_review_checklist(plan, checklist_path)
        print(f"[OK] wrote {json_path}")
        print(f"[OK] wrote {md_path}")
        print(f"[OK] wrote {checklist_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
