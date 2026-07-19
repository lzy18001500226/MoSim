#!/usr/bin/env python3
"""Build readable P5 enhancement graphical-structure fixtures."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT_ROOT = ROOT / "Results/control_platform/p5_enhancement_mworks_20260717"
MODEL_DIR = RESULT_ROOT / "models/graphical_variants"


HEADER = '''model {model} "P5 representative native graphical x-axis structure: {algorithm}"
  extends ModelWorkspace;
  import SysplorerEmbeddedCoder.Types.*;
  import BaseWorkspace.*;
  annotation(__MWORKS(version="26.3.0",modelType=Control,BlockSystem(blockKind=BlockKind.userModel,SampleTime(auto=true),OutputInterval=0.01),SysblockVersion="1.0"),experiment(Algorithm=Euler,Interval=0.01,IntegratorStep=0.01,StartTime=0,StopTime=0.2,StoreEventValue=0),Diagram(coordinateSystem(extent={{{{-520,-220}},{{520,220}}}},grid={{2,2}})));
'''

FOOTER = '''  model ModelWorkspace
    annotation(__MWORKS(hide=true,BlockSystem(blockKind=BlockKind.modelWorkspace)));
  end ModelWorkspace;
equation
{equations}
end {model};
'''


def constant(name: str, value: float, x: int, y: int) -> str:
    return f'  SysplorerEmbeddedCoder.Sources.Constant {name}(k={value}) annotation(Placement(transformation(origin={{{x},{y}}},extent={{{{-16,-12}},{{16,12}}}})));'


def gain(name: str, value: float, x: int, y: int) -> str:
    return f'  SysplorerEmbeddedCoder.MathOperation.Gain {name}(k={value}) annotation(Placement(transformation(origin={{{x},{y}}},extent={{{{-18,-14}},{{18,14}}}})));'


def summation(name: str, signs: str, x: int, y: int) -> str:
    return f'  SysplorerEmbeddedCoder.MathOperation.Sum {name}(inputs="{signs}") annotation(Placement(transformation(origin={{{x},{y}}},extent={{{{-18,-14}},{{18,14}}}})),__MWORKS(BlockSystem(Instance(u(u1,u2)))));'


def saturation(name: str, low: float, high: float, x: int, y: int) -> str:
    return f'  SysplorerEmbeddedCoder.Discontinuities.Saturation {name}(lowLimit={low},upLimit={high}) annotation(Placement(transformation(origin={{{x},{y}}},extent={{{{-18,-14}},{{18,14}}}})));'


def delay(name: str, x: int, y: int) -> str:
    return f'  SysplorerEmbeddedCoder.Discrete.UnitDelay {name}(initCond=0.0) annotation(Placement(transformation(origin={{{x},{y}}},extent={{{{-18,-14}},{{18,14}}}})));'


def outport(name: str, x: int, y: int) -> str:
    return f'  SysplorerEmbeddedCoder.Port.Outport {name} annotation(Placement(transformation(origin={{{x},{y}}},extent={{{{-14,-12}},{{14,12}}}})));'


def connect(source: str, target: str, points: str) -> str:
    return f'  connect({source},{target}) annotation(Line(points={{{points}}},color={{0,0,0}}));'


def render(model: str, algorithm: str, blocks: list[str], equations: list[str]) -> str:
    return HEADER.format(model=model, algorithm=algorithm) + "\n".join(blocks) + "\n" + FOOTER.format(
        model=model, equations="\n".join(equations)
    )


def common_sources() -> list[str]:
    return [
        constant("position_error_x", 0.8, -450, 100),
        constant("velocity_error_x", 0.4, -450, 40),
        constant("measured_acceleration_x", 0.1, -450, -80),
    ]


def common_nominal_blocks() -> list[str]:
    return [
        gain("position_feedback", 11.0, -350, 100),
        gain("velocity_feedback", 6.5, -350, 40),
        summation("nominal_acceleration", "++", -250, 70),
    ]


def common_nominal_connections() -> list[str]:
    return [
        connect("position_error_x.y", "position_feedback.u", "{-434,100},{-368,100}"),
        connect("velocity_error_x.y", "velocity_feedback.u", "{-434,40},{-368,40}"),
        connect("position_feedback.y", "nominal_acceleration.u1", "{-332,100},{-286,100},{-286,78},{-268,78}"),
        connect("velocity_feedback.y", "nominal_acceleration.u2", "{-332,40},{-286,40},{-286,62},{-268,62}"),
    ]


def build_models() -> dict[str, str]:
    variants: dict[str, tuple[list[str], list[str]]] = {}

    blocks = common_sources() + common_nominal_blocks() + [
        delay("disturbance_estimate", -170, -80),
        summation("residual", "+-", -350, -80),
        gain("l1_low_pass", 0.047619, -260, -80),
        summation("estimate_update", "++", -80, -80),
        gain("adaptive_compensation", -1.0, 20, -80),
        summation("enhanced_command", "++", 120, 30),
        saturation("acceleration_limit", -4.0, 4.0, 240, 30),
        outport("command_x", 400, 30), outport("compensation_x", 400, -80),
    ]
    equations = common_nominal_connections() + [
        connect("measured_acceleration_x.y", "residual.u1", "{-434,-80},{-368,-80}"),
        connect("disturbance_estimate.y", "residual.u2", "{-152,-80},{-152,-130},{-390,-130},{-390,-88},{-368,-88}"),
        connect("residual.y", "l1_low_pass.u", "{-332,-80},{-278,-80}"),
        connect("disturbance_estimate.y", "estimate_update.u1", "{-152,-80},{-116,-80},{-116,-72},{-98,-72}"),
        connect("l1_low_pass.y", "estimate_update.u2", "{-242,-80},{-116,-80},{-116,-88},{-98,-88}"),
        connect("estimate_update.y", "disturbance_estimate.u1", "{-62,-80},{-40,-80},{-40,-150},{-210,-150},{-210,-80},{-188,-80}"),
        connect("estimate_update.y", "adaptive_compensation.u", "{-62,-80},{2,-80}"),
        connect("adaptive_compensation.y", "enhanced_command.u2", "{38,-80},{80,-80},{80,22},{102,22}"),
        connect("nominal_acceleration.y", "enhanced_command.u1", "{-232,70},{80,70},{80,38},{102,38}"),
        connect("enhanced_command.y", "acceleration_limit.u", "{138,30},{222,30}"),
        connect("acceleration_limit.y", "command_x", "{258,30},{386,30}"),
        connect("adaptive_compensation.y", "compensation_x", "{38,-80},{386,-80}"),
    ]
    variants["l1_adaptive"] = (blocks, equations)

    blocks = common_sources() + common_nominal_blocks() + [
        gain("drag_feedforward", 0.12, -260, -40),
        delay("disturbance_observer", -170, -110),
        summation("observer_residual", "+-", -350, -110),
        gain("observer_bandwidth_dt", 0.05, -260, -110),
        summation("awff_compensation", "+-", -60, -60),
        summation("enhanced_command", "++", 100, 30),
        saturation("acceleration_limit", -4.0, 4.0, 220, 30),
        outport("command_x", 400, 30), outport("compensation_x", 400, -60),
    ]
    equations = common_nominal_connections() + [
        connect("velocity_error_x.y", "drag_feedforward.u", "{-434,40},{-300,40},{-300,-40},{-278,-40}"),
        connect("measured_acceleration_x.y", "observer_residual.u1", "{-434,-80},{-390,-80},{-390,-102},{-368,-102}"),
        connect("disturbance_observer.y", "observer_residual.u2", "{-152,-110},{-152,-160},{-390,-160},{-390,-118},{-368,-118}"),
        connect("observer_residual.y", "observer_bandwidth_dt.u", "{-332,-110},{-278,-110}"),
        connect("observer_bandwidth_dt.y", "disturbance_observer.u1", "{-242,-110},{-188,-110}"),
        connect("drag_feedforward.y", "awff_compensation.u1", "{-242,-40},{-100,-40},{-100,-52},{-78,-52}"),
        connect("disturbance_observer.y", "awff_compensation.u2", "{-152,-110},{-100,-110},{-100,-68},{-78,-68}"),
        connect("nominal_acceleration.y", "enhanced_command.u1", "{-232,70},{60,70},{60,38},{82,38}"),
        connect("awff_compensation.y", "enhanced_command.u2", "{-42,-60},{60,-60},{60,22},{82,22}"),
        connect("enhanced_command.y", "acceleration_limit.u", "{118,30},{202,30}"),
        connect("acceleration_limit.y", "command_x", "{238,30},{386,30}"),
        connect("awff_compensation.y", "compensation_x", "{-42,-60},{386,-60}"),
    ]
    variants["awff"] = (blocks, equations)

    blocks = common_sources() + common_nominal_blocks() + [
        gain("tracking_differentiator", 4.0, -220, 130),
        summation("eso_position_error", "+-", -350, -100),
        gain("eso_nonlinear_feedback", 8.0, -240, -100),
        delay("eso_disturbance_state", -140, -100),
        gain("disturbance_compensation", -1.0, -40, -100),
        summation("adrc_command", "++", 100, 30),
        saturation("acceleration_limit", -4.0, 4.0, 220, 30),
        outport("command_x", 400, 30), outport("observer_state_x", 400, -100),
    ]
    equations = common_nominal_connections() + [
        connect("position_error_x.y", "tracking_differentiator.u", "{-434,100},{-300,100},{-300,130},{-238,130}"),
        connect("measured_acceleration_x.y", "eso_position_error.u1", "{-434,-80},{-390,-80},{-390,-92},{-368,-92}"),
        connect("eso_disturbance_state.y", "eso_position_error.u2", "{-122,-100},{-122,-160},{-390,-160},{-390,-108},{-368,-108}"),
        connect("eso_position_error.y", "eso_nonlinear_feedback.u", "{-332,-100},{-258,-100}"),
        connect("eso_nonlinear_feedback.y", "eso_disturbance_state.u1", "{-222,-100},{-158,-100}"),
        connect("eso_disturbance_state.y", "disturbance_compensation.u", "{-122,-100},{-58,-100}"),
        connect("nominal_acceleration.y", "adrc_command.u1", "{-232,70},{60,70},{60,38},{82,38}"),
        connect("disturbance_compensation.y", "adrc_command.u2", "{-22,-100},{60,-100},{60,22},{82,22}"),
        connect("adrc_command.y", "acceleration_limit.u", "{118,30},{202,30}"),
        connect("acceleration_limit.y", "command_x", "{238,30},{386,30}"),
        connect("eso_disturbance_state.y", "observer_state_x", "{-122,-100},{386,-100}"),
    ]
    variants["complete_adrc"] = (blocks, equations)

    blocks = common_sources() + common_nominal_blocks() + [
        summation("acceleration_increment_error", "+-", -120, -60),
        gain("indi_increment_gain", 0.12, -20, -60),
        saturation("increment_limit", -0.35, 0.35, 80, -60),
        summation("indi_command", "++", 180, 30),
        saturation("acceleration_limit", -4.0, 4.0, 290, 30),
        outport("command_x", 430, 30), outport("compensation_x", 430, -60),
    ]
    equations = common_nominal_connections() + [
        connect("nominal_acceleration.y", "acceleration_increment_error.u1", "{-232,70},{-170,70},{-170,-52},{-138,-52}"),
        connect("measured_acceleration_x.y", "acceleration_increment_error.u2", "{-434,-80},{-170,-80},{-170,-68},{-138,-68}"),
        connect("acceleration_increment_error.y", "indi_increment_gain.u", "{-102,-60},{-38,-60}"),
        connect("indi_increment_gain.y", "increment_limit.u", "{-2,-60},{62,-60}"),
        connect("nominal_acceleration.y", "indi_command.u1", "{-232,70},{140,70},{140,38},{162,38}"),
        connect("increment_limit.y", "indi_command.u2", "{98,-60},{140,-60},{140,22},{162,22}"),
        connect("indi_command.y", "acceleration_limit.u", "{198,30},{272,30}"),
        connect("acceleration_limit.y", "command_x", "{308,30},{416,30}"),
        connect("increment_limit.y", "compensation_x", "{98,-60},{416,-60}"),
    ]
    variants["standardized_indi"] = (blocks, equations)

    blocks = common_sources() + common_nominal_blocks() + [
        gain("error_normalization", 2.857143, -260, -80),
        saturation("blend_limit", 0.0, 1.0, -160, -80),
        gain("gain_range", 0.35, -60, -80),
        constant("base_gain", 1.0, -60, -140),
        summation("effective_gain_scale", "++", 40, -100),
        gain("scheduled_feedback", 1.0, 40, 70),
        saturation("acceleration_limit", -4.0, 4.0, 180, 70),
        outport("command_x", 400, 70), outport("gain_scale", 400, -100),
    ]
    equations = common_nominal_connections() + [
        connect("position_error_x.y", "error_normalization.u", "{-434,100},{-300,100},{-300,-80},{-278,-80}"),
        connect("error_normalization.y", "blend_limit.u", "{-242,-80},{-178,-80}"),
        connect("blend_limit.y", "gain_range.u", "{-142,-80},{-78,-80}"),
        connect("gain_range.y", "effective_gain_scale.u1", "{-42,-80},{0,-80},{0,-92},{22,-92}"),
        connect("base_gain.y", "effective_gain_scale.u2", "{-44,-140},{0,-140},{0,-108},{22,-108}"),
        connect("nominal_acceleration.y", "scheduled_feedback.u", "{-232,70},{22,70}"),
        connect("scheduled_feedback.y", "acceleration_limit.u", "{58,70},{162,70}"),
        connect("acceleration_limit.y", "command_x", "{198,70},{386,70}"),
        connect("effective_gain_scale.y", "gain_scale", "{58,-100},{386,-100}"),
    ]
    variants["parameter_scheduling"] = (blocks, equations)

    blocks = common_sources() + common_nominal_blocks() + [
        gain("learning_gain", 0.08, -240, -80),
        delay("phase_memory", -140, -80),
        gain("forgetting_factor", 0.995, -140, -140),
        summation("memory_update", "++", -20, -100),
        saturation("memory_limit", -1.5, 1.5, 90, -100),
        summation("ilc_command", "++", 190, 30),
        saturation("acceleration_limit", -4.0, 4.0, 300, 30),
        outport("command_x", 430, 30), outport("learned_compensation_x", 430, -100),
    ]
    equations = common_nominal_connections() + [
        connect("position_error_x.y", "learning_gain.u", "{-434,100},{-300,100},{-300,-80},{-258,-80}"),
        connect("phase_memory.y", "forgetting_factor.u", "{-122,-80},{-110,-80},{-110,-140},{-122,-140}"),
        connect("learning_gain.y", "memory_update.u1", "{-222,-80},{-60,-80},{-60,-92},{-38,-92}"),
        connect("forgetting_factor.y", "memory_update.u2", "{-122,-140},{-60,-140},{-60,-108},{-38,-108}"),
        connect("memory_update.y", "memory_limit.u", "{-2,-100},{72,-100}"),
        connect("memory_limit.y", "phase_memory.u1", "{108,-100},{130,-100},{130,-180},{-180,-180},{-180,-80},{-158,-80}"),
        connect("nominal_acceleration.y", "ilc_command.u1", "{-232,70},{150,70},{150,38},{172,38}"),
        connect("phase_memory.y", "ilc_command.u2", "{-122,-80},{150,-80},{150,22},{172,22}"),
        connect("ilc_command.y", "acceleration_limit.u", "{208,30},{282,30}"),
        connect("acceleration_limit.y", "command_x", "{318,30},{416,30}"),
        connect("phase_memory.y", "learned_compensation_x", "{-122,-80},{-100,-80},{-100,-200},{390,-200},{390,-100},{416,-100}"),
    ]
    variants["ilc"] = (blocks, equations)

    paths: dict[str, str] = {}
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    for algorithm, (blocks, equations) in variants.items():
        model = f"MoSim_P5_{algorithm.upper()}_GRAPHICAL_MIL"
        path = MODEL_DIR / f"{model}.mo"
        path.write_text(render(model, algorithm, blocks, equations), encoding="utf-8", newline="\n")
        paths[algorithm] = str(path.relative_to(ROOT)).replace("\\", "/")
    return paths


def main() -> int:
    paths = build_models()
    manifest = {
        "schema": "mosim.control_platform.p5_enhancement_graphical_structure.v1",
        "status": "generated_pending_live_check",
        "models": paths,
        "claim_boundary": (
            "Readable x-axis native graphical structure fixtures derived from the frozen P5 C core. "
            "They document algorithm topology and are not numerical-equivalence or full-aircraft gates."
        ),
    }
    path = RESULT_ROOT / "P5_GRAPHICAL_STRUCTURE_MANIFEST.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
