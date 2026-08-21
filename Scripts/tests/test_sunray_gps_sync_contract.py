from __future__ import annotations

import importlib.util
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SYNC_PATH = ROOT / "Scripts" / "sunray" / "sync_assembled_model_into_sunray_ros1.py"
SUNRAY_MODEL_ROOT = (
    ROOT
    / "src"
    / "simulation"
    / "gazebo"
    / "sunray"
    / "models"
    / "drone_models"
    / "sunray150_with_mid360"
)
GPS_MODEL_ROOT = ROOT / "Config" / "gazebo" / "models" / "gps"
MAVROS_PLUGINLIST_PATH = ROOT / "Config" / "gazebo" / "mavros" / "px4_pluginlists.yaml"
PROFILE_PATH = ROOT / "Config" / "plant" / "sunray150_virtual_px4_classic_profile.json"


def load_sync_module():
    spec = importlib.util.spec_from_file_location("mosim_sunray_sync_contract", SYNC_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_nested_gps_preserves_px4_transport_contract_and_is_idempotent() -> None:
    sync = load_sync_module()
    profile = sync.load_virtual_profile(ROOT)

    for name in ("sunray150_with_mid360.sdf.jinja", "sunray150_with_mid360.sdf"):
        source = (SUNRAY_MODEL_ROOT / name).read_text(encoding="utf-8")
        patched, replacements = sync.patch_drone_model_text(source, profile, "nested", "nested")
        replayed, replay_replacements = sync.patch_drone_model_text(
            patched, profile, "nested", "nested"
        )

        assert patched.count("model://gps") == 1
        assert "<name>gps0</name>" in patched
        assert "<joint name='gps0_joint' type='fixed'>" in patched
        assert "<child>gps0::link</child>" in patched
        assert "gps_joint_1" not in patched
        assert replacements["nested_gps_include_inserted"] == 1
        assert replay_replacements["nested_gps_include_inserted"] == 1
        assert patched == replayed


def test_flight_controller_imu_rate_cleanup_cannot_modify_p3d_rate() -> None:
    sync = load_sync_module()
    profile = sync.load_virtual_profile(ROOT)
    source = (SUNRAY_MODEL_ROOT / "sunray150_with_mid360.sdf").read_text(encoding="utf-8")

    patched, replacements = sync.patch_drone_model_text(source, profile, "nested", "nested")
    source_root = ET.fromstring(source)
    patched_root = ET.fromstring(patched)

    source_imu = source_root.find(".//plugin[@name='gazebo_imu_plugin']")
    patched_imu = patched_root.find(".//plugin[@name='gazebo_imu_plugin']")
    source_p3d = source_root.find(".//plugin[@name='p3d_base_controller']")
    patched_p3d = patched_root.find(".//plugin[@name='p3d_base_controller']")

    assert source_imu is not None and patched_imu is not None
    assert source_p3d is not None and patched_p3d is not None
    assert patched_imu.find("updateRate") is None
    assert patched_imu.find("pubRate") is None
    assert patched_p3d.findtext("updateRate") == source_p3d.findtext("updateRate")
    assert replacements["unsupported_flight_controller_imu_rate_tags_removed"] == 0


def test_all_sensor_mass_accounting_modes_close_to_one_kg() -> None:
    sync = load_sync_module()
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    mass = profile["mass_accounting"]
    ros1 = mass["ros1_gazebo_classic"]
    rotor_mass = int(mass["rotor_count"]) * float(mass["rotor_mass_kg_each"])

    expected_keys = {
        ("nested", "removed"): "nested_mid360",
        ("inline", "removed"): "inline_mid360",
        ("nested", "nested"): "nested_mid360_gps",
        ("inline", "inline"): "inline_mid360_gps",
    }
    for modes, expected_key in expected_keys.items():
        mid360_mode, gps_mode = modes
        assert sync.gps_mass_accounting_key(mid360_mode, gps_mode) == expected_key
        entry = ros1[expected_key]
        total = (
            float(entry["base_link_mass_kg"])
            + float(entry["flight_imu_mass_kg"])
            + rotor_mass
            + float(entry["camera_sensor_model_mass_kg_each"])
            * int(entry["camera_sensor_model_count"])
        )
        if mid360_mode == "nested":
            total += float(entry["mid360_nested_model_mass_kg"])
        if gps_mode == "nested":
            total += float(entry["gps_nested_model_mass_kg"])
        elif gps_mode == "inline":
            total += float(entry["gps_inline_model_mass_kg"])
        assert math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1.0e-12), expected_key


def test_project_local_gps_model_is_complete_and_traceable() -> None:
    gps_sdf = GPS_MODEL_ROOT / "gps.sdf"
    model_config = GPS_MODEL_ROOT / "model.config"
    notice = GPS_MODEL_ROOT / "NOTICE.md"

    assert gps_sdf.is_file()
    assert model_config.is_file()
    assert notice.is_file()

    sdf_root = ET.parse(gps_sdf).getroot()
    assert sdf_root.find("./model[@name='gps']/link[@name='link']") is not None
    plugin = sdf_root.find(".//plugin[@filename='libgazebo_gps_plugin.so']")
    assert plugin is not None

    config_root = ET.parse(model_config).getroot()
    assert config_root.findtext("sdf") == "gps.sdf"
    notice_text = notice.read_text(encoding="utf-8")
    assert "PX4-Autopilot/Tools/sitl_gazebo/models/gps" in notice_text
    assert "BSD 3-Clause License" in notice_text


def test_project_mavros_profile_exposes_home_position_without_broadening_control() -> None:
    text = MAVROS_PLUGINLIST_PATH.read_text(encoding="utf-8")
    sync = load_sync_module()
    home_position = sync.mavros_pluginlist_home_position_state(text)
    _, whitelist = text.split("plugin_whitelist:", 1)

    assert home_position == {"blacklisted": False, "whitelisted": True}
    assert "- setpoint_raw" in whitelist
    assert "- setpoint_attitude" in whitelist


def test_gpu_livox_promotes_ray_config_to_the_sensor(tmp_path: Path, monkeypatch) -> None:
    sync = load_sync_module()
    source = (
        ROOT
        / "src"
        / "simulation"
        / "gazebo"
        / "sunray"
        / "models"
        / "sensor_models"
        / "livox_mid360"
        / "livox_mid360.sdf"
    )
    target = tmp_path / "livox_mid360.sdf"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(sync, "SUNRAY_MID360_RAY_BACKEND", "gpu")
    monkeypatch.setattr(sync, "SUNRAY_LIVOX_PLUGIN_FILENAME", "/tmp/libmosim_gpu_livox_pointcloud.so")

    replacements = sync.delete_default_livox_sensor_shell(target)
    root = ET.parse(target).getroot()
    sensor = root.find(".//sensor[@name='laser_livox']")
    assert sensor is not None
    assert sensor.attrib["type"] == "gpu_ray"
    assert sensor.find("ray") is not None
    plugin = sensor.find("plugin[@name='mosim_gpu_livox_pointcloud']")
    assert plugin is not None
    assert plugin.find("ray") is None
    assert replacements["gpu_ray_config_promoted"] == 1
