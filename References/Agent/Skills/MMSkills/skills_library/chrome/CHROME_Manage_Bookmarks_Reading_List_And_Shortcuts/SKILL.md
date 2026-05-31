---
name: Manage Bookmarks Reading List And Shortcuts
description: Save the current Chrome page, choose or create a destination, and verify the saved result. Use the image cards only when the current UI genuinely matches the bookmark states they show.
---

# Manage Bookmarks Reading List And Shortcuts

## When This Skill Is Applicable

Use this skill when Chrome needs to save the current page into bookmarks, the reading list, or a similar saved-entry surface, and the task also cares about choosing a destination or confirming the saved result.

The image set in this package is bookmark-specific. Use the screenshots only when the live UI matches the bookmark star, the compact "Bookmark added" popover, the full "Edit bookmark" dialog, or the final filled-star verification state. If the task is using a reading-list or shortcut surface that looks different, stay text-first and verify on the live UI instead of forcing a card match.

## Text-First Procedure

1. Confirm the active tab is the page that should be saved.
2. Open Chrome's save surface. For bookmark flows this is usually the toolbar star at the right side of the address bar.
3. If a compact save popover appears, keep the current page title unless the task asks for a rename, then choose the requested folder if it is already listed.
4. If the requested destination is missing or a new folder is required, open the fuller chooser, create or select the needed folder, and save.
5. Verify the result on the active page before finishing. A filled bookmark star is enough for a plain bookmark save, but folder-specific tasks need a second check that the chosen destination is correct.
6. For reading-list or shortcut-style saves, use the equivalent Chrome save surface and verify the requested entry on that surface. Do not rely on bookmark-specific visuals when the UI differs.

## Visual State Card Usage

- `state_cards.json` is the full audited image-card set.
- `runtime_state_cards.json` is the compact version for Agent branch loading.
- Runtime should load only the card or cards whose screenshot state matches the current Chrome surface. Do not preload the whole set when only one state is relevant.

Current image cards:

- `Images/bookmark_save_control.png`: normal page state with the toolbar bookmark star available.
- `Images/edit_bookmark_dialog.png`: compact "Bookmark added" popover with the Folder dropdown open.
- `Images/bookmark_folder_creation.png`: full "Edit bookmark" dialog with the folder tree and new-folder area.
- `Images/bookmark_result_state.png`: post-save verification state with the bookmark star active.

## Visual Transfer Limits

- Red boxes are interaction cues. They show the kind of control to use, not reusable coordinates.
- Green boxes are verification cues. They mark state evidence, not click targets.
- Page content, URLs, folder names, typed queries, suggestion rows, crop boundaries, and window geometry in the screenshots are source-example details and must not be copied into a new task.
- If the live UI is a reading-list panel, bookmark manager page, or shortcut editor that does not match one of these screenshots, follow the text procedure and verify against the live surface.

## Result Verification Cues

- Bookmark flow: the current page shows an active or filled bookmark star after saving.
- Folder-sensitive flow: the chosen destination is also visible in the save UI or in the bookmark manager.
- Reading-list or shortcut flow: the requested item appears on the relevant saved-entry surface; a bookmark star alone is not enough.

## Common Failure Modes

- Opening the save UI on the wrong tab.
- Accepting the default folder when the task asked for a specific or newly created destination.
- Stopping after the compact popover opens without confirming save.
- Treating the filled star as proof of folder placement when the task required destination verification.
