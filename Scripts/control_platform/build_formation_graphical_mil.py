#!/usr/bin/env python3
"""Build readable P8 formation-family graphical MWORKS fixtures."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT_ROOT = ROOT / "Results/control_platform/p8_formation_mworks_20260717"
MODEL_DIR = RESULT_ROOT / "models/graphical_variants"

MODE_SPECS = {
    "leader_follower": ("leader_reference", "relative_offset", "follower_error", "tracking_correction", "separation_guard"),
    "virtual_structure": ("virtual_center", "rigid_body_offset", "structure_error", "structure_correction", "shape_guard"),
    "consensus": ("neighbor_average", "consensus_weight", "agreement_error", "consensus_correction", "separation_guard"),
    "containment": ("boundary_reference", "convex_weighting", "containment_error", "containment_correction", "boundary_guard"),
    "formation_tracking": ("trajectory_reference", "formation_offset", "tracking_error", "tracking_correction", "separation_guard"),
    "formation_reconfiguration": ("nominal_shape", "reconfiguration_selector", "transition_error", "shape_transition", "separation_guard"),
    "fault_tolerant_formation": ("health_mask", "active_member_projection", "degraded_error", "fault_aware_correction", "active_agent_guard"),
    "formation_cbf": ("pairwise_distance", "safety_margin", "barrier_residual", "cbf_correction", "safe_set_projection"),
    "distributed_mpc_formation": ("horizon_reference", "neighbor_prediction", "prediction_error", "distributed_optimization", "constraint_projection"),
}


def component(type_name: str, name: str, params: str, x: int, y: int) -> str:
    suffix = f"({params})" if params else ""
    return (
        f"  {type_name} {name}{suffix} annotation(Placement("
        f"transformation(origin={{{x},{y}}},extent={{{{-24,-18}},{{24,18}}}})));"
    )


def connect(source: str, target: str, points: str) -> str:
    return f"  connect({source},{target}) annotation(Line(points={{{points}}},color={{0,0,0}}));"


def summation(name: str, x: int, y: int) -> str:
    return (
        f'  SysplorerEmbeddedCoder.MathOperation.Sum {name}(inputs="+-") '
        f"annotation(Placement(transformation(origin={{{x},{y}}},"
        "extent={{-24,-18},{24,18}})),"
        "__MWORKS(BlockSystem(Instance(u(u1,u2)))));"
    )


def model_name(mode: str) -> str:
    return f"MoSim_P8_{mode.upper()}_GRAPHICAL_MIL"


def build_model(mode: str) -> str:
    source, transform, error, correction, guard = MODE_SPECS[mode]
    name = model_name(mode)
    blocks = [
        component("SysplorerEmbeddedCoder.Sources.Constant", source, "k=2.0", -500, 90),
        component("SysplorerEmbeddedCoder.MathOperation.Gain", transform, "k=0.75", -350, 90),
        component("SysplorerEmbeddedCoder.Sources.Constant", "measured_group_state", "k=0.35", -350, -80),
        summation(error, -190, 40),
        component("SysplorerEmbeddedCoder.MathOperation.Gain", correction, "k=0.6", -30, 40),
        component("SysplorerEmbeddedCoder.Discontinuities.Saturation", guard, "lowLimit=-1.5,upLimit=1.5", 140, 40),
        component("SysplorerEmbeddedCoder.MathOperation.Gain", "three_uav_reference_distribution", "k=3.0", 320, 40),
        component("SysplorerEmbeddedCoder.Port.Outport", "formation_command", "", 520, 90),
        component("SysplorerEmbeddedCoder.Port.Outport", "formation_error", "", 520, 10),
        component("SysplorerEmbeddedCoder.Port.Outport", "minimum_pair_distance", "", 520, -70),
    ]
    equations = [
        connect(f"{source}.y", f"{transform}.u", "{-476,90},{-374,90}"),
        connect(f"{transform}.y", f"{error}.u1", "{-326,90},{-260,90},{-260,48},{-214,48}"),
        connect("measured_group_state.y", f"{error}.u2", "{-326,-80},{-260,-80},{-260,32},{-214,32}"),
        connect(f"{error}.y", f"{correction}.u", "{-166,40},{-54,40}"),
        connect(f"{correction}.y", f"{guard}.u", "{-6,40},{116,40}"),
        connect(f"{guard}.y", "three_uav_reference_distribution.u", "{164,40},{296,40}"),
        connect("three_uav_reference_distribution.y", "formation_command", "{344,40},{430,40},{430,90},{496,90}"),
        connect(f"{error}.y", "formation_error", "{-166,40},{430,40},{430,10},{496,10}"),
        connect(f"{guard}.y", "minimum_pair_distance", "{164,40},{400,40},{400,-70},{496,-70}"),
    ]
    return f'''model {name} "P8 {mode.replace('_', ' ')} formation signal chain"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.02),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.02,IntegratorStep=0.02,StartTime=0,StopTime=0.4,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-570,-150}},{{570,150}}}},grid={{2,2}})));
{chr(10).join(blocks)}
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
{chr(10).join(equations)}
end {name};
'''


def main() -> int:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    models = {}
    for mode in MODE_SPECS:
        path = MODEL_DIR / f"{model_name(mode)}.mo"
        path.write_text(build_model(mode), encoding="utf-8", newline="\n")
        models[mode] = str(path.relative_to(ROOT)).replace("\\", "/")
    manifest = {
        "schema": "mosim.control_platform.p8_formation_graphical_structure.v1",
        "status": "generated_pending_live_check",
        "live_check": None,
        "models": models,
        "claim_boundary": (
            "Readable route-specific formation signal chains for report topology only. "
            "The existing nine-mode CFunction MWORKS MIL remains the numerical authority."
        ),
    }
    (RESULT_ROOT / "P8_GRAPHICAL_STRUCTURE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
