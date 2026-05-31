#!/usr/bin/env python3
"""Smoke test the temporary-index split Git checker."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.devops import git_batch_plan
from CoAgent.devops import git_split_index_check


def main() -> int:
    plan = git_batch_plan.build_plan()
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        lists = git_batch_plan.write_batch_lists(Path(tmp) / "lists", plan)
        batch_paths = next(iter(lists["batches"].values()))
        result = git_split_index_check.check_batch(ROOT / batch_paths["staged"], Path(tmp) / "split_index.json")
        assert result["mode"] == "read_only_temporary_index"
        assert "tree_oid" in result
        assert result["output"].startswith("Results/tmp/")
    print("git_split_index_check_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
