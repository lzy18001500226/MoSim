r"""Mid360-driven local-grid obstacle avoidance demo in RflySim3D.

Run with RflySim3D open and RflySim's bundled Python:

    D:\PX4PSP\Python38\python.exe tools\rflysim\rflysim_mid360_reactive_avoidance.py

This is a diagnostic prototype. It reads Mid360 point clouds, builds a local
occupancy grid in the body frame, runs A* toward a short-horizon goal, and drives
the RflySim3D actor from the planned local path. It is not a formal demo, not a
PX4/CopterSim dynamics proof, and its optional test boxes are not real buildings.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import heapq
from collections import deque
from pathlib import Path

import numpy as np

RFY = Path(r"D:\PX4PSP\RflySimAPIs")
SDK = RFY / "RflySimSDK"
sys.path[:0] = [
    str(SDK),
    str(SDK / "ue"),
    str(SDK / "vision"),
    str(RFY / "8.RflySimVision" / "0.ApiExps" / "10.Mid360Demo"),
]

import UE4CtrlAPI  # noqa: E402
import VisionCaptureApi  # noqa: E402


MID360_CONFIG = RFY / "8.RflySimVision" / "0.ApiExps" / "10.Mid360Demo" / "Config_udp.json"


def normalize(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v)
    if norm < 1e-9:
        return v * 0.0
    return v / norm


def cloud_xyz(cloud: np.ndarray) -> np.ndarray:
    flat = cloud.reshape(-1, cloud.shape[-1]) if cloud.ndim >= 2 else cloud.reshape(-1, 1)
    finite = flat[np.isfinite(flat).all(axis=1)]
    if finite.shape[1] < 3 or len(finite) == 0:
        return np.empty((0, 3), dtype=float)
    return finite[:, :3].astype(float)


def cloud_summary(xyz: np.ndarray) -> str:
    if len(xyz) == 0:
        return "empty"
    mins = np.min(xyz, axis=0)
    maxs = np.max(xyz, axis=0)
    return "min=({:.2f},{:.2f},{:.2f}) max=({:.2f},{:.2f},{:.2f})".format(
        mins[0], mins[1], mins[2], maxs[0], maxs[1], maxs[2]
    )


def world_to_body(vec_world: np.ndarray, yaw: float) -> np.ndarray:
    c = math.cos(yaw)
    s = math.sin(yaw)
    return np.array([c * vec_world[0] + s * vec_world[1], -s * vec_world[0] + c * vec_world[1], vec_world[2]])


def body_to_world(vec_body: np.ndarray, yaw: float) -> np.ndarray:
    c = math.cos(yaw)
    s = math.sin(yaw)
    return np.array([c * vec_body[0] - s * vec_body[1], s * vec_body[0] + c * vec_body[1], vec_body[2]])


def wrap_angle(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def slew_yaw(current: float, target: float, max_delta: float) -> float:
    return current + float(np.clip(wrap_angle(target - current), -max_delta, max_delta))


def cloud_to_body_candidates(xyz: np.ndarray, pos: np.ndarray, yaw: float) -> list[tuple[str, np.ndarray]]:
    if len(xyz) == 0:
        empty = np.empty((0, 3), dtype=float)
        return [("empty", empty)]
    body_direct = xyz.copy()
    body_from_world = np.array([world_to_body(point - pos, yaw) for point in xyz], dtype=float)
    # Some RflySim point-cloud examples use a horizontal-axis convention that
    # differs from the simple x-forward/y-left assumption. Keep a swapped
    # candidate and select the one with the most useful local hits.
    body_swapped = np.column_stack((xyz[:, 1], xyz[:, 0], xyz[:, 2]))
    body_world_swapped = np.column_stack((xyz[:, 1] - pos[1], xyz[:, 0] - pos[0], xyz[:, 2] - pos[2]))
    body_world_swapped_yaw = np.array(
        [world_to_body(np.array([point[1] - pos[1], point[0] - pos[0], point[2] - pos[2]]), yaw) for point in xyz],
        dtype=float,
    )
    return [
        ("world", body_from_world),
        ("world_swapped_yaw", body_world_swapped_yaw),
        ("world_swapped", body_world_swapped),
        ("body", body_direct),
        ("swapped", body_swapped),
    ]


def candidate_score(xyz_body: np.ndarray, forward_m: float, side_m: float) -> int:
    if len(xyz_body) == 0:
        return 0
    local = (
        (xyz_body[:, 0] > 0.1)
        & (xyz_body[:, 0] < forward_m)
        & (np.abs(xyz_body[:, 1]) < side_m)
    )
    return int(np.sum(local))


def select_body_cloud(xyz: np.ndarray, pos: np.ndarray, yaw: float, forward_m: float, side_m: float) -> tuple[str, np.ndarray]:
    candidates = cloud_to_body_candidates(xyz, pos, yaw)
    name, body = max(candidates, key=lambda item: candidate_score(item[1], forward_m, side_m))
    return name, body


def transform_cloud(xyz: np.ndarray, pos: np.ndarray, yaw: float, mode: str, forward_m: float, side_m: float) -> tuple[str, np.ndarray]:
    if mode == "auto":
        return select_body_cloud(xyz, pos, yaw, forward_m, side_m)
    candidates = dict(cloud_to_body_candidates(xyz, pos, yaw))
    if mode not in candidates:
        raise ValueError(f"Unsupported cloud frame mode: {mode}")
    return mode, candidates[mode]


def clear_debug_markers(ue, ids: range) -> None:
    for marker_id in ids:
        ue.sendUE4PosNew(
            marker_id,
            -3,
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            windowID=-1,
        )


def draw_debug_markers(
    ue,
    pos: np.ndarray,
    yaw: float,
    plan_body: np.ndarray,
    cloud_body: np.ndarray,
    plan_ids: range,
    obstacle_ids: range,
) -> None:
    plan_count = min(len(plan_body), len(plan_ids))
    for marker_id, point_body in zip(list(plan_ids)[:plan_count], plan_body[:plan_count]):
        point_world = pos + body_to_world(np.array([point_body[0], point_body[1], 0.0]), yaw)
        ue.sendUE4PosScale(
            copterID=marker_id,
            vehicleType=815,
            PosE=[float(point_world[0]), float(point_world[1]), float(pos[2] - 0.05)],
            AngEuler=[0.0, 0.0, 0.0],
            Scale=[0.16, 0.16, 0.16],
            windowID=-1,
        )
    for marker_id in list(plan_ids)[plan_count:]:
        ue.sendUE4PosNew(marker_id, -3, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], windowID=-1)

    local_hits = cloud_body[
        (cloud_body[:, 0] > 0.15)
        & (cloud_body[:, 0] < 6.0)
        & (np.abs(cloud_body[:, 1]) < 3.0)
    ] if len(cloud_body) else np.empty((0, 3))
    obstacle_count = min(len(local_hits), len(obstacle_ids))
    for marker_id, point_body in zip(list(obstacle_ids)[:obstacle_count], local_hits[:obstacle_count]):
        point_world = pos + body_to_world(np.array([point_body[0], point_body[1], 0.0]), yaw)
        ue.sendUE4PosScale(
            copterID=marker_id,
            vehicleType=815,
            PosE=[float(point_world[0]), float(point_world[1]), float(pos[2] - 0.15)],
            AngEuler=[0.0, 0.0, 0.0],
            Scale=[0.12, 0.12, 0.12],
            windowID=-1,
        )
    for marker_id in list(obstacle_ids)[obstacle_count:]:
        ue.sendUE4PosNew(marker_id, -3, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], windowID=-1)


class LocalGridPlanner:
    def __init__(self, forward_m: float, side_m: float, resolution_m: float, inflation_m: float):
        self.forward_m = forward_m
        self.side_m = side_m
        self.resolution_m = resolution_m
        self.inflation_cells = max(1, int(math.ceil(inflation_m / resolution_m)))
        self.rows = int(round(forward_m / resolution_m)) + 1
        self.cols = int(round(2.0 * side_m / resolution_m)) + 1

    def to_cell(self, point_xy: np.ndarray) -> tuple[int, int]:
        row = int(round(point_xy[0] / self.resolution_m))
        col = int(round((point_xy[1] + self.side_m) / self.resolution_m))
        return row, col

    def to_xy(self, cell: tuple[int, int]) -> np.ndarray:
        row, col = cell
        return np.array([row * self.resolution_m, col * self.resolution_m - self.side_m], dtype=float)

    def build_occupancy(self, xyz: np.ndarray, z_limit_m: float) -> np.ndarray:
        occ = np.zeros((self.rows, self.cols), dtype=bool)
        if len(xyz) == 0:
            return occ
        valid = (
            (xyz[:, 0] > 0.15)
            & (xyz[:, 0] < self.forward_m)
            & (np.abs(xyz[:, 1]) < self.side_m)
            & (xyz[:, 2] > -z_limit_m)
            & (xyz[:, 2] < z_limit_m)
        )
        for x, y, _z in xyz[valid]:
            row, col = self.to_cell(np.array([x, y]))
            r0 = max(0, row - self.inflation_cells)
            r1 = min(self.rows - 1, row + self.inflation_cells)
            c0 = max(0, col - self.inflation_cells)
            c1 = min(self.cols - 1, col + self.inflation_cells)
            occ[r0 : r1 + 1, c0 : c1 + 1] = True
        # Never block the cell occupied by the vehicle itself.
        start = self.to_cell(np.array([0.0, 0.0]))
        occ[start] = False
        return occ

    def choose_goal_cell(self, goal_body: np.ndarray, occ: np.ndarray) -> tuple[int, int]:
        x = float(np.clip(goal_body[0], 1.0, self.forward_m - self.resolution_m))
        y = float(np.clip(goal_body[1], -self.side_m + self.resolution_m, self.side_m - self.resolution_m))
        preferred = self.to_cell(np.array([x, y]))
        if not occ[preferred]:
            return preferred
        queue: deque[tuple[int, int]] = deque([preferred])
        visited = {preferred}
        while queue:
            row, col = queue.popleft()
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
                nr, nc = row + dr, col + dc
                nxt = (nr, nc)
                if 0 <= nr < self.rows and 0 <= nc < self.cols and nxt not in visited:
                    if not occ[nxt]:
                        return nxt
                    visited.add(nxt)
                    queue.append(nxt)
        return self.to_cell(np.array([1.0, 0.0]))

    def astar(self, occ: np.ndarray, start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
        moves = [
            (-1, 0, 1.0),
            (1, 0, 1.0),
            (0, -1, 1.0),
            (0, 1, 1.0),
            (-1, -1, 1.414),
            (-1, 1, 1.414),
            (1, -1, 1.414),
            (1, 1, 1.414),
        ]
        open_heap: list[tuple[float, tuple[int, int]]] = []
        heapq.heappush(open_heap, (0.0, start))
        came_from: dict[tuple[int, int], tuple[int, int]] = {}
        g_score = {start: 0.0}
        while open_heap:
            _score, current = heapq.heappop(open_heap)
            if current == goal:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
            for dr, dc, cost in moves:
                nr, nc = current[0] + dr, current[1] + dc
                nxt = (nr, nc)
                if not (0 <= nr < self.rows and 0 <= nc < self.cols) or occ[nxt]:
                    continue
                tentative = g_score[current] + cost
                if tentative < g_score.get(nxt, float("inf")):
                    came_from[nxt] = current
                    g_score[nxt] = tentative
                    heuristic = math.hypot(goal[0] - nr, goal[1] - nc)
                    # Penalize excessive side motion but allow it when needed.
                    side_penalty = 0.02 * abs(nc - self.to_cell(np.array([0.0, 0.0]))[1])
                    heapq.heappush(open_heap, (tentative + heuristic + side_penalty, nxt))
        return [start]

    def best_escape_goal(self, occ: np.ndarray, start: tuple[int, int]) -> tuple[int, int]:
        candidates: list[tuple[float, tuple[int, int]]] = []
        preferred_rows = range(self.rows - 1, max(start[0] + 2, self.rows // 2), -1)
        center_col = start[1]
        for row in preferred_rows:
            for col in range(self.cols):
                if occ[row, col]:
                    continue
                # Prefer forward progress and visible side motion over getting
                # stuck at the current cell when the straight corridor is full.
                forward_bonus = row * 1.5
                side_distance = abs(col - center_col)
                side_bonus = min(side_distance, self.cols // 3)
                center_penalty = 0.15 * side_distance
                score = forward_bonus + side_bonus - center_penalty
                candidates.append((score, (row, col)))
        if not candidates:
            return start
        candidates.sort(reverse=True)
        return candidates[0][1]

    def plan(self, xyz: np.ndarray, goal_body: np.ndarray, z_limit_m: float) -> tuple[np.ndarray, dict]:
        occ = self.build_occupancy(xyz, z_limit_m=z_limit_m)
        start = self.to_cell(np.array([0.0, 0.0]))
        goal = self.choose_goal_cell(goal_body, occ)
        path_cells = self.astar(occ, start, goal)
        used_escape_goal = False
        if len(path_cells) <= 1:
            goal = self.best_escape_goal(occ, start)
            path_cells = self.astar(occ, start, goal)
            used_escape_goal = True
        path_xy = np.array([self.to_xy(cell) for cell in path_cells], dtype=float)
        return path_xy, {
            "occupied_cells": int(np.sum(occ)),
            "path_len": int(len(path_cells)),
            "goal_cell": goal,
            "escape_goal": used_escape_goal,
            "front_blocked": bool(np.any(occ[1 : min(self.rows, int(3.0 / self.resolution_m)), :])),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-s", type=float, default=45.0)
    parser.add_argument("--rate-hz", type=float, default=20.0)
    parser.add_argument("--speed-mps", type=float, default=1.1)
    parser.add_argument("--vehicle-id", type=int, default=1)
    parser.add_argument("--altitude-m", type=float, default=2.0)
    parser.add_argument("--start-x", type=float, default=0.0)
    parser.add_argument("--start-y", type=float, default=30.0)
    parser.add_argument("--goal-x", type=float, default=0.0)
    parser.add_argument("--goal-y", type=float, default=46.0)
    parser.add_argument("--avoid-distance-m", type=float, default=3.0)
    parser.add_argument("--udp-port", type=int, default=9999)
    parser.add_argument("--local-forward-m", type=float, default=6.0)
    parser.add_argument("--local-side-m", type=float, default=3.0)
    parser.add_argument("--local-grid-m", type=float, default=0.25)
    parser.add_argument("--inflation-m", type=float, default=0.45)
    parser.add_argument(
        "--yaw-rate-limit-deg-s",
        type=float,
        default=35.0,
        help="Limit displayed yaw rate to avoid visual spinning when local plans jump.",
    )
    parser.add_argument(
        "--cloud-frame",
        choices=["body", "world", "world_swapped_yaw", "world_swapped", "swapped", "auto"],
        default="body",
        help="Mid360 point-cloud frame transform. Use body for the RflySim3D direct sensor smoke test; auto is diagnostics only.",
    )
    parser.add_argument(
        "--show-debug-markers",
        action="store_true",
        help="Show per-frame local path and point-cloud debug markers. This is useful for debugging but can make RflySim3D flicker.",
    )
    parser.add_argument(
        "--spawn-test-obstacles",
        action="store_true",
        help="Spawn temporary Box actors for sensor debugging only. Do not use as formal wall/building obstacles.",
    )
    args = parser.parse_args()

    ue = UE4CtrlAPI.UE4CtrlAPI()
    for cmd in (
        "t.MaxFPS 60",
        "r.setres 1280x720w",
        "RflyChangeMapbyName SLAMScene",
        "RflyCameraFovDegrees 95",
        "RflyShowTextTime Mid360_reactive_avoidance_start 8",
    ):
        ue.sendUE4Cmd(cmd, windowID=-1)
        time.sleep(0.25)

    pos = np.array([args.start_x, args.start_y, -args.altitude_m], dtype=float)
    goal = np.array([args.goal_x, args.goal_y, -args.altitude_m], dtype=float)
    yaw = math.atan2(goal[1] - pos[1], goal[0] - pos[0])
    ue.sendUE4PosNew(
        copterID=args.vehicle_id,
        vehicleType=3,
        PosE=pos.tolist(),
        AngEuler=[0.0, 0.0, yaw],
        PWMs=[5600] * 4 + [0] * 4,
        windowID=-1,
    )
    ue.sendUE4LabelID(args.vehicle_id, "Mid360 reactive", fontSize=36, RGB=[0, 255, 255], windowID=-1)
    for cmd in (
        f"RflyChangeViewKeyCmd B {args.vehicle_id}",
        "RflyChangeViewKeyCmd T 1",
        "RflyCameraPosAng 8 18 -10 0 -25 28",
        "RflyShowTextTime FOCUS_DRONE_ID_1 8",
    ):
        ue.sendUE4Cmd(cmd, windowID=-1)
        time.sleep(0.15)
    ue.sendUE4PosScale(
        copterID=9200,
        vehicleType=815,
        PosE=goal.tolist(),
        AngEuler=[0.0, 0.0, 0.0],
        Scale=[0.42, 0.42, 0.42],
        windowID=-1,
    )
    ue.sendUE4LabelID(9200, "GOAL", fontSize=24, RGB=[255, 230, 0], windowID=-1)
    if args.spawn_test_obstacles:
        obstacle_positions = (
            [args.start_x - 1.5, args.start_y + 4.0, -args.altitude_m],
            [args.start_x - 0.9, args.start_y + 4.0, -args.altitude_m],
            [args.start_x - 0.3, args.start_y + 4.0, -args.altitude_m],
            [args.start_x + 0.3, args.start_y + 4.0, -args.altitude_m],
            [args.start_x + 0.9, args.start_y + 4.0, -args.altitude_m],
            [args.start_x + 1.5, args.start_y + 4.0, -args.altitude_m],
            [args.start_x - 1.0, args.start_y + 8.0, -args.altitude_m],
            [args.start_x - 0.4, args.start_y + 8.0, -args.altitude_m],
            [args.start_x + 0.2, args.start_y + 8.0, -args.altitude_m],
            [args.start_x + 0.8, args.start_y + 8.0, -args.altitude_m],
        )
        for idx, obstacle in enumerate(obstacle_positions):
            ue.sendUE4PosScale(
                copterID=9100 + idx,
                vehicleType=815,
                PosE=obstacle,
                AngEuler=[0.0, 0.0, 0.0],
                Scale=[0.35, 0.35, 2.0],
                windowID=-1,
            )
    time.sleep(1.0)

    config_path = Path(r"C:\Users\HP\Desktop\Quadrotor\.tmp\mid360_reactive_config.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config = json.loads(MID360_CONFIG.read_text(encoding="utf-8"))
    config["VisionSensors"][0]["TargetCopter"] = int(args.vehicle_id)
    config["VisionSensors"][0]["SendProtocol"] = [1, 127, 0, 0, 1, int(args.udp_port), 0, 0]
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    vis = VisionCaptureApi.VisionCaptureApi()
    vis.jsonLoad(jsonPath=str(config_path))
    ok = vis.sendReqToUE4()
    print(f"sendReqToUE4={ok}", flush=True)
    vis.startImgCap()

    planner = LocalGridPlanner(
        forward_m=args.local_forward_m,
        side_m=args.local_side_m,
        resolution_m=args.local_grid_m,
        inflation_m=args.inflation_m,
    )
    latest_cloud = np.empty((0, 3), dtype=float)
    latest_cloud_mode = "empty"
    latest_plan_body = np.array([[1.0, 0.0]], dtype=float)
    latest_info = {"occupied_cells": 0, "path_len": 1, "front_blocked": False, "escape_goal": False}
    plan_marker_ids = range(9300, 9318)
    obstacle_marker_ids = range(9350, 9374)
    if args.show_debug_markers:
        clear_debug_markers(ue, plan_marker_ids)
        clear_debug_markers(ue, obstacle_marker_ids)
    dt = 1.0 / args.rate_hz
    start = time.time()
    steps = 0
    blocked_steps = 0
    while time.time() - start < args.duration_s:
        if vis.hasData and vis.hasData[0]:
            cloud = np.asarray(vis.Img[0])
            raw_cloud = cloud_xyz(cloud)
            latest_cloud_mode, latest_cloud = transform_cloud(
                raw_cloud,
                pos,
                yaw,
                mode=args.cloud_frame,
                forward_m=args.local_forward_m,
                side_m=args.local_side_m,
            )
            goal_body = world_to_body(goal - pos, yaw)
            latest_plan_body, latest_info = planner.plan(latest_cloud, goal_body, z_limit_m=5.0)
            if args.show_debug_markers:
                draw_debug_markers(
                    ue,
                    pos,
                    yaw,
                    latest_plan_body,
                    latest_cloud,
                    plan_marker_ids,
                    obstacle_marker_ids,
                )
            vis.hasData[0] = False

        to_goal = goal - pos
        to_goal[2] = 0.0
        if np.linalg.norm(to_goal[:2]) < 0.35:
            print("goal_reached", flush=True)
            break

        lookahead_idx = min(3, len(latest_plan_body) - 1)
        local_target_body = np.array([1.0, 0.0, 0.0], dtype=float)
        if len(latest_plan_body) > 1:
            local_target_body[:2] = latest_plan_body[lookahead_idx]
        local_target_world = body_to_world(local_target_body, yaw)
        desired = normalize(0.55 * normalize(to_goal) + 1.35 * normalize(local_target_world))
        if latest_info["front_blocked"]:
            blocked_steps += 1
        velocity = desired * args.speed_mps
        pos += velocity * dt
        pos[2] = -args.altitude_m
        target_yaw = math.atan2(desired[1], desired[0])
        yaw = slew_yaw(yaw, target_yaw, math.radians(args.yaw_rate_limit_deg_s) * dt)
        rpm = 5600.0 + 300.0 * math.sin(steps * 0.25)
        ue.sendUE4PosNew(
            copterID=args.vehicle_id,
            vehicleType=3,
            PosE=pos.tolist(),
            AngEuler=[0.0, 0.0, yaw],
            VelE=[float(velocity[0]), float(velocity[1]), 0.0],
            PWMs=[rpm] * 4 + [0] * 4,
            windowID=-1,
        )
        if steps % 20 == 0:
            print(
                "step={} pos=({:.2f},{:.2f}) occupied={} path_len={} front_blocked={} escape={} points={} mode={} {}".format(
                    steps,
                    pos[0],
                    pos[1],
                    latest_info["occupied_cells"],
                    latest_info["path_len"],
                    latest_info["front_blocked"],
                    latest_info.get("escape_goal", False),
                    len(latest_cloud),
                    latest_cloud_mode,
                    cloud_summary(latest_cloud),
                ),
                flush=True,
            )
        steps += 1
        time.sleep(dt)

    ue.sendUE4Cmd("RflyShowTextTime Mid360_reactive_avoidance_done 8", windowID=-1)
    print(f"done steps={steps} blocked_steps={blocked_steps} final=({pos[0]:.2f},{pos[1]:.2f},{pos[2]:.2f})", flush=True)
    time.sleep(0.2)
    os._exit(0)


if __name__ == "__main__":
    raise SystemExit(main())
