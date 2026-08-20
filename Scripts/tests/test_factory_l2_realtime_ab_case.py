from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts" / "sunray" / "run_factory_l2_realtime_ab_case.sh"


def test_plugin_source_fingerprint_uses_relative_package_paths() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    assert "plugin_source_fingerprint()" in source
    assert 'cd "${source_dir}"' in source
    assert "find . -type f -print0" in source
    assert 'PLUGIN_SOURCE_SHA256="$(plugin_source_fingerprint "${PLUGIN_SOURCE_DIR}")"' in source
    assert 'find "${PLUGIN_SOURCE_DIR}" -type f -print0' not in source


def test_factory_ab_runner_rejects_unsupported_lockstep_pacing_before_startup() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    assert "validate_lockstep_pacing_contract()" in source
    assert "(int(rate) % 250) == 0" in source
    assert "max_step_size=${MAX_STEP_SIZE_S} s must equal 1/rate" in source
    assert "libgazebo_mavlink_interface" in source
    assert source.index("validate_lockstep_pacing_contract") < source.index("source /opt/ros/noetic/setup.bash")
