"""Launch MoSim UE scene replay publishers and optional RViz2 views."""

from __future__ import annotations

from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression


PROJECT_ROOT = Path("/mnt/c/Users/HP/Desktop/MoSim")


def _bool_text(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


def _scene_id(value: str) -> str:
    aliases = {
        "factory": "factoryenvironmentcollect",
        "FactoryEnvironmentCollect": "factoryenvironmentcollect",
        "factoryenvironmentcollect": "factoryenvironmentcollect",
        "derelict": "derelictcorridormegascans",
        "DerelictCorridorMegascans": "derelictcorridormegascans",
        "derelictcorridormegascans": "derelictcorridormegascans",
    }
    if value not in aliases:
        raise RuntimeError(
            f"unsupported scene '{value}'; use factoryenvironmentcollect or derelictcorridormegascans"
        )
    return aliases[value]


def _path(context, name: str) -> Path:
    return Path(LaunchConfiguration(name).perform(context))


def _publisher_args(base_args: list[str], max_frames: str, loop: str) -> list[str]:
    args = list(base_args)
    if max_frames != "0":
        args.extend(["--max-frames", max_frames])
    if _bool_text(loop):
        args.append("--loop")
    return args


def _launch_setup(context, *_args, **_kwargs):
    scene = _scene_id(LaunchConfiguration("scene").perform(context))
    output_root = _path(context, "output_root")
    scene_dir = output_root / scene
    fps = LaunchConfiguration("fps").perform(context)
    max_frames = LaunchConfiguration("max_frames").perform(context)
    loop = LaunchConfiguration("loop").perform(context)
    wall_time = LaunchConfiguration("wall_time").perform(context)
    rviz_profile = LaunchConfiguration("rviz_profile").perform(context)

    render_replay = scene_dir / "render_replay.csv"
    local_known_map = scene_dir / "local_known_map_frames.jsonl"
    local_plan = scene_dir / "local_plan_frames.jsonl"
    lidar_frames = scene_dir / "lidar_point_frames.jsonl"
    fastlio_dataset = scene_dir / "fastlio_replay_dataset.jsonl"

    required = [render_replay, local_known_map, local_plan, lidar_frames, fastlio_dataset]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("missing MoSim replay artifacts: " + ", ".join(missing))

    mapping_args = _publisher_args(
        [
            str(PROJECT_ROOT / "Scripts/ros/publish_mosim_mapping_replay_ros2.py"),
            "--render-replay-csv",
            str(render_replay),
            "--local-known-map-jsonl",
            str(local_known_map),
            "--local-plan-jsonl",
            str(local_plan),
            "--lidar-point-frames-jsonl",
            str(lidar_frames),
            "--fps",
            fps,
        ],
        max_frames,
        loop,
    )
    fastlio_args = _publisher_args(
        [
            str(PROJECT_ROOT / "Scripts/UE5/publish_fastlio_replay_ros2.py"),
            "--dataset",
            str(fastlio_dataset),
            "--fps",
            fps,
        ],
        max_frames,
        loop,
    )
    if _bool_text(wall_time):
        mapping_args.append("--wall-time")
        fastlio_args.append("--wall-time")

    actions = [
        ExecuteProcess(
            cmd=["python3", *mapping_args],
            cwd=str(PROJECT_ROOT),
            name="mosim_mapping_replay_publisher",
            output="screen",
        ),
        ExecuteProcess(
            cmd=["python3", *fastlio_args],
            cwd=str(PROJECT_ROOT),
            name="mosim_fastlio_input_replay_publisher",
            output="screen",
        ),
    ]

    rviz_configs = {
        "overview": [PROJECT_ROOT / "Config/rviz2/mosim_uav_mapping.rviz"],
        "planning_grid": [PROJECT_ROOT / "Config/rviz2/mosim_uav_planning_grid.rviz"],
        "fastlio_pointcloud": [PROJECT_ROOT / "Config/rviz2/mosim_uav_fastlio_pointcloud.rviz"],
        "split": [
            PROJECT_ROOT / "Config/rviz2/mosim_uav_planning_grid.rviz",
            PROJECT_ROOT / "Config/rviz2/mosim_uav_fastlio_pointcloud.rviz",
        ],
    }
    if rviz_profile not in rviz_configs:
        raise RuntimeError("unsupported rviz_profile; use overview, planning_grid, fastlio_pointcloud, or split")
    for config in rviz_configs[rviz_profile]:
        if not config.is_file():
            raise RuntimeError(f"missing RViz2 config: {config}")
        actions.append(
            ExecuteProcess(
                cmd=["rviz2", "-d", str(config)],
                cwd=str(PROJECT_ROOT),
                name=f"rviz2_{config.stem}",
                condition=IfCondition(LaunchConfiguration("start_rviz")),
                output="screen",
            )
        )

    actions.append(
        ExecuteProcess(
            cmd=["bash", "-lc", LaunchConfiguration("fastlio_launch_cmd")],
            cwd=str(PROJECT_ROOT),
            name="external_fastlio_ros2_runtime",
            condition=IfCondition(
                PythonExpression(
                    [
                        "'",
                        LaunchConfiguration("start_fastlio"),
                        "' == 'true' and '",
                        LaunchConfiguration("fastlio_launch_cmd"),
                        "' != ''",
                    ]
                )
            ),
            output="screen",
        )
    )
    return actions


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("scene", default_value="factoryenvironmentcollect"),
            DeclareLaunchArgument(
                "output_root",
                default_value=str(PROJECT_ROOT / "Results/unreal_scene_mapping"),
            ),
            DeclareLaunchArgument("fps", default_value="10"),
            DeclareLaunchArgument("max_frames", default_value="0"),
            DeclareLaunchArgument("loop", default_value="true"),
            DeclareLaunchArgument("wall_time", default_value="true"),
            DeclareLaunchArgument("start_rviz", default_value="true"),
            DeclareLaunchArgument("rviz_profile", default_value="split"),
            DeclareLaunchArgument("start_fastlio", default_value="false"),
            DeclareLaunchArgument("fastlio_launch_cmd", default_value=""),
            OpaqueFunction(function=_launch_setup),
        ]
    )
