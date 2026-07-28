#!/usr/bin/env python3
"""Build hash-bound whole-aircraft bindings for the five non-PID champions.

The binding is deliberately separate from the frozen 46-route G6 matrix.  It
names the promoted controller core, its explicit adapter, the sampled
whole-aircraft runner, the common inner allocator, and the common plant so a
future MWORKS run cannot silently switch implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = ROOT / "Config" / "control_platform" / "g6_champion_bindings"
MODEL_ROOT = "Models/MoSimQuadrotorModel"
RESULT_ROOT = "Results/control_platform/g6_formal_champion_promotion_20260725"

# Every promoted whole-aircraft closure must bind the actual plant and reference
# sources, not only the thin runner that instantiates them.
SHARED_CLOSURE_SOURCES: tuple[tuple[str, str], ...] = (
    ("shared_sunray150_assembly", f"{MODEL_ROOT}/Vehicle/Sunray150Assembly.mo"),
    ("physical_wrench_adapter", f"{MODEL_ROOT}/Vehicle/Dynamics/PhysicalWrenchAdapter.mo"),
    ("wrapper_surface", f"{MODEL_ROOT}/Vehicle/Dynamics/WrapperSurface.mo"),
    ("rotor_actuator_core", f"{MODEL_ROOT}/Vehicle/Dynamics/RotorActuatorCore.mo"),
    ("plant_sensor_surface", f"{MODEL_ROOT}/Vehicle/Sensors/package.mo"),
    ("virtual_px4_classic_profile", f"{MODEL_ROOT}/Parameters/Sunray150VirtualPx4Classic.mo"),
    ("climb_path_reference", f"{MODEL_ROOT}/Guidance/Trajectories/package.mo"),
)


SPECS: tuple[dict[str, Any], ...] = (
    {
        "controller_id": "lqr_baseline",
        "controller_category": "classic_robust",
        "runner": "Experiment/Runners/Formal/LqrBaselineFormalRunner.mo",
        "runner_class": "MoSimQuadrotorModel.Experiment.Runners.Formal.LqrBaselineFormalRunner",
        "adapter": "Control/Adapters/LqrBaselineAttitudeThrustAdapter.mo",
        "adapter_class": "MoSimQuadrotorModel.Control.Adapters.LqrBaselineAttitudeThrustAdapter",
        "core_role": "graphical_controller_core",
        "core": "Control/Implementations/ClassicRobust/MoSim_G5_LQR_DIRECT_GRAPHICAL_MIL.mo",
        "bridge_role": "equation_bridge",
        "bridge": "Control/Bridges/LqrBaselineEquationBridge.mo",
        "adapter_implementation": {
            "kind": "equation_bridge",
            "bridge_class": "MoSimQuadrotorModel.Control.Bridges.LqrBaselineEquationBridge",
            "graphical_core_role": "graphical_controller_core",
            "reason": (
                "The readable direct graphical LQR core passes as a top-level G5 model, but MWORKS "
                "does not materialize its Sysblock Sum child ports when it is nested in the whole-aircraft "
                "adapter. The bridge retains the same scalar equations, gains, saturations, enable gate, "
                "and full input/output boundary while the named graphical core remains the topology evidence."
            ),
        },
        "layout_target": "MoSim_G5_LQR_DIRECT_GRAPHICAL_MIL remains the G5 readable controller topology evidence.",
    },
    {
        "controller_id": "super_twisting_smc",
        "controller_category": "sliding_mode",
        "runner": "Experiment/Runners/Formal/SuperTwistingSmcFormalRunner.mo",
        "runner_class": "MoSimQuadrotorModel.Experiment.Runners.Formal.SuperTwistingSmcFormalRunner",
        "adapter": "Control/Adapters/SuperTwistingSmcAttitudeThrustAdapter.mo",
        "adapter_class": "MoSimQuadrotorModel.Control.Adapters.SuperTwistingSmcAttitudeThrustAdapter",
        "core_role": "current_root_cfunction_core",
        "core": "Control/Bridges/SuperTwistingSmcCFunction.mo",
        "source_import": f"{RESULT_ROOT}/super_twisting_smc/adapter_source_import.json",
        "layout_target": "The selected Super-Twisting graphical route remains the G5 topology evidence; this runner is a sampled whole-aircraft wrapper.",
    },
    {
        "controller_id": "linear_mpc",
        "controller_category": "optimization",
        "runner": "Experiment/Runners/Formal/LinearMpcFormalRunner.mo",
        "runner_class": "MoSimQuadrotorModel.Experiment.Runners.Formal.LinearMpcFormalRunner",
        "adapter": "Control/Adapters/LinearMpcAttitudeThrustAdapter.mo",
        "adapter_class": "MoSimQuadrotorModel.Control.Adapters.LinearMpcAttitudeThrustAdapter",
        "core_role": "current_root_cfunction_core",
        "core": "Control/Bridges/LinearMpcCFunction.mo",
        "source_import": f"{RESULT_ROOT}/linear_mpc/adapter_source_import.json",
        "layout_target": "The selected Linear MPC graphical route remains the G5 topology evidence; this runner is a sampled whole-aircraft wrapper.",
    },
    {
        "controller_id": "dfbc_high_order_attitude",
        "controller_category": "geometric_flatness",
        "runner": "Experiment/Runners/Formal/DfbcHighOrderFormalRunner.mo",
        "runner_class": "MoSimQuadrotorModel.Experiment.Runners.Formal.DfbcHighOrderFormalRunner",
        "adapter": "Control/Adapters/DfbcHighOrderAttitudeThrustAdapter.mo",
        "adapter_class": "MoSimQuadrotorModel.Control.Adapters.DfbcHighOrderAttitudeThrustAdapter",
        "core_role": "graphical_controller_core",
        "core": "Control/Implementations/GeometricFlatness/MoSim_G5_DFBC_HIGH_ORDER_ATTITUDE_DIRECT_GRAPHICAL_MIL.mo",
        "bridge_role": "equation_bridge",
        "bridge": "Control/Bridges/DfbcHighOrderEquationBridge.mo",
        "adapter_implementation": {
            "kind": "equation_bridge",
            "bridge_class": "MoSimQuadrotorModel.Control.Bridges.DfbcHighOrderEquationBridge",
            "graphical_core_role": "graphical_controller_core",
            "reason": (
                "The readable direct graphical high-order DFBC core passes as a top-level G5 model, but "
                "MWORKS does not materialize its Sysblock Sum child ports when it is nested in the whole-aircraft "
                "adapter. The bridge retains the same scalar equations, 100 Hz surface memory, gains, saturations, "
                "enable gate, and full input/output boundary while the named graphical core remains the topology evidence."
            ),
        },
        "layout_target": "MoSim_G5_DFBC_HIGH_ORDER_ATTITUDE_DIRECT_GRAPHICAL_MIL remains the G5 readable controller topology evidence.",
    },
    {
        "controller_id": "trained_neural_residual",
        "controller_category": "learning",
        "runner": "Experiment/Runners/Formal/TrainedNeuralResidualFormalRunner.mo",
        "runner_class": "MoSimQuadrotorModel.Experiment.Runners.Formal.TrainedNeuralResidualFormalRunner",
        "adapter": "Control/Adapters/TrainedNeuralResidualAttitudeThrustAdapter.mo",
        "adapter_class": "MoSimQuadrotorModel.Control.Adapters.TrainedNeuralResidualAttitudeThrustAdapter",
        "core_role": "current_root_cfunction_core",
        "core": "Control/Bridges/TrainedNeuralResidualCFunction.mo",
        "source_import": f"{RESULT_ROOT}/trained_neural_residual/adapter_source_import.json",
        "layout_target": "The selected trained-neural-residual graphical route remains the G5 topology evidence; this runner is a sampled whole-aircraft wrapper.",
    },
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project_file(relative_path: str) -> Path:
    path = (ROOT / relative_path).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"binding path leaves project root: {relative_path}") from exc
    if not path.is_file():
        raise FileNotFoundError(f"binding input is missing: {relative_path}")
    return path


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def source(role: str, relative_path: str) -> dict[str, str]:
    path = project_file(relative_path)
    return {"role": role, "path": relative(path), "expected_sha256": sha256(path)}


def binding(spec: dict[str, Any]) -> dict[str, Any]:
    runner_path = f"{MODEL_ROOT}/{spec['runner']}"
    adapter_path = f"{MODEL_ROOT}/{spec['adapter']}"
    core_path = f"{MODEL_ROOT}/{spec['core']}"
    sources = [
        source("formal_runner", runner_path),
        source("formal_adapter", adapter_path),
        source(str(spec["core_role"]), core_path),
        source("shared_attitude_rate_allocator", f"{MODEL_ROOT}/Control/Allocation/OfflineAttitudeRateAllocator.mo"),
        *(source(role, path) for role, path in SHARED_CLOSURE_SOURCES),
    ]
    bridge = spec.get("bridge")
    bridge_role = spec.get("bridge_role")
    if isinstance(bridge, str) and isinstance(bridge_role, str):
        sources.append(source(bridge_role, f"{MODEL_ROOT}/{bridge}"))
    source_import = spec.get("source_import")
    if isinstance(source_import, str):
        sources.append(source("adapter_source_import_manifest", source_import))
    return {
        "schema": "mosim.g6_formal_champion_binding.v1",
        "controller_id": spec["controller_id"],
        "controller_category": spec["controller_category"],
        "scenario": {
            "scenario_id": "climb_path_50s",
            "reference_owner": "MoSimQuadrotorModel.Guidance.Trajectories.ClimbPath",
            "duration_s": 50,
        },
        "target": {
            "model_file": runner_path,
            "model_class": spec["runner_class"],
            "model_sha256": sha256(project_file(runner_path)),
        },
        "formal_adapter": {
            "model_file": adapter_path,
            "model_class": spec["adapter_class"],
            "model_sha256": sha256(project_file(adapter_path)),
            "output_boundary": "ATTITUDE_THRUST",
            "implementation": spec.get("adapter_implementation", {"kind": "direct_model_reference"}),
        },
        "formal_harness_feedback_boundary": {
            "kind": "sampled_controller_inputs",
            "sample_period_s": 0.01,
            "initial_measurement": "zero",
            "signals": [
                "reference.position_command -> controller.position_ref",
                "reference.velocity_command -> controller.velocity_ref",
                "reference.acceleration_command -> controller.acceleration_ref",
                "plant.position -> controller.position_mea",
                "plant.attitude -> controller.attitude_mea",
            ],
            "continuous_inner_loop_signals": [
                "plant.attitude -> offline_inner_allocator.attitude_mea",
            ],
            "reason": (
                "The promoted formal runner samples position, velocity, and acceleration references plus the "
                "plant measurements consumed by its controller adapter at 100 Hz. The shared inner attitude-rate "
                "allocator remains directly connected to plant attitude so its stabilizing feedback is continuous."
            ),
        },
        "source_bindings": sources,
        "model_layout_boundary": {
            "state": "formal_runner_sampled_feedback_harness_not_controller_graphical_topology",
            "reason": (
                f"{spec['layout_target']} The named runner proves only its sampled whole-aircraft closure entry."
            ),
        },
        "claim_boundary": (
            f"Real offline MWORKS formal whole-aircraft minimum closure for the selected {spec['controller_id']} candidate. "
            "It is not PX4, Gazebo, ROS, or flight-runtime evidence."
        ),
    }


def selected_specs(identifiers: list[str] | None) -> list[dict[str, Any]]:
    if not identifiers:
        return list(SPECS)
    by_id = {str(spec["controller_id"]): spec for spec in SPECS}
    return [by_id[identifier] for identifier in identifiers]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", choices=[str(spec["controller_id"]) for spec in SPECS])
    parser.add_argument("--check", action="store_true", help="verify bindings without writing")
    args = parser.parse_args()
    errors: list[str] = []
    outputs: list[str] = []
    for spec in selected_specs(args.only):
        path = OUTPUT_ROOT / f"{spec['controller_id']}.json"
        expected = binding(spec)
        outputs.append(relative(path))
        if args.check:
            if not path.is_file():
                errors.append(f"{spec['controller_id']}: binding is missing")
                continue
            try:
                actual = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{spec['controller_id']}: binding JSON is invalid: {exc}")
                continue
            if actual != expected:
                errors.append(f"{spec['controller_id']}: binding differs from deterministic content")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"ok": not errors, "bindings": outputs, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
