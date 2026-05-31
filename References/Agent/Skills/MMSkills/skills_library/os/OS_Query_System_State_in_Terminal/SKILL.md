---
name: Query System State in Terminal
description: Inspect Ubuntu system state from Terminal, run the exact query command the task asks for, and verify the requested result from visible shell output.
---

# Query System State in Terminal

## When This Skill Applies

Use this skill when the task asks for Ubuntu system facts that are best retrieved in Terminal and the success condition depends on visible shell output. Typical targets include the active shell, installed shells, release details, package or Python environment state, resource usage, device status, module status, or a file or path check that must be confirmed on screen.

This is a text-first skill. The command itself depends on the current task, so the reusable part is the workflow: get into Terminal, run the exact query command, and verify the exact output that answers the request.

## Preconditions

- Terminal is already open, or it can be opened directly from the desktop or dock.
- The task names a concrete thing to query or verify.
- You can read the resulting terminal output on screen before finishing.

## Core Workflow

1. Get to Terminal and make sure it is the active window.
2. Confirm the working context only if the query depends on a directory, environment, account, or target path.
3. Type and run the exact command needed for the requested system state.
4. Read the output and match it against the requested fact before marking the task complete.

## Visual State Card Usage

- Audit-ready image cards live in `state_cards.json`.
- Compact runtime cards for the Agent branch live in `runtime_state_cards.json`.
- Load only cards whose `when_to_use` conditions match the current screenshot. Do not load the whole image set by default.
- Treat red boxes as interaction cues and green boxes as state or verification cues. They are never reusable coordinates.
- If no image card matches the current screen, continue with the text procedure instead of forcing a visual match.

The current package contains one usable desktop-launcher cue and two non-terminal screenshots that should be treated as rejection cues. Runtime should therefore load only matching cards:

- `Images/os_query_system_state_in_terminal_prepare_terminal_context.png` is relevant only when the Ubuntu desktop is visible and Terminal still needs to be opened or focused.
- `Images/os_query_system_state_in_terminal_run_requested_command.png` should be loaded only if the current screen matches that Settings page and you need to reject it as a terminal command-entry state.
- `Images/os_query_system_state_in_terminal_verify_terminal_result.png` should be loaded only if the current screen matches that Settings page and you need to reject it as a terminal verification state.

## Procedure Notes

### Prepare Terminal Context

Use this step when Terminal is not yet active. If the desktop is visible, open or focus Terminal from the dock. If Terminal is already open, skip directly to the command step.

Image reference:
- `Images/os_query_system_state_in_terminal_prepare_terminal_context.png`

### Run the Requested Command

Enter the exact command needed for the requested query. Do not replace it with a nearby guess. If the command depends on a path, package name, username, process name, or shell name, verify that the argument matches the task before pressing Enter.

Image reference:
- `Images/os_query_system_state_in_terminal_run_requested_command.png` only as a negative-match card; it is not a reusable command-entry screenshot.

### Verify the Terminal Result

Do not finish just because the command ran. Finish only when the requested fact is visibly present in Terminal output. The verification target may be a shell name, a list entry, a version string, a status line, a package record, a path, or another explicit value named in the task.

Image reference:
- `Images/os_query_system_state_in_terminal_verify_terminal_result.png` only as a negative-match card; it is not a reusable terminal-result screenshot.

## Visual Transfer Limits

- Do not copy literal example values, filenames, usernames, wallpaper details, clock values, or widget positions from the stored screenshots.
- Do not reuse bounding-box locations as click coordinates.
- Do not infer terminal success from screenshots that are actually showing a different application.
- For this skill, the strongest transferable visual rule is simple: a real terminal workflow must show Terminal, an input prompt, or terminal output. Screens from Settings are explicit non-matches.

## Result Verification Cues

Use these cues before finishing:

- Terminal is the active window.
- The command has completed and printed visible output.
- The output includes the exact fact the task asked you to confirm.
- The value is read from the current terminal output, not inferred from a command name alone.

If the task expects a negative result, verify that the failure or absence message is visible in Terminal before finishing.

## Common Failure Modes

- Running a plausible command in the wrong directory or against the wrong target.
- Reading only the command text and not the output.
- Accepting an unrelated app window as evidence that the terminal workflow is complete.
- Finishing on partial output when the requested line or value is not yet visible.
