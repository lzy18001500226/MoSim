---
name: window-ui-action-control
description: Operate desktop windows through explicitly authorized UI actions. Use when a task needs background UI Automation, window-handle/control messages, safe low-risk clicks, foreground click then minimize, coordinate-click fallback, dry-run action planning, or desktop action stop-condition enforcement.
---

# Window UI Action Control

Use this skill only for action. A task must explicitly authorize UI operation
before loading this skill. If the task only needs screenshots or observation,
use `window-capture-evidence` instead.

## Action Authority Gate

Before any action, record:

```text
skill: window-ui-action-control
local_goal:
authorized_task_scope:
target_app_or_window:
allowed_action_classes:
forbidden_action_classes:
dry_run_first: true | false
rollback_or_state_restore:
stop_triggers:
evidence_path:
```

If these fields cannot be answered from the task, do not act. Return a blocker
or ask the owner for explicit scope.

## Method Priority

1. Prefer the application API, plugin, MCP, CLI, or script interface.
2. Use UI Automation when stable attributes exist: `AutomationId`, `Name`,
   `ControlType`, `InvokePattern`, `SelectionPattern`, or equivalent.
3. Use Win32/window-handle or child-control messages only after confirming the
   target process, title, class, handle, and control identity.
4. Use foreground click only when background methods cannot operate the target
   reliably and the task allows foreground interaction.
5. Use coordinate click only as a last resort after confirming window rectangle,
   DPI scale, target bounds, and no drift.

## Background Action

Background action means using API/UIA/handle-level operation without foreground
focus when possible. It still changes application state, so it must be
authorized. Keep the action narrow and verify the result with readback,
screenshot, log, API state, or a durable artifact.

## Foreground Click Then Minimize

Use foreground click followed by minimize only when all are true:

```text
the task explicitly authorizes foreground UI action
the target window and control are positively identified
background UIA/API/handle action is unavailable or unsafe
the click is low-risk and reversible or state-neutral
the requested final state is minimized or restored
```

Expected sequence:

```text
capture or enumerate target state
  -> bring the exact target window foreground only if needed
  -> perform the smallest authorized click/keystroke
  -> verify the immediate result
  -> minimize or restore state only if requested
  -> record action evidence
```

## High-Risk Controls

Do not click or invoke these controls unless the current task explicitly names
the exact control and expected consequence:

```text
login
authorization
payment
delete
archive
reset
restart
save overwrite
send
approval
pin/unpin
unknown modal button
crash-report submission
credential or token prompt
```

For project workflows that ban these actions outright, the project workflow
wins even if this generic skill describes how to gate them.

MoSim exception: PMO or user-authorized ops may perform bounded official
MWORKS/Sysplorer/Syslab login recovery only when the user has explicitly
authorized that recovery in the MoSim workflow. Use only the approved secure
credential source; never write credentials to docs, logs, packets, screenshot
manifests, emails, or terminal output. Stop without action on MFA/captcha,
account/password error, abnormal authorization, unknown modal/window,
crash/error-report, save/overwrite prompt, or any non-MWORKS credential
surface.

## Coordinate Fallback Checklist

Before a coordinate click:

1. Confirm the active target by process, title, handle, and screenshot.
2. Confirm DPI scale and window rectangle.
3. Confirm the target area has not shifted after any scroll, resize, or refresh.
4. Prefer the center of a stable control, not nearby text or decorations.
5. Take pre-action evidence when practical.
6. Verify post-action state; stop if the first click does not produce the
   expected state.

## Stop Conditions

Stop without acting when:

1. The target window or control is ambiguous.
2. The UI is blank, loading, stale, offscreen, minimized unexpectedly, or shows
   an unknown modal.
3. The action could commit data, spend money, delete/archive, send externally,
   approve, authenticate, save over work, restart an app, or change lifecycle
   state beyond the authorized task.
4. A different project workflow forbids the action.
5. Verification cannot distinguish success from a no-op.

## Do Not

1. Do not convert screenshot permission into click permission.
2. Do not click by coordinates when a stable API/UIA/control route exists.
3. Do not operate a window just to inspect it; use `window-capture-evidence`.
4. Do not hide failed or ambiguous actions. Return evidence and a blocker.
