from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "Config" / "control_platform" / "offline_composition_catalog.json"
APP_SOURCE = ROOT / "apps" / "model_studio" / "src" / "app.jl"


def test_model_studio_contains_every_offline_profile_authority() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8-sig"))
    source = APP_SOURCE.read_text(encoding="utf-8")
    expected = [profile["profile_id"] for profile in catalog["certified_profiles"]]
    expected.extend(proof["profile_id"] for proof in catalog["custom_profile_proofs"])
    expected.extend(profile["profile_id"] for profile in catalog["disabled_profiles"])
    missing = [profile_id for profile_id in expected if profile_id not in source]
    assert missing == []


def test_model_studio_fail_closes_disabled_safety_profile() -> None:
    source = APP_SOURCE.read_text(encoding="utf-8")
    assert '"QP/NMPC Safety [当前禁用]"' in source
    assert "available=false" in source
    assert "app.MilButton.Enable = item.available" in source
    assert "app.ResultButton.Enable = item.available" in source


def test_certification_runner_closes_windows_and_session() -> None:
    source = (ROOT / "Scripts" / "mworks" / "run_offline_profile_certification.py").read_text(
        encoding="utf-8"
    )
    assert '"--gui-reset-windows"' in source
    assert '"--shutdown-session"' in source
