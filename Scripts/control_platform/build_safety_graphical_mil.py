#!/usr/bin/env python3
"""Build the readable P6 safety-family graphical MWORKS fixture."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT_ROOT = ROOT / "Results/control_platform/p6_safety_mworks_20260717"
MODEL_DIR = RESULT_ROOT / "models/graphical_variants"
MODEL = "MoSim_P6_SAFETY_SUPERVISOR_FAMILY_GRAPHICAL_MIL"


def constant(name: str, value: float, x: int, y: int) -> str:
    return (
        f"  SysplorerEmbeddedCoder.Sources.Constant {name}(k={value}) "
        f"annotation(Placement(transformation(origin={{{x},{y}}},"
        "extent={{-16,-12},{16,12}})));"
    )


def gain(name: str, value: float, x: int, y: int) -> str:
    return (
        f"  SysplorerEmbeddedCoder.MathOperation.Gain {name}(k={value}) "
        f"annotation(Placement(transformation(origin={{{x},{y}}},"
        "extent={{-18,-14},{18,14}})));"
    )


def summation(name: str, x: int, y: int) -> str:
    return (
        f'  SysplorerEmbeddedCoder.MathOperation.Sum {name}(inputs="++") '
        f"annotation(Placement(transformation(origin={{{x},{y}}},"
        "extent={{-18,-14},{18,14}})),"
        "__MWORKS(BlockSystem(Instance(u(u1,u2)))));"
    )


def saturation(name: str, low: float, high: float, x: int, y: int) -> str:
    return (
        f"  SysplorerEmbeddedCoder.Discontinuities.Saturation {name}("
        f"lowLimit={low},upLimit={high}) annotation(Placement("
        f"transformation(origin={{{x},{y}}},extent={{{{-18,-14}},{{18,14}}}})));"
    )


def outport(name: str, x: int, y: int) -> str:
    return (
        f"  SysplorerEmbeddedCoder.Port.Outport {name} annotation(Placement("
        f"transformation(origin={{{x},{y}}},extent={{{{-14,-12}},{{14,12}}}})));"
    )


def connect(source: str, target: str, points: str) -> str:
    return (
        f"  connect({source},{target}) annotation("
        f"Line(points={{{points}}},color={{0,0,0}}));"
    )


def build_model() -> str:
    blocks = [
        constant("candidate_acceleration_x", 8.0, -480, 150),
        constant("obstacle_margin", 0.4, -480, 70),
        constant("reference_position_x", 12.0, -480, -20),
        constant("command_age_s", 1.0, -480, -115),
        constant("emergency_request", 1.0, -480, -175),
        saturation("candidate_command_limit", -4.0, 4.0, -350, 150),
        gain("cbf_barrier_correction", -2.0, -350, 70),
        summation("constraint_command_merge", -210, 120),
        saturation("final_safety_filter", -3.0, 3.0, -70, 120),
        saturation("geofence_projection", -10.0, 10.0, -350, -20),
        gain("reference_governor", 0.8, -210, -20),
        gain("health_watchdog", 2.0, -350, -115),
        gain("emergency_stop_request", 5.0, -350, -175),
        summation("failsafe_action_arbiter", -210, -145),
        saturation("action_priority_limit", 0.0, 5.0, -70, -145),
        outport("safe_acceleration_x", 250, 120),
        outport("safe_reference_x", 250, -20),
        outport("action", 250, -145),
    ]
    equations = [
        connect("candidate_acceleration_x.y", "candidate_command_limit.u", "{-464,150},{-368,150}"),
        connect("obstacle_margin.y", "cbf_barrier_correction.u", "{-464,70},{-368,70}"),
        connect("candidate_command_limit.y", "constraint_command_merge.u1", "{-332,150},{-270,150},{-270,128},{-228,128}"),
        connect("cbf_barrier_correction.y", "constraint_command_merge.u2", "{-332,70},{-270,70},{-270,112},{-228,112}"),
        connect("constraint_command_merge.y", "final_safety_filter.u", "{-192,120},{-88,120}"),
        connect("final_safety_filter.y", "safe_acceleration_x", "{-52,120},{236,120}"),
        connect("reference_position_x.y", "geofence_projection.u", "{-464,-20},{-368,-20}"),
        connect("geofence_projection.y", "reference_governor.u", "{-332,-20},{-228,-20}"),
        connect("reference_governor.y", "safe_reference_x", "{-192,-20},{236,-20}"),
        connect("command_age_s.y", "health_watchdog.u", "{-464,-115},{-368,-115}"),
        connect("emergency_request.y", "emergency_stop_request.u", "{-464,-175},{-368,-175}"),
        connect("health_watchdog.y", "failsafe_action_arbiter.u1", "{-332,-115},{-270,-115},{-270,-137},{-228,-137}"),
        connect("emergency_stop_request.y", "failsafe_action_arbiter.u2", "{-332,-175},{-270,-175},{-270,-153},{-228,-153}"),
        connect("failsafe_action_arbiter.y", "action_priority_limit.u", "{-192,-145},{-88,-145}"),
        connect("action_priority_limit.y", "action", "{-52,-145},{236,-145}"),
    ]
    return f'''model {MODEL} "P6 safety family: constraint shaping, reference governance and failsafe arbitration"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-540,-230}},{{320,230}}}},grid={{2,2}})));
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
        "schema": "mosim.control_platform.p6_safety_graphical_structure.v1",
        "status": "generated_pending_live_check",
        "model": str(model_path.relative_to(ROOT)).replace("\\", "/"),
        "family_modes": [
            "safety_filter",
            "cbf",
            "reference_governor",
            "geofence",
            "emergency_stop",
            "return_and_land",
            "failsafe_state_machine",
        ],
        "claim_boundary": (
            "Readable native graphical family fixture for report topology only. "
            "The seven-mode CFunction MIL and generated runtime matrix remain the "
            "numerical and runtime authorities."
        ),
    }
    manifest_path = RESULT_ROOT / "P6_GRAPHICAL_STRUCTURE_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
