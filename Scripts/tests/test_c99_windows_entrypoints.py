from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CMD_DIR = ROOT / "Scripts" / "cmd"


def test_c99_windows_entrypoints_resolve_their_own_project_root() -> None:
    for name in (
        "00_准备C99单机环境.cmd",
        "01_运行C99单机起飞悬停降落.cmd",
        "02_运行C99风扰闭环.cmd",
        "03_运行C99电机故障恢复闭环.cmd",
    ):
        source = (CMD_DIR / name).read_text(encoding="utf-8")

        assert 'for %%I in ("%~dp0\\..\\..") do set "MOSIM_ROOT=%%~fI"' in source
        assert 'wsl.exe -d Ubuntu-20.04 --exec wslpath -a -u "%MOSIM_ROOT%"' in source
        assert "PROJECT_ROOT='%MOSIM_WSL_ROOT%'" in source
        assert "C:\\Users\\HP\\Desktop\\MoSim" not in source


def test_current_c99_shell_entrypoints_default_to_their_own_project_root() -> None:
    preflight = (ROOT / "Scripts" / "sunray" / "check_sunray_ros1_runtime_preflight.sh").read_text(
        encoding="utf-8"
    )
    basic_gate = (ROOT / "Scripts" / "sunray" / "run_px4ctrl_basic_gate.sh").read_text(encoding="utf-8")
    wind_gate = (ROOT / "Scripts" / "sunray" / "run_px4ctrl_fastlio_wind_demo_gate.sh").read_text(
        encoding="utf-8"
    )

    assert 'PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"' in preflight
    assert 'PROJECT_ROOT="${PROJECT_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"' in basic_gate
    assert 'PROJECT_ROOT="${PROJECT_ROOT}" \\' in wind_gate
