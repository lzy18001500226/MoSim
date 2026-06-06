# PentestAgent — CLAUDE.md

## Project overview

**PentestAgent** (v0.2.0) is an AI-powered penetration testing framework built in Python.
It wraps LiteLLM to support any provider (Anthropic, OpenAI, etc.) and exposes a TUI,
a CLI, and an MCP server interface. The agent can run tools locally or inside a Docker
sandbox (base or Kali image).

## Tech stack

- **Python 3.10+**, packaged with Hatchling (`pyproject.toml`)
- **LiteLLM** — provider-agnostic LLM wrapper
- **Textual** — TUI framework (`pentestagent/interface/`)
- **Typer** — CLI framework
- **Playwright** — browser tool
- **MCP (Model Context Protocol)** — both client (consuming external servers) and server
  (exposing PentestAgent to Claude Desktop / Cursor / etc.)
- **FAISS + sentence-transformers** — optional RAG engine (`pip install -e ".[rag]"`)

## Repository layout

```
pentestagent/
  agents/
    crew/           # Multi-agent mode: orchestrator + worker pool + shadow graph
    pa_agent/       # Single-agent implementation
    state.py        # Shared agent state
  config/
    settings.py     # Global Settings dataclass (singleton via get_settings())
    constants.py    # Model defaults, iteration limits, etc.
  interface/
    cli.py          # Typer CLI entry-point
    notifier.py     # Event bus between agent and UI
    utils.py        # Shared UI helpers
  knowledge/
    graph.py        # ShadowGraph — derives strategic insights from notes
    indexer.py      # Indexes knowledge sources for RAG
    rag.py          # FAISS-backed retrieval
  llm/
    config.py       # LiteLLM configuration
    memory.py       # Conversation/token management
    utils.py        # Streaming helpers
  mcp/
    stdio_adapter.py    # STDIO MCP server transport
    example_adapter.py  # SSE MCP server transport
  playbooks/
    base_playbook.py
    thp3_recon.py / thp3_network.py / thp3_web.py
  runtime/
    docker_runtime.py   # Runs tool commands inside Docker
    tool_server.py      # Local runtime
  tools/
    loader.py       # Discovers & dynamically imports tool modules
    executor.py     # Executes tool calls, tracks tokens
    token_tracker.py
    terminal/       # Shell execution tool
    browser/        # Playwright browser tool
    web_search/     # Tavily web search (needs TAVILY_API_KEY)
    notes/          # Persistent findings store → loot/notes.json
    finish/         # Signals task completion
  workspaces/       # Workspace isolation helpers
loot/               # Persisted notes and findings (git-ignored)
mcp_examples/       # Example MCP configs and adapters
scripts/            # setup.sh / setup.ps1
tests/              # pytest suite
```

## Configuration

Create `.env` in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
PENTESTAGENT_MODEL=claude-sonnet-4-20250514

# Optional
TAVILY_API_KEY=...          # web_search tool
OPENAI_API_KEY=sk-...       # if using OpenAI
```

Settings are managed by `pentestagent/config/settings.py` (`get_settings()` singleton).
The MCP external-server config lives in `mcp_servers.json` (Claude Desktop format).

## Running the project

```bash
source venv/bin/activate
pentestagent                    # TUI
pentestagent -t 192.168.1.1     # TUI with pre-set target
pentestagent tui --docker       # Use Docker sandbox for tool execution
pentestagent run -t example.com --playbook thp3_web   # Run a playbook
pentestagent mcp_server --type stdio   # Expose as MCP server (STDIO)
pentestagent mcp_server --type sse     # Expose as MCP server (HTTP/SSE, port 8080)
```

## PentestAgent as MCP server

PentestAgent can expose itself as an MCP server so any MCP-compatible client
(Claude Desktop, Cursor, etc.) can drive it programmatically.

### Transports

```bash
# STDIO — for local clients
pentestagent mcp_server --type stdio
pentestagent mcp_server --type stdio --target 192.168.1.1 --scope 192.168.1.0/24 --docker

# SSE (HTTP) — for remote/networked clients (default: 0.0.0.0:8080)
pentestagent mcp_server --type sse
pentestagent mcp_server --type sse --host 0.0.0.0 --port 8080 --target 10.0.0.1
```

### Claude Desktop config (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "pentestagent": {
      "command": "pentestagent",
      "args": ["mcp_server", "--type", "stdio"]
    }
  }
}
```

### Tools exposed by the MCP server

| Category | Tools |
|----------|-------|
| Status / config | `get_server_status`, `get_config`, `update_config` |
| Task execution | `run_task` (blocking), `run_task_async` (returns task_id) |
| Task inspection | `list_tasks`, `get_task_status`, `get_task_result`, `await_tasks` |
| Task control | `cancel_task` |
| Tool management | `list_tools`, `enable_tool`, `disable_tool` |
| Conversation | `get_conversation_history`, `reset_conversation` |
| Memory | `store_memory`, `retrieve_memory`, `clear_memory` |
| Observability | `get_logs`, `get_metrics` |

### Async task pattern

```
run_task_async  task="Enumerate subdomains of example.com"
run_task_async  task="Run nmap SYN scan on example.com"
await_tasks     task_ids=["<id1>", "<id2>"]  timeout_seconds=300
get_task_result task_id="<id1>"
get_task_result task_id="<id2>"
```

### `mcp_server` flags

| Flag | Default | Description |
|------|---------|-------------|
| `--type` | *(required)* | `stdio` or `sse` |
| `--host` | `0.0.0.0` | SSE bind host |
| `--port` | `8080` | SSE bind port |
| `--target` | none | Primary pentest target |
| `--scope` | `[]` | In-scope CIDRs (space-separated) |
| `--model` | env var | Overrides `PENTESTAGENT_MODEL` |
| `--docker` | false | Use DockerRuntime |
| `--no-rag` | false | Skip RAG initialisation |
| `--no-mcp` | false | Skip external MCP connections |

---

## TUI commands (quick reference)

| Command | Description |
|---------|-------------|
| `/assist <task>` | Single-shot instruction with tool execution |
| `/agent <task>` | Autonomous single-agent loop |
| `/crew <task>` | Multi-agent: orchestrator spawns specialised workers |
| `/interact <task>` | Guided interactive chat |
| `/target <host>` | Set target |
| `/tools` | List available tools |
| `/notes` | Show saved findings |
| `/report` | Generate report from session |
| `/mcp list/add` | Manage MCP servers |
| `Esc` | Stop running agent |

## Conversation history controls (TUI)

Each user message in the TUI exposes two inline buttons: **rewind** and **fork**.

### Rewind

Clicking **rewind** on a user message opens a confirmation dialog and then truncates the
conversation back to just before that message — both in the UI and in the agent's
in-memory history. Use it to retry a query from scratch without saving the discarded path.

### Fork

Clicking **>> fork** on a user message:

1. **Saves** the current full conversation to the conversation store
   (`ConversationStore`, persisted under the workspaces base directory) and reports
   the short ID of the saved snapshot.
2. **Truncates** the conversation to just before the selected message (same as rewind).

This lets you branch off from any point while keeping the original conversation
retrievable. Typical use-case: try an alternative approach from a given message without
losing the thread you had so far.

Both controls are implemented in `pentestagent/interface/tui.py` via
`RewindButton` / `ForkButton` widgets and their corresponding `*ConfirmScreen` modals.

## Key architectural patterns

- **Tool registration**: Tools self-register via `pentestagent/tools/loader.py`. Add a new
  tool by creating a directory under `pentestagent/tools/<name>/` with an `__init__.py`
  that registers it with the tool registry.
- **Modes**: assist → single LLM call; agent → agentic loop; crew → `CrewOrchestrator`
  manages a `WorkerPool`; interact → streaming chat.
- **MCP server tools**: `run_task`, `run_task_async`, `await_tasks`, `get_task_result`,
  `list_tasks`, `cancel_task`, `list_tools`, `enable_tool`, `disable_tool`, `store_memory`,
  `retrieve_memory`, `get_logs`, `get_metrics`.
- **Agent self-spawning** (`spawn_mcp_agent`): running agent can spawn child agents as
  MCP servers over stdio, enabling hierarchical multi-agent workflows.
- **RAG tool optimizer**: if an MCP server exposes >128 tools, a single
  `mcp_<server>_rag_optimizer` meta-tool replaces them and retrieves relevant subsets via
  embedding similarity.
- **Notes persistence**: findings saved to `loot/notes.json` via the `notes` tool;
  categories: `credential`, `vulnerability`, `finding`, `artifact`.
- **ShadowGraph** (crew mode only): builds a knowledge graph from notes to provide
  strategic context to the orchestrator.

## Development

```bash
pip install -e ".[dev]"
pytest                       # Run tests
pytest --cov=pentestagent    # With coverage
black pentestagent           # Format
ruff check pentestagent      # Lint
```

Test config: `pytest.ini_options` in `pyproject.toml`, asyncio mode = auto.

## Docker

```bash
docker compose build
docker compose run --rm pentestagent          # Base image
docker compose --profile kali run --rm pentestagent-kali   # Kali image
```

## Legal

Only use against systems you have **explicit written authorisation** to test.
Unauthorised access is illegal. MIT licence.
