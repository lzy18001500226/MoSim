#!/usr/bin/env python3
"""Smoke test the read-only CoAgent Git batch planner."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.devops import git_batch_plan


def main() -> int:
    assert git_batch_plan.classify("CoAgent/runtime/mosim_agent_runtime.py") == "runtime_protocol_bootstrap"
    assert git_batch_plan.classify("CoAgent/protocol/task_packet_schema.json") == "runtime_protocol_bootstrap"
    assert git_batch_plan.classify("CoAgent/dispatch/dispatch_helper.py") == "dispatch_transport_context_memory"
    assert git_batch_plan.classify("CoAgent/status_export/status_export.py") == "review_gateway_status"
    assert git_batch_plan.classify("CoAgent/doctor/coagent_doctor.py") == "guardrails_doctor_automation"
    assert git_batch_plan.classify("CoAgent/tests/test_git_batch_plan.py") == "tests"
    plan = git_batch_plan.build_plan()
    assert plan["ok"], plan
    assert isinstance(plan["batches"], list), plan
    assert plan["total_file_count"] >= 1, plan
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        outputs = git_batch_plan.write_batch_lists(Path(tmp) / "lists", plan)
        assert outputs["directory"].startswith("Results/tmp/")
        assert outputs["overlap"].endswith("overlap.paths")
        for paths in outputs["batches"].values():
            assert paths["all"].endswith(".paths")
            assert paths["staged"].endswith(".staged.paths")
            assert paths["worktree"].endswith(".worktree.paths")
    print("git_batch_plan_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
