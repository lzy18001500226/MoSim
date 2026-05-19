r"""Headless ESDF/Voronoi path-planning smoke test for RflySim.

Run with RflySim's bundled Python:

    D:\PX4PSP\Python38\python.exe tools\rflysim\rflysim_esdf_path_smoke.py

This validates the map-to-path layer only. It does not require PX4, QGC,
CopterSim, or RflySim3D to be open.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path

import numpy as np
import yaml
from PIL import Image
from scipy.interpolate import interp1d
from scipy.ndimage import distance_transform_edt
from skimage.morphology import medial_axis


DEFAULT_MAP_DIR = Path(
    r"D:\PX4PSP\RflySimAPIs\8.RflySimVision\2.AdvExps\e16_ESDFPathPlan\maps"
)


def load_map(map_dir: Path) -> tuple[dict, np.ndarray]:
    with (map_dir / "map_cropped.yaml").open("r", encoding="utf-8") as f:
        params = yaml.safe_load(f)
    image_path = map_dir / params["image"]
    raw = np.asarray(Image.open(image_path).convert("L"))
    return params, raw


def nearest_free(mask_free: np.ndarray, point: tuple[int, int]) -> tuple[int, int]:
    rows, cols = mask_free.shape
    r0 = int(np.clip(point[0], 0, rows - 1))
    c0 = int(np.clip(point[1], 0, cols - 1))
    if mask_free[r0, c0]:
        return r0, c0

    visited = np.zeros(mask_free.shape, dtype=bool)
    queue: deque[tuple[int, int]] = deque([(r0, c0)])
    visited[r0, c0] = True
    while queue:
        r, c = queue.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr, nc]:
                if mask_free[nr, nc]:
                    return nr, nc
                visited[nr, nc] = True
                queue.append((nr, nc))
    raise RuntimeError("No free cell found in map.")


def corner_free_point(
    free: np.ndarray,
    esdf: np.ndarray,
    corner: tuple[float, float],
    min_clearance_m: float,
) -> tuple[int, int]:
    rows, cols = free.shape
    rr, cc = np.where(free & (esdf >= min_clearance_m))
    if len(rr) == 0:
        rr, cc = np.where(free)
    target = np.asarray([corner[0] * (rows - 1), corner[1] * (cols - 1)])
    scale = np.asarray([max(rows - 1, 1), max(cols - 1, 1)])
    dist2 = np.sum(((np.column_stack((rr, cc)) - target) / scale) ** 2, axis=1)
    idx = int(np.argmin(dist2))
    return int(rr[idx]), int(cc[idx])


def nearest_skeleton(voronoi: np.ndarray, point: tuple[int, int]) -> tuple[int, int]:
    ys, xs = np.where(voronoi)
    if len(ys) == 0:
        return point
    d2 = (ys - point[0]) ** 2 + (xs - point[1]) ** 2
    idx = int(np.argmin(d2))
    return int(ys[idx]), int(xs[idx])


def bfs_on_skeleton(voronoi: np.ndarray, start: tuple[int, int], goal: tuple[int, int]) -> np.ndarray:
    rows, cols = voronoi.shape
    skel_start = nearest_skeleton(voronoi, start)
    skel_goal = nearest_skeleton(voronoi, goal)
    queue: deque[tuple[tuple[int, int], list[tuple[int, int]]]] = deque([(skel_start, [skel_start])])
    visited = {skel_start}
    while queue:
        current, path = queue.popleft()
        if current == skel_goal:
            return np.asarray([start, *path, goal], dtype=float)
        r, c = current
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nr, nc = r + dr, c + dc
            nxt = (nr, nc)
            if 0 <= nr < rows and 0 <= nc < cols and nxt not in visited:
                if voronoi[nr, nc] or nxt == skel_goal:
                    visited.add(nxt)
                    queue.append((nxt, [*path, nxt]))
    raise RuntimeError(f"No Voronoi skeleton path from {start} to {goal}.")


def resample_path(path: np.ndarray, num_points: int) -> np.ndarray:
    if len(path) < 2:
        return path
    dist = np.sqrt(np.sum(np.diff(path, axis=0) ** 2, axis=1))
    cumulative = np.insert(np.cumsum(dist), 0, 0.0)
    if cumulative[-1] <= 0:
        return path
    f_row = interp1d(cumulative, path[:, 0], kind="linear")
    f_col = interp1d(cumulative, path[:, 1], kind="linear")
    samples = np.linspace(0.0, cumulative[-1], num_points)
    return np.column_stack((f_row(samples), f_col(samples)))


def optimize_path(
    path: np.ndarray,
    esdf: np.ndarray,
    num_iters: int = 50,
    safe_dist_m: float = 0.25,
    resolution_m: float = 0.05,
) -> np.ndarray:
    if len(path) < 3:
        return path
    safe_dist_px = safe_dist_m / resolution_m
    grad_row, grad_col = np.gradient(esdf / resolution_m)
    tuned = path.copy()
    alpha = 0.04
    smooth_weight = 0.45
    obs_weight = 0.65
    rows, cols = esdf.shape
    for _ in range(num_iters):
        smooth = np.zeros_like(tuned)
        smooth[1:-1] = tuned[1:-1] - 0.5 * (tuned[:-2] + tuned[2:])
        obstacle = np.zeros_like(tuned)
        for i in range(1, len(tuned) - 1):
            r = int(np.clip(round(tuned[i, 0]), 0, rows - 1))
            c = int(np.clip(round(tuned[i, 1]), 0, cols - 1))
            dist_px = esdf[r, c] / resolution_m
            if dist_px < safe_dist_px:
                factor = safe_dist_px - dist_px
                obstacle[i, 0] = -factor * grad_row[r, c]
                obstacle[i, 1] = -factor * grad_col[r, c]
        tuned[1:-1] -= alpha * (smooth_weight * smooth[1:-1] + obs_weight * obstacle[1:-1])
        tuned[0] = path[0]
        tuned[-1] = path[-1]
    return tuned


def path_metrics(path: np.ndarray, esdf: np.ndarray, resolution_m: float) -> dict:
    clipped = np.column_stack(
        (
            np.clip(np.rint(path[:, 0]).astype(int), 0, esdf.shape[0] - 1),
            np.clip(np.rint(path[:, 1]).astype(int), 0, esdf.shape[1] - 1),
        )
    )
    clearances = esdf[clipped[:, 0], clipped[:, 1]]
    segment_px = np.sqrt(np.sum(np.diff(path, axis=0) ** 2, axis=1))
    return {
        "points": int(len(path)),
        "length_m": float(np.sum(segment_px) * resolution_m),
        "min_clearance_m": float(np.min(clearances)),
        "mean_clearance_m": float(np.mean(clearances)),
        "start_pixel": [float(path[0, 0]), float(path[0, 1])],
        "goal_pixel": [float(path[-1, 0]), float(path[-1, 1])],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map-dir", type=Path, default=DEFAULT_MAP_DIR)
    parser.add_argument("--points", type=int, default=220)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--path-output", type=Path)
    args = parser.parse_args()

    params, raw = load_map(args.map_dir)
    resolution = float(params["resolution"])
    obstacle = raw < 250
    free = ~obstacle
    esdf = distance_transform_edt(free, sampling=resolution) - distance_transform_edt(obstacle, sampling=resolution)
    voronoi = medial_axis(free)

    start = corner_free_point(free, esdf, corner=(0.82, 0.18), min_clearance_m=0.25)
    goal = corner_free_point(free, esdf, corner=(0.18, 0.82), min_clearance_m=0.25)
    if np.linalg.norm(np.asarray(start) - np.asarray(goal)) < 10:
        start = nearest_free(free, (raw.shape[0] * 3 // 4, raw.shape[1] // 5))
        goal = nearest_free(free, (raw.shape[0] // 4, raw.shape[1] * 4 // 5))

    skeleton_path = bfs_on_skeleton(voronoi, start, goal)
    sampled = resample_path(skeleton_path, args.points)
    path = optimize_path(sampled, esdf, resolution_m=resolution)
    metrics = path_metrics(path, esdf, resolution)
    metrics.update(
        {
            "source": "rflysim_esdf_map_to_path_smoke",
            "map_dir": str(args.map_dir),
            "map_shape": [int(raw.shape[0]), int(raw.shape[1])],
            "resolution_m": resolution,
            "obstacle_pixels": int(np.sum(obstacle)),
            "free_pixels": int(np.sum(free)),
        }
    )

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.path_output:
        args.path_output.parent.mkdir(parents=True, exist_ok=True)
        np.save(args.path_output, path)

    print(json.dumps(metrics, ensure_ascii=False, indent=2), flush=True)
    return 0 if metrics["min_clearance_m"] > 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
