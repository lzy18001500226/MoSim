---
name: Sort and Filter Calc Tables
description: Apply sorts, auto-filters, and range filters to Calc tables and verify the visible filtered rows or ordering on the sheet.
---

# Sort and Filter Calc Tables

## When This Skill Applies

- Use when the task asks to sort, filter, or exclude values from a table.
- Use when the main result is the visible ordering or filtered subset of a worksheet table.

## Preconditions

- The target table is visible or selected.
- The requested sort key or filter values are known.

## Procedure

1. Use when the task asks to sort, filter, or exclude values from a table.
2. These are table-filtering tasks.
3. Check the final visible Calc state and confirm the task-specific result is actually present.

## Visual State Card Usage

- Detailed review cards live in `state_cards.json`.
- Runtime-facing cards live in `runtime_state_cards.json`.
- Load only the state whose screenshot actually matches the live Calc surface.
- Image references in this package:
  - `Images/data_menu_autofilter.png`
  - `Images/data_menu_autofilter_after.png`
  - `Images/data_menu_autofilter_focus_crop.png`
  - `Images/filtered_table_result.png`
  - `Images/filtered_table_result_focus_crop.png`
  - `Images/header_filter_controls_visible.png`
  - `Images/header_filter_controls_visible_after.png`
  - `Images/header_filter_controls_visible_focus_crop.png`

## Common Failure Modes

- Filtering the wrong range or wrong column.
- Assuming the filter was applied without checking the visible table subset.
