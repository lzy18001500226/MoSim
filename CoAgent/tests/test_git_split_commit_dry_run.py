#!/usr/bin/env python3
"""Smoke test sequential temporary-index split Git dry-run."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.devops import git_batch_plan
from CoAgent.devops import git_split_commit_dry_run


def main() -> int:
    plan = git_batch_plan.build_plan()
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        lists = git_batch_plan.write_batch_lists(tmp_root / "lists", plan)
        result = git_split_commit_dry_run.dry_run(ROOT / lists["directory"], tmp_root / "dry_run.json")
        assert result["mode"] == "sequential_temporary_index_dry_run"
        assert result["head_unchanged"], result
        assert result["live_index_unchanged"], result
        assert not result["writes_refs"], result
        assert not result["writes_live_index"], result
        assert not result["writes_worktree"], result
        assert not result["creates_commits"], result
        assert result["output"].startswith("Results/tmp/")
    print("git_split_commit_dry_run_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
