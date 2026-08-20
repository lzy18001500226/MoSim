#!/usr/bin/env python3
"""Audit the 46 graphical Experiment family entries against the frozen map.

This is a source/static gate. It proves that the public family entries point
to the archived graphical controller cores (or an official Sysblock whole-
aircraft chain), that the common aircraft template is wired, and that the
APP keeps its two legacy active controller ids. It does not replace MWORKS
``check_model``, diagram review, or a 50 s simulation.
"""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "Config" / "control_platform" / "control_scheme_catalog.json"
APP_PATH = ROOT / "Config" / "control_platform" / "mworks_app_entrypoints.json"
TASK_ROUTE_PATH = ROOT / "Config" / "control_platform" / "model_studio_task_routes_v1.toml"
EXPERIMENT_ROOT = ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment"
BASELINE_IDS = {"official_pid", "px4ctrl"}

CONNECT_RE = re.compile(r"\bconnect\s*\(", re.MULTILINE)
MODEL_RE = re.compile(r"^\s*model\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\b", re.MULTILINE)
EXTENDS_RE = re.compile(r"^\s*extends\s+(?P<name>[A-Za-z_][A-Za-z0-9_.]*)\s*;", re.MULTILINE)
NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
POINT_RE = re.compile(rf"\{{\s*({NUMBER})\s*,\s*({NUMBER})\s*\}}")


def pascal(value: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in value.split("_") if part)


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


def check_required_connections(
    text: str,
    required: list[str],
    *,
    require_visible_line: bool = True,
) -> list[str]:
    """Return missing connection tokens while preserving the line contract."""
    statements = connection_statements(text)
    failures: list[str] = []
    for token in required:
        statement = next((item for item in statements if token in item), None)
        if statement is None:
            failures.append(f"missing connection: {token}")
        elif require_visible_line and not visible_line_ok(statement):
            failures.append(f"connection without non-degenerate Line: {token}")
    return failures


def modelica_path_from_fqn(fqn: str) -> str:
    prefix = "MoSimQuadrotorModel."
    if not fqn.startswith(prefix):
        raise ValueError(f"unsupported Modelica FQN: {fqn}")
    return "Models/MoSimQuadrotorModel/" + fqn[len(prefix) :].replace(".", "/") + ".mo"


def load_documents() -> tuple[dict[str, Any], dict[str, Any]]:
    model_map = json.loads(MAP_PATH.read_text(encoding="utf-8-sig"))
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8-sig"))
    if not isinstance(model_map.get("schemes"), list):
        raise ValueError("current model map schemes must be a list")
    if not isinstance(catalog.get("schemes"), list):
        raise ValueError("control scheme catalog schemes must be a list")
    return model_map, {str(row["scheme_id"]): row for row in catalog["schemes"]}


def runner_spec(route: dict[str, Any]) -> dict[str, str]:
    scheme_id = str(route["controller_id"])
    runner_class = str(route["runner_class"])
    runner_name = runner_class.rsplit(".", 1)[-1]
    runner_file = str(route["runner_file"])
    package_dir = str(Path(runner_file).parent).replace("\\", "/")
    return {
        "package_dir": package_dir,
        "runner_name": runner_name,
        "path": runner_file,
        "class": runner_class,
        "scheme_id": scheme_id,
    }


def core_source_check(scheme_id: str, core_model: str | None) -> dict[str, Any]:
    """Check the public controller core as a real visible Sysblock surface."""

    if not core_model:
        return {
            "scheme_id": scheme_id,
            "model": None,
            "path": None,
            "ok": False,
            "failures": ["current Runner has no resolvable Control core"],
        }

    relative_path = modelica_path_from_fqn(core_model)
    try:
        text = read(relative_path)
    except ValueError as error:
        return {
            "scheme_id": scheme_id,
            "model": core_model,
            "path": relative_path,
            "ok": False,
            "failures": [str(error)],
        }

    model_name = core_model.rsplit(".", 1)[-1]
    statements = connection_statements(text)
    failures: list[str] = []
    if not re.search(rf"^\s*(?:model|block)\s+{re.escape(model_name)}\b", text, re.MULTILINE):
        failures.append(f"core declaration missing: {model_name}")
    if "SysblockVersion" not in text:
        failures.append("core SysblockVersion metadata missing")
    if "BlockSystem(blockKind=BlockKind.userModel" not in text:
        failures.append("core BlockSystem(userModel) metadata missing")
    if not statements:
        failures.append("core has no visible connect() statements")
    invalid = [index for index, statement in enumerate(statements, start=1) if not visible_line_ok(statement)]
    if invalid:
        failures.append("core connections without non-degenerate Line annotations: " + ", ".join(map(str, invalid)))
    return {
        "scheme_id": scheme_id,
        "model": core_model,
        "path": relative_path,
        "connect_count": len(statements),
        "visible_line_count": len(statements) - len(invalid),
        "ok": not failures,
        "failures": failures,
    }


def runner_source_check(route: dict[str, Any], spec: dict[str, str]) -> dict[str, Any]:
    failures: list[str] = []
    relative_path = spec["path"]
    try:
        text = read(relative_path)
    except ValueError as error:
        return {"scheme_id": route["controller_id"], "path": relative_path, "ok": False, "failures": [str(error)]}
    model_name = spec["runner_name"]
    if not re.search(rf"^\s*model\s+{re.escape(model_name)}\b", text, re.MULTILINE):
        failures.append(f"runner declaration missing: {model_name}")
    if "StopTime = 50" not in text:
        failures.append("50 s review experiment annotation missing")
    failures.extend(runner_connection_check(text))
    if route.get("harness_kind") != "experiment_family_graphical_runner":
        failures.append(f"unexpected harness kind: {route.get('harness_kind')}")
    core_matches = re.findall(
        r"(MoSimQuadrotorModel\.Control\.[A-Za-z0-9_.]+)\s+(?:core|controller|controller_core)\b",
        text,
    )
    if not core_matches:
        failures.append("current Runner has no explicit Control core/controller instance")
    core_model = core_matches[0] if core_matches else None
    core_graphics = core_source_check(route["controller_id"], core_model)
    failures.extend(f"core: {failure}" for failure in core_graphics["failures"])
    return {
        "scheme_id": route["controller_id"],
        "path": relative_path,
        "runner_class": spec["class"],
        "core_model": core_model,
        "core_graphics": core_graphics,
        "connect_count": len(connection_statements(text)),
        "ok": not failures,
        "failures": failures,
    }


def runner_connection_check(text: str) -> list[str]:
    failures: list[str] = []
    statements = connection_statements(text)
    invalid = [index for index, statement in enumerate(statements, start=1) if not visible_line_ok(statement)]
    if invalid:
        failures.append("connections without non-degenerate Line annotations: " + ", ".join(map(str, invalid)))
    output_route = (
        "output_adapter.rotor_command[1]",
        "output_adapter.rotor_command[2]",
        "output_adapter.rotor_command[3]",
        "output_adapter.rotor_command[4]",
    )
    direct_route = (
        "controller_core.y",
        "controller_core.y1",
        "controller_core.y2",
        "controller_core.y3",
    )
    if all(any(token in statement for statement in statements) for token in output_route):
        route_requirements = tuple(
            f"connect(output_adapter.rotor_command[{index}], fault_compensator.command_in[{index}])"
            for index in range(1, 5)
        )
    elif all(any(token in statement for statement in statements) for token in direct_route):
        route_requirements = tuple(
            f"connect(controller_core.{name}, fault_compensator.command_in[{index}])"
            for index, name in enumerate(("y", "y1", "y2", "y3"), start=1)
        )
    else:
        route_requirements = ("controller output to fault_compensator route",)
    required = route_requirements + (
        "connect(fault_compensator.command_out[1], esc.motor_command_raw[1])",
        "connect(motor1.command_to_plant, plant.rotor_command[1])",
        "connect(plant.rotor_speed[1], motor1.speed)",
        "connect(plant.position, perception.position_raw)",
    )
    for token in required:
        if not any(token in statement for statement in statements):
            failures.append(f"missing template connection: {token}")
    return failures


def official_runner_connection_check(text: str) -> list[str]:
    required = (
        "connect(core.y, yaw_router.amplitude_in_1)",
        "connect(core.y1, yaw_router.amplitude_in_2)",
        "connect(core.y2, yaw_router.amplitude_in_3)",
        "connect(core.y3, yaw_router.amplitude_in_4)",
        "connect(yaw_router.amplitude_out_1, mapper.amplitude_1)",
        "connect(yaw_router.amplitude_out_2, mapper.amplitude_2)",
        "connect(yaw_router.amplitude_out_3, mapper.amplitude_3)",
        "connect(yaw_router.amplitude_out_4, mapper.amplitude_4)",
        "connect(mapper.rotor_command_1, fault_compensator.command_in[1])",
        "connect(fault_compensator.command_out[1], esc.motor_command_raw[1])",
        "connect(motor1.command_to_plant, plant.rotor_command[1])",
        "connect(plant.rotor_speed[1], motor1.speed)",
        "connect(plant.position, perception.position_raw)",
    )
    return check_required_connections(text, list(required))


def package_check(specs: list[dict[str, str]]) -> dict[str, Any]:
    failures: list[str] = []
    expected_by_package: dict[str, set[str]] = {}
    for spec in specs:
        expected_by_package.setdefault(spec["package_dir"], set()).add(spec["runner_name"])
    for package_dir, expected in expected_by_package.items():
        relative_path = f"{package_dir}/package.order"
        try:
            entries = {line.strip() for line in read(relative_path).splitlines() if line.strip()}
        except ValueError as error:
            failures.append(str(error))
            continue
        for name in sorted(expected - entries):
            failures.append(f"{relative_path}: missing entry {name}")
    return {"ok": not failures, "expected_entries": {key: sorted(value) for key, value in expected_by_package.items()}, "failures": failures}


def app_policy_check() -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    contract = json.loads(APP_PATH.read_text(encoding="utf-8-sig"))
    policy = contract.get("entry_policy", {})
    if policy.get("active_entry_mode") != "current_graphical_runner_batch":
        failures.append("APP active_entry_mode is not current_graphical_runner_batch")
    if policy.get("new_semantic_entries_complete") is not False:
        failures.append("APP semantic catalog gate is no longer deferred")
    if policy.get("new_semantic_entry_count") != 48:
        failures.append("APP semantic entry count changed from 48")
    expected_ids = {str(row["scheme_id"]) for row in json.loads(CATALOG_PATH.read_text(encoding="utf-8-sig"))["schemes"]}
    active_ids = set(policy.get("active_controller_ids", []))
    if active_ids != expected_ids:
        failures.append("APP active_controller_ids do not cover the 48-entry catalog")
    entries = {entry.get("entry_id"): entry for entry in contract.get("review_entrypoints", [])}
    for entry_id in ("sunray150_assembly", "official_pid_baseline"):
        if entry_id not in entries:
            failures.append(f"APP review entry missing: {entry_id}")
    official = entries.get("official_pid_baseline", {})
    for key in ("runner_file", "controller_review_file"):
        value = official.get(key)
        if not isinstance(value, str) or not repo_path(value).is_file():
            failures.append(f"APP official PID asset missing: {key}")
    for value in official.get("existing_result_roots", []):
        if not (ROOT / value).is_dir():
            warnings.append(f"APP historical result root is absent in this worktree: {value}")
    return {"ok": not failures, "warnings": warnings, "active_controller_ids": policy.get("active_controller_ids"), "failures": failures}


def run_checks() -> dict[str, Any]:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8-sig"))
    catalog_by_id = {str(row["scheme_id"]): row for row in catalog["schemes"]}
    task_routes = tomllib.loads(TASK_ROUTE_PATH.read_text(encoding="utf-8"))
    routes = {str(row["controller_id"]): row for row in task_routes.get("route", [])}
    rows = [row for scheme_id, row in catalog_by_id.items() if scheme_id not in BASELINE_IDS]
    failures: list[str] = []
    entries: list[dict[str, Any]] = []
    specs: list[dict[str, str]] = []
    for row in sorted(rows, key=lambda item: str(item["scheme_id"])):
        scheme_id = str(row["scheme_id"])
        route = routes.get(scheme_id)
        if route is None or not bool(route.get("available")):
            failures.append(f"{scheme_id}: current task route is unavailable")
            continue
        spec = runner_spec(route)
        specs.append(spec)
        source_result = runner_source_check(route, spec)
        runner_result = {
            "scheme_id": scheme_id,
            "path": spec["path"],
            "kind": "current_graphical_runner",
            "ok": source_result["ok"],
            "failures": source_result["failures"],
        }
        for failure in source_result.get("failures", []):
            failures.append(f"{scheme_id}: runner: {failure}")
        for failure in runner_result.get("failures", []):
            if f"{scheme_id}: runner: {failure}" not in failures:
                failures.append(f"{scheme_id}: runner: {failure}")
        entries.append(
            {
                "scheme_id": scheme_id,
                "source": source_result,
                "core": source_result.get("core_graphics"),
                "runner": runner_result,
            }
        )
    packages = package_check(specs)
    failures.extend(f"package: {failure}" for failure in packages["failures"])
    app = app_policy_check()
    failures.extend(f"app: {failure}" for failure in app["failures"])
    return {
        "schema": "mosim.experiment_graphical_family_entries.v1",
        "status": "pass" if not failures else "fail",
        "ok": not failures,
        "family_entry_count": len(rows),
        "graphical_core_count": sum(row.get("current_model_role") == "graphical_controller_core" for row in rows),
        "full_profile_count": sum(row.get("current_model_role") == "full_profile_whole_aircraft_closed_loop" for row in rows),
        "planned_included": [str(row["scheme_id"]) for row in rows if row.get("implementation_status") == "planned"],
        "entries": entries,
        "package_registration": packages,
        "app_policy": app,
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args(argv)
    try:
        summary = run_checks()
    except (OSError, ValueError, KeyError, json.JSONDecodeError, re.error) as error:
        summary = {
            "schema": "mosim.experiment_graphical_family_entries.v1",
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
