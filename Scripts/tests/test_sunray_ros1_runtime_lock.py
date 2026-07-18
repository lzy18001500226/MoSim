from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LOCK_HELPER = ROOT / "Scripts/sunray/sunray_ros1_runtime_lock.sh"
BASIC_RUNNER = ROOT / "Scripts/sunray/run_px4ctrl_basic_gate.sh"
SWARM_RUNNER = ROOT / "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh"


def test_shared_runtime_lock_is_used_by_basic_and_swarm_runners() -> None:
    helper = LOCK_HELPER.read_text(encoding="utf-8")
    basic = BASIC_RUNNER.read_text(encoding="utf-8")
    swarm = SWARM_RUNNER.read_text(encoding="utf-8")

    assert "mkdir -- \"${SUNRAY_ROS1_RUNTIME_LOCK_DIR}\"" in helper
    assert "current_boot_id" in helper
    assert "kill -0 \"${owner_pid}\"" in helper
    assert '"${inherited_owner_pid}" == "$$"' in helper
    assert "Sunray ROS1 runtime is busy" in helper
    assert "sunray_ros1_runtime_lock_release" in helper

    for runner in (basic, swarm):
        assert 'source "${PROJECT_ROOT}/Scripts/sunray/sunray_ros1_runtime_lock.sh"' in runner
        assert "sunray_ros1_runtime_lock_acquire" in runner
        assert "sunray_ros1_runtime_lock_release" in runner


def test_swarm_startup_cleanup_keeps_runtime_lock_owned() -> None:
    swarm = SWARM_RUNNER.read_text(encoding="utf-8")

    assert "cleanup_runtime() {" in swarm
    assert "cleanup() {\n  cleanup_runtime\n  sunray_ros1_runtime_lock_release\n}" in swarm
    assert "prepare_px4_ros1_runtime_overlay\n\ncleanup_runtime\nsleep 3\nsource_env" in swarm
