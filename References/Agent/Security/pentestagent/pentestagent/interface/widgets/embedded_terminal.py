"""EmbeddedTerminal — Textual widget that renders a child-agent PTY.

The widget holds the *master* end of a PTY pair.  The child process writes
its TUI output to the *slave* end; this widget reads from the master,
feeds the bytes through a pyte VT100 emulator, and renders the resulting
screen as Rich Text — colours, bold, underline and reverse included.

Keyboard input and scroll-wheel events are forwarded to the child via the
master fd so the child's TUI remains fully interactive when the widget has
focus.  Mouse click events request focus so the user can start typing
immediately after clicking.

Resize events propagate to the child via TIOCSWINSZ so its TUI reflows
when the panel is resized.
"""

from __future__ import annotations

import fcntl
import os
import select
import struct
import termios
import time

try:
    import pyte

    _PYTE_OK = True
except ImportError:
    pyte = None  # type: ignore
    _PYTE_OK = False

from rich.style import Style
from rich.text import Text
from textual import events, work
from textual.app import RenderableType
from textual.widget import Widget

# ── pyte colour → Rich colour ─────────────────────────────────────────────────

_NAMED: dict[str, str] = {
    "black": "black",
    "red": "red",
    "green": "green",
    "yellow": "yellow",
    "blue": "blue",
    "magenta": "magenta",
    "cyan": "cyan",
    "white": "white",
    "brightblack": "bright_black",
    "brightred": "bright_red",
    "brightgreen": "bright_green",
    "brightyellow": "bright_yellow",
    "brightblue": "bright_blue",
    "brightmagenta": "bright_magenta",
    "brightcyan": "bright_cyan",
    "brightwhite": "bright_white",
}

_HEX6 = frozenset("0123456789abcdefABCDEF")


def _rich_color(c: "str | int") -> "str | None":
    if c == "default":
        return None
    if isinstance(c, int):
        return f"color({c})"
    # pyte returns true-color as a bare 6-char hex string (no '#')
    if len(c) == 6 and all(ch in _HEX6 for ch in c):
        return f"#{c}"
    return _NAMED.get(c, c) or None


# ── Key → PTY byte mapping ────────────────────────────────────────────────────

# Maps Textual key names to the byte sequences a VT100 terminal sends.
_KEY_MAP: dict[str, bytes] = {
    "enter": b"\r",
    "backspace": b"\x7f",
    "tab": b"\t",
    "escape": b"\x1b",
    "up": b"\x1b[A",
    "down": b"\x1b[B",
    "right": b"\x1b[C",
    "left": b"\x1b[D",
    "home": b"\x1b[H",
    "end": b"\x1b[F",
    "pageup": b"\x1b[5~",
    "pagedown": b"\x1b[6~",
    "delete": b"\x1b[3~",
    "insert": b"\x1b[2~",
    # Function keys
    "f1": b"\x1bOP",
    "f2": b"\x1bOQ",
    "f3": b"\x1bOR",
    "f4": b"\x1bOS",
    "f5": b"\x1b[15~",
    "f6": b"\x1b[17~",
    "f7": b"\x1b[18~",
    "f8": b"\x1b[19~",
    "f9": b"\x1b[20~",
    "f10": b"\x1b[21~",
    "f11": b"\x1b[23~",
    "f12": b"\x1b[24~",
}

# ctrl+a … ctrl+z → 0x01 … 0x1a
for _i, _c in enumerate("abcdefghijklmnopqrstuvwxyz", 1):
    _KEY_MAP[f"ctrl+{_c}"] = bytes([_i])


# ── Widget ────────────────────────────────────────────────────────────────────


class EmbeddedTerminal(Widget):
    """Interactive embedded terminal that renders a child process's PTY output."""

    can_focus = True  # must be True to receive keyboard events

    DEFAULT_CSS = """
    EmbeddedTerminal {
        height: 1fr;
        border: round #3a3a3a;
        border-title-color: #9a9a9a;
        border-title-style: bold;
        background: #0a0a0a;
        color: #d4d4d4;
        padding: 0;
        overflow: hidden;
    }
    EmbeddedTerminal:focus {
        border: round #525252;
    }
    """

    # Minimum interval between screen refreshes (≈30 fps).
    _REFRESH_INTERVAL = 1 / 30

    def __init__(self, master_fd: int, label: str = "agent", **kwargs):
        super().__init__(**kwargs)
        self._master_fd = master_fd
        self._label = label
        if _PYTE_OK:
            self._screen: pyte.Screen = pyte.Screen(80, 24)
            self._stream: pyte.Stream = pyte.Stream(self._screen)
        else:
            self._screen = None
            self._stream = None
        self.border_title = label

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        self._pty_reader()

    def on_unmount(self) -> None:
        try:
            os.close(self._master_fd)
        except OSError:
            pass

    # ── PTY reader (thread worker + select) ───────────────────────────────────

    @work(exclusive=True, thread=True)
    def _pty_reader(self) -> None:
        """Read the master PTY fd in a background thread.

        select.select() is used because PTY master fds are not reliably
        pollable via epoll (used by asyncio.add_reader on Linux).

        Refreshes are rate-limited to ~30 fps so the Textual render loop is
        not flooded when the child outputs large amounts of text.
        """
        last_refresh = 0.0
        while True:
            try:
                r, _, _ = select.select([self._master_fd], [], [], 0.05)
                if not r:
                    continue
                data = os.read(self._master_fd, 65536)
                if not data:
                    break
                if self._stream is not None:
                    self._stream.feed(data.decode("utf-8", errors="replace"))
                now = time.monotonic()
                if now - last_refresh >= self._REFRESH_INTERVAL:
                    last_refresh = now
                    self.refresh()
            except OSError:
                break

    # ── PTY writer helper ─────────────────────────────────────────────────────

    def _write_pty(self, data: bytes) -> None:
        try:
            os.write(self._master_fd, data)
        except OSError:
            pass

    # ── Keyboard input forwarding ─────────────────────────────────────────────

    def on_key(self, event: events.Key) -> None:
        event.stop()
        # Printable character — send its UTF-8 encoding directly.
        if (
            event.character
            and len(event.character) == 1
            and event.character.isprintable()
        ):
            self._write_pty(event.character.encode("utf-8"))
            return
        seq = _KEY_MAP.get(event.key)
        if seq:
            self._write_pty(seq)

    # ── Mouse input forwarding ────────────────────────────────────────────────

    def _sgr_mouse(
        self, event: events.MouseEvent, button_code: int, press: bool
    ) -> None:
        """Write an SGR mouse escape sequence to the PTY.

        Format: ESC [ < Cb ; Cx ; Cy M   (press)
                ESC [ < Cb ; Cx ; Cy m   (release)

        Cb  = button code (0=left, 1=middle, 2=right, 64=scroll-up, 65=scroll-down)
              plus modifier bits: shift=4, alt/meta=8, ctrl=16
        Cx/Cy = 1-based column/row.

        Textual dispatches mouse events with coordinates relative to the
        widget's outer region (border included).  The border is 1 cell on
        each side, so the content area starts at (1, 1).  To convert to
        1-based PTY coordinates we therefore use event.x / event.y directly
        (no extra +1 needed — the border offset already provides it).
        """
        btn = button_code
        if event.shift:
            btn |= 4
        if event.meta:
            btn |= 8
        if event.ctrl:
            btn |= 16
        # Widget coords are 0-based and include the 1-cell border, so the first
        # content cell is at (1, 1) → PTY row/col 1 = max(1, event.x/y).
        cx = max(1, event.x)
        cy = max(1, event.y)
        suffix = "M" if press else "m"
        self._write_pty(f"\x1b[<{btn};{cx};{cy}{suffix}".encode())

    def on_mouse_down(self, event: events.MouseDown) -> None:
        event.stop()
        event.prevent_default()
        self.focus()
        self.capture_mouse()  # own all mouse events until mouse_up
        # Textual: 1=left, 2=right, 3=middle → SGR: 0=left, 2=right, 1=middle
        btn = {1: 0, 2: 2, 3: 1}.get(event.button, 0)
        self._sgr_mouse(event, btn, press=True)

    def on_mouse_up(self, event: events.MouseUp) -> None:
        event.stop()
        event.prevent_default()
        self.release_mouse()
        btn = {1: 0, 2: 2, 3: 1}.get(event.button, 0)
        self._sgr_mouse(event, btn, press=False)

    def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        event.stop()
        self._sgr_mouse(event, 64, press=True)

    def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        event.stop()
        self._sgr_mouse(event, 65, press=True)

    def on_mouse_move(self, event: events.MouseMove) -> None:
        event.stop()
        event.prevent_default()
        # SGR button 32 = motion; add held-button bits if a button is pressed.
        btn = 32
        if event.button == 1:
            btn |= 0  # left — motion base already covers it
        elif event.button == 2:
            btn |= 2
        elif event.button == 3:
            btn |= 1
        self._sgr_mouse(event, btn, press=True)

    # ── Resize propagation ────────────────────────────────────────────────────

    def on_resize(self, event: events.Resize) -> None:
        rows = max(1, event.size.height - 2)  # subtract border
        cols = max(1, event.size.width - 2)
        if self._screen is not None:
            self._screen.resize(rows, cols)
        try:
            fcntl.ioctl(
                self._master_fd,
                termios.TIOCSWINSZ,
                struct.pack("HHHH", rows, cols, 0, 0),
            )
        except OSError:
            pass

    # ── Rendering ─────────────────────────────────────────────────────────────

    def render(self) -> RenderableType:
        if self._screen is None:
            return Text(
                "pyte not installed — run: pip install pyte",
                style=Style(color="red", dim=True),
            )

        result = Text(no_wrap=True, overflow="fold")
        buf = self._screen.buffer
        for y in range(self._screen.lines):
            row = buf[y]
            for x in range(self._screen.columns):
                char = row[x]
                try:
                    sty = Style()
                    fg = _rich_color(char.fg)
                    bg = _rich_color(char.bg)
                    if fg:
                        sty += Style(color=fg)
                    if bg:
                        sty += Style(bgcolor=bg)
                    if char.bold:
                        sty += Style(bold=True)
                    if char.underscore:
                        sty += Style(underline=True)
                    if char.reverse:
                        sty += Style(reverse=True)
                except Exception:
                    sty = Style()
                result.append(char.data or " ", style=sty)
            if y < self._screen.lines - 1:
                result.append("\n")
        return result
