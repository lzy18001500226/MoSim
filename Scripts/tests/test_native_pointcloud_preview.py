#!/usr/bin/env python3
"""Regression checks for the native point-cloud preview fallback."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_preview_scripts_do_not_use_html() -> None:
    for relative in (
        "Scripts/UE5/open_native_pointcloud_preview.sh",
        "Scripts/UE5/open_native_pointcloud_preview.ps1",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        forbidden = ("pointcloud_viewer.html", "<html", "Start-Process *html")
        for phrase in forbidden:
            if phrase.lower() in text.lower():
                raise AssertionError(f"{relative} contains stale HTML route: {phrase}")


def test_workflow_records_two_window_policy() -> None:
    text = (ROOT / "Docs/Workflows/unreal_renderer.md").read_text(encoding="utf-8")
    required = (
        "Native Mapping Window Policy",
        "Unreal / `MoSimSceneLibrary`",
        "RViz / RViz2 or equivalent native robotics viewer",
        "HTML report preview",
        "never the active point-cloud/map review surface",
        "The operator-facing default is split RViz windows",
        "RViz planning/grid window",
        "RViz point-cloud/FAST-LIO window",
        "RVIZ_PROFILE=split",
        "Hard implementation constraints",
        "Global scene truth stays hidden from the planner",
    )
    for phrase in required:
        if phrase not in text:
            raise AssertionError(f"missing mapping-window policy phrase: {phrase}")


def test_agents_records_mapping_window_rule() -> None:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    required = (
        "Unreal Mapping Window Rule",
        "RViz/RViz2 or an equivalent native robotics",
        "Browser HTML is not an accepted active point-cloud/map review surface",
        "Global UE collision/occupancy truth is a validation oracle only",
    )
    for phrase in required:
        if phrase not in text:
            raise AssertionError(f"missing AGENTS mapping-window rule phrase: {phrase}")


def test_preview_dry_run_contract_when_powershell_available() -> None:
    if os.name == "nt":
        powershell = shutil.which("powershell") or shutil.which("powershell.exe")
        if powershell is None:
            return
        result = subprocess.run(
            [
                powershell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "Scripts/UE5/open_native_pointcloud_preview.ps1",
                "-SceneId",
                "factoryenvironmentcollect",
                "-ProjectRoot",
                str(ROOT),
                "-MaxFrames",
                "2",
                "-MaxPointsPerFrame",
                "20",
                "-DryRun",
            ],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
        )
    elif shutil.which("powershell.exe") is None:
        return
    else:
        result = subprocess.run(
            [
                "bash",
                "Scripts/UE5/open_native_pointcloud_preview.sh",
                "factoryenvironmentcollect",
            ],
            cwd=ROOT,
            env={
                **os.environ,
                "DRY_RUN": "1",
                "MAX_FRAMES": "2",
                "MAX_POINTS_PER_FRAME": "20",
            },
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
        )
    stdout = result.stdout.decode("utf-8", errors="replace")
    payload = json.loads(stdout)
    if payload.get("schema") != "mosim.native_pointcloud_preview_dryrun.v1":
        raise AssertionError(payload)
    if "not FAST-LIO/RViz runtime evidence" not in payload.get("claim", ""):
        raise AssertionError(payload)


def main() -> int:
    test_preview_scripts_do_not_use_html()
    test_workflow_records_two_window_policy()
    test_agents_records_mapping_window_rule()
    test_preview_dry_run_contract_when_powershell_available()
    print("[OK] native point-cloud preview fallback regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
