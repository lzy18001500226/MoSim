"""Regression checks for semantic-catalog completion gating."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
QUALITY_ROOT = ROOT / "Scripts" / "quality"
if str(QUALITY_ROOT) not in sys.path:
    sys.path.insert(0, str(QUALITY_ROOT))


def load_policy_module():
    path = QUALITY_ROOT / "model_studio_entry_policy.py"
    spec = importlib.util.spec_from_file_location("model_studio_entry_policy_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_incomplete_semantic_catalog_exposes_the_current_graphical_batch() -> None:
    policy_module = load_policy_module()
    policy = policy_module.load_entry_policy(ROOT)

    assert policy["new_semantic_entries_complete"] is False
    assert len(policy["_semantic_rows"]) == 48
    assert len(policy["_model_rows"]) == 48
    assert all(row["display_name_en"] for row in policy["_model_rows"].values())
    active = policy_module.active_controller_ids(policy)
    assert len(active) == 19
    assert {"official_pid", "px4ctrl"}.issubset(active)
    assert policy["current_graphical_entry_count"] == 17
    assert len(policy["current_graphical_active_controller_ids"]) == 17
    assert policy_module.controller_is_active(policy, "adaptive_backstepping") is True
    assert policy_module.controller_is_active(policy, "linear_mpc") is False
