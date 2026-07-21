import subprocess
import sys
from pathlib import Path


def test_profile_sampler_self_test() -> None:
    result = subprocess.run(
        [sys.executable, "Scripts/sunray/profile_fuel_runtime_processes.py", "--self-test"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_fuel_launcher_profile_is_opt_in_and_run_scoped() -> None:
    launcher = Path("Scripts/sunray/start_factory_fuel_single_exploration_review.ps1").read_text(
        encoding="utf-8"
    )

    assert "[int]$Mid360PluginDownsample = 4" in launcher
    assert 'SUNRAY_MID360_PLUGIN_DOWNSAMPLE=$Mid360PluginDownsample' in launcher
    assert "[switch]$ProfileRuntimeProcesses" in launcher
    assert "profile_fuel_runtime_processes.py" in launcher
    assert "fuel_runtime_process_profile.csv" in launcher
    assert "fuel_runtime_process_profile.json" in launcher
