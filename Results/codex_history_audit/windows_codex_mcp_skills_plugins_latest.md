# Windows Codex MCP Skills Plugins Status
Generated: 2026-06-05T19:39:13.063248

## Codex Home
- Active home: `C:\Users\HP\.codex`
- Operating model: Windows is the only active Codex environment; WSL is runtime only through `wsl.exe -d Ubuntu-22.04 -- ...`.

## MCP
- Enabled MCP servers: 8
- Servers: sysplorer, syslab, git, filesystem, windows-mcp, ros-mcp, mosim-unreal, mosim-epic
- Initialize probe: all 8 enabled MCP servers returned initialize results.
- Removed default `blender` MCP because it requires a running Blender addon/socket and did not complete initialize during startup. Keep it as on-demand, not startup default.

## Skills
- Total `SKILL.md` files under Windows `.codex/skills`: 51
- System skills under `.system`: 5
- Non-system skills: 46

## Plugins
- Marketplace plugins: none configured.
- Removed stale `[marketplaces.local]` and `[plugins."codex-session-tools@local"]` entries because no supported Windows marketplace manifest existed; `codex plugin list` now reports no marketplace plugins instead of failing.

## Verification Commands
- `codex doctor --summary --ascii --no-color`: 0 fail, config/auth/MCP/state ok.
- `codex mcp list`: 8 enabled MCP servers.
- `codex plugin list`: no marketplace plugins found, no error.
