---
name: window-capture-evidence
description: Capture desktop window screenshots and window-state evidence. Use when a task needs background Win32 PrintWindow capture, foreground or maximized screenshot evidence, minimized-window restore/maximize/capture/minimize handling, blank screenshot triage, or screenshot metadata without performing UI clicks or other window actions.
---

# Window Capture Evidence

Use this skill for observation only. It captures or classifies window evidence;
it does not click buttons, close dialogs, log in, save, restart, send, approve,
pin, archive, or otherwise operate the UI.

## Decision Tree

1. Prefer an application API, MCP, CLI, log, or existing evidence file when it
   can answer the question without GUI observation.
2. Use DPI-aware background capture when the task needs ordinary screenshot
   evidence and the target window is not known to require foreground-only
   validation.
3. Treat minimized windows as a state problem, not a screenshot problem:
   default background capture may record the minimized state but cannot prove
   full client-area content until the window is restored enough to paint.
4. Use foreground or maximized capture only when the workflow says hidden panes,
   modal blockers, activation/license/login state, or full-window layout must
   be visually proven.
5. Use restore/maximize/capture/minimize only when the target is minimized and
   a full-window screenshot is required.
6. If the output is blank, wrong, stale, cropped, ambiguous, or from the wrong
   window, retry once after a short wait or with a safer capture mode; then
   return a blocker instead of overclaiming.

## Capture Modes

### Background Capture

Use background capture for ordinary layout, result-window, phase, or state
evidence when a hidden foreground-only panel is not part of the claim. Do not
maximize, focus, move, or click the target window. If the target is minimized
and the task requires ordinary phase evidence, restore only enough for the
client area to paint, capture, validate size/content, and minimize after.

Background `PrintWindow` is appropriate for windows that are visible but
covered or behind other windows. It is not complete evidence for a minimized
window: Windows often moves minimized windows to an offscreen rectangle and
leaves only non-client/title-bar content paintable. A helper script should mark
that result as not captured or incomplete instead of producing a tiny title-bar
image as evidence.

For MoSim's existing PowerShell helper, the parameter is `-OutDir`:

```powershell
& Scripts\tools\capture_window_background.cmd -TitleRegex "<title-regex>" -ProcessRegex "<process-regex>" -OutDir Results\window_capture\manual
```

For MoSim live simulation phase evidence, prefer:

```powershell
& Scripts\tools\capture_window_background.cmd -TitleRegex "<title-regex>" -ProcessRegex "<process-regex>" -OutDir Results\mworks_background_capture\<request_id> -RestoreMinimized -MinimizeAfter
```

Do not add `-Maximize` for ordinary phase evidence. Use `-Maximize` only when
the owning workflow requires activation/login/license/authorization evidence or
full-window graphical review.

### Foreground Or Maximized Capture

Use foreground or maximized capture only when required by the owning workflow or
task packet. Record why background capture is insufficient. Do not click inside
the window as part of this skill.

### Restore, Maximize, Capture, Minimize

Use this only as an exception for a minimized target that needs full-window
evidence. The expected sequence is:

```text
confirm target window identity
  -> restore if minimized
  -> maximize if full-window evidence is required
  -> wait briefly for paint
  -> capture screenshot
  -> minimize after capture only if the task explicitly requests restoring the prior minimized state
  -> record final state and evidence path
```

For MoSim's existing helper:

```powershell
& Scripts\tools\capture_window_background.cmd -TitleRegex "<title-regex>" -ProcessRegex "<process-regex>" -OutDir Results\window_capture\manual -RestoreMinimized -Maximize -MaximizeWaitMs 500 -MinimizeAfter
```

For ordinary MoSim simulation phase evidence, do not maximize by default:

```powershell
& Scripts\tools\capture_window_background.cmd -TitleRegex "<title-regex>" -ProcessRegex "<process-regex>" -OutDir Results\window_capture\manual -RestoreMinimized -MinimizeAfter
```

Use `-Maximize` only for activation/login/license/authorization evidence or an
explicit full-window wiring/layout review.

## Evidence Record

Every capture result should record:

```text
skill: window-capture-evidence
capture_mode: background | foreground | maximized | restore_maximize_capture_minimize
target_selection: title/process/handle criteria used
evidence_path:
timestamp:
window_title:
process_name:
hwnd_or_native_id_if_available:
window_state_before:
window_state_after:
blank_or_ambiguous: true | false
width:
height:
dpi_awareness:
cropped_or_incomplete: true | false
limitations:
```

For formal MoSim simulation evidence, also index or copy screenshots into:

```text
Results/<group>/<scene>/<experiment>/screenshots/
Results/<group>/<scene>/<experiment>/logs/screenshot_manifest.json
```

## Stop Conditions

Stop and return a blocker or issue note when:

1. Multiple matching windows cannot be distinguished.
2. The screenshot is blank, wrong, or ambiguous after one bounded retry.
3. The target window is minimized and the task does not authorize restore or
   full-window capture.
4. The window is a login, license, authorization, crash, save, restart, send,
   approval, deletion, archive, or unknown dialog and the task lacks explicit
   authority for that review mode.
5. The requested operation would require a click or UI action. Switch to
   `window-ui-action-control` only if the task explicitly authorizes action.
6. The task asks to infer product acceptance or runtime success from screenshot
   evidence alone.

## Do Not

1. Do not perform clicks, keystrokes, menu selections, close/minimize actions
   except the explicitly requested `-MinimizeAfter` restoration case.
2. Do not treat the ability to capture as permission to operate the UI.
3. Do not use background screenshots as proof of hidden activation, license,
   login, or authorization state when foreground evidence is required.
4. Do not silently switch from observation to action.
