#!/usr/bin/env python3
"""Validate that COAGENT-MINILOOP-03 is no longer a visible-thread proof."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "Results" / "coagent_miniloop" / "COAGENT-MINILOOP-03"

REQUIRED_FILES = [
    "scoped_task_packet.md",
    "worker_result_packet.json",
]


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check() -> dict[str, Any]:
    missing = [name for name in REQUIRED_FILES if not (BUNDLE / name).exists()]
    require(not missing, f"missing files: {missing}")

    result = load_json(BUNDLE / "worker_result_packet.json")
    require(result.get("task_id") == "COAGENT-MINILOOP-03", "worker result task_id mismatch")
    require(result.get("canonical_status") == "completed", "worker result not completed")
    require(result.get("owner") == "COAGENT-MINILOOP-03-VISIBLE-RESUME", "worker owner mismatch")
    require(result.get("acceptance_state") == "met", "acceptance state not met")

    summary = ROOT / "Results" / "agent_packets" / "summaries" / "COAGENT-MINILOOP-03.summary.md"
    require(summary.exists(), "missing result router summary")
    summary_text = summary.read_text(encoding="utf-8")
    require("review_status: `accepted`" in summary_text, "router summary does not show accepted")
    require("runtime_state: `done`" in summary_text, "router summary does not show runtime done")

    transport_run = ROOT / "Results" / "coagent_transport" / "runs" / "COAGENT-MINILOOP-03.json"
    require(transport_run.exists(), "missing transport run metadata")
    run = load_json(transport_run)
    require(run.get("thread_id") == "019e62b1-a1d3-74c2-853c-85c510e41f59", "unexpected resumable rollout thread id")
    require(run.get("department") == "TestOwner", "unexpected target department")

    graph = load_json(ROOT / "CoAgent" / "dispatch" / "department_threads.json")
    test_owner = next(item for item in graph["threads"] if item["department"] == "TestOwner")
    require(test_owner["status"] == "inactive_ui_deleted", "TestOwner must not be dispatchable")

    return {
        "ok": True,
        "task_id": "COAGENT-MINILOOP-03",
        "state": "superseded_not_visible",
        "department": "TestOwner",
        "thread_id": run["thread_id"],
        "files_checked": len(REQUIRED_FILES),
        "limitation": "The historical rollout file was resumable, but the user confirmed the department UI conversation had been deleted. This is not accepted as a visible department communication proof.",
    }


def main() -> int:
    print(json.dumps(check(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
