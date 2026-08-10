#!/usr/bin/env python3
"""Check the source-level surface of a strict graphical controller route.

This is a source gate only. It does not prove MWORKS loading, GUI layout,
CheckModel, simulation, numerical equivalence, or whole-aircraft acceptance.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_CORE_TOKENS = ("CFunction", "EquationBridge", "external ")
FORBIDDEN_ADAPTER_CORE_TOKENS = (
    "OfficialPidCoreSysblock",
    "Vehicle.Blocks.Controller.Controller",
)
NATIVE_CORE_TOKENS = (
    "extends ModelWorkspace",
    "SysplorerEmbeddedCoder.Port.Inport",
    "SysplorerEmbeddedCoder.Port.Outport",
)
IDENTIFIER = r"[A-Za-z_]\w*"
INDEX = r"(?:\s*\[[^\[\]]+\])*"
ENDPOINT = rf"{IDENTIFIER}{INDEX}(?:\s*\.\s*{IDENTIFIER}{INDEX})*"
CONNECT_RE = re.compile(
    rf"\bconnect\s*\(\s*{ENDPOINT}\s*,\s*{ENDPOINT}\s*\)",
    re.MULTILINE,
)
NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
POINT_RE = re.compile(rf"\{{\s*({NUMBER})\s*,\s*({NUMBER})\s*\}}")


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
    raise ValueError("cannot locate statement terminator")


def token_call_span(text: str, token: str, start: int, end: int) -> tuple[int, int] | None:
    match = re.compile(rf"\b{re.escape(token)}\s*\(").search(text, start, end)
    if match is None:
        return None
    open_paren = text.find("(", match.start(), end)
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(open_paren, end):
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
            if depth == 0:
                return match.start(), index + 1
    raise ValueError(f"unbalanced {token}() annotation")


def read_repo_file(value: str) -> tuple[Path, str]:
    path = (ROOT / value).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as error:
        raise ValueError(f"path outside repository: {value}") from error
    if not path.is_file():
        raise ValueError(f"missing source file: {value}")
    return path, path.read_text(encoding="utf-8")


def check_model_declared(text: str, model_name: str, label: str, errors: list[str]) -> None:
    if not re.search(rf"\bmodel\s+{re.escape(model_name)}\b", text):
        errors.append(f"{label}: model declaration not found: {model_name}")


def check_sysblock_metadata(text: str, label: str, errors: list[str]) -> None:
    required = ("__MWORKS", "SysblockVersion", "BlockSystem")
    for token in required:
        if token not in text:
            errors.append(f"{label}: missing Sysblock metadata: {token}")
    if not re.search(r"\bmodelType\s*=\s*Control\b", text):
        errors.append(f"{label}: missing Sysblock metadata: modelType=Control")


def check_graphical_surface(text: str, label: str, errors: list[str]) -> None:
    connections = list(CONNECT_RE.finditer(text))
    if not connections:
        errors.append(f"{label}: no explicit connect() topology")
    if "Placement(" not in text:
        errors.append(f"{label}: no placed graphical instances")
    connect_count = len(connections)
    line_count = len(re.findall(r"annotation\s*\(\s*Line\b", text))
    if connect_count and line_count != connect_count:
        errors.append(
            f"{label}: visible Line annotation count {line_count} "
            f"does not match connect count {connect_count}"
        )
    for index, connection in enumerate(connections, start=1):
        try:
            finish = statement_end(text, connection.start())
            line_span = token_call_span(text, "Line", connection.start(), finish)
        except ValueError as error:
            errors.append(f"{label}: cannot inspect connection {index}: {error}")
            continue
        if line_span is None:
            errors.append(f"{label}: connection {index} has no visible Line annotation")
            continue
        points = [
            (float(x), float(y))
            for x, y in POINT_RE.findall(text[line_span[0] : line_span[1]])
        ]
        if len(points) < 2 or not any(point != points[0] for point in points[1:]):
            errors.append(f"{label}: connection {index} has a degenerate visible Line")


def check_core(path_value: str, base_value: str | None, model_name: str, errors: list[str]) -> None:
    _, text = read_repo_file(path_value)
    check_model_declared(text, model_name, "core", errors)
    check_sysblock_metadata(text, "core", errors)
    check_graphical_surface(text, "core", errors)
    for token in NATIVE_CORE_TOKENS:
        if token not in text:
            errors.append(f"core: missing native Sysblock structure: {token}")
    inheritance = re.findall(r"(?m)^\s*extends\s+([^;]+);", text)
    for base_class in inheritance:
        if base_class.strip() != "ModelWorkspace":
            errors.append(
                "core: strict core may not inherit a non-native Modelica controller base: "
                f"{base_class.strip()}"
            )
    if not re.search(r"SysplorerEmbeddedCoder\.(?!Port\.)", text):
        errors.append("core: no native SysplorerEmbeddedCoder processing block")
    for token in FORBIDDEN_CORE_TOKENS:
        if token in text:
            errors.append(f"core: forbidden token {token!r} in {path_value}")
    if base_value:
        errors.append("core: --core-base is not permitted for a strict native Sysblock core")


def check_adapter(path_value: str, errors: list[str]) -> None:
    _, text = read_repo_file(path_value)
    check_sysblock_metadata(text, "adapter", errors)
    check_graphical_surface(text, "adapter", errors)
    for token in FORBIDDEN_CORE_TOKENS:
        if token in text:
            errors.append(f"adapter: forbidden token {token!r} in {path_value}")
    for token in FORBIDDEN_ADAPTER_CORE_TOKENS:
        if token in text:
            errors.append(
                "adapter: strict route still instantiates a text-backed controller core: "
                f"{token}"
            )


def check_runner(
    path_value: str, base_value: str | None, errors: list[str]
) -> None:
    _, text = read_repo_file(path_value)
    effective_text = text
    inherited = False
    if base_value:
        if "extends " not in text:
            errors.append("runner: --runner-base requires an explicit extends declaration")
        else:
            _, base_text = read_repo_file(base_value)
            effective_text = text + "\n" + base_text
            inherited = True

    missing = [
        token
        for token in ("Sunray150Assembly", "connect(", "controller")
        if token not in effective_text
    ]
    if missing:
        source = "runner/base" if inherited else "runner"
        for token in missing:
            errors.append(
                f"{source}: missing whole-aircraft graphical surface token: {token}"
            )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core", required=True, help="repository-relative strict core source")
    parser.add_argument("--core-model", required=True, help="core model class name")
    parser.add_argument("--core-base", help="repository-relative source containing the inherited graphical base")
    parser.add_argument("--adapter", required=True, help="repository-relative graphical adapter source")
    parser.add_argument("--runner", required=True, help="repository-relative whole-aircraft graphical runner")
    parser.add_argument(
        "--runner-base",
        help="repository-relative inherited whole-aircraft runner source",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    errors: list[str] = []
    try:
        check_core(args.core, args.core_base, args.core_model, errors)
        check_adapter(args.adapter, errors)
        check_runner(args.runner, args.runner_base, errors)
    except ValueError as error:
        errors.append(str(error))
    if errors:
        print("STRICT_GRAPHICAL_SYSBLOCK_SURFACE=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("STRICT_GRAPHICAL_SYSBLOCK_SURFACE=PASS")
    print("claim_boundary=source_static_only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
