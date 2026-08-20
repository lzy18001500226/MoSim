#!/usr/bin/env python3
"""Remove zero-length consecutive points from current controller diagrams."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


POINTS_RE = re.compile(r"points\s*=\s*\{\{(?P<body>.*?)\}\}", re.DOTALL)
POINT_RE = re.compile(
    r"\{\s*(?P<x>-?(?:\d+(?:\.\d*)?|\.\d+))\s*,\s*"
    r"(?P<y>-?(?:\d+(?:\.\d*)?|\.\d+))\s*\}"
)


def target_files(root: Path) -> list[Path]:
    experiment = root / "Experiment"
    files = sorted(experiment.rglob("*GraphicalRunner.mo"))
    planned_core = root / "Control" / "PidFamily" / "PidAwffLinearEsoGraphicalController.mo"
    if planned_core.is_file():
        files.append(planned_core)
    return files


def normalize_text(text: str) -> tuple[str, int, int]:
    changed = 0
    removed = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal changed, removed
        points = list(POINT_RE.finditer(match.group("body")))
        if len(points) < 2:
            return match.group(0)

        kept: list[tuple[str, str]] = []
        for point in points:
            pair = (point.group("x"), point.group("y"))
            if kept and kept[-1] == pair:
                removed += 1
                continue
            kept.append(pair)

        if len(kept) == len(points):
            return match.group(0)
        changed += 1
        body = "},{".join(f"{x},{y}" for x, y in kept)
        return f"points={{{{{body}}}}}"

    return POINTS_RE.sub(replace, text), changed, removed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("Models/MoSimQuadrotorModel"))
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    records: list[dict[str, object]] = []
    total_removed = 0
    total_changed = 0
    for path in target_files(root):
        original = path.read_text(encoding="utf-8")
        normalized, changed, removed = normalize_text(original)
        if changed:
            path.write_text(normalized, encoding="utf-8", newline="\n")
        total_changed += changed
        total_removed += removed
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "line_annotations_changed": changed,
                "duplicate_points_removed": removed,
            }
        )

    report = {
        "schema": "mosim.controller_graphical_line_normalization.v1",
        "root": root.as_posix(),
        "target_file_count": len(records),
        "files_changed": sum(1 for record in records if record["line_annotations_changed"]),
        "line_annotations_changed": total_changed,
        "duplicate_points_removed": total_removed,
        "topology_unchanged": True,
        "records": records,
    }
    if args.json_output:
        output = args.json_output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
