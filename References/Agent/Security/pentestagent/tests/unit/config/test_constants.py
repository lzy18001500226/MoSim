"""Tests for pentestagent.config.constants."""

import pentestagent.config.constants as C


class TestAppInfo:
    def test_app_name_is_string(self):
        assert isinstance(C.APP_NAME, str)
        assert len(C.APP_NAME) > 0

    def test_app_version_format(self):
        parts = C.APP_VERSION.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)


class TestAgentStateConstants:
    def test_all_states_are_strings(self):
        states = [
            C.AGENT_STATE_IDLE,
            C.AGENT_STATE_THINKING,
            C.AGENT_STATE_EXECUTING,
            C.AGENT_STATE_WAITING_INPUT,
            C.AGENT_STATE_COMPLETE,
            C.AGENT_STATE_ERROR,
        ]
        for s in states:
            assert isinstance(s, str)

    def test_all_states_are_unique(self):
        states = [
            C.AGENT_STATE_IDLE,
            C.AGENT_STATE_THINKING,
            C.AGENT_STATE_EXECUTING,
            C.AGENT_STATE_WAITING_INPUT,
            C.AGENT_STATE_COMPLETE,
            C.AGENT_STATE_ERROR,
        ]
        assert len(states) == len(set(states))


class TestToolCategories:
    def test_categories_are_strings(self):
        cats = [
            C.TOOL_CATEGORY_EXECUTION,
            C.TOOL_CATEGORY_WEB,
            C.TOOL_CATEGORY_NETWORK,
            C.TOOL_CATEGORY_RECON,
            C.TOOL_CATEGORY_EXPLOITATION,
            C.TOOL_CATEGORY_MCP,
        ]
        for c in cats:
            assert isinstance(c, str)

    def test_categories_are_unique(self):
        cats = [
            C.TOOL_CATEGORY_EXECUTION,
            C.TOOL_CATEGORY_WEB,
            C.TOOL_CATEGORY_NETWORK,
            C.TOOL_CATEGORY_RECON,
            C.TOOL_CATEGORY_EXPLOITATION,
            C.TOOL_CATEGORY_MCP,
        ]
        assert len(cats) == len(set(cats))


class TestTimeouts:
    def test_command_timeout_is_positive_int(self):
        assert isinstance(C.DEFAULT_COMMAND_TIMEOUT, int)
        assert C.DEFAULT_COMMAND_TIMEOUT > 0

    def test_vpn_timeout_is_positive_int(self):
        assert isinstance(C.DEFAULT_VPN_TIMEOUT, int)
        assert C.DEFAULT_VPN_TIMEOUT > 0

    def test_mcp_timeout_is_positive_int(self):
        assert isinstance(C.DEFAULT_MCP_TIMEOUT, int)
        assert C.DEFAULT_MCP_TIMEOUT > 0

    def test_command_timeout_is_reasonable(self):
        # Should be between 10 seconds and 1 hour
        assert 10 <= C.DEFAULT_COMMAND_TIMEOUT <= 3600


class TestLLMDefaults:
    def test_temperature_range(self):
        # temperature can be None if model not set, skip if so
        if C.DEFAULT_TEMPERATURE is not None:
            assert 0.0 <= C.DEFAULT_TEMPERATURE <= 2.0

    def test_max_tokens_positive(self):
        assert isinstance(C.DEFAULT_MAX_TOKENS, int)
        assert C.DEFAULT_MAX_TOKENS > 0

    def test_max_tokens_reasonable(self):
        # Reasonable upper limit for current models
        assert C.DEFAULT_MAX_TOKENS <= 100_000


class TestAgentDefaults:
    def test_max_iterations_is_int(self):
        assert isinstance(C.AGENT_MAX_ITERATIONS, int)

    def test_max_iterations_positive(self):
        assert C.AGENT_MAX_ITERATIONS > 0

    def test_orchestrator_max_iterations_gte_agent(self):
        assert C.ORCHESTRATOR_MAX_ITERATIONS >= C.AGENT_MAX_ITERATIONS

    def test_memory_reserve_ratio_range(self):
        assert 0.0 < C.MEMORY_RESERVE_RATIO < 1.0


class TestRAGSettings:
    def test_chunk_size_positive(self):
        assert C.DEFAULT_CHUNK_SIZE > 0

    def test_chunk_overlap_less_than_chunk_size(self):
        assert C.DEFAULT_CHUNK_OVERLAP < C.DEFAULT_CHUNK_SIZE

    def test_chunk_overlap_non_negative(self):
        assert C.DEFAULT_CHUNK_OVERLAP >= 0

    def test_rag_top_k_positive(self):
        assert C.DEFAULT_RAG_TOP_K > 0


class TestFileExtensions:
    def test_text_extensions_have_dot_prefix(self):
        for ext in C.KNOWLEDGE_TEXT_EXTENSIONS:
            assert ext.startswith(".")

    def test_data_extensions_have_dot_prefix(self):
        for ext in C.KNOWLEDGE_DATA_EXTENSIONS:
            assert ext.startswith(".")


class TestTransportTypes:
    def test_stdio_transport(self):
        assert C.MCP_TRANSPORT_STDIO == "stdio"

    def test_sse_transport(self):
        assert C.MCP_TRANSPORT_SSE == "sse"

    def test_transports_are_distinct(self):
        assert C.MCP_TRANSPORT_STDIO != C.MCP_TRANSPORT_SSE


class TestExitCommands:
    def test_exit_commands_is_list(self):
        assert isinstance(C.EXIT_COMMANDS, list)

    def test_exit_commands_not_empty(self):
        assert len(C.EXIT_COMMANDS) > 0

    def test_exit_in_exit_commands(self):
        assert "exit" in C.EXIT_COMMANDS

    def test_quit_in_exit_commands(self):
        assert "quit" in C.EXIT_COMMANDS
