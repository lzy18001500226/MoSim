"""Simple notifier bridge for UI notifications.

Modules can call `notify(level, message)` to emit operator-visible
notifications. A UI (TUI) may register a callback via `register_callback()`
to receive notifications and display them. If no callback is registered,
notifications are logged.

A second channel — `spawn_terminal` / `register_spawn_terminal_callback` —
lets agent code request that the TUI open an EmbeddedTerminal widget for a
child agent's PTY output.

A third channel — `despawn_terminal` / `register_despawn_terminal_callback` —
lets agent code request that the TUI remove a previously opened terminal.
"""

import logging
from typing import Callable, Optional

_callback: Optional[Callable[[str, str], None]] = None
_spawn_terminal_cb: Optional[Callable[[int, str], None]] = None
_despawn_terminal_cb: Optional[Callable[[str], None]] = None
_agent_wake_up_cb: Optional[Callable[[], None]] = None


def register_callback(cb: Callable[[str, str], None]) -> None:
    """Register a callback to receive notifications.

    Callback receives (level, message).
    """
    global _callback
    _callback = cb


def notify(level: str, message: str) -> None:
    """Emit a notification. If UI callback registered, call it; otherwise log."""
    global _callback
    if _callback:
        try:
            _callback(level, message)
            return
        except Exception:
            logging.getLogger(__name__).exception("Notifier callback failed")

    # Fallback to logging
    log = logging.getLogger("pentestagent.notifier")
    if level.lower() in ("error", "critical"):
        log.error(message)
    elif level.lower() in ("warn", "warning"):
        log.warning(message)
    else:
        log.info(message)


def register_spawn_terminal_callback(cb: Callable[[int, str], None]) -> None:
    """Register a callback so the TUI can create an EmbeddedTerminal widget.

    Callback receives (master_fd, label).
    """
    global _spawn_terminal_cb
    _spawn_terminal_cb = cb


def spawn_terminal(master_fd: int, label: str) -> bool:
    """Ask the TUI to open an EmbeddedTerminal for *master_fd*.

    Returns True if the TUI accepted the request, False if no TUI is active
    (caller should fall back to opening a new terminal window).
    """
    global _spawn_terminal_cb
    if _spawn_terminal_cb:
        try:
            _spawn_terminal_cb(master_fd, label)
            return True
        except Exception:
            logging.getLogger(__name__).exception("spawn_terminal callback failed")
    return False


def register_despawn_terminal_callback(cb: Callable[[str], None]) -> None:
    """Register a callback so the TUI can remove a CollapsibleTerminal widget.

    Callback receives (label,).
    """
    global _despawn_terminal_cb
    _despawn_terminal_cb = cb


def despawn_terminal(label: str) -> None:
    """Ask the TUI to close and remove the terminal identified by *label*."""
    global _despawn_terminal_cb
    if _despawn_terminal_cb:
        try:
            _despawn_terminal_cb(label)
        except Exception:
            logging.getLogger(__name__).exception("despawn_terminal callback failed")


def register_agent_wake_up_callback(cb: Callable[[], None]) -> None:
    """Register a callback that the TUI uses to restart the agent loop.

    Called when a child-agent push notification arrives while the parent
    agent is idle.  The TUI callback should invoke agent.wake_up() and
    route its output to the chat panel.
    """
    global _agent_wake_up_cb
    _agent_wake_up_cb = cb


def agent_wake_up() -> None:
    """Signal the TUI to resume the parent agent loop (idle → thinking).

    If no TUI callback is registered (headless mode), this is a no-op;
    the injected conversation_history message will be processed the next
    time the agent is invoked manually.
    """
    global _agent_wake_up_cb
    if _agent_wake_up_cb:
        try:
            _agent_wake_up_cb()
        except Exception:
            logging.getLogger(__name__).exception("agent_wake_up callback failed")
