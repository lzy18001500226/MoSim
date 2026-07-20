from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "quality" / "check_controller_graphical_reviews.py"
AUDIT = (
    ROOT
    / "Results"
    / "control_platform"
    / "report_closeout_20260721"
    / "static_audit"
    / "控制器证据审计.json"
)


def load_module():
    spec = importlib.util.spec_from_file_location("controller_graphical_reviews", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def test_controller_graphical_review_accepts_only_route_bound_complete_packet(tmp_path):
    module = load_module()
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    row = next(item for item in audit["rows"] if item["controller"] == "super_twisting_smc")
    artifacts = {}
    for key in module.REQUIRED_ARTIFACT_KEYS:
        artifact = tmp_path / f"{key}.txt"
        artifact.write_text(key, encoding="utf-8")
        artifacts[key] = str(artifact)
    source = ROOT / row["selected_internal_source"]
    packet = {
        "schema": module.REQUIRED_SCHEMA,
        "controller": "super_twisting_smc",
        "status": "accepted",
        "source": "MWORKS_MCP",
        "license_state": "licensed",
        "internal_model_path": row["selected_internal_source"],
        "internal_model_sha256": digest(source),
        "check_model_status": "passed",
        "simulation_status": "passed",
        "result_binding_status": "passed",
        "result_window_title": row["source_records"][0]["model_name"],
        "layout_review": {key: True for key in module.REQUIRED_LAYOUT_KEYS},
        "artifacts": artifacts,
    }
    packet_path = tmp_path / "super_twisting_smc.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    assert module.validate_packet(packet, row, packet_path) == []

    packet["result_window_title"] = "MoSim_P3_TERMINAL_SMC_GRAPHICAL_MIL"
    errors = module.validate_packet(packet, row, packet_path)
    assert any(error["field"] == "result_window_title" for error in errors)


def test_review_audit_keeps_missing_routes_visible(tmp_path):
    module = load_module()
    report = module.audit_reviews(AUDIT, tmp_path)

    assert report["expected_native_graphical_routes"] == 47
    assert report["accepted"] == 0
    assert report["blocked"] == 0
    assert report["missing"] == 47
    assert report["invalid"] == 0
