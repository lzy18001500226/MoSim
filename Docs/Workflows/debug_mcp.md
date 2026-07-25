# MCP Troubleshooting

> Use this workflow only when a configured MCP server does not start, exposes
> no tools, or cannot reach its declared local bridge. It is not a simulator,
> controller, login, or runtime-acceptance workflow.

## 1. Scope And Success Boundary

Start with the active Codex surface:

```text
Codex desktop or Windows-native route
  -> inspect the Windows-native MCP configuration and Windows wrappers

Intentional WSL route
  -> inspect the Linux-side configuration and Linux wrappers
```

Do not combine Windows paths, `wsl.exe`, `/mnt/c`, or Linux wrapper paths in
one configuration route. A listed MCP server only proves that its stdio
process is configured. A live MWORKS, Unreal, Blender, ROS, or Gazebo action
needs the separate evidence gate owned by its topic workflow.

Pass conditions are deliberately narrow:

1. the active Codex surface lists the expected MCP server and tools; and
2. when a server uses a local application bridge, one read-only bridge probe
   succeeds.

`Auth: Unsupported` is normal for many local MCP servers. `Tools: (none)`, a
startup error, or a bridge connection failure is a troubleshooting result, not
a controller or simulator failure.

## 2. Bounded Procedure

1. Record whether the active task is running in Windows-native Codex or an
   intentionally WSL-backed environment. Do not guess from an old command.
2. Inspect the configured servers with:

   ```text
   codex mcp list
   ```

3. Identify the single failing server and its declared wrapper/configuration
   source. Use `Docs/Index/api_index.md` to locate the project-owned tool and
   skill; do not create a second wrapper or duplicate configuration.
4. Check the wrapper with its documented harmless `--help`, `dump-tools`, or
   equivalent listing action. Keep secrets, account caches, browser profiles,
   and raw launcher logs out of project evidence.
5. If the server fronts a local application, perform one read-only connection
   probe through its owning skill. A successful stdio wrapper cannot stand in
   for an editor, simulator, or MWORKS connection.
6. Record the command, active host route, exact error, and next owner under the
   task's normal `Results/` evidence path. Do not append an attempt diary here.

Use a 60-second bound for an interactive startup or bridge probe unless the
owning workflow specifies a shorter bound. Stop the attempt after a timeout;
do not turn a missing bridge into an unbounded wait loop.

## 3. Route To The Owning Workflow

| Failure surface | Owner after the MCP check |
|---|---|
| MWORKS/Sysplorer/Syslab model access | `Docs/Skills/Mworks/mworks-mcp-operations/SKILL.md` and the relevant MWORKS workflow |
| MWORKS license, activation, login, unknown GUI state | `AGENTS.md` blocker rule; do not continue model work |
| Windows capture or explicitly authorized desktop action | `Docs/Skills/Desktop/` |
| Unreal editor or scene bridge | `Docs/Workflows/unreal_renderer.md` and the Unreal skill |
| ROS1/Sunray/Gazebo/PX4 runtime | `Docs/Workflows/sunray_ros1_current_runtime_lane.md` |
| Project tool/capability ownership | `Docs/Index/api_index.md`, `Docs/Index/capability_index.md` |

Do not alter external Codex configuration, WSL defaults, application account
state, license state, or a global installation merely because a project-side
wrapper failed. First confirm the active configuration source; obtain the
required authorization before an infrastructure change outside this repository.

## 4. Evidence And Escalation

A useful troubleshooting result contains:

```text
active host route
server name and wrapper/config source
one sanitized startup or read-only probe result
whether the failure is stdio, configuration, local bridge, license/UI, or runtime
next owning workflow or exact blocker
```

For a repeatable failure, promote only the concise cause and recovery step to
the owning workflow or skill. Historical Windows/WSL migration incidents,
retired notification material, and legacy wrapper examples are preserved at:

```text
Docs/Cache/workflow_history/debug_mcp_20260726_pre_cleanup.md
```
