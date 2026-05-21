from pathlib import Path

from _shared import create_deepseek_agent, print_action_results, print_response


agent = create_deepseek_agent(
    "Use MCP actions for exact calculations. Prefer calling the tools over mental math."
)


if __name__ == "__main__":
    server_script = Path(__file__).with_name("_calculator_mcp_server.py")
    agent.use_mcp(str(server_script))

    agent.input(
        "Use the MCP actions to compute (12.5 + 7.25) * 3, then answer with the exact result."
    )
    records = agent.get_action_result()
    print_action_results(records)
    response = agent.get_response()
    print_response(response)

# Expected key output after configuring DeepSeek:
# [ACTION_RECORDS] includes MCP calculator action calls.
# The final computed value for (12.5 + 7.25) * 3 is 59.25.
# [MODEL_REPLY] reports 59.25.

# How it works:
# agent.use_mcp(script_path) spawns _calculator_mcp_server.py as a subprocess and
# communicates over stdin/stdout using the Model Context Protocol.
# The MCP server exposes add and multiply tools that the model can plan and call
# just like native Agently actions.  get_action_result() drives the full MCP call
# cycle; the subprocess is managed by Agently and torn down after the request.
#
# Flow:
# agent.use_mcp("_calculator_mcp_server.py")
#   | subprocess launched over stdio
#   v
# model plans: add(12.5, 7.25) -> 19.75
#              multiply(19.75, 3) -> 59.25
#   |
#   v
# ActionResult records returned
#   |
#   v
# model reply: "The result is 59.25."
