# MCP examples

PentestAgent connects to external MCP servers via a `mcp_servers.json` file in the project root. The format is the same as Claude Desktop.

Place the file at the root of the repo (next to `.env`) before starting the agent. Servers are connected at startup and manageable via the `/mcp` TUI command.

## Format

```json
{
  "mcpServers": {
    "server-name": {
      "command": "python",
      "args": ["path/to/server.py", "--transport", "stdio"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

For SSE servers use `"type": "sse"` and `"url"` instead of `command`/`args`:

```json
{
  "mcpServers": {
    "server-name": {
      "type": "sse",
      "url": "http://127.0.0.1:8085/sse"
    }
  }
}
```

## Examples

See the `stdio/` and `sse/` subdirectories for working configs.

### MetasploitMCP (stdio)

[MetasploitMCP](https://github.com/GH05TCREW/MetasploitMCP) exposes the Metasploit Framework over MCP. Start `msfrpcd` first, then add to `mcp_servers.json`:

```json
{
  "mcpServers": {
    "metasploit": {
      "command": "python",
      "args": ["path/to/MetasploitMCP.py", "--transport", "stdio"],
      "env": {
        "MSF_PASSWORD": "yourpassword",
        "MSF_SERVER": "127.0.0.1",
        "MSF_PORT": "55553",
        "MSF_SSL": "false"
      }
    }
  }
}
```

Start msfrpcd:

```bash
msfrpcd -P yourpassword -S -a 127.0.0.1 -p 55553
```
