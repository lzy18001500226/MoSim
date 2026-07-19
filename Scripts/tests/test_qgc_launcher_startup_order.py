from pathlib import Path


def test_qgc_one_click_launcher_opens_operator_surface_before_runtime_wait() -> None:
    launcher = Path("Scripts/ui/run_qgc_with_ue.ps1").read_text(encoding="utf-8")

    qgc_launch = "& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $QgcLauncher"
    assert '"start_run", "--run-id", $runId' in launcher
    assert "RUNTIME_STATUS.json" in launcher
    assert "px4_ekf_global_origin.txt" in launcher
    assert "preflight_ready=true" in launcher
    assert '$runtime.status -eq "running"' in launcher
    assert '@($runtime.missing_readiness).Count -eq 0' in launcher
    assert launcher.index('"start_run", "--run-id", $runId') < launcher.index(qgc_launch)
    assert launcher.index(qgc_launch) < launcher.index(
        '$runtimeStatus = Join-Path $ProjectRoot'
    )
    assert "qgc_start_failed" in launcher
