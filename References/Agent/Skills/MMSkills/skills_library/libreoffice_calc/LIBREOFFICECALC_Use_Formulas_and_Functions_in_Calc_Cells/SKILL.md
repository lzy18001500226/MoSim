---
name: Use Formulas and Functions in Calc Cells
description: Enter direct Calc formulas or wizard-selected functions in the correct target cell, verify the first result, and only then fill the intended range.
---

# Use Formulas and Functions in Calc Cells

## When This Skill Applies

- Use when the task is primarily a direct worksheet formula or named function task: totals, averages, date arithmetic, rounding, scaling, concatenation, or similar cell-level calculations.
- Use when success is judged by visible worksheet values in a target cell or repeated range.
- Keep this as the default formula path unless the task is explicitly a keyed lookup/cross-sheet retrieval or a business-metric specialist flow such as revenue, profit, or discount columns.

## When Not To Use

- Do not use as the main planner for explicit VLOOKUP-style, keyed-reference, or source-sheet lookup tasks. Use `LIBREOFFICECALC_Lookup_Reference_and_Keyed_Fill_Formulas`.
- Do not use as the main planner for revenue/profit/cost/discount output columns when the business-metric relation is the main difficulty. Use `LIBREOFFICECALC_Apply_Revenue_Cost_Discount_Profit_Formulas`.
- Do not drift into chart, page-setup, cleaning, or formatting-only branches just because the task includes a later save or visual polish step.

## Core Procedure

1. Anchor the correct destination cell or first output cell before typing anything.
2. Enter the first formula directly in the cell or formula bar, or use Function Wizard only when a named function is genuinely easier.
3. Verify the first computed result on the sheet:
   - the active cell is in the requested row or column,
   - the visible header or output label matches the prompt,
   - the displayed result is plausible for the current row.
4. Fill or copy the formula only through the requested range.
5. Re-check the destination range instead of stopping at formula entry.

## Verification Focus

- Confirm the result landed in the requested target column or target row, not an adjacent helper region.
- For date tasks, verify that the result displays as a date rather than an unexpected serial number.
- For fill-down or fill-across tasks, verify one later cell too so the relative references did not drift.

## Failure Recovery

- If the first result looks wrong, stop before filling the rest of the range.
- If the active cell is wrong, reselect the correct destination cell and re-enter the formula instead of editing random cells.
- If the formula actually depends on another sheet or keyed matching, switch to the lookup skill rather than forcing a generic formula pattern.

## Visual State Card Usage

- Runtime cards live in `runtime_state_cards.json`.
- Audit cards live in `state_cards.json`.
- Match only the card that fits the current live Calc surface.

Image references in this package:

- `Images/direct_formula_entry_target_cell.png`
- `Images/direct_formula_entry_target_cell_focus_crop.png`
- `Images/function_result_visible_in_target_cell.png`
- `Images/function_result_visible_in_target_cell_focus_crop.png`
- `Images/function_wizard_named_function_selection.png`
- `Images/function_wizard_named_function_selection_focus_crop.png`
- `Images/function_wizard_named_function_selection_after.png`
