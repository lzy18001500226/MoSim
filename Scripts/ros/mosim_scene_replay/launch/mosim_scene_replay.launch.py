"""Launch MoSim MWORKS UAV state bridge and optional FAST-LIO/RViz2 views."""

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
    scan_duration_s = LaunchConfiguration("scan_duration_s").perform(context)
    effective_scan_duration_s = "0.09" if scan_duration_s in {"0", "0.0", ""} else scan_duration_s
    imu_substeps_per_frame = LaunchConfiguration("imu_substeps_per_frame").perform(context)
    imu_span_s = LaunchConfiguration("imu_span_s").perform(context)
    imu_lead_sleep_s = LaunchConfiguration("imu_lead_sleep_s").perform(context)
    max_frames = LaunchConfiguration("max_frames").perform(context)
    loop = LaunchConfiguration("loop").perform(context)
    wall_time = LaunchConfiguration("wall_time").perform(context)
    rviz_profile = LaunchConfiguration("rviz_profile").perform(context)

    dense_lidar_frames = scene_dir / "livox_like_lidar_frames.jsonl"
    mworks_raw = scene_dir / "mworks_smoke" / "raw" / f"sunray150_ue_{scene}_linear_mpc_smoke.csv"
    fastlio_lidar_topic = LaunchConfiguration("fastlio_lidar_topic").perform(context)
    fastlio_pointcloud_topic = LaunchConfiguration("fastlio_pointcloud_topic").perform(context)
    fastlio_imu_topic = LaunchConfiguration("fastlio_imu_topic").perform(context)
    fastlio_lidar_frame = LaunchConfiguration("fastlio_lidar_frame").perform(context)
    fastlio_imu_frame = LaunchConfiguration("fastlio_imu_frame").perform(context)

    if not dense_lidar_frames.is_file():
        dense_lidar_frames = scene_dir / "livox_like_lidar_frames_mworks_body.jsonl"
    required = [dense_lidar_frames, mworks_raw]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("missing MoSim MWORKS/FAST-LIO input artifacts: " + ", ".join(missing))

    fastlio_args = _publisher_args(
        [
            str(PROJECT_ROOT / "Scripts/ros/publish_mworks_uav_state_ros2.py"),
            "--mworks-raw-csv",
            str(mworks_raw),
            "--lidar-point-frames-jsonl",
            str(dense_lidar_frames),
            "--truth-rate-hz",
            "20",
            "--imu-rate-hz",
            "200",
            "--lidar-rate-hz",
            fps,
            "--controller-rate-hz",
            "20",
            "--scan-duration-s",
            effective_scan_duration_s,
            "--lidar-topic",
            fastlio_pointcloud_topic,
            "--livox-custom-topic",
            fastlio_lidar_topic,
            "--publish-livox-custom",
            "--imu-topic",
            fastlio_imu_topic,
            "--lidar-frame",
            fastlio_lidar_frame,
            "--imu-frame",
            fastlio_imu_frame,
        ],
        max_frames,
        loop,
    )
    if _bool_text(wall_time):
        fastlio_args.append("--wall-time")

    actions = [
        ExecuteProcess(
            cmd=["python3", *fastlio_args],
            cwd=str(PROJECT_ROOT),
            name="mosim_mworks_uav_state_publisher",
            output="screen",
        ),
    ]

    fastlio_rviz = PROJECT_ROOT / "Config/rviz2/mosim_uav_fastlio_pointcloud.rviz"
    rviz_configs = {
        "overview": [fastlio_rviz],
        "fastlio_pointcloud": [fastlio_rviz],
        "split": [fastlio_rviz],
    }
    if rviz_profile not in rviz_configs:
        raise RuntimeError("unsupported rviz_profile; use overview, fastlio_pointcloud, or split")
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
            DeclareLaunchArgument("scan_duration_s", default_value="0"),
            DeclareLaunchArgument("imu_substeps_per_frame", default_value="10"),
            DeclareLaunchArgument("imu_span_s", default_value="0"),
            DeclareLaunchArgument("imu_lead_sleep_s", default_value="0.005"),
            DeclareLaunchArgument("max_frames", default_value="0"),
            DeclareLaunchArgument("loop", default_value="true"),
            DeclareLaunchArgument("wall_time", default_value="true"),
            DeclareLaunchArgument("start_rviz", default_value="true"),
            DeclareLaunchArgument("rviz_profile", default_value="split"),
            DeclareLaunchArgument("start_fastlio", default_value="false"),
            DeclareLaunchArgument("fastlio_launch_cmd", default_value=""),
            DeclareLaunchArgument("fastlio_lidar_topic", default_value="/mosim/livox/lidar"),
            DeclareLaunchArgument("fastlio_pointcloud_topic", default_value="/mosim/lidar_points"),
            DeclareLaunchArgument("fastlio_imu_topic", default_value="/mosim/forward/imu"),
            DeclareLaunchArgument("fastlio_lidar_frame", default_value="base/mid360_link"),
            DeclareLaunchArgument("fastlio_imu_frame", default_value="base/forward_imu_optical_frame"),
            OpaqueFunction(function=_launch_setup),
        ]
    )
