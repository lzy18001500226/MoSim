# Pi integration notes

This repo can be installed as a Pi package and also includes a project-local Pi extension at `.pi/extensions/windows-mcp/` for local checkout development.

## What the Pi package does

Pi does not include built-in MCP support. The Pi package in this repo starts the existing `windows-mcp` server over stdio and exposes Pi-native tools that forward to the existing MCP tools.

This integration intentionally keeps Windows-MCP server internals unchanged. It does not add new MCP server tools or alter the desktop/UIA modules.

## Pi tools exposed

- `win_snapshot` -> `Snapshot`
- `win_screenshot` -> `Screenshot`
- `win_app` -> `App`
- `win_click` -> `Click`
- `win_type` -> `Type`
- `win_move` -> `Move`
- `win_scroll` -> `Scroll`
- `win_shortcut` -> `Shortcut`
- `win_wait` -> `Wait`

## Enable in Pi

One-line global setup:

```powershell
pi install git:github.com/CursorTouch/Windows-MCP
```

Try without installing:

```powershell
pi -e git:github.com/CursorTouch/Windows-MCP
```

Local checkout setup:

```powershell
git clone https://github.com/CursorTouch/Windows-MCP.git
cd Windows-MCP
uv sync
npm install
pi
```

Pi auto-discovers project extensions under `.pi/extensions/*/index.ts` when run from a local checkout. If Pi is already running, use `/reload`.

If you manually copy the extension somewhere else, set:

```powershell
$env:WINDOWS_MCP_ROOT = "C:\path\to\Windows-MCP"
```

## Recommended agent pattern

- Use `win_snapshot` before operating a visible app.
- Prefer element labels/ids returned by `win_snapshot` with `win_click`, `win_type`, `win_move`, and `win_scroll`.
- Use coordinates when labels/ids are unavailable or ambiguous.
- Use `win_shortcut` for keyboard workflows such as `ctrl+l`, `ctrl+c`, `alt+tab`, or `win+r`.
- Use `win_screenshot` for fast visual inspection when UI element extraction is not needed.
- Use `use_dom=true` with `win_snapshot` for browser page content instead of browser UI.
