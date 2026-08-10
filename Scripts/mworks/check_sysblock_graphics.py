#!/usr/bin/env python3
"""Static acceptance checks for project graphical Sysblock controllers."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MODEL_DECLARATION_RE = re.compile(r"^\s*model\s+([A-Za-z_][A-Za-z0-9_]*)\b")
MODEL_END_RE = re.compile(r"^\s*end\s+([A-Za-z_][A-Za-z0-9_]*)\s*;")
EXTENDS_RE = re.compile(r"^\s*extends\s+([^;(\s]+)", re.MULTILINE)


@dataclass(eq=False)
class ModelicaModel:
    path: Path
    name: str
    start_line: int
    end_line: int | None = None
    parent: "ModelicaModel | None" = None


def modelica_models(base: Path) -> tuple[list[ModelicaModel], dict[Path, list[str]]]:
    """Return named Modelica model blocks with their direct lexical parents."""

    models: list[ModelicaModel] = []
    sources: dict[Path, list[str]] = {}
    for path in sorted(base.glob("*.mo")):
        lines = path.read_text(encoding="utf-8").splitlines()
        sources[path] = lines
        stack: list[ModelicaModel] = []
        for line_number, line in enumerate(lines, start=1):
            declaration = MODEL_DECLARATION_RE.match(line)
            if declaration:
                model = ModelicaModel(
                    path=path,
                    name=declaration.group(1),
                    start_line=line_number,
                    parent=stack[-1] if stack else None,
                )
                models.append(model)
                stack.append(model)

            ending = MODEL_END_RE.match(line)
            if ending:
                for index in range(len(stack) - 1, -1, -1):
                    if stack[index].name == ending.group(1):
                        stack[index].end_line = line_number
                        del stack[index:]
                        break
        unclosed = [model.name for model in stack]
        if unclosed:
            raise ValueError(f"unclosed Modelica model(s) in {path}: {', '.join(unclosed)}")
    return models, sources


def model_own_text(
    model: ModelicaModel,
    models: list[ModelicaModel],
    sources: dict[Path, list[str]],
) -> str:
    """Return a model body without direct nested models contaminating its metadata."""

    if model.end_line is None:
        raise ValueError(f"model has no end marker: {model.path}:{model.start_line}")
    lines = list(sources[model.path][model.start_line - 1 : model.end_line])
    for child in models:
        if child.parent is not model or child.end_line is None:
            continue
        start = child.start_line - model.start_line
        end = child.end_line - model.start_line
        lines[start : end + 1] = [""] * (end - start + 1)
    return "\n".join(lines)


def model_label(model: ModelicaModel, base: Path) -> str:
    names: list[str] = []
    current: ModelicaModel | None = model
    while current is not None:
        names.append(current.name)
        current = current.parent
    return f"{model.path.relative_to(base).as_posix()}:{'.'.join(reversed(names))}"


def direct_extends(text: str) -> list[str]:
    return EXTENDS_RE.findall(text)


def base_name(base_class: str) -> str:
    return base_class.rsplit(".", maxsplit=1)[-1]


def sysblock_metadata_audit(base: Path) -> dict[str, Any]:
    """Audit real Sysblock classes by class body, not by file name.

    Package-navigation aliases are reported separately. They intentionally do
    not own a graphical diagram, so copying a base class's full annotation into
    them would turn navigation wrappers into misleading independent Sysblocks.
    """

    models, sources = modelica_models(base)
    own_texts = {id(model): model_own_text(model, models, sources) for model in models}
    is_sysblock = {
        id(model): (
            "SysblockVersion" in own_texts[id(model)]
            and "BlockSystem(blockKind=BlockKind.userModel" in own_texts[id(model)]
        )
        for model in models
    }
    sysblocks = [model for model in models if is_sysblock[id(model)]]
    by_name: dict[str, list[ModelicaModel]] = {}
    for model in sysblocks:
        by_name.setdefault(model.name, []).append(model)

    def resolves_model_workspace(model: ModelicaModel, visited: set[int] | None = None) -> bool:
        visited = set() if visited is None else visited
        if id(model) in visited:
            return False
        visited.add(id(model))
        bases = direct_extends(own_texts[id(model)])
        if any(base_name(base) == "ModelWorkspace" for base in bases):
            return True
        for base in bases:
            for parent_model in by_name.get(base_name(base), []):
                if resolves_model_workspace(parent_model, visited):
                    return True
        return False

    def resolves_base_workspace_import(
        model: ModelicaModel,
        visited: set[int] | None = None,
    ) -> bool:
        visited = set() if visited is None else visited
        if id(model) in visited:
            return False
        visited.add(id(model))
        if re.search(r"^\s*import\s+BaseWorkspace\.\*;", own_texts[id(model)], re.MULTILINE):
            return True
        if model.parent is not None and resolves_base_workspace_import(model.parent, visited):
            return True
        for base in direct_extends(own_texts[id(model)]):
            for parent_model in by_name.get(base_name(base), []):
                if resolves_base_workspace_import(parent_model, visited):
                    return True
        return False

    missing_model_workspace = [
        model_label(model, base)
        for model in sysblocks
        if not resolves_model_workspace(model)
    ]
    missing_base_workspace_import = [
        model_label(model, base)
        for model in sysblocks
        if not resolves_base_workspace_import(model)
    ]

    # Duplicate declarations are illegal within one class body. Matching
    # declarations on a parent chain are legal and remain resolver-only.
    duplicate_model_workspace_extends: list[str] = []
    duplicate_base_workspace_import: list[str] = []
    for model in sysblocks:
        own = own_texts[id(model)]
        workspace_count = sum(
            1 for parent in direct_extends(own) if base_name(parent) == "ModelWorkspace"
        )
        if workspace_count >= 2:
            lines = [
                model.start_line + offset
                for offset, line in enumerate(own.splitlines())
                if re.match(r"^\s*extends\s+ModelWorkspace\s*(\(|;)", line)
            ]
            duplicate_model_workspace_extends.append(
                f"{model_label(model, base)} count={workspace_count} lines={lines}"
            )
        import_count = len(
            re.findall(r"^\s*import\s+BaseWorkspace\.\*;", own, re.MULTILINE)
        )
        if import_count >= 2:
            duplicate_base_workspace_import.append(
                f"{model_label(model, base)} count={import_count}"
            )

    missing_derived_metadata: list[str] = []
    package_navigation_aliases: list[str] = []
    for model in models:
        if is_sysblock[id(model)]:
            continue
        base_targets = [
            base
            for base in direct_extends(own_texts[id(model)])
            if base_name(base) in by_name
        ]
        if not base_targets or "SysblockVersion" in own_texts[id(model)]:
            continue
        is_navigation_alias = (
            model.path.name == "package.mo"
            and "connect(" not in own_texts[id(model)]
            and "SysplorerEmbeddedCoder.Port." not in own_texts[id(model)]
        )
        label = model_label(model, base)
        if is_navigation_alias:
            package_navigation_aliases.append(label)
        else:
            missing_derived_metadata.append(label)

    by_file: dict[str, int] = {}
    for model in sysblocks:
        filename = model.path.relative_to(base).as_posix()
        by_file[filename] = by_file.get(filename, 0) + 1
    innovation_count = by_file.get("AWFF_InnovationGraphicalControllers.mo", 0)
    return {
        "scope": base.as_posix(),
        "sysblock_class_count": len(sysblocks),
        "sysblock_class_count_by_file": by_file,
        "awff_innovation_graphical_controllers_class_count": innovation_count,
        "missing_model_workspace": missing_model_workspace,
        "missing_base_workspace_import": missing_base_workspace_import,
        "duplicate_model_workspace_extends": duplicate_model_workspace_extends,
        "duplicate_base_workspace_import": duplicate_base_workspace_import,
        "derived_sysblock_missing_own_metadata": missing_derived_metadata,
        "package_navigation_aliases_excluded": package_navigation_aliases,
        "pass": not (
            missing_model_workspace
            or missing_base_workspace_import
            or missing_derived_metadata
            or duplicate_model_workspace_extends
            or duplicate_base_workspace_import
        ),
    }


BEHAVIOR_EXPECTATIONS: dict[str, list[str]] = {
    "AWFF_FullControllerFlatGraphical_Sysblock.mo": [
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
        "SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator",
    ],
    "AWFF_InnovationGraphicalControllers.L1ResidualOuterLoopBlock": [
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
        "SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator",
    ],
    "AWFF_InnovationGraphicalControllers.PIDAttitudeInnerLoopBlock": [
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
    ],
    "AWFF_InnovationGraphicalControllers.INDIAttitudeInnerLoopBlock": [
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
        "SysplorerEmbeddedCoder.Discrete.UnitDelay",
    ],
    "AWFF_InnovationGraphicalControllers.MotorMixerBlock": [
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
    ],
    "AWFF_InnovationGraphicalControllers.KnownRotorFaultMixerBlock": [
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
    ],
    "AWFF_InnovationGraphicalControllers.RotorFaultIsolationBlock": [
        "SysplorerEmbeddedCoder.Discontinuities.DeadZone",
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
        "SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator",
        "SysplorerEmbeddedCoder.SignalRouting.Switch",
    ],
    "AWFF_InnovationGraphicalControllers.AdaptiveFaultMixerBlock": [
        "SysplorerEmbeddedCoder.MathOperation.Product",
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
    ],
    "AWFF_InnovationGraphicalControllers.LinearMPCOuterLoopBlock": [
        "SysplorerEmbeddedCoder.Discrete.UnitDelay",
        "SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator",
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
    ],
    "AWFF_InnovationGraphicalControllers.Rotor1OnlineEfficiencyEstimatorBlock": [
        "SysplorerEmbeddedCoder.Discontinuities.DeadZone",
        "SysplorerEmbeddedCoder.Discrete.DiscreteTimeIntegrator",
        "SysplorerEmbeddedCoder.Discontinuities.Saturation",
    ],
    "AWFF_InnovationGraphicalControllers.AWFF_L1OnlineFaultAllocationControllerGraphical_Sysblock": [
        "L1ResidualOuterLoopBlock",
        "Rotor1OnlineEfficiencyEstimatorBlock",
        "AdaptiveFaultMixerBlock",
    ],
    "AWFF_InnovationGraphicalControllers.AWFF_FaultCompensationControllerGraphical_Sysblock": [
        "L1ResidualOuterLoopBlock",
        "PIDAttitudeInnerLoopBlock",
        "KnownRotorFaultMixerBlock",
    ],
    "AWFF_InnovationGraphicalControllers.AWFF_LinearMPCControllerGraphical_Sysblock": [
        "LinearMPCOuterLoopBlock",
        "INDIAttitudeInnerLoopBlock",
        "MotorMixerBlock",
    ],
    "AWFF_InnovationGraphicalControllers.AWFF_LinearMPCOnlineFaultAllocationControllerGraphical_Sysblock": [
        "LinearMPCOuterLoopBlock",
        "Rotor1OnlineEfficiencyEstimatorBlock",
        "AdaptiveFaultMixerBlock",
    ],
}


REQUIRED_MODELS: dict[str, dict[str, Any]] = {
    "AWFF_PositionOuterLoop_Sysblock.mo": {
        "inports": ["x_error", "y_error", "z_error", "z_ref_rate"],
        "outports": ["pitch_ref", "roll_ref", "thrust_ref"],
        "required_blocks": ["x_kp", "x_kd", "x_sum", "x_scale", "y_kp", "y_kd", "y_sum", "y_scale", "z_kp", "z_ki", "z_kd", "z_ff", "z_sum"],
        "min_connects": 20,
    },
    "AWFF_AttitudeInnerLoop_Sysblock.mo": {
        "inports": ["roll_ref", "pitch_ref", "yaw_ref", "roll_mea", "pitch_mea", "yaw_mea"],
        "outports": ["roll_cmd", "pitch_cmd", "yaw_cmd"],
        "required_blocks": ["roll_error", "roll_kp", "roll_kd", "roll_sum", "pitch_error", "pitch_kp", "pitch_kd", "pitch_sum", "yaw_error", "yaw_kp"],
        "min_connects": 18,
    },
    "AWFF_MotorMixer_Sysblock.mo": {
        "inports": ["thrust_ref", "roll_cmd", "pitch_cmd", "yaw_cmd"],
        "outports": ["y", "y1", "y2", "y3"],
        "required_blocks": ["neg_roll", "neg_pitch", "neg_yaw", "motor1_sum", "motor2_sum", "motor3_sum", "motor4_sum"],
        "min_connects": 23,
    },
    "AWFF_FullController_Sysblock.mo": {
        "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
        "outports": ["y", "y1", "y2", "y3"],
        "required_blocks": ["position_loop", "attitude_loop", "motor_mixer"],
        "required_references": ["AWFF_PositionOuterLoop_Sysblock", "AWFF_AttitudeInnerLoop_Sysblock", "AWFF_MotorMixer_Sysblock"],
        "min_connects": 18,
    },
    "AWFF_FullControllerFlatGraphical_Sysblock.mo": {
        "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
        "outports": ["y", "y1", "y2", "y3"],
        "required_blocks": ["x_kp", "x_kd", "x_sum", "pitch_ref_scale", "y_kp", "y_kd", "y_sum", "roll_ref_scale", "z_kp", "z_ki", "z_kd", "z_ff", "thrust_sum", "roll_error", "roll_cmd_sum", "pitch_error", "pitch_cmd_sum", "yaw_error", "motor1_sum", "motor2_sum", "motor3_sum", "motor4_sum"],
        "min_connects": 60,
    },
}


PACKAGE_MODELS: dict[str, dict[str, dict[str, Any]]] = {
    "AWFF_InnovationGraphicalControllers.mo": {
        "INDIAttitudeInnerLoopBlock": {
            "inports": ["roll_ref", "pitch_ref", "yaw_ref", "roll_mea", "pitch_mea", "yaw_mea"],
            "outports": ["roll_cmd", "pitch_cmd", "yaw_cmd"],
            "required_blocks": [
                "roll_error_sum",
                "roll_kp_gain",
                "roll_indi_gain_block",
                "pitch_error_sum",
                "pitch_kp_gain",
                "pitch_indi_gain_block",
                "yaw_error_sum",
                "yaw_kp_gain",
                "yaw_indi_gain_block",
            ],
            "min_connects": 27,
        },
        "MotorMixerBlock": {
            "inports": ["thrust_ref", "roll_cmd", "pitch_cmd", "yaw_cmd"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": [
                "roll_pos",
                "roll_neg",
                "pitch_pos",
                "pitch_neg",
                "yaw_pos",
                "yaw_neg",
                "thrust_neg",
                "motor1_sum",
                "motor2_sum",
                "motor3_sum",
                "motor4_sum",
            ],
            "min_connects": 23,
        },
        "KnownRotorFaultMixerBlock": {
            "inports": ["thrust_ref", "roll_cmd", "pitch_cmd", "yaw_cmd"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["raw_mixer", "rotor1_comp_gain"],
            "min_connects": 5,
        },
        "RotorFaultIsolationBlock": {
            "inports": ["x_error", "y_error"],
            "outports": ["eta_hat1", "eta_hat2", "eta_hat3", "eta_hat4", "fault_index"],
            "required_blocks": ["neg_x_half", "pos_x_half", "neg_y_half", "pos_y_half", "sig1_sum", "eta1_gain", "eta1_raw_sum"],
            "min_connects": 24,
        },
        "AdaptiveFaultMixerBlock": {
            "inports": ["thrust_ref", "roll_cmd", "pitch_cmd", "yaw_cmd", "eta_hat1", "eta_hat2", "eta_hat3", "eta_hat4"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["raw_mixer"],
            "min_connects": 4,
        },
        "AWFF_L1ResidualControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["l1_outer", "attitude_loop", "motor_mixer", "L1ResidualOuterLoopBlock", "PIDAttitudeInnerLoopBlock", "MotorMixerBlock"],
            "min_connects": 18,
        },
        "AWFF_INDIControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["l1_outer", "attitude_loop", "motor_mixer", "L1ResidualOuterLoopBlock", "INDIAttitudeInnerLoopBlock", "MotorMixerBlock"],
            "min_connects": 18,
        },
        "AWFF_L1FaultAllocationControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["l1_outer", "attitude_loop", "motor_mixer", "L1ResidualOuterLoopBlock", "PIDAttitudeInnerLoopBlock", "KnownRotorFaultMixerBlock"],
            "min_connects": 18,
        },
        "AWFF_L1MultiFaultIsolationControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3", "eta_hat1", "eta_hat2", "eta_hat3", "eta_hat4", "fault_index"],
            "required_blocks": ["l1_outer", "attitude_loop", "motor_mixer", "fault_isolation", "L1ResidualOuterLoopBlock", "PIDAttitudeInnerLoopBlock", "AdaptiveFaultMixerBlock", "RotorFaultIsolationBlock"],
            "min_connects": 29,
        },
        "AWFF_L1OnlineFaultAllocationControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3", "eta_hat"],
            "required_blocks": ["l1_outer", "attitude_loop", "motor_mixer", "rotor1_eta_estimator", "L1ResidualOuterLoopBlock", "PIDAttitudeInnerLoopBlock", "AdaptiveFaultMixerBlock", "Rotor1OnlineEfficiencyEstimatorBlock"],
            "min_connects": 24,
        },
        "AWFF_FaultCompensationControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["awff_outer", "attitude_loop", "motor_mixer", "L1ResidualOuterLoopBlock", "PIDAttitudeInnerLoopBlock", "KnownRotorFaultMixerBlock"],
            "min_connects": 18,
        },
        "LinearMPCOuterLoopBlock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate"],
            "outports": ["pitch_ref", "roll_ref", "thrust_ref"],
            "required_blocks": [
                "x_error_delay",
                "x_horizon_gain",
                "x_terminal_sum",
                "x_l1_filter",
                "x_acc_sat",
                "pitch_ref_sat",
                "y_error_delay",
                "y_horizon_gain",
                "y_terminal_sum",
                "y_l1_filter",
                "y_acc_sat",
                "roll_ref_sat",
                "z_error_delay",
                "z_horizon_gain",
                "z_terminal_sum",
                "z_integrator",
                "z_l1_filter_mpc",
                "thrust_sat",
            ],
            "min_connects": 75,
        },
        "Rotor1OnlineEfficiencyEstimatorBlock": {
            "inports": ["x_error", "y_error"],
            "outports": ["eta_hat"],
            "required_blocks": [
                "eta_signature_sum",
                "eta_signature_deadzone",
                "eta_drop_filter",
                "eta_raw_sum",
                "eta_sat",
            ],
            "min_connects": 11,
        },
        "AWFF_LinearMPCControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3"],
            "required_blocks": ["mpc_outer", "attitude_loop", "motor_mixer", "LinearMPCOuterLoopBlock", "INDIAttitudeInnerLoopBlock", "MotorMixerBlock"],
            "min_connects": 18,
        },
        "AWFF_LinearMPCOnlineFaultAllocationControllerGraphical_Sysblock": {
            "inports": ["x_error", "y_error", "z_error", "z_ref_rate", "roll_mea", "pitch_mea", "yaw_mea", "yaw_ref"],
            "outports": ["y", "y1", "y2", "y3", "eta_hat"],
            "required_blocks": ["mpc_outer", "attitude_loop", "motor_mixer", "rotor1_eta_estimator", "LinearMPCOuterLoopBlock", "INDIAttitudeInnerLoopBlock", "AdaptiveFaultMixerBlock", "Rotor1OnlineEfficiencyEstimatorBlock"],
            "min_connects": 24,
        },
    },
}


def find_port_names(text: str, port_kind: str) -> list[str]:
    pattern = re.compile(rf"SysplorerEmbeddedCoder\.Port\.{port_kind}\s+([A-Za-z_][A-Za-z0-9_]*)")
    return pattern.findall(text)


def top_level_model_text(text: str) -> str:
    """Return declarations before nested model definitions.

    Hierarchical Sysblock controllers may embed child models so a standalone
    parent file can be opened without preloading dependencies. Static port
    checks should still report only the parent model interface.
    """

    match = re.search(r"^  model\s+[A-Za-z_][A-Za-z0-9_]*\b", text, re.MULTILINE)
    return text[: match.start()] if match else text


def named_model_text(text: str, model_name: str) -> str:
    match = re.search(rf"^  model\s+{re.escape(model_name)}\b", text, re.MULTILINE)
    if not match:
        return ""
    end_match = re.search(rf"^  end\s+{re.escape(model_name)};", text[match.start() :], re.MULTILINE)
    if not end_match:
        return text[match.start() :]
    return text[match.start() : match.start() + end_match.end()]


def check_text(
    interface_text: str,
    path: Path,
    spec: dict[str, Any],
    label: str | None = None,
    structure_text: str | None = None,
) -> dict[str, Any]:
    if structure_text is None:
        structure_text = interface_text
    inports = find_port_names(interface_text, "Inport")
    outports = find_port_names(interface_text, "Outport")
    connect_count = structure_text.count("connect(")
    line_count = structure_text.count("annotation(Line")
    placement_count = structure_text.count("Placement(")

    missing_inports = [name for name in spec["inports"] if name not in inports]
    missing_outports = [name for name in spec["outports"] if name not in outports]
    missing_blocks = [
        name
        for name in spec.get("required_blocks", [])
        if not re.search(rf"\b{name}\b", structure_text)
    ]
    missing_refs = [
        name
        for name in spec.get("required_references", [])
        if name not in structure_text
    ]

    failures: list[str] = []
    if missing_inports:
        failures.append(f"missing inports: {', '.join(missing_inports)}")
    if missing_outports:
        failures.append(f"missing outports: {', '.join(missing_outports)}")
    if missing_blocks:
        failures.append(f"missing blocks: {', '.join(missing_blocks)}")
    if missing_refs:
        failures.append(f"missing references: {', '.join(missing_refs)}")
    if connect_count < int(spec["min_connects"]):
        failures.append(f"connect count {connect_count} < {spec['min_connects']}")
    if line_count != connect_count:
        failures.append(f"annotation(Line) count {line_count} != connect count {connect_count}")
    if placement_count <= len(inports) + len(outports):
        failures.append("diagram placements do not cover internal blocks")

    return {
        "file": path.as_posix(),
        "model": label,
        "ok": not failures,
        "inports": inports,
        "outports": outports,
        "connect_count": connect_count,
        "line_annotation_count": line_count,
        "placement_count": placement_count,
        "failures": failures,
    }


def check_model(path: Path, spec: dict[str, Any]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    parent_text = top_level_model_text(text)
    return check_text(parent_text if parent_text else text, path, spec, structure_text=text)


def check_package_models(path: Path, specs: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    results: list[dict[str, Any]] = []
    for model_name, spec in specs.items():
        model_text = named_model_text(text, model_name)
        if not model_text:
            results.append(
                {
                    "file": path.as_posix(),
                    "model": model_name,
                    "ok": False,
                    "inports": [],
                    "outports": [],
                    "connect_count": 0,
                    "line_annotation_count": 0,
                    "placement_count": 0,
                    "failures": ["model not found"],
                }
            )
            continue
        results.append(check_text(model_text, path, spec, model_name))
    if re.search(r"extends\s+AWFF_|redeclare|extends\s+MotorMixerBlock", text):
        results.append(
            {
                "file": path.as_posix(),
                "model": "package_safety",
                "ok": False,
                "inports": [],
                "outports": [],
                "connect_count": 0,
                "line_annotation_count": 0,
                "placement_count": 0,
                "failures": ["package contains fragile graphical inheritance/redeclare pattern"],
            }
        )
    return results


def behavior_contract_checks(base: Path) -> list[dict[str, Any]]:
    """Report whether graphical models expose key dynamic/nonlinear behavior.

    The structure checks above answer "can this model be opened and reviewed as
    a block diagram?". This contract answers the separate question the project
    actually needs before using a graphical model as a simulation counterpart:
    do the diagrams contain the expected saturation, delay/integrator, switch,
    dead-zone, and product behavior instead of only passing wires through?
    """

    results: list[dict[str, Any]] = []
    innovation_path = base / "AWFF_InnovationGraphicalControllers.mo"
    for label, required_tokens in BEHAVIOR_EXPECTATIONS.items():
        if label.endswith(".mo"):
            path = base / label
            model_text = path.read_text(encoding="utf-8") if path.exists() else ""
        else:
            path = innovation_path
            model_name = label.split(".")[-1]
            package_text = path.read_text(encoding="utf-8") if path.exists() else ""
            model_text = named_model_text(package_text, model_name)

        missing = [token for token in required_tokens if token not in model_text]
        results.append(
            {
                "file": path.as_posix(),
                "model": label,
                "ok": not missing,
                "required_behavior_blocks": required_tokens,
                "missing_behavior_blocks": missing,
                "failures": []
                if not missing
                else [
                    "missing graphical behavior blocks: "
                    + ", ".join(missing)
                ],
            }
        )
    return results


def run_checks() -> dict[str, Any]:
    base = (
        ROOT
        / "Models"
        / "MoSimQuadrotorModel"
        / "Control"
        / "Implementations"
        / "Sysblocks"
    )
    results = [check_model(base / filename, spec) for filename, spec in REQUIRED_MODELS.items()]
    for filename, specs in PACKAGE_MODELS.items():
        results.extend(check_package_models(base / filename, specs))
    behavior_results = behavior_contract_checks(base)
    metadata_audit = sysblock_metadata_audit(base)
    structure_ok = all(item["ok"] for item in results)
    behavior_equivalence_ok = all(item["ok"] for item in behavior_results)
    metadata_ok = bool(metadata_audit["pass"])
    return {
        "source": "static_model_contract",
        "scope": "graphical_awff_sysblock_controller",
        "ok": structure_ok and behavior_equivalence_ok and metadata_ok,
        "structure_ok": structure_ok,
        "behavior_equivalence_ok": behavior_equivalence_ok,
        "metadata_ok": metadata_ok,
        "metadata_audit": metadata_audit,
        "Results": results,
        "behavior_results": behavior_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, help="Optional JSON summary output path")
    args = parser.parse_args()

    summary = run_checks()
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
