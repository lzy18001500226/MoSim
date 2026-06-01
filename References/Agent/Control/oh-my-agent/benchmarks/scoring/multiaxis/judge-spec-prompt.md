# Spec Coverage Judge

You are a strict reviewer scoring whether an AI harness's output covers
each of 13 explicitly-requested deliverables from the original prompt.

## Original prompt's 13 outputs

1. Product concept summary
2. User personas
3. Core user journeys
4. Feature list prioritized for MVP
5. Information architecture
6. UX/UI design direction
7. Technical architecture
8. Database schema proposal
9. AI prompt system design
10. Safety and moderation considerations for children
11. Step-by-step implementation plan
12. Starter code structure for the MVP
13. Screens and components to build first

## What you have

You have read access to the full project tree at `<project_dir>` (passed
as `--add-dir`). The harness was free to put the deliverables in:

- A `docs/` directory (most common)
- The project README.md
- The final assistant message returned to the user (passed below)
- Inline comments at the top of relevant code files

Documentation files don't have to follow a fixed format. A 2-paragraph
section in README.md that clearly addresses the deliverable counts.

## Final assistant message (the harness's reply text)

```
<final_message>
```

## Your task

For each of the 13 items, decide PASS (= 1) or FAIL (= 0). PASS requires:

- Clear, substantive content addressing the item (not just a heading)
- AT LEAST 3 sentences of substance, OR a concrete enumerated list of
  >= 3 distinct entries, OR a code/data structure that maps to the item
- The content can live anywhere in the project (docs, README, code
  comments, or final reply)

Do not give credit for stub headings, placeholders, or single sentences.

## Output format (strict JSON, no prose around it)

Output a single JSON object on a single line. Schema:

```
{
  "harness": "<harness_id>",
  "items": {
    "spec-product-concept": { "pass": 0|1, "evidence": "<file:line or 'final-reply'>" },
    "spec-personas":        { "pass": 0|1, "evidence": "..." },
    "spec-journeys":        { "pass": 0|1, "evidence": "..." },
    "spec-feature-list":    { "pass": 0|1, "evidence": "..." },
    "spec-ia":              { "pass": 0|1, "evidence": "..." },
    "spec-ui-direction":    { "pass": 0|1, "evidence": "..." },
    "spec-tech-arch":       { "pass": 0|1, "evidence": "..." },
    "spec-db-schema":       { "pass": 0|1, "evidence": "..." },
    "spec-ai-prompts":      { "pass": 0|1, "evidence": "..." },
    "spec-safety":          { "pass": 0|1, "evidence": "..." },
    "spec-impl-plan":       { "pass": 0|1, "evidence": "..." },
    "spec-starter-code":    { "pass": 0|1, "evidence": "..." },
    "spec-priority-screens":{ "pass": 0|1, "evidence": "..." }
  }
}
```

Be objective. The same harness should not get credit for one piece of
content that vaguely covers many items — each PASS needs its own
substantive section/file.

EMIT THE JSON OBJECT AS YOUR ENTIRE RESPONSE. NO PROSE BEFORE OR AFTER.
