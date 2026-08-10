from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts" / "sunray" / "build_factory_l2_diff_swarm_c99_fixed_hover_evidence.py"
SPEC = importlib.util.spec_from_file_location("factory_l2_diff_swarm_evidence", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def create_run(tmp_path: Path) -> Path:
    run_dir = tmp_path / "factory_l2_diff_swarm_c99_fixture"
    run_dir.mkdir()
    targets = {"1": [1.0, -1.0, 1.0], "2": [1.0, 1.0, 1.0], "3": [1.0, 0.0, 1.0]}
    per_uav = {}
    startup_topics = {}
    for uid, target in targets.items():
        per_uav[uid] = {
            "target": {"x": target[0], "y": target[1], "z": target[2]},
            "target_hold": {
                "reached": True,
                "reached_by": "strict_radius",
                "required_s": 5.0,
                "duration_s": 5.2,
                "end_snapshot": {"error_xyz_m": 0.03, "speed_mps": 0.02, "abs_vz_mps": 0.01},
            },
        }
        startup_topics[f"uav{uid}"] = {
            "mavros_state": {"received": True, "data": {"connected": True}},
            "odom": {"received": True},
            "raw_lidar": {"received": True},
        }
        (run_dir / f"uav{uid}_raw_position_cmd.csv").write_text("t,x\n" + "\n".join(f"{i},0" for i in range(10)) + "\n", encoding="utf-8")
        (run_dir / f"uav{uid}_position_cmd.csv").write_text("t,x\n0,0\n", encoding="utf-8")
        (run_dir / f"uav{uid}_bspline_summary.csv").write_text("t,kind\n0,PolyTraj\n", encoding="utf-8")
        (run_dir / f"uav{uid}_truth.csv").write_text("t,x,y,z\n0,0,0,0\n", encoding="utf-8")
        write_json(run_dir / f"uav{uid}_pointcloud_diagnostics.json", {"status": "passed"})

    write_json(
        run_dir / "EGO_SWARM_METRICS.json",
        {
            "status": "passed",
            "blockers": [],
            "uav_num": 3,
            "per_uav": per_uav,
            "min_inter_uav_distance_m": 0.9,
            "min_inter_uav_pair": [2, 3],
            "inter_uav_emergency_hold": {"events": []},
            "landing": {"completed": True, "exit_reason": "all_uavs_landed_and_disarmed"},
        },
    )
    write_json(
        run_dir / "RUN_INPUTS.json",
        {
            "run_id": "fixture",
            "world_file": "/tmp/factoryenvironmentcollect_l2_static_review_clean.sdf",
            "factory_l2_model_path_active": True,
            "planner_variant": "diff_planner",
        },
    )
    write_json(
        run_dir / "RUN_MANIFEST.json",
        {"mission_exit_code": 0, "controller_core_profile": "graphical_c99"},
    )
    write_json(
        run_dir / "STARTUP_ATTEMPT_SUMMARY.json",
        {"attempts": [{"exit_code": 0, "mission_status": "passed", "topics": startup_topics}]},
    )
    write_json(run_dir / "planner_runtime_log_audit.json", {"status": "passed", "blockers": [], "fatal_event_count": 0})
    write_json(
        run_dir / "c99_diff_target_coordinate_contract.json",
        {
            "status": "passed",
            "source_frame": "world",
            "mavros_frame": "common_world",
            "mission_frame": "common_world",
            "planner_frame": "common_world",
            "source_targets": targets,
            "mission_targets": targets,
            "planner_targets": targets,
        },
    )
    (run_dir / "c99_multiuav_contract.env").write_text(
        "PLANNER_VARIANT=diff_planner\n"
        "UAV_NUM=3\n"
        "PX4CTRL_BUILD_BACKEND=graphical_px4ctrl_c99\n"
        "PX4CTRL_HOVER_PERCENTAGE=0.456\n"
        "EGO_GATE_TARGET_HOLD_S=5.0\n",
        encoding="utf-8",
    )
    (run_dir / "goal5_preloaded_3uav.world").write_text(
        '<world name="factoryenvironmentcollect_l2_static_review_clean"/>\n', encoding="utf-8"
    )
    (run_dir / "inter_uav_separation.csv").write_text("t,distance_m\n0,0.9\n", encoding="utf-8")
    (run_dir / "planner_swarm_px4ctrl_goal5.log").write_text("planner started\n", encoding="utf-8")
    return run_dir


def test_build_packet_for_passed_three_uav_run(tmp_path: Path) -> None:
    run_dir = create_run(tmp_path)
    packet = MODULE.build_packet(run_dir, tmp_path / "packet", 5.0, 0.45)

    assert packet["status"] == "passed"
    assert packet["blockers"] == []
    assert len(packet["per_uav"]) == 3
    assert packet["separation"]["observed_min_distance_m"] == 0.9

    json_path, summary_path = MODULE.write_packet(tmp_path / "packet", packet, force=False)
    assert json_path.is_file()
    assert summary_path.is_file()


def test_build_packet_rejects_missing_strict_hold(tmp_path: Path) -> None:
    run_dir = create_run(tmp_path)
    metrics_path = run_dir / "EGO_SWARM_METRICS.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics["per_uav"]["2"]["target_hold"]["reached"] = False
    write_json(metrics_path, metrics)

    packet = MODULE.build_packet(run_dir, tmp_path / "packet", 5.0, 0.45)

    assert packet["status"] == "blocked"
    assert "uav2_strict_target_hold" in packet["blockers"]
