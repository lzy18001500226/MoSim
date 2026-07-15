from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "Scripts" / "sunray" / "audit_roslaunch_runtime_log.py"


def run_audit(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AUDIT), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def write_log(path: Path, event_ros_time: float) -> None:
    path.write_text(
        "\n".join(
            [
                "[WARN] [1000.000000000, 10.000000000]: start flight",
                f"[ERROR] [1001.000000000, {event_ros_time:.9f}]: Fail to solve ACVRP.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_racer_acvrp_blocks_inside_active_window(tmp_path: Path) -> None:
    log_path = tmp_path / "planner.log"
    output_path = tmp_path / "audit.json"
    write_log(log_path, event_ros_time=12.0)

    result = run_audit(
        "--log",
        str(log_path),
        "--output",
        str(output_path),
        "--planner-semantic-profile",
        "racer",
        "--semantic-blocker-max-ros-time",
        "13.0",
        "--missing-is-blocker",
    )

    assert result.returncode == 1, result.stdout + result.stderr
    audit = json.loads(output_path.read_text(encoding="utf-8"))
    assert audit["status"] == "blocked"
    assert audit["semantic_blockers"] == ["planner_semantic_racer_acvrp_failed"]
    assert audit["ignored_semantic_blocker_counts"] == {}


def test_racer_acvrp_after_done_is_diagnostic_and_remerge_clears_old_blocker(tmp_path: Path) -> None:
    log_path = tmp_path / "planner.log"
    output_path = tmp_path / "audit.json"
    metrics_path = tmp_path / "metrics.json"
    write_log(log_path, event_ros_time=15.0)
    metrics_path.write_text(
        json.dumps(
            {
                "schema": "mosim.sunray_ros1.goal5_ego_swarm_metrics.v1",
                "status": "blocked",
                "blockers": ["racer_planner_semantic_racer_acvrp_failed"],
                "runtime_log_audit": {
                    "status": "blocked",
                    "blockers": ["racer_planner_semantic_racer_acvrp_failed"],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_audit(
        "--log",
        str(log_path),
        "--output",
        str(output_path),
        "--metrics-json",
        str(metrics_path),
        "--blocker-prefix",
        "racer",
        "--planner-semantic-profile",
        "racer",
        "--semantic-blocker-max-ros-time",
        "14.0",
        "--missing-is-blocker",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    audit = json.loads(output_path.read_text(encoding="utf-8"))
    assert audit["status"] == "passed"
    assert audit["semantic_blockers"] == []
    assert audit["ignored_semantic_blocker_counts"] == {"racer_acvrp_failed": 1}

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert metrics["status"] == "passed"
    assert metrics["blockers"] == []
    assert metrics["runtime_log_audit"]["ignored_semantic_blocker_counts"] == {"racer_acvrp_failed": 1}


def test_racer_replan_and_stale_id_events_are_diagnostic(tmp_path: Path) -> None:
    log_path = tmp_path / "planner.log"
    output_path = tmp_path / "audit.json"
    log_path.write_text(
        "\n".join(
            [
                "[ERROR] [1001.000000000, 12.000000000]: Drone 1 collide with drone 2.",
                "[ERROR] [1001.100000000, 12.100000000]: out of order bspline.",
                "[ERROR] [1001.200000000, 12.200000000]: No path to next viewpoint",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_audit(
        "--log",
        str(log_path),
        "--output",
        str(output_path),
        "--planner-semantic-profile",
        "racer",
        "--semantic-blocker-max-ros-time",
        "13.0",
        "--missing-is-blocker",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    audit = json.loads(output_path.read_text(encoding="utf-8"))
    assert audit["status"] == "passed"
    assert audit["semantic_blockers"] == []
    assert audit["semantic_event_counts"] == {
        "racer_no_path_to_viewpoint": 1,
        "racer_out_of_order_bspline": 1,
        "racer_swarm_collision_prediction": 1,
    }


def test_racer_pair_opt_evidence_distinguishes_applied_ownership_change(tmp_path: Path) -> None:
    log_path = tmp_path / "planner.log"
    output_path = tmp_path / "audit.json"
    log_path.write_text(
        "\n".join(
            [
                "[WARN] [1001.0, 12.0]: Pair opt 1 & 2",
                "[WARN] [1001.1, 12.1]: Drone 1 send opt request to 2, pair opt t: 0.01",
                "[WARN] [1001.2, 12.2]: MoSim RACER pair opt applied role=receiver sender=1 receiver=2 changed=true sender_grids=2->1 receiver_grids=1->2 stamp=12.0",
                "[WARN] [1001.3, 12.3]: get response 1",
                "[WARN] [1001.4, 12.4]: MoSim RACER pair opt applied role=initiator sender=1 receiver=2 changed=true sender_grids=2->1 receiver_grids=1->2 stamp=12.0",
                "[WARN] [1001.5, 12.5]: MoSim D3 reject pair opt 2 & 3: empty allocation ego=0 other=3",
                "[ERROR] [1001.6, 12.6]: Larger cost after reallocation",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_audit(
        "--log",
        str(log_path),
        "--output",
        str(output_path),
        "--planner-semantic-profile",
        "racer",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    evidence = json.loads(output_path.read_text(encoding="utf-8"))["racer_pair_opt"]
    assert evidence["status"] == "applied_with_ownership_change"
    assert evidence["successful_transaction_count"] == 1
    assert evidence["ownership_change_transaction_count"] == 1
    assert evidence["counts"]["applied_receiver"] == 1
    assert evidence["counts"]["applied_initiator"] == 1
    assert evidence["counts"]["rejected_empty"] == 1
    assert evidence["counts"]["rejected_larger_cost"] == 1
