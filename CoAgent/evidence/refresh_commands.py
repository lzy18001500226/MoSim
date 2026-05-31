#!/usr/bin/env python3
"""Shared refresh-command plan for CoAgent recovery evidence."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RefreshStep:
    label: str
    command: str


def standard_refresh_steps(task_id: str) -> list[RefreshStep]:
    """Return the standard command order for rebuilding task review evidence.

    The plan is intentionally command-only. Callers decide whether to execute
    it, write it to a package, or show it to a reviewer.
    """

    return [
        RefreshStep(
            "quick_doctor",
            "python3 CoAgent/doctor/coagent_doctor.py --mode quick --json --output Results/coagent_doctor/latest_gateway_quick.json",
        ),
        RefreshStep(
            "full_doctor",
            "python3 CoAgent/doctor/coagent_doctor.py --mode full --json --output Results/coagent_doctor/latest_gateway_full.json",
        ),
        RefreshStep(
            "git_handoff",
            (
                f"python3 CoAgent/devops/git_handoff_packet.py --task-id {task_id} "
                f"--output Results/coagent_status/{task_id}.git_handoff.json "
                f"--markdown-output Results/coagent_status/{task_id}.git_handoff.md --json"
            ),
        ),
        RefreshStep(
            "closeout_verification",
            (
                f"python3 CoAgent/review_queue/review_queue.py verify-closeout --task-id {task_id} "
                f"--output Results/agent_packets/closeouts/{task_id}.closeout_verification.json "
                f"--markdown-output Results/agent_packets/closeouts/{task_id}.closeout_verification.md --json"
            ),
        ),
        RefreshStep(
            "task_health",
            (
                f"python3 CoAgent/task_health/task_health.py --task-id {task_id} "
                f"--output Results/coagent_status/{task_id}.task_health.json "
                f"--markdown-output Results/coagent_status/{task_id}.task_health.md --json"
            ),
        ),
        RefreshStep(
            "status_resume",
            (
                f"python3 CoAgent/status_export/status_export.py --task-id {task_id} "
                f"--output Results/coagent_status/{task_id}.status.json "
                f"--markdown-output Results/coagent_status/{task_id}.status.md "
                f"--resume-output Results/coagent_status/{task_id}.resume.json "
                f"--resume-markdown-output Results/coagent_status/{task_id}.resume.md --json"
            ),
        ),
        RefreshStep(
            "evidence_manifest",
            (
                f"python3 CoAgent/evidence/evidence_manifest.py --task-id {task_id} "
                f"--output Results/coagent_status/{task_id}.evidence_manifest.json "
                f"--markdown-output Results/coagent_status/{task_id}.evidence_manifest.md --json"
            ),
        ),
        RefreshStep(
            "review_package",
            (
                f"python3 CoAgent/review_package/review_package.py --task-id {task_id} "
                f"--output Results/coagent_status/{task_id}.review_package.json "
                f"--markdown-output Results/coagent_status/{task_id}.review_package.md --json"
            ),
        ),
    ]


def standard_refresh_commands(task_id: str) -> list[str]:
    return [step.command for step in standard_refresh_steps(task_id)]
