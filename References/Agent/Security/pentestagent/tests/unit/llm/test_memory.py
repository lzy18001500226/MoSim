"""Tests for pentestagent.llm.memory (ConversationMemory)."""

import pytest
from unittest.mock import AsyncMock

from pentestagent.llm.memory import ConversationMemory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _msg(role: str, content: str) -> dict:
    return {"role": role, "content": content}


def _make_history(n: int, role: str = "user") -> list:
    return [_msg(role, f"message {i}") for i in range(n)]


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

class TestConversationMemoryInit:
    def test_default_token_budget(self):
        mem = ConversationMemory(max_tokens=10000, reserve_ratio=0.8)
        assert mem.token_budget == 8000

    def test_reserve_ratio_applied(self):
        mem = ConversationMemory(max_tokens=100000, reserve_ratio=0.5)
        assert mem.token_budget == 50000

    def test_initial_no_summary(self):
        mem = ConversationMemory()
        stats = mem.get_stats()
        assert stats["has_summary"] is False

    def test_initial_summarized_count_zero(self):
        mem = ConversationMemory()
        assert mem.get_stats()["summarized_message_count"] == 0

    def test_get_stats_fields(self):
        mem = ConversationMemory()
        stats = mem.get_stats()
        for key in ("max_tokens", "token_budget", "summarize_threshold", "recent_to_keep"):
            assert key in stats


# ---------------------------------------------------------------------------
# get_messages — basic truncation
# ---------------------------------------------------------------------------

class TestGetMessages:
    def test_empty_history_returns_empty(self):
        mem = ConversationMemory()
        assert mem.get_messages([]) == []

    def test_small_history_returned_in_full(self):
        mem = ConversationMemory(max_tokens=100000)
        history = _make_history(5)
        result = mem.get_messages(history)
        assert len(result) == 5

    def test_oversized_history_truncated(self):
        # Very small budget forces truncation
        mem = ConversationMemory(max_tokens=20, reserve_ratio=1.0)
        history = _make_history(100)
        result = mem.get_messages(history)
        assert len(result) < 100

    def test_most_recent_messages_kept_on_truncation(self):
        mem = ConversationMemory(max_tokens=50, reserve_ratio=1.0)
        history = [_msg("user", f"message-{i}") for i in range(20)]
        result = mem.get_messages(history)
        if result:
            # The last message should be present (most recent)
            assert result[-1]["content"] == "message-19"

    def test_returns_list(self):
        mem = ConversationMemory()
        result = mem.get_messages(_make_history(3))
        assert isinstance(result, list)

    def test_messages_are_dicts(self):
        mem = ConversationMemory()
        result = mem.get_messages(_make_history(3))
        for msg in result:
            assert isinstance(msg, dict)


# ---------------------------------------------------------------------------
# Token counting
# ---------------------------------------------------------------------------

class TestTokenCounting:
    def test_get_total_tokens_positive(self):
        mem = ConversationMemory()
        tokens = mem.get_total_tokens([_msg("user", "hello world")])
        assert tokens > 0

    def test_longer_message_more_tokens(self):
        mem = ConversationMemory()
        short = mem.get_total_tokens([_msg("user", "hi")])
        long = mem.get_total_tokens([_msg("user", "hi " * 100)])
        assert long > short

    def test_empty_message_zero_or_low_tokens(self):
        mem = ConversationMemory()
        tokens = mem.get_total_tokens([_msg("user", "")])
        assert tokens == 0

    def test_fits_in_context_small_history(self):
        mem = ConversationMemory(max_tokens=100000)
        assert mem.fits_in_context(_make_history(3)) is True

    def test_does_not_fit_oversized(self):
        mem = ConversationMemory(max_tokens=5, reserve_ratio=1.0)
        big = [_msg("user", "word " * 1000)]
        assert mem.fits_in_context(big) is False


# ---------------------------------------------------------------------------
# get_messages_with_summary
# ---------------------------------------------------------------------------

class TestGetMessagesWithSummary:
    @pytest.mark.asyncio
    async def test_small_history_not_summarized(self):
        mem = ConversationMemory(max_tokens=100000)
        llm_call = AsyncMock(return_value="summary")
        history = _make_history(5)
        result = await mem.get_messages_with_summary(history, llm_call)
        llm_call.assert_not_called()
        assert result == history

    @pytest.mark.asyncio
    async def test_large_history_triggers_summarization(self):
        # Small budget + large history → summarization needed
        mem = ConversationMemory(
            max_tokens=200,
            reserve_ratio=1.0,
            recent_to_keep=2,
            summarize_threshold=0.1,
        )
        llm_call = AsyncMock(return_value="summary of older messages")
        history = [_msg("user", "word " * 20) for _ in range(20)]
        result = await mem.get_messages_with_summary(history, llm_call)
        llm_call.assert_called()
        # Result should include the summary message
        assert any(
            "summary" in msg.get("content", "").lower()
            for msg in result
        )

    @pytest.mark.asyncio
    async def test_empty_history_returns_empty(self):
        mem = ConversationMemory()
        llm_call = AsyncMock()
        result = await mem.get_messages_with_summary([], llm_call)
        assert result == []
        llm_call.assert_not_called()

    @pytest.mark.asyncio
    async def test_cached_summary_not_recalculated(self):
        mem = ConversationMemory(
            max_tokens=200,
            reserve_ratio=1.0,
            recent_to_keep=2,
            summarize_threshold=0.1,
        )
        llm_call = AsyncMock(return_value="summary")
        history = [_msg("user", "word " * 20) for _ in range(20)]

        await mem.get_messages_with_summary(history, llm_call)
        call_count_after_first = llm_call.call_count

        # Same history, same split point → should use cache
        await mem.get_messages_with_summary(history, llm_call)
        assert llm_call.call_count == call_count_after_first


# ---------------------------------------------------------------------------
# clear_summary_cache
# ---------------------------------------------------------------------------

class TestClearSummaryCache:
    def test_clear_resets_cached_summary(self):
        mem = ConversationMemory()
        mem._cached_summary = "some summary"
        mem._summarized_count = 10
        mem.clear_summary_cache()
        assert mem._cached_summary is None
        assert mem._summarized_count == 0

    def test_stats_reflect_cleared_state(self):
        mem = ConversationMemory()
        mem._cached_summary = "old"
        mem.clear_summary_cache()
        stats = mem.get_stats()
        assert stats["has_summary"] is False
        assert stats["summarized_message_count"] == 0


# ---------------------------------------------------------------------------
# Security: API keys must not be injected into summary prompts
# ---------------------------------------------------------------------------

class TestSecuritySensitiveDataInSummary:
    @pytest.mark.asyncio
    async def test_api_key_in_history_passed_to_llm_call_not_leaked_elsewhere(self):
        """The memory module should pass message content to llm_call as-is.
        This test ensures the SUMMARY_PROMPT template itself doesn't inject
        extra sensitive data beyond what's in the conversation."""
        from pentestagent.llm.memory import SUMMARY_PROMPT

        assert "API_KEY" not in SUMMARY_PROMPT
        assert "sk-" not in SUMMARY_PROMPT
        assert "password" not in SUMMARY_PROMPT.lower()

    def test_format_for_summary_skips_system_messages(self):
        """System messages (which may contain API keys) should NOT be included
        in summarization input."""
        mem = ConversationMemory()
        messages = [
            _msg("system", "API_KEY=sk-secret-do-not-share"),
            _msg("user", "hello"),
            _msg("assistant", "world"),
        ]
        result = mem._format_for_summary(messages)
        assert "sk-secret-do-not-share" not in result

    def test_format_for_summary_includes_user_and_assistant(self):
        mem = ConversationMemory()
        messages = [_msg("user", "scan 192.168.1.1"), _msg("assistant", "starting scan")]
        result = mem._format_for_summary(messages)
        assert "scan 192.168.1.1" in result
        assert "starting scan" in result

    def test_long_content_truncated_in_summary_format(self):
        mem = ConversationMemory()
        long_content = "A" * 10000
        messages = [_msg("user", long_content)]
        result = mem._format_for_summary(messages)
        assert len(result) < len(long_content)
