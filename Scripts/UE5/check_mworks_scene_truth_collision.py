#!/usr/bin/env python3
"""Check MWORKS scene-smoke trajectories against UE scene-truth occupancy."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"
DEFAULT_SCENES = ("factoryenvironmentcollect", "derelictcorridormegascans")


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def grid_cell(origin_xy_m: list[float], resolution_m: float, x_m: float, y_m: float) -> tuple[int, int]:
    return (
        int(round((x_m - origin_xy_m[0]) / resolution_m)),
        int(round((y_m - origin_xy_m[1]) / resolution_m)),
    )


def cell_center(origin_xy_m: list[float], resolution_m: float, cell: tuple[int, int]) -> tuple[float, float]:
    return (
        origin_xy_m[0] + cell[0] * resolution_m,
        origin_xy_m[1] + cell[1] * resolution_m,
    )


def finite_float(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f"non-finite {key}: {row[key]}")
    return value


def nearest_occupied_clearance_m(
    occupied_cells: set[tuple[int, int]],
    origin_xy_m: list[float],
    resolution_m: float,
    x_m: float,
    y_m: float,
) -> float | None:
    if not occupied_cells:
        return None
    nearest = min(
        math.hypot(x_m - cell_center(origin_xy_m, resolution_m, cell)[0], y_m - cell_center(origin_xy_m, resolution_m, cell)[1])
        for cell in occupied_cells
    )
    return nearest - 0.5 * resolution_m


def check_rows_against_grid(
    *,
    rows: list[dict[str, str]],
    x_key: str,
    y_key: str,
    label: str,
    occupied_cells: set[tuple[int, int]],
    origin_xy_m: list[float],
    resolution_m: float,
    grid_size: list[int],
    max_violations: int,
) -> dict[str, Any]:
    occupied_samples: list[dict[str, Any]] = []
    out_of_bounds_samples: list[dict[str, Any]] = []
    min_clearance: float | None = None
    occupied_unique: set[tuple[int, int]] = set()
    out_unique: set[tuple[int, int]] = set()

    for index, row in enumerate(rows):
        x_m = finite_float(row, x_key)
        y_m = finite_float(row, y_key)
        time_s = float(row.get("time", index))
        cell = grid_cell(origin_xy_m, resolution_m, x_m, y_m)
        in_bounds = 0 <= cell[0] < grid_size[0] and 0 <= cell[1] < grid_size[1]
        clearance = nearest_occupied_clearance_m(occupied_cells, origin_xy_m, resolution_m, x_m, y_m)
        if clearance is not None and (min_clearance is None or clearance < min_clearance):
            min_clearance = clearance
        if not in_bounds:
            out_unique.add(cell)
            if len(out_of_bounds_samples) < max_violations:
                out_of_bounds_samples.append({
                    "row": index,
                    "time_s": time_s,
                    "position_m": [x_m, y_m],
                    "cell_xy": list(cell),
                })
            continue
        if cell in occupied_cells:
            occupied_unique.add(cell)
            if len(occupied_samples) < max_violations:
                occupied_samples.append({
                    "row": index,
                    "time_s": time_s,
                    "position_m": [x_m, y_m],
                    "cell_xy": list(cell),
                    "approx_clearance_m": clearance,
                })

    return {
        "label": label,
        "row_count": len(rows),
        "occupied_sample_count": sum(
            1
            for row in rows
            if grid_cell(origin_xy_m, resolution_m, finite_float(row, x_key), finite_float(row, y_key)) in occupied_cells
        ),
        "occupied_unique_cell_count": len(occupied_unique),
        "out_of_bounds_sample_count": len(out_of_bounds_samples),
        "out_of_bounds_unique_cell_count": len(out_unique),
        "min_approx_clearance_m": min_clearance,
        "collision_free_against_truth": not occupied_unique and not out_unique,
        "first_occupied_samples": occupied_samples,
        "first_out_of_bounds_samples": out_of_bounds_samples,
    }


def check_scene(scene_dir: Path, *, max_violations: int = 12) -> dict[str, Any]:
    scene_id = scene_dir.name
    occupancy = load_json(scene_dir / "occupancy_grid.json")
    grid = occupancy["grid"]
    origin_xy_m = [float(value) for value in grid["origin_xy_m"]]
    resolution_m = float(grid["resolution_m"])
    grid_size = [int(value) for value in grid["size"]]
    occupied_cells = {tuple(int(value) for value in item) for item in grid["occupied_cells_xy"]}
    raw_csv = scene_dir / "mworks_smoke" / "raw" / f"sunray150_ue_{scene_id}_linear_mpc_smoke.csv"
    metrics_json = scene_dir / "mworks_smoke" / "metrics" / f"sunray150_ue_{scene_id}_linear_mpc_smoke.json"
    rows = read_csv(raw_csv)
    if not rows:
        raise ValueError(f"empty MWORKS raw CSV: {raw_csv}")
    if not {"time", "x", "y", "x_ref", "y_ref"} <= set(rows[0]):
        raise ValueError(f"raw CSV missing required columns: {raw_csv}")

    actual = check_rows_against_grid(
        rows=rows,
        x_key="x",
        y_key="y",
        label="actual_mworks_position",
        occupied_cells=occupied_cells,
        origin_xy_m=origin_xy_m,
        resolution_m=resolution_m,
        grid_size=grid_size,
        max_violations=max_violations,
    )
    reference = check_rows_against_grid(
        rows=rows,
        x_key="x_ref",
        y_key="y_ref",
        label="mworks_reference_position",
        occupied_cells=occupied_cells,
        origin_xy_m=origin_xy_m,
        resolution_m=resolution_m,
        grid_size=grid_size,
        max_violations=max_violations,
    )

    metrics: dict[str, Any] = {}
    if metrics_json.exists():
        metrics = load_json(metrics_json)

    report = {
        "schema": "mosim.mworks_ue_scene_truth_collision_check.v1",
        "scene_id": scene_id,
        "source": metrics.get("source", "MWORKS_MCP"),
        "evidence_level": metrics.get("evidence_level", "real_sysplorer_mcp_ue_scene_control_smoke"),
        "claim_boundary": [
            "This checks the MWORKS simulated trajectory against UE scene-truth occupancy.",
            "A pass here is still smoke evidence, not completed autonomous navigation or FAST-LIO localization.",
            "The global occupancy truth is used only for validation after simulation, not as a planner input.",
        ],
        "inputs": {
            "occupancy_grid": rel(scene_dir / "occupancy_grid.json"),
            "raw_csv": rel(raw_csv),
            "metrics_json": rel(metrics_json),
        },
        "grid": {
            "origin_xy_m": origin_xy_m,
            "resolution_m": resolution_m,
            "size": grid_size,
            "occupied_cell_count": len(occupied_cells),
        },
        "actual": actual,
        "reference": reference,
        "pass": bool(actual["collision_free_against_truth"] and reference["collision_free_against_truth"]),
    }
    collision_dir = scene_dir / "mworks_smoke" / "collision"
    collision_dir.mkdir(parents=True, exist_ok=True)
    (collision_dir / "mworks_scene_truth_collision.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def write_status(output_root: Path, reports: list[dict[str, Any]]) -> None:
    lines = [
        "# MWORKS UE Scene Truth Collision Status",
        "",
        "This status validates MWORKS smoke trajectories against UE scene-truth occupancy after simulation.",
        "The global occupancy truth is a validation oracle only; it is not planner input.",
        "",
        "| Scene | Pass | Actual Occupied Samples | Reference Occupied Samples | Min Actual Clearance | Report |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for report in reports:
        actual = report["actual"]
        reference = report["reference"]
        report_path = output_root / report["scene_id"] / "mworks_smoke" / "collision" / "mworks_scene_truth_collision.json"
        min_clearance = actual.get("min_approx_clearance_m")
        min_clearance_text = "n/a" if min_clearance is None else f"{float(min_clearance):.4f} m"
        lines.append(
            f"| `{report['scene_id']}` | `{str(report['pass']).lower()}` | "
            f"{actual['occupied_sample_count']} | {reference['occupied_sample_count']} | "
            f"{min_clearance_text} | `{rel(report_path)}` |"
        )
    lines.extend([
        "",
        "Pass means the sampled MWORKS smoke trajectory and its reference stayed out of occupied validation cells.",
        "Fail means the controller/planner coupling needs more clearance, slower references, or a safety filter before this can be promoted beyond smoke evidence.",
    ])
    (output_root / "MWORKS_UE_SCENE_COLLISION_STATUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", action="append", default=[])
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--max-violations", type=int, default=12)
    parser.add_argument("--fail-on-violation", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = project_path(args.output_root)
    scene_ids = args.scene or list(DEFAULT_SCENES)
    reports = [check_scene(output_root / scene_id.lower(), max_violations=args.max_violations) for scene_id in scene_ids]
    write_status(output_root, reports)
    for report in reports:
        actual = report["actual"]
        print(
            f"{report['scene_id']}: pass={report['pass']} "
            f"actual_occupied={actual['occupied_sample_count']} "
            f"reference_occupied={report['reference']['occupied_sample_count']}"
        )
    if args.fail_on_violation and not all(report["pass"] for report in reports):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
