# pyright: reportMissingImports=false

"""InteractiveWrapper example using an Agently Agent with streamed UI output."""

from agently import Agently
from agently_devtools import ObservationBridge, InteractiveWrapper

bridge = ObservationBridge(app_id="agently-main-examples", group_id="interactive-wrapper-agent")
bridge.register(Agently)


# Create a simple Agent
agent = Agently.create_agent()

# Configure the agent with a persistent system prompt
agent.system(
    "You are a helpful assistant. Answer user questions concisely and clearly. "
    "When the user asks 'hello', respond with a friendly greeting. "
    "Prefer short paragraphs so streamed output is easy to follow.",
    always=True,
)

# Create InteractiveWrapper wrapping the agent
interactive = InteractiveWrapper(
    agent,
    title="Streaming Chat Agent",
    description="An interactive Agently Agent whose response appears incrementally when the configured model supports streaming",
)


if __name__ == "__main__":
    print(f"Interactive UI: {interactive.ui_url}")
    print(
        "If your configured model backend supports streaming, the answer will appear incrementally in the browser UI."
    )
    print("If agently-devtools start is running, Agent runs will also appear in the local DevTools console.")
    try:
        interactive.wait()
    finally:
        bridge.unregister(Agently)

# Stable expected key output from the declared run:
# launched example prints the local DevTools or Interactive UI URL and streams/records the declared demo events.
#
# How it works:
# InteractiveWrapper wraps an Agently Agent directly.  When the browser sends a request,
# the wrapper calls agent.input(request_data["input"]).streaming_print()-style internally
# and streams delta tokens to the browser UI as they arrive from the model.
# ObservationBridge is registered so agent runs appear in the devtools console as well.
# The agent has a persistent system prompt (always=True) that applies to every request.
#
# Flow:
# bridge.register(Agently) -> devtools event hooks installed
# InteractiveWrapper(agent, ...) -> starts local HTTP server
# interactive.ui_url -> http://localhost:<port>/?...
#   |  (browser sends request: "hello")
#   v
# agent.system("You are a helpful assistant...", always=True).input("hello")
# delta tokens streamed to browser UI
# interactive.wait() -> blocks until Ctrl-C
