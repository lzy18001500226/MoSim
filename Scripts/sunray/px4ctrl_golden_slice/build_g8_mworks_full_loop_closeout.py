#!/usr/bin/env python3
"""Build the G8 MWORKS full-loop closeout package.

This is a packaging and evidence-validation gate. It does not start MWORKS,
Gazebo, PX4, MAVROS, ROS, or RViz.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


DEFAULT_M1_DIR = "Results/sunray_ros1/px4ctrl_mworks_goal5_m1_20260629_084200"
DEFAULT_G5_DIR = "Results/sunray_ros1/px4ctrl_g5_offline_20260629_084406"
DEFAULT_G6_C_ABI_DIR = "Results/sunray_ros1/px4ctrl_g6_c_abi_20260629_084417"
DEFAULT_M4A_DIR = "Results/sunray_ros1/px4ctrl_mworks_goal5_m4a_cfunction_20260629_092411"
DEFAULT_G7A_DIR = "Results/sunray_ros1/px4ctrl_g7a_ros_sunray_adapter_gate_20260629_101000"
DEFAULT_G7B_DIR = "Results/sunray_ros1/px4ctrl_g7b_gazebo_ab_takeoff_hover_land_20260629_105702"
DEFAULT_DIFF_SINGLE_DIR = "Results/sunray_ros1/review_diff_interactive_guard_20260629_002228"
DEFAULT_DIFF_SWARM_DIR = "Results/sunray_ros1/sunray_ros1_goal5_diff_planner_3uav_20260629_023923"
DEFAULT_G7C_DIR = "Results/sunray_ros1/sunray_ros1_goal5_diff_planner_3uav_generated_core_frozen_targets_20260629_111346"


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def read_json(path: Path) -> tuple[dict[str, Any], str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - closeout should preserve exact parse failure.
        return {}, f"{type(exc).__name__}: {exc}"
    if not isinstance(data, dict):
        return {}, "top-level JSON is not an object"
    return data, ""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(path: Path, root: Path, role: str, required: bool = True) -> dict[str, Any]:
    item: dict[str, Any] = {
        "path": rel(path, root),
        "role": role,
        "required": required,
        "exists": path.exists(),
    }
    if path.exists() and path.is_file():
        item["bytes"] = path.stat().st_size
        item["sha256"] = sha256(path)
    return item


def status_from_json(path: Path, root: Path, role: str, expected: set[str] | None = None) -> dict[str, Any]:
    data, error = read_json(path)
    status = data.get("status") if data else None
    expected = expected or {"passed"}
    item: dict[str, Any] = require_file(path, root, role)
    item["json_parse_error"] = error
    item["status"] = status
    item["accepted_statuses"] = sorted(expected)
    item["accepted"] = bool(path.exists() and not error and status in expected)
    return item


def nested(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def metric_summary(metrics_path: Path) -> tuple[dict[str, Any], list[str]]:
    metrics, error = read_json(metrics_path)
    blockers: list[str] = []
    if error:
        return {"parse_error": error}, [f"cannot parse {metrics_path}: {error}"]
    summary: dict[str, Any] = {
        "status": metrics.get("status"),
        "blockers": metrics.get("blockers", []),
        "warnings": metrics.get("warnings", []),
        "uav_num": metrics.get("uav_num"),
        "execute_target_error_m": {},
        "min_inter_uav_distance_m": metrics.get("min_inter_uav_distance_m"),
        "min_inter_uav_pair": metrics.get("min_inter_uav_pair"),
    }
    if metrics.get("status") != "passed":
        blockers.append(f"{metrics_path} status is {metrics.get('status')!r}")
    if metrics.get("blockers"):
        blockers.append(f"{metrics_path} has blockers: {metrics.get('blockers')!r}")
    per_uav = metrics.get("per_uav", {})
    if isinstance(per_uav, dict):
        for uid, payload in sorted(per_uav.items()):
            if isinstance(payload, dict):
                summary["execute_target_error_m"][f"uav{uid}"] = payload.get("execute_target_error_m")
    return summary, blockers


def write_summary(path: Path, manifest: dict[str, Any]) -> None:
    g7b = manifest["gates"]["g7b_gazebo_ab"]["metrics"]
    g7c = manifest["gates"]["g7c_generated_core_swarm"]["metrics"]
    lines = [
        "# G8 MWORKS Full-Loop Closeout",
        "",
        f"- status: `{manifest['status']}`",
        f"- freeze_id: `{manifest['freeze_id']}`",
        f"- generated_core_baseline: `{manifest['generated_core_baseline']}`",
        f"- result_dir: `{manifest['result_dir']}`",
        "",
        "## Accepted Evidence",
        "",
        "| Gate | Status | Evidence |",
        "|---|---:|---|",
    ]
    for gate_name, gate in manifest["gates"].items():
        lines.append(
            f"| `{gate_name}` | `{gate['status']}` | `{gate['evidence_dir']}` |"
        )
    lines.extend(
        [
            "",
            "## Runtime Metrics",
            "",
            "- G7B single-UAV original/generated A/B: `passed`",
            f"  - original steady hover XY RMSE: `{g7b.get('original_steady_hover_xy_rmse_m')}` m",
            f"  - generated steady hover XY RMSE: `{g7b.get('generated_steady_hover_xy_rmse_m')}` m",
            f"  - original all-reference XYZ RMSE: `{g7b.get('original_all_reference_xyz_rmse_m')}` m",
            f"  - generated all-reference XYZ RMSE: `{g7b.get('generated_all_reference_xyz_rmse_m')}` m",
            "- G7C generated-core three-UAV Diff smoke: `passed`",
            f"  - execute target errors: `{g7c.get('execute_target_error_m')}` m",
            f"  - min inter-UAV distance: `{g7c.get('min_inter_uav_distance_m')}` m",
            "",
            "## Reproduce",
            "",
            "```powershell",
            "python Scripts\\sunray\\px4ctrl_golden_slice\\build_g8_mworks_full_loop_closeout.py",
            "```",
            "",
            "Optional runtime reruns, only when a regression needs fresh evidence:",
            "",
            "```powershell",
            "wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/px4ctrl_golden_slice/run_px4ctrl_g7b_gazebo_ab_gate.sh hover'",
            "wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && UAV_NUM=3 PLANNER_VARIANT=diff_planner PX4CTRL_CORE_PROFILE=mworks_generated_c bash Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh'",
            "```",
            "",
            "## Claim Boundary",
            "",
            manifest["claim_boundary"],
            "",
            "## Not Claimed",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in manifest["not_claimed"]])
    if manifest["blockers"]:
        lines.extend(["", "## Blockers", ""])
        lines.extend([f"- {item}" for item in manifest["blockers"]])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default="C:/Users/HP/Desktop/MoSim")
    parser.add_argument("--result-dir", default="")
    parser.add_argument("--m1-dir", default=DEFAULT_M1_DIR)
    parser.add_argument("--g5-dir", default=DEFAULT_G5_DIR)
    parser.add_argument("--g6-c-abi-dir", default=DEFAULT_G6_C_ABI_DIR)
    parser.add_argument("--m4a-dir", default=DEFAULT_M4A_DIR)
    parser.add_argument("--g7a-dir", default=DEFAULT_G7A_DIR)
    parser.add_argument("--g7b-dir", default=DEFAULT_G7B_DIR)
    parser.add_argument("--diff-single-dir", default=DEFAULT_DIFF_SINGLE_DIR)
    parser.add_argument("--diff-swarm-dir", default=DEFAULT_DIFF_SWARM_DIR)
    parser.add_argument("--g7c-dir", default=DEFAULT_G7C_DIR)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    result_dir = Path(args.result_dir).resolve() if args.result_dir else root / "Results" / "sunray_ros1" / f"g8_mworks_full_loop_closeout_{time.strftime('%Y%m%d_%H%M%S')}"
    result_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "m1": (root / args.m1_dir).resolve(),
        "g5": (root / args.g5_dir).resolve(),
        "g6_c_abi": (root / args.g6_c_abi_dir).resolve(),
        "m4a": (root / args.m4a_dir).resolve(),
        "g7a": (root / args.g7a_dir).resolve(),
        "g7b": (root / args.g7b_dir).resolve(),
        "diff_single": (root / args.diff_single_dir).resolve(),
        "diff_swarm": (root / args.diff_swarm_dir).resolve(),
        "g7c": (root / args.g7c_dir).resolve(),
    }

    m4a_manifest, _ = read_json(paths["m4a"] / "RUN_MANIFEST.json")
    generated_code_dir = root / str(nested(m4a_manifest, "mworks_generate_model_code", "code_dir", default=""))
    if not generated_code_dir.exists():
        generated_code_dir = paths["m4a"] / "px4ctrl_core_cfunction_codegen_strict" / "PX4CTRL_Core_CFunction_Sysblock"

    required_artifacts = [
        require_file(paths["m1"] / "RUN_MANIFEST.json", root, "M1 I/O contract manifest"),
        require_file(paths["m1"] / "IO_CONTRACT.md", root, "M1 I/O contract human-readable contract"),
        require_file(paths["m4a"] / "generate_model_code_result.json", root, "MWORKS check_model and GenerateModelCode record"),
        require_file(paths["m4a"] / "SUMMARY.md", root, "MWORKS CFunction route summary"),
        require_file(generated_code_dir / "PX4CTRL_Core_CFunction_Sysblock.c", root, "generated C source"),
        require_file(generated_code_dir / "PX4CTRL_Core_CFunction_Sysblock.h", root, "generated C header"),
        require_file(generated_code_dir / "PX4CTRL_Core_CFunction_Sysblock_data.c", root, "generated C data source"),
        require_file(generated_code_dir / "PX4CTRL_Core_CFunction_Sysblock_private.h", root, "generated private header"),
        require_file(generated_code_dir / "extern_inc" / "momodel_extern_ince1.c", root, "generated external include C source"),
        require_file(paths["g7b"] / "G7B_CLOSEOUT_ACCEPTANCE.json", root, "G7B accepted closeout"),
        require_file(paths["g7c"] / "SUMMARY.md", root, "G7C generated-core swarm smoke summary"),
    ]

    gate_status_items = {
        "m1_io_contract": status_from_json(paths["m1"] / "RUN_MANIFEST.json", root, "M1 I/O contract", {"frozen_for_offline_gate"}),
        "g5_offline_cpp": status_from_json(paths["g5"] / "gate_result.json", root, "G5 C++ offline equivalence"),
        "g6_c_abi": status_from_json(paths["g6_c_abi"] / "gate_result.json", root, "G6 C ABI equivalence"),
        "m4a_generate_model_code": status_from_json(paths["m4a"] / "generate_model_code_result.json", root, "M4A MWORKS codegen"),
        "g6_generated_c_four_way": status_from_json(paths["m4a"] / "generated_c_four_way_gate" / "gate_result.json", root, "G6 generated-C four-way equivalence"),
        "g7a_static_adapter": status_from_json(paths["g7a"] / "gate_result.json", root, "G7A ROS/Sunray static adapter"),
        "g7b_gazebo_ab": status_from_json(paths["g7b"] / "G7B_CLOSEOUT_ACCEPTANCE.json", root, "G7B Gazebo A/B closeout"),
        "diff_single_runtime_baseline": require_file(paths["diff_single"] / "RUN_MANIFEST.json", root, "Diff single-UAV frozen runtime baseline", required=True),
        "diff_swarm_runtime_baseline": status_from_json(paths["diff_swarm"] / "EGO_SWARM_METRICS.json", root, "Diff three-UAV original-core frozen runtime baseline"),
        "g7c_generated_core_swarm": status_from_json(paths["g7c"] / "EGO_SWARM_METRICS.json", root, "G7C generated-core three-UAV smoke"),
    }

    codegen_result, codegen_error = read_json(paths["m4a"] / "generate_model_code_result.json")
    if not codegen_error and codegen_result.get("ok") is True and codegen_result.get("check_model") is True and codegen_result.get("generate_model_code") is True:
        gate_status_items["m4a_generate_model_code"]["accepted"] = True
        gate_status_items["m4a_generate_model_code"]["status"] = "passed"
    else:
        gate_status_items["m4a_generate_model_code"]["accepted"] = False
        gate_status_items["m4a_generate_model_code"]["status"] = "failed"

    if gate_status_items["diff_single_runtime_baseline"]["exists"]:
        gate_status_items["diff_single_runtime_baseline"]["accepted"] = True
        gate_status_items["diff_single_runtime_baseline"]["status"] = "frozen_by_user"
    else:
        gate_status_items["diff_single_runtime_baseline"]["accepted"] = False
        gate_status_items["diff_single_runtime_baseline"]["status"] = "missing"

    g7b_compare, g7b_compare_error = read_json(paths["g7b"] / "compare_rerun_p95_abs" / "PX4CTRL_G7_AB_COMPARE.json")
    g7b_metrics = {
        "compare_status": g7b_compare.get("status") if not g7b_compare_error else None,
        "original_steady_hover_xy_rmse_m": nested(g7b_compare, "metric_comparisons", default=[]),
        "generated_steady_hover_xy_rmse_m": None,
        "original_all_reference_xyz_rmse_m": None,
        "generated_all_reference_xyz_rmse_m": None,
    }
    if not g7b_compare_error:
        for item in g7b_compare.get("metric_comparisons", []):
            if not isinstance(item, dict):
                continue
            path = item.get("path")
            if path == "steady_hover.xy_rmse_m":
                g7b_metrics["original_steady_hover_xy_rmse_m"] = item.get("original")
                g7b_metrics["generated_steady_hover_xy_rmse_m"] = item.get("generated")
            elif path == "all_reference_tracking.xyz_rmse_m":
                g7b_metrics["original_all_reference_xyz_rmse_m"] = item.get("original")
                g7b_metrics["generated_all_reference_xyz_rmse_m"] = item.get("generated")

    diff_swarm_summary, diff_swarm_blockers = metric_summary(paths["diff_swarm"] / "EGO_SWARM_METRICS.json")
    g7c_summary, g7c_blockers = metric_summary(paths["g7c"] / "EGO_SWARM_METRICS.json")

    blockers: list[str] = []
    for item in required_artifacts:
        if item["required"] and not item["exists"]:
            blockers.append(f"missing required artifact: {item['path']}")
    for gate_name, item in gate_status_items.items():
        if not item.get("accepted"):
            blockers.append(f"{gate_name} not accepted: status={item.get('status')!r}, path={item.get('path')}")
    blockers.extend(diff_swarm_blockers)
    blockers.extend(g7c_blockers)
    if g7b_compare_error:
        blockers.append(f"cannot parse G7B compare JSON: {g7b_compare_error}")
    elif g7b_compare.get("status") != "passed":
        blockers.append(f"G7B compare status is {g7b_compare.get('status')!r}")

    manifest: dict[str, Any] = {
        "schema": "mosim.sunray_ros1.g8_mworks_full_loop_closeout.v1",
        "status": "passed" if not blockers else "blocked",
        "freeze_id": "G8_MWORKS_FULL_LOOP_BASELINE_20260629",
        "generated_core_baseline": "PX4CTRL_Core_CFunction_Sysblock",
        "created_at_local": time.strftime("%Y-%m-%d %H:%M:%S %z"),
        "project_root": str(root),
        "result_dir": str(result_dir),
        "live_mworks_touched": False,
        "live_ros_gazebo_touched": False,
        "evidence_validation_mode": "file_manifest_closeout_only",
        "gates": {
            "m1_io_contract": {
                "status": gate_status_items["m1_io_contract"]["status"],
                "accepted": gate_status_items["m1_io_contract"]["accepted"],
                "evidence_dir": rel(paths["m1"], root),
            },
            "g5_offline_cpp": {
                "status": gate_status_items["g5_offline_cpp"]["status"],
                "accepted": gate_status_items["g5_offline_cpp"]["accepted"],
                "evidence_dir": rel(paths["g5"], root),
            },
            "g6_c_abi": {
                "status": gate_status_items["g6_c_abi"]["status"],
                "accepted": gate_status_items["g6_c_abi"]["accepted"],
                "evidence_dir": rel(paths["g6_c_abi"], root),
            },
            "m4a_mworks_cfunction_codegen": {
                "status": gate_status_items["m4a_generate_model_code"]["status"],
                "accepted": gate_status_items["m4a_generate_model_code"]["accepted"],
                "evidence_dir": rel(paths["m4a"], root),
            },
            "g6_generated_c_four_way": {
                "status": gate_status_items["g6_generated_c_four_way"]["status"],
                "accepted": gate_status_items["g6_generated_c_four_way"]["accepted"],
                "evidence_dir": rel(paths["m4a"] / "generated_c_four_way_gate", root),
            },
            "g7a_static_adapter": {
                "status": gate_status_items["g7a_static_adapter"]["status"],
                "accepted": gate_status_items["g7a_static_adapter"]["accepted"],
                "evidence_dir": rel(paths["g7a"], root),
            },
            "g7b_gazebo_ab": {
                "status": gate_status_items["g7b_gazebo_ab"]["status"],
                "accepted": gate_status_items["g7b_gazebo_ab"]["accepted"],
                "evidence_dir": rel(paths["g7b"], root),
                "metrics": g7b_metrics,
            },
            "diff_single_runtime_baseline": {
                "status": gate_status_items["diff_single_runtime_baseline"]["status"],
                "accepted": gate_status_items["diff_single_runtime_baseline"]["accepted"],
                "evidence_dir": rel(paths["diff_single"], root),
            },
            "diff_swarm_runtime_baseline": {
                "status": gate_status_items["diff_swarm_runtime_baseline"]["status"],
                "accepted": gate_status_items["diff_swarm_runtime_baseline"]["accepted"],
                "evidence_dir": rel(paths["diff_swarm"], root),
                "metrics": diff_swarm_summary,
            },
            "g7c_generated_core_swarm": {
                "status": gate_status_items["g7c_generated_core_swarm"]["status"],
                "accepted": gate_status_items["g7c_generated_core_swarm"]["accepted"],
                "evidence_dir": rel(paths["g7c"], root),
                "metrics": g7c_summary,
            },
        },
        "required_artifacts": required_artifacts,
        "gate_status_items": gate_status_items,
        "claim_boundary": (
            "G8 freezes the MWORKS CFunction generated px4ctrl core as a "
            "reproducible baseline across I/O contract, MWORKS check/codegen, "
            "offline C/C++ equivalence, static ROS/Sunray ATTITUDE_THRUST "
            "adapter, single-UAV Gazebo A/B, and three-UAV Diff-Planner "
            "generated-core smoke. This closeout package itself is file-level "
            "validation and does not start live MWORKS, ROS, Gazebo, PX4, "
            "MAVROS, FAST-LIO, Diff-Planner, or RViz."
        ),
        "not_claimed": [
            "advanced controller family implementation",
            "PX4-native uORB module deployment",
            "MWORKS GUI synchronous real-time Gazebo co-simulation",
            "autonomous exploration",
            "Point-LIO replacement",
            "UE/frontend authoritative runtime evidence",
            "final competition controller performance",
        ],
        "reproduce_commands": {
            "closeout": "python Scripts\\sunray\\px4ctrl_golden_slice\\build_g8_mworks_full_loop_closeout.py",
            "g7b_optional_runtime_rerun": "wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && bash Scripts/sunray/px4ctrl_golden_slice/run_px4ctrl_g7b_gazebo_ab_gate.sh hover'",
            "g7c_optional_runtime_rerun": "wsl -d Ubuntu-20.04 --exec bash -lc 'cd /mnt/c/Users/HP/Desktop/MoSim && UAV_NUM=3 PLANNER_VARIANT=diff_planner PX4CTRL_CORE_PROFILE=mworks_generated_c bash Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh'",
        },
        "blockers": blockers,
    }

    (result_dir / "G8_CLOSEOUT.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary(result_dir / "SUMMARY.md", manifest)
    print(result_dir)
    return 0 if manifest["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
