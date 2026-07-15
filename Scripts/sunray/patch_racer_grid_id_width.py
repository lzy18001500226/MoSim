#!/usr/bin/env python3
"""Widen RACER grid identifiers for Factory-scale HGrid maps."""

from __future__ import annotations

import argparse
from pathlib import Path


MESSAGE_FIELDS = {
    "exploration_manager/msg/DroneState.msg": ("grid_ids",),
    "exploration_manager/msg/PairOpt.msg": ("ego_ids", "other_ids"),
    "exploration_manager/msg/GridIds.msg": ("ids",),
}


def widen_fields(path: Path, fields: tuple[str, ...]) -> bool:
    if not path.is_file():
        raise FileNotFoundError(f"RACER message missing: {path}")

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    changed = False
    for field in fields:
        matching_indexes = []
        matching_types = []
        for index, line in enumerate(lines):
            declaration = line.split("#", 1)[0].strip().split()
            if len(declaration) == 2 and declaration[1] == field:
                matching_indexes.append(index)
                matching_types.append(declaration[0])

        if matching_types == ["int32[]"]:
            continue
        if matching_types != ["int8[]"]:
            raise RuntimeError(
                f"{path}: expected field declaration not found: int8[] {field}"
            )

        index = matching_indexes[0]
        lines[index] = lines[index].replace("int8[]", "int32[]", 1)
        changed = True

    if changed:
        path.write_text("".join(lines), encoding="utf-8")
    return changed


def apply(root: Path) -> bool:
    changed_paths = []
    for relative_path, fields in MESSAGE_FIELDS.items():
        path = root / relative_path
        if widen_fields(path, fields):
            changed_paths.append(relative_path)

    if changed_paths:
        print("RACER grid-id width patch applied: " + ", ".join(changed_paths))
        return True

    print(f"RACER grid-id width patch already present: {root}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("racer_source_root", type=Path)
    args = parser.parse_args()
    apply(args.racer_source_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
