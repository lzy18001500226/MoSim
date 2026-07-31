#!/usr/bin/env python3
"""Static contract for the isolated three-UAV PX4CTRL ECBF reference-safety route."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLANNING = ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning"
BASELINE = PLANNING / "ThreeUavOpenBlocksReconfigurableFormationPx4Ctrl.mo"
SAFETY_MODEL = PLANNING / "ThreeUavOpenBlocksReconfigurableFormationPx4CtrlEcbfSafety.mo"
SAFETY_FILTER = PLANNING / "ThreeUavPairwiseEcbfReferenceSafetyFilter.mo"
SAFETY_SMOOTHER = PLANNING / "ThreeUavPairwiseEcbfReferenceSmoother.mo"
PACKAGE = PLANNING / "package.mo"
ORDER = PLANNING / "package.order"
RUNNER = ROOT / "Scripts" / "mworks" / "run_three_uav_openblocks_px4ctrl_ecbf_safety_completion.py"
MCP_RUNNER = ROOT / "Scripts" / "mworks" / "run_three_uav_openblocks_px4ctrl_ecbf_safety_mcp.py"


def assert_connection(source: str, left: str, right: str) -> None:
    needle = f"connect({left}, {right})"
    if needle not in source:
        raise AssertionError(f"Missing connection: {needle}")


def component_body(source: str, component_name: str) -> str:
    match = re.search(rf"(?s)\b{re.escape(component_name)}\s*\((.*?)\)\s*annotation", source)
    if not match:
        raise AssertionError(f"Missing component declaration: {component_name}")
    return match.group(1)


def literal_vector(body: str, field_name: str) -> list[str]:
    match = re.search(rf"\b{re.escape(field_name)}\s*=\s*\{{", body)
    if not match:
        raise AssertionError(f"Missing vector binding: {field_name}")
    start = match.end()
    depth = 1
    cursor = start
    while cursor < len(body) and depth:
        if body[cursor] == "{":
            depth += 1
        elif body[cursor] == "}":
            depth -= 1
        cursor += 1
    if depth:
        raise AssertionError(f"Unclosed vector binding: {field_name}")
    return re.findall(r"(?<![A-Za-z_])[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?", body[start : cursor - 1])


def main() -> int:
    baseline = BASELINE.read_text(encoding="utf-8")
    safety_model = SAFETY_MODEL.read_text(encoding="utf-8")
    safety_filter = SAFETY_FILTER.read_text(encoding="utf-8")
    safety_smoother = SAFETY_SMOOTHER.read_text(encoding="utf-8")
    package = PACKAGE.read_text(encoding="utf-8")
    order = ORDER.read_text(encoding="utf-8").splitlines()
    runner = RUNNER.read_text(encoding="utf-8")
    mcp_runner = MCP_RUNNER.read_text(encoding="utf-8")

    assert "model ThreeUavOpenBlocksReconfigurableFormationPx4Ctrl" in baseline
    assert "safetyFilter" not in baseline
    for index in (1, 2, 3):
        assert_connection(baseline, f"reference{index}.position_command", f"vehicle{index}.position_reference")
        assert_connection(baseline, f"reference{index}.velocity_command", f"vehicle{index}.velocity_reference")
        assert_connection(baseline, f"reference{index}.acceleration_command", f"vehicle{index}.acceleration_reference")

    assert "model ThreeUavOpenBlocksReconfigurableFormationPx4CtrlEcbfSafety" in safety_model
    assert safety_model.count("PlannedQuinticPx4CtrlReference reference") == 3
    assert safety_model.count("OpenBlocksPx4CtrlVehicle vehicle") == 3
    assert "OpenBlocksMapTruthDisplay navigationDisplay" in safety_model
    assert "ThreeUavPairwiseEcbfReferenceSafetyFilter safetyFilter" in safety_model
    assert "ThreeUavPairwiseEcbfReferenceSmoother safetySmoother" in safety_model
    filter_parameters = component_body(safety_model, "safetyFilter")
    assert "pair_minimum_distance_m = 1.0" in filter_parameters
    assert "pair_activation_distance_m = 1.5" in filter_parameters
    assert "max_reference_offset_m = 0.5" in filter_parameters

    for index in (1, 2, 3):
        assert_connection(safety_model, f"reference{index}.position_command", f"safetyFilter.nominal_position_{index}")
        assert_connection(safety_model, f"reference{index}.velocity_command", f"safetyFilter.nominal_velocity_{index}")
        assert_connection(safety_model, f"reference{index}.acceleration_command", f"safetyFilter.nominal_acceleration_{index}")
        assert_connection(safety_model, f"vehicle{index}.position", f"safetyFilter.actual_position_{index}")
        assert_connection(safety_model, f"velocityEstimator{index}.y", f"safetyFilter.actual_velocity_{index}")
        assert_connection(safety_model, f"reference{index}.position_command", f"safetySmoother.nominal_position_{index}")
        assert_connection(safety_model, f"reference{index}.velocity_command", f"safetySmoother.nominal_velocity_{index}")
        assert_connection(safety_model, f"reference{index}.acceleration_command", f"safetySmoother.nominal_acceleration_{index}")
        assert_connection(safety_model, f"safetyFilter.safe_position_{index}", f"safetySmoother.raw_safe_position_{index}")
        assert_connection(safety_model, f"safetyFilter.safe_velocity_{index}", f"safetySmoother.raw_safe_velocity_{index}")
        assert_connection(safety_model, f"safetyFilter.safe_acceleration_{index}", f"safetySmoother.raw_safe_acceleration_{index}")
        assert_connection(safety_model, f"safetySmoother.safe_position_{index}", f"vehicle{index}.position_reference")
        assert_connection(safety_model, f"safetySmoother.safe_velocity_{index}", f"vehicle{index}.velocity_reference")
        assert_connection(safety_model, f"safetySmoother.safe_acceleration_{index}", f"vehicle{index}.acceleration_reference")

        baseline_reference = component_body(baseline, f"reference{index}")
        safety_reference = component_body(safety_model, f"reference{index}")
        for field, expected_length in (("p_x", 91), ("p_y", 91), ("p_z", 91), ("segment_duration", 90)):
            assert len(literal_vector(baseline_reference, field)) == expected_length, (index, field)
            assert literal_vector(baseline_reference, field) == literal_vector(safety_reference, field), (index, field)

    assert_connection(safety_model, "safetySmoother.safe_position_1", "navigationDisplay.reference_position")
    for channel in (
        "nominal_formation_deviation_m",
        "safety_minimum_predicted_pair_distance_m",
        "safety_active_pair_count",
        "safety_maximum_reference_offset_m",
        "safety_requested_reference_offset_m",
        "safety_maximum_ecbf_residual_m2_s2",
        "safety_correction_saturated",
    ):
        assert channel in safety_model, channel

    for required in (
        "function projectPairwiseReference",
        "pair_minimum_distance_m",
        "pair_activation_distance_m",
        "requiredRadialAcceleration := -relativeVelocitySquared",
        "accelerationCorrection[first, axis]",
        "positionCorrection[first, axis]",
        "max_reference_offset_m",
        "max_safety_acceleration_correction_m_s2",
        "projection_passes",
        "minimum_actual_pair_distance_m",
        "minimum_predicted_pair_distance_m",
        "correction_saturated",
    ):
        assert required in safety_filter, required
    assert "wall" not in safety_filter.lower()
    assert "ModelingPy.ConnectSysplorer(port=port)" in runner
    assert 'ConnectSysplorer("127.0.0.1", port)' not in runner
    for required in (
        "SYSPLORER_API_PORT",
        "require_explicit_existing_port",
        "already_running",
        "dedicated_sysplorer_port",
        '"check_model"',
        "simulate_modelingpy",
        "read_result_series",
        '"Control" / "Adapters" / "Px4CtrlAttitudeThrustAdapter.mo"',
        'f"uav{_index}_pitch_argument"',
    ):
        assert required in mcp_runner, required
    assert "StartSysplorer" not in mcp_runner

    for entry in (
        "ThreeUavPairwiseEcbfReferenceSafetyFilter",
        "ThreeUavPairwiseEcbfReferenceSmoother",
        "ThreeUavOpenBlocksReconfigurableFormationPx4CtrlEcbfSafety",
    ):
        assert order.count(entry) == 1, entry
    assert "model OpenBlocksThreeUavPx4CtrlFormationEcbfSafety" in package
    assert (
        "extends MoSimQuadrotorModel.Guidance.Planning."
        "ThreeUavOpenBlocksReconfigurableFormationPx4CtrlEcbfSafety;"
    ) in package

    for required in (
        "block ThreeUavPairwiseEcbfReferenceSmoother",
        "position_time_constant_s",
        "velocity_time_constant_s",
        "acceleration_time_constant_s",
        "der(positionCorrection[vehicle, axis])",
        "der(velocityCorrection[vehicle, axis])",
        "der(accelerationCorrection[vehicle, axis])",
        "maximum_applied_reference_offset_m",
    ):
        assert required in safety_smoother, required

    print("[OK] Three-UAV OpenBlocks PX4CTRL ECBF reference-safety source contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
