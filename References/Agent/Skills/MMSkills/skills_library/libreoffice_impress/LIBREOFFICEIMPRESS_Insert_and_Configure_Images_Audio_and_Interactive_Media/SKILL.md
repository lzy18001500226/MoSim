---
name: Insert and Configure Images, Audio, and Interactive Media
description: Insert a media object on the intended slide, optionally configure click behavior, and verify the requested result before leaving the slide.
---

# Insert and Configure Images, Audio, and Interactive Media

## When This Skill Applies

Use this skill when the task asks you to place an image, audio object, video object, or click-triggered media interaction onto a slide in LibreOffice Impress.

Use it when:
- the target slide is already known or can be identified in the slide pane
- the task needs a real media object, not a drawn shape or text-only edit
- the workflow may include selecting a file, placing the object, or opening the Interaction dialog

Do not use it as the main skill when the task is only about resizing, aligning, or restyling an already correct media object.

## Preconditions

- LibreOffice Impress is open on the target presentation.
- The correct slide can be selected in the left thumbnail pane.
- If the task names a source file, that file is accessible from the local file chooser.

## Visual State Card Usage

- `state_cards.json` is the full audit record for the packaged screenshots.
- `runtime_state_cards.json` is the compact version intended for Agent or OSWorld runtime loading.
- Load only the image card that matches the current screenshot state. Do not preload all cards just because the task mentions media.
- Treat red boxes as interaction cues and green boxes as state or verification cues. They identify what matters on screen, not reusable coordinates.

Current image cards:
- `Images/media_insert_surface.png`: selected slide plus empty content placeholder ready to start image insertion
- `Images/media_result_state.png`: system `Insert Image` chooser after starting insertion; despite the filename, this is not a finished on-slide result
- `Images/media_interaction_controls.png`: open `Interaction` dialog for configuring click behavior on an already selected media object

## Visual Transfer Limits

- Do not copy sample slide text, theme styling, slide numbers, filenames, object sizes, or positions unless the current task explicitly requires them.
- Do not assume the chooser folder, file ordering, or desktop theme will match the example.
- Do not treat boxed regions as exact click locations. Re-find the corresponding control in the current screenshot.
- The packaged screenshots show image insertion and click-action configuration states; final media appearance still has to be verified against the current task.

## Procedure

1. Select the intended slide in the left thumbnail pane.
2. If the slide has an empty content placeholder and the task is to insert an image, use the placeholder insert control or the normal insert path to open the chooser.
3. If the system chooser opens, use the state represented by `Images/media_result_state.png` only for selecting the requested image file and confirming with `Open`.
4. If the task requires click behavior, first ensure the media object exists and is selected, then open the `Interaction` dialog and set the requested action.
5. After placement or configuration, return focus to the slide and verify the actual task result on the current slide before finishing.

## Result Verification Cues

- The intended slide remains selected after the workflow.
- The requested media object is visible on the slide, or remains selected if you are still configuring it.
- If click behavior was requested, the Interaction dialog shows the chosen action before you confirm it, or the object behaves as requested after configuration.
- Do not mark the task complete from the chooser dialog alone.

## Common Failure Modes

- Starting from the wrong slide thumbnail, then inserting media onto the wrong slide.
- Treating the chooser checkpoint as a finished result.
- Opening the Interaction dialog before selecting the media object.
- Copying example-only values such as a sample filename, object size, or on-screen position when the current task does not ask for them.
