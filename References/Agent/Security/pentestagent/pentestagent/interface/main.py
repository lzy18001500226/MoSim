"""Main entry point for PentestAgent."""

import argparse
import asyncio
from pathlib import Path

from aiohttp import web

from ..config.constants import AGENT_MAX_ITERATIONS, DEFAULT_MODEL
from ..mcp.server import (
    MCPRouter,
    mcp_tool_registry,
    mcp_transport_stdio,
    mcp_transport_streamable_http,
)
from .cli import run_cli
from .tui import run_tui


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PentestAgent - AI Penetration Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pentestagent tui                              Launch TUI
  pentestagent tui -t 192.168.1.1               Launch TUI with target
  pentestagent run -t localhost --task "scan"   Headless run
  pentestagent tools list                       List available tools
  pentestagent mcp list                         List MCP servers
        """,
    )

    parser.add_argument("--version", action="version", version="PentestAgent 0.2.0")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Common arguments for runtime modes
    runtime_parent = argparse.ArgumentParser(add_help=False)
    runtime_parent.add_argument("--target", "-t", help="Target (IP, hostname, or URL)")
    runtime_parent.add_argument(
        "--model",
        "-m",
        default=DEFAULT_MODEL,
        help="LLM model (set PENTESTAGENT_MODEL in .env)",
    )
    runtime_parent.add_argument(
        "--docker",
        "-d",
        action="store_true",
        help="Run tools inside Docker container (requires Docker)",
    )
    runtime_parent.add_argument(
        "--playbook",
        "-p",
        help="Playbook to execute (e.g., thp3_web)",
    )

    # TUI subcommand
    subparsers.add_parser(
        "tui", parents=[runtime_parent], help="Launch TUI (Interactive Mode)"
    )

    # Run subcommand (Headless)
    run_parser = subparsers.add_parser(
        "run", parents=[runtime_parent], help="Run in headless mode"
    )
    run_parser.add_argument("task", nargs="*", help="Task to run")
    run_parser.add_argument(
        "--report",
        "-r",
        nargs="?",
        const="auto",
        help=(
            "Generate report. "
            "If used without value, auto-generates path under loot/reports/. "
            "If omitted, no report is generated."
        ),
    )
    run_parser.add_argument(
        "--max-loops",
        type=int,
        default=AGENT_MAX_ITERATIONS,
        help=f"Max agent loops before stopping (default: {AGENT_MAX_ITERATIONS})",
    )

    # Tools subcommand
    tools_parser = subparsers.add_parser("tools", help="Manage tools")
    tools_subparsers = tools_parser.add_subparsers(
        dest="tools_command", help="Tool commands"
    )

    # tools list
    tools_list = tools_subparsers.add_parser("list", help="List all available tools")
    tools_list.add_argument(
        "--include-mcp",
        action="store_true",
        help="Temporarily connect to configured MCP servers and include their tools",
    )

    # tools call
    tools_call = tools_subparsers.add_parser(
        "call", help="Call a tool (via MCP daemon if available)"
    )
    tools_call.add_argument("server", help="MCP server name")
    tools_call.add_argument("tool", help="Tool name")
    tools_call.add_argument(
        "--json",
        dest="json_args",
        help="JSON string of arguments to pass to the tool",
        default=None,
    )

    # tools info
    tools_info = tools_subparsers.add_parser("info", help="Show tool details")
    tools_info.add_argument("name", help="Tool name")

    # tools env
    tools_subparsers.add_parser("env", help="Show detected CLI tools in environment")

    mcp_server_parser = subparsers.add_parser("mcp_server", help="Act as MCP server")
    mcp_server_parser.add_argument(
        "--type",
        choices=["stdio", "sse"],
        required=True,
        help="Transport type: stdio (for Claude Desktop / MCP clients) or sse (HTTP)",
    )
    mcp_server_parser.add_argument(
        "--host", default="0.0.0.0", help="SSE bind host (default: 0.0.0.0)"
    )
    mcp_server_parser.add_argument(
        "--port", type=int, default=8080, help="SSE bind port (default: 8080)"
    )
    mcp_server_parser.add_argument(
        "--target", default=None, help="Primary pentest target (IP / hostname)"
    )
    mcp_server_parser.add_argument(
        "--scope", nargs="*", default=[], help="In-scope targets/CIDRs"
    )
    mcp_server_parser.add_argument(
        "--model",
        default=None,
        help="Model identifier (overrides PENTESTAGENT_MODEL env var)",
    )
    mcp_server_parser.add_argument(
        "--docker",
        action="store_true",
        help="Use DockerRuntime instead of LocalRuntime",
    )
    mcp_server_parser.add_argument(
        "--no-rag", action="store_true", help="Skip RAG engine initialisation"
    )
    mcp_server_parser.add_argument(
        "--no-mcp", action="store_true", help="Skip external MCP server connections"
    )
    mcp_server_parser.add_argument(
        "--tui",
        action="store_true",
        help=(
            "Launch TUI observation panel alongside the MCP server. "
            "With --type sse the TUI runs in the same process. "
            "With --type stdio, requires --mcp-fifo-in/out so that MCP I/O "
            "uses named pipes instead of stdin/stdout (leaving the PTY free for the TUI)."
        ),
    )
    mcp_server_parser.add_argument(
        "--mcp-fifo-in",
        default=None,
        dest="mcp_fifo_in",
        help="Named FIFO path for incoming MCP requests (parent→child). "
        "Required when --type stdio --tui is used.",
    )
    mcp_server_parser.add_argument(
        "--mcp-fifo-out",
        default=None,
        dest="mcp_fifo_out",
        help="Named FIFO path for outgoing MCP responses (child→parent). "
        "Required when --type stdio --tui is used.",
    )

    # MCP subcommand
    mcp_parser = subparsers.add_parser("mcp", help="Manage MCP servers")
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command", help="MCP commands")

    # mcp list
    mcp_subparsers.add_parser("list", help="List configured MCP servers")

    # mcp status
    mcp_subparsers.add_parser("status", help="Show MCP daemon status (socket)")

    # mcp add
    mcp_add = mcp_subparsers.add_parser("add", help="Add an MCP server")
    mcp_add.add_argument("name", help="Server name")
    mcp_add.add_argument("command", help="Command to run (e.g., npx)")
    mcp_add.add_argument("args", nargs="*", help="Command arguments")
    mcp_add.add_argument("--description", default="", help="Server description")

    # mcp remove
    mcp_remove = mcp_subparsers.add_parser("remove", help="Remove an MCP server")
    mcp_remove.add_argument("name", help="Server name to remove")

    # mcp disable
    mcp_disable = mcp_subparsers.add_parser(
        "disable", help="Disable an MCP server (update config)"
    )
    mcp_disable.add_argument("name", help="Server name to disable")

    # mcp enable
    mcp_enable = mcp_subparsers.add_parser(
        "enable", help="Enable an MCP server (update config)"
    )
    mcp_enable.add_argument("name", help="Server name to enable")

    # mcp test
    mcp_test = mcp_subparsers.add_parser("test", help="Test MCP server connection")
    mcp_test.add_argument("name", help="Server name to test")
    # mcp connect (keep manager connected and register tools)
    mcp_connect = mcp_subparsers.add_parser(
        "connect", help="Connect to an MCP server and keep connection alive"
    )
    mcp_connect.add_argument(
        "name",
        nargs="?",
        default="all",
        help="Server name to connect (or 'all' to connect all configured)",
    )
    mcp_connect.add_argument(
        "--detach",
        action="store_true",
        help="Run as background daemon (writes PID file at ~/.pentestagent/mcp.pid)",
    )

    # mcp disconnect
    mcp_disconnect = mcp_subparsers.add_parser(
        "disconnect", help="Disconnect from an MCP server"
    )
    mcp_disconnect.add_argument(
        "name",
        nargs="?",
        default="all",
        help="Server name to disconnect (or 'all' to disconnect all)",
    )

    # workspace management
    ws_parser = subparsers.add_parser(
        "workspace", help="Workspace lifecycle and info commands"
    )
    ws_parser.add_argument(
        "action",
        nargs="?",
        help="Action or workspace name. Subcommands: info, note, clear, export, import",
    )
    ws_parser.add_argument(
        "rest", nargs=argparse.REMAINDER, help="Additional arguments"
    )

    # NOTE: use `workspace list` to list workspaces (handled by workspace subcommand)

    # target management
    tgt_parser = subparsers.add_parser(
        "target", help="Add or list targets for the active workspace"
    )
    tgt_parser.add_argument(
        "values", nargs="*", help="Targets to add (IP/CIDR/hostname)"
    )

    return parser, parser.parse_args()


def handle_tools_command(args: argparse.Namespace):
    """Handle tools subcommand."""
    from rich.console import Console
    from rich.table import Table

    from ..tools import get_all_tools, get_tool

    console = Console()

    if args.tools_command == "list":
        # Optionally include MCP-discovered tools by connecting temporarily
        manager = None
        mcp_socket_path = None
        try:
            from pathlib import Path

            mcp_socket_path = Path.home() / ".pentestagent" / "mcp.sock"
        except Exception:
            mcp_socket_path = None

        if getattr(args, "include_mcp", False):
            # Try to query running MCP daemon via unix socket first
            tried_socket = False
            if mcp_socket_path and mcp_socket_path.exists():
                tried_socket = True
                try:
                    import json
                    import socket

                    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                        s.connect(str(mcp_socket_path))
                        s.sendall(
                            (json.dumps({"cmd": "list_tools"}) + "\n").encode("utf-8")
                        )
                        # Read until EOF
                        resp = b""
                        while True:
                            part = s.recv(4096)
                            if not part:
                                break
                            resp += part
                    data = json.loads(resp.decode("utf-8"))
                    mcp_tools = []
                    if data.get("status") == "ok":
                        mcp_tools = data.get("tools", [])
                    else:
                        mcp_tools = []
                except Exception:
                    tried_socket = False

            if not tried_socket:
                from ..mcp.manager import MCPManager

                manager = MCPManager()
                try:
                    asyncio.run(manager.connect_all())
                except Exception:
                    pass

        try:
            tools = get_all_tools()
        finally:
            # If we temporarily connected to MCP servers, disconnect them to
            # ensure subprocess transports are closed before the event loop exits.
            if manager is not None:
                try:
                    asyncio.run(manager.disconnect_all())
                except Exception:
                    pass

        # Merge MCP daemon tools (if returned by socket) into displayed list
        if "mcp_tools" in locals() and mcp_tools:
            # Create lightweight objects to display alongside registered tools
            class _FakeTool:
                def __init__(self, name, category, description):
                    self.name = name
                    self.category = category
                    self.description = description

            for t in mcp_tools:
                tools.append(
                    _FakeTool(
                        f"mcp_{t.get('server')}_{t.get('name')}",
                        "mcp",
                        t.get("description", ""),
                    )
                )

        if not tools:
            console.print("[yellow]No tools found[/]")
            return

        table = Table(title="Available Tools")
        table.add_column("Name", style="cyan")
        table.add_column("Category", style="green")
        table.add_column("Description")

        for tool in sorted(tools, key=lambda t: t.name):
            desc = (
                tool.description[:50] + "..."
                if len(tool.description) > 50
                else tool.description
            )
            table.add_row(tool.name, tool.category, desc)

        console.print(table)
        console.print(f"\nTotal: {len(tools)} tools")

    elif args.tools_command == "info":
        tool = get_tool(args.name)
        if not tool:
            console.print(f"[red]Tool not found: {args.name}[/]")
            return

        console.print(f"\n[bold cyan]{tool.name}[/]")
        console.print(f"[dim]Category:[/] {tool.category}")
        console.print(f"\n{tool.description}")

        if tool.schema.properties:
            console.print("\n[bold]Parameters:[/]")
            for name, props in tool.schema.properties.items():
                required = (
                    "required" if name in (tool.schema.required or []) else "optional"
                )
                ptype = props.get("type", "any")
                desc = props.get("description", "")
                console.print(f"  [cyan]{name}[/] ({ptype}, {required}): {desc}")

    elif args.tools_command == "env":
        from ..runtime.runtime import detect_environment

        env = detect_environment()

        console.print("\n[bold]Environment:[/]")
        console.print(f"  OS: {env.os} ({env.os_version})")
        console.print(f"  Architecture: {env.architecture}")
        console.print(f"  Shell: {env.shell}")

        if env.available_tools:
            console.print(
                f"\n[bold]Detected CLI Tools ({len(env.available_tools)}):[/]"
            )

            # Group by category
            by_category = {}
            for tool_info in env.available_tools:
                if tool_info.category not in by_category:
                    by_category[tool_info.category] = []
                by_category[tool_info.category].append(tool_info)

            for category in sorted(by_category.keys()):
                tools_in_cat = by_category[category]
                console.print(f"\n[bold cyan]{category}[/] ({len(tools_in_cat)}):")
                for tool_info in sorted(tools_in_cat, key=lambda t: t.name):
                    console.print(f"  • {tool_info.name}")
        else:
            console.print("\n[yellow]No CLI tools detected[/]")
            console.print(
                "\n[dim]Tip: Install tools like nmap, curl, git to expand capabilities[/]"
            )

    else:
        console.print("[yellow]Use 'pentestagent tools --help' for commands[/]")

    if args.tools_command == "call":
        import json
        import socket

        server = args.server
        tool = args.tool
        json_args = {}
        if args.json_args:
            try:
                json_args = json.loads(args.json_args)
            except Exception as e:
                console.print(f"[red]Invalid JSON for --json: {e}[/]")
                return

        # Try daemon socket first
        from pathlib import Path

        sock = Path.home() / ".pentestagent" / "mcp.sock"
        if sock.exists():
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.connect(str(sock))
                    s.sendall(
                        (
                            json.dumps(
                                {
                                    "cmd": "call_tool",
                                    "server": server,
                                    "tool": tool,
                                    "args": json_args,
                                }
                            )
                            + "\n"
                        ).encode("utf-8")
                    )
                    resp = b""
                    while True:
                        part = s.recv(4096)
                        if not part:
                            break
                        resp += part
                data = json.loads(resp.decode("utf-8"))
                if data.get("status") == "ok":
                    console.print(
                        f"[green]Tool call succeeded. Result:[/] {data.get('result')}"
                    )
                else:
                    console.print(
                        f"[red]Tool call failed: {data.get('error')} {data.get('message','')}[/]"
                    )
                return
            except Exception:
                pass

        # Fallback: temporary connect and call
        from ..mcp.manager import MCPManager

        manager = MCPManager()

        async def _call():
            sv = await manager.connect_server(server)
            if not sv:
                raise RuntimeError(f"Failed to connect to server: {server}")
            try:
                res = await manager.call_tool(server, tool, json_args)
                return res
            finally:
                await manager.disconnect_all()

        try:
            res = asyncio.run(_call())
            console.print(f"[green]Tool call succeeded. Result:[/] {res}")
        except Exception as e:
            console.print(f"[red]Tool call failed: {e}[/]")


def handle_mcp_command(args: argparse.Namespace):
    """Handle MCP subcommand."""
    from rich.console import Console
    from rich.table import Table

    from ..mcp.manager import MCPManager

    console = Console()
    manager = MCPManager()

    if args.mcp_command == "list":
        servers = manager.list_configured_servers()

        if not servers:
            console.print("[yellow]No MCP servers configured[/]")
            console.print(
                "\nAdd a server with: pentestagent mcp add <name> <command> <args...>"
            )
            return

        table = Table(title="Configured MCP Servers")
        table.add_column("Name", style="cyan")
        table.add_column("Command", style="green")
        table.add_column("Args")
        table.add_column("Connected", style="yellow")

        for server in servers:
            args_str = " ".join(server["args"][:3])
            if len(server["args"]) > 3:
                args_str += "..."
            connected = "+" if server.get("connected") else "-"
            table.add_row(server["name"], server["command"], args_str, connected)

        console.print(table)
        console.print(f"\nConfig file: {manager.config_path}")

    elif args.mcp_command == "add":
        manager.add_stdio_server(
            name=args.name,
            command=args.command,
            args=args.args or [],
            description=args.description,
        )
        console.print(f"[green]Added MCP server: {args.name}[/]")
        console.print(f"  Command: {args.command} {' '.join(args.args or [])}")

    elif args.mcp_command == "remove":
        if manager.remove_server(args.name):
            console.print(f"[yellow]Removed MCP server: {args.name}[/]")
        else:
            console.print(f"[red]Server not found: {args.name}[/]")

    elif args.mcp_command == "disable":
        if manager.set_enabled(args.name, False):
            console.print(f"[yellow]Disabled MCP server in config: {args.name}[/]")
        else:
            console.print(f"[red]Server not found: {args.name}[/]")

    elif args.mcp_command == "enable":
        if manager.set_enabled(args.name, True):
            console.print(f"[green]Enabled MCP server in config: {args.name}[/]")
        else:
            console.print(f"[red]Server not found: {args.name}[/]")

    elif args.mcp_command == "test":
        console.print(f"[bold]Testing MCP server: {args.name}[/]\n")

        async def test_server():
            server = await manager.connect_server(args.name)
            if server and server.connected:
                console.print("[green]+ Connected successfully![/]")
                console.print(f"\n[bold]Available tools ({len(server.tools)}):[/]")
                for tool in server.tools:
                    desc = tool.get("description", "No description")[:60]
                    console.print(f"  [cyan]{tool['name']}[/]: {desc}")
                await manager.disconnect_all()
            else:
                console.print("[red]x Failed to connect[/]")

        asyncio.run(test_server())

    elif args.mcp_command == "connect":
        # Connect and keep the manager running so MCP tools remain registered
        name = args.name
        detach = getattr(args, "detach", False)

        console.print(f"[bold]Connecting to MCP server: {name}[/]\n")

        async def run_connect():
            # Long-running connect: connect requested server(s) and wait for signal
            import signal

            stop_event = asyncio.Event()

            def _signal_handler():
                try:
                    stop_event.set()
                except Exception:
                    pass

            loop = asyncio.get_running_loop()
            for s in (signal.SIGINT, signal.SIGTERM):
                try:
                    loop.add_signal_handler(s, _signal_handler)
                except Exception:
                    # Not all platforms support add_signal_handler (e.g., Windows)
                    pass

            if name == "all":
                await manager.connect_all()
            else:
                server = await manager.connect_server(name)
                if not server:
                    console.print(f"[red]Failed to connect: {name}[/]")
                    return

            # Start control socket so other CLI invocations can query daemon
            try:
                await manager.start_control_server()
            except Exception:
                pass

            console.print("[green]Connected. Press Ctrl-C to stop and disconnect.[/]")
            await stop_event.wait()

            console.print("\n[yellow]Shutting down connections...[/]")
            try:
                await manager.disconnect_all()
            except Exception:
                pass
            try:
                await manager.stop_control_server()
            except Exception:
                pass

        # If detach requested, perform a simple double-fork to daemonize
        if detach:
            import os
            from pathlib import Path

            pid_dir = Path.home() / ".pentestagent"
            pid_dir.mkdir(parents=True, exist_ok=True)
            pidfile = pid_dir / "mcp.pid"

            # Simple double-fork daemonization (POSIX only)
            try:
                pid = os.fork()
                if pid > 0:
                    # parent exits
                    console.print(
                        f"[green]MCP manager detached (pid: {pid}). PID file: {pidfile}[/]"
                    )
                    return
            except OSError as e:
                console.print(f"[red]Fork failed: {e}[/]")
                return

            os.setsid()
            try:
                pid2 = os.fork()
                if pid2 > 0:
                    # first child exits
                    os._exit(0)
            except OSError:
                pass

            # child continues as daemon
            # detach std file descriptors
            try:
                with (
                    open(os.devnull, "rb") as devnull_in,
                    open(os.devnull, "wb") as devnull_out,
                ):
                    os.dup2(devnull_in.fileno(), 0)
                    os.dup2(devnull_out.fileno(), 1)
                    os.dup2(devnull_out.fileno(), 2)
            except Exception:
                pass

            # write pidfile
            try:
                with open(pidfile, "w") as f:
                    f.write(str(os.getpid()))
            except Exception:
                pass

            # Run the connect loop in the daemon
            try:
                asyncio.run(run_connect())
            finally:
                try:
                    if pidfile.exists():
                        pidfile.unlink()
                except Exception:
                    pass
        else:
            try:
                asyncio.run(run_connect())
            except KeyboardInterrupt:
                console.print("[yellow]Interrupted by user[/]")

    elif args.mcp_command == "disconnect":
        name = args.name

        # If a background daemon was created via --detach, try to read its pidfile
        from pathlib import Path

        pid_dir = Path.home() / ".pentestagent"
        pidfile = pid_dir / "mcp.pid"

        if pidfile.exists():
            try:
                pid_text = pidfile.read_text().strip()
                pid = int(pid_text)
                import os
                import signal
                import time

                try:
                    os.kill(pid, signal.SIGTERM)
                    # give it a moment to exit
                    time.sleep(0.5)
                except ProcessLookupError:
                    pass
                try:
                    pidfile.unlink()
                except Exception:
                    pass

                console.print(
                    f"[green]Sent SIGTERM to daemon (pid: {pid}). PID file removed.[/]"
                )
                return
            except Exception:
                # Fall back to in-process disconnect below
                pass

        async def run_disconnect():
            if name == "all":
                await manager.disconnect_all()
                console.print("[green]Disconnected all MCP servers[/]")
            else:
                await manager.disconnect_server(name)
                console.print(f"[green]Disconnected MCP server: {name}[/]")

        asyncio.run(run_disconnect())

    elif args.mcp_command == "status":
        # Try querying the daemon socket
        import json
        import socket
        from pathlib import Path

        sock = Path.home() / ".pentestagent" / "mcp.sock"
        if sock.exists():
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.connect(str(sock))
                    s.sendall((json.dumps({"cmd": "status"}) + "\n").encode("utf-8"))
                    resp = b""
                    while True:
                        part = s.recv(4096)
                        if not part:
                            break
                        resp += part
                data = json.loads(resp.decode("utf-8"))
                if data.get("status") == "ok":
                    rows = data.get("servers", [])
                    if not rows:
                        console.print("[yellow]No MCP servers connected[/]")
                        return
                    table = Table(title="MCP Daemon Status")
                    table.add_column("Name")
                    table.add_column("Connected")
                    table.add_column("Tools")
                    for r in rows:
                        table.add_row(
                            r.get("name"),
                            "+" if r.get("connected") else "-",
                            str(r.get("tool_count", 0)),
                        )
                    console.print(table)
                    return
            except Exception:
                pass

        # Fallback: show configured servers and whether manager can see them
        servers = manager.list_configured_servers()
        table = Table(title="Configured MCP Servers")
        table.add_column("Name")
        table.add_column("Command")
        table.add_column("Connected")
        for s in servers:
            table.add_row(
                s.get("name"), s.get("command"), "+" if s.get("connected") else "-"
            )
        console.print(table)

    else:
        console.print("[yellow]Use 'pentestagent mcp --help' for available commands[/]")


async def _initialize(args: argparse.Namespace) -> dict:
    """
    Build every component via the shared initializer, then bootstrap the
    MCP tools registry.  Returns the full components dict so callers have
    access to runtime, rag_engine, etc.
    """
    from rich.console import Console

    from ..llm import LLM, ModelConfig
    from ..mcp.server import bootstrap
    from .initializer import build_agent_components

    console = Console(stderr=True)

    def _on_progress(level: str, msg: str) -> None:
        if level == "warning":
            console.print(f"[yellow]{msg}[/yellow]")
        else:
            console.print(msg)

    components = await build_agent_components(
        target=args.target or None,
        scope=list(args.scope),
        model=args.model or None,
        docker=args.docker,
        no_rag=args.no_rag,
        no_mcp=args.no_mcp,
        on_progress=_on_progress,
    )

    agent = components["agent"]
    runtime = components["runtime"]
    model = components["model"]

    # Bootstrap the MCP tool registry so run_task / run_task_async work.
    RuntimeClass = type(runtime)
    llm_kwargs = {
        "model": model,
        "config": ModelConfig(temperature=0.7),
        "rag_engine": components["rag_engine"],
    }
    runtime_kwargs: dict = {}

    bootstrap(
        primary_agent=agent,
        llm_class=LLM,
        runtime_class=RuntimeClass,
        llm_kwargs=llm_kwargs,
        runtime_kwargs=runtime_kwargs,
    )
    console.print("mcp_tools registry bootstrapped.")

    console.print(
        f"Startup complete | model={model} "
        f"tools={len(components['all_tools'])} "
        f"mcp_servers={components['mcp_server_count']} "
        f"rag_docs={components['rag_doc_count']} "
        f"runtime={type(runtime).__name__}"
    )

    return components


def start_mcp_server(args: argparse.Namespace) -> None:
    """
    Initialise PentestAgent and serve MCP requests over stdio or SSE.
    When ``args.tui`` is True (SSE-only), also launches the TUI in
    MCP observation mode so an operator can watch tasks live.
    """
    from rich.console import Console

    from ..mcp.server import MCPRouter, mcp_tool_registry, mcp_transport_stdio

    console = Console(stderr=True)

    if getattr(args, "tui", False):
        if args.type == "sse":
            asyncio.run(_run_mcp_with_tui(args))
            return
        # stdio + tui: requires named FIFOs so that the PTY is free for the TUI
        if not getattr(args, "mcp_fifo_in", None) or not getattr(
            args, "mcp_fifo_out", None
        ):
            console.print(
                "[red]--tui with --type stdio requires --mcp-fifo-in and --mcp-fifo-out[/red]"
            )
            return
        asyncio.run(_run_stdio_tui_fifo(args))
        return

    async def _run_stdio() -> None:
        await _initialize(args)
        router = MCPRouter(mcp_tool_registry)
        console.print("Serving over stdio.")
        await mcp_transport_stdio.run_stdio(router)

    async def _run_streamable_http() -> None:
        await _initialize(args)
        router = MCPRouter(mcp_tool_registry)
        app = mcp_transport_streamable_http.create_streamable_http_app(router)
        console.print(f"Serving SSE on {args.host}:{args.port}")
        await web._run_app(app, host=args.host, port=args.port)

    if args.type == "stdio":
        asyncio.run(_run_stdio())
    else:
        asyncio.run(_run_streamable_http())


async def _run_stdio_tui_fifo(args: argparse.Namespace) -> None:
    """Launch MCP STDIO server over named FIFOs *and* the TUI in the same process.

    The FIFOs decouple MCP I/O from the terminal's PTY, so Textual can use the
    PTY normally while the parent agent communicates via the pipe pair.
    """
    from ..mcp.server.mcp_tools import set_ui_hook
    from .tui import PentestAgentTUI

    components = await _initialize(args)

    app = PentestAgentTUI(
        mcp_mode=True,
        prebuilt_components=components,
    )
    set_ui_hook(app.on_mcp_event)

    router = MCPRouter(mcp_tool_registry)
    fifo_task = asyncio.create_task(
        mcp_transport_stdio.run_stdio_fifo(router, args.mcp_fifo_in, args.mcp_fifo_out)
    )

    try:
        await app.run_async()
    finally:
        fifo_task.cancel()
        try:
            await fifo_task
        except (asyncio.CancelledError, Exception):
            pass


async def _run_mcp_with_tui(args: argparse.Namespace) -> None:
    """Launch the MCP SSE server and the TUI observation panel together."""

    from ..mcp.server import MCPRouter, mcp_tool_registry
    from ..mcp.server.mcp_tools import set_ui_hook
    from .tui import PentestAgentTUI

    # Build all components first (before starting the TUI).
    components = await _initialize(args)

    # Create the TUI in MCP observation mode with the pre-built agent.
    app = PentestAgentTUI(
        mcp_mode=True,
        prebuilt_components=components,
    )

    # Wire MCP task events to the TUI.
    set_ui_hook(app.on_mcp_event)

    # Build the SSE server but run it as an asyncio task alongside the TUI.
    router = MCPRouter(mcp_tool_registry)
    aiohttp_app = mcp_transport_streamable_http.create_streamable_http_app(router)
    runner = web.AppRunner(aiohttp_app)
    await runner.setup()
    site = web.TCPSite(runner, args.host, args.port)
    await site.start()

    try:
        await app.run_async()
    finally:
        await runner.cleanup()


def handle_workspace_command(args: argparse.Namespace):
    """Handle workspace lifecycle commands and actions."""

    from pentestagent.workspaces.manager import WorkspaceError, WorkspaceManager
    from pentestagent.workspaces.utils import (
        export_workspace,
        import_workspace,
        resolve_knowledge_paths,
    )

    wm = WorkspaceManager()

    action = args.action
    rest = args.rest or []

    # No args -> show active workspace
    if not action:
        active = wm.get_active()
        if not active:
            print("No active workspace.")
        else:
            print(f"Active workspace: {active}")
        return

    # Subcommands
    if action == "info":
        # show info for active or specified workspace
        name = rest[0] if rest else wm.get_active()
        if not name:
            print("No workspace specified and no active workspace.")
            return
        try:
            meta = wm.get_meta(name)
            created = meta.get("created_at")
            last_active = meta.get("last_active_at")
            targets = meta.get("targets", [])
            kp = resolve_knowledge_paths()
            ks = "workspace" if kp.get("using_workspace") else "global"
            # estimate loot size if present
            import os

            loot_dir = (wm.workspace_path(name) / "loot").resolve()
            size = 0
            files = 0
            if loot_dir.exists():
                for rootp, _, filenames in os.walk(loot_dir):
                    for fn in filenames:
                        try:
                            fp = os.path.join(rootp, fn)
                            size += os.path.getsize(fp)
                            files += 1
                        except Exception:
                            # Best-effort loot stats: skip files we can't stat (e.g., permissions, broken symlinks)
                            pass

            print(f"Name: {name}")
            print(f"Created: {created}")
            print(f"Last active: {last_active}")
            print(f"Targets: {len(targets)}")
            print(f"Knowledge scope: {ks}")
            print(f"Loot files: {files}, approx size: {size} bytes")
        except Exception as e:
            print(f"Error retrieving workspace info: {e}")
        return

    if action == "list":
        # list all workspaces and mark active
        try:
            wss = wm.list_workspaces()
            active = wm.get_active()
            if not wss:
                print("No workspaces found.")
                return
            for name in sorted(wss):
                prefix = "* " if name == active else "  "
                print(f"{prefix}{name}")
        except Exception as e:
            print(f"Error listing workspaces: {e}")
        return

    if action == "note":
        # Append operator note to active workspace (or specified via --workspace/-w)
        active = wm.get_active()
        name = active

        text_parts = rest or []
        i = 0
        # Parse optional workspace selector flags before the note text.
        while i < len(text_parts):
            part = text_parts[i]
            if part in ("--workspace", "-w"):
                if i + 1 >= len(text_parts):
                    print("Usage: workspace note [--workspace NAME] <text>")
                    return
                name = text_parts[i + 1]
                i += 2
                continue
            # First non-option token marks the start of the note text
            break

        if not name:
            print("No active workspace. Set one with /workspace <name>.")
            return

        text = " ".join(text_parts[i:])
        if not text:
            print("Usage: workspace note [--workspace NAME] <text>")
            return
        try:
            wm.set_operator_note(name, text)
            print(f"Operator note saved for workspace '{name}'.")
        except Exception as e:
            print(f"Error saving note: {e}")
        return

    if action == "clear":
        active = wm.get_active()
        if not active:
            print("No active workspace.")
            return
        marker = wm.active_marker()
        try:
            if marker.exists():
                marker.unlink()
            print(f"Workspace '{active}' deactivated.")
        except Exception as e:
            print(f"Error deactivating workspace: {e}")
        return

    if action == "export":
        # export <NAME> [--output file.tar.gz]
        if not rest:
            print("Usage: workspace export <NAME> [--output file.tar.gz]")
            return
        name = rest[0]
        out = None
        if "--output" in rest:
            idx = rest.index("--output")
            if idx + 1 < len(rest):
                out = Path(rest[idx + 1])
        try:
            archive = export_workspace(name, output=out)
            print(f"Workspace exported: {archive}")
        except Exception as e:
            print(f"Export failed: {e}")
        return

    if action == "import":
        # import <ARCHIVE>
        if not rest:
            print("Usage: workspace import <archive.tar.gz>")
            return
        archive = Path(rest[0])
        try:
            name = import_workspace(archive)
            print(f"Workspace imported: {name} (not activated)")
        except Exception as e:
            print(f"Import failed: {e}")
        return

    # Default: treat action as workspace name -> create and set active
    name = action
    try:
        existed = wm.workspace_path(name).exists()
        if not existed:
            wm.create(name)
        wm.set_active(name)

        # restore last target if present
        last = wm.get_meta_field(name, "last_target")
        if last:
            print(f"Workspace '{name}' set active. Restored target: {last}")
        else:
            if existed:
                print(f"Workspace '{name}' set active.")
            else:
                print(f"Workspace '{name}' created and set active.")
    except WorkspaceError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error creating workspace: {e}")


def handle_workspaces_list():
    from pentestagent.workspaces.manager import WorkspaceManager

    wm = WorkspaceManager()
    wss = wm.list_workspaces()
    active = wm.get_active()
    if not wss:
        print("No workspaces found.")
        return
    for name in sorted(wss):
        prefix = "* " if name == active else "  "
        print(f"{prefix}{name}")


def handle_target_command(args: argparse.Namespace):
    """Handle target add/list commands."""
    from pentestagent.workspaces.manager import WorkspaceError, WorkspaceManager

    wm = WorkspaceManager()
    active = wm.get_active()
    if not active:
        print("No active workspace. Set one with /workspace <name>.")
        return

    vals = args.values or []
    try:
        if not vals:
            targets = wm.list_targets(active)
            if not targets:
                print(f"No targets for workspace '{active}'.")
            else:
                print(f"Targets for workspace '{active}': {targets}")
            return

        saved = wm.add_targets(active, vals)
        print(f"Targets for workspace '{active}': {saved}")
    except WorkspaceError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error updating targets: {e}")


def main():
    """Main entry point."""
    parser, args = parse_arguments()

    # Handle subcommands
    if args.command == "tools":
        handle_tools_command(args)
        return

    if args.command == "mcp":
        handle_mcp_command(args)
        return

    if args.command == "workspace":
        handle_workspace_command(args)
        return

    if args.command == "mcp_server":
        start_mcp_server(args)

    # 'workspace list' handled by workspace subcommand

    if args.command == "target":
        handle_target_command(args)
        return

    if args.command == "run":
        # Check model configuration
        if not args.model:
            print("Error: No model configured.")
            print("Set PENTESTAGENT_MODEL in .env file or use --model flag.")
            print(
                "Example: PENTESTAGENT_MODEL=gpt-5 or PENTESTAGENT_MODEL=claude-sonnet-4-20250514"
            )
            return

        if not args.target:
            print("Error: --target is required for run mode")
            return

        # Handle playbook or task
        task_description = ""
        mode = "agent"
        if args.playbook:
            from ..playbooks import get_playbook

            try:
                playbook = get_playbook(args.playbook)
                task_description = playbook.get_task()
                mode = getattr(playbook, "mode", "agent")

                # Use playbook's max_loops if defined
                if hasattr(playbook, "max_loops"):
                    args.max_loops = playbook.max_loops

                print(f"Loaded playbook: {playbook.name}")
                print(f"Description: {playbook.description}")
                print(f"Mode: {mode}")
            except ValueError as e:
                print(f"Error: {e}")
                return
        elif args.task:
            task_description = " ".join(args.task)
        else:
            print("Error: Either task (positional) or --playbook is required")
            return

        try:
            asyncio.run(
                run_cli(
                    target=args.target,
                    model=args.model,
                    task=task_description,
                    report=args.report,
                    max_loops=args.max_loops,
                    use_docker=args.docker,
                    mode=mode,
                )
            )
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user.")
        return

    if args.command == "tui":
        # Check model configuration
        if not args.model:
            print("Error: No model configured.")
            print("Set PENTESTAGENT_MODEL in .env file or use --model flag.")
            print(
                "Example: PENTESTAGENT_MODEL=gpt-5 or PENTESTAGENT_MODEL=claude-sonnet-4-20250514"
            )
            return

        run_tui(target=args.target, model=args.model, use_docker=args.docker)
        return

    # If no command provided, default to TUI
    if args.command is None:
        # Ensure a default model is configured; provide a friendly error if not
        if not DEFAULT_MODEL:
            print("Error: No default model configured (PENTESTAGENT_MODEL).")
            print(
                "Set PENTESTAGENT_MODEL in .env file or pass --model on the command line."
            )
            print(
                "Example: PENTESTAGENT_MODEL=gpt-5 or PENTESTAGENT_MODEL=claude-sonnet-4-20250514"
            )
            return

        run_tui(target=None, model=DEFAULT_MODEL, use_docker=False)
        return


if __name__ == "__main__":
    main()
