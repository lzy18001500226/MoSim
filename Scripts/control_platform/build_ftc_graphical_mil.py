#!/usr/bin/env python3
"""Build the readable P7 FDI/FTC graphical MWORKS fixture."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT_ROOT = ROOT / "Results/control_platform/p7_ftc_mworks_20260717"
MODEL_DIR = RESULT_ROOT / "models/graphical_variants"
MODEL = "MoSim_P7_FDI_FTC_FAMILY_GRAPHICAL_MIL"


def component(type_name: str, name: str, params: str, x: int, y: int) -> str:
    suffix = f"({params})" if params else ""
    return (
        f"  {type_name} {name}{suffix} annotation(Placement("
        f"transformation(origin={{{x},{y}}},extent={{{{-18,-14}},{{18,14}}}})));"
    )


def constant(name: str, value: float, x: int, y: int) -> str:
    return component("SysplorerEmbeddedCoder.Sources.Constant", name, f"k={value}", x, y)


def gain(name: str, value: float, x: int, y: int) -> str:
    return component("SysplorerEmbeddedCoder.MathOperation.Gain", name, f"k={value}", x, y)


def summation(name: str, signs: str, x: int, y: int) -> str:
    return (
        f'  SysplorerEmbeddedCoder.MathOperation.Sum {name}(inputs="{signs}") '
        f"annotation(Placement(transformation(origin={{{x},{y}}},"
        "extent={{-18,-14},{18,14}})),"
        "__MWORKS(BlockSystem(Instance(u(u1,u2)))));"
    )


def saturation(name: str, low: float, high: float, x: int, y: int) -> str:
    return component(
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
        name,
        f"lowLimit={low},upLimit={high}",
        x,
        y,
    )


def delay(name: str, initial: float, x: int, y: int) -> str:
    return component(
        "SysplorerEmbeddedCoder.Discrete.UnitDelay", name, f"initCond={initial}", x, y
    )


def outport(name: str, x: int, y: int) -> str:
    return component("SysplorerEmbeddedCoder.Port.Outport", name, "", x, y)


def connect(source: str, target: str, points: str) -> str:
    return (
        f"  connect({source},{target}) annotation("
        f"Line(points={{{points}}},color={{0,0,0}}));"
    )


def build_model() -> str:
    blocks = [
        constant("desired_thrust", 2.4, -500, 120),
        constant("measured_motor_response_1", 0.3135, -500, 20),
        constant("healthy_effectiveness", 1.0, -500, -110),
        gain("nominal_control_allocation", 0.25, -390, 120),
        summation("motor_response_residual", "+-", -270, 70),
        gain("residual_to_effectiveness", -1.6666666667, -150, 70),
        summation("effectiveness_update", "++", -40, 20),
        saturation("bounded_effectiveness_estimate", 0.0, 1.0, 80, 20),
        delay("persistent_effectiveness_state", 1.0, 200, 20),
        summation("fault_score", "+-", 310, -55),
        gain("fault_isolation_gain", 2.0, 420, -55),
        saturation("isolated_fault_score", 0.0, 1.0, 530, -55),
        gain("fault_aware_reallocation", 0.4, 530, 70),
        summation("reconfigured_motor_command", "++", 650, 120),
        saturation("actuator_command_limit", 0.0, 1.0, 770, 120),
        gain("degraded_action_selection", 2.0, 650, -55),
        outport("motor_command_1", 900, 120),
        outport("eta_hat_1", 900, 20),
        outport("isolated_score", 900, -55),
        outport("action", 900, -125),
    ]
    equations = [
        connect("desired_thrust.y", "nominal_control_allocation.u", "{-482,120},{-408,120}"),
        connect("nominal_control_allocation.y", "motor_response_residual.u1", "{-372,120},{-320,120},{-320,78},{-288,78}"),
        connect("measured_motor_response_1.y", "motor_response_residual.u2", "{-482,20},{-320,20},{-320,62},{-288,62}"),
        connect("motor_response_residual.y", "residual_to_effectiveness.u", "{-252,70},{-168,70}"),
        connect("healthy_effectiveness.y", "effectiveness_update.u1", "{-482,-110},{-90,-110},{-90,28},{-58,28}"),
        connect("residual_to_effectiveness.y", "effectiveness_update.u2", "{-132,70},{-90,70},{-90,12},{-58,12}"),
        connect("effectiveness_update.y", "bounded_effectiveness_estimate.u", "{-22,20},{62,20}"),
        connect("bounded_effectiveness_estimate.y", "persistent_effectiveness_state.u1", "{98,20},{182,20}"),
        connect("healthy_effectiveness.y", "fault_score.u1", "{-482,-110},{260,-110},{260,-47},{292,-47}"),
        connect("persistent_effectiveness_state.y", "fault_score.u2", "{218,20},{260,20},{260,-63},{292,-63}"),
        connect("fault_score.y", "fault_isolation_gain.u", "{328,-55},{402,-55}"),
        connect("fault_isolation_gain.y", "isolated_fault_score.u", "{438,-55},{512,-55}"),
        connect("isolated_fault_score.y", "fault_aware_reallocation.u", "{548,-55},{570,-55},{570,70},{548,70}"),
        connect("nominal_control_allocation.y", "reconfigured_motor_command.u1", "{-372,120},{600,120},{600,128},{632,128}"),
        connect("fault_aware_reallocation.y", "reconfigured_motor_command.u2", "{548,70},{600,70},{600,112},{632,112}"),
        connect("reconfigured_motor_command.y", "actuator_command_limit.u", "{668,120},{752,120}"),
        connect("actuator_command_limit.y", "motor_command_1", "{788,120},{882,120}"),
        connect("persistent_effectiveness_state.y", "eta_hat_1", "{218,20},{882,20}"),
        connect("isolated_fault_score.y", "isolated_score", "{548,-55},{882,-55}"),
        connect("isolated_fault_score.y", "degraded_action_selection.u", "{548,-55},{600,-55},{632,-55}"),
        connect("degraded_action_selection.y", "action", "{668,-55},{710,-55},{710,-125},{882,-125}"),
    ]
    return f'''model {MODEL} "P7 FDI/FTC family: residual, estimation, isolation and reconfiguration"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.25,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-560,-190}},{{940,190}}}},grid={{2,2}})));
{chr(10).join(blocks)}
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
{chr(10).join(equations)}
end {MODEL};
'''


def main() -> int:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / f"{MODEL}.mo"
    model_path.write_text(build_model(), encoding="utf-8", newline="\n")
    manifest = {
        "schema": "mosim.control_platform.p7_ftc_graphical_structure.v1",
        "status": "generated_pending_live_check",
        "live_check": None,
        "model": str(model_path.relative_to(ROOT)).replace("\\", "/"),
        "family_modes": [
            "fdi",
            "passive_ftc",
            "active_ftc",
            "fault_aware_control_allocation",
            "single_motor_safe_landing",
            "multi_fault_estimation_reconfiguration",
        ],
        "claim_boundary": (
            "Readable native graphical FDI/FTC signal chain for report topology only. "
            "Six-mode CFunction MIL, generated-C SIL and physical Gazebo injection "
            "remain separate numerical and runtime authorities."
        ),
    }
    manifest_path = RESULT_ROOT / "P7_GRAPHICAL_STRUCTURE_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
