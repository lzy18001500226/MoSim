import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANUAL = ROOT / "Docs" / "报告" / "用户手册_正文骨架.md"

RUNS = {
    "nominal": ROOT
    / "Results"
    / "sunray_ros1"
    / "sunray_ros1_graphical_c99_takeoff_hover_land_20260731_002",
    "wind": ROOT
    / "Results"
    / "sunray_ros1"
    / "sunray_ros1_graphical_c99_wind_hover_20260801_002",
    "motor_fault": ROOT
    / "Results"
    / "sunray_ros1"
    / "sunray_ros1_graphical_c99_motor_fault_recovery_20260731_002",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_manual_gives_a_clean_clone_and_source_local_c99_path() -> None:
    source = MANUAL.read_text(encoding="utf-8")

    assert "git clone https://github.com/lzy18001500226/MoSim.git MoSim" in source
    assert "git status --short" in source
    assert "check_project_path_registry.py --project-root . --require-canonical-active" in source
    assert "check_local_source_activation.py --project-root ." in source
    assert "00_准备C99单机环境.cmd" in source
    assert "01_运行C99单机起飞悬停降落.cmd" in source
    assert "02_运行C99风扰闭环.cmd" in source
    assert "03_运行C99电机故障恢复闭环.cmd" in source
    assert "PX4CTRL_BUILD_BACKEND=graphical_px4ctrl_c99" in source


def test_manual_matches_the_frozen_fastlio_ekf_boundary() -> None:
    source = MANUAL.read_text(encoding="utf-8")

    assert "EKF2_GPS_CTRL=0" in source
    assert "EKF2_EV_CTRL=15" in source
    assert "移除 GPS、FAST-LIO" not in source
    assert "将真值直接接入控制器" in source

    for result_dir in RUNS.values():
        manifest = load_json(result_dir / "RUN_MANIFEST.json")
        diagnostics = manifest["diagnostics"]

        assert diagnostics["fastlio_ekf_fusion_enabled"] == "true"
        assert diagnostics["gazebo_truth_alignment_input_enabled"] is True
        assert diagnostics["gazebo_truth_direct_px4ctrl_input_allowed"] is False
        assert "PX4CTRL_BUILD_BACKEND=graphical_px4ctrl_c99" in (
            result_dir / "px4ctrl_build_backend.txt"
        ).read_text(encoding="utf-8")


def test_documented_c99_evidence_artifacts_are_passed_records() -> None:
    assert load_json(RUNS["nominal"] / "PX4CTRL_BASIC_MISSION_METRICS.json")["status"] == "passed"
    assert load_json(RUNS["wind"] / "DEMO_STATUS.json")["status"] == "passed"
    assert load_json(RUNS["wind"] / "WIND_INJECTION_EVIDENCE.json")["status"] == "passed"
    assert load_json(RUNS["motor_fault"] / "DEMO_STATUS.json")["status"] == "passed"
    assert (
        load_json(RUNS["motor_fault"] / "MOTOR_EFFICIENCY_INJECTION_EVIDENCE.json")["status"]
        == "passed"
    )
