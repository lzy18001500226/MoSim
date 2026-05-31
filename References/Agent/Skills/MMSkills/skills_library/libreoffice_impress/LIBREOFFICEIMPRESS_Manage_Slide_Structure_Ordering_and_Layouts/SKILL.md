---
name: Manage Slide Structure, Ordering, and Layouts
description: Select the correct slide, use slide-level controls, and verify navigator or canvas changes before leaving the slide structure workflow.
---

# Manage Slide Structure, Ordering, and Layouts

## When This Skill Applies

- Use this skill for navigator-level work in LibreOffice Impress: restoring the slide pane, selecting slide thumbnails, inserting, deleting, duplicating, reordering slides, or applying a different slide layout.
- Use it when the left filmstrip and the slide shell are the important surfaces for the task and when success depends on slide order, slide count, slide identity, or placeholder layout.
- Do not use it as the main skill just because the instruction names `slide 2` or `page 3`. If the real operation is editing text, moving an object, changing a background, editing notes, or saving/exporting, use the content skill for that operation and treat slide targeting as a short setup step.

## Preconditions

- The left slide navigator is visible, or you can restore it before acting.
- You can identify the intended slide or slide range before making a structural change.

## Entry Checks

1. Start from the slide navigator and identify the target slide thumbnail or slide range.
2. Confirm that the intended thumbnail is selected and that the main canvas matches that selection.
3. For multi-slide work, confirm the exact endpoints of the range before opening any menu or dragging any thumbnail.

## Operation Patterns

1. For reorder tasks, drag the thumbnail only after the correct source thumbnail is selected.
2. For duplicate, delete, insert, or layout tasks, open the thumbnail context menu or the equivalent slide-level command from the selected slide.
3. Keep the operation on the navigator surface until the requested structural action is fully applied.

## Result Verification

1. For reorder, insert, duplicate, or delete, verify the navigator order and slide count before leaving the filmstrip.
2. For layout changes, verify both the selected thumbnail and the main canvas placeholder arrangement.
3. For mixed tasks, finish the slide-level verification first, then hand off to the content-edit skill for text or object work.

## Failure Recovery

- If the canvas does not match the selected thumbnail, stop and reselect the intended slide before acting.
- If the wrong thumbnail was right-clicked or dragged, cancel the menu or undo the drag before doing anything else.
- If a duplication or reorder result is ambiguous, count thumbnails and inspect adjacent slides before moving on.
- If the task only needed slide targeting and not a structural change, exit this skill once the correct slide is confirmed and switch to the content-edit skill.

## Visual State Card Usage

- `state_cards.json` is the full audit version. It records one detailed card per image under `Images/`.
- `runtime_state_cards.json` is the compact runtime version for the Agent branch.
- Load only the image cards whose `when_to_use` and `visible_cues` match the current screenshot. Do not load all cards just because the task sounds related.
- Red boxes are interaction cues. Green boxes are state or result cues. They are not reusable coordinates.
- If a card's `when_not_to_use` matches the current screen, ignore that card and continue with text guidance or another matching card.

## Visual Transfer Limits

- Treat the screenshot theme, sample placeholder text, slide numbers, thumbnail order, and example slide contents as non-transferable.
- The transferable part is the UI relationship: which slide is selected, which slide-level control is open, and what visual state confirms the requested result.
- Menu labels can vary by locale or version. Match the equivalent command, not the literal screenshot wording.
- Use the image cards to recognize state and confirm results, not to copy exact pointer positions or box locations.

## Result Verification Cues

- The selected thumbnail and the main canvas still refer to the same target slide before you act.
- A context menu or other slide-level control is attached to the intended selected thumbnail, not to a neighboring slide.
- After the action, the navigator reflects the requested slide order or slide count when the task changes structure.
- After a layout change, the main canvas reflects the requested placeholder arrangement or slide structure.

## Common Failure Modes

- Acting on the wrong slide because the wrong thumbnail was selected.
- Opening a layout or delete control from the wrong thumbnail.
- Keeping this skill active for a task whose real work is inside the slide after the correct target slide is already known.
- Treating the example slide theme or placeholder text as required output instead of verifying the requested structural outcome.
- Verifying only the canvas for a reorder or delete task and missing that the navigator order or slide count is still wrong.

## Image-Grounded Procedure

### change_slide_structure_or_layout

Use the text procedure first, then load only the matching visual state card:

- `Images/slide_thumbnail_selected.png`: use when the main need is to confirm that the intended slide thumbnail is selected before a structural action.
- `Images/slide_layout_control.png`: use when a thumbnail context menu is open and you need to choose a layout or another slide-level control from that selected slide.
- `Images/slide_structure_result.png`: use when the action is complete and the main canvas should now show the result that needs verification.

For auditing, consult `state_cards.json`. For runtime loading, use `runtime_state_cards.json` and only return the matching card's `state_id`.
