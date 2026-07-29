from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_wsl_helper_reads_exit_code_without_windows_powershell_start_process() -> None:
    source = (ROOT / "Scripts/sunray/Invoke-SunrayWslBounded.ps1").read_text(encoding="utf-8")

    assert "System.Diagnostics.ProcessStartInfo" in source
    assert "ReadToEndAsync()" in source
    assert "$process.WaitForExit($TimeoutS * 1000)" in source
    assert "Start-Process -FilePath $wslExe" not in source
    assert "ExitCode = $process.ExitCode" in source
