#!/usr/bin/env python3
"""Prepare or run Unreal command-line scene-truth export for MoSim scenes."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from export_unreal_scene_truth import slug
from plan_scene_truth_export import ROOT, plan_exports, quote, to_windows_path


ENGINE_ROOT_BY_VERSION = {
    "4.27": Path("/mnt/d/Program Files/Epic Games/UE_4.27"),
    "5.4": Path("/mnt/d/Program Files/Epic Games/UE_5.4"),
    "5.5": Path("/mnt/d/Program Files/Epic Games/UE_5.5"),
    "5.7": Path("/mnt/d/Program Files/Epic Games/UE_5.7"),
}


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def engine_version_for_project(uproject_path: Path) -> str:
    value = str(read_json(uproject_path).get("EngineAssociation", "")).strip()
    if value in ENGINE_ROOT_BY_VERSION:
        return value
    if value.startswith("5.5"):
        return "5.5"
    if value.startswith("5.4"):
        return "5.4"
    if value.startswith("5.7"):
        return "5.7"
    if value.startswith("4.27"):
        return "4.27"
    return "5.5"


def to_wsl_path(path: str) -> Path:
    text = path.replace("\\", "/")
    if len(text) >= 3 and text[1] == ":" and text[2] == "/":
        return Path("/mnt") / text[0].lower() / text[3:]
    return Path(path)


def resolve_editor_cmd(uproject_path: Path, engine_root: Path | None, editor_cmd: Path | None) -> Path:
    candidates: list[Path] = []
    if editor_cmd:
        candidates.append(editor_cmd)
    env_cmd = os.environ.get("UE_EDITOR_CMD")
    if env_cmd:
        candidates.append(Path(env_cmd))
    if engine_root:
        candidates.extend(
            [
                engine_root / "Engine/Binaries/Win64/UnrealEditor-Cmd.exe",
                engine_root / "Engine/Binaries/Win64/UE4Editor-Cmd.exe",
            ]
        )
    env_root = os.environ.get("UE_ROOT")
    if env_root:
        env_root_path = Path(env_root)
        candidates.extend(
            [
                env_root_path / "Engine/Binaries/Win64/UnrealEditor-Cmd.exe",
                env_root_path / "Engine/Binaries/Win64/UE4Editor-Cmd.exe",
            ]
        )
    version_root = ENGINE_ROOT_BY_VERSION[engine_version_for_project(uproject_path)]
    candidates.extend(
        [
            version_root / "Engine/Binaries/Win64/UnrealEditor-Cmd.exe",
            version_root / "Engine/Binaries/Win64/UE4Editor-Cmd.exe",
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Unreal Editor commandlet executable not found. Checked: "
        + ", ".join(map(str, candidates))
    )


def write_batch_script(plan: dict[str, str], script_path: Path, map_package: str | None = None) -> None:
    """Write an Unreal Editor Python script that loads a map and exports truth."""
    source = [
        "import runpy",
        "import sys",
        "from pathlib import Path",
        "",
    ]
    if map_package:
        source.extend(
            [
                "import unreal",
                f"unreal.EditorLevelLibrary.load_level({map_package!r})",
                "",
            ]
        )
    export_script = ROOT / "Scripts" / "UE5" / "export_unreal_scene_truth.py"
    map_id = Path(plan["truth_output"]).stem.replace("_collision_truth", "")
    source.extend(
        [
            "sys.argv = [",
            f"    {to_windows_path(export_script)!r},",
            "    'export',",
            f"    '--scene-id', {slug(plan['name'])!r},",
            f"    '--map-id', {map_id!r},",
            f"    '--output', {to_windows_path(plan['truth_output'])!r},",
            "]",
            f"runpy.run_path({to_windows_path(export_script)!r}, run_name='__main__')",
            "",
        ]
    )
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text("\n".join(source), encoding="utf-8")


def build_command(
    *,
    editor_cmd: Path,
    uproject_path: Path,
    batch_script: Path,
    map_path: str = "",
    unattended: bool = True,
) -> list[str]:
    command = [
        str(editor_cmd),
        to_windows_path(uproject_path),
    ]
    if map_path:
        command.append(map_path)
    command.extend(
        [
            "-run=pythonscript",
            f"-script={to_windows_path(batch_script)}",
            "-nosplash",
            "-NoSound",
            "-stdout",
            "-FullStdOutLogOutput",
        ]
    )
    if unattended:
        command.append("-unattended")
    return command


def first_plan(scene_root: Path, truth_root: Path, query: str) -> dict[str, str]:
    plans = plan_exports(scene_root, truth_root, query)
    if not plans:
        raise RuntimeError(f"No scene export plan matched query: {query}")
    if len(plans) > 1:
        names = ", ".join(plan["name"] for plan in plans)
        raise RuntimeError(f"Query matched multiple scenes; narrow it first: {names}")
    return plans[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="Unique scene name substring, e.g. Derelict.")
    parser.add_argument("--scene-root", type=Path, default=ROOT / "References/UnrealScenes")
    parser.add_argument("--truth-root", type=Path, default=ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_truth")
    parser.add_argument("--engine-root", type=Path, default=None)
    parser.add_argument("--editor-cmd", type=Path, default=None)
    parser.add_argument("--map-package", default="", help="Optional UE package path, e.g. /Game/DerelictCorridor/Maps/DerelictCorridor.")
    parser.add_argument("--batch-script", type=Path, default=ROOT / "Results/tmp/unreal_scene_truth_export.py")
    parser.add_argument(
        "--run",
        action="store_true",
        help="Actually launch the Unreal Editor commandlet. Default is dry-run.",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    plan = first_plan(args.scene_root, args.truth_root, args.query)
    uproject_path = to_wsl_path(plan["uproject_path"])
    editor_cmd = resolve_editor_cmd(uproject_path, args.engine_root, args.editor_cmd)
    map_package = args.map_package or plan.get("recommended_map_package", "")
    write_batch_script(plan, args.batch_script, map_package or None)
    command = build_command(
        editor_cmd=editor_cmd,
        uproject_path=uproject_path,
        batch_script=args.batch_script,
        map_path=map_package,
    )
    result = {
        "scene": plan["name"],
        "uproject_path": plan["uproject_path"],
        "engine_version": engine_version_for_project(uproject_path),
        "editor_cmd": to_windows_path(editor_cmd),
        "batch_script": str(args.batch_script),
        "truth_output": plan["truth_output"],
        "map_package": map_package,
        "command": command,
        "dry_run": not args.run,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"Scene: {result['scene']}")
        print(f"Project: {result['uproject_path']}")
        print(f"Editor-Cmd: {result['editor_cmd']}")
        print(f"Batch script: {result['batch_script']}")
        print(f"Truth output: {result['truth_output']}")
        print("Command:")
        print("  " + " ".join(quote(part) if " " in part else part for part in command))
    if not args.run:
        return 0
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
