#!/usr/bin/env python3
"""Materialize the project-owned MoSim custom build into canonical QGC source."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "ground_station" / "qgc" / "mosim_extension" / "custom"
CANONICAL_QGC_ROOT = ROOT / "src" / "ground_station" / "qgc" / "qgroundcontrol"
TARGET = CANONICAL_QGC_ROOT / "custom"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def materialize(source: Path = SOURCE, target: Path = TARGET, project_root: Path = ROOT) -> dict[str, object]:
    source = source.resolve()
    target = target.resolve()
    project_root = project_root.resolve()
    canonical_qgc = (project_root / "src" / "ground_station" / "qgc" / "qgroundcontrol").resolve()
    if source != SOURCE.resolve() and project_root not in source.parents:
        raise ValueError("overlay source must be project-owned")
    if target != TARGET.resolve() and project_root not in target.parents:
        raise ValueError("overlay target must be project-owned")
    if target == TARGET.resolve() and canonical_qgc not in target.parents:
        raise ValueError("overlay target escaped the canonical QGC source tree")
    if not (source / "CMakeLists.txt").is_file():
        raise FileNotFoundError(source / "CMakeLists.txt")
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True)
    files = {
        path.relative_to(source).as_posix(): _digest(path)
        for path in sorted(source.rglob("*"))
        if path.is_file()
    }
    manifest = {
        "schema": "mosim.qgc_custom_overlay.v1",
        "source": source.relative_to(project_root).as_posix() if project_root in source.parents else str(source),
        "target": target.relative_to(project_root).as_posix() if project_root in target.parents else str(target),
        "files": files,
    }
    (target / ".mosim-overlay.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    return manifest


if __name__ == "__main__":
    result = materialize()
    print(json.dumps({"target": result["target"], "file_count": len(result["files"])}, ensure_ascii=False))
