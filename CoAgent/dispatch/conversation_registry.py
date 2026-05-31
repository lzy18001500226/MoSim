#!/usr/bin/env python3
"""Helpers for CoAgent visible department conversation registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
THREADS_JSON = ROOT / "CoAgent" / "dispatch" / "department_threads.json"


def load_registry(path: Path = THREADS_JSON) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_registry(data: dict[str, Any], path: Path = THREADS_JSON) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_thread_by_department(department: str, path: Path = THREADS_JSON) -> dict[str, Any]:
    data = load_registry(path)
    for item in data["threads"]:
        if item["department"] == department:
            return item
    raise KeyError(department)
