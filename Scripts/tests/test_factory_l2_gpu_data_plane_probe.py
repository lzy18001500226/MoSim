from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "Scripts" / "sunray" / "run_factory_l2_gpu_data_plane_probe.sh"


def test_probe_summary_handles_a_missing_gazebo_performance_message() -> None:
    source = PROBE.read_text(encoding="utf-8")

    assert 'performance = payload.get("gazebo_performance_metrics") or {}' in source
    assert 'print(f"gazebo_rtf={performance.get(\'real_time_factor\')}")' in source


def test_probe_accepts_full_model_optimization_cases() -> None:
    source = PROBE.read_text(encoding="utf-8")

    assert 'CASE_NAME="${FACTORY_L2_PACING_CASE:-gpu_full}"' in source
    assert 'control|control_gpu_visual|gpu|gpu_full|gpu_full10x5|gpu_full2x2|gpu2x2' in source


def test_probe_rejects_unsupported_400_hz_before_launch() -> None:
    source = PROBE.read_text(encoding="utf-8")

    assert 'gpu_full_physics400)' in source
    assert 'PX4 Gazebo lockstep requires real_time_update_rate' in source
    assert source.index('gpu_full_physics400)') < source.index('mkdir -p "${CASE_DIR}"')


def test_probe_reserves_the_default_gazebo_master_port() -> None:
    source = PROBE.read_text(encoding="utf-8")

    assert 'if (( ROS_MASTER_PORT == 11345 )); then' in source
    assert 'conflicts with the default Gazebo master port' in source


def test_probe_records_gpu_plugin_profile_configuration() -> None:
    source = PROBE.read_text(encoding="utf-8")

    assert 'mosim_gpu_livox_output_mode=%s' in source
    assert 'mosim_gpu_livox_profile_interval_frames=%s' in source
    assert 'MOSIM_GPU_LIVOX_PROFILE_OUTPUT="${PROFILE_OUTPUT_PATH}"' in source
    assert 'gpu_livox_profile_artifact=missing' in source
    assert 'MOSIM_GPU_RESOURCE_SAMPLE_INTERVAL_S' in source
    assert 'sample_factory_l2_runtime_resources.py' in source
    assert 'gpu_pacing_resource_samples=missing' in source


def test_probe_cleanup_owns_the_pipeline_launcher_process_tree() -> None:
    source = PROBE.read_text(encoding="utf-8")

    assert 'collect_process_tree()' in source
    assert 'collect_run_scoped_processes()' in source
    assert 'mapfile -t launcher_process_tree < <(collect_process_tree "${LAUNCH_PID}")' in source
    assert 'done < <(collect_run_scoped_processes)' in source
    assert 'kill "-${signal}" "${tree_pid}"' in source
    assert 'trap cleanup_probe EXIT' in source
    assert 'local exit_code=$?' in source
    assert 'exit "${exit_code}"' in source


def test_probe_creates_the_supervisor_log_parent_before_starting_tee() -> None:
    source = PROBE.read_text(encoding="utf-8")

    assert source.index('mkdir -p "${CASE_DIR}"') < source.index('> >(tee "${SUPERVISOR_LOG}")')
    assert ') | tee "${SUPERVISOR_LOG}"' not in source
