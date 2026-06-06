"""Tests for pentestagent.config.settings."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from pentestagent.config.settings import Settings, get_settings, update_settings


class TestSettingsDefaults:
    def test_temperature_default(self):
        s = Settings()
        assert isinstance(s.temperature, float)
        assert 0.0 <= s.temperature <= 1.0

    def test_max_tokens_default(self):
        s = Settings()
        assert isinstance(s.max_tokens, int)
        assert s.max_tokens > 0

    def test_max_context_tokens_default(self):
        s = Settings()
        assert s.max_context_tokens > 0

    def test_max_iterations_default(self):
        s = Settings()
        assert isinstance(s.max_iterations, int)
        assert s.max_iterations > 0

    def test_scope_default_is_empty_list(self):
        s = Settings()
        assert s.scope == []

    def test_target_default_is_none(self):
        s = Settings()
        assert s.target is None

    def test_knowledge_path_is_path(self):
        s = Settings()
        assert isinstance(s.knowledge_path, Path)

    def test_mcp_config_path_is_path(self):
        s = Settings()
        assert isinstance(s.mcp_config_path, Path)


class TestSettingsEnvVars:
    def test_openai_api_key_from_env(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-openai"}):
            s = Settings()
            assert s.openai_api_key == "sk-test-openai"

    def test_anthropic_api_key_from_env(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test"}):
            s = Settings()
            assert s.anthropic_api_key == "sk-ant-test"

    def test_missing_api_keys_are_none(self):
        clean_env = {k: v for k, v in os.environ.items()
                     if k not in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")}
        with patch.dict(os.environ, clean_env, clear=True):
            s = Settings()
            assert s.openai_api_key is None
            assert s.anthropic_api_key is None


class TestSettingsPathConversion:
    def test_string_knowledge_path_converted(self):
        s = Settings(knowledge_path="my/knowledge")
        assert isinstance(s.knowledge_path, Path)
        assert s.knowledge_path == Path("my/knowledge")

    def test_string_mcp_config_path_converted(self):
        s = Settings(mcp_config_path="some/mcp.json")
        assert isinstance(s.mcp_config_path, Path)

    def test_string_vpn_config_path_converted(self):
        s = Settings(vpn_config_path="/etc/vpn/config.ovpn")
        assert isinstance(s.vpn_config_path, Path)

    def test_none_vpn_config_path_stays_none(self):
        s = Settings(vpn_config_path=None)
        assert s.vpn_config_path is None


class TestSettingsSecurityApiKeyLeakage:
    """API keys must NOT appear in string representations."""

    def test_repr_does_not_expose_openai_key(self):
        s = Settings(openai_api_key="sk-super-secret-openai")
        representation = repr(s)
        assert "sk-super-secret-openai" not in representation

    def test_repr_does_not_expose_anthropic_key(self):
        s = Settings(anthropic_api_key="sk-ant-super-secret")
        representation = repr(s)
        assert "sk-ant-super-secret" not in representation

    def test_str_does_not_expose_openai_key(self):
        s = Settings(openai_api_key="sk-super-secret-openai")
        assert "sk-super-secret-openai" not in str(s)

    def test_str_does_not_expose_anthropic_key(self):
        s = Settings(anthropic_api_key="sk-ant-super-secret")
        assert "sk-ant-super-secret" not in str(s)


class TestGetSettings:
    def test_get_settings_returns_settings_instance(self):
        import pentestagent.config.settings as settings_module
        settings_module._settings = None
        result = get_settings()
        assert isinstance(result, Settings)

    def test_get_settings_returns_singleton(self):
        import pentestagent.config.settings as settings_module
        settings_module._settings = None
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_update_settings_replaces_singleton(self):
        import pentestagent.config.settings as settings_module
        settings_module._settings = None
        s1 = get_settings()
        s2 = update_settings(max_iterations=5)
        assert get_settings() is s2
        assert s2.max_iterations == 5

    def test_update_settings_returns_new_instance(self):
        s1 = get_settings()
        s2 = update_settings(temperature=0.1)
        assert s1 is not s2
