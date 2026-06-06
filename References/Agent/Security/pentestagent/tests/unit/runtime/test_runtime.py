"""Tests for pentestagent.runtime.runtime (CommandResult, detect_environment, LocalRuntime)."""

import asyncio
import pytest

from pentestagent.runtime.runtime import (
    CommandResult,
    EnvironmentInfo,
    LocalRuntime,
    ToolInfo,
    detect_environment,
)


# ---------------------------------------------------------------------------
# CommandResult
# ---------------------------------------------------------------------------

class TestCommandResult:
    def test_success_on_zero_exit_code(self):
        r = CommandResult(exit_code=0, stdout="ok", stderr="")
        assert r.success is True

    def test_failure_on_nonzero_exit_code(self):
        r = CommandResult(exit_code=1, stdout="", stderr="error")
        assert r.success is False

    def test_output_combines_stdout_and_stderr(self):
        r = CommandResult(exit_code=0, stdout="OUT", stderr="ERR")
        assert "OUT" in r.output
        assert "ERR" in r.output

    def test_output_only_stdout(self):
        r = CommandResult(exit_code=0, stdout="OUT", stderr="")
        assert r.output == "OUT"

    def test_output_only_stderr(self):
        r = CommandResult(exit_code=0, stdout="", stderr="ERR")
        assert r.output == "ERR"

    def test_output_empty_when_both_empty(self):
        r = CommandResult(exit_code=0, stdout="", stderr="")
        assert r.output == ""

    def test_negative_exit_code_is_failure(self):
        r = CommandResult(exit_code=-1, stdout="", stderr="timeout")
        assert r.success is False


# ---------------------------------------------------------------------------
# EnvironmentInfo
# ---------------------------------------------------------------------------

class TestEnvironmentInfo:
    def _make_env(self, tools=None):
        return EnvironmentInfo(
            os="Linux",
            os_version="5.15",
            shell="bash",
            architecture="x86_64",
            available_tools=tools or [],
        )

    def test_str_contains_os(self):
        env = self._make_env()
        assert "Linux" in str(env)

    def test_str_contains_shell(self):
        env = self._make_env()
        assert "bash" in str(env)

    def test_str_no_tools_shows_none(self):
        env = self._make_env(tools=[])
        assert "None" in str(env)

    def test_str_groups_tools_by_category(self):
        tools = [
            ToolInfo(name="nmap", path="/usr/bin/nmap", category="network_scan"),
            ToolInfo(name="curl", path="/usr/bin/curl", category="utilities"),
        ]
        env = self._make_env(tools=tools)
        s = str(env)
        assert "nmap" in s
        assert "curl" in s
        assert "network_scan" in s
        assert "utilities" in s


# ---------------------------------------------------------------------------
# detect_environment
# ---------------------------------------------------------------------------

class TestDetectEnvironment:
    def test_returns_environment_info(self):
        env = detect_environment()
        assert isinstance(env, EnvironmentInfo)

    def test_os_is_non_empty_string(self):
        env = detect_environment()
        assert isinstance(env.os, str)
        assert len(env.os) > 0

    def test_shell_is_non_empty_string(self):
        env = detect_environment()
        assert isinstance(env.shell, str)
        assert len(env.shell) > 0

    def test_available_tools_is_list(self):
        env = detect_environment()
        assert isinstance(env.available_tools, list)

    def test_tool_info_fields(self):
        env = detect_environment()
        for tool in env.available_tools:
            assert isinstance(tool.name, str)
            assert isinstance(tool.path, str)
            assert isinstance(tool.category, str)


# ---------------------------------------------------------------------------
# LocalRuntime — basic lifecycle
# ---------------------------------------------------------------------------

class TestLocalRuntimeLifecycle:
    @pytest.mark.asyncio
    async def test_start_sets_running(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runtime = LocalRuntime()
        await runtime.start()
        assert await runtime.is_running() is True
        await runtime.stop()

    @pytest.mark.asyncio
    async def test_stop_clears_running(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runtime = LocalRuntime()
        await runtime.start()
        await runtime.stop()
        assert await runtime.is_running() is False

    @pytest.mark.asyncio
    async def test_get_status_returns_dict(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runtime = LocalRuntime()
        await runtime.start()
        status = await runtime.get_status()
        assert isinstance(status, dict)
        assert status["type"] == "local"
        assert status["running"] is True
        await runtime.stop()

    @pytest.mark.asyncio
    async def test_status_after_stop(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runtime = LocalRuntime()
        await runtime.start()
        await runtime.stop()
        status = await runtime.get_status()
        assert status["running"] is False


# ---------------------------------------------------------------------------
# LocalRuntime — execute_command
# ---------------------------------------------------------------------------

class TestLocalRuntimeExecuteCommand:
    @pytest.mark.asyncio
    async def test_echo_command(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runtime = LocalRuntime()
        await runtime.start()
        result = await runtime.execute_command("echo hello")
        assert result.success is True
        assert "hello" in result.stdout
        await runtime.stop()

    @pytest.mark.asyncio
    async def test_exit_code_propagated(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runtime = LocalRuntime()
        await runtime.start()
        result = await runtime.execute_command("exit 42", timeout=5)
        assert result.exit_code == 42
        await runtime.stop()

    @pytest.mark.asyncio
    async def test_stderr_captured(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runtime = LocalRuntime()
        await runtime.start()
        result = await runtime.execute_command("echo error >&2")
        assert "error" in result.stderr or "error" in result.stdout
        await runtime.stop()

    @pytest.mark.asyncio
    async def test_timeout_returns_failure(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runtime = LocalRuntime()
        await runtime.start()
        result = await runtime.execute_command("sleep 60", timeout=1)
        assert result.exit_code != 0
        assert "timed out" in result.stderr.lower()
        await runtime.stop()

    @pytest.mark.asyncio
    async def test_command_result_type(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runtime = LocalRuntime()
        await runtime.start()
        result = await runtime.execute_command("echo test")
        assert isinstance(result, CommandResult)
        await runtime.stop()

    @pytest.mark.asyncio
    async def test_ansi_codes_stripped(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        runtime = LocalRuntime()
        await runtime.start()
        result = await runtime.execute_command(r"printf '\033[1;32mGREEN\033[0m'")
        assert "\033[" not in result.stdout
        await runtime.stop()
