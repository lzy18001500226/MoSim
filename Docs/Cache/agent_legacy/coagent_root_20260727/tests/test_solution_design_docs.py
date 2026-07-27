#!/usr/bin/env python3
"""Smoke test for CoAgent solution synthesis docs and templates."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.doctor.check_solution_design import main


def test_solution_design_docs_and_templates() -> None:
    assert main() == 0
