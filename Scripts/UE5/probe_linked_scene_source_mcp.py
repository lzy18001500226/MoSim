#!/usr/bin/env python3
"""Probe live Unreal MCP edit authority for the currently linked scene source.

This combines registry evidence with a reversible editor-side actor edit.  It
does not save the map and does not modify third-party assets permanently.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from check_ue_fab_goal_acceptance import ROOT, SCENE_SOURCE_REGISTRY, load_json, source_by_id
from probe_unreal_editor_mcp_tools import default_host, run_probe, unique_actor_name


def linked_source(source_id: str) -> dict[str, object]:
    registry = load_json(SCENE_SOURCE_REGISTRY)
    source = source_by_id(registry, source_id)
    if not source:
        raise ValueError(f"scene source not found: {source_id}")
    if source.get("imported_into_renderer") is not True:
        raise ValueError(f"{source_id} is not imported/reused in MworksUnrealRenderer")
    renderer_map_asset = source.get("renderer_map_asset")
    renderer_content_root = source.get("renderer_content_root")
    for key, value in [("renderer_content_root", renderer_content_root), ("renderer_map_asset", renderer_map_asset)]:
        if not value or not (ROOT / str(value)).exists():
            raise ValueError(f"{source_id} missing valid {key}: {value}")
    return source


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-source-id", default="local_derelictcorridormegascans")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=55557)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--json-output", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = linked_source(args.scene_source_id)
    host = default_host(args.host)
    actor_name = unique_actor_name(f"MoSimSceneSourceProbe_{args.scene_source_id}")
    evidence = run_probe(host, args.port, actor_name, args.timeout)
    evidence["scene_source_id"] = args.scene_source_id
    evidence["scene_source"] = {
        "renderer_content_root": source.get("renderer_content_root"),
        "renderer_map_asset": source.get("renderer_map_asset"),
        "renderer_map_package": source.get("renderer_map_package"),
        "renderer_reuse_kind": source.get("renderer_reuse_kind"),
        "truth_artifacts": source.get("truth_artifacts", []),
    }
    evidence["scope"] = (
        "reversible actor edit in currently connected MoSim UE editor; "
        "registry proves selected scene source is linked into renderer Content"
    )
    if args.json_output:
        output = args.json_output if args.json_output.is_absolute() else ROOT / args.json_output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote {output.relative_to(ROOT).as_posix()}")
    print(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
