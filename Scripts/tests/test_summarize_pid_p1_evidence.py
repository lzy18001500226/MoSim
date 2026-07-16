from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/summarize_pid_p1_evidence.py"


def test_summary_preserves_unaccepted_claim_boundaries() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert '"selectable": False' in text
    assert 'variant_equivalence["six_variant_graphical_equivalence"]' in text
    assert 'attitude_thrust["lifecycle_fail_closed"]' in text
    assert 'attitude_thrust_mworks["sample_count"] == 126' in text
    assert 'attitude_thrust_mworks["output_count"] == 20' in text
    assert "len(generated_input_fields) == 41" in text
    assert "physical_parameter_inputs.issubset(generated_input_fields)" in text
    assert "== 2520" in text
    assert 'attitude_thrust_sil["comparison"]["pass"]' in text
    assert '"gazebo_px4_mavros_closed_loop": False' in text


def test_summary_indexes_required_evidence() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for name in (
        "mcp_evidence.json",
        "pid_graphical_build_manifest.json",
        "pid_codegen_manifest.json",
        "pid_codegen_runtime_check.json",
        "pid_graphical_codegen_equivalence.json",
        "pid_graphical_variant_mil.json",
        "pid_six_variant_graphical_equivalence.json",
        "PID_ATTITUDE_THRUST_GATE.json",
        "MWORKS_ATTITUDE_THRUST_MANIFEST.json",
        "generate_model_code_result_v2.json",
        "codegen_runtime_check_v2.json",
        "sil_equivalence_126_rows_v2.json",
        "screenshot_manifest.json",
    ):
        assert name in text


def test_summary_writes_reproducible_lf_json() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'newline="\\n"' in text
    assert "write_json_lf(output, summary)" in text
