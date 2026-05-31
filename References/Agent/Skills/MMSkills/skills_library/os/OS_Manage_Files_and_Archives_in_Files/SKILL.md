---
name: Manage Files and Archives in Files
description: Use Ubuntu Files or the desktop file surface to open the right location, manipulate visible items, and verify the requested file result.
---

# Manage Files and Archives in Files

## When This Skill Is Applicable

Use this skill for GUI file-management tasks in Ubuntu Files, Trash, or a desktop/Home surface when the task requires one or more of the following:

- opening Files and navigating to the correct folder, Home view, or Trash
- creating, moving, copying, restoring, compressing, or deleting visible files or folders in Files
- emptying Trash or checking whether files are present or absent after a GUI file action
- verifying that the requested destination surface now shows the correct file, folder, archive, or empty state

Do not use this skill for shell-only file operations, terminal search workflows, or tasks whose main action happens outside Ubuntu file-management surfaces.

## Preconditions

- The task names a source or destination surface clearly enough to navigate there.
- The needed file or folder can be identified from the live task, not from example image content.

## Visual State Card Usage

- `runtime_state_cards.json` is the compact set for the Agent branch. Load only the cards whose screenshots plausibly match the current screen.
- `state_cards.json` is the audit-detail version with fuller transfer limits and evidence notes.
- Red boxes are interaction cues. They show the kind of control to use in that screenshot, not a reusable click coordinate.
- Green boxes are verification or state cues. They mark what kind of result signal matters in the image, not a required object location.
- If no image card matches the current screen, continue from the text procedure instead of forcing an image match.

## Visual Transfer Limits

- Do not copy example filenames, folder names, archive names, desktop arrangements, dock order, wallpaper, or item positions from the screenshots.
- Treat image text and icons as example content unless the live task explicitly asks for the same value.
- Transfer only the reusable UI relationship: launcher state, Files sidebar/path state, selected-item readiness, and destination-surface verification.
- Some cards verify from the desktop or Home-like surface rather than from an open Files window. Verify on the live destination surface, not on the example surface.

## Result Verification Cues

- The correct destination surface is open and stable before you judge success.
- The requested file or folder is present, absent, restored, archived, or emptied exactly as the live task requires.
- If the action was a move, copy, restore, or compression step, verify the result in the destination surface instead of relying on the action itself.
- If the result should be visible in Files, Trash, or on the desktop, verify there directly rather than trusting a prior selection state.

## Common Failure Modes

- Opening Files but never reaching the requested folder, Home surface, or Trash before acting.
- Acting on the wrong selected item because the example filenames were treated as instructions.
- Verifying success from the wrong surface, such as checking the desktop when the task expects a Files folder view, or the reverse.
- Treating an annotation box as a coordinate recipe instead of using the live UI structure.

## Atomic Capabilities

- **open_target_files_surface**: Open or foreground Ubuntu Files, then navigate to the requested folder, Home surface, or Trash.
- **apply_gui_file_action**: Apply the needed Files GUI action to the correct selected item or visible control.
- **verify_gui_path_result**: Confirm that the requested result is visible on the correct destination surface.

## Procedures

### Apply The Files Workflow

#### 1. Open The Target Files Surface

Use when the correct Files surface is not yet open.

- Open Ubuntu Files from the dock or switch to it if it is already running.
- Navigate to the requested folder, Home surface, or Trash.
- Image reference: `Images/os_manage_files_and_archives_in_files_open_target_files_surface.png`

#### 2. Apply The GUI File Action

Use when the right Files surface is open and the relevant item is ready.

- Select the correct file or folder for the live task.
- Use the appropriate Files control, toolbar action, context menu, or drag-and-drop interaction.
- Image reference: `Images/os_manage_files_and_archives_in_files_apply_gui_file_action.png`

#### 3. Verify The GUI Path Result

Use when the action is complete and the result must be confirmed on the destination surface.

- Check the final Files folder, Trash, or desktop/Home surface that should now reflect the requested change.
- Confirm the live task's requested presence, absence, restore, move, copy, or archive result.
- Image reference: `Images/os_manage_files_and_archives_in_files_verify_gui_path_result.png`

Only load the matching runtime image card for the screen you are actually on. Use `runtime_state_cards.json` for branch-time loading and `state_cards.json` for audit review.
