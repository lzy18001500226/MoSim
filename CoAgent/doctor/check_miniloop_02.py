#!/usr/bin/env python3
"""Validate the COAGENT-MINILOOP-02 real communication proof."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "Results" / "coagent_miniloop" / "COAGENT-MINILOOP-02"

REQUIRED_FILES = [
    "task_charter.yaml",
    "context_pack.yaml",
    "scoped_task_packet.md",
    "worker_result_packet.json",
    "transport_attempt.json",
    "review_packet.yaml",
    "closeout_summary.md",
    "retrospective.md",
]


def load(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    data = json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
    if not isinstance(data, dict):
        raise AssertionError(f"{path} must contain object/mapping")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check() -> dict[str, Any]:
    missing = [name for name in REQUIRED_FILES if not (BUNDLE / name).exists()]
    require(not missing, f"missing files: {missing}")

    result = load(BUNDLE / "worker_result_packet.json")
    attempt = load(BUNDLE / "transport_attempt.json")
    review = load(BUNDLE / "review_packet.yaml")

    require(result.get("task_id") == "COAGENT-MINILOOP-02", "worker result task_id mismatch")
    require(result.get("canonical_status") == "completed", "worker result not completed")
    require(result.get("owner") == "COAGENT-MINILOOP-02-WORKER", "worker owner mismatch")
    require(result.get("evidence"), "worker result missing evidence")

    require(attempt.get("session_id") == "019e72f7-7584-74d3-8933-c29fede9c384", "session id missing")
    require(attempt.get("result") == "completed", "transport attempt not completed")
    forbidden = attempt.get("forbidden_action_observations", {})
    for key in ["git_used", "mcp_used", "worktree_created", "source_files_modified"]:
        require(forbidden.get(key) is False, f"forbidden action observed: {key}")

    require(review.get("decision") == "accepted_with_concerns", "review must record accepted_with_concerns")
    require(review.get("integration_permission", {}).get("can_close_task") is True, "review must allow close")

    summary = ROOT / "Results" / "agent_packets" / "summaries" / "COAGENT-MINILOOP-02.summary.md"
    require(summary.exists(), "missing result router summary")
    summary_text = summary.read_text(encoding="utf-8")
    require("review_status: `accepted`" in summary_text, "router summary does not show accepted")
    require("runtime_state: `done`" in summary_text, "router summary does not show runtime done")

    return {
        "ok": True,
        "task_id": "COAGENT-MINILOOP-02",
        "state": "accepted_with_concerns",
        "session_id": attempt["session_id"],
        "files_checked": len(REQUIRED_FILES),
        "limitation": attempt.get("limitation", ""),
    }


def main() -> int:
    print(json.dumps(check(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
