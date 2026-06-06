"""CollapsibleTerminal — wraps EmbeddedTerminal with a clickable title header.

Clicking the header collapses/expands the terminal.  When collapsed the inner
EmbeddedTerminal gets ``display: none``, which causes Textual to skip
rendering it entirely.  The PTY reader thread keeps running (so the child
process stays alive) but no screen redraws are scheduled, keeping CPU overhead
minimal for invisible panels.
"""

from __future__ import annotations

from textual import events, on
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from .embedded_terminal import EmbeddedTerminal


class CollapsibleTerminal(Widget):
    """Collapsible container around an :class:`EmbeddedTerminal`.

    The header row shows ``▼ label`` when expanded and ``▶ label`` when
    collapsed.  Click the header to toggle.  When collapsed the widget shrinks
    to three rows (top-border + header + bottom-border) and the embedded
    terminal is hidden via ``display: none`` so Textual skips rendering it.
    """

    collapsed: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
    CollapsibleTerminal {
        height: 1fr;
        border: round #3a3a3a;
        margin-bottom: 1;
    }
    CollapsibleTerminal.collapsed {
        height: 3;
    }
    CollapsibleTerminal > ._ct-header {
        height: 1;
        padding: 0 1;
        color: #7878b0;
    }
    CollapsibleTerminal > ._ct-header:hover {
        background: #1a1a3a;
        color: #c0c0f0;
    }
    CollapsibleTerminal > EmbeddedTerminal {
        height: 1fr;
        border: none;
    }
    CollapsibleTerminal.collapsed > EmbeddedTerminal {
        display: none;
    }
    """

    def __init__(self, master_fd: int, label: str = "agent", **kwargs) -> None:
        super().__init__(**kwargs)
        self._master_fd = master_fd
        self._label = label

    def compose(self):  # type: ignore[override]
        yield Static(f"▼  {self._label}", classes="_ct-header", markup=False)
        yield EmbeddedTerminal(master_fd=self._master_fd, label=self._label)

    # ── Reactive watcher ──────────────────────────────────────────────────────

    def watch_collapsed(self, value: bool) -> None:
        """Sync CSS class and header icon whenever *collapsed* changes."""
        self.set_class(value, "collapsed")
        icon = "▶" if value else "▼"
        try:
            self.query_one("._ct-header", Static).update(f"{icon}  {self._label}")
        except Exception:
            pass

    # ── Header click → toggle ─────────────────────────────────────────────────

    @on(events.Click, "._ct-header")
    def _on_header_click(self, event: events.Click) -> None:
        self.collapsed = not self.collapsed
        event.stop()
