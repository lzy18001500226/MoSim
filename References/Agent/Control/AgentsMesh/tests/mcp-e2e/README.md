# MCP End-to-End Tests

Black-box test suite that drives the runner's MCP HTTP server (JSON-RPC 2.0)
and asserts the full chain: HTTP `/mcp` → runner gRPC client → backend gRPC
dispatch → service → Postgres. Complements (does not replace) the unit and
integration tests in `runner/internal/mcp/` and `backend/internal/api/grpc/`,
which mock one side of the link.

## Scope

- **In scope**: every MCP tool exposed by `runner/internal/mcp/registerTools()`
- **Out of scope**: real LLM behaviour (we use the `e2e-echo` stub agent),
  mTLS PKI, web/iOS/desktop UI

## Local run

```bash
# 1) Start the dev stack — this starts Postgres, the host backend, the host
#    runner (with MCP @ 127.0.0.1:19000), and seeds dev-org / dev-runner /
#    dev@agentsmesh.local. Idempotent.
bazel run //deploy/dev:up

# 2) Run the suites. The env vars below tell the harness which ports
#    deploy/dev published (defaults match the main worktree).
bazel test //tests/mcp-e2e/suites:e2e \
  --test_tag_filters=e2e \
  --test_env=BACKEND_HTTP_PORT=10015 \
  --test_env=MCP_PORT=19000 \
  --test_env=POSTGRES_PORT=10002 \
  --test_output=errors
```

If `deploy/dev/.env` has different ports (e.g. when running in a worktree
with a non-zero port offset), source it first:

```bash
source deploy/dev/.env
bazel test //tests/mcp-e2e/suites:e2e \
  --test_tag_filters=e2e \
  --test_env=BACKEND_HTTP_PORT=$BACKEND_HTTP_PORT \
  --test_env=MCP_PORT=19000 \
  --test_env=POSTGRES_PORT=$POSTGRES_PORT \
  --test_output=errors
```

## Layout

| Path | Role |
|---|---|
| `client/mcp.go` | 50-line JSON-RPC 2.0 over HTTP client, `X-Pod-Key` header, double-decode of `result.content[0].text` |
| `client/backend_rest.go` | `/api/v1` client (login, list_runners, create_pod, terminate_pod) |
| `client/db.go` | gorm-free `database/sql` queries for fact assertions (block count, op_log presence, workspace UUID lookup) |
| `fixture/env.go` | Read deploy/dev ports + creds from environment, with sensible defaults |
| `fixture/auth.go` | Process-scoped login cache (one token per `bazel test` invocation) |
| `fixture/runner.go` | Discover the online dev-runner via REST list |
| `fixture/pod.go` | `NewEchoPod(t)` creates a Pod, waits for runner registration via the debug `/pods` endpoint, registers `t.Cleanup` to terminate |
| `suites/*_test.go` | One file per MCP tool family |

## stub agent: `e2e-echo`

Registered by migration `000127_add_e2e_echo_agent.up.sql`. Agentfile:

```
AGENT e2e-echo
EXECUTABLE bash
MODE pty
MCP ON
arg "-c" "echo ready; while IFS= read -r line; do echo \"got: $line\"; done"
```

This is a real PTY pod (so `get_pod_snapshot`/`send_pod_input` work) without
any LLM API dependency. Tests that don't need PTY semantics still create one
to exercise the full lifecycle.

## Adding a spec

1. Pick the right suite file (or create a new `<family>_test.go`).
2. Use `fixture.LoadEnv` + `fixture.SharedREST` + `fixture.DiscoverRunner` +
   `fixture.NewEchoPod` to set up state — they handle cleanup.
3. Call `pod.MCP.CallTool(ctx, "<tool>", args, &out)`.
4. Assert on the decoded JSON, plus DB facts via `client.OpenDB(env.PostgresDSN)`
   when behaviour isn't observable through the API.

## Why not Playwright?

MCP is JSON-RPC, not a UI surface. We'd be using ~10% of Playwright's capability
(its HTTP request fixture) and inheriting its browser/Node setup cost. A 50-line
Go client over the same RPC stays in the repo's main toolchain and can import
backend domain types when DB assertions need them.
