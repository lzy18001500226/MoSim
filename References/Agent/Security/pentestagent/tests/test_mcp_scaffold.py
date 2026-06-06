import asyncio


from pentestagent.mcp.example_adapter import ExampleAdapter


def test_example_adapter_list_and_call():
    adapter = ExampleAdapter()

    async def run():
        await adapter.start()
        tools = await adapter.list_tools()
        assert isinstance(tools, list)
        assert any(t.get("name") == "ping" for t in tools)

        result = await adapter.call_tool("ping", {})
        assert isinstance(result, list)
        assert result[0].get("text") == "pong"

        await adapter.stop()

    asyncio.run(run())
