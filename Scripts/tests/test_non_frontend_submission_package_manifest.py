from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/quality/build_non_frontend_submission_package_manifest.py"


def load_module():
    spec = importlib.util.spec_from_file_location("package_manifest", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_package_manifest_excludes_frontend_and_external_roots():
    module = load_module()
    data = module.build()
    assert data["scope"]["frontend_excluded"] is True
    assert "apps/flight_console" in data["scope"]["exclude_roots"]
    assert "UE5" in data["scope"]["exclude_roots"]
    assert all(not item["path"].startswith("apps/flight_console/") for item in data["candidate_files"])
    assert all(not item["path"].startswith("References/") for item in data["candidate_files"])
    assert all("frontend" not in item["path"].lower().replace("non_frontend", "nonfrontend") for item in data["candidate_files"])
    assert all("orchestrator" not in item["path"].lower() for item in data["candidate_files"])
    assert isinstance(data["inaccessible_paths"], list)
    assert data["candidate_file_count"] < 10000
    assert all(item["path"] not in module.SELF_REFERENTIAL_OUTPUTS for item in data["candidate_files"])


def test_package_manifest_has_current_delivery_inputs():
    module = load_module()
    data = module.build()
    required = {item["path"]: item for item in data["required_paths"]}
    assert required["AGENTS.md"]["exists"] is True
    assert required["Results/control_platform/non_frontend_evidence_index_20260718/NON_FRONTEND_DELIVERY_MANIFEST.json"]["exists"] is True
    assert "copy, delete, stage" in " ".join(data["claim_boundary"])
    assert data["inaccessible_path_count"] == 0
