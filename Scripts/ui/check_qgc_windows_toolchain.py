#!/usr/bin/env python3
"""Read-only preflight for the MoSim QGroundControl Windows toolchain."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


QT_VERSION = "6.8.3"
QT_KIT = "msvc2022_64"
QT_MODULES = (
    "Qt6Charts",
    "Qt6Location",
    "Qt6Positioning",
    "Qt6TextToSpeech",
    "Qt6Core5Compat",
    "Qt6Multimedia",
    "Qt6SerialPort",
    "Qt6ShaderTools",
    "Qt6Bluetooth",
    "Qt6Quick3D",
    "Qt6Sensors",
)


def _first_existing(paths: list[Path]) -> Path | None:
    return next((path.resolve() for path in paths if path.is_file()), None)


def _qt_root(explicit: str | None) -> Path | None:
    candidates: list[Path] = []
    for value in (explicit, os.environ.get("QTDIR"), os.environ.get("Qt6_DIR")):
        if value:
            path = Path(value)
            candidates.append(path.parents[2] if path.name == "Qt6" and len(path.parents) >= 3 else path)
    candidates.extend((Path("C:/Qt") / QT_VERSION / QT_KIT, Path.home() / "Qt" / QT_VERSION / QT_KIT))
    return next((path.resolve() for path in candidates if (path / "bin" / "qtpaths6.exe").is_file()), None)


def inspect(*, qt_dir: str | None = None) -> dict[str, Any]:
    program_files_x86 = Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)"))
    vswhere = _first_existing(
        [
            program_files_x86 / "Microsoft Visual Studio/Installer/vswhere.exe",
            Path("C:/Program Files/Microsoft Visual Studio/Installer/vswhere.exe"),
        ]
    )
    vs_installation: str | None = None
    windows_sdk = False
    if vswhere:
        query = subprocess.run(
            [str(vswhere), "-products", "*", "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationPath"],
            capture_output=True,
            text=True,
            check=False,
        )
        vs_installation = next((line.strip() for line in query.stdout.splitlines() if line.strip()), None)
        for component in (
            "Microsoft.VisualStudio.Component.Windows11SDK.26100",
            "Microsoft.VisualStudio.Component.Windows11SDK.22621",
            "Microsoft.VisualStudio.Component.Windows10SDK.19041",
        ):
            sdk_query = subprocess.run(
                [str(vswhere), "-products", "*", "-requires", component, "-property", "installationPath"],
                capture_output=True,
                text=True,
                check=False,
            )
            if sdk_query.stdout.strip():
                windows_sdk = True
                break
    qt_root = _qt_root(qt_dir)
    missing_modules: list[str] = []
    if qt_root:
        cmake_root = qt_root / "lib" / "cmake"
        missing_modules = [module for module in QT_MODULES if not (cmake_root / module).is_dir()]
    else:
        missing_modules = list(QT_MODULES)

    gstreamer_candidates = [
        Path(value)
        for value in (
            os.environ.get("GSTREAMER_1_0_ROOT_MSVC_X86_64"),
            os.environ.get("GSTREAMER_ROOT_X86_64"),
            "C:/gstreamer/1.0/msvc_x86_64",
        )
        if value
    ]
    gstreamer_root = next(
        (path.resolve() for path in gstreamer_candidates if (path / "bin/gst-launch-1.0.exe").is_file()), None
    )

    checks = {
        "cmake": shutil.which("cmake"),
        "ninja": shutil.which("ninja"),
        "visual_studio_installation": vs_installation,
        "windows_sdk": windows_sdk or None,
        "qt_root": str(qt_root) if qt_root else None,
        "gstreamer_root": str(gstreamer_root) if gstreamer_root else None,
    }
    blockers = [name for name, value in checks.items() if value is None]
    if missing_modules:
        blockers.append("qt_modules")
    return {
        "schema": "mosim.flight_console.windows_toolchain_preflight.v1",
        "status": "ready" if not blockers else "blocked",
        "required": {
            "qt_version": QT_VERSION,
            "qt_kit": QT_KIT,
            "qt_modules": list(QT_MODULES),
            "visual_studio": "Visual Studio 2022 C++ Build Tools with Windows 10/11 SDK",
            "gstreamer": "1.22.12 runtime and development packages",
        },
        "detected": checks,
        "missing_qt_modules": missing_modules,
        "blockers": blockers,
        "mutated_system": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qt-dir")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = inspect(qt_dir=args.qt_dir)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(rendered, end="")
    return 0 if report["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
