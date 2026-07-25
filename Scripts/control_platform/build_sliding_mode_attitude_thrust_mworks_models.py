#!/usr/bin/env python3
"""Build the P3 sliding-mode ATTITUDE_THRUST CFunction bridge and MIL fixtures."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INPUTS = [
    "controller_id", "dt",
    "position_x", "position_y", "position_z",
    "velocity_x", "velocity_y", "velocity_z",
    "reference_position_x", "reference_position_y", "reference_position_z",
    "reference_velocity_x", "reference_velocity_y", "reference_velocity_z",
    "reference_acceleration_x", "reference_acceleration_y", "reference_acceleration_z",
    "reference_yaw", "mass_kg", "gravity_mps2", "hover_percentage",
    "max_tilt_rad", "min_collective_thrust_n", "max_collective_thrust_n",
    "enable", "reset",
]
OUTPUTS = [
    "desired_attitude_w", "desired_attitude_x", "desired_attitude_y", "desired_attitude_z",
    "normalized_thrust", "collective_thrust_n",
    "desired_acceleration_x", "desired_acceleration_y", "desired_acceleration_z",
    "sliding_surface_x", "sliding_surface_y", "sliding_surface_z",
    "auxiliary_state_x", "auxiliary_state_y", "auxiliary_state_z",
    "effective_reaching_gain_x", "effective_reaching_gain_y", "effective_reaching_gain_z",
    "saturated", "status_code",
]
VARIANTS = {
    1: "integral_smc",
    2: "terminal_smc",
    3: "nonsingular_terminal_smc",
    4: "super_twisting_smc",
    5: "adaptive_smc",
    6: "fuzzy_smc",
}
FEATURE_OUTPUT = {
    "integral_smc": "auxiliary_state_x",
    "terminal_smc": "sliding_surface_x",
    "nonsingular_terminal_smc": "sliding_surface_x",
    "super_twisting_smc": "auxiliary_state_x",
    "adaptive_smc": "effective_reaching_gain_x",
    "fuzzy_smc": "effective_reaching_gain_x",
}
BASE_INPUTS = {
    "dt": 0.01,
    "position_x": 0.2, "position_y": -0.1, "position_z": 0.7,
    "velocity_x": -0.3, "velocity_y": 0.2, "velocity_z": -0.1,
    "reference_position_x": 1.0, "reference_position_y": 0.5, "reference_position_z": 1.2,
    "reference_velocity_x": 0.1, "reference_velocity_y": -0.2, "reference_velocity_z": 0.0,
    "reference_acceleration_x": 0.05, "reference_acceleration_y": -0.04,
    "reference_acceleration_z": 0.02, "reference_yaw": 0.3,
    "mass_kg": 1.0, "gravity_mps2": 9.80665, "hover_percentage": 0.37,
    "max_tilt_rad": 0.5235987755982988,
    "min_collective_thrust_n": 0.0, "max_collective_thrust_n": 16.0,
    "enable": 1.0, "reset": 0.0,
}


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_p2_builder():
    return load_module(
        ROOT / "Scripts/control_platform/build_linear_robust_attitude_thrust_mworks_models.py",
        "p2_mworks_builder",
    )


def embedded_c() -> str:
    p2_builder = load_p2_builder()
    builder = p2_builder.load_generic_builder()
    core_dir = ROOT / "Scripts/control_platform"
    header = (core_dir / "sliding_mode_attitude_thrust_core.h").read_text(encoding="utf-8")
    source = (core_dir / "sliding_mode_attitude_thrust_core.c").read_text(encoding="utf-8")
    blob = builder.strip_c_for_modelica_include(header, source)
    blob = "\n".join(
        line for line in blob.splitlines()
        if line.strip() != '#include "sliding_mode_attitude_thrust_core.h"'
    )
    scalar_args = ",\n    ".join(f"double {name}" for name in INPUTS)
    output_args = ",\n    ".join(f"double *{name}" for name in OUTPUTS)
    wrapper = f'''
void MosimSlidingModeStepScalar(
    {scalar_args},
    {output_args})
{{
    static MosimSlidingModeState states[7];
    MosimSlidingModeParams params;
    MosimSlidingModeInput input;
    MosimSlidingModeOutput output;
    int id = (int)controller_id;
    int result;
    memset(&input, 0, sizeof(input));
    input.dt = dt;
    input.position[0] = position_x; input.position[1] = position_y; input.position[2] = position_z;
    input.velocity[0] = velocity_x; input.velocity[1] = velocity_y; input.velocity[2] = velocity_z;
    input.reference_position[0] = reference_position_x;
    input.reference_position[1] = reference_position_y;
    input.reference_position[2] = reference_position_z;
    input.reference_velocity[0] = reference_velocity_x;
    input.reference_velocity[1] = reference_velocity_y;
    input.reference_velocity[2] = reference_velocity_z;
    input.reference_acceleration[0] = reference_acceleration_x;
    input.reference_acceleration[1] = reference_acceleration_y;
    input.reference_acceleration[2] = reference_acceleration_z;
    input.reference_yaw = reference_yaw;
    input.enable = enable != 0.0;
    input.reset = reset != 0.0;
    mosim_sliding_mode_default_params(&params);
    params.mass_kg = mass_kg;
    params.gravity_mps2 = gravity_mps2;
    params.hover_percentage = hover_percentage;
    params.max_tilt_rad = max_tilt_rad;
    params.min_collective_thrust_n = min_collective_thrust_n;
    params.max_collective_thrust_n = max_collective_thrust_n;
    if (id < 1 || id > 6) id = 0;
    result = mosim_sliding_mode_step(id, &params, &states[id], &input, &output);
    if (result != 0) {{
        memset(&output, 0, sizeof(output));
        output.desired_attitude_wxyz[0] = 1.0;
        output.status_code = result;
    }}
    *desired_attitude_w = output.desired_attitude_wxyz[0];
    *desired_attitude_x = output.desired_attitude_wxyz[1];
    *desired_attitude_y = output.desired_attitude_wxyz[2];
    *desired_attitude_z = output.desired_attitude_wxyz[3];
    *normalized_thrust = output.normalized_thrust;
    *collective_thrust_n = output.collective_thrust_n;
    *desired_acceleration_x = output.desired_acceleration[0];
    *desired_acceleration_y = output.desired_acceleration[1];
    *desired_acceleration_z = output.desired_acceleration[2];
    *sliding_surface_x = output.sliding_surface[0];
    *sliding_surface_y = output.sliding_surface[1];
    *sliding_surface_z = output.sliding_surface[2];
    *auxiliary_state_x = output.auxiliary_state[0];
    *auxiliary_state_y = output.auxiliary_state[1];
    *auxiliary_state_z = output.auxiliary_state[2];
    *effective_reaching_gain_x = output.effective_reaching_gain[0];
    *effective_reaching_gain_y = output.effective_reaching_gain[1];
    *effective_reaching_gain_z = output.effective_reaching_gain[2];
    *saturated = (double)output.saturated;
    *status_code = (double)output.status_code;
}}
'''
    return "\n".join([blob.strip(), wrapper.strip()]) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", default="Results/control_platform/p3_sliding_mode_mworks_20260716")
    args = parser.parse_args()
    result_dir = (ROOT / args.result_dir).resolve()
    model_dir = result_dir / "models"
    codegen_dir = result_dir / "generated_c"
    model_dir.mkdir(parents=True, exist_ok=True)
    codegen_dir.mkdir(parents=True, exist_ok=True)

    p2_builder = load_p2_builder()
    p2_builder.INPUTS = INPUTS
    p2_builder.OUTPUTS = OUTPUTS
    p2_builder.BASE_INPUTS = BASE_INPUTS
    generic_builder = p2_builder.load_generic_builder()
    bridge_name = "MoSim_P3_SlidingMode_CFunction_Sysblock"
    bridge = generic_builder.build_model(bridge_name, codegen_dir, embedded_c(), real_as_float=False)
    bridge = bridge.replace("MosimPx4ctrlG9FamilyCStepScalar", "MosimSlidingModeStepScalar")
    bridge_path = model_dir / f"{bridge_name}.mo"
    bridge_path.write_text(bridge, encoding="utf-8", newline="\n")

    fixtures: dict[str, str] = {}
    for controller_id, algorithm_name in VARIANTS.items():
        fixture_name = f"MoSim_P3_{algorithm_name.upper()}_MIL"
        fixtures[algorithm_name] = fixture_name
        (model_dir / f"{fixture_name}.mo").write_text(
            p2_builder.fixture_model(fixture_name, controller_id, bridge_name),
            encoding="utf-8", newline="\n",
        )
    manifest = {
        "schema": "mosim.p3_sliding_mode_mworks_build.v1",
        "bridge_model": bridge_name,
        "bridge_path": str(bridge_path),
        "fixtures": fixtures,
        "feature_output": FEATURE_OUTPUT,
        "inputs": INPUTS,
        "outputs": OUTPUTS,
        "sample_time_s": 0.01,
        "stop_time_s": 0.2,
        "neural_smc": {"decision": "deferred", "selectable": False},
        "claim_boundary": "Fixed-size CFunction bridge and six MIL fixtures only. Live CheckModel/MIL, graphical equivalence, official codegen/SIL, and Gazebo runtime are separate gates.",
    }
    (result_dir / "BUILD_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
