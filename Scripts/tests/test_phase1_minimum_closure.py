from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MWORKS_DIR = ROOT / "Scripts" / "mworks"
if str(MWORKS_DIR) not in sys.path:
    sys.path.insert(0, str(MWORKS_DIR))

import run_phase1_minimum_closure as phase1  # noqa: E402
import run_g6_formal_champion as champion  # noqa: E402


def test_phase1_matrix_has_exactly_46_unique_routes() -> None:
    matrix = phase1.build_matrix()
    rows = matrix["rows"]
    assert matrix["route_count"] == 46
    assert len(rows) == 46
    assert len({row["scheme_id"] for row in rows}) == 46


def test_phase1_preserves_missing_adapter_as_terminal_failure_not_fake_closure() -> None:
    matrix = phase1.build_matrix()
    rows = {row["scheme_id"]: row for row in matrix["rows"]}
    assert rows["adaptive_backstepping"]["execution_kind"] == "adapter_missing"
    assert "truthfully" in rows["adaptive_backstepping"]["adapter_missing_reason"]


def test_phase1_has_named_runner_and_fixed_integrated_targets() -> None:
    matrix = phase1.build_matrix()
    rows = {row["scheme_id"]: row for row in matrix["rows"]}
    assert rows["official_pid"]["target_boundary"] == "ROTOR_COMMAND"
    assert rows["cascade_pid"]["execution_kind"] == "adapter_backed_whole_aircraft"
    assert rows["fixed_awff_pid"]["execution_kind"] == "fixed_integrated_whole_aircraft"


def test_champion_adapters_use_qualified_bridge_types() -> None:
    adapters = {
        "CascadePidAttitudeThrustAdapter.mo": "PidAttitudeThrustCFunction",
        "LqrBaselineAttitudeThrustAdapter.mo": "LqrBaselineEquationBridge",
        "SuperTwistingSmcAttitudeThrustAdapter.mo": "SuperTwistingSmcCFunction",
        "LinearMpcAttitudeThrustAdapter.mo": "LinearMpcCFunction",
        "DfbcHighOrderAttitudeThrustAdapter.mo": "DfbcHighOrderEquationBridge",
        "TrainedNeuralResidualAttitudeThrustAdapter.mo": "TrainedNeuralResidualCFunction",
    }
    root = ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Adapters"
    for filename, bridge in adapters.items():
        source = (root / filename).read_text(encoding="utf-8")
        assert f"MoSimQuadrotorModel.Control.Bridges.{bridge} core" in source


def test_cascade_pid_bridges_the_mworks_roll_measurement_to_enu_flu() -> None:
    source = (
        ROOT
        / "Models"
        / "MoSimQuadrotorModel"
        / "Control"
        / "Adapters"
        / "CascadePidAttitudeThrustAdapter.mo"
    ).read_text(encoding="utf-8")

    assert "roll_mea = -attitude_mea[1];" in source
    assert "core.angular_velocity_x_in = -angular_rate_estimator[1].y;" in source
    assert "attitude_ref[1] = -roll_ref;" in source


def test_shared_allocator_maps_embedded_yaw_authority_to_the_physical_plant() -> None:
    source = (
        ROOT
        / "Models"
        / "MoSimQuadrotorModel"
        / "Control"
        / "Allocation"
        / "OfflineAttitudeRateAllocator.mo"
    ).read_text(encoding="utf-8")

    assert "embedded_yaw_authority_reference_ratio = 0.016" in source
    assert "embedded_yaw_authority_reference_ratio / profile.moment_constant_ratio_m" in source
    assert "command_scale * yaw_authority_scale * 0.707" in source


def test_lqr_adapter_bridges_enu_flu_roll_to_the_shared_mworks_plant() -> None:
    source = (
        ROOT
        / "Models"
        / "MoSimQuadrotorModel"
        / "Control"
        / "Adapters"
        / "LqrBaselineAttitudeThrustAdapter.mo"
    ).read_text(encoding="utf-8")

    assert "attitude_ref[1] = -core.desired_roll_rad_out;" in source
    assert "mass_kg * gravity_mps2 / hover_normalized_command" in source
    assert "* core.normalized_thrust_out - mass_kg * gravity_mps2;" in source


def test_other_recovered_champion_adapters_bridge_enu_flu_roll_to_mworks() -> None:
    filenames = (
        "SuperTwistingSmcAttitudeThrustAdapter.mo",
        "LinearMpcAttitudeThrustAdapter.mo",
        "DfbcHighOrderAttitudeThrustAdapter.mo",
        "TrainedNeuralResidualAttitudeThrustAdapter.mo",
    )
    root = ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Adapters"
    for filename in filenames:
        source = (root / filename).read_text(encoding="utf-8")
        assert "attitude_ref[1] = -roll_ref;" in source


def test_champion_recovery_accepts_phase1_provenance_and_records_terminal_error() -> None:
    phase1_matrix = ROOT / "Results" / "control_platform" / "phase1_minimum_closure" / "PHASE1_MATRIX.json"
    assert champion.checked_route_matrix(phase1_matrix) == phase1_matrix.resolve()

    series = {
        "x": [0.0],
        "y": [0.0],
        "z": [1.0],
        "x_ref": [0.0],
        "y_ref": [0.0],
        "z_ref": [3.0],
    }
    assert champion.add_derived_position_error(series) == 2.0
    assert series["position_error_norm"] == [2.0]
    assert champion.FORMAL_RESULT_INTERVAL_S == 0.01
    assert champion.FORMAL_SOLVER_PROFILE == {
        "algo": "Rkfix4",
        "integralStep": 0.002,
        "storeDouble": True,
        "storeEvent": False,
        "isPieceWiseStep": True,
        "pieceWiseStep": ((0.0, 0.002),),
    }
