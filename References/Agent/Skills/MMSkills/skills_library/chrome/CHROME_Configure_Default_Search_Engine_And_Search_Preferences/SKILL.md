---
name: Configure Default Search Engine And Search Preferences
description: Use Chrome search-engine settings and Google Search Settings surfaces to change providers or inspect search-display preferences without inventing controls that are not visible.
---

# Configure Default Search Engine And Search Preferences

## When This Skill Is Applicable

Use this skill when a Chrome task asks you to:

- change the default search engine
- inspect, edit, or remove search-engine or site-search entries
- verify a downstream search-results preference or a Google Search settings control

This is a text-first OSWorld skill. Follow the procedure as the primary workflow. Use visuals only when the live screenshot clearly matches one of the image cards.

## Preconditions

- Chrome can open Settings.
- The Search engine section is reachable from the Settings sidebar.
- The requested provider or downstream search preference is available in the current environment.

## Visual State Card Usage

Audit-grade image cards live in `state_cards.json`. Compact runtime cards for the Agent branch live in `runtime_state_cards.json`.

Load only the card whose `when_to_use` and visible cues match the live screenshot:

- `Images/search_engine_settings_surface.png`: entry cue for selecting **Search engine** from the left Settings sidebar.
- `Images/search_engine_selection_dialog.png`: operation cue for confirming a selected provider in the Search engine modal.
- `Images/manage_search_engines_page.png`: operation cue for opening **Manage search engines and site search** from the Search engine page.
- `Images/search_preference_filter_applied.png`: verification cue for a downstream results-page filter.
- `Images/google_search_more_settings_menu.png`: entry cue for the Google results-page Search Settings menu when the task is about Google Search display preferences.
- `Images/google_search_other_settings_surface.png`: cautionary operation cue for the visible controls on Google Search Settings > Other settings.

At runtime, do not load every image card by default. Load only the matching card or cards for the current screen state.

## Visual Transfer Limits

- Red boxes are interaction cues tied to the preserved screenshot state. Green boxes are verification or state cues. Neither is a reusable coordinate.
- Do not copy provider names, search terms, result images, filter values, profile names, or row positions from the examples unless the current task explicitly matches them.
- Chrome Settings and Google Search Settings are different surfaces. Do not assume a control available in one exists in the other.
- If a requested control is not visibly present on the current Google Search Settings page, do not fabricate success.

## Procedure

1. Decide which settings surface the task actually needs.
   - Use `chrome://settings/searchEngines` or the Chrome Settings sidebar when the task is about the default provider or search-engine entries.
   - Use the Google results-page Search Settings menu only when the task is about Google Search display behavior.

2. Change the default provider when requested.
   - On the Chrome Search engine page, open the provider selection dialog.
   - Select the provider named by the current task.
   - Confirm only after the correct provider is selected.
   - Verify that the dialog closes and the requested provider is shown as the default.

3. Manage search-engine entries when requested.
   - From the Search engine page, open **Manage search engines and site search**.
   - Delete, edit, or inspect entries according to the current task, using live labels in the management list.
   - Verify that only the requested entry changes were made.

4. Inspect Google Search settings when requested.
   - From a live Google results page, open the Search Settings menu and use **More settings**.
   - Compare the visible page content against the task. If the requested control is not actually visible, continue searching visible settings surfaces or treat the control as unavailable in the current environment.

## Result Verification Cues

- The default search engine shown in Chrome Settings matches the requested provider.
- Any requested management change is visible in the search-engine or site-search list.
- Any requested search-results preference is visibly active on the results page or in Google Search Settings.
- If the relevant Google Search Settings page does not visibly expose the requested control, do not mark success.

## Common Failure Modes

- Confirming the provider dialog while the old provider is still selected.
- Treating Google Search Settings as the same surface as Chrome Search engine settings.
- Scrolling or clicking through a Google Search settings page that does not contain the requested control while still assuming the task is solved.
- Treating example provider names or example result filters from the images as reusable task values.
- Marking success from an open settings page without verifying that the requested control exists and is in the requested state.
