---
name: Search Web and Open Target Result
description: Use Google search in Chrome to submit a query, choose the intended result, and verify that the browser has opened the requested destination page instead of a similarly named result. This skill stops at the landing page and does not cover deep in-site browsing or long-page extraction.
---

# Search Web and Open Target Result

## Overview

Use Google search in Chrome to submit a query, choose the intended result, and verify that the browser has opened the requested destination page instead of a similarly named result. This skill stops at the landing page and does not cover deep in-site browsing or long-page extraction.

## When to Use

- Searching the web from Google or the Chrome new-tab surface
- Opening a specific result after the query runs
- Verifying that the target destination page is visibly open

## Preconditions

- The target query or destination site is already known.
- Chrome can reach a search surface such as Google homepage or Google results.

## Visual Annotation Conventions

- Red boxes mark action targets.
- Green boxes mark verification or recovery signals.

## Procedures

### web_search

#### open_search_surface

- Trigger: The query has not been entered yet.
- Visual grounding: The Google homepage or another web-search surface is open with a visible search field.
- Action: Focus the visible search field so the query can be typed and submitted.
- Image: `Images/google_search_box_ready.png`

#### choose_target_result

- Trigger: The query has already been submitted and the correct result is visible in the results list.
- Visual grounding: The search-results page shows candidate results that match the typed query.
- Action: Click the result title or card that matches the requested destination.
- Image: `Images/search_result_target_link.png`

#### Expected Result: verify_destination_page

- Trigger: The navigation has already occurred and the destination page should be loaded.
- Visual grounding: The requested destination page or result card is open after selecting the result.
- Action: Verify that the destination page heading or primary result card is visibly open before continuing.
- Image: `Images/destination_page_open.png`

## Common Failure Modes

- Opening a similarly named result instead of the requested destination.
- Treating a result snippet or knowledge card as completion before the destination page actually opens.
- Using the skill for in-site section hunting after the destination has already loaded.

## Runtime Assets

- `state_cards.json` carries the richer multiview authoring bundle.
- `runtime_state_cards.json` carries the slimmer runtime-facing card set.
