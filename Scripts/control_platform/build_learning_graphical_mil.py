#!/usr/bin/env python3
"""Build readable P9 learning-control graphical MWORKS fixtures."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT_ROOT = ROOT / "Results/control_platform/p9_learning_mworks_20260717"
MODEL_DIR = RESULT_ROOT / "models/graphical_variants"

ROUTES = {
    "trained_neural_residual": {
        "model": "MoSim_P9_TRAINED_NEURAL_RESIDUAL_GRAPHICAL_MIL",
        "blocks": (
            "feature_normalization",
            "hidden_layer_inference",
            "bounded_neural_residual",
            "nominal_acceleration_merge",
            "attitude_thrust_projection",
        ),
        "gains": (0.8, 0.45, 0.18, 1.0, 0.34),
    },
    "rl_gain_scheduler": {
        "model": "MoSim_P9_RL_GAIN_SCHEDULER_GRAPHICAL_MIL",
        "blocks": (
            "state_feature_vector",
            "frozen_policy_inference",
            "bounded_gain_schedule",
            "nominal_gain_modulation",
            "attitude_thrust_projection",
        ),
        "gains": (0.75, 0.35, 0.20, 1.0, 0.34),
    },
}


def component(type_name: str, name: str, params: str, x: int, y: int) -> str:
    suffix = f"({params})" if params else ""
    return (
        f"  {type_name} {name}{suffix} annotation(Placement("
        f"transformation(origin={{{x},{y}}},extent={{{{-26,-18}},{{26,18}}}})));"
    )


def connect(source: str, target: str, points: str) -> str:
    return f"  connect({source},{target}) annotation(Line(points={{{points}}},color={{0,0,0}}));"


def summation(name: str, x: int, y: int) -> str:
    return (
        f'  SysplorerEmbeddedCoder.MathOperation.Sum {name}(inputs="++") '
        f"annotation(Placement(transformation(origin={{{x},{y}}},"
        "extent={{-26,-18},{26,18}})),"
        "__MWORKS(BlockSystem(Instance(u(u1,u2)))));"
    )


def build_model(route: str, spec: dict[str, object]) -> str:
    model = str(spec["model"])
    feature, inference, bounded, merge, projection = spec["blocks"]
    gains = spec["gains"]
    blocks = [
        component("SysplorerEmbeddedCoder.Sources.Constant", "measured_state", "k=0.55", -520, 90),
        component("SysplorerEmbeddedCoder.MathOperation.Gain", feature, f"k={gains[0]}", -370, 90),
        component("SysplorerEmbeddedCoder.MathOperation.Gain", inference, f"k={gains[1]}", -210, 90),
        component("SysplorerEmbeddedCoder.Discontinuities.Saturation", bounded, "lowLimit=-0.25,upLimit=0.25", -40, 90),
        component("SysplorerEmbeddedCoder.Sources.Constant", "nominal_acceleration", "k=9.80665", -210, -70),
        summation(merge, 140, 40),
        component("SysplorerEmbeddedCoder.MathOperation.Gain", projection, f"k={gains[4]}", 320, 40),
        component("SysplorerEmbeddedCoder.Discontinuities.Saturation", "command_guard", "lowLimit=0.0,upLimit=1.0", 470, 40),
        component("SysplorerEmbeddedCoder.Port.Outport", "normalized_thrust", "", 620, 90),
        component("SysplorerEmbeddedCoder.Port.Outport", "learning_action", "", 620, 10),
        component("SysplorerEmbeddedCoder.Port.Outport", "fallback_active", "", 620, -70),
        component("SysplorerEmbeddedCoder.Sources.Constant", "fallback_flag", "k=0.0", 470, -70),
    ]
    equations = [
        connect("measured_state.y", f"{feature}.u", "{-494,90},{-396,90}"),
        connect(f"{feature}.y", f"{inference}.u", "{-344,90},{-236,90}"),
        connect(f"{inference}.y", f"{bounded}.u", "{-184,90},{-66,90}"),
        connect(f"{bounded}.y", f"{merge}.u1", "{-14,90},{60,90},{60,48},{114,48}"),
        connect("nominal_acceleration.y", f"{merge}.u2", "{-184,-70},{60,-70},{60,32},{114,32}"),
        connect(f"{merge}.y", f"{projection}.u", "{166,40},{294,40}"),
        connect(f"{projection}.y", "command_guard.u", "{346,40},{444,40}"),
        connect("command_guard.y", "normalized_thrust", "{496,40},{550,40},{550,90},{594,90}"),
        connect(f"{bounded}.y", "learning_action", "{-14,90},{540,90},{540,10},{594,10}"),
        connect("fallback_flag.y", "fallback_active", "{496,-70},{594,-70}"),
    ]
    return f'''model {model} "P9 {route.replace('_', ' ')} learning-control signal chain"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.02),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.02,IntegratorStep=0.02,StartTime=0,StopTime=0.4,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-690,-150}},{{690,150}}}},grid={{2,2}})));
{chr(10).join(blocks)}
  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
{chr(10).join(equations)}
end {model};
'''


def main() -> int:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    models = {}
    for route, spec in ROUTES.items():
        path = MODEL_DIR / f"{spec['model']}.mo"
        path.write_text(build_model(route, spec), encoding="utf-8", newline="\n")
        models[route] = path.relative_to(ROOT).as_posix()
    manifest = {
        "schema": "mosim.control_platform.p9_learning_graphical_structure.v1",
        "status": "generated_pending_live_check",
        "live_check": None,
        "models": models,
        "claim_boundary": (
            "Readable learning-control signal chains for report topology only. "
            "The original P9 CFunction MWORKS MIL remains the numerical authority."
        ),
    }
    (RESULT_ROOT / "P9_GRAPHICAL_STRUCTURE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
