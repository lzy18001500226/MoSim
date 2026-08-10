"""Check that active report surfaces distinguish current and historical counts."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CURRENT_STATUS = (
    ROOT
    / "Results"
    / "control_platform"
    / "phase2_full_48_climbpath"
    / "g3_repair"
    / "G3_CATALOG_48_CURRENT_STATUS.json"
)
FROZEN_STATUS = (
    ROOT
    / "Results"
    / "control_platform"
    / "phase2_full_48_climbpath"
    / "g3_repair"
    / "G3_STATUS.json"
)
COUNT_DEFINITION = ROOT / "Config" / "control_platform" / "climbpath_baseline_count_definition.json"
AUDIT_DOC = ROOT / "Docs" / "报告" / "审计" / "当前目录48条ClimbPath口径对齐_20260801.md"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    current = read_json(CURRENT_STATUS)
    frozen = read_json(FROZEN_STATUS)
    definition = read_json(COUNT_DEFINITION)
    audit_text = AUDIT_DOC.read_text(encoding="utf-8")

    current_summary = current["summary"]
    require(current_summary["catalog_entry_count"] == 48, "current catalog count is not 48")
    require(current_summary["passed_count"] == 30, "current catalog pass count is not 30")
    require(current_summary["failed_count"] == 18, "current catalog failure count is not 18")
    require(current_summary["not_run_count"] == 0, "current catalog not_run count is not zero")
    require(current_summary["inventory_reconciled"] is True, "current catalog is not reconciled")
    current_rows = {row["scheme_id"]: row for row in current["rows"]}
    failure_classes = Counter(
        row["failure_class"] for row in current_rows.values() if row["status"] == "fail"
    )
    require(
        failure_classes
        == Counter(
            {
                "terminal_position_error_exceeds_5m": 9,
                "simulation_timeout": 8,
                "simulate_failed": 1,
            }
        ),
        f"current failure taxonomy is stale: {failure_classes}",
    )
    pole = current_rows["pole_placement_luenberger"]
    require(pole["evidence_origin"] == "post_freeze_current_override_record", "pole override is missing")
    require(pole["failure_class"] == "terminal_position_error_exceeds_5m", "pole is not a terminal-error failure")
    require(
        pole["terminal_position_error_norm_m"] == 402.1409427651827,
        "pole terminal metric drifted",
    )

    require(frozen["effective_passed_count"] == 28, "frozen G3 pass count changed")
    require(frozen["effective_failed_count"] == 20, "frozen G3 failure count changed")
    require(frozen["completed"] is False, "frozen G3 completion state changed")
    require(
        sha256(FROZEN_STATUS)
        == "080573fdf7a5b63b76cff81d2eed787deae8604a03662df00974d3835131e130",
        "frozen G3 status hash changed",
    )

    current_definition = definition["current_catalog_48_reconciliation"]
    historical_definition = definition["historical_frozen_g3_snapshot"]
    require(current_definition["catalog_entry_count"] == 48, "definition current count is not 48")
    require(current_definition["passed_count"] == 30, "definition current pass count is not 30")
    require(current_definition["failed_count"] == 18, "definition current failure count is not 18")
    require(current_definition["not_run_count"] == 0, "definition current not_run count is not zero")
    require(historical_definition["effective_passed_count"] == 28, "definition historical pass drift")
    require(historical_definition["effective_failed_count"] == 20, "definition historical failure drift")
    require(definition["static_inventory"]["formal_runner_files"] == 53, "FormalRunner file count drift")

    required_markers = {
        "Docs/Workflows/mainline_operations_board.md": "30 passes, 18 completed failures",
        "Docs/报告/README.md": "30 通过、18 完成失败、0 未运行",
        "Docs/Design/报告手册交付证据总账_P0_20260731.md": "当前目录 ClimbPath 对账通过 | 30/48",
        "Docs/报告/用户手册_正文骨架.md": "30/48 通过，18/48 完成失败，0/48 未运行",
        "Docs/报告/审计/控制器证据审计.md": "30/48 通过、18/48",
        "Docs/报告/图/README.md": "当前目录 48 条名义对账",
        "Docs/报告/仿真分析报告_正文骨架.md": "当前固定目录对账为 30/48",
        "Docs/报告/figures/第10章/FIGURE_GENERATION_SUMMARY_20260731.md": "30 通过 / 18 失败 / 0 未运行",
    }
    for relative, marker in required_markers.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        require(marker in text, f"missing current marker in {relative}")
        require("G3_STATUS.json" in text, f"missing historical source marker in {relative}")

    require("30/48" in audit_text, "current audit does not state 30/48")
    require("28/48" in audit_text and "20/48" in audit_text, "current audit lacks historical split")
    require("当前 30 条通过图集" in audit_text, "atlas boundary is missing")
    require("402.1409427651827" in audit_text, "current audit lacks pole 50 s metric")

    result = {
        "status": "passed",
        "current_catalog": {"count": 48, "passed": 30, "failed": 18, "not_run": 0},
        "current_failure_taxonomy": dict(failure_classes),
        "historical_g3_snapshot": {"count": 48, "passed": 28, "failed": 20, "completed": False},
        "formal_runner_files": 53,
        "frozen_g3_sha256": sha256(FROZEN_STATUS),
        "checked_files": len(required_markers) + 4,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, FileNotFoundError, KeyError, json.JSONDecodeError) as exc:
        print(f"alignment check failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
