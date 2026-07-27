#!/usr/bin/env python3
"""Smoke test CoAgent doctor quick/full mode planning."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.doctor import coagent_doctor


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    quick = coagent_doctor.collect(ns(output=None, json=True, mode="quick", skip_status_export=False, include_heavy=False))
    assert quick["mode"] == "quick", quick
    assert quick["elapsed_seconds"] >= 0, quick
    quick_ids = set(quick["checks"])
    assert "coagent.status_export" not in quick_ids, quick_ids
    assert "coagent.lifecycle" not in quick_ids, quick_ids
    assert "coagent.active_queue" in quick_ids, quick_ids
    assert all("elapsed_seconds" in item["detail"] for item in quick["checks"].values()), quick

    full_plan = [
        func.__name__
        for func in coagent_doctor.check_plan(ns(mode="full", skip_status_export=False))
    ]
    assert "check_status_export_smoke" in full_plan, full_plan
    assert "check_lifecycle_smoke" in full_plan, full_plan
    assert "check_git_split_commit_dry_run_smoke" not in full_plan, full_plan
    assert "check_git_split_commit_apply_smoke" not in full_plan, full_plan
    assert "check_review_package_smoke" not in full_plan, full_plan

    heavy_plan = [
        func.__name__
        for func in coagent_doctor.check_plan(ns(mode="full", skip_status_export=False, include_heavy=True))
    ]
    assert "check_git_split_commit_dry_run_smoke" in heavy_plan, heavy_plan
    assert "check_git_split_commit_apply_smoke" in heavy_plan, heavy_plan
    assert "check_review_package_smoke" in heavy_plan, heavy_plan

    skipped_plan = [
        func.__name__
        for func in coagent_doctor.check_plan(ns(mode="full", skip_status_export=True, include_heavy=False))
    ]
    assert "check_status_export_smoke" not in skipped_plan, skipped_plan

    print("doctor_modes_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
