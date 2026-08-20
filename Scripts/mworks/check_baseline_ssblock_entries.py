#!/usr/bin/env python3
"""Check the two review baseline runners for direct graphical Sysblock entries.

This is a source/static gate. It does not replace Sysplorer ``check_model`` or
visible diagram review, but it prevents a later scenario command from silently
switching back to an equation-only, adapter, or diagnostics entry point.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

GRAPHICAL_CLASSES = {
    "official_core": {
        "path": "Models/MoSimQuadrotorModel/Control/PID/OfficialPidGraphicalCore.mo",
        "model": "OfficialPidGraphicalCore",
    },
    "shared_mapper": {
        "path": "Models/MoSimQuadrotorModel/Control/PID/BaselineRotorMapper.mo",
        "model": "BaselineRotorMapper",
    },
    "px4ctrl_outer_loop": {
        "path": "Models/MoSimQuadrotorModel/Control/Px4Ctrl/Px4CtrlOuterLoopGraphicalSysblock.mo",
        "model": "Px4CtrlOuterLoopGraphicalSysblock",
        "required_tokens": (
            "within MoSimQuadrotorModel.Control.Px4Ctrl;",
        ),
    },
    "px4ctrl_core": {
        "path": "Models/MoSimQuadrotorModel/Control/Px4Ctrl/Px4CtrlBaselineCore.mo",
        "model": "Px4CtrlBaselineCore",
        "required_tokens": (
            "Px4CtrlOuterLoopGraphicalSysblock outer_loop",
            "SysplorerEmbeddedCoder.Port.Inport vx_ref",
            "SysplorerEmbeddedCoder.Port.Inport vy_ref",
            "SysplorerEmbeddedCoder.Port.Inport vz_ref",
            "SysplorerEmbeddedCoder.Port.Inport ax_ref",
            "SysplorerEmbeddedCoder.Port.Inport ay_ref",
            "SysplorerEmbeddedCoder.Port.Inport az_ref",
            "SysplorerEmbeddedCoder.Port.Inport vx_mea",
            "SysplorerEmbeddedCoder.Port.Inport vy_mea",
            "SysplorerEmbeddedCoder.Port.Inport vz_mea",
            "connect(vx_ref, outer_loop.ref_v_x)",
            "connect(ax_ref, outer_loop.ref_a_x)",
            "connect(vx_mea, outer_loop.mea_v_x)",
            "connect(outer_loop.desired_acc_z, z_collective_delta.u1)",
        ),
    },
}

RUNNERS = {
    "official_pid": {
        "path": "Models/MoSimQuadrotorModel/Experiment/Baselines/OfficialPidRunner.mo",
        "model": "OfficialPidRunner",
        "core_type": "OfficialPidGraphicalCore",
        "core_instance": "core",
        "core_namespace": "MoSimQuadrotorModel.Control.PID",
        "mapper_type": "BaselineRotorMapper",
        "mapper_instance": "mapper",
        "mapper_namespace": "MoSimQuadrotorModel.Control.PID",
        "feedback_tokens": (
            "MoSimQuadrotorModel.Control.PID.WorldFramePassthrough preprocessor",
            "MoSimQuadrotorModel.Control.PID.OfficialPidGraphicalCore core",
            "MoSimQuadrotorModel.Control.PID.YawDampedAmplitudeRouter yaw_router",
        ),
        "feedback_contract": (
            "connect(plant.attitude, preprocessor.attitude)",
            "connect(preprocessor.roll_mea, core.roll_mea)",
        ),
        "forbidden_runner_tokens": ("roll_feedback_sign",),
    },
    "px4ctrl": {
        "path": "Models/MoSimQuadrotorModel/Experiment/Px4Ctrl/Px4CtrlRunner.mo",
        "model": "Px4CtrlRunner",
        "core_type": "Px4CtrlBaselineCore",
        "core_instance": "controller_core",
        "core_namespace": "MoSimQuadrotorModel.Control.Px4Ctrl",
        "mapper_type": "BaselineRotorMapper",
        "mapper_instance": "mapper",
        "mapper_namespace": "MoSimQuadrotorModel.Control.PID",
        "output_contract": (
            "connect(controller_core.y, output_bridge.amp_1)",
            "connect(controller_core.y1, output_bridge.amp_2)",
            "connect(controller_core.y2, output_bridge.amp_3)",
            "connect(controller_core.y3, output_bridge.amp_4)",
            "connect(output_bridge.out_1, mapper.amplitude_1)",
            "connect(output_bridge.out_2, mapper.amplitude_2)",
            "connect(output_bridge.out_3, mapper.amplitude_3)",
            "connect(output_bridge.out_4, mapper.amplitude_4)",
        ),
        "dynamic_contract": (
            "connect(input_sampler.s_vel_ref_x, controller_core.vx_ref)",
            "connect(input_sampler.s_acc_ref_x, controller_core.ax_ref)",
            "connect(input_sampler.s_vel_mea_x, controller_core.vx_mea)",
            "connect(input_sampler.s_att_roll, controller_core.roll_mea)",
        ),
    },
}

PACKAGE_ENTRIES = {
    "Models/MoSimQuadrotorModel/package.order": ("Control", "Experiment"),
    "Models/MoSimQuadrotorModel/Control/package.order": ("PID", "Px4Ctrl"),
    "Models/MoSimQuadrotorModel/Experiment/package.order": ("Baselines", "Px4Ctrl"),
    "Models/MoSimQuadrotorModel/Control/PID/package.order": (
        "OfficialPidGraphicalCore",
        "BaselineRotorMapper",
    ),
    "Models/MoSimQuadrotorModel/Control/Px4Ctrl/package.order": (
        "Px4CtrlBaselineCore",
        "Px4CtrlInputSampler",
        "Px4CtrlOutputBridge",
        "Px4CtrlOuterLoopGraphicalSysblock",
    ),
    "Models/MoSimQuadrotorModel/Experiment/Baselines/package.order": (
        "OfficialPidRunner",
    ),
    "Models/MoSimQuadrotorModel/Experiment/Px4Ctrl/package.order": (
        "Px4CtrlRunner",
    ),
}

PACKAGE_DECLARATIONS = {
    "Models/MoSimQuadrotorModel/Control/PID/package.mo": (
        "within MoSimQuadrotorModel.Control;",
        "package PID",
    ),
    "Models/MoSimQuadrotorModel/Control/Px4Ctrl/package.mo": (
        "within MoSimQuadrotorModel.Control;",
        "package Px4Ctrl",
    ),
    "Models/MoSimQuadrotorModel/Experiment/Baselines/package.mo": (
        "within MoSimQuadrotorModel.Experiment;",
        "package Baselines",
    ),
    "Models/MoSimQuadrotorModel/Experiment/Px4Ctrl/package.mo": (
        "within MoSimQuadrotorModel.Experiment;",
        "package Px4Ctrl",
    ),
}

CONNECT_RE = re.compile(r"\bconnect\s*\(", re.MULTILINE)
NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
POINT_RE = re.compile(rf"\{{\s*({NUMBER})\s*,\s*({NUMBER})\s*\}}")
USER_MODEL_BLOCK_RE = re.compile(
    r"BlockSystem\s*\(\s*blockKind\s*=\s*BlockKind\.userModel",
)
SYSBLOCK_VERSION_RE = re.compile(r"SysblockVersion\s*=")


def repo_path(relative_path: str) -> Path:
    path = (ROOT / relative_path).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as error:
        raise ValueError(f"path escapes repository: {relative_path}") from error
    return path


def read(relative_path: str) -> str:
    path = repo_path(relative_path)
    if not path.is_file():
        raise ValueError(f"missing source file: {relative_path}")
    return path.read_text(encoding="utf-8")


def statement_end(text: str, start: int) -> int:
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(start, len(text)):
        character = text[index]
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in {"'", '"'}:
            quote = character
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
        elif character == ";" and depth == 0:
            return index + 1
    raise ValueError("unterminated Modelica statement")


def connection_statements(text: str) -> list[str]:
    return [
        text[match.start() : statement_end(text, match.start())]
        for match in CONNECT_RE.finditer(text)
    ]


def visible_line_ok(statement: str) -> bool:
    line_match = re.search(
        r"annotation\s*\(\s*Line\s*\((?P<body>.*?)\)\s*\)",
        statement,
        re.DOTALL,
    )
    if line_match is None:
        return False
    points = [
        (float(x), float(y))
        for x, y in POINT_RE.findall(line_match.group("body"))
    ]
    return len(points) >= 2 and any(point != points[0] for point in points[1:])


def check_graphical_class(
    relative_path: str,
    model_name: str,
    required_tokens: tuple[str, ...] = (),
) -> dict[str, Any]:
    failures: list[str] = []
    text = read(relative_path)
    if not re.search(rf"^\s*model\s+{re.escape(model_name)}\b", text, re.MULTILINE):
        failures.append(f"model declaration missing: {model_name}")
    for token in (
        "extends ModelWorkspace;",
        "import BaseWorkspace.*;",
        "SysplorerEmbeddedCoder.Port.Inport",
        "SysplorerEmbeddedCoder.Port.Outport",
    ):
        if token not in text:
            failures.append(f"missing graphical Sysblock marker: {token}")
    if not USER_MODEL_BLOCK_RE.search(text):
        failures.append("missing graphical Sysblock marker: BlockSystem(blockKind=BlockKind.userModel")
    if not SYSBLOCK_VERSION_RE.search(text):
        failures.append("missing graphical Sysblock marker: SysblockVersion=")
    for token in required_tokens:
        if token not in text:
            failures.append(f"missing required graphical contract token: {token}")

    statements = connection_statements(text)
    invalid_lines = [
        index for index, statement in enumerate(statements, start=1)
        if not visible_line_ok(statement)
    ]
    if not statements:
        failures.append("no connect() topology")
    if invalid_lines:
        failures.append(
            "connections without non-degenerate Line annotations: "
            + ", ".join(map(str, invalid_lines))
        )
    return {
        "path": relative_path,
        "model": model_name,
        "connect_count": len(statements),
        "visible_line_count": len(statements) - len(invalid_lines),
        "invalid_line_connections": invalid_lines,
        "metadata_ok": bool(USER_MODEL_BLOCK_RE.search(text) and SYSBLOCK_VERSION_RE.search(text)),
        "ok": not failures,
        "failures": failures,
    }


def check_required_connections(
    text: str,
    required: list[str],
    *,
    require_visible_line: bool = True,
) -> list[str]:
    statements = connection_statements(text)
    missing: list[str] = []
    for token in required:
        match = next((statement for statement in statements if token in statement), None)
        if match is None:
            missing.append(token)
        elif require_visible_line and not visible_line_ok(match):
            missing.append(f"{token} [missing non-degenerate Line]")
    return missing


def check_runner(spec: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    text = read(spec["path"])
    if not re.search(rf"^\s*model\s+{re.escape(spec['model'])}\b", text, re.MULTILINE):
        failures.append(f"model declaration missing: {spec['model']}")
    direct_core = f"{spec['core_namespace']}.{spec['core_type']} {spec['core_instance']}"
    direct_mapper = f"{spec['mapper_namespace']}.{spec['mapper_type']} {spec['mapper_instance']}"
    for token in (direct_core, direct_mapper):
        if token not in text:
            failures.append(f"missing direct graphical instance: {token}")
    for token in ("ContinuousMapper", "EquationBridge", "SysblockCoreAdapter", "SysblockMapperAdapter"):
        if token in text:
            failures.append(f"forbidden fallback/adapter token in review runner: {token}")
    for token in spec.get("forbidden_runner_tokens", ()):
        if token in text:
            failures.append(f"forbidden runner token: {token}")
    for index in range(1, 5):
        required = [
            f"{spec['mapper_instance']}.rotor_command_{index}",
            f"fault_compensator.command_in[{index}]",
        ]
        bridge_connections: list[str] = []
        if spec.get("output_contract"):
            for token in spec["output_contract"]:
                if token.startswith("connect("):
                    bridge_connections.append(token)
                elif token not in text:
                    failures.append(f"missing runner bridge declaration: {token}")
        else:
            required.extend((
                f"connect({spec['core_instance']}.{'y' if index == 1 else f'y{index - 1}'}, yaw_router.amplitude_in_{index})",
                f"connect(yaw_router.amplitude_out_{index}, {spec['mapper_instance']}.amplitude_{index})",
            ))
        failures.extend(check_required_connections(text, required))
        if bridge_connections:
            failures.extend(check_required_connections(text, bridge_connections, require_visible_line=False))
    for token in spec.get("feedback_tokens", ()):
        if token not in text:
            failures.append(f"missing runner feedback token: {token}")
    failures.extend(
        check_required_connections(text, list(spec.get("feedback_contract", ())))
    )
    for token in spec.get("dynamic_contract", ()):
        if token not in text:
            failures.append(f"missing px4ctrl dynamic input contract: {token}")
    return {
        "path": spec["path"],
        "model": spec["model"],
        "core_type": spec["core_type"],
        "mapper_type": spec["mapper_type"],
        "ok": not failures,
        "failures": failures,
    }


def check_packages() -> dict[str, Any]:
    failures: list[str] = []
    checked: list[dict[str, Any]] = []
    for relative_path, tokens in PACKAGE_DECLARATIONS.items():
        text = read(relative_path)
        missing = [token for token in tokens if token not in text]
        if missing:
            failures.append(f"{relative_path}: missing declarations {', '.join(missing)}")
        checked.append({
            "path": relative_path,
            "required_declarations": list(tokens),
            "missing": missing,
            "ok": not missing,
        })
    for relative_path, entries in PACKAGE_ENTRIES.items():
        path = repo_path(relative_path)
        if not path.is_file():
            failures.append(f"missing package registration file: {relative_path}")
            checked.append({"path": relative_path, "entries": list(entries), "ok": False})
            continue
        lines = {
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
        missing = [entry for entry in entries if entry not in lines]
        if missing:
            failures.append(f"{relative_path}: missing entries {', '.join(missing)}")
        checked.append({
            "path": relative_path,
            "entries": list(entries),
            "missing": missing,
            "ok": not missing,
        })
    return {"ok": not failures, "checked": checked, "failures": failures}


def run_checks() -> dict[str, Any]:
    failures: list[str] = []
    graphical = {
        key: check_graphical_class(
            spec["path"],
            spec["model"],
            spec.get("required_tokens", ()),
        )
        for key, spec in GRAPHICAL_CLASSES.items()
    }
    runners = {key: check_runner(spec) for key, spec in RUNNERS.items()}
    package_result = check_packages()
    for item in (*graphical.values(), *runners.values()):
        failures.extend(f"{item['path']}: {failure}" for failure in item["failures"])
    failures.extend(package_result["failures"])
    return {
        "schema_version": "mosim.baseline_ssblock_entries.v1",
        "source": "static_model_contract",
        "status": "pass" if not failures else "fail",
        "ok": not failures,
        "entry_invariant": "graphical_core_to_mapper_via_unity_port_bridge",
        "graphical_classes": graphical,
        "runners": runners,
        "package_registration": package_result,
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args(argv)
    try:
        summary = run_checks()
    except (OSError, ValueError, re.error) as error:
        summary = {
            "schema_version": "mosim.baseline_ssblock_entries.v1",
            "source": "static_model_contract",
            "status": "fail",
            "ok": False,
            "failures": [str(error)],
        }
    if args.json_output:
        output = args.json_output if args.json_output.is_absolute() else ROOT / args.json_output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
