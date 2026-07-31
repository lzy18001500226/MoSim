#!/usr/bin/env python3
"""导出 OpenBlocks 地图的全部障碍几何，供 Syslab 绘图脚本读取。

复用 plan_astar_min_snap 的两个展开函数，保证与规划器口径完全一致：
  expand_wall_groups      -> 16 个墙盒（L/T 臂已展开）
  expand_random_obstacles -> 7102 个 0.20 m 随机柱（seed 20260518 可复现）
合计 7118 = truth_obstacle_count。

墙按 min/max 盒输出（绘图画闭合矩形），随机柱只输出中心点：7102 个盒子
逐个画闭合折线会产生 7102 条曲线，TyPlot 图例与渲染都吃不消，散点足够。
"""

from __future__ import annotations

import json
from pathlib import Path

from plan_astar_min_snap import expand_random_obstacles, expand_wall_groups, read_yaml

BASE_DIR = Path(r"C:\Users\HP\Desktop\MoSim")
MAP_YAML = BASE_DIR / "Config" / "planners" / "astar_min_snap" / "map_open_blocks.yaml"
OUT_JSON = BASE_DIR / "Results" / "planning" / "_openblocks_obstacles.json"


def main() -> None:
    config = read_yaml(MAP_YAML)
    config = expand_wall_groups(config)
    config = expand_random_obstacles(config)
    obstacles = config["map"]["obstacles"]

    walls = [o for o in obstacles if o.get("wall_group_id")]
    columns = [o for o in obstacles if o.get("random_cluster")]
    others = [o for o in obstacles if not o.get("wall_group_id") and not o.get("random_cluster")]

    payload = {
        "source_yaml": str(MAP_YAML),
        "total_obstacles": len(obstacles),
        "wall_box_count": len(walls),
        "random_column_count": len(columns),
        "other_count": len(others),
        "walls": [
            {"wall_group_id": o["wall_group_id"], "min": o["min"], "max": o["max"]}
            for o in walls
        ],
        "column_centers_xy": [
            [0.5 * (o["min"][0] + o["max"][0]), 0.5 * (o["min"][1] + o["max"][1])]
            for o in columns
        ],
        "column_size_m": columns[0]["column_size_m"] if columns else None,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"walls={len(walls)} columns={len(columns)} others={len(others)} total={len(obstacles)}")
    print(f"-> {OUT_JSON}")


if __name__ == "__main__":
    main()
