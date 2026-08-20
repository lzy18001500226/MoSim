import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "mworks_live" / "analyze_rt1_graphical_equivalence.py"
SPEC = importlib.util.spec_from_file_location("rt1_graphical_equivalence", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def valid_fixture() -> dict[str, object]:
    values = [
        0.02,
        -0.03,
        1.01,
        0.05,
        -0.04,
        0.01,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.12,
        -0.08,
        1.04,
        0.02,
        0.01,
        -0.02,
        0.03,
        -0.02,
        0.01,
        0.0,
        0.0,
    ]
    expected = MODULE.expected_command(values)
    return {
        "execution_source": "local_udp_fixture_to_mworks_realtime_simulation",
        "fixture_profile": "rt2_outer_loop_excitation",
        "run_id": "rt2-test",
        "passed": True,
        "minimum_responses": 1,
        "sent_frames": [{"sequence": 7, "values": values}],
        "responses": [
            {
                "state_sequence": 7,
                "q_xyzw": expected["q_xyzw"],
                "collective_thrust_n": expected["collective_thrust_n"],
                "output_valid": True,
                "controller_status": 1,
            }
        ],
    }


def test_rt2_identity_attitude_outer_loop_equivalence_passes() -> None:
    result = MODULE.analyze(valid_fixture())

    assert result["passed"] is True
    assert result["comparison_count"] == 1
    assert result["max_quaternion_component_error"] == 0.0
    assert result["max_collective_thrust_error_n"] == 0.0


def test_rt2_equivalence_rejects_graphical_command_mismatch() -> None:
    fixture = valid_fixture()
    response = fixture["responses"][0]
    response["collective_thrust_n"] += 0.01

    result = MODULE.analyze(fixture)

    assert result["passed"] is False
    assert any(item["reason_code"] == "graphical_outer_loop_mismatch" for item in result["failures"])


def test_rt2_equivalence_rejects_short_quaternion() -> None:
    fixture = valid_fixture()
    response = fixture["responses"][0]
    response["q_xyzw"] = response["q_xyzw"][:3]

    result = MODULE.analyze(fixture)

    assert result["passed"] is False
    assert any(item["reason_code"] == "invalid_response_quaternion" for item in result["failures"])
