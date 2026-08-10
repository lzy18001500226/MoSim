import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUNRAY = ROOT / "Scripts" / "sunray"
PREPARE = SUNRAY / "prepare_c99_diff_swarm_runtime.sh"
COMPONENTS = SUNRAY / "run_c99_diff_swarm_components.sh"
MISSION = SUNRAY / "run_c99_diff_swarm_mission.sh"
MISSION_STAGE = SUNRAY / "run_px4ctrl_ego_swarm_mission_stage.sh"
REVIEW = SUNRAY / "review_c99_diff_swarm_run.sh"
REVIEWER = SUNRAY / "review_c99_diff_swarm_run.py"
STOP = SUNRAY / "stop_c99_diff_swarm_components.sh"
CONTRACT = SUNRAY / "c99_diff_stage_contract.sh"
WRAPPER = SUNRAY / "run_c99_multiuav_planner_gate.sh"
SWARM_GATE = SUNRAY / "run_px4ctrl_ego_swarm_gate.sh"


def test_staged_entrypoints_preserve_a_dedicated_prepare_contract() -> None:
    prepare = PREPARE.read_text(encoding="utf-8")
    wrapper = WRAPPER.read_text(encoding="utf-8")
    contract = CONTRACT.read_text(encoding="utf-8")

    assert "C99_DIFF_PREPARE_ONLY=true" in prepare
    assert "c99_multiuav_contract.env" in prepare
    assert 'C99_DIFF_PREPARE_ONLY="${C99_DIFF_PREPARE_ONLY:-false}"' in wrapper
    assert "C99_DIFF_PREPARE_STATUS.json" in wrapper
    assert "No Gazebo, PX4, MAVROS, planner, mission, or RViz runtime is claimed." in wrapper
    assert "c99_diff_load_contract" in contract
    assert "unsafe contract key" in contract


def test_components_are_held_by_the_existing_owned_process_runner() -> None:
    components = COMPONENTS.read_text(encoding="utf-8")
    gate = SWARM_GATE.read_text(encoding="utf-8")
    stop = STOP.read_text(encoding="utf-8")

    assert "GOAL5_COMPONENTS_ONLY=true" in components
    assert "KEEP_ALIVE=true" in components
    assert "c99_diff_swarm_components_runner.pid" in components
    assert 'GOAL5_STARTUP_ATTEMPTS="${GOAL5_STARTUP_ATTEMPTS:-2}"' in components
    assert 'MAVROS_READY_TIMEOUT_S="${MAVROS_READY_TIMEOUT_S:-180}"' in components
    assert 'GOAL5_COMPONENTS_ONLY="${GOAL5_COMPONENTS_ONLY:-false}"' in gate
    assert "C99_DIFF_SWARM_COMPONENTS_READY.json" in gate
    assert "requires KEEP_ALIVE=true" in gate
    assert "while true; do" in gate
    assert 'kill -INT "${runner_pid}"' in stop
    assert 'kill -INT "${leaf_runner_pid}"' in stop
    assert 'open(f"/proc/{pid}/cmdline"' in stop
    assert "runner_cmdline" in stop
    assert "pkill" not in stop


def test_mission_and_review_stages_are_independent_from_component_startup() -> None:
    mission = MISSION.read_text(encoding="utf-8")
    mission_stage = MISSION_STAGE.read_text(encoding="utf-8")
    review = REVIEW.read_text(encoding="utf-8")

    assert "C99_DIFF_SWARM_COMPONENTS_READY.json" in mission
    assert "run_px4ctrl_ego_swarm_mission_stage.sh" in mission
    assert "run_px4ctrl_ego_swarm_gate.sh" not in mission_stage
    assert "px4ctrl_ego_swarm_mission_node.py" in mission_stage
    assert "planner_runtime_log_audit.json" in review
    assert "review_c99_diff_swarm_run.py" in review
    assert "C99_DIFF_SWARM_STAGE_REVIEW.json" in review
    assert "inter_uav_separation" in REVIEWER.read_text(encoding="utf-8")


def write_complete_staged_artifacts(tmp_path: Path, *, min_inter_uav_distance_m: float) -> None:
    (tmp_path / "C99_DIFF_PREPARE_STATUS.json").write_text(
        json.dumps({"status": "passed"}), encoding="utf-8"
    )
    (tmp_path / "C99_DIFF_SWARM_COMPONENTS_READY.json").write_text(
        json.dumps({"status": "passed", "uav_num": 3}), encoding="utf-8"
    )
    (tmp_path / "c99_diff_swarm_component_contract.env").write_text(
        "EGO_GATE_MIN_INTER_UAV_DISTANCE=0.45\n", encoding="utf-8"
    )
    (tmp_path / "c99_diff_target_coordinate_contract.json").write_text("{}", encoding="utf-8")
    (tmp_path / "EGO_SWARM_METRICS.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "per_uav": {
                    "1": {"target_hold": {"reached": True}},
                    "2": {"target_hold": {"reached": True}},
                    "3": {"target_hold": {"reached": True}},
                },
                "min_inter_uav_distance_m": min_inter_uav_distance_m,
                "inter_uav_emergency_hold": {"events": []},
                "landing": {"completed": True},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "planner_runtime_log_audit.json").write_text(
        json.dumps({"status": "passed"}), encoding="utf-8"
    )


def run_reviewer(tmp_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(REVIEWER), "--result-dir", str(tmp_path)],
        check=False,
        capture_output=True,
        text=True,
    )


def test_reviewer_accepts_complete_staged_artifacts(tmp_path: Path) -> None:
    write_complete_staged_artifacts(tmp_path, min_inter_uav_distance_m=0.98)

    completed = run_reviewer(tmp_path)

    assert completed.returncode == 0, completed.stderr
    packet = json.loads((tmp_path / "C99_DIFF_SWARM_STAGE_REVIEW.json").read_text(encoding="utf-8"))
    assert packet["status"] == "passed"
    assert all(check["status"] == "passed" for check in packet["checks"])


def test_reviewer_rejects_a_separation_breach(tmp_path: Path) -> None:
    write_complete_staged_artifacts(tmp_path, min_inter_uav_distance_m=0.44)

    completed = run_reviewer(tmp_path)

    assert completed.returncode == 1
    packet = json.loads((tmp_path / "C99_DIFF_SWARM_STAGE_REVIEW.json").read_text(encoding="utf-8"))
    separation = next(check for check in packet["checks"] if check["name"] == "inter_uav_separation")
    assert packet["status"] == "failed"
    assert separation["status"] == "failed"
