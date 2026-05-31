#!/usr/bin/env python3
"""Smoke test shared CoAgent evidence refresh command planning."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.evidence import evidence_manifest
from CoAgent.evidence.refresh_commands import standard_refresh_commands, standard_refresh_steps
from CoAgent.review_package import review_package
from CoAgent.status_export import status_export


def main() -> int:
    task_id = "coagent_refresh_commands_smoke"
    commands = standard_refresh_commands(task_id)
    labels = [step.label for step in standard_refresh_steps(task_id)]

    assert commands == evidence_manifest.refresh_commands(task_id)
    assert commands == status_export.evidence_refresh_commands(task_id)
    assert commands == review_package.evidence_refresh_commands(task_id)

    assert labels == [
        "quick_doctor",
        "full_doctor",
        "git_handoff",
        "closeout_verification",
        "task_health",
        "status_resume",
        "evidence_manifest",
        "review_package",
    ], labels
    assert "coagent_doctor.py --mode quick" in commands[0]
    assert "coagent_doctor.py --mode full" in commands[1]
    assert "evidence_manifest.py" in commands[-2]
    assert "review_package.py" in commands[-1]
    assert all(task_id in command or "coagent_doctor.py" in command for command in commands)

    print("evidence_refresh_commands_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
