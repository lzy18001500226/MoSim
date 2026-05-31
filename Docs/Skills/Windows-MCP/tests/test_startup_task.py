from unittest.mock import Mock

from click.testing import CliRunner

from windows_mcp.__main__ import main
import windows_mcp.__main__ as cli


def test_resolve_program_prefers_installed_script(monkeypatch):
    monkeypatch.setattr(cli.shutil, "which", lambda name: "C:\\Tools\\windows-mcp.exe" if name == "windows-mcp" else None)

    assert cli._resolve_program() == ["C:\\Tools\\windows-mcp.exe"]


def test_resolve_program_falls_back_to_uvx_for_ephemeral_uv_cache(monkeypatch):
    def fake_which(name: str):
        if name == "windows-mcp":
            return "C:\\Users\\me\\.cache\\uv\\archive\\bin\\windows-mcp.exe"
        if name == "uvx":
            return "C:\\Tools\\uvx.exe"
        return None

    monkeypatch.setattr(cli.shutil, "which", fake_which)

    assert cli._resolve_program() == ["C:\\Tools\\uvx.exe", "windows-mcp"]


def test_install_writes_start_script_and_creates_task(monkeypatch, tmp_path):
    runner = CliRunner()
    monkeypatch.setattr(cli, "CONFIG_DIR", tmp_path)
    start_script = tmp_path / "start server.cmd"
    monkeypatch.setattr(cli, "_START_SCRIPT_PATH", start_script)
    monkeypatch.setattr(cli, "_resolve_program", lambda: ["C:\\Tools\\windows-mcp.exe"])

    calls = []

    def fake_schtasks(*args: str):
        calls.append(args)
        if args[:2] == ("/Query", "/TN"):
            return Mock(returncode=1, stdout="", stderr="ERROR: The system cannot find the file specified.")
        return Mock(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(cli, "_schtasks", fake_schtasks)

    result = runner.invoke(main, ["install", "--transport", "sse", "--host", "127.0.0.1", "--port", "9000"])

    assert result.exit_code == 0, result.output
    script = start_script.read_text(encoding="utf-8")
    assert "windows-mcp.exe serve --transport sse --host 127.0.0.1 --port 9000" in script
    assert '1>>"' in script
    assert '2>>"' in script
    assert (
        "/Create",
        "/SC",
        "ONLOGON",
        "/TN",
        cli._TASK_NAME,
        "/TR",
        f'"{start_script}"',
        "/F",
    ) in calls
    assert ("/Run", "/TN", cli._TASK_NAME) in calls


def test_uninstall_removes_task_and_wrapper(monkeypatch, tmp_path):
    runner = CliRunner()
    start_script = tmp_path / "start-server.cmd"
    start_script.write_text("@echo off\n", encoding="utf-8")

    monkeypatch.setattr(cli, "_START_SCRIPT_PATH", start_script)

    calls = []

    def fake_schtasks(*args: str):
        calls.append(args)
        if args[:2] == ("/End", "/TN"):
            return Mock(returncode=0, stdout="", stderr="")
        return Mock(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(cli, "_schtasks", fake_schtasks)

    result = runner.invoke(main, ["uninstall"])

    assert result.exit_code == 0, result.output
    assert not start_script.exists()
    assert ("/End", "/TN", cli._TASK_NAME) in calls
    assert ("/Delete", "/TN", cli._TASK_NAME, "/F") in calls
