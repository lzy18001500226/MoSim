#!/usr/bin/env python3
"""Smoke test split commit apply planning without updating refs."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.devops import git_batch_plan
from CoAgent.devops import git_split_commit_apply


def main() -> int:
    plan = git_batch_plan.build_plan()
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        lists = git_batch_plan.write_batch_lists(tmp_root / "lists", plan)
        result = git_split_commit_apply.build_commit_plan(
            ROOT / lists["directory"],
            output=tmp_root / "split_commit_apply_plan.json",
        )
        assert result["mode"] == "split_commit_apply_plan"
        assert result["apply"] is False
        assert result["ok"], result
        assert result["live_index_matches_dry_run_final_tree"], result
        assert isinstance(result["commit_count"], int), result
        assert result["has_commits"] == (result["commit_count"] >= 1), result
        assert result["output"].startswith("Results/tmp/")
    print("git_split_commit_apply_plan_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
