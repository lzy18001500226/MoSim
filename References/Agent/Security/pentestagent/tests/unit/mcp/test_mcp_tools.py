"""Tests for pentestagent.mcp.tools (create_mcp_tool, format_mcp_result)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from pentestagent.mcp.tools import create_mcp_tool, format_mcp_result
from pentestagent.tools.registry import Tool


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_server(name: str = "test_server") -> MagicMock:
    server = MagicMock()
    server.name = name
    return server


def _make_manager(result=None) -> MagicMock:
    manager = MagicMock()
    manager.call_tool = AsyncMock(return_value=result or [{"type": "text", "text": "ok"}])
    return manager


def _basic_tool_def(name: str = "my_tool") -> dict:
    return {
        "name": name,
        "description": "A test MCP tool",
        "inputSchema": {
            "type": "object",
            "properties": {"param": {"type": "string"}},
            "required": ["param"],
        },
    }


# ---------------------------------------------------------------------------
# create_mcp_tool — structure
# ---------------------------------------------------------------------------

class TestCreateMCPToolStructure:
    def test_returns_tool_instance(self):
        tool = create_mcp_tool(_basic_tool_def(), _make_server(), _make_manager())
        assert isinstance(tool, Tool)

    def test_tool_name_prefixed_with_server(self):
        tool = create_mcp_tool(_basic_tool_def("ping"), _make_server("srv"), _make_manager())
        assert tool.name == "mcp_srv_ping"

    def test_tool_description_from_def(self):
        tool = create_mcp_tool(_basic_tool_def(), _make_server(), _make_manager())
        assert "A test MCP tool" in tool.description

    def test_tool_schema_properties_copied(self):
        tool = create_mcp_tool(_basic_tool_def(), _make_server(), _make_manager())
        assert "param" in tool.schema.properties

    def test_tool_schema_required_copied(self):
        tool = create_mcp_tool(_basic_tool_def(), _make_server(), _make_manager())
        assert "param" in tool.schema.required

    def test_tool_category_includes_server_name(self):
        tool = create_mcp_tool(_basic_tool_def(), _make_server("myserver"), _make_manager())
        assert "myserver" in tool.category

    def test_tool_metadata_has_mcp_server(self):
        tool = create_mcp_tool(_basic_tool_def(), _make_server("s"), _make_manager())
        assert tool.metadata["mcp_server"] == "s"

    def test_tool_metadata_has_mcp_tool(self):
        tool = create_mcp_tool(_basic_tool_def("ping"), _make_server(), _make_manager())
        assert tool.metadata["mcp_tool"] == "ping"

    def test_minimal_tool_def_no_schema(self):
        minimal = {"name": "no_schema"}
        tool = create_mcp_tool(minimal, _make_server(), _make_manager())
        assert isinstance(tool, Tool)
        assert tool.name == "mcp_test_server_no_schema"

    def test_tool_def_without_description_gets_default(self):
        no_desc = {"name": "t"}
        tool = create_mcp_tool(no_desc, _make_server("s"), _make_manager())
        assert tool.description  # non-empty


# ---------------------------------------------------------------------------
# create_mcp_tool — execution
# ---------------------------------------------------------------------------

class TestCreateMCPToolExecution:
    @pytest.mark.asyncio
    async def test_execute_calls_manager_call_tool(self):
        manager = _make_manager()
        tool = create_mcp_tool(_basic_tool_def(), _make_server("srv"), manager)
        await tool.execute({"param": "x"}, runtime=None)
        manager.call_tool.assert_called_once_with("srv", "my_tool", {"param": "x"})

    @pytest.mark.asyncio
    async def test_execute_formats_text_result(self):
        manager = _make_manager(result=[{"type": "text", "text": "hello mcp"}])
        tool = create_mcp_tool(_basic_tool_def(), _make_server(), manager)
        result = await tool.execute({"param": "x"}, runtime=None)
        assert "hello mcp" in result

    @pytest.mark.asyncio
    async def test_execute_formats_image_result(self):
        manager = _make_manager(result=[{"type": "image", "mimeType": "image/png"}])
        tool = create_mcp_tool(_basic_tool_def(), _make_server(), manager)
        result = await tool.execute({"param": "x"}, runtime=None)
        assert "Image" in result

    @pytest.mark.asyncio
    async def test_execute_formats_resource_result(self):
        manager = _make_manager(result=[{"type": "resource", "uri": "file://test"}])
        tool = create_mcp_tool(_basic_tool_def(), _make_server(), manager)
        result = await tool.execute({"param": "x"}, runtime=None)
        assert "Resource" in result or "file://test" in result

    @pytest.mark.asyncio
    async def test_execute_string_result(self):
        manager = _make_manager(result="plain string result")
        tool = create_mcp_tool(_basic_tool_def(), _make_server(), manager)
        result = await tool.execute({"param": "x"}, runtime=None)
        assert "plain string result" in result

    @pytest.mark.asyncio
    async def test_execute_exception_returns_error_message(self):
        manager = MagicMock()
        manager.call_tool = AsyncMock(side_effect=RuntimeError("connection lost"))
        tool = create_mcp_tool(_basic_tool_def(), _make_server(), manager)
        result = await tool.execute({"param": "x"}, runtime=None)
        assert "MCP tool error" in result
        assert "connection lost" in result


# ---------------------------------------------------------------------------
# format_mcp_result
# ---------------------------------------------------------------------------

class TestFormatMCPResult:
    def test_text_type(self):
        result = format_mcp_result([{"type": "text", "text": "hello"}])
        assert "hello" in result

    def test_image_type(self):
        result = format_mcp_result([{"type": "image", "mimeType": "image/png", "data": "abc"}])
        assert "Image" in result
        assert "image/png" in result

    def test_resource_type(self):
        result = format_mcp_result([{"type": "resource", "uri": "file://x"}])
        assert "Resource" in result
        assert "file://x" in result

    def test_unknown_type_converted_to_str(self):
        result = format_mcp_result([{"type": "unknown", "data": "xyz"}])
        assert "xyz" in result or "unknown" in result

    def test_plain_string(self):
        result = format_mcp_result("plain")
        assert "plain" in result

    def test_dict_with_content_key(self):
        result = format_mcp_result({"content": [{"type": "text", "text": "nested"}]})
        assert "nested" in result

    def test_multiple_items_joined(self):
        items = [{"type": "text", "text": "a"}, {"type": "text", "text": "b"}]
        result = format_mcp_result(items)
        assert "a" in result
        assert "b" in result

    def test_empty_list(self):
        result = format_mcp_result([])
        assert isinstance(result, str)

    def test_none_result(self):
        result = format_mcp_result(None)
        assert isinstance(result, str)

    def test_integer_result(self):
        result = format_mcp_result(42)
        assert "42" in result


# ---------------------------------------------------------------------------
# Security: MCP tool names from malicious servers
# ---------------------------------------------------------------------------

class TestMCPSchemaInjection:
    """Verify that dangerous tool names / schemas from untrusted MCP servers
    are handled safely (stored but not executed as shell commands)."""

    DANGEROUS_NAMES = [
        "../../../etc/passwd",
        "; rm -rf /",
        "$(id)",
        "`whoami`",
        "name\x00null",
        "<script>alert(1)</script>",
    ]

    @pytest.mark.parametrize("dangerous_name", DANGEROUS_NAMES)
    def test_dangerous_tool_name_stored_in_mcp_prefix(self, dangerous_name):
        tool_def = {"name": dangerous_name, "description": "evil"}
        tool = create_mcp_tool(tool_def, _make_server("evil_srv"), _make_manager())
        # The name is prefixed — the dangerous payload is inside the string, not executed
        assert tool.name.startswith("mcp_evil_srv_")
        # The tool object exists — the system doesn't crash on creation
        assert isinstance(tool, Tool)

    def test_oversize_description_handled(self):
        tool_def = {"name": "t", "description": "D" * 100_000}
        tool = create_mcp_tool(tool_def, _make_server(), _make_manager())
        assert isinstance(tool, Tool)

    def test_deeply_nested_schema_handled(self):
        nested = {"type": "object", "properties": {}}
        current = nested["properties"]
        for i in range(50):
            current[f"level_{i}"] = {"type": "object", "properties": {}}
            current = current[f"level_{i}"]["properties"]
        tool_def = {"name": "nested", "inputSchema": nested}
        tool = create_mcp_tool(tool_def, _make_server(), _make_manager())
        assert isinstance(tool, Tool)
