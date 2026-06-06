---
id: auto-compact
name: Auto-Compact
description: Runs /compact to condense context when needed
icon: auto-compact.png
category: workflow
activationTriggers:
  - context
  - memory
  - compact
  - summarize
  - long conversation
---

# Instructions

When context grows large or after completing a significant task, run the /compact command to summarize and condense the conversation context.

## Behavioral Guidelines

- Monitor context window usage
- Compact after completing major tasks
- Preserve essential context during compaction
- Summarize decisions and outcomes
- Keep actionable information prominent
- Remove redundant exploration paths

## When to Compact

- After completing a significant feature
- When context approaches limits
- After extensive exploration/debugging
- Before starting a new major task
- When switching focus areas

## Compaction Preserves

- Final decisions and rationale
- Key code locations
- Unresolved issues
- User preferences discovered
- Important constraints identified
