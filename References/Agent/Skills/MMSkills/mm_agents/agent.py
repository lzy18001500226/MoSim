"""Minimal OSWorld agent compatibility helpers used by MMSkills.

This repository ships the MMSkills general visual-agent integration layer, not the full
OSWorld agent zoo.  The full OSWorld project provides a much larger
``mm_agents.agent`` module; the MMSkills files only need the response parsing
helpers below when imported outside an OSWorld checkout.
"""

from __future__ import annotations

import ast
import json
import re
from typing import Any


def parse_actions_from_string(input_string: str) -> list[Any] | str:
    """Parse OSWorld JSON-style action responses."""
    if input_string.strip() in ["WAIT", "DONE", "FAIL"]:
        return [input_string.strip()]

    matches = re.findall(r"```json\s+(.*?)\s+```", input_string, re.DOTALL)
    if not matches:
        matches = re.findall(r"```\s+(.*?)\s+```", input_string, re.DOTALL)

    if matches:
        try:
            return [json.loads(match) for match in matches]
        except json.JSONDecodeError as exc:
            return f"Failed to parse JSON: {exc}"

    return [json.loads(input_string)]


def parse_code_from_string(input_string: str) -> list[str]:
    """Parse Python/pyautogui actions from fenced model responses."""
    if input_string.strip() in ["WAIT", "DONE", "FAIL"]:
        return [input_string.strip()]

    pattern = r"```(?:\w+\s+)?(.*?)```"
    matches = re.findall(pattern, input_string, re.DOTALL)
    codes: list[str] = []

    def has_executable_python_body(snippet: str) -> bool:
        stripped = snippet.strip()
        if not stripped:
            return False
        try:
            tree = ast.parse(stripped)
        except SyntaxError:
            return any(line.strip() and not line.strip().startswith("#") for line in stripped.splitlines())
        return len(tree.body) > 0

    for match in matches:
        match = match.strip()
        commands = ["WAIT", "DONE", "FAIL"]
        if match in commands:
            codes.append(match)
            continue
        last_line = match.split("\n")[-1]
        if last_line in commands:
            prefix = "\n".join(match.split("\n")[:-1])
            if has_executable_python_body(prefix):
                codes.append(prefix)
            codes.append(last_line)
        elif has_executable_python_body(match):
            codes.append(match)

    return codes


class PromptAgent:
    """Placeholder for OSWorld's baseline PromptAgent.

    Use the original OSWorld package when running non-MMSkills baselines.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise ImportError(
            "MMSkills only vendors the general/MMSkills integration layer. "
            "Run OSWorld from an OSWorld checkout for PromptAgent baselines."
        )
