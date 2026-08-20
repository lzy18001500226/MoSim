from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Px4Ctrl" / "Px4CtrlRunner.mo"
DISPLAY = ROOT / "Models" / "MoSimQuadrotorModel" / "Environment" / "Maps" / "OpenBlocksLocalPerceptionDisplay.mo"
BASE_DISPLAY = ROOT / "Models" / "MoSimQuadrotorModel" / "Environment" / "Maps" / "PlanningNavigationDisplay.mo"


def test_px4ctrl_runner_uses_dynamic_local_perception_only() -> None:
    runner = RUNNER.read_text(encoding="utf-8")
    display = DISPLAY.read_text(encoding="utf-8")
    base_display = BASE_DISPLAY.read_text(encoding="utf-8")

    assert "MoSimQuadrotorModel.Environment.Maps.OpenBlocksLocalPerceptionDisplay nav_display" in runner
    assert "OpenBlocksMapTruthDisplay nav_display" not in runner
    for index in (1, 2, 3):
        assert f"connect(plant.position[{index}], nav_display.actual_position[{index}])" in runner
        assert f"connect(reference.position_command[{index}], nav_display.reference_position[{index}])" in runner

    for token in (
        "final highlight_local_costmap = true",
        "final local_costmap_radius_m = 6.0",
        "final local_costmap_fade_radius_m = 9.0",
        "final show_static_map_layers = false",
        "final show_global_wall_truth = false",
        "final render_terrain_blocks = true",
        "final terrain_render_stride = 2",
    ):
        assert token in display

    assert "local_ground_fade" not in display
    assert "local_ground_core" not in display
    assert "Shape ground_pillar[ground_pillar_count]" in base_display
