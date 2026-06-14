#!/usr/bin/env python3
"""Inspect the runtime Sunray150 UE StaticMesh material bindings.

This is a commandlet wrapper around a small Editor Python script. It records
the actual StaticMesh material slots and assigned UE material assets so the
reviewed Blender/FBX material route can be checked without relying on a
foreground Editor session.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from run_scene_truth_export import (
    ENGINE_ROOT_BY_VERSION,
    resolve_editor_cmd,
    tail_lines,
    to_windows_path,
)


ROOT = Path(__file__).resolve().parents[2]
RENDERER_UPROJECT = ROOT / "UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject"
DEFAULT_ASSET_PATH = "/Game/Sunray150/sunray150_with_mid360_textured"
DEFAULT_EXPECTED_MANIFEST = (
    ROOT
    / "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/sunray150_with_mid360_textured_export_manifest.json"
)


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def output_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def write_editor_script(
    script_path: Path,
    *,
    asset_path: str,
    expected_manifest: Path,
    evidence_path: Path,
) -> None:
    asset_name = asset_path.rsplit("/", 1)[-1]
    object_path = asset_path + "." + asset_name
    source = f"""
import json
from pathlib import Path
import unreal

asset_path = {asset_path!r}
object_path = {object_path!r}
expected_manifest = Path({to_windows_path(expected_manifest)!r})
evidence_path = Path({to_windows_path(evidence_path)!r})

expected_names = []
if expected_manifest.exists():
    data = json.loads(expected_manifest.read_text(encoding="utf-8"))
    expected_names = list(data.get("first_materials", []))

old_prefixes = ("MoSim_", "CarbonFrame", "Mid360BaseGrey", "Mid360DomeBlue", "LightPlastic")
new_prefixes = ("Sunray150_Texture_", "MID360_Texture_")

asset = unreal.load_asset(object_path)
slots = []
dependencies = []
referencers = []
ok = bool(asset)

if ok:
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    deps = asset_registry.get_dependencies(asset.get_package().get_name(), unreal.AssetRegistryDependencyOptions(True, True, True, True))
    refs = asset_registry.get_referencers(asset.get_package().get_name(), unreal.AssetRegistryDependencyOptions(True, True, True, True))
    dependencies = sorted(str(item) for item in deps)
    referencers = sorted(str(item) for item in refs)

    get_static_materials = getattr(asset, "get_editor_property", None)
    static_materials = []
    if callable(get_static_materials):
        try:
            static_materials = list(asset.get_editor_property("static_materials"))
        except Exception:
            static_materials = []
    if static_materials:
        for idx, entry in enumerate(static_materials):
            mat = getattr(entry, "material_interface", None)
            slot_name = str(getattr(entry, "material_slot_name", ""))
            imported_name = str(getattr(entry, "imported_material_slot_name", ""))
            mat_path = str(mat.get_path_name()) if mat else ""
            mat_name = str(mat.get_name()) if mat else ""
            slots.append({{
                "index": idx,
                "slot_name": slot_name,
                "imported_slot_name": imported_name,
                "material_name": mat_name,
                "material_path": mat_path,
                "is_old_mosim_material": mat_name.startswith(old_prefixes) or any(token in mat_name for token in old_prefixes),
                "is_expected_review_material": mat_name in expected_names or mat_name.startswith(new_prefixes),
            }})
    else:
        get_num_sections = getattr(asset, "get_num_sections", None)
        if callable(get_num_sections):
            try:
                count = int(asset.get_num_sections(0))
            except Exception:
                count = 0
            for idx in range(count):
                mat = asset.get_material(idx)
                mat_name = str(mat.get_name()) if mat else ""
                slots.append({{
                    "index": idx,
                    "slot_name": "",
                    "imported_slot_name": "",
                    "material_name": mat_name,
                    "material_path": str(mat.get_path_name()) if mat else "",
                    "is_old_mosim_material": mat_name.startswith(old_prefixes) or any(token in mat_name for token in old_prefixes),
                    "is_expected_review_material": mat_name in expected_names or mat_name.startswith(new_prefixes),
                }})

payload = {{
    "schema": "mosim.sunray150_runtime_material_inspection.v1",
    "ok": ok,
    "asset_path": asset_path,
    "object_path": object_path,
    "asset_class": str(asset.get_class().get_name()) if ok else "",
    "expected_manifest": str(expected_manifest),
    "expected_material_count": len(expected_names),
    "expected_materials_first": expected_names[:40],
    "material_slot_count": len(slots),
    "slots": slots,
    "old_mosim_slot_count": sum(1 for item in slots if item["is_old_mosim_material"]),
    "expected_review_slot_count": sum(1 for item in slots if item["is_expected_review_material"]),
    "dependencies": dependencies,
    "referencers": referencers,
    "claim_boundary": [
        "UE asset material binding inspection only.",
        "Does not prove visual acceptance without screenshot review.",
        "Does not change MWORKS, ROS2, controller, planner, or runtime evidence."
    ],
}}
evidence_path.parent.mkdir(parents=True, exist_ok=True)
evidence_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
if not ok:
    raise RuntimeError("StaticMesh asset not found: " + object_path)
"""
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(source.strip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-path", default=DEFAULT_ASSET_PATH)
    parser.add_argument("--expected-manifest", type=Path, default=DEFAULT_EXPECTED_MANIFEST)
    parser.add_argument("--engine-version", default="5.5")
    parser.add_argument("--engine-root", type=Path, default=None)
    parser.add_argument("--editor-cmd", type=Path, default=None)
    parser.add_argument(
        "--script-path",
        type=Path,
        default=ROOT / "Results/tmp/inspect_sunray150_runtime_materials_editor.py",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=ROOT / "Results/tmp/inspect_sunray150_runtime_materials_latest.json",
    )
    parser.add_argument("--log-output", type=Path, default=None)
    parser.add_argument("--timeout-seconds", type=float, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    expected_manifest = args.expected_manifest if args.expected_manifest.is_absolute() else ROOT / args.expected_manifest
    script_path = args.script_path if args.script_path.is_absolute() else ROOT / args.script_path
    evidence_path = args.json_output if args.json_output.is_absolute() else ROOT / args.json_output
    engine_root = args.engine_root or ENGINE_ROOT_BY_VERSION.get(args.engine_version)
    editor_cmd = resolve_editor_cmd(RENDERER_UPROJECT, engine_root, args.editor_cmd)

    write_editor_script(
        script_path,
        asset_path=args.asset_path,
        expected_manifest=expected_manifest,
        evidence_path=evidence_path,
    )
    command = [
        str(editor_cmd),
        to_windows_path(RENDERER_UPROJECT),
        "-run=pythonscript",
        f"-script={to_windows_path(script_path)}",
        "-nosplash",
        "-NoSound",
        "-stdout",
        "-FullStdOutLogOutput",
        "-unattended",
    ]
    payload: dict[str, Any] = {
        "renderer_uproject": rel(RENDERER_UPROJECT),
        "asset_path": args.asset_path,
        "editor_cmd": to_windows_path(editor_cmd),
        "script_path": rel(script_path),
        "json_output": rel(evidence_path),
        "command": command,
    }
    try:
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=args.timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        if args.log_output:
            log_path = args.log_output if args.log_output.is_absolute() else ROOT / args.log_output
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(output_text(exc.stdout) + output_text(exc.stderr), encoding="utf-8", errors="replace")
            payload["log_output"] = rel(log_path)
            payload["tail"] = tail_lines(log_path, 80)
        payload.update({"ok": False, "reason": "timeout", "timeout_seconds": args.timeout_seconds})
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 124
    if args.log_output:
        log_path = args.log_output if args.log_output.is_absolute() else ROOT / args.log_output
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text((completed.stdout or "") + (completed.stderr or ""), encoding="utf-8", errors="replace")
        payload["log_output"] = rel(log_path)
        payload["tail"] = tail_lines(log_path, 80)
    if evidence_path.exists():
        payload["inspection"] = json.loads(evidence_path.read_text(encoding="utf-8"))
    payload["returncode"] = completed.returncode
    payload["ok"] = completed.returncode == 0 and bool(payload.get("inspection", {}).get("ok"))
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else completed.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
