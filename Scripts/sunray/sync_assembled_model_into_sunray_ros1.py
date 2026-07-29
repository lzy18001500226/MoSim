#!/usr/bin/env python3
"""Sync the accepted MoSim Sunray150 assembly visuals into Sunray ROS1.

The YunZong/Sunray ROS1 stack uses a Gazebo Classic PX4 jinja SDF model named
``sunray150_with_mid360``.  The accepted MoSim visual/geometry baseline lives
under ``Config/gazebo/models/sunray150_assembled`` and uses Gazebo Sim plugin
syntax, so it cannot be copied wholesale into the ROS1/PX4 model.

This script keeps Sunray's Gazebo Classic sensors, MAVLink, motor, p3d, camera,
and MID360 plugins, but replaces the vehicle visual meshes, rotor visual meshes,
body collision envelope, and accepted inertia values with the MoSim assembly
baseline.

The accepted MoSim assembled body already contains the MID360 visual and a
reviewed mount pose.  Sunray's standalone ``livox_mid360`` visual/collision
mesh is not used.  The MID360 sensor source can be selected with
``SUNRAY_MID360_SENSOR_MODE``:

``inline``
    Inline the ray/IMU sensors into the vehicle base link.  This is kept only
    as a bounded diagnostic mode because it changes the original Sunray MID360
    sensor assembly semantics.

``nested``
    Restore the original Sunray nested ``model://livox_mid360`` sensor model
    with a fixed joint, while keeping the default sensor shell mesh deleted.
    This is the current default for Sunray ROS1 MID360/FAST-LIO review.

GPS can be selected with ``SUNRAY_GPS_SENSOR_MODE``.  ``nested`` restores the
upstream PX4 Gazebo Classic ``model://gps`` / ``gps0_joint`` contract and is
the only GPS mode admitted to the current PX4 EKF state-chain gate.  ``inline``
is retained only for historical diagnostics; ``removed`` remains the default
for paths that intentionally use external fusion instead of GPS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT_DEFAULT = Path("/mnt/c/Users/HP/Desktop/MoSim")
SUNRAY_WS_DEFAULT = Path("/tmp/mosim_sunray_build_20260620_114615/Sunray")
LOCAL_PROJECT_ROOT = Path(__file__).resolve().parents[2]
VIRTUAL_PROFILE_RELATIVE_PATH = Path("Config/plant/sunray150_virtual_px4_classic_profile.json")
MAVROS_PLUGINLIST_RELATIVE_PATH = Path("Config/gazebo/mavros/px4_pluginlists.yaml")


BODY_VISUAL = """      <visual name='base_link_assembled_visual'>
        <pose>0 0 0 1.57079632679 0 0</pose>
        <geometry>
          <mesh>
            <uri>model://sunray150_with_mid360/meshes/sunray150_dae_mid360_realistic_material_audit_gazebo_body_static.obj</uri>
          </mesh>
        </geometry>
      </visual>"""


ROTOR_VISUAL_TEMPLATE = """      <visual name='rotor_{idx}_assembled_propeller_visual'>
        <geometry>
          <mesh>
            <uri>model://sunray150_with_mid360/meshes/sunray150_propeller_rotor_{idx}_link_local.obj</uri>
          </mesh>
        </geometry>
        <material>
          <ambient>0.58 0.70 0.72 1</ambient>
          <diffuse>0.52 0.66 0.70 1</diffuse>
          <specular>0.08 0.09 0.09 1</specular>
        </material>
      </visual>"""


ASSEMBLED_MID360_INCLUDE_POSE = "-0.000005 0.032295 0.050167 0 0 4.712389"
ASSEMBLED_MID360_RAY_SENSOR_POSE = "-0.000005 0.032295 0.150167 0 0 4.712389"
SUNRAY_MID360_RAY_SENSOR_LOCAL_POSE = "0 0 0.1 0 0 0"
SUNRAY_MID360_PLUGIN_DOWNSAMPLE = int(os.environ.get("SUNRAY_MID360_PLUGIN_DOWNSAMPLE", "1"))
SUNRAY_MID360_LIDAR_UPDATE_RATE_HZ = float(os.environ.get("SUNRAY_MID360_LIDAR_UPDATE_RATE_HZ", "20.0"))
SUNRAY_MID360_IMU_UPDATE_RATE_HZ = 200
SUNRAY_FLIGHT_CONTROLLER_IMU_UPDATE_RATE_HZ = 400
SUNRAY_GAZEBO_MAX_STEP_SIZE_S = os.environ.get("SUNRAY_GAZEBO_MAX_STEP_SIZE_S", "0.001")
SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ = int(os.environ.get("SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ", "1000"))
SUNRAY_LIVOX_PLUGIN_FILENAME = os.environ.get("SUNRAY_LIVOX_PLUGIN_FILENAME", "liblivox_laser_simulation.so")
SUNRAY_MID360_CSV_FILE_NAME = os.environ.get("SUNRAY_MID360_CSV_FILE_NAME", "mid360-real-centr.csv")
SUNRAY_MID360_SENSOR_MODE = os.environ.get("SUNRAY_MID360_SENSOR_MODE", "nested").strip().lower()
if SUNRAY_MID360_SENSOR_MODE not in {"inline", "nested"}:
    raise RuntimeError(f"unsupported SUNRAY_MID360_SENSOR_MODE={SUNRAY_MID360_SENSOR_MODE!r}")
SUNRAY_MAVLINK_ENABLE_LOCKSTEP = os.environ.get("SUNRAY_MAVLINK_ENABLE_LOCKSTEP", "true").strip().lower()
if SUNRAY_MAVLINK_ENABLE_LOCKSTEP not in {"true", "false"}:
    raise RuntimeError(f"unsupported SUNRAY_MAVLINK_ENABLE_LOCKSTEP={SUNRAY_MAVLINK_ENABLE_LOCKSTEP!r}")
SUNRAY_MAVLINK_INTERFACE_MODE = os.environ.get("SUNRAY_MAVLINK_INTERFACE_MODE", "enabled").strip().lower()
if SUNRAY_MAVLINK_INTERFACE_MODE not in {"enabled", "disabled"}:
    raise RuntimeError(f"unsupported SUNRAY_MAVLINK_INTERFACE_MODE={SUNRAY_MAVLINK_INTERFACE_MODE!r}")
SUNRAY_GPS_SENSOR_MODE = os.environ.get("SUNRAY_GPS_SENSOR_MODE", "removed").strip().lower()
if SUNRAY_GPS_SENSOR_MODE not in {"removed", "inline", "nested"}:
    raise RuntimeError(f"unsupported SUNRAY_GPS_SENSOR_MODE={SUNRAY_GPS_SENSOR_MODE!r}")


MID360_NESTED_INCLUDE = """    <include>
      <uri>model://livox_mid360</uri>
      <name>livox_mid360_{{{{mavlink_id}}}}</name>
      <pose>{assembled_mid360_include_pose}</pose>
    </include>
    <joint name="mid360_joint" type="fixed">
      <child>livox_mid360_{{{{mavlink_id}}}}::base_link</child>
      <parent>base_link</parent>
      <axis>
        <xyz>0 0 1</xyz>
        <limit>
          <upper>0</upper>
          <lower>0</lower>
        </limit>
      </axis>
    </joint>""".format(assembled_mid360_include_pose=ASSEMBLED_MID360_INCLUDE_POSE)


GPS_NESTED_INCLUDE = """<include>
  <uri>model://gps</uri>
  <pose>0.1 0 0 0 0 0</pose>
  <name>gps0</name>
</include>
<joint name='gps0_joint' type='fixed'>
  <child>gps0::link</child>
  <parent>base_link</parent>
</joint>"""


MID360_INLINE_SENSORS = """      <sensor type="ray" name="laser_livox_{{{{mavlink_id}}}}">
        <pose>{ray_sensor_pose}</pose>
        <visualize>false</visualize>
        <always_on>True</always_on>
        <update_rate>{lidar_rate}</update_rate>
        <plugin name="gazebo_ros_laser_controller_{{{{mavlink_id}}}}" filename="{livox_plugin_filename}">
          <ray>
            <scan>
              <horizontal>
                <samples>100</samples>
                <resolution>1</resolution>
                <min_angle>-3.1415926535897931</min_angle>
                <max_angle>3.1415926535897931</max_angle>
              </horizontal>
              <vertical>
                <samples>50</samples>
                <resolution>1</resolution>
                <min_angle>-3.1415926535897931</min_angle>
                <max_angle>3.1415926535897931</max_angle>
              </vertical>
            </scan>
            <range>
              <min>0.4</min>
              <max>40</max>
              <resolution>1</resolution>
            </range>
            <noise>
              <type>gaussian</type>
              <mean>0.0</mean>
              <stddev>0.0</stddev>
            </noise>
          </ray>
          <visualize>0</visualize>
          <samples>20000</samples>
          <downsample>{downsample}</downsample>
          <csv_file_name>{mid360_csv_file_name}</csv_file_name>
          <publish_pointcloud_type>1</publish_pointcloud_type>
          <robotNamespace>/uav{{{{mavlink_id}}}}</robotNamespace>
          <ros_topic>livox/lidar</ros_topic>
          <frameName>base_link</frameName>
        </plugin>
      </sensor>

      <sensor name="mid360_imu_sensor_{{{{mavlink_id}}}}" type="imu">
        <pose>{imu_sensor_pose}</pose>
        <always_on>true</always_on>
        <update_rate>{imu_rate}</update_rate>
        <visualize>0</visualize>
        <topic>livox/imu</topic>
        <plugin filename="libgazebo_ros_imu_sensor.so" name="mid360_imu_plugin_{{{{mavlink_id}}}}">
          <robotNamespace>/uav{{{{mavlink_id}}}}</robotNamespace>
          <topicName>livox/imu</topicName>
          <bodyName>base_link</bodyName>
          <updateRateHZ>{imu_rate_float}</updateRateHZ>
          <gaussianNoise>0.0</gaussianNoise>
          <xyzOffset>0 0 0</xyzOffset>
          <rpyOffset>0 0 0</rpyOffset>
          <frameName>base_link</frameName>
        </plugin>
      </sensor>""".format(
    ray_sensor_pose=ASSEMBLED_MID360_RAY_SENSOR_POSE,
    imu_sensor_pose=ASSEMBLED_MID360_INCLUDE_POSE,
    lidar_rate=SUNRAY_MID360_LIDAR_UPDATE_RATE_HZ,
    downsample=SUNRAY_MID360_PLUGIN_DOWNSAMPLE,
    livox_plugin_filename=SUNRAY_LIVOX_PLUGIN_FILENAME,
    mid360_csv_file_name=SUNRAY_MID360_CSV_FILE_NAME,
    imu_rate=SUNRAY_MID360_IMU_UPDATE_RATE_HZ,
    imu_rate_float=float(SUNRAY_MID360_IMU_UPDATE_RATE_HZ),
)


INLINE_GPS_SENSOR = """<link name="gps{{mavlink_id}}">
  <pose>0.0 0 0 0 0 0</pose>
  <inertial>
    <pose>0 0 0 0 0 0</pose>
    <mass>0.015</mass>
    <inertia>
      <ixx>1e-05</ixx>
      <ixy>0</ixy>
      <ixz>0</ixz>
      <iyy>1e-05</iyy>
      <iyz>0</iyz>
      <izz>1e-05</izz>
    </inertia>
  </inertial>
  <visual name="visual">
    <geometry>
      <cylinder>
        <radius>0.01</radius>
        <length>0.002</length>
      </cylinder>
    </geometry>
    <material>
      <script>
        <name>Gazebo/Black</name>
      </script>
    </material>
  </visual>
  <sensor name="gps_sensor_{{mavlink_id}}" type="gps">
    <pose>0 0 0 0 0 0</pose>
    <update_rate>5.0</update_rate>
    <always_on>true</always_on>
    <visualize>false</visualize>
    <plugin name="gps_plugin_{{mavlink_id}}" filename="libgazebo_gps_plugin.so">
      <robotNamespace></robotNamespace>
      <topic>gps</topic>
      <gpsNoise>true</gpsNoise>
      <gpsXYRandomWalk>2.0</gpsXYRandomWalk>
      <gpsZRandomWalk>4.0</gpsZRandomWalk>
      <gpsXYNoiseDensity>2.0e-4</gpsXYNoiseDensity>
      <gpsZNoiseDensity>4.0e-4</gpsZNoiseDensity>
      <gpsVXYNoiseDensity>0.2</gpsVXYNoiseDensity>
      <gpsVZNoiseDensity>0.4</gpsVZNoiseDensity>
    </plugin>
  </sensor>
</link>
<joint name="gps{{mavlink_id}}_joint" type="fixed">
  <child>gps{{mavlink_id}}</child>
  <parent>base_link</parent>
</joint>"""


def replace_one(pattern: str, repl: str, text: str, label: str) -> tuple[str, int]:
    text2, count = re.subn(pattern, repl, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError(f"expected exactly one replacement for {label}, got {count}")
    return text2, count


def replace_one_if_present(pattern: str, repl: str, text: str) -> tuple[str, int]:
    return re.subn(pattern, repl, text, count=1, flags=re.DOTALL)


def insert_before_rosbag_plugin(text: str, block: str, label: str) -> tuple[str, int]:
    """Insert an SDF block before rosbag while retaining the source indentation."""
    pattern = (
        r"(?m)^(?P<indent>[ \t]*)(?P<plugin><plugin name='rosbag' "
        r"filename='libgazebo_multirotor_base_plugin\.so'>)"
    )

    def replacement(match: re.Match[str]) -> str:
        indent = match.group("indent")
        rendered = "\n".join(f"{indent}{line}" if line else "" for line in block.splitlines())
        return f"{rendered}\n{indent}{match.group('plugin')}"

    text2, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"expected exactly one replacement for {label}, got {count}")
    return text2, count


def format_scalar(value: object) -> str:
    """Render profile numbers consistently for SDF text without losing precision."""
    return f"{float(value):.12g}"


def format_pose(values: object) -> str:
    if not isinstance(values, list) or len(values) != 6:
        raise ValueError(f"expected six-component pose, got {values!r}")
    return " ".join(format_scalar(value) for value in values)


def format_xyz_pose(values: object) -> str:
    if not isinstance(values, list) or len(values) != 3:
        raise ValueError(f"expected three-component position, got {values!r}")
    return " ".join(format_scalar(value) for value in values) + " 0 0 0"


def format_link_pose(values: object) -> str:
    if isinstance(values, list) and len(values) == 3:
        return format_xyz_pose(values)
    return format_pose(values)


def gps_mass_accounting_key(mid360_sensor_mode: str, gps_sensor_mode: str) -> str:
    """Return the profile entry that exactly matches the generated sensor tree."""
    if gps_sensor_mode == "removed":
        return f"{mid360_sensor_mode}_mid360"
    return f"{mid360_sensor_mode}_mid360_gps"


def load_virtual_profile(project_root: Path) -> dict[str, Any]:
    """Load the project-owned virtual plant contract used by every sync."""
    profile_path = project_root / VIRTUAL_PROFILE_RELATIVE_PATH
    if not profile_path.exists():
        raise FileNotFoundError(profile_path)
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if profile.get("schema") != "mosim.sunray150_virtual_px4_classic_profile.v1":
        raise RuntimeError(f"unsupported virtual profile schema in {profile_path}")
    if profile.get("profile_id") != "sunray150_virtual_px4_classic_v1":
        raise RuntimeError(f"unsupported virtual profile id in {profile_path}")
    return profile


def replace_link_pose(text: str, link_name: str, pose: object, label: str) -> tuple[str, int]:
    return replace_one(
        rf"(<link\s+name=['\"]{re.escape(link_name)}['\"]>.*?<pose>)\s*[^<]+(\s*</pose>)",
        rf"\g<1>{format_link_pose(pose)}\g<2>",
        text,
        label,
    )


def replace_link_inertial_scalar(
    text: str,
    link_name: str,
    field_name: str,
    value: object,
    label: str,
) -> tuple[str, int]:
    return replace_one(
        rf"(<link\s+name=['\"]{re.escape(link_name)}['\"]>.*?<inertial>.*?<{field_name}>)\s*[^<]+(\s*</{field_name}>)",
        rf"\g<1>{format_scalar(value)}\g<2>",
        text,
        label,
    )


def replace_plugin_scalar(
    text: str,
    plugin_name: str,
    field_name: str,
    value: object,
    label: str,
) -> tuple[str, int]:
    return replace_one(
        rf"(<plugin\s+name=['\"]{re.escape(plugin_name)}['\"]\s+filename=['\"]libgazebo_motor_model\.so['\"]>.*?<{field_name}>)\s*[^<]+(\s*</{field_name}>)",
        rf"\g<1>{format_scalar(value)}\g<2>",
        text,
        label,
    )


def replace_plugin_text(
    text: str,
    plugin_name: str,
    field_name: str,
    value: str,
    label: str,
) -> tuple[str, int]:
    return replace_one(
        rf"(<plugin\s+name=['\"]{re.escape(plugin_name)}['\"]\s+filename=['\"]libgazebo_motor_model\.so['\"]>.*?<{field_name}>)\s*[^<]+(\s*</{field_name}>)",
        rf"\g<1>{value}\g<2>",
        text,
        label,
    )


def sync_meshes(source_model: Path, target_model: Path) -> list[str]:
    source_meshes = source_model / "meshes"
    target_meshes = target_model / "meshes"
    target_meshes.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    required_files = [
        "sunray150_dae_mid360_realistic_material_audit_gazebo_body_static.obj",
        "sunray150_dae_mid360_realistic_material_audit_gazebo_visual.mtl",
        "sunray150_propeller_rotor_0_link_local.obj",
        "sunray150_propeller_rotor_1_link_local.obj",
        "sunray150_propeller_rotor_2_link_local.obj",
        "sunray150_propeller_rotor_3_link_local.obj",
    ]
    for name in required_files:
        src = source_meshes / name
        if not src.exists():
            raise FileNotFoundError(src)
        dst = target_meshes / name
        shutil.copy2(src, dst)
        copied.append(str(dst))

    source_textures = source_meshes / "Textures"
    if source_textures.exists():
        target_textures = target_meshes / "Textures"
        target_textures.mkdir(parents=True, exist_ok=True)
        for src in sorted(source_textures.glob("*")):
            if src.is_file():
                dst = target_textures / src.name
                shutil.copy2(src, dst)
                copied.append(str(dst))
    return copied


def patch_drone_model_text(
    text: str,
    profile: dict[str, Any] | None = None,
    mid360_sensor_mode: str | None = None,
    gps_sensor_mode: str | None = None,
) -> tuple[str, dict[str, int]]:
    original = text
    replacements: dict[str, int] = {}

    if profile is None:
        profile = load_virtual_profile(LOCAL_PROJECT_ROOT)
    sensor_mode = mid360_sensor_mode or SUNRAY_MID360_SENSOR_MODE
    if sensor_mode not in {"inline", "nested"}:
        raise RuntimeError(f"unsupported MID360 sensor mode {sensor_mode!r}")
    gps_mode = gps_sensor_mode or SUNRAY_GPS_SENSOR_MODE
    if gps_mode not in {"removed", "inline", "nested"}:
        raise RuntimeError(f"unsupported GPS sensor mode {gps_mode!r}")

    mass_accounting = profile["mass_accounting"]
    ros1_accounting = mass_accounting["ros1_gazebo_classic"]
    mass_accounting_key = gps_mass_accounting_key(sensor_mode, gps_mode)
    if mass_accounting_key not in ros1_accounting:
        raise RuntimeError(f"missing ROS1 mass-accounting mode {mass_accounting_key!r}")
    mode_accounting = ros1_accounting[mass_accounting_key]
    inertia = profile["inertia"]["diagonal_kg_m2"]
    rotor = profile["rotor"]
    motor = profile["motor_model"]

    text, count = replace_link_inertial_scalar(
        text,
        "base_link",
        "mass",
        mode_accounting["base_link_mass_kg"],
        "ROS1 base-link mass from the virtual profile",
    )
    replacements["base_mass"] = count
    for field_name, value in zip(("ixx", "iyy", "izz"), inertia):
        text, count = replace_link_inertial_scalar(
            text,
            "base_link",
            field_name,
            value,
            f"ROS1 base-link inertia {field_name} from the virtual profile",
        )
        replacements[f"base_inertia_{field_name}"] = count

    rotor_inertia = rotor["inertia_diagonal_kg_m2"]
    gazebo_centers = rotor["gazebo_centers_m"]
    gazebo_order = rotor["gazebo_order"]
    turning_directions = rotor["gazebo_turning_direction"]
    if not all(isinstance(value, list) and len(value) == 4 for value in (gazebo_centers, gazebo_order, turning_directions)):
        raise RuntimeError("virtual profile must define four Gazebo rotor centers, names, and turning directions")

    for index, rotor_name in enumerate(gazebo_order):
        link_name = f"rotor_{index}"
        text, count = replace_link_pose(
            text,
            link_name,
            gazebo_centers[index],
            f"ROS1 {link_name} pose from the virtual profile",
        )
        replacements[f"{link_name}_pose"] = count
        text, count = replace_link_inertial_scalar(
            text,
            link_name,
            "mass",
            rotor["mass_kg_each"],
            f"ROS1 {link_name} mass from the virtual profile",
        )
        replacements[f"{link_name}_mass"] = count
        for field_name, value in zip(("ixx", "iyy", "izz"), rotor_inertia):
            text, count = replace_link_inertial_scalar(
                text,
                link_name,
                field_name,
                value,
                f"ROS1 {link_name} inertia {field_name} from the virtual profile",
            )
            replacements[f"{link_name}_inertia_{field_name}"] = count

        plugin_name = f"{rotor_name}_motor_model"
        text, count = replace_plugin_text(
            text,
            plugin_name,
            "turningDirection",
            str(turning_directions[index]),
            f"ROS1 {plugin_name} direction from the virtual profile",
        )
        replacements[f"{plugin_name}_direction"] = count
        for field_name, value in (
            ("timeConstantUp", motor["time_constant_up_s"]),
            ("timeConstantDown", motor["time_constant_down_s"]),
            ("maxRotVelocity", motor["max_rotor_velocity_rad_s"]),
            ("motorConstant", motor["motor_constant_n_per_rad_s2"]),
            ("momentConstant", motor["moment_constant_ratio_m"]),
            ("rotorDragCoefficient", motor["rotor_drag_coefficient"]),
            ("rollingMomentCoefficient", motor["rolling_moment_coefficient"]),
            ("rotorVelocitySlowdownSim", motor["rotor_velocity_slowdown_sim"]),
        ):
            text, count = replace_plugin_scalar(
                text,
                plugin_name,
                field_name,
                value,
                f"ROS1 {plugin_name} {field_name} from the virtual profile",
            )
            replacements[f"{plugin_name}_{field_name}"] = count

    text, count = replace_one(
        r"(<plugin\s+name=['\"]rosbag['\"]\s+filename=['\"]libgazebo_multirotor_base_plugin\.so['\"]>.*?<rotorVelocitySlowdownSim>)\s*[^<]+(\s*</rotorVelocitySlowdownSim>)",
        rf"\g<1>{format_scalar(motor['rotor_velocity_slowdown_sim'])}\g<2>",
        text,
        "ROS1 rosbag rotor velocity slowdown from the virtual profile",
    )
    replacements["rosbag_rotorVelocitySlowdownSim"] = count

    text, count = replace_one_if_present(
        r"<visual name='base_link_inertia_visual'>.*?</visual>",
        BODY_VISUAL,
        text,
    )
    replacements["base_visual"] = count

    for idx in range(4):
        text, count = replace_one_if_present(
            rf"\s*<collision name='rotor_{idx}_collision'>.*?</collision>",
            "",
            text,
        )
        replacements[f"rotor_{idx}_collision_removed"] = count

        text, count = replace_one_if_present(
            rf"<visual name='rotor_{idx}_visual'>.*?</visual>",
            ROTOR_VISUAL_TEMPLATE.format(idx=idx),
            text,
        )
        replacements[f"rotor_{idx}_visual"] = count

    text, count = replace_one_if_present(
        r"\s*<include>\s*<uri>model://livox_mid360</uri>\s*(?:<name>.*?</name>\s*)?<pose>.*?</pose>\s*</include>\s*"
        r"<joint name=\"mid360_joint\" type=\"fixed\">.*?</joint>",
        "",
        text,
    )
    replacements["old_mid360_include_removed"] = count

    text, count = replace_one_if_present(
        r"(?m)^[ \t]*<include>\s*<uri>model://gps</uri>\s*(?:<pose>.*?</pose>\s*)?"
        r"(?:<name>gps(?:0)?</name>\s*)?</include>\s*"
        r"<joint name=['\"]gps(?:0)?_joint['\"] type=['\"]fixed['\"]>.*?</joint>\r?\n?",
        "",
        text,
    )
    replacements["nested_gps_include_removed"] = count

    text, count = replace_one_if_present(
        r"(?m)^[ \t]*<link name=['\"](?:gps_link_|gps)[^'\"]+['\"]>.*?</link>\s*"
        r"<joint name=['\"](?:gps_joint_[^'\"]+|gps[^'\"]+_joint)['\"] type=['\"]fixed['\"]>.*?</joint>\r?\n?",
        "",
        text,
    )
    replacements["inline_gps_sensor_removed"] = count

    if "model://gps" in text:
        raise RuntimeError("unrecognized nested GPS block remained after normalization")

    if gps_mode == "nested":
        text, count = insert_before_rosbag_plugin(
            text, GPS_NESTED_INCLUDE, "nested PX4 Gazebo Classic GPS before PX4 plugins"
        )
    else:
        count = 0
    replacements["nested_gps_include_inserted"] = count

    if gps_mode == "inline":
        text, count = insert_before_rosbag_plugin(
            text, INLINE_GPS_SENSOR, "inline per-instance GPS sensor before PX4 plugins"
        )
    else:
        count = 0
    replacements["inline_gps_sensor_inserted"] = count

    text, count = replace_one_if_present(
        r"\s*<sensor type=\"ray\" name=\"laser_livox[^\"]*\">.*?</sensor>\s*"
        r"<sensor name=\"mid360_imu_sensor[^\"]*\" type=\"imu\">.*?</sensor>",
        "",
        text,
    )
    replacements["inline_mid360_sensor_removed"] = count

    if sensor_mode == "nested":
        if "model://livox_mid360" not in text:
            text, count = replace_one(
                r"(<link name='base_link'>.*?</link>)",
                rf"\1\n{MID360_NESTED_INCLUDE}",
                text,
                "restore nested livox_mid360 include and fixed joint",
            )
        else:
            count = 0
        replacements["inline_mid360_sensor_inserted"] = 0
        replacements["nested_mid360_include_restored"] = count
    else:
        if "laser_livox" not in text:
            text, count = replace_one(
                r"(<link name='base_link'>.*?)(\s*</link>)",
                rf"\1\n{MID360_INLINE_SENSORS}\2",
                text,
                "inline livox_mid360 ray and IMU sensors into base_link",
            )
        else:
            count = 0
        replacements["inline_mid360_sensor_inserted"] = count
        replacements["nested_mid360_include_restored"] = 0

    text, count = re.subn(
        r"\s*<pubRate>\s*400\s*</pubRate>",
        "",
        text,
        count=1,
    )
    replacements["unsupported_flight_controller_imu_pub_rate_removed"] = count

    text, count = re.subn(
        r"(<plugin name='gazebo_imu_plugin' filename='libgazebo_imu_plugin\.so'>.*?<updateRate>)\s*[^<]+\s*(</updateRate>)",
        rf"\g<1>{float(SUNRAY_FLIGHT_CONTROLLER_IMU_UPDATE_RATE_HZ):.1f}\2",
        text,
        count=1,
        flags=re.DOTALL,
    )
    replacements["flight_controller_imu_update_rate_hz"] = count

    text, count = re.subn(
        r"(<enable_lockstep>)\s*(?:true|false)\s*(</enable_lockstep>)",
        rf"\g<1>{SUNRAY_MAVLINK_ENABLE_LOCKSTEP}\2",
        text,
        count=1,
    )
    replacements["mavlink_enable_lockstep"] = count

    text, count = re.subn(
        r"\s*<!-- MOSIM_DISABLED_MAVLINK_INTERFACE_BEGIN\s*(<plugin name='mavlink_interface' filename='libgazebo_mavlink_interface\.so'>.*?</plugin>)\s*MOSIM_DISABLED_MAVLINK_INTERFACE_END -->",
        r"\n    \1",
        text,
        count=1,
        flags=re.DOTALL,
    )
    replacements["mavlink_interface_reenabled"] = count

    if SUNRAY_MAVLINK_INTERFACE_MODE == "disabled":
        text, count = re.subn(
            r"\s*<plugin name='mavlink_interface' filename='libgazebo_mavlink_interface\.so'>.*?</plugin>",
            r"\n    <!-- MOSIM_DISABLED_MAVLINK_INTERFACE_BEGIN \g<0> MOSIM_DISABLED_MAVLINK_INTERFACE_END -->",
            text,
            count=1,
            flags=re.DOTALL,
        )
    else:
        count = 0
    replacements["mavlink_interface_disabled"] = count

    return text, replacements


def patch_drone_model_file(
    model_path: Path,
    profile: dict[str, Any],
    mid360_sensor_mode: str,
    gps_sensor_mode: str,
) -> dict[str, int]:
    text = model_path.read_text(encoding="utf-8")
    patched, replacements = patch_drone_model_text(text, profile, mid360_sensor_mode, gps_sensor_mode)
    if patched == text:
        replacements["backup_written"] = 0
        return replacements

    backup_path = model_path.with_suffix(model_path.suffix + f".bak_mosim_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(model_path, backup_path)
    model_path.write_text(patched, encoding="utf-8")
    replacements["backup_written"] = 1
    return replacements


def patch_jinja(
    jinja_path: Path,
    profile: dict[str, Any],
    mid360_sensor_mode: str,
    gps_sensor_mode: str,
) -> dict[str, int]:
    original = jinja_path.read_text(encoding="utf-8")
    text, replacements = patch_drone_model_text(original, profile, mid360_sensor_mode, gps_sensor_mode)

    if text == original:
        replacements["backup_written"] = 0
        return replacements

    backup_path = jinja_path.with_suffix(jinja_path.suffix + f".bak_mosim_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copy2(jinja_path, backup_path)
    jinja_path.write_text(text, encoding="utf-8")
    replacements["backup_written"] = 1
    return replacements


def patch_world_physics(world_path: Path) -> dict[str, int]:
    text = world_path.read_text(encoding="utf-8")
    original = text
    replacements: dict[str, int] = {}

    text, count = re.subn(
        r"(<max_step_size>)\s*[^<]+\s*(</max_step_size>)",
        rf"\g<1>{SUNRAY_GAZEBO_MAX_STEP_SIZE_S}\2",
        text,
        count=1,
    )
    replacements["gazebo_max_step_size_s"] = count

    text, count = re.subn(
        r"(<real_time_update_rate>)\s*[^<]+\s*(</real_time_update_rate>)",
        rf"\g<1>{SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ}\2",
        text,
        count=1,
    )
    replacements["gazebo_real_time_update_rate_hz"] = count

    if text != original:
        backup_path = world_path.with_suffix(world_path.suffix + f".bak_mosim_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copy2(world_path, backup_path)
        world_path.write_text(text, encoding="utf-8")
        replacements["backup_written"] = 1
    else:
        replacements["backup_written"] = 0

    patched = world_path.read_text(encoding="utf-8")
    if f"<max_step_size>{SUNRAY_GAZEBO_MAX_STEP_SIZE_S}</max_step_size>" not in patched:
        raise RuntimeError("planning_test.world max_step_size was not set to the MoSim 400Hz physics baseline")
    if f"<real_time_update_rate>{SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ}</real_time_update_rate>" not in patched:
        raise RuntimeError("planning_test.world real_time_update_rate was not set to the MoSim 400Hz physics baseline")
    return replacements


def delete_default_livox_sensor_shell(sensor_sdf_path: Path) -> dict[str, int]:
    text = sensor_sdf_path.read_text(encoding="utf-8")
    replacements: dict[str, int] = {}

    collision_pattern = (
        r"\s*<collision\s+name=[\"']collision[\"']>\s*"
        r"<pose>0 0 0 1\.57 0 3\.14159</pose>.*?"
        r"model://livox_mid360/meshes/test2\.dae.*?</collision>"
    )
    text, count = re.subn(collision_pattern, "", text, count=1, flags=re.DOTALL)
    replacements["default_mid360_collision_deleted"] = count

    visual_pattern = (
        r"\s*<visual\s+name=[\"']link_fixed_joint_lump__oasis_300_visual[\"']>\s*"
        r"<pose>0 0 0 1\.57 0 3\.14159</pose>.*?"
        r"model://livox_mid360/meshes/test2\.dae.*?</visual>"
    )
    text, count = re.subn(visual_pattern, "", text, count=1, flags=re.DOTALL)
    replacements["default_mid360_visual_deleted"] = count

    text, count = re.subn(
        r"(<sensor type=\"ray\" name=\"laser_livox\">\s*)<pose>.*?</pose>",
        rf"\1<pose>{SUNRAY_MID360_RAY_SENSOR_LOCAL_POSE}</pose>",
        text,
        count=1,
        flags=re.DOTALL,
    )
    replacements["assembled_mid360_ray_sensor_local_pose"] = count

    text, count = re.subn(
        r"(<sensor type=\"ray\" name=\"laser_livox\">.*?<update_rate>)\s*[^<]+\s*(</update_rate>)",
        rf"\g<1>{SUNRAY_MID360_LIDAR_UPDATE_RATE_HZ:g}\2",
        text,
        count=1,
        flags=re.DOTALL,
    )
    replacements["mid360_lidar_sensor_update_rate_hz"] = count

    text, count = re.subn(
        r"<downsample>\s*\d+\s*</downsample>",
        f"<downsample>{SUNRAY_MID360_PLUGIN_DOWNSAMPLE}</downsample>",
        text,
        count=1,
    )
    replacements["mid360_plugin_downsample"] = count

    text, count = re.subn(
        r"<csv_file_name>\s*[^<]+\s*</csv_file_name>",
        f"<csv_file_name>{SUNRAY_MID360_CSV_FILE_NAME}</csv_file_name>",
        text,
        count=1,
    )
    replacements["mid360_csv_file_name"] = count

    text, count = re.subn(
        r'(<plugin name="gazebo_ros_laser_controller" filename=")[^"]+(">)',
        rf"\g<1>{SUNRAY_LIVOX_PLUGIN_FILENAME}\2",
        text,
        count=1,
    )
    replacements["mid360_livox_plugin_filename"] = count

    text, count = re.subn(
        r"(<sensor name=\"imu_sensor\" type=\"imu\">.*?<update_rate>)\s*[^<]+\s*(</update_rate>)",
        rf"\g<1>{SUNRAY_MID360_IMU_UPDATE_RATE_HZ}\2",
        text,
        count=1,
        flags=re.DOTALL,
    )
    replacements["mid360_imu_sensor_update_rate_hz"] = count

    text, count = re.subn(
        r"(<updateRateHZ>)\s*[^<]+\s*(</updateRateHZ>)",
        rf"\g<1>{float(SUNRAY_MID360_IMU_UPDATE_RATE_HZ):.1f}\2",
        text,
        count=1,
    )
    replacements["mid360_imu_plugin_update_rate_hz"] = count

    if any(replacements.values()):
        backup_path = sensor_sdf_path.with_suffix(
            sensor_sdf_path.suffix + f".bak_mosim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        shutil.copy2(sensor_sdf_path, backup_path)
        sensor_sdf_path.write_text(text, encoding="utf-8")
        replacements["backup_written"] = 1
    else:
        replacements["backup_written"] = 0

    # The sensor/plugin blocks must survive this visual-only patch.
    patched = sensor_sdf_path.read_text(encoding="utf-8")
    required = [
        'sensor type="ray" name="laser_livox"',
        "<ros_topic>livox/lidar</ros_topic>",
        'sensor name="imu_sensor" type="imu"',
        "libgazebo_ros_imu_sensor.so",
        "<topicName>livox/imu</topicName>",
    ]
    missing = [needle for needle in required if needle not in patched]
    if (
        f'filename="{SUNRAY_LIVOX_PLUGIN_FILENAME}"' not in patched
        and 'filename="liblivox_laser_simulation.so"' not in patched
    ):
        missing.append(f'filename="{SUNRAY_LIVOX_PLUGIN_FILENAME}"')
    if missing:
        raise RuntimeError(f"livox sensor patch removed required sensor/plugin entries: {missing}")
    if "model://livox_mid360/meshes/test2.dae" in patched:
        raise RuntimeError("default livox_mid360 mesh reference still exists after deletion patch")
    return replacements


def patch_planning_launch_time_arg(launch_path: Path) -> dict[str, int]:
    text = launch_path.read_text(encoding="utf-8")
    replacements: dict[str, int] = {}
    if '<arg name="use_sim_time" default=' not in text:
        needle = '<arg name="world" default="$(find sunray_simulator)/worlds/planning_test.world"/>'
        if needle not in text:
            raise RuntimeError("planning launch world arg not found for use_sim_time insertion")
        text = text.replace(needle, needle + '\n    <arg name="use_sim_time" default="false"/>', 1)
        count = 1
        replacements["use_sim_time_arg_inserted"] = count
    else:
        replacements["use_sim_time_arg_inserted"] = 0

    text, count = re.subn(
        r'<arg name="use_sim_time" value="false"\s*/>',
        '<arg name="use_sim_time" value="$(arg use_sim_time)"/>',
        text,
        count=1,
    )
    replacements["use_sim_time_value_parameterized"] = count

    if any(replacements.values()):
        backup_path = launch_path.with_suffix(
            launch_path.suffix + f".bak_mosim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        shutil.copy2(launch_path, backup_path)
        launch_path.write_text(text, encoding="utf-8")
        replacements["backup_written"] = 1
    else:
        replacements["backup_written"] = 0

    patched = launch_path.read_text(encoding="utf-8")
    if '<arg name="use_sim_time" default="false"/>' not in patched:
        raise RuntimeError("planning launch is missing configurable use_sim_time arg")
    if '<arg name="use_sim_time" value="$(arg use_sim_time)"/>' not in patched:
        raise RuntimeError("planning launch still does not pass configurable use_sim_time to empty_world")
    return replacements


def patch_control_launch_tunable_params(launch_path: Path) -> dict[str, int]:
    text = launch_path.read_text(encoding="utf-8")
    replacements: dict[str, int] = {}

    anchor = '<arg name="use_offset" default="false" />'
    insert = """<arg name="use_offset" default="false" />
    <arg name="control_loop_hz" default="200.0" />
    <arg name="quad_mass" default="1.0" />
    <arg name="hov_percent" default="0.37" />
    <arg name="pxy_int_max" default="10.0" />
    <arg name="pz_int_max" default="10.0" />
    <arg name="Kp_xy" default="3.0" />
    <arg name="Kp_z" default="3.0" />
    <arg name="Kv_xy" default="3.0" />
    <arg name="Kv_z" default="3.0" />
    <arg name="Kvi_xy" default="0.3" />
    <arg name="Kvi_z" default="0.3" />
    <arg name="tilt_angle_max" default="20.0" />"""
    if '<arg name="quad_mass" default=' not in text:
        if anchor not in text:
            raise RuntimeError("sunray_control_node.launch use_offset arg not found for PID arg insertion")
        text = text.replace(anchor, insert, 1)
        replacements["pid_args_inserted"] = 1
    else:
        replacements["pid_args_inserted"] = 0

    param_to_arg = {
        "system_params/control_loop_hz": "control_loop_hz",
        "ctrl_param/quad_mass": "quad_mass",
        "ctrl_param/hov_percent": "hov_percent",
        "ctrl_param/pxy_int_max": "pxy_int_max",
        "ctrl_param/pz_int_max": "pz_int_max",
        "ctrl_param/Kp_xy": "Kp_xy",
        "ctrl_param/Kp_z": "Kp_z",
        "ctrl_param/Kv_xy": "Kv_xy",
        "ctrl_param/Kv_z": "Kv_z",
        "ctrl_param/Kvi_xy": "Kvi_xy",
        "ctrl_param/Kvi_z": "Kvi_z",
        "ctrl_param/tilt_angle_max": "tilt_angle_max",
    }
    for param_name, arg_name in param_to_arg.items():
        text, count = re.subn(
            rf'(<param name="{re.escape(param_name)}" value=")[^"]+("\s*/>)',
            rf'\g<1>$(arg {arg_name})\2',
            text,
            count=1,
        )
        replacements[f"{arg_name}_parameterized"] = count

    if any(replacements.values()):
        backup_path = launch_path.with_suffix(
            launch_path.suffix + f".bak_mosim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        shutil.copy2(launch_path, backup_path)
        launch_path.write_text(text, encoding="utf-8")
        replacements["backup_written"] = 1
    else:
        replacements["backup_written"] = 0

    patched = launch_path.read_text(encoding="utf-8")
    if '<arg name="control_loop_hz" default=' not in patched:
        if '<arg name="use_offset" default="false" />' not in patched:
            raise RuntimeError("sunray_control_node.launch use_offset arg not found for control_loop_hz insertion")
        patched = patched.replace(
            '<arg name="use_offset" default="false" />',
            '<arg name="use_offset" default="false" />\n    <arg name="control_loop_hz" default="200.0" />',
            1,
        )
        launch_path.write_text(patched, encoding="utf-8")
        replacements["control_loop_arg_inserted"] = 1
    if '<param name="system_params/control_loop_hz" value="$(arg control_loop_hz)" />' not in patched:
        cmd_timeout_param = '<param name="system_params/cmd_timeout" value="$(arg cmd_timeout)" />'
        if cmd_timeout_param not in patched:
            raise RuntimeError("sunray_control_node.launch cmd_timeout param not found for control_loop_hz insertion")
        patched = patched.replace(
            cmd_timeout_param,
            cmd_timeout_param + '\n        <param name="system_params/control_loop_hz" value="$(arg control_loop_hz)" />',
            1,
        )
        launch_path.write_text(patched, encoding="utf-8")
        replacements["control_loop_param_inserted"] = 1
    text = patched
    for param_name, arg_name in param_to_arg.items():
        needle = f'<param name="{param_name}" value="$(arg {arg_name})" />'
        if needle not in patched:
            raise RuntimeError(f"sunray_control_node.launch was not parameterized for {param_name}")
    return replacements


def sync_control_runtime_sources(project_root: Path, sunray_ws: Path) -> dict[str, object]:
    source_root = project_root / "References/Sunray/General_Module/sunray_uav_control"
    target_root = sunray_ws / "General_Module/sunray_uav_control"
    relative_files = [
        Path("uav_control/UAVControl.h"),
        Path("uav_control/UAVControl.cpp"),
        Path("uav_control/uav_control_node.cpp"),
        Path("launch/sunray_control_node.launch"),
    ]
    copied: list[str] = []
    for relative in relative_files:
        src = source_root / relative
        dst = target_root / relative
        if not src.exists():
            raise FileNotFoundError(src)
        if not dst.exists():
            raise FileNotFoundError(dst)
        src_text = src.read_text(encoding="utf-8")
        if dst.read_text(encoding="utf-8") != src_text:
            backup_path = dst.with_suffix(dst.suffix + f".bak_mosim_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy2(dst, backup_path)
            dst.write_text(src_text, encoding="utf-8")
            copied.append(str(relative).replace("\\", "/"))
    return {
        "source_root": str(source_root),
        "target_root": str(target_root),
        "copied": copied,
        "copied_count": len(copied),
    }


def sync_runtime_plugins(project_root: Path, sunray_ws: Path) -> dict[str, object]:
    source_lib = project_root / "References/Sunray/devel/lib"
    target_lib = sunray_ws / "devel/lib"
    plugin_names = [
        "liblivox_laser_simulation.so",
    ]
    copied: list[str] = []
    missing: list[str] = []
    target_lib.mkdir(parents=True, exist_ok=True)
    for name in plugin_names:
        src = source_lib / name
        dst = target_lib / name
        if not src.exists():
            missing.append(str(src))
            continue
        if not dst.exists() or src.stat().st_size != dst.stat().st_size:
            if dst.exists():
                backup_path = dst.with_suffix(dst.suffix + f".bak_mosim_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                shutil.copy2(dst, backup_path)
            shutil.copy2(src, dst)
            copied.append(name)
    if missing:
        raise FileNotFoundError(f"missing runtime plugin source(s): {missing}")
    return {
        "source_lib": str(source_lib),
        "target_lib": str(target_lib),
        "copied": copied,
        "copied_count": len(copied),
    }


def mavros_pluginlist_home_position_state(text: str) -> dict[str, bool]:
    """Return the effective home-position membership from a MAVROS plugin list."""
    if "plugin_whitelist:" not in text:
        raise RuntimeError("MAVROS plugin list has no plugin_whitelist section")
    blacklist, whitelist = text.split("plugin_whitelist:", 1)
    entry = re.compile(r"(?m)^\s*-\s*home_position\s*(?:#.*)?$")
    return {
        "blacklisted": bool(entry.search(blacklist)),
        "whitelisted": bool(entry.search(whitelist)),
    }


def sync_mavros_pluginlist(project_root: Path, sunray_ws: Path) -> dict[str, object]:
    """Install the project-owned MAVROS plugin surface into the runtime copy."""
    source_path = project_root / MAVROS_PLUGINLIST_RELATIVE_PATH
    target_path = sunray_ws / "simulation/sunray_simulator/config/px4_pluginlists.yaml"
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    if not target_path.is_file():
        raise FileNotFoundError(target_path)

    source_text = source_path.read_text(encoding="utf-8")
    home_position = mavros_pluginlist_home_position_state(source_text)
    if home_position["blacklisted"] or not home_position["whitelisted"]:
        raise RuntimeError(
            "project MAVROS profile must whitelist home_position without blacklisting it"
        )
    copied = target_path.read_text(encoding="utf-8") != source_text
    if copied:
        backup_path = target_path.with_suffix(
            target_path.suffix + f".bak_mosim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        shutil.copy2(target_path, backup_path)
        target_path.write_text(source_text, encoding="utf-8")

    target_text = target_path.read_text(encoding="utf-8")
    if target_text != source_text:
        raise RuntimeError("MAVROS plugin-list target differs after sync")
    return {
        "source": str(source_path),
        "target": str(target_path),
        "copied": copied,
        "source_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        "target_sha256": hashlib.sha256(target_text.encode("utf-8")).hexdigest(),
        "home_position_blacklisted": home_position["blacklisted"],
        "home_position_whitelisted": home_position["whitelisted"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT_DEFAULT)
    parser.add_argument("--sunray-ws", type=Path, default=SUNRAY_WS_DEFAULT)
    parser.add_argument("--manifest", type=Path, default=None)
    args = parser.parse_args()

    profile = load_virtual_profile(args.project_root)
    source_model = args.project_root / "Config/gazebo/models/sunray150_assembled"
    target_model = args.sunray_ws / "simulation/sunray_simulator/models/drone_models/sunray150_with_mid360"
    jinja_path = target_model / "sunray150_with_mid360.sdf.jinja"
    sdf_path = target_model / "sunray150_with_mid360.sdf"
    sensor_sdf_path = args.sunray_ws / "simulation/sunray_simulator/models/sensor_models/livox_mid360/livox_mid360.sdf"
    planning_launch_path = args.sunray_ws / "simulation/sunray_simulator/launch_uav_demo/sunray_sim_uav_planning.launch"
    control_launch_path = args.sunray_ws / "General_Module/sunray_uav_control/launch/sunray_control_node.launch"
    planning_world_path = args.sunray_ws / "simulation/sunray_simulator/worlds/planning_test.world"
    project_gps_sdf_path = args.project_root / "Config/gazebo/models/gps/gps.sdf"

    if not source_model.exists():
        raise FileNotFoundError(source_model)
    if not jinja_path.exists():
        raise FileNotFoundError(jinja_path)
    if not sdf_path.exists():
        raise FileNotFoundError(sdf_path)
    if not sensor_sdf_path.exists():
        raise FileNotFoundError(sensor_sdf_path)
    if not planning_launch_path.exists():
        raise FileNotFoundError(planning_launch_path)
    if not control_launch_path.exists():
        raise FileNotFoundError(control_launch_path)
    if not planning_world_path.exists():
        raise FileNotFoundError(planning_world_path)
    if SUNRAY_GPS_SENSOR_MODE == "nested" and not project_gps_sdf_path.exists():
        raise FileNotFoundError(project_gps_sdf_path)

    copied = sync_meshes(source_model, target_model)
    control_source_sync = sync_control_runtime_sources(args.project_root, args.sunray_ws)
    runtime_plugin_sync = sync_runtime_plugins(args.project_root, args.sunray_ws)
    mavros_pluginlist_sync = sync_mavros_pluginlist(args.project_root, args.sunray_ws)
    replacements = patch_jinja(
        jinja_path,
        profile,
        SUNRAY_MID360_SENSOR_MODE,
        SUNRAY_GPS_SENSOR_MODE,
    )
    sdf_replacements = patch_drone_model_file(
        sdf_path,
        profile,
        SUNRAY_MID360_SENSOR_MODE,
        SUNRAY_GPS_SENSOR_MODE,
    )
    sensor_replacements = delete_default_livox_sensor_shell(sensor_sdf_path)
    launch_replacements = patch_planning_launch_time_arg(planning_launch_path)
    control_launch_replacements = patch_control_launch_tunable_params(control_launch_path)
    world_replacements = patch_world_physics(planning_world_path)

    manifest = {
        "schema": "mosim.sunray_ros1_assembled_model_sync.v1",
        "status": "synced",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "virtual_profile": {
            "profile_id": profile["profile_id"],
            "profile_path": str(args.project_root / VIRTUAL_PROFILE_RELATIVE_PATH),
            "takeoff_mass_kg": profile["mass_accounting"]["total_takeoff_mass_kg"],
            "ros1_mass_accounting": profile["mass_accounting"]["ros1_gazebo_classic"],
        },
        "source_model": str(source_model),
        "target_model": str(target_model),
        "patched_jinja": str(jinja_path),
        "patched_sdf": str(sdf_path),
        "patched_sensor_sdf": str(sensor_sdf_path),
        "patched_planning_launch": str(planning_launch_path),
        "patched_control_launch": str(control_launch_path),
        "patched_planning_world": str(planning_world_path),
        "control_source_sync": control_source_sync,
        "runtime_plugin_sync": runtime_plugin_sync,
        "mavros_pluginlist_sync": mavros_pluginlist_sync,
        "copied_count": len(copied),
        "copied_first": copied[:12],
        "replacements": replacements,
        "sdf_replacements": sdf_replacements,
        "sensor_replacements": sensor_replacements,
        "launch_replacements": launch_replacements,
        "control_launch_replacements": control_launch_replacements,
        "world_replacements": world_replacements,
        "frequency_baseline": {
            "gazebo_physics_hz": SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ,
            "gazebo_max_step_size_s": float(SUNRAY_GAZEBO_MAX_STEP_SIZE_S),
            "flight_controller_imu_expected_hz": SUNRAY_FLIGHT_CONTROLLER_IMU_UPDATE_RATE_HZ,
            "flight_controller_imu_source": "gazebo_imu_plugin /imu updateRate is explicitly patched in the assembled Sunray150 SDF",
            "mid360_lidar_update_rate_hz": SUNRAY_MID360_LIDAR_UPDATE_RATE_HZ,
            "mid360_imu_update_rate_hz": SUNRAY_MID360_IMU_UPDATE_RATE_HZ,
        },
        "mid360_sensor_mode": SUNRAY_MID360_SENSOR_MODE,
        "mavlink_enable_lockstep": SUNRAY_MAVLINK_ENABLE_LOCKSTEP,
        "mavlink_interface_mode": SUNRAY_MAVLINK_INTERFACE_MODE,
        "gps_sensor_mode": SUNRAY_GPS_SENSOR_MODE,
        "gps_mass_accounting_mode": gps_mass_accounting_key(
            SUNRAY_MID360_SENSOR_MODE,
            SUNRAY_GPS_SENSOR_MODE,
        ),
        "boundary": [
            "Keeps YunZong/Sunray Gazebo Classic PX4, MAVLink, motor, IMU, p3d, camera, and MID360 plugins; GPS is controlled separately by gps_sensor_mode and defaults to removed.",
            "Replaces only accepted MoSim assembled body visual, rotor propeller visuals, rotor collision omission, and base mass.",
            "Deletes the standalone YunZong livox_mid360 visual/collision mesh because the accepted MoSim assembled body already includes the MID360 visual.",
            f"MID360 sensor mode is {SUNRAY_MID360_SENSOR_MODE}; nested mode restores model://livox_mid360 with a fixed joint, inline mode is diagnostic-only.",
            f"GPS sensor mode is {SUNRAY_GPS_SENSOR_MODE}; nested mode restores the upstream model://gps + gps0_joint transport contract and consumes the matching 1 kg mass-accounting entry.",
            "Uses the project-owned MAVROS plugin profile, including home_position for the passive GPS/EKF state-chain gate.",
            f"Sets mavlink_interface enable_lockstep to {SUNRAY_MAVLINK_ENABLE_LOCKSTEP}; default true preserves Sunray baseline, false is a bounded Goal5 diagnostic for multi-UAV MID360 plugin loading.",
            f"Sets mavlink_interface mode to {SUNRAY_MAVLINK_INTERFACE_MODE}; disabled is a bounded diagnostic only and is not a PX4 closed-loop evidence mode.",
            f"Uses the reviewed MoSim assembly pose for the MID360 mount: {ASSEMBLED_MID360_INCLUDE_POSE}.",
            f"Sets the MID360 LiDAR Gazebo update rate to {SUNRAY_MID360_LIDAR_UPDATE_RATE_HZ:g}Hz for the current FAST-LIO localization profile.",
            f"Sets the Livox plugin downsample to {SUNRAY_MID360_PLUGIN_DOWNSAMPLE} so the raw PointCloud2 density is not reduced before localization review.",
            f"Sets the Livox internal IMU Gazebo update rate to {SUNRAY_MID360_IMU_UPDATE_RATE_HZ}Hz to support the current 20Hz LiDAR/FAST-LIO profile.",
            f"Sets Gazebo physics to {SUNRAY_GAZEBO_REAL_TIME_UPDATE_RATE_HZ}Hz and the PX4 flight-controller IMU /imu plugin updateRate to {SUNRAY_FLIGHT_CONTROLLER_IMU_UPDATE_RATE_HZ}Hz; /imu and /uav1/mavros/imu/data must still be verified by rostopic hz.",
            "Does not claim FAST-LIO success or flight-control performance.",
        ],
    }

    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
