from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/quality/build_non_frontend_final_qa_audit.py"


def load_module():
    spec = importlib.util.spec_from_file_location("final_qa", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_final_qa_audit_passes_current_exact_selection():
    data = load_module().build()
    assert data["status"] == "passed"
    assert data["selected_file_count"] > 100
    assert data["checks"]["package_boundary_ready"] is True
    assert data["checks"]["over_100mb_files"] == []
    assert data["checks"]["secret_findings"] == []
    assert data["checks"]["upstream_source_count"] > 0
    assert data["checks"]["upstream_source_findings"] == []
