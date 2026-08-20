#!/usr/bin/env python3
"""Create a per-run Gazebo Classic world copy with explicit ODE pacing."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def project_path(project_root: Path, value: str, *, results_only: bool = False) -> Path:
    candidate = Path(value)
    resolved = (candidate if candidate.is_absolute() else project_root / candidate).resolve()
    try:
        resolved.relative_to(project_root)
    except ValueError as exc:
        raise ValueError(f"path must remain below project root: {value}") from exc
    if results_only:
        results_root = (project_root / "Results").resolve()
        try:
            resolved.relative_to(results_root)
        except ValueError as exc:
            raise ValueError(f"path must remain below Results: {value}") from exc
    return resolved


def positive_number(value: str, name: str) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{name} must be numeric") from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError(f"{name} must be a positive finite number")
    return parsed


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(content)
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_write_bytes(path, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def relative_to_root(project_root: Path, path: Path) -> str:
    return path.relative_to(project_root).as_posix()


def set_child_value(parent: ET.Element, tag: str, value: str) -> None:
    child = parent.find(tag)
    if child is None:
        child = ET.SubElement(parent, tag)
    child.text = value


def materialize_world_overlay(
    project_root: Path,
    source: Path,
    output: Path,
    manifest: Path,
    max_step_size_s: float,
    real_time_update_rate_hz: float,
) -> dict[str, Any]:
    tree = ET.parse(source)
    root = tree.getroot()
    worlds = root.findall("world")
    if len(worlds) != 1:
        raise ValueError(f"expected exactly one world in {source}, found {len(worlds)}")
    physics_nodes = worlds[0].findall("physics")
    if len(physics_nodes) != 1:
        raise ValueError(f"expected exactly one physics node in {source}, found {len(physics_nodes)}")
    physics = physics_nodes[0]
    if physics.get("type") != "ode":
        raise ValueError(f"expected an ODE physics node in {source}")

    set_child_value(physics, "max_step_size", format(max_step_size_s, ".12g"))
    set_child_value(physics, "real_time_update_rate", format(real_time_update_rate_hz, ".12g"))
    rendered = ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"
    atomic_write_bytes(output, rendered)

    payload = {
        "schema": "mosim.gazebo_factory_world_overlay.v1",
        "status": "generated",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "path": relative_to_root(project_root, source),
            "sha256": sha256_file(source),
        },
        "output": {
            "path": relative_to_root(project_root, output),
            "sha256": sha256_file(output),
        },
        "world": {
            "name": worlds[0].get("name", ""),
            "physics_name": physics.get("name", ""),
            "physics_type": physics.get("type", ""),
            "max_step_size_s": max_step_size_s,
            "real_time_update_rate_hz": real_time_update_rate_hz,
        },
        "claim_boundary": (
            "This generated per-run world changes only the ODE max_step_size and "
            "real_time_update_rate. It does not modify the source Factory world, "
            "model collision geometry, sensor definitions, or planner configuration."
        ),
    }
    atomic_write_json(manifest, payload)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--max-step-size-s", required=True, type=lambda value: positive_number(value, "max-step-size-s"))
    parser.add_argument(
        "--real-time-update-rate-hz",
        required=True,
        type=lambda value: positive_number(value, "real-time-update-rate-hz"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    source = project_path(project_root, args.source)
    output = project_path(project_root, args.output, results_only=True)
    manifest = project_path(project_root, args.manifest, results_only=True)
    if not source.is_file():
        raise SystemExit(f"world source does not exist: {source}")
    if output == source:
        raise SystemExit("world overlay output must differ from source")
    payload = materialize_world_overlay(
        project_root,
        source,
        output,
        manifest,
        args.max_step_size_s,
        args.real_time_update_rate_hz,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
