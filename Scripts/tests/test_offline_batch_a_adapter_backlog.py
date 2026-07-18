from __future__ import annotations

import copy
import json

from Scripts.quality import check_offline_batch_a_adapter_backlog as checker


def authority() -> tuple[dict, dict]:
    backlog = json.loads(checker.BACKLOG_PATH.read_text(encoding="utf-8-sig"))
    inventory = json.loads(checker.INVENTORY_PATH.read_text(encoding="utf-8-sig"))
    return backlog, inventory


def test_current_batch_a_backlog_passes() -> None:
    backlog, inventory = authority()
    assert checker.validate(backlog, inventory) == []
    assert len(backlog["entries"]) == 16


def test_missing_batch_a_module_fails_coverage() -> None:
    backlog, inventory = authority()
    changed = copy.deepcopy(backlog)
    changed["entries"].pop()
    assert "batch_a_module_coverage_mismatch" in checker.validate(changed, inventory)


def test_source_anchor_must_exist() -> None:
    backlog, inventory = authority()
    changed = copy.deepcopy(backlog)
    changed["entries"][0]["source_anchor"] = "missing.mo"
    assert "source_anchor_missing:px4ctrl" in checker.validate(changed, inventory)


def test_neural_pid_keeps_zero_untrained_claim() -> None:
    backlog, inventory = authority()
    changed = copy.deepcopy(backlog)
    entry = next(item for item in changed["entries"] if item["module_id"] == "neural_pid")
    entry["next_gate"] = "extract_adapter"
    assert "neural_pid_claim_boundary_missing" in checker.validate(changed, inventory)
