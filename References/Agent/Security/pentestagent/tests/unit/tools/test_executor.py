"""Tests for pentestagent.tools.executor (ToolExecutor, ExecutionResult)."""

import asyncio
import pytest

from pentestagent.tools.executor import ExecutionResult, ToolExecutor
from pentestagent.tools.registry import Tool, ToolSchema


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_tool(name: str = "t", success: bool = True, delay: float = 0.0,
               required: list = None) -> Tool:
    async def fn(arguments: dict, runtime) -> str:
        if delay:
            await asyncio.sleep(delay)
        if not success:
            raise RuntimeError("simulated failure")
        return f"result:{arguments}"

    schema = ToolSchema(
        properties={"cmd": {"type": "string"}},
        required=required or [],
    )
    return Tool(name=name, description="", schema=schema, execute_fn=fn)


def _make_executor(timeout: int = 10, max_retries: int = 0) -> ToolExecutor:
    return ToolExecutor(runtime=None, timeout=timeout, max_retries=max_retries)


# ---------------------------------------------------------------------------
# ExecutionResult
# ---------------------------------------------------------------------------

class TestExecutionResult:
    def test_duration_property(self):
        r = ExecutionResult(tool_name="t", arguments={}, duration_ms=1500.0)
        assert r.duration == 1.5

    def test_success_default_true(self):
        r = ExecutionResult(tool_name="t", arguments={})
        assert r.success is True


# ---------------------------------------------------------------------------
# ToolExecutor.execute — success path
# ---------------------------------------------------------------------------

class TestToolExecutorSuccess:
    @pytest.mark.asyncio
    async def test_execute_success(self):
        executor = _make_executor()
        tool = _make_tool()
        result = await executor.execute(tool, {"cmd": "echo"})
        assert result.success is True
        assert result.error is None
        assert "result:" in result.result

    @pytest.mark.asyncio
    async def test_result_recorded_in_history(self):
        executor = _make_executor()
        tool = _make_tool()
        await executor.execute(tool, {"cmd": "x"})
        assert len(executor.execution_history) == 1

    @pytest.mark.asyncio
    async def test_duration_tracked(self):
        executor = _make_executor()
        tool = _make_tool()
        result = await executor.execute(tool, {"cmd": "x"})
        assert result.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_tool_name_in_result(self):
        executor = _make_executor()
        tool = _make_tool(name="my_tool")
        result = await executor.execute(tool, {"cmd": "x"})
        assert result.tool_name == "my_tool"

    @pytest.mark.asyncio
    async def test_timestamps_set(self):
        executor = _make_executor()
        tool = _make_tool()
        result = await executor.execute(tool, {"cmd": "x"})
        assert result.start_time is not None
        assert result.end_time is not None
        assert result.end_time >= result.start_time


# ---------------------------------------------------------------------------
# ToolExecutor.execute — failure paths
# ---------------------------------------------------------------------------

class TestToolExecutorFailure:
    @pytest.mark.asyncio
    async def test_invalid_arguments_fail_immediately(self):
        executor = _make_executor()
        tool = _make_tool(required=["cmd"])
        result = await executor.execute(tool, {})  # missing "cmd"
        assert result.success is False
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_tool_exception_captured(self):
        executor = _make_executor()
        tool = _make_tool(success=False)
        result = await executor.execute(tool, {"cmd": "x"})
        assert result.success is False
        assert "simulated failure" in result.error

    @pytest.mark.asyncio
    async def test_timeout_returns_failure(self):
        executor = _make_executor(timeout=1)
        tool = _make_tool(delay=5)
        result = await executor.execute(tool, {"cmd": "x"})
        assert result.success is False
        assert "timed out" in result.error.lower()

    @pytest.mark.asyncio
    async def test_failed_result_in_history(self):
        executor = _make_executor()
        tool = _make_tool(success=False)
        await executor.execute(tool, {"cmd": "x"})
        assert executor.execution_history[-1].success is False


# ---------------------------------------------------------------------------
# Retries
# ---------------------------------------------------------------------------

class TestToolExecutorRetries:
    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        attempt_count = {"n": 0}

        async def flaky(arguments, runtime):
            attempt_count["n"] += 1
            if attempt_count["n"] < 2:
                raise RuntimeError("transient error")
            return "ok"

        tool = Tool(name="flaky", description="", schema=ToolSchema(), execute_fn=flaky)
        executor = ToolExecutor(runtime=None, timeout=10, max_retries=1)
        result = await executor.execute(tool, {})
        assert result.success is True
        assert attempt_count["n"] == 2

    @pytest.mark.asyncio
    async def test_exhausted_retries_returns_failure(self):
        executor = ToolExecutor(runtime=None, timeout=10, max_retries=1)
        tool = _make_tool(success=False)
        result = await executor.execute(tool, {"cmd": "x"})
        assert result.success is False


# ---------------------------------------------------------------------------
# execute_batch
# ---------------------------------------------------------------------------

class TestToolExecutorBatch:
    @pytest.mark.asyncio
    async def test_sequential_batch(self):
        executor = _make_executor()
        tool = _make_tool()
        results = await executor.execute_batch(
            [(tool, {"cmd": "a"}), (tool, {"cmd": "b"})]
        )
        assert len(results) == 2
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_parallel_batch(self):
        executor = _make_executor()
        tool = _make_tool()
        results = await executor.execute_batch(
            [(tool, {"cmd": "a"}), (tool, {"cmd": "b"})], parallel=True
        )
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_batch_preserves_order(self):
        results_order = []

        async def ordered_fn(arguments, runtime):
            results_order.append(arguments["cmd"])
            return "ok"

        tool = Tool(name="ord", description="", schema=ToolSchema(), execute_fn=ordered_fn)
        executor = _make_executor()
        await executor.execute_batch(
            [(tool, {"cmd": "first"}), (tool, {"cmd": "second"})]
        )
        assert results_order == ["first", "second"]


# ---------------------------------------------------------------------------
# get_execution_stats
# ---------------------------------------------------------------------------

class TestExecutionStats:
    @pytest.mark.asyncio
    async def test_empty_stats(self):
        executor = _make_executor()
        stats = executor.get_execution_stats()
        assert stats["total_executions"] == 0
        assert stats["success_rate"] == 0.0

    @pytest.mark.asyncio
    async def test_stats_after_execution(self):
        executor = _make_executor()
        tool = _make_tool()
        await executor.execute(tool, {"cmd": "x"})
        stats = executor.get_execution_stats()
        assert stats["total_executions"] == 1
        assert stats["successful"] == 1
        assert stats["success_rate"] == 1.0

    @pytest.mark.asyncio
    async def test_stats_tracks_failures(self):
        executor = _make_executor()
        tool = _make_tool(success=False)
        await executor.execute(tool, {"cmd": "x"})
        stats = executor.get_execution_stats()
        assert stats["failed"] == 1
        assert stats["success_rate"] == 0.0

    @pytest.mark.asyncio
    async def test_tools_used_counted(self):
        executor = _make_executor()
        tool = _make_tool(name="counter")
        await executor.execute(tool, {"cmd": "x"})
        await executor.execute(tool, {"cmd": "y"})
        stats = executor.get_execution_stats()
        assert stats["tools_used"]["counter"] == 2


# ---------------------------------------------------------------------------
# History management
# ---------------------------------------------------------------------------

class TestHistoryManagement:
    @pytest.mark.asyncio
    async def test_clear_history(self):
        executor = _make_executor()
        tool = _make_tool()
        await executor.execute(tool, {"cmd": "x"})
        executor.clear_history()
        assert executor.execution_history == []

    @pytest.mark.asyncio
    async def test_get_last_result(self):
        executor = _make_executor()
        tool = _make_tool(name="last_test")
        await executor.execute(tool, {"cmd": "x"})
        last = executor.get_last_result()
        assert last is not None
        assert last.tool_name == "last_test"

    @pytest.mark.asyncio
    async def test_get_last_result_by_name(self):
        executor = _make_executor()
        tool_a = _make_tool(name="toolA")
        tool_b = _make_tool(name="toolB")
        await executor.execute(tool_a, {"cmd": "x"})
        await executor.execute(tool_b, {"cmd": "y"})
        last_a = executor.get_last_result("toolA")
        assert last_a.tool_name == "toolA"

    def test_get_last_result_empty_history(self):
        executor = _make_executor()
        assert executor.get_last_result() is None
