---
name: Find and Replace Text or Formatting
description: Open Writer's Find and Replace dialog, fill the search and replacement fields or replacement formatting, run the replacement, and verify the replace count or changed document state.
---

# Find and Replace Text or Formatting

## When This Skill Applies

- The task explicitly needs repeated literal replacements or formatting replacement through Writer's Find and Replace surface.
- The task depends on the Find and Replace dialog, the replacement-formatting subdialog, or the replace-count confirmation message.
- This is the right skill for repeated-match replacement, not for a one-off direct edit on visible text.

## Preconditions

- The target document is already open.
- The search target, replacement text, or replacement formatting rule is already known.
- If the task later requires saving or exporting, finish the replacement first and then hand off to the save/export skill.

## Do Not Use

- Do not use this skill for simple selection-plus-toolbar edits such as changing one visible word to bold, subscript, or a new font.
- Do not promote this skill to the front of ordinary Writer tasks just because it could theoretically be used.
- If the task is primarily regex or pattern-class driven, prefer the regex specialist instead.

## Procedure

1. Open or confirm the main Find and Replace dialog.
Enter the find term and confirm the scope options only if the task actually needs them.

2. If the task changes formatting instead of literal text, open the replacement-formatting controls and set only the requested attribute.
Do not carry over stale formatting or selection-only options from previous attempts.

3. Run `Replace` or `Replace All` based on the task.
Use `Replace All` only when the whole-document scope is correct.

4. Verify before leaving the flow.
Check the replace-count message and, when formatting matters, also verify the changed document content on the page.
If the count looks wrong or the visible text did not change as intended, stay in the dialog and correct the scope or fields before moving on.

## Visual State Card Usage

- Detailed authoring cards live in `state_cards.json`.
- Runtime-facing cards live in `runtime_state_cards.json`.
- Load only the state whose `when_to_use` matches the current surface.
- Use the success-message card only after a replacement has actually been triggered.

## Common Failure Modes

- Running `Replace All` with the wrong scope because a stale option such as selection-only or match-case was left enabled.
- Trusting the replace-count message alone when the task also requires formatting verification on the document canvas.
- Using Find and Replace as a default selection aid on tasks that should stay on the main document surface.
