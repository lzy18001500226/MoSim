#!/usr/bin/env python3
"""Audit and repair the current 46-controller graphical runner layouts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "Config" / "control_platform" / "control_scheme_catalog.json"

FAMILY_DIRS = {
    "PidFamily": "SingleUav/PidFamily",
    "ClassicRobust": "SingleUav/ClassicRobust",
    "SlidingMode": "SingleUav/SlidingMode",
    "Optimization": "SingleUav/Optimization",
    "GeometricFlatness": "SingleUav/GeometricFlatness",
    "Learning": "SingleUav/Learning",
}

SPECIAL_PATHS = {
    "awff_pid": "Models/MoSimQuadrotorModel/Experiment/SingleUav/IntegratedChains/AwffPidGraphicalRunner.mo",
    "awff_l1_residual": "Models/MoSimQuadrotorModel/Experiment/SingleUav/IntegratedChains/AwffL1ResidualGraphicalRunner.mo",
    "awff_l1_indi": "Models/MoSimQuadrotorModel/Experiment/SingleUav/IntegratedChains/AwffL1IndiGraphicalRunner.mo",
    "linear_mpc_l1_indi": "Models/MoSimQuadrotorModel/Experiment/SingleUav/IntegratedChains/LinearMpcL1IndiGraphicalRunner.mo",
    "qp_nmpc_l1_indi_cbf": "Models/MoSimQuadrotorModel/Experiment/SingleUav/IntegratedChains/QpNmpcL1IndiCbfGraphicalRunner.mo",
    "pid_awff_linear_eso": "Models/MoSimQuadrotorModel/Experiment/SingleUav/AwffControllers/PidAwffLinearEsoGraphicalRunner.mo",
    "linear_mpc": "Models/MoSimQuadrotorModel/Experiment/SingleUav/LinearMpc/LinearMpcGraphicalRunner.mo",
}

ANCHORS = {
    "reference": (-380, 185),
    "fault_compensator": (320, 5),
    "esc": (190, 5),
    "battery": (55, 5),
    "motor1": (465, 220),
    "motor2": (465, 142),
    "motor3": (465, 64),
    "motor4": (465, -14),
    "plant": (650, 100),
    "perception": (-380, 5),
    "flight_controller": (-95, 5),
    "mission_computer": (-235, 5),
}

CONNECT_RE = re.compile(r"\bconnect\s*\(")
POINT_RE = re.compile(r"\{\s*(-?[0-9.]+)\s*,\s*(-?[0-9.]+)\s*\}")
ORIGIN_RE = re.compile(
    r"\b(?P<name>reference|fault_compensator|esc|battery|motor[1-4]|plant|"
    r"perception|flight_controller|mission_computer)\b.*?"
    r"origin\s*=\s*\{\s*(?P<x>-?[0-9.]+)\s*,\s*(?P<y>-?[0-9.]+)",
    re.DOTALL,
)


def pascal(value: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in value.split("_") if part)


def entry_path(row: dict[str, Any]) -> Path:
    scheme_id = str(row["scheme_id"])
    relative = SPECIAL_PATHS.get(scheme_id)
    if relative is None:
        family = FAMILY_DIRS[str(row["implementation_package"])]
        relative = (
            f"Models/MoSimQuadrotorModel/Experiment/{family}/"
            f"{pascal(scheme_id)}GraphicalRunner.mo"
        )
    return ROOT / relative


def statement_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for match in CONNECT_RE.finditer(text):
        depth = 0
        quote: str | None = None
        escaped = False
        end = None
        for index in range(match.end() - 1, len(text)):
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
                end = index + 1
                break
        if end is None:
            raise ValueError(f"unterminated connect statement at offset {match.start()}")
        spans.append((match.start(), end))
    return spans


def connect_args(statement: str) -> tuple[str, str]:
    start = statement.find("(") + 1
    depth = 0
    for index in range(start, len(statement)):
        character = statement[index]
        if character == "(":
            depth += 1
        elif character == ")":
            if depth == 0:
                inner = statement[start:index]
                split_depth = 0
                for split in range(len(inner)):
                    if inner[split] in "([{":
                        split_depth += 1
                    elif inner[split] in ")]}":
                        split_depth -= 1
                    elif inner[split] == "," and split_depth == 0:
                        return inner[:split].strip(), inner[split + 1 :].strip()
                break
            depth -= 1
    raise ValueError(f"cannot split connect arguments: {statement[:100]}")


def signal_index(value: str, fallback: int) -> int:
    match = re.search(r"\[([1-4])\]", value)
    return int(match.group(1)) if match else fallback


def points_for(src: str, dst: str, order: int) -> tuple[str, tuple[int, int, int]]:
    index = signal_index(src + dst, ((order - 1) % 4) + 1)
    motor_y = {1: 220, 2: 142, 3: 64, 4: -14}[index]

    if (src.startswith("core.") or src.startswith("controller.")) and dst.startswith("output_adapter."):
        y = 230 - (index - 1) * 28
        return f"{{{{15,{y}}},{{40,{y}}},{{40,{y - 8}}},{{58,{y - 8}}}}}", (55, 80, 115)
    if src.startswith("output_adapter.") and dst.startswith("fault_compensator.command_in"):
        y = 130 - (index - 1) * 18
        return f"{{{{158,{y}}},{{205,{y}}},{{205,{5 + (4 - index) * 10}}},{{270,{5 + (4 - index) * 10}}}}}", (55, 80, 115)
    if src.startswith("controller_core.") and dst.startswith("fault_compensator.command_in"):
        y = 230 - (index - 1) * 24
        return f"{{{{15,{y}}},{{205,{y}}},{{205,{5 + (4 - index) * 10}}},{{270,{5 + (4 - index) * 10}}}}}", (55, 80, 115)
    if src.startswith("fault_compensator.command_out") and dst.startswith("esc.motor_command_raw"):
        y = 30 - (index - 1) * 10
        return f"{{{{370,{y}}},{{245,{y}}},{{245,{y - 18}}},{{140,{y - 18}}}}}", (55, 80, 115)
    if src.startswith("esc.motor_command[") and dst.endswith(".command"):
        return f"{{{{240,{30 - (index - 1) * 10}}},{{300,{30 - (index - 1) * 10}}},{{300,{motor_y}}},{{436,{motor_y}}}}}", (55, 80, 115)
    if src.startswith("motor") and src.endswith(".command_to_plant"):
        return f"{{{{494,{motor_y}}},{{522,{motor_y}}}}}", (55, 80, 115)
    if src.startswith("plant.rotor_speed[") and dst.startswith("motor"):
        return f"{{{{777,{motor_y}}},{{805,{motor_y}}},{{805,-120}},{{410,-120}},{{410,{motor_y}}},{{494,{motor_y}}}}}", (130, 0, 130)
    if src.startswith("battery.") and dst.startswith("esc."):
        y = 30 if src.endswith("bus_voltage") else 20
        return f"{{{{105,{y}}},{{140,{y}}}}}", (80, 80, 80)
    if src == "plant.position" and dst == "perception.position_raw":
        return "{{522,150},{700,150},{700,-100},{-400,-100},{-400,30},{-430,30}}", (0, 100, 150)
    if src.startswith("perception.") and dst.startswith("flight_controller."):
        y = 30 if src.endswith("gps_position") else -20
        return f"{{{{-330,{y}}},{{-145,{y}}}}}", (0, 100, 150)
    if src == "plant.attitude" and dst == "flight_controller.attitude_raw":
        return "{{777,191},{820,191},{820,-80},{-170,-80},{-170,15},{-145,15}}", (0, 100, 150)
    if src == "plant.rotor_speed" and dst == "flight_controller.motor_speed_raw":
        return "{{777,161},{840,161},{840,-90},{-180,-90},{-180,-5},{-145,-5}}", (130, 0, 130)
    if src.startswith("perception.") and dst.startswith("mission_computer."):
        y = 10 if src.endswith("local_position") else -5
        return f"{{{{-330,{y}}},{{-285,{y}}}}}", (0, 100, 150)
    if src.startswith("flight_controller.") and dst.startswith("mission_computer."):
        y = 25 if src.endswith("position_est") else -15
        return f"{{{{-45,{y}}},{{-30,{y}}},{{-30,-60}},{{-300,-60}},{{-300,{y}}},{{-285,{y}}}}}", (100, 70, 20)
    if dst.startswith(("core.", "controller.", "controller_core.")):
        target_y = 240 - ((order - 1) % 8) * 14
        if src.startswith("reference."):
            return f"{{{{-330,{target_y}}},{{-300,{target_y}}},{{-300,{target_y}}},{{-145,{target_y}}}}}", (0, 0, 127)
        if src.startswith("mission_computer."):
            return f"{{{{-185,{target_y}}},{{-165,{target_y}}},{{-165,{target_y}}},{{-145,{target_y}}}}}", (0, 0, 127)
        if src.startswith("flight_controller."):
            return f"{{{{-45,{target_y}}},{{-20,{target_y}}},{{-20,-100}},{{-220,-100}},{{-220,{target_y}}},{{-145,{target_y}}}}}", (0, 100, 150)
        return f"{{{{777,191}},{{820,191}},{{820,-100}},{{-220,-100}},{{-220,{target_y}}},{{-145,{target_y}}}}}", (0, 100, 150)
    if src.startswith("reference.") and dst.startswith("mission_computer."):
        return "{{-330,220},{-300,220},{-300,80},{-285,80}}", (0, 0, 127)
    y = 260 - (order % 12) * 18
    return f"{{{{-100,{y}}},{{0,{y}}},{{0,{y - 10}}},{{100,{y - 10}}}}}", (0, 0, 127)


def line_replacement(statement: str, points: str, color: tuple[int, int, int]) -> str:
    color_text = "{" + ",".join(str(value) for value in color) + "}"
    line_text = f"Line(points={points}, color={color_text})"
    match = re.search(r"\bLine\s*\(", statement)
    if match:
        depth = 0
        end = None
        for index in range(match.end() - 1, len(statement)):
            if statement[index] == "(":
                depth += 1
            elif statement[index] == ")":
                depth -= 1
                if depth == 0:
                    end = index + 1
                    break
        if end is None:
            raise ValueError("unterminated Line annotation")
        return statement[: match.start()] + line_text + statement[end:]
    return statement[:-1].rstrip() + f" annotation({line_text});"


def repair_text(text: str) -> tuple[str, int]:
    replacements: list[tuple[int, int, str]] = []
    for order, (start, end) in enumerate(statement_spans(text), start=1):
        statement = text[start:end]
        src, dst = connect_args(statement)
        points, color = points_for(src, dst, order)
        replacements.append((start, end, line_replacement(statement, points, color)))
    repaired = text
    for start, end, replacement in reversed(replacements):
        repaired = repaired[:start] + replacement + repaired[end:]
    return repaired, len(replacements)


def audit_file(row: dict[str, Any], path: Path) -> dict[str, Any]:
    failures: list[str] = []
    relative = path.relative_to(ROOT).as_posix()
    if not path.is_file():
        return {"scheme_id": row["scheme_id"], "path": relative, "ok": False, "failures": ["missing source file"]}
    text = path.read_text(encoding="utf-8")
    spans = statement_spans(text)
    statements = [text[start:end] for start, end in spans]
    visible = 0
    placeholder = 0
    for statement in statements:
        match = re.search(r"\bLine\s*\((.*?)\)", statement, re.DOTALL)
        if match is None:
            continue
        visible += 1
        points = POINT_RE.findall(match.group(1))
        if "{-440," in match.group(1) and "{-120," in match.group(1):
            placeholder += 1
        if len(points) < 2 or len(set(points)) == 1:
            failures.append("degenerate Line annotation")
    if len(statements) == 0:
        failures.append("no connect() statements")
    if visible != len(statements):
        failures.append(f"visible Line annotations {visible}/{len(statements)}")
    if placeholder:
        failures.append(f"placeholder baseline routes: {placeholder}")
    if "StopTime = 50" not in text:
        failures.append("missing 50 s experiment annotation")
    for name, (expected_x, expected_y) in ANCHORS.items():
        match = re.search(
            rf"(?m)^\s*[A-Za-z0-9_.]+\s+{re.escape(name)}\b.*?"
            rf"origin\s*=\s*\{{\s*(-?[0-9.]+)\s*,\s*(-?[0-9.]+)",
            text,
            re.DOTALL,
        )
        if match is None:
            failures.append(f"missing layout anchor: {name}")
        elif (float(match.group(1)), float(match.group(2))) != (expected_x, expected_y):
            failures.append(f"layout anchor drift: {name}")
    required_families = (
        "fault_compensator.command_in[1]",
        "fault_compensator.command_out[1]",
        "esc.motor_command_raw[1]",
        "motor1.command_to_plant",
        "plant.rotor_speed[1]",
        "plant.position, perception.position_raw",
        "perception.gps_position, flight_controller.gps_position",
        "plant.attitude, flight_controller.attitude_raw",
    )
    for token in required_families:
        if not any(token in statement for statement in statements):
            failures.append(f"missing common chain token: {token}")
    return {
        "scheme_id": row["scheme_id"],
        "path": relative,
        "connect_count": len(statements),
        "visible_line_count": visible,
        "placeholder_route_count": placeholder,
        "ok": not failures,
        "failures": sorted(set(failures)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="rewrite current runner Line annotations")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    catalog = json.loads(CATALOG.read_text(encoding="utf-8-sig"))
    rows = [row for row in catalog["schemes"] if row["scheme_id"] not in {"official_pid", "px4ctrl"}]
    changed: list[str] = []
    if args.write:
        for row in rows:
            path = entry_path(row)
            if not path.is_file():
                continue
            before = path.read_text(encoding="utf-8")
            after, _ = repair_text(before)
            if after != before:
                path.write_text(after, encoding="utf-8", newline="\n")
                changed.append(path.relative_to(ROOT).as_posix())
    entries = [audit_file(row, entry_path(row)) for row in sorted(rows, key=lambda item: item["scheme_id"])]
    summary = {
        "schema": "mosim.controller_family_layout.v1",
        "source": "static_model_contract",
        "controller_count": len(rows),
        "changed_paths": changed,
        "passed": sum(1 for entry in entries if entry["ok"]),
        "failed": sum(1 for entry in entries if not entry["ok"]),
        "ok": len(rows) == 46 and all(entry["ok"] for entry in entries),
        "entries": entries,
    }
    payload = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    if args.json_output:
        output = args.json_output if args.json_output.is_absolute() else ROOT / args.json_output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
