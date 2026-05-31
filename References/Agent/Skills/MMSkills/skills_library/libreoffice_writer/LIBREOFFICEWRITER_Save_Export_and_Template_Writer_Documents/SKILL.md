---
name: Save, Export, and Template Writer Documents
description: Use Writer's output surfaces to save a copy, confirm an export target such as PDF, or store the current document as a reusable template.
---

# Save, Export, and Template Writer Documents

## When This Skill Applies

- The document edits are already complete and the remaining work is to send the document through the correct output surface.
- The task explicitly asks to save a copy, export to another format such as PDF, or save the current document as a reusable template.
- The current screenshot already shows either the File menu route, a save/export file chooser, or the dedicated template dialog.

## Preconditions

- Writer is open on the target document.
- The requested filename, format, or template name is known from the task.
- Content editing should be finished before entering this flow.

## Do Not Use

- Do not use this skill for paragraph, character, table, or reference edits inside the document body.
- Do not treat `Save`, `Save a Copy...`, PDF export, and `Save As Template` as interchangeable. Pick the exact route the task asks for.

## Procedure

1. Choose the exact route first.
If the task must keep the original file untouched, use `Save a Copy...`.
If the task must produce another format, stay in the export/save chooser until the requested format is visibly selected.
If the task is about templates, use the dedicated template modal rather than a generic file save.

2. Verify the route before committing.
For PDF tasks, verify both the filename and that the file type is visibly set to PDF.
For template tasks, verify that the dialog title is `Save As Template` and the template-name field is filled.
For copy-save tasks, verify that Writer opened a new output dialog instead of silently overwriting the current file.

3. Commit only after the surface matches the task.
Do not click the final save button while the dialog still shows the wrong format, the wrong filename, or the wrong output mode.

## Visual State Card Usage

- Detailed authoring cards live in `state_cards.json`.
- Runtime-facing cards live in `runtime_state_cards.json`.
- Load only the state whose `when_to_use` matches the current surface. Do not preload all save/export images just because the task mentions output.
- Use the cards as recognition aids, not coordinate templates.

## Common Failure Modes

- Using `Save` when the task required `Save a Copy...`, which can overwrite the source file.
- Clicking `Save` in the chooser before checking that the file-type control matches the requested format.
- Treating a generic file chooser as proof that the template flow is correct.
- Reusing example filenames or paths from the image cards instead of the task's requested value.
