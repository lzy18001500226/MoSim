"""Tests for pentestagent.tools.registry."""

import pytest

from pentestagent.tools.registry import (
    Tool,
    ToolSchema,
    clear_tools,
    disable_tool,
    enable_tool,
    get_all_tools,
    get_tool,
    get_tool_names,
    get_tools_by_category,
    register_tool,
    register_tool_instance,
    unregister_tool,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_tool(name: str = "test_tool", category: str = "general") -> Tool:
    async def _fn(arguments: dict, runtime) -> str:
        return "ok"

    return Tool(
        name=name,
        description="A test tool",
        schema=ToolSchema(
            properties={"param": {"type": "string", "description": "A param"}},
            required=["param"],
        ),
        execute_fn=_fn,
        category=category,
    )


@pytest.fixture(autouse=True)
def isolated_registry():
    """Ensure each test starts with a clean registry."""
    clear_tools()
    yield
    clear_tools()


# ---------------------------------------------------------------------------
# ToolSchema
# ---------------------------------------------------------------------------

class TestToolSchema:
    def test_defaults_initialized(self):
        schema = ToolSchema()
        assert schema.properties == {}
        assert schema.required == []

    def test_to_dict_contains_type(self):
        schema = ToolSchema(properties={"a": {"type": "string"}}, required=["a"])
        d = schema.to_dict()
        assert d["type"] == "object"
        assert "a" in d["properties"]
        assert "a" in d["required"]

    def test_custom_type(self):
        schema = ToolSchema(type="array")
        assert schema.to_dict()["type"] == "array"


# ---------------------------------------------------------------------------
# Tool.validate_arguments
# ---------------------------------------------------------------------------

class TestToolValidateArguments:
    def test_valid_arguments_pass(self):
        tool = _make_tool()
        valid, err = tool.validate_arguments({"param": "hello"})
        assert valid is True
        assert err is None

    def test_missing_required_field_fails(self):
        tool = _make_tool()
        valid, err = tool.validate_arguments({})
        assert valid is False
        assert "param" in err

    def test_wrong_type_fails(self):
        tool = _make_tool()
        valid, err = tool.validate_arguments({"param": 123})
        assert valid is False
        assert "param" in err

    def test_extra_unknown_fields_are_allowed(self):
        tool = _make_tool()
        valid, err = tool.validate_arguments({"param": "ok", "extra": "ignored"})
        assert valid is True

    def test_unknown_json_type_is_allowed(self):
        schema = ToolSchema(
            properties={"x": {"type": "unknown_type"}},
            required=["x"],
        )

        async def fn(a, r):
            return ""

        tool = Tool(name="t", description="", schema=schema, execute_fn=fn)
        valid, err = tool.validate_arguments({"x": object()})
        assert valid is True

    def test_integer_type_validated(self):
        schema = ToolSchema(
            properties={"n": {"type": "integer"}},
            required=["n"],
        )

        async def fn(a, r):
            return ""

        tool = Tool(name="t", description="", schema=schema, execute_fn=fn)
        valid, _ = tool.validate_arguments({"n": 42})
        assert valid is True
        invalid, err = tool.validate_arguments({"n": "not_an_int"})
        assert invalid is False

    def test_boolean_type_validated(self):
        schema = ToolSchema(
            properties={"flag": {"type": "boolean"}},
            required=["flag"],
        )

        async def fn(a, r):
            return ""

        tool = Tool(name="t", description="", schema=schema, execute_fn=fn)
        valid, _ = tool.validate_arguments({"flag": True})
        assert valid is True
        invalid, _ = tool.validate_arguments({"flag": "yes"})
        assert invalid is False


# ---------------------------------------------------------------------------
# Tool.to_llm_format
# ---------------------------------------------------------------------------

class TestToolToLlmFormat:
    def test_format_has_type_function(self):
        tool = _make_tool()
        fmt = tool.to_llm_format()
        assert fmt["type"] == "function"

    def test_format_has_name(self):
        tool = _make_tool(name="my_tool")
        fmt = tool.to_llm_format()
        assert fmt["function"]["name"] == "my_tool"

    def test_format_has_description(self):
        tool = _make_tool()
        fmt = tool.to_llm_format()
        assert "description" in fmt["function"]

    def test_format_has_parameters(self):
        tool = _make_tool()
        fmt = tool.to_llm_format()
        params = fmt["function"]["parameters"]
        assert "properties" in params
        assert "required" in params


# ---------------------------------------------------------------------------
# Tool.execute — disabled state
# ---------------------------------------------------------------------------

class TestToolDisabledExecution:
    @pytest.mark.asyncio
    async def test_disabled_tool_returns_disabled_message(self):
        tool = _make_tool()
        tool.enabled = False
        result = await tool.execute({"param": "x"}, runtime=None)
        assert "disabled" in result.lower()

    @pytest.mark.asyncio
    async def test_enabled_tool_executes(self):
        tool = _make_tool()
        result = await tool.execute({"param": "x"}, runtime=None)
        assert result == "ok"


# ---------------------------------------------------------------------------
# Registry operations
# ---------------------------------------------------------------------------

class TestRegisterAndGet:
    def test_register_tool_instance_and_get(self):
        tool = _make_tool("alpha")
        register_tool_instance(tool)
        assert get_tool("alpha") is tool

    def test_get_nonexistent_tool_returns_none(self):
        assert get_tool("does_not_exist") is None

    def test_get_all_tools_includes_registered(self):
        tool = _make_tool("beta")
        register_tool_instance(tool)
        assert tool in get_all_tools()

    def test_get_tool_names_includes_registered(self):
        tool = _make_tool("gamma")
        register_tool_instance(tool)
        assert "gamma" in get_tool_names()

    def test_name_collision_overwrites(self):
        tool_a = _make_tool("dup")
        tool_b = _make_tool("dup")
        register_tool_instance(tool_a)
        register_tool_instance(tool_b)
        assert get_tool("dup") is tool_b

    def test_clear_tools_removes_all(self):
        register_tool_instance(_make_tool("one"))
        register_tool_instance(_make_tool("two"))
        clear_tools()
        assert get_all_tools() == []

    def test_unregister_existing_tool(self):
        register_tool_instance(_make_tool("removeme"))
        assert unregister_tool("removeme") is True
        assert get_tool("removeme") is None

    def test_unregister_nonexistent_returns_false(self):
        assert unregister_tool("ghost") is False


class TestGetToolsByCategory:
    def test_returns_tools_in_category(self):
        register_tool_instance(_make_tool("web_tool", category="web"))
        register_tool_instance(_make_tool("net_tool", category="network"))
        web_tools = get_tools_by_category("web")
        assert any(t.name == "web_tool" for t in web_tools)
        assert all(t.category == "web" for t in web_tools)

    def test_unknown_category_returns_empty(self):
        register_tool_instance(_make_tool("t"))
        assert get_tools_by_category("nonexistent") == []


class TestEnableDisable:
    def test_disable_tool(self):
        register_tool_instance(_make_tool("d_tool"))
        assert disable_tool("d_tool") is True
        assert get_tool("d_tool").enabled is False

    def test_enable_tool(self):
        t = _make_tool("e_tool")
        t.enabled = False
        register_tool_instance(t)
        assert enable_tool("e_tool") is True
        assert get_tool("e_tool").enabled is True

    def test_disable_nonexistent_returns_false(self):
        assert disable_tool("ghost") is False

    def test_enable_nonexistent_returns_false(self):
        assert enable_tool("ghost") is False


class TestRegisterToolDecorator:
    def test_decorator_registers_tool(self):
        @register_tool(
            name="decorated_tool",
            description="Test decorator",
            schema=ToolSchema(properties={"cmd": {"type": "string"}}, required=["cmd"]),
            category="test",
        )
        async def my_tool(arguments: dict, runtime) -> str:
            return "decorated"

        assert get_tool("decorated_tool") is not None
        assert get_tool("decorated_tool").category == "test"

    @pytest.mark.asyncio
    async def test_decorator_preserves_execution(self):
        @register_tool(
            name="exec_tool",
            description="Execution test",
            schema=ToolSchema(),
        )
        async def exec_fn(arguments: dict, runtime) -> str:
            return "executed"

        tool = get_tool("exec_tool")
        result = await tool.execute({}, runtime=None)
        assert result == "executed"
