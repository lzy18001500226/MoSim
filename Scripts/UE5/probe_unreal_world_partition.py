#!/usr/bin/env python3
"""Probe Unreal Editor Python world-partition and component APIs.

Run this file inside Unreal Editor Python after a target map is loaded.  It is
diagnostic only and writes a compact JSON artifact for exporter development.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def unreal_name(value: Any) -> str:
    for method_name in ("get_path_name", "get_name"):
        method = getattr(value, method_name, None)
        if callable(method):
            try:
                result = method()
            except Exception:
                continue
            if result:
                return str(result)
    return str(value)


def method_names(value: Any, tokens: tuple[str, ...]) -> list[str]:
    names: list[str] = []
    for name in dir(value):
        lower = name.lower()
        if any(token in lower for token in tokens):
            names.append(name)
    return sorted(names)


def component_summary(component: Any) -> dict[str, Any]:
    cls = component.get_class() if hasattr(component, "get_class") else None
    summary = {
        "name": unreal_name(component),
        "class": unreal_name(cls) if cls else type(component).__name__,
        "methods": method_names(component, ("instance", "mesh", "bounds", "collision")),
    }
    for attr in ("static_mesh", "instancing_random_seed"):
        try:
            value = getattr(component, attr)
        except Exception:
            continue
        if value:
            summary[attr] = unreal_name(value)
    for method_name in ("get_instance_count", "get_instance_transform"):
        method = getattr(component, method_name, None)
        if callable(method):
            try:
                if method_name == "get_instance_transform":
                    summary[method_name] = "callable"
                else:
                    summary[method_name] = method()
            except Exception as exc:
                summary[method_name] = f"error: {exc}"
    return summary


def build_payload() -> dict[str, Any]:
    import unreal  # type: ignore

    world = unreal.EditorLevelLibrary.get_editor_world()
    actors = unreal.EditorLevelLibrary.get_all_level_actors() if world else []
    payload: dict[str, Any] = {
        "world": unreal_name(world) if world else "",
        "actor_count": len(actors),
        "world_partition_classes": [
            name for name in dir(unreal) if "WorldPartition" in name or "DataLayer" in name
        ],
        "subsystems": [],
        "actors": [],
    }

    for class_name in (
        "WorldPartitionEditorSubsystem",
        "DataLayerEditorSubsystem",
        "EditorActorSubsystem",
        "LevelEditorSubsystem",
    ):
        cls = getattr(unreal, class_name, None)
        if cls is None:
            payload["subsystems"].append({"class": class_name, "available": False})
            continue
        try:
            subsystem = unreal.get_editor_subsystem(cls)
        except Exception as exc:
            payload["subsystems"].append({"class": class_name, "available": True, "error": str(exc)})
            continue
        payload["subsystems"].append(
            {
                "class": class_name,
                "available": True,
                "subsystem": unreal_name(subsystem),
                "methods": method_names(subsystem, ("load", "cell", "region", "partition", "actor", "data_layer")),
            }
        )

    for actor in actors[:80]:
        components = actor.get_components_by_class(unreal.ActorComponent)
        payload["actors"].append(
            {
                "name": actor.get_actor_label(),
                "class": unreal_name(actor.get_class()),
                "component_count": len(components),
                "components": [component_summary(component) for component in components[:20]],
            }
        )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build_payload()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "actor_count": payload["actor_count"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
