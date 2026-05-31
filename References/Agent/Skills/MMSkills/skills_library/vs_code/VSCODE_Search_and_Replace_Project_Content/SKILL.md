---
name: Search and Replace Project Content
description: Search for the requested text through VS Code's search UI or find widget, then replace only the intended value and verify the post-replacement state rather than stopping at an open search panel. Use this when the search surface itself matters: search panel, results tree, find widget, and replace verification. Do not collapse these flows into generic editor editing.
---

# Search and Replace Project Content

Search for the requested text through VS Code's search UI or find widget, then replace only the intended value and verify the post-replacement state rather than stopping at an open search panel. Use this when the search surface itself matters: search panel, results tree, find widget, and replace verification. Do not collapse these flows into generic editor editing.

## When This Skill Applies
- The task is fundamentally about locating text before editing it.
- The user asks for a find-and-replace operation or for project search results to be inspected.

## Visual State Card Usage
- `runtime_state_cards.json` is the compact runtime set for agent execution.
- `state_cards.json` is the audit version with fuller transfer limits, bundle reasoning, and evidence lineage.
- Red boxes mark interaction targets. Green boxes mark state or verification cues.
- Boxes are never reusable coordinates; match by UI structure, labels, and nearby context.

## Procedure
1. Inspect workspace search results before editing.
   Use this branch when The task depends on project-wide matches or search navigation.
   Key states: `search_panel_ready`, `search_results_tree_visible`. Verify the persistent result before stopping.
2. Replace the requested value and verify the final editor state.
   Use this branch when The task is a direct find-and-replace operation.
   Key states: `find_widget_populated`, `matched_value_ready_for_overwrite`, `replacement_saved_in_editor`. Verify the persistent result before stopping.

## Common Failure Modes
- Stopping after opening the search panel without confirming the correct matches.
- Failing to verify the final edited state after the replace action.
- Stopping after opening the Search view without verifying a changed value in the editor or results tree.

## Transfer Limits
- Do not copy example coordinates, filenames, workspace names, extension names, or text literals unless the live task explicitly asks for them.
- Treat the images as state-recognition aids only. Adjust to the live VS Code labels and currently visible controls.
