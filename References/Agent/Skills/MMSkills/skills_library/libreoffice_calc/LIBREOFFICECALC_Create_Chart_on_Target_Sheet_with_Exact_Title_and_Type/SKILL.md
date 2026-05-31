---
name: Create Chart on Target Sheet with Exact Title and Type
description: Create a chart on the requested destination sheet while honoring an exact chart title and chart family.
---

# Create Chart on Target Sheet with Exact Title and Type

## When This Skill Applies

- Use when the task explicitly names both a target sheet and a required chart title or exact chart type.
- Use when the chart placement and final title are first-class requirements rather than incidental details.

## Preconditions

- The destination worksheet or chart sheet is known.
- The exact chart title text is available from the instruction.

## Procedure

1. Use when the task explicitly names both a target sheet and a required chart title or exact chart type.
2. Chart placement is part of the evaluator-visible result.
3. Check the final visible Calc state and confirm the task-specific result is actually present.

## Visual State Card Usage

- Detailed review cards live in `state_cards.json`.
- Runtime-facing cards live in `runtime_state_cards.json`.
- Load only the state whose screenshot actually matches the live Calc surface.
- Image references in this package:
  - `Images/chart_exact_title_entry.png`
  - `Images/chart_exact_title_entry_focus_crop.png`
  - `Images/chart_subtype_selected_on_target_sheet.png`
  - `Images/chart_subtype_selected_on_target_sheet_after.png`
  - `Images/chart_subtype_selected_on_target_sheet_focus_crop.png`
  - `Images/finished_chart_visible_on_target_sheet.png`
  - `Images/finished_chart_visible_on_target_sheet_focus_crop.png`

## Common Failure Modes

- Creating the chart on the current sheet when the task named another sheet.
- Leaving a placeholder title or wrong chart family in place.
