#!/usr/bin/env python3
"""Build a read-only discovery index for ``Results/runs`` manifests.

This script never modifies a run bundle. It only reads
``Results/runs/**/RUN_MANIFEST.json`` and writes one derived index so future
MoSim Studio/QGC views can find declared models, native results, logs and
replay inputs by ``run_id``.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestration.run_manifest_contract import RUN_INDEX_V1_SCHEMA, normalize_run_manifest


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def _portable(path: Path, *, relative_to: Path) -> str:
    try:
        return path.resolve().relative_to(relative_to.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def build_run_index(
    *,
    runs_root: Path,
    project_root: Path | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Read supported manifests below one run root without changing them."""

    runs_root = runs_root.resolve()
    project_root = (project_root or ROOT).resolve()
    records: list[dict[str, Any]] = []
    issues: list[dict[str, str]] = []
    seen_run_ids: dict[str, str] = {}
    if runs_root.is_dir():
        manifest_paths = sorted(runs_root.rglob("RUN_MANIFEST.json"))
    else:
        manifest_paths = []
        issues.append({"path": _portable(runs_root, relative_to=project_root), "reason_code": "runs_root_missing"})

    for manifest_path in manifest_paths:
        portable_manifest = _portable(manifest_path, relative_to=project_root)
        try:
            raw = json.loads(manifest_path.read_text(encoding="utf-8"))
            normalized = normalize_run_manifest(raw)
            run_id = normalized["run_id"]
            previous = seen_run_ids.get(run_id)
            if previous is not None:
                raise ValueError(f"duplicate_run_id:{previous}")
            seen_run_ids[run_id] = portable_manifest
            normalized["run_directory"] = _portable(manifest_path.parent, relative_to=project_root)
            normalized["manifest_path"] = portable_manifest
            records.append(normalized)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            issues.append({"path": portable_manifest, "reason_code": str(exc)})

    stamp = generated_at or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return {
        "schema": RUN_INDEX_V1_SCHEMA,
        "generated_at": stamp,
        "runs_root": _portable(runs_root, relative_to=project_root),
        "run_count": len(records),
        "status": "complete" if not issues else "partial",
        "runs": records,
        "issues": issues,
        "claim_boundary": (
            "Derived discovery index only. It does not alter manifests, prove that declared artifacts exist, "
            "or establish controller, planner, simulator, or flight-runtime success."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-root", type=Path, default=ROOT / "Results" / "runs")
    parser.add_argument("--output", type=Path, default=ROOT / "Results" / "RUN_INDEX.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    index = build_run_index(runs_root=args.runs_root, project_root=ROOT)
    _atomic_write_json(args.output, index)
    print(
        json.dumps(
            {
                "schema": "mosim.run_index_result.v1",
                "output": str(args.output),
                "run_count": index["run_count"],
                "status": index["status"],
                "issue_count": len(index["issues"]),
            },
            ensure_ascii=False,
        )
    )
    return 0 if not index["issues"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
