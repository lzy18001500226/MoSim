# pyright: reportMissingImports=false

"""Basic InteractiveWrapper example using a streaming callable."""

import time
from collections.abc import Generator

from agently import Agently
from agently_devtools import ObservationBridge, InteractiveWrapper

bridge = ObservationBridge(app_id="agently-main-examples", group_id="interactive-wrapper-basic")
bridge.register(Agently)


def echo_handler(request_data: dict, **options) -> Generator[str, None, None]:
    """
    Stream a simple echo response chunk by chunk.

    Args:
        request_data: Dictionary with 'input' key containing user message
        **options: Additional options from FastAPIHelper

    Returns:
        Incremental text chunks rendered as they arrive in the UI
    """
    message = request_data.get("input", "").strip()
    if not message:
        yield "Please provide some input."
        return

    chunks = [
        "Analyzing input...\n",
        f"Echo: {message}\n",
        f"Message length: {len(message)} characters\n",
        f"Word count: {len(message.split())}\n",
    ]
    for chunk in chunks:
        time.sleep(0.2)
        yield chunk


# Create InteractiveWrapper instance
interactive = InteractiveWrapper(
    echo_handler,
    title="Streaming Echo Demo",
    description="Generator-based echo handler that streams chunks into the interactive UI",
)


if __name__ == "__main__":
    print(f"Interactive UI: {interactive.ui_url}")
    print("This example streams several text chunks instead of returning one full response.")
    print(
        "ObservationBridge is also registered, but this plain callable example does not emit Agently runtime runs unless you replace the handler with an Agently target."
    )
    try:
        interactive.wait()
    finally:
        bridge.unregister(Agently)

# Stable expected key output from the declared run:
# launched example prints the local DevTools or Interactive UI URL and streams/records the declared demo events.
#
# How it works:
# InteractiveWrapper wraps a streaming callable (a generator function here) in a local
# HTTP server that the agently-devtools UI connects to.  When a request arrives, the
# wrapper calls echo_handler(request_data), iterates the generator, and streams each
# chunk to the browser UI incrementally.  ObservationBridge is also registered but
# emits no runtime events because this example does not use an Agently agent.
# Print the ui_url and open it in a browser to see the streaming echo demo.
#
# Flow:
# InteractiveWrapper(echo_handler, title="...") -> starts local HTTP server
# interactive.ui_url -> http://localhost:<port>/?...
#   |  (browser sends request)
#   v
# echo_handler(request_data): yields 4 chunks with 0.2s sleep between each
# chunks streamed to browser: "Analyzing input...", "Echo: ...", "Length: ...", "Words: ..."
# interactive.wait() -> blocks until Ctrl-C
