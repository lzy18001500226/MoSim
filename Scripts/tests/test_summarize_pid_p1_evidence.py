from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/control_platform/summarize_pid_p1_evidence.py"


def load_summary_module():
    spec = importlib.util.spec_from_file_location("pid_p1_summary", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load PID P1 summary module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_summary_closes_runtime_gate_only_from_six_acknowledged_profiles() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert 'variant_equivalence["six_variant_graphical_equivalence"]' in text
    assert 'attitude_thrust["lifecycle_fail_closed"]' in text
    assert 'attitude_thrust_mworks["sample_count"] == 126' in text
    assert 'attitude_thrust_mworks["output_count"] == 20' in text
    assert "len(generated_input_fields) == 41" in text
    assert "physical_parameter_inputs.issubset(generated_input_fields)" in text
    assert "== 2520" in text
    assert 'attitude_thrust_sil["comparison"]["pass"]' in text
    assert '"gazebo_px4_mavros_closed_loop": runtime_gate_passed' in text
    assert '"selectable": runtime_gate_passed' in text
    for profile in (
        "cascade_pid",
        "gain_scheduled_pid",
        "fuzzy_pid",
        "neural_pid",
        "anti_windup",
        "feedforward_profile",
    ):
        assert profile in text


def test_runtime_profile_assessment_is_fail_closed(tmp_path: Path) -> None:
    module = load_summary_module()
    profile = "cascade_pid"
    (tmp_path / "PX4CTRL_BASIC_MISSION_METRICS.json").write_text(
        json.dumps({"status": "passed", "steady_hover": {"z_abs_rmse_m": 0.01}}),
        encoding="utf-8",
    )
    (tmp_path / "RUN_MANIFEST.json").write_text(
        json.dumps({
            "mission": "takeoff_hover_land",
            "controller_core_profile": profile,
            "diagnostics": {"mission_exit_code": 0},
        }),
        encoding="utf-8",
    )
    (tmp_path / "PID_GENERATED_RUNTIME_PROVENANCE.json").write_text(
        json.dumps({
            "status": "passed",
            "controller_name": profile,
            "provenance_level": "runtime_acknowledged",
            "errors": [],
        }),
        encoding="utf-8",
    )
    assert module.assess_runtime_profile(profile, tmp_path)["status"] == "passed"
    (tmp_path / "PID_GENERATED_RUNTIME_PROVENANCE.json").unlink()
    result = module.assess_runtime_profile(profile, tmp_path)
    assert result["status"] == "blocked"
    assert "missing_provenance" in result["errors"]


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
