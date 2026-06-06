"""Terminal tool for PentestAgent."""

from typing import TYPE_CHECKING

from ..registry import ToolSchema, register_tool

if TYPE_CHECKING:
    from ...runtime import Runtime


@register_tool(
    name="terminal",
    description="Execute shell commands.",
    schema=ToolSchema(
        properties={
            "command": {
                "type": "string",
                "description": "The shell command to execute",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default: 300)",
                "default": 300,
            },
            "working_dir": {
                "type": "string",
                "description": "Working directory for the command (optional)",
            },
        },
        required=["command"],
    ),
    category="execution",
)
async def terminal(arguments: dict, runtime: "Runtime") -> str:
    """
    Execute a terminal command in the sandbox.

    Args:
        arguments: Dictionary with 'command', optional 'timeout' and 'working_dir'
        runtime: The runtime environment

    Returns:
        Formatted output string with command results
    """
    command = arguments["command"]
    timeout = arguments.get("timeout", 300)
    working_dir = arguments.get("working_dir")

    # Build the full command with working directory if specified
    if working_dir:
        full_command = f"cd {working_dir} && {command}"
    else:
        full_command = command

    # If the provided command appears to be flags-only (starts with '-')
    # it's likely the LLM intended to call a specific tool (e.g. `nmap`)
    # but omitted the binary name. Detect this pattern and prefix with
    # the `nmap` binary when available in the runtime environment.
    try:
        cmd_prefix = ""
        cmd_rest = full_command
        if "&&" in full_command:
            left, right = full_command.split("&&", 1)
            cmd_prefix = left + "&& "
            cmd_rest = right

        if cmd_rest.lstrip().startswith("-"):
            try:
                available = getattr(runtime, "environment", None)
                tool_names = (
                    [t.name for t in available.available_tools] if available else []
                )
            except Exception:
                tool_names = []

            # Heuristic mapping of common flags to likely binaries
            import re

            lower = cmd_rest.lower()
            chosen = None

            # nmap indicators
            if re.search(r"\b-p\b|\b-p[0-9]|-s[sv]|\b-on\b|\b-o[nag]\b", lower):
                if "nmap" in tool_names:
                    chosen = "nmap"

            # gobuster indicators (wordlist, dirscan)
            if not chosen and re.search(r"\b-w\b|--wordlist|\b-u\b|--url", lower):
                if "gobuster" in tool_names:
                    chosen = "gobuster"

            # rustscan/masscan indicators (large-port ranges, fast scan)
            if not chosen and re.search(
                r"\b--rate\b|\b--ping\b|\b--range\b|\b-z\b", lower
            ):
                for alt in ("rustscan", "masscan"):
                    if alt in tool_names:
                        chosen = alt
                        break

            # web fetchers
            if not chosen and re.search(r"https?://", cmd_rest):
                for alt in ("curl", "wget"):
                    if alt in tool_names:
                        chosen = alt
                        break

            # Fallback prefer nmap if present, then first interesting tool
            if not chosen:
                for alt in (
                    "nmap",
                    "rustscan",
                    "masscan",
                    "gobuster",
                    "nikto",
                    "ffuf",
                    "dirb",
                    "curl",
                    "wget",
                ):
                    if alt in tool_names:
                        chosen = alt
                        break

            if chosen:
                full_command = cmd_prefix + chosen + " " + cmd_rest.lstrip()
    except Exception:
        # Best-effort; do not fail if introspection errors occur
        pass

    result = await runtime.execute_command(full_command, timeout=timeout)

    # Truncate large outputs to prevent context window flooding
    MAX_OUTPUT_CHARS = 50000

    stdout = result.stdout or ""
    stderr = result.stderr or ""

    if len(stdout) > MAX_OUTPUT_CHARS:
        truncated_bytes = len(stdout) - MAX_OUTPUT_CHARS
        stdout = (
            stdout[: MAX_OUTPUT_CHARS // 2]
            + f"\n\n... [{truncated_bytes} chars truncated] ...\n\n"
            + stdout[-MAX_OUTPUT_CHARS // 2 :]
        )

    if len(stderr) > MAX_OUTPUT_CHARS:
        truncated_bytes = len(stderr) - MAX_OUTPUT_CHARS
        stderr = (
            stderr[: MAX_OUTPUT_CHARS // 2]
            + f"\n\n... [{truncated_bytes} chars truncated] ...\n\n"
            + stderr[-MAX_OUTPUT_CHARS // 2 :]
        )

    # Format the output
    output_parts = [f"Command: {command}"]

    if working_dir:
        output_parts.append(f"Working Directory: {working_dir}")

    output_parts.append(f"Exit Code: {result.exit_code}")

    if stdout:
        output_parts.append(f"\n--- stdout ---\n{stdout}")

    if stderr:
        output_parts.append(f"\n--- stderr ---\n{stderr}")

    if not stdout and not stderr:
        output_parts.append("\n(No output)")

    return "\n".join(output_parts)
