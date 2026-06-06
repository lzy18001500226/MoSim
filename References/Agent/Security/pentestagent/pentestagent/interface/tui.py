"""
PentestAgent TUI - Terminal User Interface
"""

import asyncio
import json
import logging
import re
import textwrap
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, cast

import pyperclip
from rich.text import Text
from textual import events, on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import (
    Center,
    Container,
    Horizontal,
    ScrollableContainer,
    Vertical,
)
from textual.events import Click
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.scrollbar import ScrollBar, ScrollBarRender
from textual.timer import Timer
from textual.widget import Widget
from textual.widgets import Button, Input, Static, Switch, Tree
from textual.widgets.tree import TreeNode

from ..config.constants import DEFAULT_MODEL

# ANSI escape sequence pattern for stripping control codes from input
_ANSI_ESCAPE = re.compile(
    r"\x1b\[[0-9;]*[mGKHflSTABCDEFsu]|\x1b\].*?\x07|\x1b\[<[0-9;]*[Mm]"
)


# ASCII-safe scrollbar renderer to avoid Unicode glyph issues
class ASCIIScrollBarRender(ScrollBarRender):
    """Scrollbar renderer using ASCII-safe characters."""

    BLANK_GLYPH = " "
    VERTICAL_BARS = [" ", " ", " ", " ", " ", " ", " ", " "]
    HORIZONTAL_BARS = [" ", " ", " ", " ", " ", " ", " ", " "]


# Apply ASCII scrollbar globally
ScrollBar.renderer = ASCIIScrollBarRender


# Custom Tree with ASCII-safe icons for PowerShell compatibility
class CrewTree(Tree):
    """Tree widget with ASCII-compatible expand/collapse icons."""

    ICON_NODE = "> "
    ICON_NODE_EXPANDED = "v "


if TYPE_CHECKING:
    from ..agents.pa_agent import PentestAgentAgent


# Each entry is (signature, description).
# Signature tokens that are <placeholders> or [optionals] match any user input.
COMMAND_SIGNATURES: List[tuple] = [
    ("/assist <task>", "Single AI call with tool execution"),
    ("/agent <task>", "Autonomous single-agent loop"),
    ("/crew <task>", "Multi-agent: orchestrator + workers"),
    ("/interact <task>", "Guided interactive chat"),
    ("/target <host>", "Set pentest target host"),
    ("/tools", "List and manage available tools"),
    ("/notes", "Show saved findings"),
    ("/report", "Generate report from session"),
    ("/mcp list", "List configured MCP servers"),
    ("/mcp add stdio <name> <command> [args...]", "Add STDIO MCP server"),
    ("/mcp add sse <name> <url>", "Add SSE/HTTP MCP server"),
    ("/workspace list", "List all workspaces"),
    ("/workspace info <name>", "Show workspace info"),
    ("/workspace note <text>", "Add note to active workspace"),
    ("/workspace clear", "Deactivate current workspace"),
    ("/workspace help", "Show workspace help"),
    ("/workspace <name>", "Create or activate workspace"),
    ("/spawn <task>", "Spawn child MCP agent"),
    ("/despawn <server_name>", "Despawn child MCP agent"),
    ("/conversations", "Browse saved conversations"),
    ("/clear", "Clear chat history"),
    ("/memory", "Show memory statistics"),
    ("/token", "Show token usage statistics"),
    ("/prompt", "Show system prompt"),
    ("/help", "Show help"),
    ("/quit", "Exit PentestAgent"),
]


def _is_placeholder(token: str) -> bool:
    return (token.startswith("<") and token.endswith(">")) or (
        token.startswith("[") and token.endswith("]")
    )


def _sig_matches(sig: str, value: str) -> bool:
    """Return True if the current input is a valid prefix path of the signature."""
    sig_tokens = sig.split()
    stripped = value.rstrip()
    has_trailing = bool(value) and value[-1] == " "
    val_tokens = stripped.split() if stripped else []

    completed = val_tokens if has_trailing else val_tokens[:-1]
    partial = "" if has_trailing else (val_tokens[-1] if val_tokens else "")

    if len(completed) > len(sig_tokens):
        return False

    for i, tok in enumerate(completed):
        sig_tok = sig_tokens[i]
        if _is_placeholder(sig_tok):
            continue
        if sig_tok != tok:
            return False

    if partial:
        next_idx = len(completed)
        if next_idx >= len(sig_tokens):
            return False
        sig_tok = sig_tokens[next_idx]
        if _is_placeholder(sig_tok):
            return True
        return sig_tok.startswith(partial)

    return True


def _get_display_parts(sig: str, value: str) -> tuple:
    """Return (next_token, remaining_tokens_str) for rendering the suggestion row."""
    sig_tokens = sig.split()
    stripped = value.rstrip()
    has_trailing = bool(value) and value[-1] == " "
    val_tokens = stripped.split() if stripped else []

    next_idx = len(val_tokens) if has_trailing else max(0, len(val_tokens) - 1)
    next_tok = sig_tokens[next_idx] if next_idx < len(sig_tokens) else ""
    remaining = (
        " ".join(sig_tokens[next_idx + 1 :]) if next_idx + 1 < len(sig_tokens) else ""
    )
    return next_tok, remaining


def _tab_complete(sig: str, value: str) -> str:
    """Return new input value produced by Tab-completing the given signature."""
    sig_tokens = sig.split()
    stripped = value.rstrip()
    has_trailing = bool(value) and value[-1] == " "
    val_tokens = stripped.split() if stripped else []

    next_idx = len(val_tokens) if has_trailing else max(0, len(val_tokens) - 1)
    if next_idx >= len(sig_tokens):
        return value

    kept = val_tokens[:next_idx]
    return " ".join(kept + [sig_tokens[next_idx]]) + " "


class CommandSuggestions(Widget):
    """Floating autocomplete dropdown for slash commands."""

    DEFAULT_CSS = """
    CommandSuggestions {
        display: none;
        width: 100%;
        height: auto;
        max-height: 12;
        background: #1a1a1a;
        border: round #383838;
        padding: 0;
        margin: 0 2;
        overflow-y: auto;
    }
    CommandSuggestions .suggestion-item {
        width: 100%;
        height: 1;
        padding: 0 1;
    }
    CommandSuggestions .suggestion-item.--selected {
        background: #252525;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._matches: List[tuple] = []
        self._selected: int = 0
        self._current_value: str = ""

    def compose(self) -> ComposeResult:
        return iter([])

    def update_suggestions(self, value: str) -> None:
        self._current_value = value
        self._matches = [
            (sig, desc) for sig, desc in COMMAND_SIGNATURES if _sig_matches(sig, value)
        ]
        self._selected = 0
        self._rebuild()
        self.display = bool(self._matches)

    def _rebuild(self) -> None:
        self.remove_children()
        for i, (sig, desc) in enumerate(self._matches):
            next_tok, remaining = _get_display_parts(sig, self._current_value)
            label = Text()
            if next_tok:
                if _is_placeholder(next_tok):
                    label.append(next_tok, style="bold #f59e0b")
                else:
                    label.append(next_tok, style="bold #38bdf8")
            if remaining:
                label.append(f" {remaining}", style="#4a4a4a")
            label.append(f"  {desc}", style="italic #4a4a4a")
            item = Static(label, classes="suggestion-item")
            if i == self._selected:
                item.add_class("--selected")
            self.mount(item)

    def select_next(self) -> None:
        if not self._matches:
            return
        self._selected = (self._selected + 1) % len(self._matches)
        self._highlight()

    def select_previous(self) -> None:
        if not self._matches:
            return
        self._selected = (self._selected - 1) % len(self._matches)
        self._highlight()

    def _highlight(self) -> None:
        children = list(self.children)
        for i, child in enumerate(children[: len(self._matches)]):
            if i == self._selected:
                child.add_class("--selected")
            else:
                child.remove_class("--selected")

    def get_tab_completion(self) -> Optional[str]:
        """Return new input value after Tab, or None if nothing to complete."""
        if not self._matches or self._selected >= len(self._matches):
            return None
        sig = self._matches[self._selected][0]
        return _tab_complete(sig, self._current_value)

    def hide(self) -> None:
        self._matches = []
        self._selected = 0
        self._current_value = ""
        self.display = False
        self.remove_children()


def wrap_text_lines(text: str, width: int = 80) -> List[str]:
    """
    Wrap text content preserving line breaks and wrapping long lines.

    Args:
        text: The text to wrap
        width: Maximum width per line (default 80 for safe terminal fit)

    Returns:
        List of wrapped lines
    """
    result = []
    for line in text.split("\n"):
        if len(line) <= width:
            result.append(line)
        else:
            # Wrap long lines
            wrapped = textwrap.wrap(
                line, width=width, break_long_words=False, break_on_hyphens=False
            )
            result.extend(wrapped if wrapped else [""])
    return result


# ----- Help Screen -----


class HelpScreen(ModalScreen):
    """Help modal"""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
    ]

    CSS = """
    HelpScreen {
        align: center middle;
        scrollbar-background: #1a1a1a;
        scrollbar-background-hover: #1a1a1a;
        scrollbar-background-active: #1a1a1a;
        scrollbar-color: #3a3a3a;
        scrollbar-color-hover: #3a3a3a;
        scrollbar-color-active: #3a3a3a;
        scrollbar-corner-color: #1a1a1a;
        scrollbar-size: 1 1;
    }

    #help-container {
        width: 110;
        height: 34;
        background: #121212;
        border: solid #3a3a3a;
        padding: 1 2;
        layout: vertical;
    }

    #help-title {
        text-align: center;
        text-style: bold;
        color: #d4d4d4;
        margin-bottom: 1;
    }

    #help-content {
        color: #9a9a9a;
    }


    #help-close {
        margin-top: 1;
        width: auto;
        min-width: 10;
        background: #1a1a1a;
        color: #9a9a9a;
        border: none;
    }

    #help-close:hover {
        background: #262626;
    }

    #help-close:focus {
        background: #262626;
        text-style: none;
    }
    """

    def compose(self) -> ComposeResult:
        yield Container(
            Static("PentestAgent Help", id="help-title"),
            Static(self._get_help_text(), id="help-content"),
            Center(Button("Close", id="help-close")),
            id="help-container",
        )

    def _get_help_text(self) -> str:
        header = (
            "[bold]Modes:[/] Assist | Agent | Crew | Interact\n"
            "[bold]Keys:[/] Enter=Send  Up/Down=History  Ctrl+Q=Quit\n"
            "[bold]Rewind:[/] Click 'rewind' on your messages to undo from that point\n\n"
            "[bold]Commands:[/]\n"
        )

        cmds = [
            ("/assist <task>", "Run in assist mode"),
            ("/agent <task>", "Run in agent mode"),
            ("/crew <task>", "Run multi-agent crew mode"),
            ("/interact <task>", "Run in interact mode"),
            (
                "/spawn \\[target] [--scope CIDR] [--model M] [--no-rag] [--no-mcp]",
                "Spawn child MCP agent",
            ),
            ("/despawn <server_name>", "Despawn child MCP agent"),
            ("/target <host>", "Set target"),
            ("/workspace <name|list>", "Manage workspaces"),
            ("/prompt", "Show system prompt"),
            ("/memory", "Show memory stats"),
            ("/token", "Show token usage & cost"),
            ("/notes", "Show saved notes"),
            ("/report", "Generate report"),
            ("/help", "Show help"),
            ("/clear", "Clear chat"),
            ("/tools", "List tools"),
            ("/conversations", "Browse & restore saved conversations"),
            ("/mcp", "List mcp servers"),
            ("/quit", "Exit"),
        ]

        # Determine consistent width for command column so the dash aligns.
        # Use visual length (\[ renders as [ in Rich, subtract the backslash).
        def _vlen(s: str) -> int:
            return len(s.replace("\\[", "["))

        cmd_col_width = max(_vlen(c) for c, _ in cmds) + 3
        lines = []
        for cmd, desc in cmds:
            pad = " " * (cmd_col_width - _vlen(cmd))
            lines.append(f"  {cmd}{pad}- {desc}")

        return header + "\n".join(lines)

    def action_dismiss(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#help-close")
    def close_help(self) -> None:
        self.app.pop_screen()


class WorkspaceHelpScreen(ModalScreen):
    """Help modal for workspace commands."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
    ]

    CSS = """
    WorkspaceHelpScreen {
        align: center middle;
        scrollbar-background: #1a1a1a;
        scrollbar-background-hover: #1a1a1a;
        scrollbar-background-active: #1a1a1a;
        scrollbar-color: #3a3a3a;
        scrollbar-color-hover: #3a3a3a;
        scrollbar-color-active: #3a3a3a;
        scrollbar-corner-color: #1a1a1a;
        scrollbar-size: 1 1;
    }

    #help-container {
        width: 60;
        height: 26;
        background: #121212;
        border: solid #3a3a3a;
        padding: 1 2;
        layout: vertical;
    }

    #help-title {
        text-align: center;
        text-style: bold;
        color: #d4d4d4;
        margin-bottom: 1;
    }

    #help-content {
        color: #9a9a9a;
    }


    #help-close {
        margin-top: 1;
        width: auto;
        min-width: 10;
        background: #1a1a1a;
        color: #9a9a9a;
        border: none;
    }

    #help-close:hover {
        background: #262626;
    }

    #help-close:focus {
        background: #262626;
        text-style: none;
    }
    """

    def compose(self) -> ComposeResult:
        from rich.table import Table
        from rich.text import Text

        # Build a two-column table to prevent wrapping
        table = Table.grid(padding=(0, 3))
        table.add_column(justify="left", ratio=2)
        table.add_column(justify="left", ratio=3)

        # Header and usage
        header = Text("Workspace Commands", style="bold")
        usage = Text("Usage: /workspace <action> or /workspace <name>")

        # Commands list
        cmds = [
            ("/workspace", "Show active"),
            ("/workspace list", "List all workspaces"),
            ("/workspace info [NAME]", "Show workspace metadata"),
            ("/workspace note <text>", "Add operator note"),
            ("/workspace clear", "Deactivate workspace"),
            ("/workspace NAME", "Create or activate workspace"),
            ("/workspace help", "Show this help"),
        ]

        # Compose table rows
        table.add_row(Text("Commands:", style="bold"), Text(""))

        for left, right in cmds:
            table.add_row(left, right)

        yield Container(
            Static(header, id="help-title"),
            Static(usage, id="help-usage"),
            Static(table, id="help-content"),
            Center(Button("Close", id="help-close"), id="help-center"),
            id="help-container",
        )

    def _get_help_text(self) -> str:
        header = "Usage: /workspace <action> or /workspace <name>\n"
        cmds = [
            ("/workspace", "Show active"),
            ("/workspace list", "List all workspaces"),
            ("/workspace info [NAME]", "Show workspace metadata"),
            ("/workspace note <text>", "Add operator note"),
            ("/workspace clear", "Deactivate workspace"),
            ("/workspace NAME", "Create or activate workspace"),
            ("/workspace help", "Show this help"),
        ]

        # Build two-column layout with fixed left column width
        left_width = 44
        lines = [header, "Commands:\n"]
        for left, right in cmds:
            if len(left) >= left_width - 2:
                # if left is long, place on its own line
                lines.append(f"  {left}\n    {right}")
            else:
                pad = " " * (left_width - len(left))
                lines.append(f"  {left}{pad}{right}")

        return "\n".join(lines)

    def action_dismiss(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#help-close")
    def close_help(self) -> None:
        self.app.pop_screen()


class ToolsScreen(ModalScreen):
    """Interactive tools browser — split-pane layout.

    Left pane: tree of tools. Right pane: full description (scrollable).
    Selecting another tool replaces the right-pane content. Close returns
    to the main screen.
    """

    BINDINGS = [Binding("escape", "dismiss", "Close"), Binding("q", "dismiss", "Close")]

    CSS = """
    ToolsScreen { align: center middle; }
    """
    from ..tools import Tool

    def __init__(self, tools: List[Tool], tui: "PentestAgentTUI") -> None:
        from ..tools import Tool

        super().__init__()
        self.tools = tools
        self.selected_tool: Optional[Tool] = None
        self.tui = tui

    def compose(self) -> ComposeResult:
        # Build a split view: left tree, right description
        with Container(id="tools-container"):
            with Horizontal(id="tools-split"):
                with Vertical(id="tools-left"):
                    yield Static("Tools", id="tools-title")
                    yield Tree("TOOLS", id="tools-tree")

                with Vertical(id="tools-right"):
                    yield Button("Enabled: OFF", id="tool-toggle-enabled")
                    yield Static("Description", id="tools-desc-title")
                    yield ScrollableContainer(
                        Static("Select a tool to view details.", id="tools-desc"),
                        id="tools-desc-scroll",
                    )

            yield Center(Button("Close", id="tools-close"))

    def on_mount(self) -> None:
        try:
            tree = self.query_one("#tools-tree", Tree)
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to query tools tree: %s", e)
            try:
                from ..interface.notifier import notify

                notify("warning", f"TUI: failed to initialize tools tree: {e}")
            except Exception as e:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about tools tree init failure: %s", e
                )
            return

        root = tree.root
        root.allow_expand = True
        root.show_root = False

        # Populate tool nodes
        for t in self.tools:
            name = getattr(t, "name", str(t))
            root.add(name, data={"tool": t})

        # Hide toggle button initially
        toggle_btn = self.query_one("#tool-toggle-enabled", Button)
        toggle_btn.display = False

        try:
            tree.focus()
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to focus tools tree: %s", e)
            try:
                from ..interface.notifier import notify

                notify("warning", f"TUI: failed to focus tools tree: {e}")
            except Exception as e:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about tools tree focus failure: %s", e
                )

    @on(Tree.NodeSelected, "#tools-tree")
    def on_tool_selected(self, event: Tree.NodeSelected) -> None:
        node = event.node
        try:
            tool = node.data.get("tool") if node.data else None
            self.selected_tool = tool
            name = getattr(tool, "name", str(tool)) if tool else "Unknown"

            # Prefer Tool.description (registered tools use this), then fall back
            desc = None
            tool_enabled = False
            if tool is not None:
                desc = getattr(tool, "description", None)
                if not desc:
                    desc = (
                        getattr(tool, "summary", None)
                        or getattr(tool, "help_text", None)
                        or getattr(tool, "__doc__", None)
                    )

                tool_enabled = getattr(tool, "enabled", False)

            if not desc:
                desc = "No description available."

            # Update right-hand description pane
            try:
                desc_widget = self.query_one("#tools-desc", Static)
                toggle_btn = self.query_one("#tool-toggle-enabled", Button)
                text = Text()
                text.append(f"{name}\n", style="bold #d4d4d4")
                text.append(str(desc), style="#d4d4d4")
                desc_widget.update(text)

                if tool:
                    enabled_icon = "ON" if tool_enabled else "OFF"
                    toggle_btn.display = True
                    toggle_btn.label = f"Enabled: {enabled_icon}"
                else:
                    toggle_btn.display = False

            except Exception as e:
                logging.getLogger(__name__).exception(
                    "Failed to update tool description pane: %s", e
                )
                try:
                    from ..interface.notifier import notify

                    notify("warning", f"TUI: failed to update tool description: {e}")
                except Exception as e:
                    logging.getLogger(__name__).exception(
                        "Failed to notify operator about tool desc update failure: %s",
                        e,
                    )
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Unhandled error in on_tool_selected: %s", e
            )
            try:
                from ..interface.notifier import notify

                notify("warning", f"TUI: error handling tool selection: {e}")
            except Exception as e:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about tool selection error: %s", e
                )

    @on(Button.Pressed, "#tools-close")
    def close_tools(self) -> None:
        self.app.pop_screen()

    # ------------------------------------------------------------

    @on(Button.Pressed, "#tool-toggle-enabled")
    async def toggle_enabled(self) -> None:

        try:

            tool = self.selected_tool
            if tool is None:
                return

            tool.enabled = not tool.enabled

            await self._refresh_tool_widget()

        except Exception as e:
            logging.getLogger(__name__).exception("Toggle failed: %s", e)
            try:
                from ..interface.notifier import notify

                # Make best effort naming
                tool_name = getattr(tool, "name", None) or (
                    tool.get("name") if isinstance(tool, dict) else str(tool)
                )
                notify("error", f"Failed to toggle tool {tool_name}: {e}")
            except Exception:
                pass
            return

    async def _refresh_tool_widget(self) -> None:
        if self.selected_tool:
            # Simulate reselecting same node
            dummy = type("Node", (), {"data": {"tool": self.selected_tool}})
            event = type("Evt", (), {"node": dummy})
            self.on_tool_selected(event)
            self.tui._update_header()


class ConversationsScreen(ModalScreen):
    """Conversation history browser — split-pane layout.

    Left pane: list of saved conversations (title + date).
    Right pane: metadata preview of the selected entry.
    Buttons: Restore (loads the conversation) + Close.
    Dismisses with the selected ConversationMeta, or None to cancel.
    """

    BINDINGS = [
        Binding("escape", "cancel_screen", "Close"),
        Binding("q", "cancel_screen", "Close"),
    ]

    CSS = """
    ConversationsScreen { align: center middle; }
    #conv-prefs-row {
        height: 3;
        align: center middle;
        padding: 0 2;
    }
    #conv-prefs-label {
        padding: 0 1;
        color: #9a9a9a;
    }
    """

    def __init__(self, conversations: list, store) -> None:
        super().__init__()
        self._conversations = conversations
        self._store = store
        self._selected = None

    def compose(self) -> ComposeResult:
        with Container(id="conv-container"):
            with Horizontal(id="conv-split"):
                with Vertical(id="conv-left"):
                    yield Static("Saved Conversations", id="conv-title")
                    yield Tree("CONVERSATIONS", id="conv-tree")
                with Vertical(id="conv-right"):
                    yield Static("Preview", id="conv-preview-title")
                    yield ScrollableContainer(
                        Static("Select a conversation to preview.", id="conv-preview"),
                        id="conv-preview-scroll",
                    )
            with Horizontal(id="conv-prefs-row"):
                yield Switch(id="conv-auto-reload", value=False)
                yield Static(
                    "Auto-reload last session on startup", id="conv-prefs-label"
                )
            with Center():
                yield Button("Restore", id="conv-restore", disabled=True)
                yield Button("Close", id="conv-close")

    def on_mount(self) -> None:
        tree = self.query_one("#conv-tree", Tree)
        root = tree.root
        root.allow_expand = True
        root.show_root = False
        for meta in self._conversations:
            label = f"{meta.title[:40]}  [{meta.created_at[:10]}]  ({meta.message_count} msgs)"
            root.add(label, data={"meta": meta})
        if not self._conversations:
            try:
                self.query_one("#conv-preview", Static).update(
                    "No saved conversations found."
                )
            except Exception:
                pass
        try:
            tree.focus()
        except Exception:
            pass
        # Load auto-reload preference
        try:
            import json as _json

            from ..workspaces.utils import get_preferences_file

            prefs_file = get_preferences_file()
            if prefs_file.exists():
                prefs = _json.loads(prefs_file.read_text(encoding="utf-8"))
                value = bool(prefs.get("auto_reload_session", False))
            else:
                value = False
            self.query_one("#conv-auto-reload", Switch).value = value
        except Exception:
            pass

    @on(Switch.Changed, "#conv-auto-reload")
    def on_auto_reload_changed(self, event: Switch.Changed) -> None:
        try:
            import json as _json

            from ..workspaces.utils import get_preferences_file

            prefs_file = get_preferences_file()
            prefs = {}
            if prefs_file.exists():
                try:
                    prefs = _json.loads(prefs_file.read_text(encoding="utf-8"))
                except Exception:
                    prefs = {}
            prefs["auto_reload_session"] = event.value
            prefs_file.write_text(_json.dumps(prefs, indent=2), encoding="utf-8")
        except Exception:
            pass

    @on(Tree.NodeSelected, "#conv-tree")
    def on_conv_selected(self, event: Tree.NodeSelected) -> None:
        meta = event.node.data.get("meta") if event.node.data else None
        self._selected = meta
        try:
            self.query_one("#conv-restore", Button).disabled = meta is None
        except Exception:
            pass
        if meta is None:
            return
        try:
            from rich.text import Text as RichText

            text = RichText()
            text.append(f"{meta.title}\n", style="bold #d4d4d4")
            text.append(
                f"Date:     {meta.created_at[:19].replace('T', ' ')}  |  ",
                style="#9a9a9a",
            )
            text.append(f"Messages: {meta.message_count}\n", style="#9a9a9a")
            text.append("─" * 40 + "\n", style="#444444")

            messages = self._store.load(meta.id)
            shown = 0
            for msg in messages:
                if shown >= 5:
                    remaining = len(messages) - shown
                    text.append(f"\n… {remaining} more message(s)", style="#6a6a6a")
                    break
                if msg.role == "user":
                    snippet = (msg.content or "").replace("\n", " ").strip()[:200]
                    text.append("\nYou: ", style="bold #7ec8e3")
                    text.append(snippet + "\n", style="#d4d4d4")
                    shown += 1
                elif msg.role == "assistant":
                    if msg.tool_calls:
                        for tc in msg.tool_calls:
                            text.append("\n[tool] ", style="bold #e3c07e")
                            text.append(f"{tc.name}\n", style="#d4d4d4")
                            shown += 1
                            if shown >= 5:
                                break
                    elif msg.content and msg.content.strip():
                        snippet = msg.content.replace("\n", " ").strip()[:200]
                        text.append("\nAgent: ", style="bold #a8cc8c")
                        text.append(snippet + "\n", style="#d4d4d4")
                        shown += 1
                elif msg.role == "tool_result" and msg.tool_results:
                    for tr in msg.tool_results:
                        result_text = (
                            (tr.result or tr.error or "")
                            .replace("\n", " ")
                            .strip()[:150]
                        )
                        text.append(f"\n  ↳ {tr.tool_name}: ", style="#9a9a9a")
                        text.append(result_text + "\n", style="#888888")
                        shown += 1
                        if shown >= 5:
                            break

            self.query_one("#conv-preview", Static).update(text)
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to update conversation preview: %s", e
            )

    @on(Button.Pressed, "#conv-restore")
    def restore_conversation(self) -> None:
        if self._selected:
            self.dismiss(self._selected)

    @on(Button.Pressed, "#conv-close")
    def close_screen(self) -> None:
        self.dismiss(None)

    def action_cancel_screen(self) -> None:
        self.dismiss(None)


class MCPScreen(ModalScreen):
    """Interactive MCP browser — split-pane layout."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
    ]

    CSS = """
    MCPScreen { align: center middle; }
    """

    from ..agents.pa_agent import PentestAgentAgent
    from ..mcp import MCPManager, MCPServerConfig, SSEServerConfig, StdioServerConfig

    def __init__(
        self, mcp_manager: MCPManager, agent: PentestAgentAgent, tui: "PentestAgentTUI"
    ) -> None:
        super().__init__()
        self.mcp_manager = mcp_manager
        self.agent = agent
        self.tui = tui
        self.selected_server = None
        self.selected_tool = None

    # ------------------------------------------------------------

    def compose(self) -> ComposeResult:
        with Container(id="mcp-container"):
            with Horizontal(id="mcp-split"):

                # LEFT SIDE
                with Vertical(id="mcp-left"):
                    yield Static("MCP Servers", id="mcp-title")
                    yield Tree("MCP Servers", id="mcp-tree")

                # RIGHT SIDE
                with Vertical(id="mcp-right"):
                    # ---- Toggle Button ----
                    yield Button("Enabled: OFF", id="mcp-toggle-enabled")
                    yield Static("Description", id="mcp-desc-title")

                    yield ScrollableContainer(
                        Static("Select a MCP server to view details.", id="mcp-desc"),
                        id="mcp-desc-scroll",
                    )

            yield Center(Button("Close", id="mcp-close"))

    # ------------------------------------------------------------

    def on_mount(self) -> None:
        try:
            tree = self.query_one("#mcp-tree", Tree)
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to query MCP tree: %s", e)
            return

        root = tree.root
        root.allow_expand = True
        root.show_root = False

        servers = self.mcp_manager.get_all_servers()

        for server in servers:
            server_node = root.add(server.name, data={"server": server})
            for tool in server.tools:
                server_node.add(tool["name"], data={"tool": tool})

        # Hide toggle button initially
        toggle_btn = self.query_one("#mcp-toggle-enabled", Button)
        toggle_btn.display = False

        try:
            tree.focus()
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to focus MCP tree: %s", e)

    # ------------------------------------------------------------

    @on(Tree.NodeSelected, "#mcp-tree")
    def on_mcp_selected(self, event: Tree.NodeSelected) -> None:
        from ..mcp import MCPServer, SSEServerConfig, StdioServerConfig

        node = event.node

        self.selected_server = node.data.get("server") if node.data else None
        self.selected_tool = node.data.get("tool") if node.data else None

        desc_widget = self.query_one("#mcp-desc", Static)
        toggle_btn = self.query_one("#mcp-toggle-enabled", Button)

        text = Text()

        if self.selected_server is not None:
            mcp: MCPServer = self.selected_server

            text.append(f"{mcp.name}\n", style="bold #d4d4d4")
            text.append(f"{mcp.config.description}\n\n", style="#d4d4d4")

            text.append(f"Type: {mcp.config.type}\n", style="#9a9a9a")

            if isinstance(mcp.config, SSEServerConfig):
                text.append(f"URL: {mcp.config.url}\n", style="#9a9a9a")

            elif isinstance(mcp.config, StdioServerConfig):
                text.append(f"Command: {mcp.config.command}\n", style="#9a9a9a")
                text.append(f"Args: {mcp.config.args}\n\n", style="#9a9a9a")

            enabled_icon = "ON" if mcp.config.enabled else "OFF"
            connected_icon = "ON" if mcp.connected else "OFF"

            text.append(f"Connected: {connected_icon}\n", style="#9a9a9a")

            if mcp.last_error:
                text.append(f"\nLast error: {mcp.last_error}\n", style="#e91b1b")

            logs = mcp.get_logs()

            if logs:
                text.append(f"\n{logs}\n", style="#86e41a")

            desc_widget.update(text)

            toggle_btn.display = True
            toggle_btn.label = f"Enabled: {enabled_icon}"

        elif self.selected_tool is not None:
            text.append(f"{self.selected_tool['description']}\n", style="#d4d4d4")
            desc_widget.update(text)
            toggle_btn.display = False

        else:
            desc_widget.update("Choose a server.")
            toggle_btn.display = False

    # ------------------------------------------------------------

    @on(Button.Pressed, "#mcp-toggle-enabled")
    async def toggle_enabled(self) -> None:
        mcp = self.selected_server
        if mcp is None:
            return

        try:
            new_value = not mcp.config.enabled

            if new_value:
                await self.mcp_manager.enable(mcp.name)
                tools = self.mcp_manager.create_mcp_tools_from_server(mcp)
                self.agent.add_tools(tools)
            else:
                tools = self.mcp_manager.create_mcp_tools_from_server(mcp)
                self.agent.delete_tools(tools)
                await self.mcp_manager.disable(mcp.name)

            self.tui._update_header()

        except Exception as e:
            logging.getLogger(__name__).exception("Toggle failed: %s", e)
            try:
                from ..interface.notifier import notify

                notify("error", f"Failed to toggle {mcp.name}: {e}")
            except Exception:
                pass
            return

        # Refresh UI
        self._refresh_description()

    # ------------------------------------------------------------

    def _refresh_description(self):
        """Rebuild right-hand side using current selection."""
        if self.selected_server:
            # Simulate reselecting same node
            dummy = type("Node", (), {"data": {"server": self.selected_server}})
            event = type("Evt", (), {"node": dummy})
            self.on_mcp_selected(event)

    # ------------------------------------------------------------

    @on(Button.Pressed, "#mcp-close")
    def close_mcp(self) -> None:
        self.app.pop_screen()


# ----- MCP task event message (for safe cross-task UI updates) -----


class MCPTaskEvent(Message):
    """Posted by on_mcp_event() so Textual handles the UI update safely."""

    def __init__(self, event: str, data: dict) -> None:
        super().__init__()
        self.event = event
        self.data = data


class SpawnTerminalMessage(Message):
    """Posted when a child agent requests an EmbeddedTerminal widget."""

    def __init__(self, master_fd: int, label: str) -> None:
        super().__init__()
        self.master_fd = master_fd
        self.label = label


class DespawnTerminalMessage(Message):
    """Posted when a child agent has been despawned and its terminal should be removed."""

    def __init__(self, label: str) -> None:
        super().__init__()
        self.label = label


class ChildAgentWakeUpMessage(Message):
    """Posted (thread-safely) when a child async task completes and the parent
    agent is idle.  Triggers _run_wake_up_mode() through Textual's message loop
    so we never call @work methods from an arbitrary async context."""


# ----- Rewind confirmation modal -----


class RewindConfirmScreen(ModalScreen[bool]):
    """Small confirmation dialog before rewinding the conversation."""

    BINDINGS = [
        Binding("escape", "dismiss_false", "Cancel"),
        Binding("n", "dismiss_false", "No"),
        Binding("y", "dismiss_true", "Yes"),
    ]

    CSS = """
    RewindConfirmScreen {
        align: center middle;
    }
    #rewind-confirm-container {
        width: 52;
        height: 11;
        background: #121212;
        border: solid #3a3a3a;
        padding: 1 2;
        layout: vertical;
    }
    #rewind-confirm-title {
        text-align: center;
        color: #d4d4d4;
        height: 3;
        content-align: center middle;
    }
    #rewind-yes {
        width: 12;
        background: #1a1a1a;
        color: #e07070;
        border: none;
        margin: 0 1;
    }
    #rewind-yes:hover { background: #2a1a1a; }
    #rewind-no {
        width: 12;
        background: #1a1a1a;
        color: #75d164;
        border: none;
        margin: 0 1;
    }
    #rewind-no:hover { background: #262626; }
    """

    def compose(self) -> ComposeResult:
        with Container(id="rewind-confirm-container"):
            yield Static(
                "Rewind conversation from this point?", id="rewind-confirm-title"
            )
            yield Center(
                Button("Yes  (y)", id="rewind-yes"), Button("No  (n)", id="rewind-no")
            )

    def action_dismiss_false(self) -> None:
        self.dismiss(False)

    def action_dismiss_true(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#rewind-yes")
    def confirm(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#rewind-no")
    def cancel(self) -> None:
        self.dismiss(False)


class ForkConfirmScreen(ModalScreen[bool]):
    """Confirmation dialog before forking — saves the current conversation first."""

    BINDINGS = [
        Binding("escape", "dismiss_false", "Cancel"),
        Binding("n", "dismiss_false", "No"),
        Binding("y", "dismiss_true", "Yes"),
    ]

    CSS = """
    ForkConfirmScreen {
        align: center middle;
    }
    #fork-confirm-container {
        width: 56;
        height: 13;
        background: #121212;
        border: solid #3a3a3a;
        padding: 1 2;
        layout: vertical;
    }
    #fork-confirm-title {
        text-align: center;
        color: #d4d4d4;
        height: 5;
        content-align: center middle;
    }
    #fork-yes {
        width: 12;
        background: #1a1a1a;
        color: #70a0e0;
        border: none;
        margin: 0 1;
    }
    #fork-yes:hover { background: #1a1a2a; }
    #fork-no {
        width: 12;
        background: #1a1a1a;
        color: #75d164;
        border: none;
        margin: 0 1;
    }
    #fork-no:hover { background: #262626; }
    """

    def compose(self) -> ComposeResult:
        with Container(id="fork-confirm-container"):
            yield Static(
                "Fork conversation from this point?\nThe current conversation will be saved.",
                id="fork-confirm-title",
            )
            yield Center(
                Button("Yes  (y)", id="fork-yes"), Button("No  (n)", id="fork-no")
            )

    def action_dismiss_false(self) -> None:
        self.dismiss(False)

    def action_dismiss_true(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#fork-yes")
    def confirm(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#fork-no")
    def cancel(self) -> None:
        self.dismiss(False)


# ----- Copy to clipboard button -----


class CopyButton(Static):
    """Minimal copy-to-clipboard button using Static instead of Button"""

    DEFAULT_CSS = """
    CopyButton {
        width: auto;
        height: 1;
        color: #6a6a6a;
        background: transparent;
        padding: 0 1;
    }
    CopyButton:hover {
        color: #d4d4d4;
        background: #2a2a2a;
    }
    CopyButton.-copied {
        color: #4ec994;
    }
    """

    def __init__(self, **kwargs):
        super().__init__("copy", **kwargs)

    def on_click(self, event: Click) -> None:
        self.post_message(CopyButton.Pressed(self))
        event.stop()

    class Pressed(Message):
        def __init__(self, button: "CopyButton") -> None:
            super().__init__()
            self.button = button


class RewindButton(Static):
    """Button to rewind conversation from this message."""

    DEFAULT_CSS = """
    RewindButton {
        width: auto;
        height: 1;
        color: #6a6a6a;
        background: transparent;
        padding: 0 1;
    }
    RewindButton:hover {
        color: #d4d4d4;
        background: #2a2a2a;
    }
    RewindButton.-active {
        color: #e07070;
    }
    """

    def __init__(self, **kwargs):
        super().__init__("<< rewind", **kwargs)

    def on_click(self, event: Click) -> None:
        self.post_message(RewindButton.Pressed(self))
        event.stop()

    class Pressed(Message):
        def __init__(self, button: "RewindButton") -> None:
            super().__init__()
            self.button = button


class ForkButton(Static):
    """Button to fork conversation from this message (saves current history first)."""

    DEFAULT_CSS = """
    ForkButton {
        width: auto;
        height: 1;
        color: #6a6a6a;
        background: transparent;
        padding: 0 1;
    }
    ForkButton:hover {
        color: #d4d4d4;
        background: #2a2a2a;
    }
    ForkButton.-active {
        color: #70a0e0;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(">> fork", **kwargs)

    def on_click(self, event: Click) -> None:
        self.post_message(ForkButton.Pressed(self))
        event.stop()

    class Pressed(Message):
        def __init__(self, button: "ForkButton") -> None:
            super().__init__()
            self.button = button


class CopyableMixin(Static):
    """Base class for messages with a copy button."""

    _copy_content: str = ""
    _header_text: Text = Text()
    _body_text: Text = Text()

    DEFAULT_CSS = """
    CopyableMixin { layout: vertical; padding: 0; }
    CopyableMixin .message-header { layout: horizontal; height: 1; width: 100%; }
    CopyableMixin .message-body { padding-left: 2; }
    CopyableMixin .btn-group { dock: right; width: auto; height: 1; layout: horizontal; background: transparent; }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(classes="message-header"):
            yield Static(self._header_text)
            with Horizontal(classes="btn-group"):
                yield CopyButton(classes="copy-btn")
        yield Static(self._body_text, classes="message-body")

    def on_copy_button_pressed(self, event: CopyButton.Pressed) -> None:

        try:
            pyperclip.copy(self._copy_content)
            btn = self.query_one(".copy-btn", CopyButton)
            btn.update("copied")
            btn.add_class("-copied")
            self.set_timer(2, self._reset_copy_btn)

        except Exception as e:
            logging.getLogger(__name__).exception("Failed to update status bar: %s", e)
            try:
                from .notifier import notify

                notify("warning", f"TUI: failed to copy output to the clipboard: {e}")
            except Exception as ne:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about status bar update failure: %s", ne
                )

    def _reset_copy_btn(self) -> None:
        btn = self.query_one(".copy-btn", CopyButton)
        btn.update("copy")
        btn.remove_class("-copied")


# ----- Main Chat Message Widgets -----


class ThinkingMessage(CopyableMixin):
    def __init__(self, content: str, **kwargs):
        super().__init__(**kwargs)
        self._copy_content = content
        self._header_text = Text.assemble(
            ("* ", "#9a9a9a"), ("Thinking", "bold #9a9a9a")
        )
        body = Text()
        for line in wrap_text_lines(content, width=90):
            body.append(f"{line}\n", style="#6b6b6b italic")
        self._body_text = body


class ToolMessage(Static):
    """Tool execution message"""

    TOOL_COLOR = "#9a9a9a"
    ARG_COLOR = "#6b6b6b"
    HINT_COLOR = "#6b6b6b"

    CHEVRON_COLLAPSED = ">"
    CHEVRON_EXPANDED = "v"
    HINT_TEXT = " (click to see result)"

    expanded: bool = reactive(False, layout=True)

    def __init__(self, tool_name: str, args: str = "", **kwargs):
        super().__init__(**kwargs)
        self.tool_name = tool_name
        self.tool_args = args
        self._result_widget: ToolResultMessage | None = None

    def render(self) -> Text:
        text = Text()

        chevron = self.CHEVRON_EXPANDED if self.expanded else self.CHEVRON_COLLAPSED

        # Header line
        text.append(f"{chevron} ", style=self.TOOL_COLOR)
        text.append(self.tool_name, style=self.TOOL_COLOR)

        # Hint text (only when result exists and is collapsed)
        if self._result_widget and not self.expanded:
            text.append(self.HINT_TEXT, style=self.HINT_COLOR)

        text.append("\n")

        # Tool arguments
        if self.tool_args:
            for line in wrap_text_lines(self.tool_args, width=110):
                text.append(f"  {line}\n", style=self.ARG_COLOR)

        return text

    def attach_result(self, result_widget: "ToolResultMessage") -> None:
        """Attach a ToolResultMessage widget below this message."""
        if self._result_widget is not None:
            return

        self._result_widget = result_widget
        self._result_widget.display = self.expanded

        # Mount directly after this widget
        self.mount(self._result_widget, after=self)

    def on_click(self) -> None:
        self.expanded = not self.expanded
        if self._result_widget:
            self._result_widget.display = self.expanded


class ToolResultMessage(CopyableMixin):
    RESULT_ICON = "#"
    RESULT_COLOR = "#124670"
    OUTPUT_COLOR = "#17606d"

    def __init__(self, tool_name: str, result: str = "", **kwargs):
        super().__init__(**kwargs)
        self.tool_name = tool_name
        self.result = result
        self._copy_content = result
        self._header_text = Text.assemble(
            (f"{self.RESULT_ICON} ", self.RESULT_COLOR),
            (f"{tool_name} output", self.RESULT_COLOR),
        )
        body = Text()
        if result:
            for line in wrap_text_lines(result, width=110):
                body.append(f"{line}\n", style=self.OUTPUT_COLOR)
        self._body_text = body


class AssistantMessage(CopyableMixin):
    def __init__(self, content: str, **kwargs):
        super().__init__(**kwargs)
        self._copy_content = content
        self._header_text = Text.assemble(
            (">> ", "#9a9a9a"), ("PentestAgent", "bold #d4d4d4")
        )
        body = Text()
        for line in wrap_text_lines(content, width=90):
            body.append(f"{line}\n", style="#d4d4d4")
        self._body_text = body


class UserMessage(CopyableMixin):
    def __init__(self, content: str, **kwargs):
        super().__init__(**kwargs)
        self._copy_content = content
        self._header_text = Text.assemble(("> ", "#9a9a9a"), ("You", "bold #d4d4d4"))
        body = Text()
        for line in wrap_text_lines(content, width=90):
            body.append(f"{line}\n", style="#d4d4d4")
        self._body_text = body

    def compose(self) -> ComposeResult:
        with Horizontal(classes="message-header"):
            yield Static(self._header_text)
            with Horizontal(classes="btn-group"):
                yield RewindButton(classes="rewind-btn")
                yield ForkButton(classes="fork-btn")
                yield CopyButton(classes="copy-btn")
        yield Static(self._body_text, classes="message-body")

    def on_rewind_button_pressed(self, event: RewindButton.Pressed) -> None:
        self.post_message(UserMessage.RewindPressed(self))

    def on_fork_button_pressed(self, event: ForkButton.Pressed) -> None:
        self.post_message(UserMessage.ForkPressed(self))

    class RewindPressed(Message):
        def __init__(self, user_message: "UserMessage") -> None:
            super().__init__()
            self.user_message = user_message

    class ForkPressed(Message):
        def __init__(self, user_message: "UserMessage") -> None:
            super().__init__()
            self.user_message = user_message


class SystemMessage(Static):
    """System message"""

    def __init__(self, content: str, **kwargs):
        super().__init__(**kwargs)
        self.message_content = content

    def render(self) -> Text:
        text = Text()
        for line in self.message_content.split("\n"):
            text.append(f"  {line}\n", style="#6b6b6b")  # phantom - subtle system text
        return text


# ----- Status Bar -----


class StatusBar(Static):
    """Animated status bar"""

    status = reactive("idle")
    mode = reactive("assist")  # "assist" or "agent"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._frame = 0
        self._timer: Optional[Timer] = None

    def on_mount(self) -> None:
        self._timer = self.set_interval(0.2, self._tick)

    def _tick(self) -> None:
        self._frame = (self._frame + 1) % 4
        if self.status not in ["idle", "complete"]:
            self.refresh()

    def render(self) -> Text:
        dots = "." * (self._frame + 1)

        # Use fixed-width labels (pad dots to 4 chars so text doesn't jump)
        dots_padded = dots.ljust(4)

        # PA theme status colors (muted, ethereal)
        status_map = {
            "idle": ("Ready", "#6b6b6b"),
            "initializing": (f"Initializing{dots_padded}", "#9a9a9a"),
            "thinking": (f"Thinking{dots_padded}", "#9a9a9a"),
            "running": (f"Running{dots_padded}", "#9a9a9a"),
            "processing": (f"Processing{dots_padded}", "#9a9a9a"),
            "waiting": ("Waiting for input", "#9a9a9a"),
            "complete": ("Complete", "#4a9f6e"),
            "error": ("Error", "#9f4a4a"),
        }

        label, color = status_map.get(self.status, (self.status, "#6b6b6b"))

        text = Text()

        # Show mode (ASCII-safe symbols)
        if self.mode == "crew":
            text.append("  :: Crew ", style="#9a9a9a")
        elif self.mode == "agent":
            text.append("  >> Agent ", style="#9a9a9a")
        elif self.mode == "interact":
            text.append("  >> Interact ", style="#9a9a9a")
        elif self.mode == "mcp":
            text.append("  [MCP] ", style="#6b9a9a")
        else:
            text.append("  >> Assist ", style="#9a9a9a")

        text.append(f"| {label}", style=color)

        if self.status not in ["idle", "initializing", "complete", "error"]:
            text.append("    ESC to stop", style="#525252")

        return text


class MemoryDiagnostics(Static):
    """Live memory diagnostics widget mounted into the chat area.

    This widget polls the agent's LLM memory stats periodically and
    renders a compact, updating diagnostics panel.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._timer: Optional[Timer] = None

    def on_mount(self) -> None:
        # Refresh periodically for a lively display
        self._timer = self.set_interval(0.8, self.refresh)

    def on_unmount(self) -> None:
        if self._timer:
            self._timer.stop()

    def _bar(self, ratio: float, width: int = 20) -> str:
        filled = int(max(0, min(1.0, ratio)) * width)
        return "█" * filled + "░" * (width - filled)

    def render(self) -> Text:
        text = Text()

        try:
            app = self.app
            agent = getattr(app, "agent", None)
            if not agent or not getattr(agent, "llm", None):
                text.append("Memory Diagnostics\n", style="bold #d4d4d4")
                text.append("Agent not initialized", style="#9a9a9a")
                return text

            stats = agent.llm.get_memory_stats()
            msgs = len(agent.conversation_history)
            llm_msgs = agent._format_messages_for_llm()
            current_tokens = agent.llm.memory.get_total_tokens(llm_msgs)

            budget = stats.get("token_budget") or 1
            thresh = stats.get("summarize_threshold") or budget
            recent_keep = stats.get("recent_to_keep", 5)
            has_summary = stats.get("has_summary", False)
            summarized_count = stats.get("summarized_message_count", 0)

            # Header
            text.append("Memory Diagnostics\n", style="bold #d4d4d4")

            # Use a consistent bar width for all bars and align labels
            bar_width = 28
            labels = ["Tokens:", "Messages:", "Retention:"]
            label_width = max(len(label_text) for label_text in labels)

            # Tokens line
            ratio = current_tokens / max(1, budget)
            bar = self._bar(ratio, width=bar_width)
            label = "Tokens:".ljust(label_width)
            text.append(
                f"{label} [{bar}] {current_tokens:,} / {budget:,}\n", style="#9a9a9a"
            )

            # Messages line (scale messages to an expected max window)
            expected_msgs_max = max(1, recent_keep * 6)
            mratio = min(1.0, msgs / expected_msgs_max)
            mbar = self._bar(mratio, width=bar_width)
            label = "Messages:".ljust(label_width)
            text.append(f"{label} [{mbar}] {msgs} active\n", style="#9a9a9a")

            # Retention / recent
            k_ratio = min(1.0, recent_keep / max(1, recent_keep))
            keep_bar = self._bar(k_ratio, width=bar_width)
            label = "Retention:".ljust(label_width)
            text.append(
                f"{label} [{keep_bar}] keeping last {recent_keep}\n", style="#9a9a9a"
            )

            # Summary status
            summary_state = "active" if has_summary else "inactive"
            emoji = "ON" if has_summary else "OFF"
            text.append(f"Summary: {emoji} {summary_state}\n", style="#9a9a9a")

            # Summarized / threshold
            text.append(
                f"Summarized: {summarized_count} / {thresh:,}\n", style="#9a9a9a"
            )
            text.append(f"Threshold: {thresh:,}\n", style="#9a9a9a")

        except Exception as e:
            text.append(f"Memory diagnostics error: {e}", style="#9a9a9a")

        return text


class TokenDiagnostics(Static):
    """Live token/cost diagnostics panel mounted into the chat area.

    Reads persisted daily usage from the token_tracker, computes cost
    using environment variables, and displays a simple ASCII progress bar.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._timer: Optional[Timer] = None

    def on_mount(self) -> None:
        # Refresh periodically for a lively display
        self._timer = self.set_interval(1.0, self.refresh)

    def on_unmount(self) -> None:
        if self._timer:
            self._timer.stop()

    def _bar(self, ratio: float, width: int = 28) -> str:
        """Block-style usage bar matching MemoryDiagnostics visuals."""
        r = max(0.0, min(1.0, ratio))
        filled = int(r * width)
        return "█" * filled + "░" * (width - filled)

    def render(self) -> Text:
        text = Text()
        try:
            import os

            # Lazy import of token_tracker (best-effort)
            try:
                from ..tools import token_tracker
            except Exception as e:
                logging.getLogger(__name__).exception(
                    "Failed to import token_tracker: %s", e
                )
                try:
                    from ..interface.notifier import notify

                    notify("warning", f"TUI: token tracker import failed: {e}")
                except Exception as e:
                    logging.getLogger(__name__).exception(
                        "Failed to notify operator about token_tracker import failure: %s",
                        e,
                    )
                token_tracker = None

            text.append("Token Usage Diagnostics\n", style="bold #d4d4d4")

            if not token_tracker:
                text.append(
                    "Token tracker not available (tools/token_tracker).\n",
                    style="#9a9a9a",
                )
                return text

            stats = token_tracker.get_stats_sync()

            # If a reset is pending (date changed), perform a reset now so daily
            # usage is accurate and visible to the user.
            reset_occurred = False
            if stats.get("reset_pending"):
                try:
                    token_tracker.record_usage_sync(0, 0)
                    stats = token_tracker.get_stats_sync()
                    reset_occurred = True
                except Exception as e:
                    logging.getLogger(__name__).exception(
                        "Token tracker reset failed: %s", e
                    )
                    try:
                        from ..interface.notifier import notify

                        notify("warning", f"Token tracker reset failed: {e}")
                    except Exception as e:
                        logging.getLogger(__name__).exception(
                            "Failed to notify operator about token tracker reset failure: %s",
                            e,
                        )

            # Extract values
            last_in = int(stats.get("last_input_tokens", 0) or 0)
            last_out = int(stats.get("last_output_tokens", 0) or 0)
            last_total = int(stats.get("last_total_tokens", 0) or 0)
            daily_usage = int(stats.get("daily_usage", 0) or 0)
            last_reset = stats.get("last_reset_date")
            current_date = stats.get("current_date")

            # (env parsing moved below)

            # Environment cost config
            def _parse_env(name: str):
                v = os.getenv(name)
                if v is None or v == "":
                    return None
                try:
                    return float(v)
                except Exception as e:
                    logging.getLogger(__name__).debug(
                        "Failed to parse env var %s: %s", name, e
                    )
                    return "INVALID"

            unified = _parse_env("COST_PER_MILLION")
            input_cost_per_m = _parse_env("INPUT_COST_PER_MILLION")
            output_cost_per_m = _parse_env("OUTPUT_COST_PER_MILLION")
            daily_limit = _parse_env("DAILY_TOKEN_LIMIT")

            # Determine if any env-based limits exist
            has_env_limits = any(
                v is not None
                for v in (unified, input_cost_per_m, output_cost_per_m, daily_limit)
            )

            # If nothing has been recorded yet (no tokens, no daily usage)
            # and no env limits are configured, show the concise sentinel only.
            if last_total == 0 and daily_usage == 0 and not has_env_limits:
                text.append("No token usage recorded\n", style="#9a9a9a")
                return text

            # Validate env vars
            env_errors = []
            if unified == "INVALID":
                env_errors.append("COST_PER_MILLION is not numeric")
            if input_cost_per_m == "INVALID":
                env_errors.append("INPUT_COST_PER_MILLION is not numeric")
            if output_cost_per_m == "INVALID":
                env_errors.append("OUTPUT_COST_PER_MILLION is not numeric")
            if daily_limit == "INVALID":
                env_errors.append("DAILY_TOKEN_LIMIT is not numeric")

            if env_errors:
                text.append("Environment configuration errors:\n", style="#ef4444")
                for e in env_errors:
                    text.append(f"  - {e}\n", style="#9a9a9a")
                text.append(
                    "\nSet environment variables correctly to compute costs.\n",
                    style="#9a9a9a",
                )
                return text

            # Compute costs
            if unified is not None:
                # Use unified cost for both input and output
                input_cost = (last_in / 1_000_000.0) * float(unified)
                output_cost = (last_out / 1_000_000.0) * float(unified)
            else:
                # Require per-direction costs to be present to compute
                if input_cost_per_m is None or output_cost_per_m is None:
                    text.append(
                        "Cost vars missing. Set COST_PER_MILLION or both INPUT_COST_PER_MILLION and OUTPUT_COST_PER_MILLION.\n",
                        style="#9a9a9a",
                    )
                    # Still show numeric token stats below
                    input_cost = output_cost = None
                else:
                    input_cost = (last_in / 1_000_000.0) * float(input_cost_per_m)
                    output_cost = (last_out / 1_000_000.0) * float(output_cost_per_m)

            total_cost = None
            if input_cost is not None and output_cost is not None:
                total_cost = input_cost + output_cost

            # Daily budget calculations per spec
            # Derive daily usage excluding last command (in case tracker already included it)
            daily_without_last = max(daily_usage - last_total, 0)
            new_daily_total = daily_without_last + last_total

            remaining_tokens = None
            percent_used = None
            if daily_limit is not None:
                try:
                    dl = float(daily_limit)
                    remaining_tokens = max(int(dl - new_daily_total), 0)
                    percent_used = (new_daily_total / max(1.0, dl)) * 100.0
                except Exception as e:
                    logging.getLogger(__name__).exception(
                        "Failed to compute daily limit values: %s", e
                    )
                    try:
                        from ..interface.notifier import notify

                        notify(
                            "warning", f"TUI: failed to compute daily token limit: {e}"
                        )
                    except Exception as e:
                        logging.getLogger(__name__).exception(
                            "Failed to notify operator about daily limit computation failure: %s",
                            e,
                        )
                    remaining_tokens = None

            # Render structured panel with aligned labels and block bars
            bar_width = 28
            labels = [
                "Last command:",
                "Cost:",
                "Daily usage:",
                "Remaining:",
                "Usage:",
                "Last reset:",
                "Current date:",
                "Reset occurred:",
            ]
            label_width = max(len(label_text) for label_text in labels)

            # Last command tokens
            label = "Last command:".ljust(label_width)
            text.append(
                f"{label} in={last_in:,} out={last_out:,} total={last_total:,}\n",
                style="#9a9a9a",
            )

            # Cost line
            label = "Cost:".ljust(label_width)
            if input_cost is not None and output_cost is not None:
                text.append(
                    f"{label} in=${input_cost:.6f} out=${output_cost:.6f} total=${total_cost:.6f}\n",
                    style="#9a9a9a",
                )
            else:
                text.append(
                    f"{label} not computed (missing env vars)\n",
                    style="#9a9a9a",
                )

            # Daily usage
            label = "Daily usage:".ljust(label_width)
            text.append(f"{label} {new_daily_total:,}\n", style="#9a9a9a")

            # Remaining tokens
            label = "Remaining:".ljust(label_width)
            if remaining_tokens is not None:
                text.append(f"{label} {remaining_tokens:,}\n", style="#9a9a9a")
            else:
                text.append(
                    f"{label} N/A (DAILY_TOKEN_LIMIT not set)\n",
                    style="#9a9a9a",
                )

            # Usage percent + bar
            label = "Usage:".ljust(label_width)
            if percent_used is not None:
                bar = self._bar(percent_used / 100.0, width=bar_width)
                text.append(
                    f"{label} [{bar}] {percent_used:.1f}%\n",
                    style="#9a9a9a",
                )
            else:
                text.append(f"{label} N/A\n", style="#9a9a9a")

            # Dates
            label = "Last reset:".ljust(label_width)
            text.append(f"{label} {last_reset}\n", style="#9a9a9a")
            label = "Current date:".ljust(label_width)
            text.append(f"{label} {current_date}\n", style="#9a9a9a")

            # Reset occurrence
            label = "Reset occurred:".ljust(label_width)
            text.append(
                f"{label} {'Yes' if reset_occurred else 'No'}\n",
                style="#9a9a9a",
            )

        except Exception as e:
            text.append(f"Token diagnostics error: {e}\n", style="#9a9a9a")

        return text


# ----- Resize Divider -----


class ResizeDivider(Widget):
    """Draggable vertical divider between the chat area and the agents panel.

    Drag left to expand the agents panel; drag right to shrink it (giving more
    room back to the parent chat area).  Hidden when the agents panel is not
    visible.
    """

    DEFAULT_CSS = """
    ResizeDivider {
        width: 2;
        height: 100%;
        background: #1a1a1a;
        color: #3a3a3a;
        display: none;
        content-align: center middle;
    }
    ResizeDivider.visible {
        display: block;
    }
    ResizeDivider:hover {
        background: #262626;
        color: #7878b0;
    }
    ResizeDivider.dragging {
        background: #262626;
        color: #9090d0;
    }
    """

    # Each row renders this single character — a thin vertical bar.
    _CHAR_IDLE = "│"
    _CHAR_ACTIVE = "┃"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._dragging: bool = False
        self._start_x: int = 0
        self._start_width: int = 84

    def render(self) -> Text:
        char = self._CHAR_ACTIVE if self._dragging else self._CHAR_IDLE
        h = max(1, self.size.height)
        return Text("\n".join([char] * h), no_wrap=True, overflow="fold")

    def on_mouse_down(self, event: events.MouseDown) -> None:
        self._dragging = True
        self._start_x = event.screen_x
        try:
            panel = self.app.query_one("#agents-panel")
            self._start_width = panel.size.width
        except Exception:
            self._start_width = 84
        self.add_class("dragging")
        self.refresh()
        self.capture_mouse()
        event.stop()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if not self._dragging:
            return
        # Drag left  → expand agents-panel (delta negative → new_width grows)
        # Drag right → shrink agents-panel (delta positive → new_width shrinks)
        delta = event.screen_x - self._start_x
        new_width = max(20, self._start_width - delta)
        try:
            panel = self.app.query_one("#agents-panel")
            panel.styles.width = new_width
        except Exception:
            pass
        event.stop()

    def on_mouse_up(self, event: events.MouseUp) -> None:
        if self._dragging:
            self._dragging = False
            self.remove_class("dragging")
            self.refresh()
            self.release_mouse()
        event.stop()


# ----- Main TUI App -----


class PentestAgentTUI(App):
    """Main PentestAgent TUI Application"""

    # ═══════════════════════════════════════════════════════════
    # PA THEME - Ethereal grays
    # ═══════════════════════════════════════════════════════════
    # Void:       #0a0a0a  (terminal black - the darkness)
    # Shadow:     #121212  (subtle surface)
    # Mist:       #1a1a1a  (panels, elevated)
    # Whisper:    #262626  (default borders)
    # Fog:        #3a3a3a  (hover states)
    # Apparition: #525252  (focus states)
    # Phantom:    #6b6b6b  (secondary text)
    # Spirit:     #9a9a9a  (normal text)
    # Specter:    #d4d4d4  (primary text)
    # Ectoplasm:  #f0f0f0  (highlights)
    # ═══════════════════════════════════════════════════════════

    CSS = """
    Screen {
        background: #0a0a0a;
    }

    #main-container {
        width: 100%;
        height: 100%;
        layout: horizontal;
    }

    /* Chat area - takes full width normally, fills remaining space with sidebar */
    #chat-area {
        width: 1fr;
        height: 100%;
    }

    #chat-area.with-sidebar {
        width: 1fr;
    }

    #chat-scroll {
        width: 100%;
        height: 1fr;
        background: transparent;
        padding: 1 2;
        scrollbar-background: #1a1a1a;
        scrollbar-background-hover: #1a1a1a;
        scrollbar-background-active: #1a1a1a;
        scrollbar-color: #3a3a3a;
        scrollbar-color-hover: #3a3a3a;
        scrollbar-color-active: #3a3a3a;
        scrollbar-corner-color: #1a1a1a;
        scrollbar-size: 1 1;
    }

    #input-container {
        width: 100%;
        height: 3;
        background: transparent;
        border: round #262626;
        margin: 0 2;
        padding: 0;
        layout: horizontal;
        align-vertical: middle;
    }

    #input-container:focus-within {
        border: round #525252;
    }

    #input-container:focus-within #chat-prompt {
        color: #d4d4d4;
    }

    #chat-prompt {
        width: auto;
        height: 100%;
        padding: 0 0 0 1;
        color: #6b6b6b;
        content-align-vertical: middle;
    }

    #chat-input {
        width: 1fr;
        height: 100%;
        background: transparent;
        border: none;
        padding: 0;
        margin: 0;
        color: #d4d4d4;
    }

    #chat-input:focus {
        border: none;
    }

    #chat-input > .input--placeholder {
        color: #6b6b6b;
        text-style: italic;
    }

    #chat-input:disabled {
        color: #525252;
        background: transparent;
    }

    #input-container.mcp-locked {
        border: round #1a1a1a;
        opacity: 0.5;
    }

    #tab-hint {
        display: none;
        width: auto;
        height: 100%;
        padding: 0 1;
        color: #3a3a3a;
        content-align-vertical: middle;
        text-style: italic;
    }

    #status-bar {
        width: 100%;
        height: 1;
        background: transparent;
        padding: 0 3;
        margin: 0;
    }

    .message {
        margin-bottom: 1;
    }

    /* Sidebar - hidden by default */
    #sidebar {
        width: 28;
        height: 100%;
        display: none;
        padding-right: 1;
    }

    #sidebar.visible {
        display: block;
    }

    #agents-panel {
        width: 84;
        height: 100%;
        display: none;
        padding-right: 1;
    }

    #agents-panel.visible {
        display: block;
    }

    #workers-tree {
        height: 1fr;
        background: transparent;
        border: round #262626;
        padding: 0 1;
        margin-bottom: 0;
    }

    #workers-tree:focus {
        border: round #3a3a3a;
    }

    #crew-stats {
        height: auto;
        max-height: 10;
        background: transparent;
        border: round #262626;
        border-title-color: #9a9a9a;
        border-title-style: bold;
        padding: 0 1;
        margin-top: 0;
    }

    Tree {
        background: transparent;
        color: #d4d4d4;
        scrollbar-background: #1a1a1a;
        scrollbar-background-hover: #1a1a1a;
        scrollbar-background-active: #1a1a1a;
        scrollbar-color: #3a3a3a;
        scrollbar-color-hover: #3a3a3a;
        scrollbar-color-active: #3a3a3a;
        scrollbar-size: 1 1;
    }

    Tree > .tree--cursor {
        background: transparent;
    }

    Tree > .tree--highlight {
        background: transparent;
    }

    Tree > .tree--highlight-line {
        background: transparent;
    }

    .tree--node-label {
        padding: 0 1;
    }

    .tree--node:hover .tree--node-label {
        background: transparent;
    }

    .tree--node.-selected .tree--node-label {
        background: transparent;
        color: #d4d4d4;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit_app", "Quit", priority=True),
        Binding("ctrl+c", "stop_agent", "Stop", priority=True, show=False),
        Binding("escape", "stop_agent", "Stop", priority=True),
        Binding("f1", "show_help", "Help"),
        Binding("tab", "focus_next", "Next", show=False),
        Binding("up", "history_up", "Prev", show=False),
        Binding("down", "history_down", "Next", show=False),
    ]

    TITLE = "PentestAgent"
    SUB_TITLE = "AI Penetration Testing"

    def __init__(
        self,
        target: Optional[str] = None,
        model: Optional[str] = None,
        use_docker: bool = False,
        mcp_mode: bool = False,
        prebuilt_components: Optional[Dict[str, Any]] = None,
        prebuilt_rag=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.target = target
        self.model = model or DEFAULT_MODEL
        self.use_docker = use_docker
        self._prebuilt_rag = prebuilt_rag

        # MCP observation mode: TUI is read-only and driven by an external MCP server.
        self.mcp_mode = mcp_mode
        self._prebuilt_components = prebuilt_components

        # Agent components
        self.agent: Optional["PentestAgentAgent"] = None
        self.runtime = None
        self.mcp_manager = None
        self.all_tools = []
        self.rag_engine = None  # RAG engine

        # State
        self._mode = (
            "mcp" if mcp_mode else "assist"
        )  # "assist", "agent", "crew", "interact", "mcp"
        self._is_running = False
        self._is_initializing = True  # Block input during init
        self._should_stop = False
        self._current_conv_id: Optional[str] = (
            None  # ID of the ongoing conversation on disk
        )

        # Per-task tool-message mapping for MCP observation mode
        self._mcp_tool_messages: Dict[str, Any] = {}
        # Worker handle returned by `@work` or an `asyncio.Task` (keep generic)
        self._current_worker: Optional[Any] = (
            None  # Track running worker for cancellation
        )
        self._current_crew = None  # Track crew orchestrator for cancellation

        # Crew mode state
        self._crew_workers: Dict[str, Dict[str, Any]] = {}
        self._crew_worker_nodes: Dict[str, TreeNode] = {}
        self._crew_orchestrator_node: Optional[TreeNode] = None
        self._crew_findings_count = 0
        self._viewing_worker_id: Optional[str] = None
        self._worker_events: Dict[str, List[Dict]] = {}
        self._crew_start_time: Optional[float] = None
        self._crew_tokens_used: int = 0
        self._crew_stats_timer: Optional[Timer] = None
        self._spinner_timer: Optional[Timer] = None
        self._spinner_frame: int = 0
        self._spinner_frames = [
            "⠋",
            "⠙",
            "⠹",
            "⠸",
            "⠼",
            "⠴",
            "⠦",
            "⠧",
            "⠇",
            "⠏",
        ]  # Braille dots spinner

        # Command history
        self._cmd_history: List[str] = []
        self._history_index: int = 0

        # Chat widgets list for rewind functionality
        self._chat_widgets: List[Widget] = []

    def compose(self) -> ComposeResult:
        with Horizontal(id="main-container"):
            # Chat area (left side)
            with Vertical(id="chat-area"):
                # Persistent header shown above the chat scroll so operator
                # always sees runtime/mode/target information.
                yield Static("", id="header")
                yield ScrollableContainer(id="chat-scroll")
                yield StatusBar(id="status-bar")
                yield CommandSuggestions(id="cmd-suggestions")
                with Horizontal(id="input-container"):
                    yield Static("> ", id="chat-prompt")
                    if self.mcp_mode:
                        yield Input(
                            placeholder="MCP Server Mode — read-only, tasks driven by MCP client",
                            id="chat-input",
                            disabled=True,
                        )
                    else:
                        yield Input(
                            placeholder="Enter task or type /help", id="chat-input"
                        )
                    yield Static("Press Tab to autocomplete", id="tab-hint")

            # Resize divider — hidden until agents panel is visible
            yield ResizeDivider(id="resize-divider")

            # Agents panel (right side, hidden by default; shows EmbeddedTerminal widgets)
            with Vertical(id="agents-panel"):
                pass

            # Sidebar (right side, hidden by default)
            with Vertical(id="sidebar"):
                yield CrewTree("CREW", id="workers-tree")
                yield Static("", id="crew-stats")

    async def on_mount(self) -> None:
        """Initialize on mount"""
        # Register notifier callback so other modules can emit operator-visible messages
        try:
            from .notifier import (
                register_agent_wake_up_callback,
                register_callback,
                register_despawn_terminal_callback,
                register_spawn_terminal_callback,
            )

            register_callback(self._notifier_callback)
            register_spawn_terminal_callback(self._spawn_terminal_callback)
            register_despawn_terminal_callback(self._despawn_terminal_callback)
            register_agent_wake_up_callback(self._on_agent_wake_up_callback)
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to register TUI notifier callback: %s", e
            )
            try:
                from .notifier import notify

                notify("warning", f"TUI: failed to register notifier callback: {e}")
            except Exception as ne:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about notifier registration failure: %s",
                    ne,
                )

        # Added, because the _notes variable is not properly loaded at the beginning and the notes.json is recreated unless you do a /notes command explicitely.
        from ..tools.notes import get_all_notes

        await get_all_notes()

        if self.mcp_mode:
            # Activate MCP observation mode using pre-built components.
            _ = cast(Any, self._activate_mcp_mode())
        else:
            # Call the textual worker - decorator returns a Worker, not a coroutine
            _ = cast(Any, self._initialize_agent())

    @work(thread=False)
    async def _initialize_agent(self) -> None:
        """Initialize agent using the shared component builder."""
        self._set_status("initializing")

        try:
            from ..tools import get_all_tools
            from .initializer import build_agent_components

            if not self.model:
                self._add_system(
                    "[!] No model configured. Set PENTESTAGENT_MODEL environment variable or create a .env file (see .env.example)."
                )
                self._set_status("error")
                self._is_initializing = False
                return

            if self.use_docker:
                self._add_system("+ Starting Docker container...")

            def _on_progress(level: str, msg: str) -> None:
                if level == "warning":
                    self._add_system(f"[!] {msg}")
                # info messages are omitted from TUI chat to keep it clean

            # After external MCP tools are loaded, refresh header + tool list.
            def _after_mcp_load() -> None:
                self.all_tools = get_all_tools()
                self._update_header()
                if self.runtime and self.mcp_manager:
                    self.runtime.mcp_manager = self.mcp_manager

            components = await build_agent_components(
                target=self.target,
                scope=[],
                model=self.model,
                docker=self.use_docker,
                no_rag=False,
                no_mcp=False,
                on_progress=_on_progress,
                after_mcp_load=_after_mcp_load,
                prebuilt_rag=self._prebuilt_rag,
            )

            self.agent = components["agent"]
            self.runtime = components["runtime"]
            self.rag_engine = components["rag_engine"]
            self.all_tools = components["all_tools"]
            self.mcp_manager = components["mcp_manager"]
            rag_doc_count = components["rag_doc_count"]
            mcp_server_count = components["mcp_server_count"]

            # Wire runtime ↔ MCP manager now that both are ready.
            if self.runtime and self.mcp_manager:
                self.runtime.mcp_manager = self.mcp_manager

            # Inject spawn/despawn child-MCP-server tools (TUI-only feature).
            from ..tools import (
                create_despawn_mcp_agent_tool,
                create_spawn_mcp_agent_tool,
            )

            if self.agent is not None:
                self.agent.add_tools(
                    [
                        create_spawn_mcp_agent_tool(self.agent),
                        create_despawn_mcp_agent_tool(self.agent),
                    ]
                )

            self._set_status("idle", "assist")
            self._is_initializing = False

            runtime_str = "Docker" if self.use_docker else "Local"
            self.mcp_server_count = mcp_server_count
            self.rag_doc_count = rag_doc_count
            try:
                self._update_header(
                    model_line=(
                        f"+ PentestAgent ready\n"
                        f"  Model: {self.model} | Tools: {len(self.all_tools)} | MCP: {mcp_server_count} | RAG: {rag_doc_count}\n"
                        f"  Runtime: {runtime_str} | Mode: Assist (use /agent or /crew for autonomous modes)"
                    )
                )
            except Exception:
                self._add_system(
                    f"+ PentestAgent ready\n"
                    f"  Model: {self.model} | Tools: {len(self.all_tools)} | MCP: {mcp_server_count} | RAG: {rag_doc_count}\n"
                    f"  Runtime: {runtime_str} | Mode: Assist (use /agent or /crew for autonomous modes)"
                )

            if self.target:
                try:
                    self._update_header(target=self.target)
                except Exception:
                    self._add_system(f"  Target: {self.target}")

            await self._restore_session()

        except Exception as e:
            import traceback

            self._add_system(f"[!] Init failed: {e}\n{traceback.format_exc()}")
            self._set_status("error")
            self._is_initializing = False

    # ------------------------------------------------------------------
    # MCP observation mode
    # ------------------------------------------------------------------

    @work(thread=False)
    async def _activate_mcp_mode(self) -> None:
        """Set up TUI in MCP observation mode using pre-built components."""
        try:
            components = self._prebuilt_components or {}
            self.agent = components.get("agent")
            self.runtime = components.get("runtime")
            self.rag_engine = components.get("rag_engine")
            self.all_tools = components.get("all_tools") or []
            self.mcp_manager = components.get("mcp_manager")
            self.model = components.get("model") or self.model
            rag_doc_count = components.get("rag_doc_count", 0)
            mcp_server_count = components.get("mcp_server_count", 0)

            # Disable the input widget — operator cannot type commands.
            try:
                inp = self.query_one("#chat-input")
                inp.disabled = True
            except Exception:
                pass
            try:
                prompt = self.query_one("#chat-prompt", Static)
                prompt.update("")
            except Exception:
                pass
            try:
                container = self.query_one("#input-container")
                container.add_class("mcp-locked")
            except Exception:
                pass

            self._is_initializing = False
            self._set_status("idle", "mcp")

            self.mcp_server_count = mcp_server_count
            self.rag_doc_count = rag_doc_count
            try:
                self._update_header(
                    model_line=(
                        f"+ PentestAgent — MCP Server Mode (read-only)\n"
                        f"  Model: {self.model} | Tools: {len(self.all_tools)} | MCP servers: {mcp_server_count} | RAG: {rag_doc_count}\n"
                        f"  Waiting for MCP client tasks…"
                    )
                )
            except Exception:
                self._add_system(
                    f"+ PentestAgent — MCP Server Mode (read-only)\n"
                    f"  Model: {self.model} | Tools: {len(self.all_tools)} | MCP: {mcp_server_count} | RAG: {rag_doc_count}"
                )

            if self.target:
                try:
                    self._update_header(target=self.target)
                except Exception:
                    pass

        except Exception as e:
            import traceback

            self._add_system(f"[!] MCP mode init failed: {e}\n{traceback.format_exc()}")
            self._set_status("error")
            self._is_initializing = False

    def on_mcp_event(self, event: str, data: dict) -> None:
        """Called by mcp_tools._emit() from an asyncio task.

        Does NOT touch any Textual widgets directly — instead posts a
        MCPTaskEvent message so Textual dispatches the update safely inside
        its own message loop (avoids NoMatches / DOM-not-ready races).
        """
        try:
            self.post_message(MCPTaskEvent(event, data))
        except Exception as e:
            logging.getLogger(__name__).exception("MCP post_message failed: %s", e)

    @on(MCPTaskEvent)
    def handle_mcp_task_event(self, message: MCPTaskEvent) -> None:
        """Handle MCP task events inside Textual's message loop (DOM is ready)."""
        event = message.event
        data = message.data
        try:
            if event == "task_start":
                task = data.get("task", "")
                target = data.get("target")
                label = f"[MCP task] {task}"
                if target:
                    label += f"  (target: {target})"
                self._add_user(label)
                self._set_status("running", "mcp")
                self._is_running = True
                self._mcp_tool_messages = {}

            elif event == "thinking":
                content = data.get("content", "")
                if content:
                    self._add_thinking(content)

            elif event == "content":
                content = data.get("content", "")
                if content:
                    self._add_assistant(content)

            elif event == "tool_call":
                call_id = data.get("id", "")
                name = data.get("name", "")
                arguments = data.get("arguments", {})
                tm = self._add_tool(name, str(arguments))
                self._mcp_tool_messages[call_id] = tm

            elif event == "tool_result":
                call_id = data.get("tool_call_id", "")
                tool_name = data.get("tool_name", "")
                result = data.get("result", "")
                success = data.get("success", True)
                tm = self._mcp_tool_messages.get(call_id)
                if tm is not None:
                    label = result if success else f"Error: {result}"
                    self._add_tool_result(tm, tool_name, label or "Done")

            elif event == "task_done":
                status = data.get("status", "done")
                error = data.get("error")
                if status == "error" and error:
                    self._add_system(f"[!] Task error: {error}")
                elif status == "cancelled":
                    self._add_system("[!] Task cancelled.")
                self._set_status("idle", "mcp")
                self._is_running = False

        except Exception as e:
            logging.getLogger(__name__).exception("MCP task event handler error: %s", e)

    def _set_status(self, status: str, mode: Optional[str] = None) -> None:
        """Update status bar"""
        try:
            bar = self.query_one("#status-bar", StatusBar)
            bar.status = status
            if mode:
                bar.mode = mode
                self._mode = mode
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to update status bar: %s", e)
            try:
                from .notifier import notify

                notify("warning", f"TUI: failed to update status bar: {e}")
            except Exception as ne:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about status bar update failure: %s", ne
                )

    def _show_notification(self, level: str, message: str) -> None:
        """Display a short operator-visible notification in the chat area."""
        try:
            # Prepend a concise system message so it is visible in the chat
            prefix = "[!]" if level.lower() in ("error", "critical") else "[!]"
            self._add_system(f"{prefix} {message}")
            # Set status bar to error briefly for emphasis
            if level.lower() in ("error", "critical"):
                self._set_status("error")
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to show notification in TUI: %s", e
            )

    def _notifier_callback(self, level: str, message: str) -> None:
        """Callback wired to `pentestagent.interface.notifier`.

        This will be registered on mount so other modules can emit notifications.
        """
        try:
            try:
                asyncio.get_running_loop()
                # Already on the app's event loop (e.g. called from an asyncio task).
                # call_from_thread would raise here — call directly instead.
                self._show_notification(level, message)
                return
            except RuntimeError:
                pass
            # Called from a worker thread — use call_from_thread.
            if hasattr(self, "call_from_thread"):
                self.call_from_thread(self._show_notification, level, message)
            else:
                self._show_notification(level, message)
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Exception in notifier callback handling: %s", e
            )

    def _spawn_terminal_callback(self, master_fd: int, label: str) -> None:
        """Callback wired to `notifier.register_spawn_terminal_callback`.

        Called from an asyncio task (agent tool execution), so we route
        through post_message / call_from_thread to stay on the Textual loop.
        """
        try:
            if hasattr(self, "call_from_thread"):
                try:
                    self.call_from_thread(
                        self.post_message, SpawnTerminalMessage(master_fd, label)
                    )
                    return
                except Exception:
                    pass
            self.post_message(SpawnTerminalMessage(master_fd, label))
        except Exception as e:
            logging.getLogger(__name__).exception(
                "spawn_terminal_callback failed: %s", e
            )

    @on(SpawnTerminalMessage)
    def _handle_spawn_terminal(self, message: SpawnTerminalMessage) -> None:
        """Mount a CollapsibleTerminal widget and show the agents panel."""
        from .widgets import CollapsibleTerminal

        try:
            panel = self.query_one("#agents-panel")
            terminal = CollapsibleTerminal(
                master_fd=message.master_fd,
                label=message.label,
            )
            panel.mount(terminal)
            panel.add_class("visible")
            try:
                self.query_one("#resize-divider", ResizeDivider).add_class("visible")
            except Exception:
                pass
            self.refresh(layout=True)
            self._add_system(
                f"[+] Child agent '{message.label}' terminal opened in side panel."
            )
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to mount EmbeddedTerminal: %s", e
            )

    def _despawn_terminal_callback(self, label: str) -> None:
        """Callback wired to `notifier.register_despawn_terminal_callback`."""
        try:
            if hasattr(self, "call_from_thread"):
                try:
                    self.call_from_thread(
                        self.post_message, DespawnTerminalMessage(label)
                    )
                    return
                except Exception:
                    pass
            self.post_message(DespawnTerminalMessage(label))
        except Exception as e:
            logging.getLogger(__name__).exception(
                "despawn_terminal_callback failed: %s", e
            )

    @on(DespawnTerminalMessage)
    def _handle_despawn_terminal(self, message: DespawnTerminalMessage) -> None:
        """Unmount the CollapsibleTerminal whose label matches the despawned agent."""
        from .widgets import CollapsibleTerminal

        try:
            panel = self.query_one("#agents-panel")

            # Count terminals that will remain *after* this removal.  We must
            # do this BEFORE calling remove() because widget.remove() is
            # deferred in Textual — the DOM query would still find the widget
            # that is being removed if we check afterwards.
            all_terminals = list(panel.query(CollapsibleTerminal))
            remaining_after = [w for w in all_terminals if w._label != message.label]

            for widget in all_terminals:
                if widget._label == message.label:
                    widget.remove()
                    break

            # Hide the panel and resize divider if no terminals will remain,
            # and reset the panel width so it fills correctly on next spawn.
            if not remaining_after:
                panel.remove_class("visible")
                panel.styles.width = None  # reset to CSS default (84)
                try:
                    self.query_one("#resize-divider", ResizeDivider).remove_class(
                        "visible"
                    )
                except Exception:
                    pass
                self.refresh(layout=True)

            self._add_system(
                f"[-] Child agent '{message.label}' terminal removed from side panel."
            )
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to unmount CollapsibleTerminal: %s", e
            )

    def _add_message(self, widget: Static) -> None:
        """Add a message widget to chat"""
        try:
            scroll = self.query_one("#chat-scroll", ScrollableContainer)
            widget.add_class("message")
            scroll.mount(widget)
            scroll.scroll_end(animate=False)
            self._chat_widgets.append(widget)
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to add message to chat: %s", e
            )
            try:
                from .notifier import notify

                notify("warning", f"TUI: failed to add chat message: {e}")
            except Exception as ne:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about add_message failure: %s", ne
                )

    def _add_system(self, content: str) -> None:
        self._add_message(SystemMessage(content))

    def _add_user(self, content: str) -> None:
        self._add_message(UserMessage(content))

    async def _cancel_running_tasks(self) -> None:
        """Cancel any in-flight worker or crew and reset running state."""
        if self._current_worker:
            self._current_worker.cancel()
            self._current_worker = None
        if self._current_crew:
            try:
                await self._current_crew.cancel()
            except Exception:
                pass
            self._current_crew = None
        self._is_running = False

    async def _truncate_to_user_message(self, user_message: "UserMessage") -> bool:
        """Cancel tasks, then truncate history and UI to before user_message.

        Returns True on success, False if the widget was not found.
        """
        await self._cancel_running_tasks()

        user_message_count = 0
        widget_index = -1
        for i, widget in enumerate(self._chat_widgets):
            if isinstance(widget, UserMessage):
                user_message_count += 1
                if widget is user_message:
                    widget_index = i
                    break

        if widget_index == -1:
            return False

        history_user_count = 0
        history_index = -1
        for i, msg in enumerate(self.agent.conversation_history):
            if msg.role == "user":
                history_user_count += 1
                if history_user_count == user_message_count:
                    history_index = i
                    break

        if history_index == -1:
            return False

        self.agent.conversation_history = self.agent.conversation_history[
            :history_index
        ]
        for widget in reversed(self._chat_widgets[widget_index:]):
            try:
                widget.remove()
            except Exception:
                pass
        self._chat_widgets = self._chat_widgets[:widget_index]
        return True

    @on(UserMessage.RewindPressed)
    def _handle_rewind(self, event: UserMessage.RewindPressed) -> None:
        if not self.agent:
            return

        def on_confirm(confirmed: bool | None) -> None:
            if confirmed:
                self.call_later(self._do_rewind, event.user_message)

        self.push_screen(RewindConfirmScreen(), on_confirm)

    async def _do_rewind(self, user_message: "UserMessage") -> None:
        if await self._truncate_to_user_message(user_message):
            self._add_system(
                f"Conversation rewound to before: {user_message._copy_content[:50]}..."
            )

    @on(UserMessage.ForkPressed)
    def _handle_fork(self, event: UserMessage.ForkPressed) -> None:
        if not self.agent:
            return

        def on_confirm(confirmed: bool | None) -> None:
            if confirmed:
                self.call_later(self._do_fork, event.user_message)

        self.push_screen(ForkConfirmScreen(), on_confirm)

    async def _do_fork(self, user_message: "UserMessage") -> None:
        saved_id: str | None = None
        try:
            from ..workspaces.utils import get_conversations_base
            from .conversation_store import ConversationStore

            if self.agent and self.agent.conversation_history:
                store = ConversationStore(get_conversations_base())
                saved_id = store.save(self.agent.conversation_history)
        except Exception as e:
            self._add_system(f"[!] Fork: could not save conversation: {e}")

        if await self._truncate_to_user_message(user_message):
            save_note = f" (saved as {saved_id[:8]}…)" if saved_id else ""
            self._add_system(
                f"Conversation forked{save_note}. Previous history saved. "
                f"Continuing before: {user_message._copy_content[:50]}…"
            )

    def _add_assistant(self, content: str) -> None:
        self._add_message(AssistantMessage(content))

    def _add_thinking(self, content: str) -> None:
        self._add_message(ThinkingMessage(content))

    def _add_tool(self, name: str, action: str = "") -> ToolMessage:
        tool_message = ToolMessage(name, action)
        self._add_message(tool_message)
        return tool_message

    def _add_tool_result(
        self, tool_message: ToolMessage, name: str, result: str
    ) -> None:
        """Display tool execution result"""
        tool_message.attach_result(ToolResultMessage(name, result))

    def _show_system_prompt(self) -> None:
        """Display the current system prompt"""
        if self.agent:
            prompt = self.agent.get_system_prompt(self._mode)
            self._add_system(f"=== System Prompt ===\n{prompt}")
        else:
            self._add_system("Agent not initialized")

    def _show_memory_stats(self) -> None:
        """Mount a live memory diagnostics widget into the chat area."""
        try:
            scroll = self.query_one("#chat-scroll", ScrollableContainer)
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to query chat-scroll for memory diagnostics: %s", e
            )
            try:
                from .notifier import notify

                notify("warning", f"TUI: memory diagnostics unavailable: {e}")
            except Exception as ne:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about memory diagnostics availability: %s",
                    ne,
                )
            self._add_system("Agent not initialized")
            return
        # Mount a new diagnostics panel with a unique ID and scroll into view
        try:
            import uuid

            panel_id = f"memory-diagnostics-{uuid.uuid4().hex}"
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to generate memory diagnostics panel id: %s", e
            )
            panel_id = None

        widget = MemoryDiagnostics(id=panel_id)
        scroll.mount(widget)
        try:
            scroll.scroll_end(animate=False)
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to scroll to memory diagnostics panel: %s", e
            )
            try:
                from .notifier import notify

                notify(
                    "warning", f"TUI: failed to scroll to memory diagnostics panel: {e}"
                )
            except Exception as ne:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about scroll failure: %s", ne
                )

    def _show_token_stats(self) -> None:
        """Mount a live token diagnostics widget into the chat area."""
        try:
            scroll = self.query_one("#chat-scroll", ScrollableContainer)
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to query chat-scroll for token diagnostics: %s", e
            )
            try:
                from ..interface.notifier import notify

                notify("warning", f"TUI: token diagnostics unavailable: {e}")
            except Exception as ne:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about token diagnostics availability: %s",
                    ne,
                )
            self._add_system("Agent not initialized")
            return
        # Mount a new diagnostics panel with a unique ID and scroll into view
        try:
            import uuid

            panel_id = f"token-diagnostics-{uuid.uuid4().hex}"
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to generate token diagnostics panel id: %s", e
            )
            try:
                from ..interface.notifier import notify

                notify(
                    "warning",
                    f"TUI: failed to generate token diagnostics panel id: {e}",
                )
            except Exception as ne:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about token diagnostics panel id generation failure: %s",
                    ne,
                )
            panel_id = None

        widget = TokenDiagnostics(id=panel_id)
        scroll.mount(widget)
        try:
            scroll.scroll_end(animate=False)
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to scroll to token diagnostics panel: %s", e
            )
            try:
                from ..interface.notifier import notify

                notify(
                    "warning", f"TUI: failed to scroll to token diagnostics panel: {e}"
                )
            except Exception as ne:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about token diagnostics scroll failure: %s",
                    ne,
                )

    async def _show_notes(self) -> None:
        """Display saved notes"""
        from ..tools.notes import get_all_notes

        notes = await get_all_notes()
        if not notes:
            self._add_system(
                "=== Notes ===\nNo notes saved.\n\nThe AI can save key findings using the notes tool."
            )
            return

        lines = [f"=== Notes ({len(notes)} entries) ==="]
        for key, value in notes.items():
            # Show full value, indent multi-line content
            if "\n" in value:
                indented = str(value).replace("\n", "\n    ")
                lines.append(f"\n[{key}]\n    {indented}")
            else:
                lines.append(f"[{key}] {value}")
        lines.append("\nFile: loot/notes.json")
        lines.append("Reports: loot/reports/")

        self._add_system("\n".join(lines))

    def _build_prior_context(self) -> str:
        """Build a summary of prior findings for crew mode.

        Extracts:
        - Tool results (nmap scans, etc.) - the actual findings
        - Assistant analyses - interpretations and summaries
        - Last user task - what they were working on

        Excludes:
        - Raw user messages (noise)
        - Tool call declarations (just names/args, not results)
        - Very short responses
        """
        if not self.agent or not self.agent.conversation_history:
            return ""

        findings = []
        last_user_task = ""

        for msg in self.agent.conversation_history:
            # Track user tasks/questions
            if msg.role == "user" and msg.content:
                last_user_task = msg.content[:200]

            # Extract tool results (the actual findings)
            elif msg.tool_results:
                for result in msg.tool_results:
                    if result.success and result.result:
                        content = (
                            result.result[:1500]
                            if len(result.result) > 1500
                            else result.result
                        )
                        findings.append(f"[{result.tool_name}]\n{content}")

            # Include assistant analyses (but not tool call messages)
            elif msg.role == "assistant" and msg.content and not msg.tool_calls:
                if len(msg.content) > 50:
                    findings.append(f"[Analysis]\n{msg.content[:1000]}")

        if not findings and not last_user_task:
            return ""

        # Build context with last user task + recent findings
        parts = []
        if last_user_task:
            parts.append(f"Last task: {last_user_task}")
        if findings:
            parts.append("Findings:\n" + "\n\n".join(findings[-5:]))

        context = "\n\n".join(parts)
        if len(context) > 4000:
            context = context[:4000] + "\n... (truncated)"

        return context

    async def _save_current_conversation(self) -> None:
        """Persist the current conversation history to the active loot store.

        On first call for a session, creates a new file and stores the id in
        _current_conv_id.  Subsequent calls update the same file so that one
        TUI session maps to exactly one saved conversation.
        """
        if not self.agent or not self.agent.conversation_history:
            return
        if not any(m.role == "user" for m in self.agent.conversation_history):
            return
        try:
            from ..workspaces.utils import get_conversations_base
            from .conversation_store import ConversationStore

            store = ConversationStore(get_conversations_base())
            conv_id = store.save(
                self.agent.conversation_history, conv_id=self._current_conv_id
            )
            if conv_id:
                self._current_conv_id = conv_id
                await self._save_session_state()
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to auto-save conversation: %s", e
            )

    async def _restore_conversation(self, conv_id: str) -> None:
        """Load a saved conversation and re-render it in the chat UI."""
        try:
            from ..workspaces.utils import get_conversations_base
            from .conversation_store import ConversationStore

            store = ConversationStore(get_conversations_base())
            messages = store.load(conv_id)
            if not messages:
                self._add_system("[!] Could not load conversation (empty or missing).")
                return

            scroll = self.query_one("#chat-scroll", ScrollableContainer)
            await scroll.remove_children()
            self._chat_widgets.clear()

            if self.agent:
                self.agent.conversation_history = messages
            self._current_conv_id = conv_id

            # Maps tool_call_id → ToolMessage widget, same pattern as _display_responses
            tool_messages_mapping: dict[str, ToolMessage] = {}

            for msg in messages:
                if msg.role == "user":
                    self._add_user(msg.content or "")
                elif msg.role == "assistant":
                    if msg.content and msg.content.strip():
                        if msg.tool_calls:
                            self._add_thinking(msg.content)
                        else:
                            self._add_assistant(msg.content)
                    if msg.tool_calls:
                        for tc in msg.tool_calls:
                            tool_messages_mapping[tc.id] = self._add_tool(
                                tc.name, str(tc.arguments)
                            )
                elif msg.role == "tool_result":
                    if msg.tool_results:
                        for tr in msg.tool_results:
                            tm = tool_messages_mapping.get(tr.tool_call_id)
                            if tm is not None:
                                if tr.success:
                                    self._add_tool_result(
                                        tm, tr.tool_name, tr.result or "Done"
                                    )
                                else:
                                    self._add_tool_result(
                                        tm, tr.tool_name, f"Error: {tr.error}"
                                    )
                elif msg.role == "system" and msg.content:
                    self._add_system(msg.content)

            self._add_system(f"Conversation restored ({len(messages)} messages)")
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to restore conversation: %s", e
            )
            self._add_system(f"[!] Restore failed: {e}")

    async def _save_session_state(self) -> None:
        """Persist current conv_id, mode, and target to session.json."""
        if not self._current_conv_id:
            return
        try:
            import json as _json

            from ..workspaces.utils import get_session_file

            session_file = get_session_file()
            session_file.write_text(
                _json.dumps(
                    {
                        "conv_id": self._current_conv_id,
                        "mode": self._mode,
                        "target": self.target,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to save session state: %s", e)

    async def _restore_session(self) -> None:
        """On startup, restore last session from session.json if the preference is enabled."""
        try:
            import json as _json

            from ..workspaces.utils import get_preferences_file, get_session_file

            # Check user preference — default is disabled
            prefs_file = get_preferences_file()
            auto_reload = False
            if prefs_file.exists():
                try:
                    prefs = _json.loads(prefs_file.read_text(encoding="utf-8"))
                    auto_reload = bool(prefs.get("auto_reload_session", False))
                except Exception:
                    pass
            if not auto_reload:
                return

            session_file = get_session_file()
            if not session_file.exists():
                return
            data = _json.loads(session_file.read_text(encoding="utf-8"))
            conv_id = data.get("conv_id")
            mode = data.get("mode", "assist")
            saved_target = data.get("target")

            if conv_id:
                await self._restore_conversation(conv_id)

            if mode in ("assist", "agent", "crew", "interact"):
                self._mode = mode
                self._set_status("idle", mode)

            if saved_target and not self.target:
                self.target = saved_target
                if self.agent:
                    self.agent.target = saved_target
                try:
                    self._update_header(target=saved_target)
                except Exception:
                    pass
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to restore session: %s", e)

    def _set_target(self, cmd: str) -> None:
        """Set the target for the engagement"""
        # Remove /target prefix
        target = cmd[7:].strip()

        if not target:
            if self.target:
                self._add_system(
                    f"Current target: {self.target}\nUsage: /target <host>"
                )
            else:
                self._add_system(
                    "No target set.\nUsage: /target <host>\nExample: /target 192.168.1.1"
                )
            return

        self.target = target

        # Update agent's target if agent exists
        if self.agent:
            self.agent.target = target
            try:
                from pentestagent.agents.base_agent import AgentMessage

                # Inform the agent (LLM) that the operator changed the target so
                # subsequent generations use the new value instead of older
                # workspace-bound targets from conversation history.
                self.agent.conversation_history.append(
                    AgentMessage(
                        role="system", content=f"Operator set target to {target}"
                    )
                )
                # Track manual target override so workspace restores can remove
                # or supersede this message when appropriate.
                try:
                    self.agent._manual_target = target
                except Exception:
                    pass
            except Exception as e:
                logging.getLogger(__name__).exception(
                    "Failed to append target change to agent history: %s", e
                )

        # Persist to active workspace if present
        try:
            from pentestagent.workspaces.manager import WorkspaceManager

            wm = WorkspaceManager()
            active = wm.get_active()
            if active:
                try:
                    wm.set_last_target(active, target)
                except Exception as e:
                    logging.getLogger(__name__).exception(
                        "Failed to persist last target for workspace %s: %s", active, e
                    )
                    try:
                        from pentestagent.interface.notifier import notify

                        notify(
                            "warning",
                            f"Failed to persist last target for workspace {active}: {e}",
                        )
                    except Exception as ne:
                        logging.getLogger(__name__).exception(
                            "Failed to notify operator about target persist error: %s",
                            ne,
                        )
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to access WorkspaceManager to persist last target: %s", e
            )
            try:
                from pentestagent.interface.notifier import notify

                notify("warning", f"TUI: failed to persist last target: {e}")
            except Exception as ne:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about WorkspaceManager access failure: %s",
                    ne,
                )

        # Update displayed Target in the UI
        try:
            self._apply_target_display(target)
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to apply target display: %s", e
            )
            try:
                from pentestagent.interface.notifier import notify

                notify("warning", f"Failed to update target display: {e}")
            except Exception as ne:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about target display error: %s", ne
                )
        # Update the initial ready SystemMessage (if present) so Target appears under Runtime
        try:
            scroll = self.query_one("#chat-scroll", ScrollableContainer)
            updated = False
            for child in scroll.children:
                if isinstance(child, SystemMessage) and "PentestAgent ready" in getattr(
                    child, "message_content", ""
                ):
                    # Replace existing Target line if present, otherwise append
                    try:
                        if "Target:" in child.message_content:
                            # replace the first Target line
                            child.message_content = re.sub(
                                r"(?m)^\s*Target:.*$",
                                f"  Target: {target}",
                                child.message_content,
                                count=1,
                            )
                        else:
                            child.message_content = (
                                child.message_content + f"\n  Target: {target}"
                            )
                        try:
                            child.refresh()
                        except Exception as e:
                            logging.getLogger(__name__).exception(
                                "Failed to refresh child message after target update: %s",
                                e,
                            )
                            try:
                                from pentestagent.interface.notifier import notify

                                notify(
                                    "warning",
                                    f"Failed to refresh UI after target update: {e}",
                                )
                            except Exception as ne:
                                logging.getLogger(__name__).exception(
                                    "Failed to notify operator about UI refresh error: %s",
                                    ne,
                                )
                    except Exception as e:
                        # Fallback to append if regex replacement fails, and surface warning
                        logging.getLogger(__name__).exception(
                            "Failed to update SystemMessage target line: %s", e
                        )
                        try:
                            from pentestagent.interface.notifier import notify

                            notify("warning", f"Failed to update target display: {e}")
                        except Exception as ne:
                            logging.getLogger(__name__).exception(
                                "Failed to notify operator about target update error: %s",
                                ne,
                            )
                        child.message_content = (
                            child.message_content + f"\n  Target: {target}"
                        )
                    updated = True
                    break
            if not updated:
                # If we couldn't find an existing banner SystemMessage to
                # update, update the persistent header instead of inserting
                # additional in-chat system messages to avoid duplicates.
                try:
                    self._update_header(target=target)
                except Exception:
                    logging.getLogger(__name__).exception(
                        "Failed to update persistent header with target"
                    )
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed while applying target display: %s", e
            )
            try:
                from pentestagent.interface.notifier import notify

                notify("warning", f"TUI: failed while updating target display: {e}")
            except Exception as ne:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about target display outer failure: %s",
                    ne,
                )
            # Last resort: append a subtle system line
            self._add_system(f"  Target: {target}")

    @work(exclusive=True)
    async def _run_report_generation(self) -> None:
        """Generate a pentest report from notes and conversation"""

        from ..tools.notes import get_all_notes

        if not self.agent or not self.agent.llm:
            self._add_system("[!] Agent not initialized")
            return

        notes = await get_all_notes()
        if not notes:
            self._add_system(
                "No notes found. PentestAgent saves findings using the notes tool during testing."
            )
            return

        self._add_system("Generating report...")

        # Format notes - extract structured content from note dicts
        notes_lines = []
        for k, v in notes.items():
            if isinstance(v, dict):
                content = v.get("content", "")
                category = v.get("category", "info")
                confidence = v.get("confidence", "medium")
                status = v.get("status", "confirmed")
                meta = v.get("metadata", {})
                target = meta.get("target", "N/A")
                header = f"### {k} [{category}] (confidence: {confidence}, status: {status}, target: {target})"
                notes_lines.append(f"{header}\n{content}")
                if meta.get("services"):
                    notes_lines.append(f"Services: {json.dumps(meta['services'])}")
                if meta.get("technologies"):
                    notes_lines.append(
                        f"Technologies: {json.dumps(meta['technologies'])}"
                    )
                if meta.get("endpoints"):
                    notes_lines.append(f"Endpoints: {json.dumps(meta['endpoints'])}")
                if meta.get("weaknesses"):
                    notes_lines.append(f"Weaknesses: {json.dumps(meta['weaknesses'])}")
                if meta.get("cve"):
                    notes_lines.append(f"CVE: {meta['cve']}")
                if meta.get("username"):
                    notes_lines.append(f"Username: {meta['username']}")
                notes_lines.append("")
            else:
                notes_lines.append(f"### {k}\n{v}\n")
        notes_text = "\n".join(notes_lines)

        # Build conversation summary from full history
        conversation_summary = ""
        if self.agent.conversation_history:
            # Summarize key actions from conversation
            actions = []
            for msg in self.agent.conversation_history:
                if msg.role == "assistant" and msg.tool_calls:
                    for tc in msg.tool_calls:
                        actions.append(f"- Tool: {tc.name}")
                elif msg.role == "tool_result" and msg.tool_results:
                    for tr in msg.tool_results:
                        # Include more of the result for report context
                        result = tr.result or ""
                        output = result[:1000] + "..." if len(result) > 1000 else result
                        status = "OK" if tr.success else "FAIL"
                        actions.append(f"  [{status}] {tr.tool_name}: {output}")
            if actions:
                conversation_summary = "\n".join(actions[-30:])  # Last 30 actions

        report_prompt = f"""Generate a penetration test report in Markdown from the notes below.

# Notes
{notes_text}

# Activity Log
{conversation_summary if conversation_summary else "N/A"}

# Target
{self.target or "Not specified"}

Output a report with:
1. Executive Summary (2-3 sentences)
2. Findings (use notes, include severity: Critical/High/Medium/Low/Info)
3. Recommendations

Be concise. Use the actual data from notes."""

        try:
            # Use generate() directly with higher max_tokens for reports (16k vs default 8k)
            report_response = await self.agent.llm.generate(
                system_prompt="You are a penetration tester writing a security report. Be concise and factual. Include ALL findings from the notes.",
                messages=[{"role": "user", "content": report_prompt}],
                tools=None,
                max_tokens=16384,
            )
            report_content = report_response.content or ""

            if not report_content or not report_content.strip():
                self._add_system(
                    "[!] Report generation returned empty. Check LLM connection."
                )
                return

            # Save to loot/reports/
            reports_dir = Path("loot/reports")
            reports_dir.mkdir(parents=True, exist_ok=True)

            # Append Shadow Graph if available
            try:
                from ..knowledge.graph import ShadowGraph
                from ..tools.notes import get_all_notes_sync

                # Rehydrate graph from notes
                graph = ShadowGraph()
                notes = get_all_notes_sync()
                if notes:
                    graph.update_from_notes(notes)
                    mermaid_code = graph.to_mermaid()

                    if mermaid_code:
                        report_content += (
                            "\n\n## Attack Graph (Visual)\n\n```mermaid\n"
                            + mermaid_code
                            + "\n```\n"
                        )
            except Exception as e:
                self._add_system(f"[!] Graph generation error: {e}")

            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            report_path = reports_dir / f"report_{timestamp}.md"
            report_path.write_text(report_content, encoding="utf-8")

            self._add_system(f"+ Report saved: {report_path}")

        except Exception as e:
            self._add_system(f"[!] Report error: {e}")

    @on(Input.Changed, "#chat-input")
    def handle_input_changed(self, event: Input.Changed) -> None:
        """Show/filter command suggestions when typing a slash command."""
        try:
            suggestions = self.query_one("#cmd-suggestions", CommandSuggestions)
            hint = self.query_one("#tab-hint", Static)
            inp = self.query_one("#chat-input", Input)
        except Exception:
            return
        val = event.value
        if val.startswith("/"):
            suggestions.update_suggestions(val)
            show = bool(suggestions.display)
            hint.display = show
            inp.styles.width = "auto" if show else "1fr"
        else:
            suggestions.hide()
            hint.display = False
            inp.styles.width = "1fr"

    @on(Input.Submitted, "#chat-input")
    async def handle_submit(self, event: Input.Submitted) -> None:
        """Handle input submission"""
        # Hide suggestions on submit
        try:
            self.query_one("#cmd-suggestions", CommandSuggestions).hide()
            self.query_one("#tab-hint", Static).display = False
            self.query_one("#chat-input", Input).styles.width = "1fr"
        except Exception:
            pass

        # MCP observation mode: the input is disabled at the widget level, but
        # guard here as well to be safe.
        if self.mcp_mode:
            event.input.value = ""
            return

        # Block input while initializing or AI is processing
        if self._is_initializing or self._is_running:
            return

        # Strip ANSI escape sequences and control codes
        message = _ANSI_ESCAPE.sub("", event.value).strip()
        if not message:
            return

        # Save to history (de-duplicate consecutive duplicates)
        if not (self._cmd_history and self._cmd_history[-1] == message):
            self._cmd_history.append(message)
        # Reset index to one past the end (blank)
        self._history_index = len(self._cmd_history)

        event.input.value = ""

        # Commands
        if message.startswith("/"):
            await self._handle_command(message)
            return

        self._add_user(message)

        if self.agent and not self._is_running:
            if self._mode == "assist":
                # Schedule assist run and keep task handle (do not wrap in asyncio.create_task; @work returns a Worker)
                self._hide_sidebar()
                self._current_worker = self._run_assist(message)
            elif self._mode == "interact":
                self._hide_sidebar()
                self._current_worker = self._run_interact(message)
            elif self._mode == "agent":
                self._hide_sidebar()
                self._current_worker = self._run_agent_mode(message)
            elif self._mode == "crew":
                self._current_worker = self._run_crew_mode(message)

    async def _handle_command(self, cmd: str) -> None:
        """Handle slash commands"""
        cmd_lower = cmd.lower().strip()
        cmd_original = cmd.strip()

        if cmd_lower in ["/help", "/h", "/?"]:
            await self.push_screen(HelpScreen())
        elif cmd_lower == "/clear":
            await self._save_current_conversation()
            self._current_conv_id = None
            # Remove autosave session pointer so next startup starts fresh
            try:
                from ..workspaces.utils import get_session_file

                sf = get_session_file()
                if sf.exists():
                    sf.unlink()
            except Exception:
                pass
            scroll = self.query_one("#chat-scroll", ScrollableContainer)
            await scroll.remove_children()
            self._chat_widgets.clear()
            self._hide_sidebar()
            # Clear agent conversation history for fresh start
            if self.agent:
                self.agent.conversation_history.clear()
            self._add_system("Chat cleared")
        elif cmd_lower == "/tools":
            # Open the interactive tools browser (split-pane).
            try:
                if self.agent:
                    await self.push_screen(
                        ToolsScreen(tools=self.agent.get_tools(), tui=self)
                    )
            except Exception:
                # Fallback: list tools in the system area if UI push fails
                from ..runtime.runtime import detect_environment

                names = [t.name for t in self.all_tools]
                msg = f"Tools ({len(names)}): " + ", ".join(names)

                # Add detected CLI tools
                env = detect_environment()
                if env.available_tools:
                    # Group by category
                    by_category = {}
                    for tool_info in env.available_tools:
                        if tool_info.category not in by_category:
                            by_category[tool_info.category] = []
                        by_category[tool_info.category].append(tool_info.name)

                    cli_sections = []
                    for category in sorted(by_category.keys()):
                        tools_list = ", ".join(sorted(by_category[category]))
                        cli_sections.append(f"{category}: {tools_list}")

                    msg += f"\n\nCLI Tools ({len(env.available_tools)}):\n" + "\n".join(
                        cli_sections
                    )

                self._add_system(msg)
        elif cmd_lower.startswith("/mcp"):
            await self._parse_mcp_command(cmd_original)
        elif cmd_lower in ["/quit", "/exit", "/q"]:
            self.exit()
        elif cmd_lower == "/prompt":
            self._show_system_prompt()
        elif cmd_lower == "/memory":
            self._show_memory_stats()
        elif cmd_lower == "/token":
            self._show_token_stats()
        elif cmd_lower == "/notes":
            await self._show_notes()
        elif cmd_lower == "/report":
            # Call the textual worker - decorator returns a Worker
            _ = cast(Any, self._run_report_generation())
        elif cmd_original.startswith("/target"):
            self._set_target(cmd_original)
        elif cmd_original.startswith("/workspace"):
            # Support lightweight workspace management from the TUI
            try:

                from pentestagent.workspaces.manager import (
                    WorkspaceError,
                    WorkspaceManager,
                )
                from pentestagent.workspaces.utils import resolve_knowledge_paths

                wm = WorkspaceManager()
                rest = cmd_original[len("/workspace") :].strip()

                if not rest:
                    active = wm.get_active()
                    if not active:
                        self._add_system("No active workspace.")
                    else:
                        # restore last target if present
                        last = wm.get_meta_field(active, "last_target")
                        if last:
                            self.target = last
                            if self.agent:
                                self.agent.target = last
                                # If the operator set a manual target while no
                                # workspace was active, remove/supersede that
                                # system message so the LLM uses the workspace
                                # target instead of the stale manual one.
                                try:
                                    manual = getattr(self.agent, "_manual_target", None)
                                    if manual:
                                        self.agent.conversation_history = [
                                            m
                                            for m in self.agent.conversation_history
                                            if not (
                                                m.role == "system"
                                                and isinstance(m.content, str)
                                                and m.content.strip().startswith(
                                                    "Operator set target to"
                                                )
                                            )
                                        ]
                                        try:
                                            delattr(self.agent, "_manual_target")
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                                try:
                                    from pentestagent.agents.base_agent import (
                                        AgentMessage,
                                    )

                                    self.agent.conversation_history.append(
                                        AgentMessage(
                                            role="system",
                                            content=f"Workspace active; restored last target: {last}",
                                        )
                                    )
                                except Exception:
                                    pass
                            try:
                                self._apply_target_display(last)
                            except Exception as e:
                                logging.getLogger(__name__).exception(
                                    "Failed to apply target display when restoring last target: %s",
                                    e,
                                )
                                try:
                                    from pentestagent.interface.notifier import notify

                                    notify(
                                        "warning",
                                        f"TUI: failed restoring last target display: {e}",
                                    )
                                except Exception:
                                    logging.getLogger(__name__).exception(
                                        "Failed to notify operator about restore-last-target failure"
                                    )
                        self._add_system(f"Active workspace: {active}")
                    return

                parts = rest.split()
                verb = parts[0].lower()

                if verb == "help":
                    try:
                        await self.push_screen(WorkspaceHelpScreen())
                    except Exception:
                        # Fallback: show inline help text
                        self._add_system(
                            "Usage: /workspace <action>\nCommands: list, info, note, clear, help, <name>"
                        )
                    return

                if verb == "list":
                    wss = wm.list_workspaces()
                    if not wss:
                        self._add_system("No workspaces found.")
                        return
                    out = []
                    active = wm.get_active()
                    for name in sorted(wss):
                        prefix = "* " if name == active else "  "
                        out.append(f"{prefix}{name}")
                    self._add_system("\n".join(out))
                    return

                if verb == "info":
                    name = parts[1] if len(parts) > 1 else wm.get_active()
                    if not name:
                        self._add_system(
                            "No workspace specified and no active workspace."
                        )
                        return
                    try:
                        meta = wm.get_meta(name)
                        created = meta.get("created_at")
                        last_active = meta.get("last_active_at")
                        targets = meta.get("targets", [])
                        kp = resolve_knowledge_paths()
                        ks = "workspace" if kp.get("using_workspace") else "global"
                        self._add_system(
                            f"Name: {name}\nCreated: {created}\nLast active: {last_active}\nTargets: {len(targets)}\nKnowledge scope: {ks}"
                        )
                    except Exception as e:
                        self._add_system(f"Error retrieving workspace info: {e}")
                    return

                if verb == "note":
                    # By default, use the active workspace; allow explicit override via --workspace/-w.
                    name = wm.get_active()
                    i = 1
                    # Parse optional workspace selector flags before the note text.
                    while i < len(parts):
                        part = parts[i]
                        if part in ("--workspace", "-w"):
                            if i + 1 >= len(parts):
                                self._add_system(
                                    "Usage: /workspace note [--workspace NAME] <text>"
                                )
                                return
                            name = parts[i + 1]
                            i += 2
                            continue
                        # First non-option token marks the start of the note text
                        break
                    if not name:
                        self._add_system(
                            "No active workspace. Set one with /workspace <name>."
                        )
                        return
                    text = " ".join(parts[i:])
                    if not text:
                        self._add_system(
                            "Usage: /workspace note [--workspace NAME] <text>"
                        )
                        return
                    try:
                        wm.set_operator_note(name, text)
                        self._add_system(f"Operator note saved for workspace '{name}'.")
                    except Exception as e:
                        self._add_system(f"Error saving note: {e}")
                    return

                if verb == "clear":
                    active = wm.get_active()
                    if not active:
                        self._add_system("No active workspace.")
                        return
                    marker = wm.active_marker()
                    try:
                        if marker.exists():
                            marker.unlink()
                        # Clear TUI and agent target when workspace is deactivated
                        self.target = ""
                        try:
                            self._apply_target_display("")
                        except Exception:
                            pass
                        if self.agent:
                            try:
                                # Clear agent's target and any manual override
                                self.agent.target = ""
                                try:
                                    if hasattr(self.agent, "_manual_target"):
                                        delattr(self.agent, "_manual_target")
                                except Exception:
                                    pass
                                from pentestagent.agents.base_agent import AgentMessage

                                self.agent.conversation_history.append(
                                    AgentMessage(
                                        role="system",
                                        content=(
                                            f"Workspace '{active}' deactivated; cleared target"
                                        ),
                                    )
                                )
                            except Exception:
                                logging.getLogger(__name__).exception(
                                    "Failed to clear agent target on workspace clear"
                                )
                        self._add_system(f"Workspace '{active}' deactivated.")
                    except Exception as e:
                        self._add_system(f"Error deactivating workspace: {e}")
                    return

                # Default: treat rest as workspace name -> create (only if missing) and set active
                name = rest
                try:
                    existed = wm.workspace_path(name).exists()
                    if not existed:
                        wm.create(name)
                    wm.set_active(name)
                    # restore last target if set on workspace
                    last = wm.get_meta_field(name, "last_target")
                    if last:
                        self.target = last
                        if self.agent:
                            self.agent.target = last
                        try:
                            self._apply_target_display(last)
                        except Exception as e:
                            logging.getLogger(__name__).exception(
                                "Failed to apply target display when activating workspace: %s",
                                e,
                            )
                            try:
                                from pentestagent.interface.notifier import notify

                                notify(
                                    "warning",
                                    f"TUI: failed to restore workspace target display: {e}",
                                )
                            except Exception:
                                logging.getLogger(__name__).exception(
                                    "Failed to notify operator about workspace target restore failure"
                                )

                    if existed:
                        self._add_system(f"Workspace '{name}' set active.")
                    else:
                        self._add_system(f"Workspace '{name}' created and set active.")
                except WorkspaceError as e:
                    self._add_system(f"Error: {e}")
                except Exception as e:
                    self._add_system(f"Error creating workspace: {e}")
            except Exception as e:
                self._add_system(f"Workspace command error: {e}")
            return
        elif cmd_original.startswith("/spawn"):
            await self._parse_spawn_command(cmd_original)
        elif cmd_original.startswith("/despawn"):
            await self._parse_despawn_command(cmd_original)
        elif cmd_original.startswith("/agent"):
            await self._parse_agent_command(cmd_original)
        elif cmd_original.startswith("/crew"):
            await self._parse_crew_command(cmd_original)
        elif cmd_original.startswith("/interact"):
            await self._parse_interact_command(cmd_original)
        elif cmd_original.startswith("/assist"):
            await self._parse_assist_command(cmd_original)
        elif cmd_lower == "/conversations":
            try:
                from ..workspaces.utils import get_conversations_base
                from .conversation_store import ConversationStore

                store = ConversationStore(get_conversations_base())
                convs = store.list_conversations()

                def on_conv_selected(meta) -> None:
                    if meta is not None:
                        self.call_later(self._restore_conversation, meta.id)

                await self.push_screen(
                    ConversationsScreen(convs, store), on_conv_selected
                )
            except Exception as e:
                self._add_system(f"[!] Conversations error: {e}")
        else:
            self._add_system(f"Unknown command: {cmd}\nType /help for commands.")

    async def _parse_spawn_command(self, cmd: str) -> None:
        """Parse and execute /spawn command — manually spawn a child MCP agent."""
        import shlex

        if not self.agent:
            self._add_system("[!] No agent initialised.")
            return

        rest = cmd[len("/spawn") :].strip()

        # Parse flags
        target: str = ""
        scope: list[str] = []
        model: str = ""
        no_rag: bool = False
        no_mcp: bool = True

        try:
            tokens = shlex.split(rest)
        except ValueError as exc:
            self._add_system(f"[!] Parse error: {exc}")
            return

        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok == "--target" and i + 1 < len(tokens):
                target = tokens[i + 1]
                i += 2
            elif tok == "--scope" and i + 1 < len(tokens):
                i += 1
                while i < len(tokens) and not tokens[i].startswith("--"):
                    scope.append(tokens[i])
                    i += 1
            elif tok == "--model" and i + 1 < len(tokens):
                model = tokens[i + 1]
                i += 2
            elif tok == "--no-rag":
                no_rag = True
                i += 1
            elif tok == "--no-mcp":
                no_mcp = True
                i += 1
            elif not tok.startswith("--") and not target:
                # Bare positional argument → target
                target = tok
                i += 1
            else:
                i += 1

        self._add_user(cmd)
        self._add_system(
            f"Spawning child agent… target={target or 'none'}  "
            f"scope={scope or []}  model={model or 'default'}"
        )
        if not self._is_running:
            self._current_worker = self._run_spawn_command(
                target, scope, model, no_rag, no_mcp
            )

    @work(thread=False)
    async def _run_spawn_command(
        self,
        target: str,
        scope: list,
        model: str,
        no_rag: bool,
        no_mcp: bool,
    ) -> None:
        from ..tools.mcp_agent import spawn_child_agent

        self._is_running = True
        try:
            result = await spawn_child_agent(
                self.agent,
                self.agent.runtime,
                {
                    "target": target,
                    "scope": scope,
                    "model": model,
                    "no_rag": no_rag,
                    "no_mcp": no_mcp,
                },
            )
            self._add_system(result)
        except Exception as exc:
            self._add_system(f"[!] Spawn failed: {exc}")
        finally:
            self._is_running = False

    async def _parse_despawn_command(self, cmd: str) -> None:
        """Parse and execute /despawn <server_name>."""
        if not self.agent:
            self._add_system("[!] No agent initialised.")
            return

        server_name = cmd[len("/despawn") :].strip()
        if not server_name:
            self._add_system(
                "Usage: /despawn <server_name>\n"
                "Example: /despawn child_agent_1\n"
                "Use /mcp list to see active child agents."
            )
            return

        self._add_user(cmd)
        self._add_system(f"Despawning '{server_name}'…")
        if not self._is_running:
            self._current_worker = self._run_despawn_command(server_name)

    @work(thread=False)
    async def _run_despawn_command(self, server_name: str) -> None:
        from ..tools.mcp_agent import despawn_child_agent

        self._is_running = True
        try:
            result = await despawn_child_agent(
                self.agent, self.agent.runtime, server_name
            )
            self._add_system(result)
        except Exception as exc:
            self._add_system(f"[!] Despawn failed: {exc}")
        finally:
            self._is_running = False

    async def _parse_agent_command(self, cmd: str) -> None:
        """Parse and execute /agent command"""

        self._set_status("idle", "agent")
        self._update_header()
        self._add_system("Changed to agent mode\n")

        # Remove /agent prefix
        rest = cmd[len("/agent") :].strip()

        if not rest:
            self._add_system(
                "Usage: /agent <task>\n"
                "Example: /agent scan 192.168.1.1\n"
                "         /agent enumerate SSH on target"
            )
            return

        task = rest

        if not task:
            self._add_system("Error: No task provided. Usage: /agent <task>")
            return

        self._add_user(f"/agent {task}")
        self._add_system(">> Agent Mode")

        # Hide crew sidebar when entering agent mode
        self._hide_sidebar()

        if self.agent and not self._is_running:
            # Schedule agent mode and keep task handle
            # Schedule agent run and keep task handle (do not wrap in asyncio.create_task; @work returns a Worker)
            self._current_worker = self._run_agent_mode(task)

    async def _parse_crew_command(self, cmd: str) -> None:
        """Parse and execute /crew command"""

        self._set_status("idle", "crew")
        self._update_header()
        self._add_system("Changed to crew mode\n")

        # Remove /crew prefix
        rest = cmd[len("/crew") :].strip()

        if not rest:
            self._add_system(
                "Usage: /crew <task>\n"
                "Example: /crew https://example.com\n"
                "         /crew 192.168.1.100\n\n"
                "Crew mode spawns specialized workers in parallel:\n"
                "  - recon: Reconnaissance and mapping\n"
                "  - sqli: SQL injection testing\n"
                "  - xss: Cross-site scripting testing\n"
                "  - ssrf: Server-side request forgery\n"
                "  - auth: Authentication testing\n"
                "  - idor: Insecure direct object references\n"
                "  - info: Information disclosure"
            )
            return

        target = rest

        if not self._is_running:
            self._add_user(f"/crew {target}")
            self._show_sidebar()
            # Schedule crew mode and keep handle
            # Schedule crew run and keep task handle (do not wrap in asyncio.create_task; @work returns a Worker)
            self._current_worker = self._run_crew_mode(target)

    async def _parse_interact_command(self, cmd: str) -> None:
        # Use interact mode by default

        self._set_status("idle", "interact")
        self._update_header()
        self._add_system("Changed to interact mode\n")

        message = cmd[len("/interact") :].strip()
        if not message:
            self._add_system(
                "Usage: /interact <task>\n"
                "Example: /interact Can you help me recon the target site?\n"
            )
            return

        if self.agent and not self._is_running:
            # Schedule interact run and keep task handle (do not wrap in asyncio.create_task; @work returns a Worker)
            self._current_worker = self._run_interact(message)

    async def _parse_assist_command(self, cmd: str) -> None:
        # Use assist mode by default

        self._set_status("idle", "assist")
        self._update_header()
        self._add_system("Changed to assist mode\n")

        message = cmd[len("/assist") :].strip()
        if not message:
            self._add_system(
                "Usage: /assist <task>\n"
                "Example: /assist Can you help me recon the target site?\n"
            )
            return

        if self.agent and not self._is_running:
            # Schedule assist run and keep task handle (do not wrap in asyncio.create_task; @work returns a Worker)
            self._current_worker = self._run_assist(message)

    async def _parse_mcp_command(self, cmd: str) -> None:
        # Remove /agent prefix
        rest = cmd[len("/mcp") :].strip()

        if not rest:
            self._add_system(
                "Usage: /mcp <command>\n" "Example: /mcp list \n" "         /mcp add"
            )
            return

        action = rest

        if action == "list":
            if self.mcp_manager:

                # Open the interactive mcp browser (split-pane).
                try:
                    await self.push_screen(
                        MCPScreen(
                            mcp_manager=self.mcp_manager, agent=self.agent, tui=self
                        )
                    )
                except Exception:
                    pass
        elif action.startswith("add"):

            from ..tools import get_all_tools, register_tool_instance

            args = rest[len("add") :].strip()

            # Parse the args string into individual components
            parts = args.split()
            if len(parts) < 2:
                self._add_system(
                    "Usage: /mcp add <type> <name> <command|url> [args...]"
                )
                return

            mcp_type = parts[0]
            name = parts[1]
            command_or_url = parts[1]

            mcp_args = parts[2:] if len(parts) > 2 else []

            if not self.mcp_manager:
                return

            if mcp_type == "sse":
                self.mcp_manager.add_sse_server(
                    name=name,
                    url=command_or_url,
                )
            else:
                self.mcp_manager.add_stdio_server(
                    name=name,
                    command=command_or_url,
                    args=mcp_args,
                )

            server = await self.mcp_manager.connect_server(name)

            self.mcp_server_count = len(self.mcp_manager.list_configured_servers())

            if server:

                tools = self.mcp_manager.create_mcp_tools_from_server(server)

                if self.agent:
                    self.agent.add_tools(tools)

                for tool in tools:
                    register_tool_instance(tool)

                self.all_tools = get_all_tools()
                self._update_header()

        if not action:
            self._add_system("Error: No action provided. Usage: /mcp <command>")
            return

    def _show_sidebar(self) -> None:
        """Show the sidebar for crew mode."""
        try:
            import time

            sidebar = self.query_one("#sidebar")
            sidebar.add_class("visible")

            chat_area = self.query_one("#chat-area")
            chat_area.add_class("with-sidebar")

            # Setup tree
            tree = self.query_one("#workers-tree", CrewTree)
            tree.root.expand()
            tree.show_root = False

            # Clear old nodes
            tree.root.remove_children()
            self._crew_worker_nodes.clear()
            self._crew_workers.clear()
            self._worker_events.clear()
            self._crew_findings_count = 0

            # Start tracking time and tokens
            self._crew_start_time = time.time()
            self._crew_tokens_used = 0

            # Start stats timer (update every second)
            if self._crew_stats_timer:
                self._crew_stats_timer.stop()
            self._crew_stats_timer = self.set_interval(1.0, self._update_crew_stats)

            # Start spinner timer for running workers (faster interval for smooth animation)
            if self._spinner_timer:
                self._spinner_timer.stop()
            self._spinner_timer = self.set_interval(0.15, self._update_spinner)

            # Add crew root node (no orchestrator - just "CREW" header)
            self._crew_orchestrator_node = tree.root.add(
                "CREW", data={"type": "crew", "id": "crew"}
            )
            if self._crew_orchestrator_node:
                try:
                    self._crew_orchestrator_node.expand()
                    tree.select_node(self._crew_orchestrator_node)
                except Exception as e:
                    logging.getLogger(__name__).exception(
                        "Failed to expand/select crew orchestrator node: %s", e
                    )
                    try:
                        from .notifier import notify

                        notify(
                            "warning", f"TUI: failed to expand crew sidebar node: {e}"
                        )
                    except Exception:
                        logging.getLogger(__name__).exception(
                            "Failed to notify operator about crew node expansion failure"
                        )
            self._viewing_worker_id = None

            # Update stats
            self._update_crew_stats()
        except Exception as e:
            self._add_system(f"[!] Sidebar error: {e}")

    def _apply_target_display(self, target: str) -> None:
        """Update or insert the Target line in the system/banner area."""
        try:
            scroll = self.query_one("#chat-scroll", ScrollableContainer)
            updated = False
            for child in scroll.children:
                if isinstance(child, SystemMessage) and "PentestAgent ready" in getattr(
                    child, "message_content", ""
                ):
                    # Replace existing Target line if present, otherwise append
                    try:
                        if "Target:" in child.message_content:
                            child.message_content = re.sub(
                                r"(?m)^\s*Target:.*$",
                                f"  Target: {target}",
                                child.message_content,
                                count=1,
                            )
                        else:
                            child.message_content = (
                                child.message_content + f"\n  Target: {target}"
                            )
                        try:
                            child.refresh()
                        except Exception as e:
                            logging.getLogger(__name__).exception(
                                "Failed to refresh child message: %s", e
                            )
                            try:
                                from pentestagent.interface.notifier import notify

                                notify(
                                    "warning", f"TUI: failed to refresh UI element: {e}"
                                )
                            except Exception:
                                logging.getLogger(__name__).exception(
                                    "Failed to notify operator about child refresh failure"
                                )
                    except Exception as e:
                        logging.getLogger(__name__).exception(
                            "Failed to update SystemMessage target line: %s", e
                        )
                        try:
                            from pentestagent.interface.notifier import notify

                            notify("warning", f"Failed to update target display: {e}")
                        except Exception:
                            logging.getLogger(__name__).exception(
                                "Failed to notify operator about target update error"
                            )
                        child.message_content = (
                            child.message_content + f"\n  Target: {target}"
                        )
                    updated = True
                    break
                if not updated:
                    try:
                        self._update_header(target=target)
                    except Exception:
                        logging.getLogger(__name__).exception(
                            "Failed to update persistent header with target"
                        )
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed updating in-scroll target display: %s", e
            )
            # Also update the persistent header so the target is always visible
        try:
            self._update_header(target=target)
        except Exception:
            pass

    def _update_header(
        self, model_line: Optional[str] = None, target: Optional[str] = None
    ) -> None:
        """Compose and update the persistent header widget."""
        try:
            header = self.query_one("#header", Static)
            # Build header text from provided pieces or current state
            lines: List[str] = []
            if model_line:
                lines.append(model_line)
            else:
                # try to recreate a compact model/runtime line
                runtime_str = (
                    "Docker" if getattr(self, "use_docker", False) else "Local"
                )
                tools_count = 0
                if self.agent:
                    tools_count = len([t for t in self.agent.get_tools() if t.enabled])
                mode = getattr(self, "_mode", "")
                mode += " (use /assist for single tool execution, /agent or /crew for autonomous modes, /interact for interactive chat)"
                lines.append(
                    f"+ PentestAgent ready\n  Model: {getattr(self, 'model', '')} | Tools: {tools_count} | MCP: {getattr(self, 'mcp_server_count', '')} | RAG: {getattr(self, 'rag_doc_count', '')}\n  Runtime: {runtime_str} | Mode: {mode}"
                )
            # Ensure target line is present/updated
            if target is None:
                target = getattr(self, "target", "")
            if target:
                # append target on its own line
                lines.append(f"  Target: {target}")

            header.update("\n".join(lines))
        except Exception:
            pass

    def _hide_sidebar(self) -> None:
        """Hide the sidebar."""
        try:
            # Stop stats timer
            if self._crew_stats_timer:
                self._crew_stats_timer.stop()
                self._crew_stats_timer = None

            sidebar = self.query_one("#sidebar")
            sidebar.remove_class("visible")

            chat_area = self.query_one("#chat-area")
            chat_area.remove_class("with-sidebar")
        except Exception as e:
            logging.getLogger(__name__).exception("Sidebar error: %s", e)
            try:
                from .notifier import notify

                notify("warning", f"TUI: sidebar error: {e}")
            except Exception:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about sidebar error"
                )

    def _update_crew_stats(self) -> None:
        """Update crew stats panel."""
        try:
            import time

            text = Text()

            # Elapsed time
            text.append("Time:   ", style="bold #d4d4d4")
            if self._crew_start_time:
                elapsed = time.time() - self._crew_start_time
                if elapsed < 60:
                    time_str = f"{int(elapsed)}s"
                elif elapsed < 3600:
                    mins = int(elapsed // 60)
                    secs = int(elapsed % 60)
                    time_str = f"{mins}m {secs}s"
                else:
                    hrs = int(elapsed // 3600)
                    mins = int((elapsed % 3600) // 60)
                    time_str = f"{hrs}h {mins}m"
                text.append(time_str, style="#9a9a9a")
            else:
                text.append("--", style="#525252")

            text.append("\n")

            # Tokens used
            text.append("Tokens: ", style="bold #d4d4d4")
            if self._crew_tokens_used > 0:
                if self._crew_tokens_used >= 1000:
                    token_str = f"{self._crew_tokens_used / 1000:.1f}k"
                else:
                    token_str = str(self._crew_tokens_used)
                text.append(token_str, style="#9a9a9a")
            else:
                text.append("--", style="#525252")

            stats = self.query_one("#crew-stats", Static)
            stats.update(text)
            stats.border_title = "# Stats"
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to hide sidebar: %s", e)
            try:
                from .notifier import notify

                notify("warning", f"TUI: failed to hide sidebar: {e}")
            except Exception:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about hide_sidebar failure"
                )

    def _update_spinner(self) -> None:
        """Update spinner animation for running workers."""
        try:
            # Advance spinner frame
            self._spinner_frame += 1

            # Only update labels for running workers (efficient)
            has_running = False
            for worker_id, worker in self._crew_workers.items():
                if worker.get("status") == "running":
                    has_running = True
                    # Update the tree node label
                    if worker_id in self._crew_worker_nodes:
                        node = self._crew_worker_nodes[worker_id]
                        node.set_label(self._format_worker_label(worker_id))

            # Stop spinner if no workers are running (save resources)
            if not has_running and self._spinner_timer:
                self._spinner_timer.stop()
                self._spinner_timer = None
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to update crew stats: %s", e)
            try:
                from .notifier import notify

                notify("warning", f"TUI: failed to update crew stats: {e}")
            except Exception:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about crew stats update failure"
                )

    def _add_crew_worker(self, worker_id: str, worker_type: str, task: str) -> None:
        """Add a worker to the sidebar tree."""
        self._crew_workers[worker_id] = {
            "worker_type": worker_type,
            "task": task,
            "status": "pending",
            "findings": 0,
        }

        try:
            label = self._format_worker_label(worker_id)
            if self._crew_orchestrator_node:
                node = self._crew_orchestrator_node.add(
                    label, data={"type": "worker", "id": worker_id}
                )
                self._crew_worker_nodes[worker_id] = node
                try:
                    self._crew_orchestrator_node.expand()
                except Exception as e:
                    logging.getLogger(__name__).exception(
                        "Failed to expand crew orchestrator node: %s", e
                    )
                    try:
                        from .notifier import notify

                        notify("warning", f"TUI: failed to expand crew node: {e}")
                    except Exception:
                        logging.getLogger(__name__).exception(
                            "Failed to notify operator about crew node expansion failure"
                        )
            self._update_crew_stats()
        except Exception as e:
            logging.getLogger(__name__).exception("Failed to update spinner: %s", e)
            try:
                from .notifier import notify

                notify("warning", f"TUI: failed to update spinner: {e}")
            except Exception:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about spinner update failure"
                )

    def _update_crew_worker(self, worker_id: str, **updates) -> None:
        """Update a worker's state."""
        if worker_id not in self._crew_workers:
            return

        self._crew_workers[worker_id].update(updates)

        # Restart spinner if a worker started running
        if updates.get("status") == "running" and not self._spinner_timer:
            self._spinner_timer = self.set_interval(0.15, self._update_spinner)

        try:
            if worker_id in self._crew_worker_nodes:
                label = self._format_worker_label(worker_id)
                self._crew_worker_nodes[worker_id].set_label(label)
            self._update_crew_stats()
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to add crew worker node: %s", e
            )
            try:
                from .notifier import notify

                notify("warning", f"TUI: failed to add crew worker node: {e}")
            except Exception:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about add_crew_worker failure"
                )

    def _format_worker_label(self, worker_id: str) -> Text:
        """Format worker label for tree."""
        worker = self._crew_workers.get(worker_id, {})
        status = worker.get("status", "pending")
        wtype = worker.get("worker_type", "worker")
        findings = worker.get("findings", 0)

        # 4-state icons: working (braille), done (checkmark), warning (!), error (X)
        if status in ("running", "pending"):
            # Animated braille spinner for all in-progress states
            icon = self._spinner_frames[self._spinner_frame % len(self._spinner_frames)]
            color = "#d4d4d4"  # white
        elif status == "complete":
            icon = "✓"
            color = "#22c55e"  # green
        elif status == "warning":
            icon = "!"
            color = "#f59e0b"  # amber/orange
        else:  # error, cancelled, unknown
            icon = "✗"
            color = "#ef4444"  # red

        text = Text()
        text.append(f"{icon} ", style=color)
        text.append(wtype.upper(), style="bold")

        if status == "complete" and findings > 0:
            text.append(f" [{findings}]", style="#22c55e")  # green
        elif status in ("error", "cancelled"):
            # Don't append " !" here since we already have the X icon
            pass

        return text

    def _handle_worker_event(
        self, worker_id: str, event_type: str, data: Dict[str, Any]
    ) -> None:
        """Handle worker events from CrewAgent - updates tree sidebar only."""
        try:
            if event_type == "spawn":
                worker_type = data.get("worker_type", "unknown")
                task = data.get("task", "")
                self._add_crew_worker(worker_id, worker_type, task)
            elif event_type == "status":
                status = data.get("status", "running")
                self._update_crew_worker(worker_id, status=status)
            elif event_type == "tool":
                # Add tool as child node under the agent
                tool_name = data.get("tool", "unknown")
                self._add_tool_to_worker(worker_id, tool_name)
            elif event_type == "tokens":
                # Track token usage
                tokens = data.get("tokens", 0)
                self._crew_tokens_used += tokens
            elif event_type == "complete":
                findings_count = data.get("findings_count", 0)
                self._update_crew_worker(
                    worker_id, status="complete", findings=findings_count
                )
                self._crew_findings_count += findings_count
                self._update_crew_stats()
            elif event_type == "warning":
                # Worker hit max iterations but has results
                self._update_crew_worker(worker_id, status="warning")
                reason = data.get("reason", "Partial completion")
                worker = self._crew_workers.get(worker_id, {})
                wtype = worker.get("worker_type", "worker")
                self._add_system(f"[!] {wtype.upper()} stopped: {reason}")
                self._update_crew_stats()
            elif event_type == "failed":
                # Worker determined task infeasible
                self._update_crew_worker(worker_id, status="failed")
                reason = data.get("reason", "Task infeasible")
                worker = self._crew_workers.get(worker_id, {})
                wtype = worker.get("worker_type", "worker")
                self._add_system(f"[!] {wtype.upper()} failed: {reason}")
                self._update_crew_stats()
            elif event_type == "error":
                self._update_crew_worker(worker_id, status="error")
                worker = self._crew_workers.get(worker_id, {})
                wtype = worker.get("worker_type", "worker")
                error_msg = data.get("error", "Unknown error")
                # Only show errors in chat - they're important
                self._add_system(f"[!] {wtype.upper()} failed: {error_msg}")
        except Exception as e:
            self._add_system(f"[!] Worker event error: {e}")

    def _add_tool_to_worker(self, worker_id: str, tool_name: str) -> None:
        """Add a tool usage as child node under worker in tree."""
        try:
            node = self._crew_worker_nodes.get(worker_id)
            if node:
                node.add_leaf(f"  {tool_name}")
                node.expand()
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to update crew worker display: %s", e
            )
            try:
                from .notifier import notify

                notify("warning", f"TUI: failed to update crew worker display: {e}")
            except Exception:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about update_crew_worker failure"
                )

    @on(Tree.NodeSelected, "#workers-tree")
    def on_worker_tree_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection."""
        node = event.node
        if node.data:
            node_type = node.data.get("type")
            if node_type == "crew":
                self._viewing_worker_id = None
            elif node_type == "worker":
                self._viewing_worker_id = node.data.get("id")

    @work(thread=False)
    async def _run_crew_mode(self, target: str) -> None:
        """Run crew mode with sidebar."""
        self._is_running = True
        self._should_stop = False
        self._set_status("thinking", "crew")

        try:
            from ..agents.base_agent import AgentMessage
            from ..agents.crew import CrewOrchestrator
            from ..llm import LLM, ModelConfig

            # Build prior context from assist/agent conversation history
            prior_context = self._build_prior_context()

            # Ensure model/runtime are available for static analysis
            assert self.model is not None
            assert self.runtime is not None

            llm = LLM(model=self.model, config=ModelConfig(temperature=0.7))

            crew = CrewOrchestrator(
                llm=llm,
                tools=self.all_tools,
                runtime=self.runtime,
                on_worker_event=self._handle_worker_event,
                rag_engine=self.rag_engine,
                target=target,
                prior_context=prior_context,
            )
            self._current_crew = crew  # Track for cancellation

            self._add_system(f"@ Task: {target}")

            # Track crew results for memory
            crew_report = None

            async for update in crew.run(target):
                if self._should_stop:
                    await crew.cancel()
                    self._add_system("[!] Stopped by user")
                    break

                phase = update.get("phase", "")

                if phase == "starting":
                    self._set_status("thinking", "crew")

                elif phase == "tokens":
                    # Track orchestrator token usage
                    tokens = update.get("tokens", 0)
                    self._crew_tokens_used += tokens
                    self._update_crew_stats()

                elif phase == "thinking":
                    # Show the orchestrator's reasoning
                    content = update.get("content", "")
                    if content:
                        self._add_thinking(content)

                elif phase == "tool_call":
                    # Show orchestration tool calls
                    tool = update.get("tool", "")
                    args = update.get("args", {})
                    self._add_tool(tool, str(args))

                elif phase == "tool_result":
                    # Tool results are tracked via worker events
                    pass

                elif phase == "complete":
                    crew_report = update.get("report", "")
                    if crew_report:
                        self._add_assistant(crew_report)

                elif phase == "error":
                    error = update.get("error", "Unknown error")
                    self._add_system(f"[!] Crew error: {error}")

            # Add crew results to main agent's conversation history
            # so assist mode can reference what happened
            if self.agent and crew_report:
                # Add the crew task as a user message
                self.agent.conversation_history.append(
                    AgentMessage(
                        role="user",
                        content=f"[CREW MODE] Run parallel analysis on target: {target}",
                    )
                )
                # Add the crew report as assistant response
                self.agent.conversation_history.append(
                    AgentMessage(role="assistant", content=crew_report)
                )

            self._set_status("complete", "crew")
            self._add_system("+ Crew task complete.")

            # Stop timers
            if self._crew_stats_timer:
                self._crew_stats_timer.stop()
                self._crew_stats_timer = None
            if self._spinner_timer:
                self._spinner_timer.stop()
                self._spinner_timer = None

            # Clear crew reference
            self._current_crew = None

        except asyncio.CancelledError:
            # Cancel crew workers first
            if self._current_crew:
                await self._current_crew.cancel()
                self._current_crew = None
            self._add_system("[!] Cancelled")
            self._set_status("idle", "crew")
            # Stop timers on cancel
            if self._crew_stats_timer:
                self._crew_stats_timer.stop()
                self._crew_stats_timer = None
            if self._spinner_timer:
                self._spinner_timer.stop()
                self._spinner_timer = None

        except Exception as e:
            import traceback

            # Cancel crew workers on error too
            if self._current_crew:
                try:
                    await self._current_crew.cancel()
                except Exception as e:
                    logging.getLogger(__name__).exception(
                        "Failed to add tool to worker node: %s", e
                    )
                    try:
                        from .notifier import notify

                        notify("warning", f"TUI: failed to add tool to worker: {e}")
                    except Exception:
                        logging.getLogger(__name__).exception(
                            "Failed to notify operator about add_tool_to_worker failure"
                        )
                self._current_crew = None
            self._add_system(f"[!] Crew error: {e}\n{traceback.format_exc()}")
            self._set_status("error")
            # Stop timers on error too
            if self._crew_stats_timer:
                self._crew_stats_timer.stop()
                self._crew_stats_timer = None
            if self._spinner_timer:
                self._spinner_timer.stop()
                self._spinner_timer = None
        finally:
            await self._save_current_conversation()
            self._is_running = False

    async def _display_responses(
        self,
        responses,
        tool_messages_mapping: dict,
        *,
        is_agent: bool = False,
    ) -> None:
        """Consume an agent message iterator and update the chat UI.

        Shared by _run_interact, _run_assist, _run_agent_mode and
        _run_wake_up_mode.  The only behavioural differences between modes
        are gated on is_agent:
          - agent:      intermediate metadata treated as thinking; state checks
                        after each message; _set_status("thinking") between turns
          - non-agent:  no state checks; "finish" tool calls/results skipped
        """
        if is_agent:
            from ..agents.base_agent import AgentState

        async for response in responses:
            if self._should_stop:
                self._add_system("[!] Stopped by user")
                break

            self._set_status("processing")

            if response.content:
                content = response.content.strip()
                if response.tool_calls or (
                    is_agent and response.metadata.get("intermediate")
                ):
                    self._add_thinking(content)
                else:
                    self._add_assistant(content)

            if response.tool_calls:
                for call in response.tool_calls:
                    if not is_agent and call.name == "finish":
                        continue
                    args_str = str(call.arguments)
                    tool_messages_mapping[call.id] = self._add_tool(call.name, args_str)

            if response.tool_results:
                for result in response.tool_results:
                    if result.tool_name == "finish":
                        continue
                    if result.tool_call_id not in tool_messages_mapping:
                        continue
                    if result.success:
                        self._add_tool_result(
                            tool_messages_mapping[result.tool_call_id],
                            result.tool_name,
                            result.result or "Done",
                        )
                    else:
                        self._add_tool_result(
                            tool_messages_mapping[result.tool_call_id],
                            result.tool_name,
                            f"Error: {result.error}",
                        )

            if is_agent:
                if self.agent.get_state() == AgentState.WAITING_INPUT:
                    self._set_status("waiting")
                    self._add_system("? Awaiting input...")
                    break
                elif self.agent.get_state() == AgentState.COMPLETE:
                    break
                self._set_status("thinking")

    @work(thread=False)
    async def _run_interact(self, message: str) -> None:
        """Run in interact mode"""
        if not self.agent:
            self._add_system("[!] Agent not ready")
            return

        self._is_running = True
        self._should_stop = False
        self._set_status("thinking", "interact")

        try:
            tool_messages_mapping: dict[str, ToolMessage] = {}
            await self._display_responses(
                self.agent.interact(message), tool_messages_mapping
            )
            self._set_status("idle", "interact")
        except asyncio.CancelledError:
            self._add_system("[!] Cancelled")
            self._set_status("idle", "interact")
        except Exception as e:
            self._add_system(f"[!] Error: {e}")
            self._set_status("error")
        finally:
            await self._save_current_conversation()
            self._is_running = False

    @work(thread=False)
    async def _run_assist(self, message: str) -> None:
        """Run in assist mode - single response"""
        if not self.agent:
            self._add_system("[!] Agent not ready")
            return

        self._is_running = True
        self._should_stop = False
        self._set_status("thinking", "assist")

        try:
            tool_messages_mapping: dict[str, ToolMessage] = {}
            await self._display_responses(
                self.agent.assist(message), tool_messages_mapping
            )
            self._set_status("idle", "assist")
        except asyncio.CancelledError:
            self._add_system("[!] Cancelled")
            self._set_status("idle", "assist")
        except Exception as e:
            self._add_system(f"[!] Error: {e}")
            self._set_status("error")
        finally:
            await self._save_current_conversation()
            self._is_running = False

    @work(thread=False)
    async def _run_agent_mode(self, task: str) -> None:
        """Run in agent mode - autonomous until task complete or user stops"""
        if not self.agent:
            self._add_system("[!] Agent not ready")
            return

        self._is_running = True
        self._should_stop = False
        self._set_status("thinking", "agent")

        try:
            tool_messages_mapping: dict[str, ToolMessage] = {}
            await self._display_responses(
                self.agent.agent_loop(task), tool_messages_mapping, is_agent=True
            )
            self._set_status("complete", "agent")
            self._add_system("+ Agent task complete. Back to assist mode.")
            await asyncio.sleep(1)
            self._set_status("idle", "assist")
        except asyncio.CancelledError:
            self._add_system("[!] Cancelled")
            self._set_status("idle", "assist")
        except Exception as e:
            self._add_system(f"[!] Error: {e}")
            self._set_status("error")
        finally:
            await self._save_current_conversation()
            self._is_running = False

    def _on_agent_wake_up_callback(self) -> None:
        """Triggered by notifier.agent_wake_up() — may come from any async context."""
        try:
            try:
                asyncio.get_running_loop()
                # Already on the app's event loop — post_message directly.
                self.post_message(ChildAgentWakeUpMessage())
                return
            except RuntimeError:
                pass
            # Called from a worker thread — use call_from_thread.
            if hasattr(self, "call_from_thread"):
                try:
                    self.call_from_thread(self.post_message, ChildAgentWakeUpMessage())
                    return
                except Exception:
                    pass
            self.post_message(ChildAgentWakeUpMessage())
        except Exception as e:
            logging.getLogger(__name__).exception(
                "_on_agent_wake_up_callback failed: %s", e
            )

    def on_child_agent_wake_up_message(self, _event: ChildAgentWakeUpMessage) -> None:
        """Received on Textual's main loop — safe to start a @work method here."""
        if not self._is_running and self.agent:
            self._current_worker = self._run_wake_up_mode()

    @work(thread=False)
    async def _run_wake_up_mode(self) -> None:
        """Resume processing a pending child-agent notification in the active mode.

        The notification has already been injected into conversation_history by
        the watcher.  Dispatches display logic per mode so the behaviour is
        identical to the regular runner (_run_assist / _run_interact /
        _run_agent_mode) — avoiding subtle differences in state checks or
        status updates that would break result display.
        """
        if not self.agent:
            return

        mode = self._mode
        self._is_running = True
        self._should_stop = False
        self._set_status("thinking", mode)
        tool_messages_mapping: dict[str, ToolMessage] = {}

        try:
            tool_messages_mapping: dict[str, ToolMessage] = {}
            await self._display_responses(
                self.agent.wake_up(mode),
                tool_messages_mapping,
                is_agent=(mode == "agent"),
            )
            self._set_status("idle", mode)

        except asyncio.CancelledError:
            self._add_system("[!] Cancelled")
            self._set_status("idle", mode)
        except Exception as e:
            self._add_system(f"[!] Error: {e}")
            self._set_status("error")
        finally:
            self._is_running = False

    def action_quit_app(self) -> None:
        # Stop any running tasks first
        if self._is_running:
            self._should_stop = True
            if (
                self._current_worker
                and not getattr(self._current_worker, "done", lambda: False)()
            ):
                cancel = getattr(self._current_worker, "cancel", None)
                if cancel:
                    cancel()
            if self._current_crew:
                # Schedule cancel but don't wait - we're exiting
                asyncio.create_task(self._cancel_crew())
        self.exit()

    def action_stop_agent(self) -> None:
        # Hide suggestions on Escape without stopping the agent
        try:
            suggestions = self.query_one("#cmd-suggestions", CommandSuggestions)
            if suggestions.display:
                suggestions.hide()
                self.query_one("#tab-hint", Static).display = False
                self.query_one("#chat-input", Input).styles.width = "1fr"
                return
        except Exception:
            pass
        if self._is_running:
            self._should_stop = True
            self._add_system("[!] Stopping...")

            # Cancel the running worker to interrupt blocking awaits
            if (
                self._current_worker
                and not getattr(self._current_worker, "done", lambda: False)()
            ):
                cancel = getattr(self._current_worker, "cancel", None)
                if cancel:
                    cancel()

            # Cancel crew orchestrator if running
            if self._current_crew:
                asyncio.create_task(self._cancel_crew())

            # Clean up agent state to prevent stale tool responses
            if self.agent:
                self.agent.cleanup_after_cancel()

            # Reconnect MCP servers (they may be in a bad state after cancellation)
            if self.mcp_manager:
                asyncio.create_task(self._reconnect_mcp_after_cancel())

    async def _cancel_crew(self) -> None:
        """Cancel crew orchestrator and all workers."""
        try:
            if self._current_crew:
                await self._current_crew.cancel()
                self._current_crew = None
                # Mark all running workers as cancelled in the UI
                for worker_id, worker in self._crew_workers.items():
                    if worker.get("status") in ("running", "pending"):
                        self._update_crew_worker(worker_id, status="cancelled")
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to cancel crew orchestrator cleanly: %s", e
            )
            try:
                from .notifier import notify

                notify("warning", f"TUI: failed during crew cancellation: {e}")
            except Exception:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about crew cancellation failure"
                )

    async def _reconnect_mcp_after_cancel(self) -> None:
        """Reconnect MCP servers after cancellation to restore clean state."""
        await asyncio.sleep(0.5)  # Brief delay for cancellation to propagate
        try:
            if self.mcp_manager:
                await self.mcp_manager.reconnect_all()
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to reconnect MCP servers after cancel: %s", e
            )
            try:
                from .notifier import notify

                notify(
                    "warning", f"TUI: failed to reconnect MCP servers after cancel: {e}"
                )
            except Exception:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about MCP reconnect failure"
                )

    def action_show_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_focus_next(self) -> None:
        """Complete suggestion with Tab, or fall back to normal focus cycling."""
        if self._suggestions_visible():
            try:
                suggestions = self.query_one("#cmd-suggestions", CommandSuggestions)
                new_value = suggestions.get_tab_completion()
                if new_value is not None:
                    inp = self.query_one("#chat-input", Input)
                    inp.value = new_value
                    inp.cursor_position = len(new_value)
                    # Refresh suggestions for the new value
                    suggestions.update_suggestions(new_value)
                    return
            except Exception:
                pass
        super().action_focus_next()

    # ----- History navigation -----

    def _suggestions_visible(self) -> bool:
        try:
            return self.query_one("#cmd-suggestions", CommandSuggestions).display
        except Exception:
            return False

    def action_history_up(self) -> None:
        """Navigate suggestions up, or recall previous input into the chat field."""
        if self._suggestions_visible():
            try:
                self.query_one("#cmd-suggestions", CommandSuggestions).select_previous()
            except Exception:
                pass
            return

        try:
            inp = self.query_one("#chat-input", Input)
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to query chat input for history up: %s", e
            )
            try:
                from .notifier import notify

                notify("warning", f"TUI: history navigation failed: {e}")
            except Exception:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about history_up failure"
                )
            return

        if not self._cmd_history:
            return

        # Move back but not below zero
        if self._history_index > 0:
            self._history_index -= 1

        inp.value = self._cmd_history[self._history_index]

    def action_history_down(self) -> None:
        """Navigate suggestions down, or recall next input (or clear when at end)."""
        if self._suggestions_visible():
            try:
                self.query_one("#cmd-suggestions", CommandSuggestions).select_next()
            except Exception:
                pass
            return

        try:
            inp = self.query_one("#chat-input", Input)
        except Exception as e:
            logging.getLogger(__name__).exception(
                "Failed to query chat input for history down: %s", e
            )
            try:
                from .notifier import notify

                notify("warning", f"TUI: history navigation failed: {e}")
            except Exception:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about history_down failure"
                )
            return

        if not self._cmd_history:
            return

        if self._history_index < len(self._cmd_history) - 1:
            self._history_index += 1
            inp.value = self._cmd_history[self._history_index]
        else:
            # Past the end: clear input and set index to end
            self._history_index = len(self._cmd_history)
            inp.value = ""

    async def on_unmount(self) -> None:
        """Cleanup"""
        await self._save_current_conversation()

        if self.mcp_manager:
            try:
                await self.mcp_manager.disconnect_all()
                await asyncio.sleep(0.1)
            except Exception as e:
                logging.getLogger(__name__).exception(
                    "Failed to disconnect MCP manager on unmount: %s", e
                )
                try:
                    from .notifier import notify

                    notify("warning", f"TUI: error during shutdown disconnect: {e}")
                except Exception:
                    logging.getLogger(__name__).exception(
                        "Failed to notify operator about MCP disconnect failure"
                    )

        if self.runtime:
            try:
                await self.runtime.stop()
            except Exception as e:
                logging.getLogger(__name__).exception(
                    "Failed to stop runtime on unmount: %s", e
                )
                try:
                    from .notifier import notify

                    notify("warning", f"TUI: runtime stop error during shutdown: {e}")
                except Exception:
                    logging.getLogger(__name__).exception(
                        "Failed to notify operator about runtime stop failure"
                    )


# ----- Entry Point -----


def run_tui(
    target: Optional[str] = None,
    model: Optional[str] = None,
    use_docker: bool = False,
):
    """Run the PentestAgent TUI"""
    # Pre-build RAG before Textual takes over the terminal.
    # On Python 3.14 Textual sets terminal FDs to raw/CLOEXEC mode;
    # sentence-transformers then spawns worker subprocesses that inherit
    # those FDs and crash with "bad value(s) in fds_to_keep".
    # Indexing here (before app.run()) avoids that entirely.
    prebuilt_rag = None
    try:
        import os
        from pathlib import Path as _Path

        from ..knowledge import RAGEngine

        embeddings_setting = os.getenv("PENTESTAGENT_EMBEDDINGS", "").lower()
        if embeddings_setting == "openai":
            use_local = False
        else:
            use_local = not os.getenv("OPENAI_API_KEY")

        bundled_path = _Path(__file__).parent.parent / "knowledge" / "sources"
        local_path = _Path("knowledge")
        knowledge_path = None
        if local_path.exists() and any(local_path.rglob("*.*")):
            knowledge_path = local_path
        elif bundled_path.exists():
            knowledge_path = bundled_path

        if knowledge_path:
            prebuilt_rag = RAGEngine(
                knowledge_path=knowledge_path,
                use_local_embeddings=use_local,
            )
            prebuilt_rag.index()
    except Exception:
        prebuilt_rag = None

    app = PentestAgentTUI(
        target=target,
        model=model,
        use_docker=use_docker,
        prebuilt_rag=prebuilt_rag,
    )
    app.run()


if __name__ == "__main__":
    run_tui()
