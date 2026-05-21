from pathlib import Path

from agently import Agently

# MCP integration also requires a tool-calling capable model.
Agently.set_settings(
    "OpenAICompatible",
    {
        "base_url": "http://127.0.0.1:11434/v1",
        "model": "qwen2.5:7b",
    },
)

agent = Agently.create_agent()
agent.set_action_loop(max_rounds=4)


## MCP (Model Context Protocol) — connect external tool servers as actions
#
# agent.use_mcp(path_or_url) accepts:
#   - A file path  →  launches the script as a subprocess (stdio transport)
#   - An HTTP URL  →  connects to a running MCP server (HTTP transport)
#
# The MCP tools are discovered automatically and exposed to the model like any
# other Agently action — no manual schema registration needed.

mcp_server = Path(__file__).with_name("_10_mcp_server.py")


def demo_mcp_stdio():
    # stdio transport: Agently spawns the MCP server as a child process.
    # The subprocess is torn down automatically after the request completes.
    agent.use_mcp(str(mcp_server))
    agent.input(
        "A marathon is 42.195 km long, and the typical marathon runner weighs 70 kg. "
        "Use the MCP actions to convert both values to imperial units."
    )
    records = agent.get_action_result()
    print("[action records]", records)
    response = agent.get_response()
    print(response.result.get_text())


# demo_mcp_stdio()


# Expected output (example):
# [action records] [ActionResult(action_id='km_to_miles', result=26.2188, ...),
#                   ActionResult(action_id='kg_to_lb',    result=154.3234, ...)]
# A marathon is 42.195 km (≈ 26.22 miles) long.
# A 70 kg runner weighs approximately 154.32 lb.
#
# How it works:
# agent.use_mcp(path) spawns _10_mcp_server.py as a subprocess and communicates
# via stdin/stdout using the Model Context Protocol JSON-RPC format.
# Agently discovers the server's tool list (km_to_miles, kg_to_lb) automatically
# and exposes them to the model with the same interface as native @action_func tools.
# get_action_result() drives the full MCP call cycle:
#   model plans calls -> Agently forwards them to the subprocess -> results returned.
# The subprocess is killed after get_response() completes.
#
# Flow:
# agent.use_mcp("_10_mcp_server.py")
#   subprocess: _10_mcp_server.py starts (stdio mode)
#   MCP handshake -> tool list: [km_to_miles, kg_to_lb]
#   |
#   v
# agent.get_action_result()
#   model plans: km_to_miles(km=42.195) -> 26.2188
#                kg_to_lb(kg=70.0)      -> 154.3234
#   |
#   v
# agent.get_response()
#   model reply: "A marathon is 26.22 miles; the runner weighs 154.32 lb."
# subprocess is killed
#
# For HTTP transport: start the server separately with MCP_TRANSPORT=http MCP_PORT=<port>
# and use agent.use_mcp("http://127.0.0.1:<port>/mcp") instead of a file path.
