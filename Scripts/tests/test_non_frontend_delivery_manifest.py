from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/quality/build_non_frontend_delivery_manifest.py"


def load_module():
    spec = importlib.util.spec_from_file_location("delivery_manifest", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_delivery_manifest_preserves_authority_counts_and_boundaries():
    module = load_module()
    data = module.build()
    assert data["status"] == "delivery_manifest_not_final_submission_acceptance"
    assert data["scope"]["frontend_excluded"] is True
    assert data["controller_baseline"]["counts"] == {
        "accepted": 27,
        "executed_blocked": 33,
        "not_run": 7,
    }
    assert data["controller_baseline"]["final_ab_counts"] == {
        "accepted": 1,
        "executed_blocked": 11,
        "not_run": 2,
    }
    accepted = data["controller_baseline"]["accepted_controller_ids"]
    assert len(accepted) == 27
    assert len(set(accepted)) == 27
    assert "unknown" not in accepted
    assert "cascade_pid" in accepted
    assert len(data["demo_storyboard"]) == 6
    assert all(item["status"].startswith("pending_") for item in data["required_human_outputs"])
    assert "all_controller_gazebo_acceptance" in data["forbidden_claims"]


def test_delivery_manifest_records_existing_authority_files():
    module = load_module()
    data = module.build()
    records = {item["path"]: item for item in data["evidence_files"]}
    assert records[module.AUTHORITY["controller_matrix"]]["exists"] is True
    assert records[module.AUTHORITY["requirement_matrix"]]["exists"] is True
    assert records[module.AUTHORITY["report_source"]]["exists"] is True
