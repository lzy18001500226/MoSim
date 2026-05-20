#!/usr/bin/env python3
"""Generate an implementation plan from project-owned Unreal scene profiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILES = ROOT / "unreal/MworksUnrealRenderer/Content/MworksData/unreal_scene_profiles.json"
DEFAULT_JSON = ROOT / "results/unreal/unreal_scene_profile_implementation_plan.json"
DEFAULT_MD = ROOT / "results/unreal/unreal_scene_profile_implementation_plan.md"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def profile_plan(profile: dict[str, Any], index: int) -> dict[str, Any]:
    render_world = profile.get("render_world", {})
    truth_geometry = profile.get("truth_geometry", {})
    return {
        "order": index,
        "profile_id": profile["profile_id"],
        "priority": profile.get("priority", "P1"),
        "purpose": profile.get("purpose", ""),
        "source_strategy": render_world.get("source_strategy", ""),
        "required_visual_classes": render_world.get("required_visual_classes", []),
        "required_proxy_classes": truth_geometry.get("required_proxy_classes", []),
        "planner_visibility": truth_geometry.get("planner_visibility", ""),
        "global_map_available_to_planner": truth_geometry.get("global_map_available_to_planner"),
        "implementation_steps": [
            "create or select authorized visual assets",
            "write scene_asset_registry entry with source and license note",
            "create matching world_geometry/collision proxies",
            "add scenario profile and planner visibility rule",
            "run Unreal bridge checks",
            "run short MWORKS playback or dry-run stream",
            "perform manual viewport/video review",
        ],
        "acceptance": profile.get("acceptance", []),
    }


def build_plan(profiles_doc: dict[str, Any]) -> dict[str, Any]:
    profiles = profiles_doc.get("profiles", [])
    ordered = sorted(
        profiles,
        key=lambda item: (
            {"P0": 0, "P1": 1, "P2": 2}.get(item.get("priority", "P1"), 9),
            item.get("profile_id", ""),
        ),
    )
    return {
        "schema": "quadrotor.unreal_scene_profile_implementation_plan.v1",
        "source_profiles": str(DEFAULT_PROFILES.relative_to(ROOT)),
        "truth_policy": profiles_doc.get("truth_policy", ""),
        "coordinate_frame": profiles_doc.get("coordinate_frame", {}),
        "runtime_targets": profiles_doc.get("runtime_targets", {}),
        "profile_count": len(ordered),
        "profiles": [profile_plan(profile, index) for index, profile in enumerate(ordered, start=1)],
        "next_recommended_task": (
            "Implement gate_ring_indoor first if the goal is attitude-control video; "
            "implement maze_building first if the goal is local perception and replanning."
        ),
    }


def write_markdown(plan: dict[str, Any], path: Path) -> None:
    lines = [
        "# Unreal Scene Profile Implementation Plan",
        "",
        f"- Source profiles: `{plan['source_profiles']}`",
        f"- Profile count: `{plan['profile_count']}`",
        f"- Next recommended task: {plan['next_recommended_task']}",
        "",
        "## Runtime Targets",
        "",
    ]
    for key, value in plan.get("runtime_targets", {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines += [
        "",
        "## Profiles",
        "",
        "| Order | Profile | Priority | Planner visibility | Visual classes | Proxy classes |",
        "| ---: | --- | --- | --- | --- | --- |",
    ]
    for profile in plan["profiles"]:
        visual = ", ".join(f"`{item}`" for item in profile["required_visual_classes"])
        proxies = ", ".join(f"`{item}`" for item in profile["required_proxy_classes"])
        lines.append(
            f"| {profile['order']} | `{profile['profile_id']}` | {profile['priority']} | "
            f"`{profile['planner_visibility']}` | {visual} | {proxies} |"
        )
    lines += ["", "## Acceptance Gates", ""]
    for profile in plan["profiles"]:
        lines.append(f"### `{profile['profile_id']}`")
        lines.append("")
        for item in profile["acceptance"]:
            lines.append(f"- {item}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILES)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-output", type=Path, default=DEFAULT_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profiles_doc = load_json(args.profiles)
    plan = build_plan(profiles_doc)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(plan, args.md_output)
    print(f"[OK] wrote {args.json_output}")
    print(f"[OK] wrote {args.md_output}")
    print(plan["next_recommended_task"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
