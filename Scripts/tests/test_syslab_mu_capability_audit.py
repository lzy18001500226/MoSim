from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts/control_platform/run_syslab_mu_capability_audit.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("syslab_mu_audit", RUNNER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parse_output_ignores_launcher_noise() -> None:
    values = load_runner().parse_output(
        "launcher banner\n"
        "musyn=false\nMuSynthesis=false\ncmsclsyn=true\nmussv=true\n"
        "bound=2.7809847614735137\nq_rows=2\nq_cols=2\n"
    )
    assert values == {
        "musyn": "false",
        "MuSynthesis": "false",
        "cmsclsyn": "true",
        "mussv": "true",
        "bound": "2.7809847614735137",
        "q_rows": "2",
        "q_cols": "2",
    }


def test_audit_keeps_dynamic_mu_claim_fail_closed() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert '"decision": "deferred"' in text
    assert "dynamic_mu_controller_synthesis_available" in text
    assert "not_a_mu_synthesis_controller" in text
