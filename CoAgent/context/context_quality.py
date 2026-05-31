#!/usr/bin/env python3
"""Validate CoAgent context pack quality before dispatching a long task."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REQUIRED_SECTIONS = [
    "## Task Identity",
    "## Goal Stack",
    "## Objective",
    "## Definition Of Done",
    "## Read Scope",
    "## Write Scope",
    "## Current State",
    "## Required Evidence",
    "## Review And Acceptance Gate",
    "## Result Packet Path",
    "## Return Contract",
]
REQUIRED_FIELDS = [
    "project_goal:",
    "canonical_task_goal:",
    "conversation_objective:",
    "review_owner:",
    "review_status_values:",
    "acceptance_state_values:",
]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    if not (resolved == ROOT.resolve() or ROOT.resolve() in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def check_text(text: str, *, warn_chars: int, fail_chars: int) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    for section in REQUIRED_SECTIONS:
        if section not in text:
            findings.append({"severity": "fail", "field": section, "reason": "missing_required_section"})
    for field in REQUIRED_FIELDS:
        if field not in text:
            findings.append({"severity": "fail", "field": field, "reason": "missing_required_field"})
    if "none recorded" in text:
        findings.append({"severity": "warning", "field": "content", "reason": "contains_none_recorded"})
    char_count = len(text)
    if char_count > fail_chars:
        findings.append({"severity": "fail", "field": "char_count", "reason": "over_fail_budget", "value": str(char_count)})
    elif char_count > warn_chars:
        findings.append({"severity": "warning", "field": "char_count", "reason": "over_warn_budget", "value": str(char_count)})
    has_result_path = "Results/agent_packets/" in text
    if not has_result_path:
        findings.append({"severity": "fail", "field": "result_file", "reason": "missing_agent_packet_path"})
    fail_count = sum(1 for item in findings if item["severity"] == "fail")
    warning_count = sum(1 for item in findings if item["severity"] == "warning")
    return {
        "ok": fail_count == 0,
        "fail_count": fail_count,
        "warning_count": warning_count,
        "char_count": char_count,
        "findings": findings,
    }


def check_file(args: argparse.Namespace) -> dict[str, Any]:
    path = project_path(args.path)
    text = path.read_text(encoding="utf-8")
    result = check_text(text, warn_chars=args.warn_chars, fail_chars=args.fail_chars)
    result["path"] = str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--warn-chars", type=int, default=14000)
    parser.add_argument("--fail-chars", type=int, default=22000)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = check_file(args)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        status = "ok" if result["ok"] else "fail"
        print(f"context_quality {status} path={result['path']} fail={result['fail_count']} warning={result['warning_count']}")
        for finding in result["findings"]:
            print(f"{finding['severity']} {finding['field']} {finding['reason']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
