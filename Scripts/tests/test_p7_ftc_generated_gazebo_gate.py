from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/sunray/p7_ftc_runtime_math.py"


def load_module():
    spec = importlib.util.spec_from_file_location("p7_coordinator", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_wrench_round_trip_basis():
    module = load_module()
    assert module.wrench_from_motors([0.25, 0.25, 0.25, 0.25]) == (1.0, 0.0, 0.0, 0.0)
    assert module.wrench_from_motors([0.0, 0.5, 0.5, 0.0]) == (1.0, 0.5, 0.0, 0.0)


def test_plugin_is_inert_by_default_and_bounded():
    source = (ROOT / "Scripts/sunray/gazebo_ftc_actuator_plugin/src/ftc_actuator_plugin.cpp").read_text()
    assert "effectiveness_{{1.0, 1.0, 1.0, 1.0}}" in source
    assert "override_enabled_{false}" in source
    assert "Clamp(msg->data[1 + rotor], 0.0, 1.0)" in source
    assert "ConnectWorldUpdateEnd" in source


def test_runtime_wrapper_uses_official_generated_c():
    text = (ROOT / "Scripts/sunray/run_p7_ftc_generated_gazebo_gate.sh").read_text()
    assert "MoSim_P7_FaultTolerantControl_CFunction_Sysblock.c" in text
    assert "momodel_extern_ince1.c" in text
    assert "PX4CTRL_SKIP_MISSION=true" in text


def test_coordinator_waits_for_px4ctrl_subscriber_and_takeoff_acceptance():
    text = (ROOT / "Scripts/sunray/run_p7_ftc_generated_coordinator.py").read_text()
    assert "self.command_pub.get_num_connections() > 0" in text
    assert "self.takeoff_land_pub.get_num_connections() > 0" in text
    assert "def request_takeoff(self)" in text
    assert "self.args.takeoff_timeout_s" in text
    assert "self.state.armed or self.extended.landed_state" in text
