from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    ROOT
    / "Scripts"
    / "sunray"
    / "px4ctrl_golden_slice"
    / "run_px4ctrl_g9_family_generated_c_gate.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("generated_c_gate", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_detects_g10_fields_across_public_and_private_headers(tmp_path: Path) -> None:
    module = load_module()
    public_header = tmp_path / "fixture.h"
    private_header = tmp_path / "fixture_private.h"
    public_header.write_text(
        "double l1_model_decay_in;\ndouble safety_accel_limit_x_in;\n",
        encoding="utf-8",
    )
    private_header.write_text("double fault_rotor_efficiency_4_in;\n", encoding="utf-8")

    assert module.detect_g10_bde_inputs([public_header, private_header]) is True


def test_rejects_partial_g10_header_contract(tmp_path: Path) -> None:
    module = load_module()
    header = tmp_path / "fixture.h"
    header.write_text(
        "double l1_model_decay_in;\ndouble safety_accel_limit_x_in;\n",
        encoding="utf-8",
    )

    assert module.detect_g10_bde_inputs([header, tmp_path / "missing_private.h"]) is False


def test_detects_p10_dfbc_fields_across_generated_headers(tmp_path: Path) -> None:
    module = load_module()
    public_header = tmp_path / "fixture.h"
    private_header = tmp_path / "fixture_private.h"
    public_header.write_text(
        "double high_order_body_rate_limit_x_in;\ndouble smooth_feedback_bound_x_in;\n",
        encoding="utf-8",
    )
    private_header.write_text("double disturbance_compensation_limit_z_in;\n", encoding="utf-8")

    assert module.detect_p10_dfbc_inputs([public_header, private_header]) is True
