"""Security tests: API key leakage through logs, exceptions, and string representations.

Verifies that sensitive credentials never appear in places where they could
accidentally be exposed: log output, error messages, string representations,
or serialized data structures.
"""

import logging
import os
from unittest.mock import patch

import pytest

from pentestagent.config.settings import Settings


# ---------------------------------------------------------------------------
# Settings — API keys never leak in repr/str
# ---------------------------------------------------------------------------

class TestSettingsApiKeyLeakage:
    FAKE_OPENAI_KEY = "sk-test-openai-secret-do-not-expose"
    FAKE_ANTHROPIC_KEY = "sk-ant-test-anthropic-secret-do-not-expose"

    def test_repr_masks_openai_key(self):
        s = Settings(openai_api_key=self.FAKE_OPENAI_KEY)
        assert self.FAKE_OPENAI_KEY not in repr(s)

    def test_str_masks_openai_key(self):
        s = Settings(openai_api_key=self.FAKE_OPENAI_KEY)
        assert self.FAKE_OPENAI_KEY not in str(s)

    def test_repr_masks_anthropic_key(self):
        s = Settings(anthropic_api_key=self.FAKE_ANTHROPIC_KEY)
        assert self.FAKE_ANTHROPIC_KEY not in repr(s)

    def test_str_masks_anthropic_key(self):
        s = Settings(anthropic_api_key=self.FAKE_ANTHROPIC_KEY)
        assert self.FAKE_ANTHROPIC_KEY not in str(s)

    def test_repr_shows_masked_placeholder(self):
        s = Settings(openai_api_key=self.FAKE_OPENAI_KEY)
        assert "***" in repr(s)

    def test_none_key_not_shown_as_masked(self):
        s = Settings(openai_api_key=None)
        assert "***" not in repr(s) or "None" in repr(s)

    def test_settings_with_both_keys_masked(self):
        s = Settings(
            openai_api_key=self.FAKE_OPENAI_KEY,
            anthropic_api_key=self.FAKE_ANTHROPIC_KEY,
        )
        combined = repr(s) + str(s)
        assert self.FAKE_OPENAI_KEY not in combined
        assert self.FAKE_ANTHROPIC_KEY not in combined


# ---------------------------------------------------------------------------
# Settings — API keys not exposed through logging
# ---------------------------------------------------------------------------

class TestSettingsApiKeyLogging:
    def test_logging_settings_does_not_expose_key(self, caplog):
        s = Settings(openai_api_key="sk-logging-test-secret")
        with caplog.at_level(logging.DEBUG):
            logging.getLogger("test").debug("Settings: %s", s)
        assert "sk-logging-test-secret" not in caplog.text

    def test_logging_repr_does_not_expose_key(self, caplog):
        s = Settings(anthropic_api_key="sk-ant-logging-secret")
        with caplog.at_level(logging.DEBUG):
            logging.getLogger("test").debug("%r", s)
        assert "sk-ant-logging-secret" not in caplog.text


# ---------------------------------------------------------------------------
# API keys not leaked through exception messages
# ---------------------------------------------------------------------------

class TestApiKeyExceptionLeakage:
    def test_settings_exception_does_not_expose_key(self):
        try:
            s = Settings(openai_api_key="sk-exception-secret")
            raise ValueError(f"Config error: {s}")
        except ValueError as e:
            assert "sk-exception-secret" not in str(e)

    def test_settings_format_in_fstring_masked(self):
        s = Settings(anthropic_api_key="sk-ant-fstring-secret")
        formatted = f"Using settings: {s}"
        assert "sk-ant-fstring-secret" not in formatted


# ---------------------------------------------------------------------------
# Environment variable hygiene
# ---------------------------------------------------------------------------

class TestEnvVarHygiene:
    def test_api_key_loaded_from_env_correctly(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-env-test"}):
            s = Settings()
            # Key should be loadable but not exposed in repr
            assert s.openai_api_key == "sk-env-test"
            assert "sk-env-test" not in repr(s)

    def test_missing_key_does_not_raise(self):
        clean = {k: v for k, v in os.environ.items()
                 if k not in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")}
        with patch.dict(os.environ, clean, clear=True):
            s = Settings()
            assert s.openai_api_key is None
            assert s.anthropic_api_key is None


# ---------------------------------------------------------------------------
# Memory module: system messages excluded from summary (API keys in system prompts)
# ---------------------------------------------------------------------------

class TestMemoryApiKeyLeakage:
    def test_system_messages_excluded_from_format_for_summary(self):
        from pentestagent.llm.memory import ConversationMemory

        mem = ConversationMemory()
        messages = [
            {"role": "system", "content": "OPENAI_API_KEY=sk-system-secret"},
            {"role": "user", "content": "hello"},
        ]
        formatted = mem._format_for_summary(messages)
        assert "sk-system-secret" not in formatted

    @pytest.mark.asyncio
    async def test_summary_prompt_template_has_no_hardcoded_secrets(self):
        from pentestagent.llm.memory import SUMMARY_PROMPT

        # Only check for actual hardcoded secret patterns, not operational terminology
        # (the prompt legitimately uses words like "token", "password" as field names to preserve)
        hardcoded_patterns = ["sk-", "bearer ", "basic auth", "eyj"]
        lower_prompt = SUMMARY_PROMPT.lower()
        for pattern in hardcoded_patterns:
            assert pattern not in lower_prompt, f"Found hardcoded secret pattern '{pattern}' in SUMMARY_PROMPT"
