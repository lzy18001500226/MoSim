# Screenshot Route Plan

## Ordinary Package/Layout Review

Use the project DPI-aware background capture route for ordinary package-browser, diagram, layout, wiring, result-window, or animation review after the approved live route is proven:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts\tools\capture_window_background.ps1 -TitleRegex 'Sysplorer|MWORKS|Quadrotor|AWFF' -OutDir Results\mworks_background_capture\<task_id> -RestoreMinimized -Maximize
```

Expected evidence:

- `capture_manifest.json` with `dpi_awareness`.
- Full-window PNG for the real main Sysplorer/MWORKS target window.
- Written observation naming the target class, window title, and reviewed package/diagram phase.

## Activation/Login/License Acceptance

Do not use background capture alone to prove activation/login/license/authorization readiness. Those claims require foreground or maximized target-main-window visual evidence handled by PMO/CoAgentOps, because `PrintWindow` can miss Qt/CEF child surfaces or hidden login panes.

## Helper Window Boundary

Helper/proxy windows may be listed in manifests, but they are not package-browser/layout acceptance evidence unless a future task explicitly asks for helper diagnostics. If a helper/proxy window obstructs the main target, stop and write a blocker rather than clicking or closing windows from R2.

## 022 Boundary

No screenshot was taken in 022. The current task is static readiness/blocker only.
