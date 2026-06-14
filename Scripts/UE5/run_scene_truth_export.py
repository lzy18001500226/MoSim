#!/usr/bin/env python3
"""Prepare or run Unreal command-line scene-truth export for MoSim scenes."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

from export_unreal_scene_truth import slug
from plan_scene_truth_export import ROOT, plan_exports, quote, to_windows_path


def engine_roots(version: str) -> list[Path]:
    return [
        Path(f"D:/Program Files/Epic Games/UE_{version}"),
        Path(f"/mnt/d/Program Files/Epic Games/UE_{version}"),
    ]


ENGINE_ROOT_BY_VERSION = {version: engine_roots(version)[0] for version in ["4.27", "5.4", "5.5", "5.7"]}


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
    for version_root in engine_roots(engine_version_for_project(uproject_path)):
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
                f"map_package = {map_package!r}",
                "loaded = False",
                "level_editor_subsystem_class = getattr(unreal, 'LevelEditorSubsystem', None)",
                "get_editor_subsystem = getattr(unreal, 'get_editor_subsystem', None)",
                "if level_editor_subsystem_class and callable(get_editor_subsystem):",
                "    subsystem = get_editor_subsystem(level_editor_subsystem_class)",
                "    load_level = getattr(subsystem, 'load_level', None)",
                "    if callable(load_level):",
                "        loaded = bool(load_level(map_package))",
                "if not loaded:",
                "    editor_level_library = getattr(unreal, 'EditorLevelLibrary', None)",
                "    load_level = getattr(editor_level_library, 'load_level', None) if editor_level_library else None",
                "    if callable(load_level):",
                "        loaded = bool(load_level(map_package))",
                "if not loaded:",
                "    raise RuntimeError('Unable to load level via UE Python API: ' + map_package)",
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


def write_probe_batch_script(probe_script: Path, output_path: Path, script_path: Path, map_package: str | None = None) -> None:
    source = [
        "import runpy",
        "import sys",
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
    source.extend(
        [
            "sys.argv = [",
            f"    {to_windows_path(probe_script)!r},",
            "    '--output',",
            f"    {to_windows_path(output_path)!r},",
            "]",
            f"runpy.run_path({to_windows_path(probe_script)!r}, run_name='__main__')",
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


def tail_lines(path: Path, max_lines: int = 80) -> list[str]:
    if max_lines <= 0 or not path.exists():
        return []
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()[-max_lines:]
    except OSError:
        return []


def run_command(
    command: list[str],
    *,
    log_output: Path | None,
    timeout_seconds: float | None,
    progress_tail_lines: int,
) -> int:
    """Run the Unreal commandlet with optional log capture and timeout evidence."""
    if not log_output:
        completed = subprocess.run(command, cwd=ROOT, check=False, timeout=timeout_seconds)
        return completed.returncode

    log_output.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    with log_output.open("w", encoding="utf-8", errors="replace", newline="\n") as log_file:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        assert process.stdout is not None
        try:
            for line in process.stdout:
                log_file.write(line)
                log_file.flush()
                if timeout_seconds is not None and time.monotonic() - start > timeout_seconds:
                    process.kill()
                    process.wait(timeout=10)
                    summary = {
                        "ok": False,
                        "reason": "timeout",
                        "timeout_seconds": timeout_seconds,
                        "returncode": 124,
                        "log_output": str(log_output),
                        "tail": tail_lines(log_output, progress_tail_lines),
                    }
                    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
                    return 124
            return process.wait()
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=10)


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
        "--probe-world-partition-output",
        type=Path,
        default=None,
        help="Write a diagnostic World Partition/API probe instead of exporting truth.",
    )
    parser.add_argument("--log-output", type=Path, default=None, help="Capture Unreal stdout/stderr to this log when --run is used.")
    parser.add_argument("--timeout-seconds", type=float, default=None, help="Optional timeout for --run. Return 124 and print a JSON tail on timeout.")
    parser.add_argument("--progress-tail-lines", type=int, default=80)
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
    if args.probe_world_partition_output:
        probe_script = ROOT / "Scripts" / "UE5" / "probe_unreal_world_partition.py"
        probe_output = (
            args.probe_world_partition_output
            if args.probe_world_partition_output.is_absolute()
            else ROOT / args.probe_world_partition_output
        )
        write_probe_batch_script(
            probe_script,
            probe_output,
            args.batch_script,
            map_package or None,
        )
    else:
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
        "probe_world_partition_output": str(probe_output) if args.probe_world_partition_output else "",
        "map_package": map_package,
        "command": command,
        "log_output": str(args.log_output) if args.log_output else "",
        "timeout_seconds": args.timeout_seconds,
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
    return run_command(
        command,
        log_output=args.log_output,
        timeout_seconds=args.timeout_seconds,
        progress_tail_lines=args.progress_tail_lines,
    )


if __name__ == "__main__":
    raise SystemExit(main())
