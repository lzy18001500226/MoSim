# PROJECT KNOWLEDGE BASE

**Generated:** 2026-05-09 18:49:04 IST
**Commit:** c45797b
**Branch:** dev

## OVERVIEW
MCP tooling for Unreal Engine 5.0-5.8 Preview. Server package version `0.5.21`; plugin version `0.1.4`. The repo has two usable surfaces: a TypeScript stdio MCP server that talks to the Unreal plugin over WebSocket, and an optional native plugin MCP HTTP/SSE endpoint at `/mcp`. Both expose the same 22 canonical parent tools with action-based dispatch to Unreal-side handlers.

## STRUCTURE
```
./
|-- src/                         # TypeScript MCP server, NodeNext ESM
|   |-- server/                  # MCP tool/resource registration and dynamic filtering
|   |-- tools/                   # 22 tool schemas, action enums, and TS handlers
|   |-- automation/              # WebSocket bridge client, handshake, request tracking
|   |-- services/                # health and optional Prometheus metrics
|   `-- utils/                   # path safety, command validation, logging, schemas
|-- plugins/McpAutomationBridge/ # Unreal editor plugin
|   `-- Source/McpAutomationBridge/
|       |-- Public/              # settings, subsystem, connection manager API
|       `-- Private/             # WS bridge, native MCP, 57 domain handler files
|-- tests/                       # Vitest unit tests and custom MCP integration runner
|-- scripts/                     # plugin packaging, sync, smoke, cleanup helpers
`-- .github/workflows/           # pinned CI, release, registry, security workflows
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add or change a TS tool contract | `src/tools/consolidated-tool-definitions.ts` | Source of truth for schemas, actions, categories, output schemas |
| Register TS tool behavior | `src/tools/consolidated-tool-handlers.ts`, `src/server/tool-registry.ts` | Register through the MCP registry path only |
| Implement TS action logic | `src/tools/handlers/*-handlers.ts` | Validate/normalize, then call `executeAutomationRequest()` |
| Add Unreal handler behavior | `plugins/.../Private/McpAutomationBridge_*Handlers.cpp` | Register in `UMcpAutomationBridgeSubsystem::InitializeHandlers()` |
| Add native MCP schema/tool metadata | `plugins/.../Private/MCP/` | Self-register with `MCP_REGISTER_TOOL`; keep canonical names only |
| Fix UE save/load crashes | `McpSafeOperations.h`, `McpAutomationBridgeHelpers.h` | Use project safe wrappers and path guards |
| Path and command security | `src/utils/path-security.ts`, `src/utils/command-validator.ts` | Enforce UE roots and console-command block list |
| Integration tests | `tests/test-runner.mjs`, `tests/mcp-tools/` | Pipe-separated expectations; Unreal-dependent unless mocked |
| Version bump | `.github/workflows/bump-version.yml` | Updates server files; plugin `.uplugin` version is separate |

## CONVENTIONS
### Transport Surfaces
1. **TypeScript stdio MCP**: `src/index.ts` creates the SDK server, keeps stdout JSON-only, and connects to Unreal through `src/automation/`.
2. **WebSocket bridge**: Plugin listen sockets default to loopback ports `8090,8091`; TS sends automation requests through the negotiated bridge.
3. **Native MCP**: Optional plugin HTTP/SSE endpoint under `Private/MCP/`; `GET /mcp` opens SSE, `POST /mcp` handles JSON-RPC, `DELETE /mcp` tears down sessions.

### Security Boundaries
- Loopback-only is the default. Non-loopback requires `MCP_AUTOMATION_ALLOW_NON_LOOPBACK=true` in TS or `bAllowNonLoopback` in plugin settings.
- Capability-token auth uses `X-MCP-Capability-Token` for native MCP and `bridge_hello.capabilityToken` for WebSocket when enabled.
- Metrics are separate: non-loopback metrics require both `MCP_METRICS_ALLOW_NON_LOOPBACK=true` and `MCP_METRICS_TOKEN`.
- Paths are limited to `/Game`, `/Engine`, `/Script`, `/Temp`, `/Niagara`, plus sanitized `MCP_ADDITIONAL_PATH_PREFIXES`.

### UE 5.7 Safety
- Do not call `UPackage::SavePackage()` directly. Use `McpSafeAssetSave`, `McpSafeLevelSave`, or `McpSafeLoadMap` wrappers.
- Blueprint component templates must be owned by SCS nodes created through `SCS->CreateNode()` and `SCS->AddNode()`.
- Do not introduce `ANY_PACKAGE`; use modern lookup patterns such as `nullptr` or project helper resolution.

### TypeScript Standards
- Strict NodeNext TypeScript. Do not add `as any`, `@ts-ignore`, or runtime `console.log`.
- Runtime logs must go through `Logger`; `routeStdoutLogsToStderr()` protects JSON-RPC stdout.
- Output schemas are registered at startup and should stay schema-backed.

## ANTI-PATTERNS
- Bypassing registry flow: never call handlers directly instead of `toolRegistry.register()` and `handleConsolidatedToolCall()`.
- Raw WebSocket calls from tools: use `executeAutomationRequest()` and the automation bridge queue.
- Unvalidated external input: command strings go through `CommandValidator`; paths go through normalization/security helpers.
- LAN exposure by accident: do not bind to `0.0.0.0` or non-loopback without explicit opt-in and token planning.
- Generated knowledge bases: do not place AGENTS files in `dist/`, `build/`, `coverage/`, `tests/reports/`, `tmp/`, plugin `Binaries/`, or plugin `Intermediate/`.

## UNIQUE STYLES
- 22 canonical parent tools hide hundreds of actions behind action enums to reduce client context.
- Dynamic tool management exists in both TS and native MCP; `manage_tools` and `inspect` are protected.
- The native plugin has self-describing MCP tool definitions in C++ separate from TS JSON schemas.
- Test expectations use string grammar such as `success|error|timeout`; first token is the primary intent.

## COMMANDS
```bash
npm run build:core     # Compile TypeScript server
npm run type-check     # Type-check without emitting
npm run test:unit      # Vitest unit tests, no Unreal required
npm run test:smoke     # Mock-mode smoke test
npm test               # Unreal-dependent integration entry
npm run test:params    # Parameter-combination audit
npm run automation:sync # Copy/sync plugin into a target project
npm run clean:tmp      # Safe cleanup of repo tmp/ artifacts
```

## NOTES
- Engine reference path: `/data/UnrealEngine/Engine/`.
- Server version sources: `package.json`, `package-lock.json`, `server.json`, `src/index.ts` fallback. Plugin version source: `plugins/McpAutomationBridge/McpAutomationBridge.uplugin`.
- External GitHub Actions are expected to be pinned to full commit SHAs.
- `tests/reports/` and package/plugin build outputs are generated artifacts, not instruction targets.
