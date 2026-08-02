---
name: template-based-word-export
description: Build, rebuild, validate, or publish a MoSim Markdown-to-Word report or handbook from an approved DOCX template while retaining native tables, Word fields, original image bytes, and size-safe publication.
---

# Template-Based Word Export

Use this skill for a user request involving Word report generation, template
placement, Word captions, native tables, formula conversion, or DOCX release.

## Read First

1. `AGENTS.md`
2. `Docs/Workflows/new_conversation_context.md`
3. `Docs/Workflows/template_based_word_export.md`
4. The named Markdown source, template, and selected builder

## Route

Select the existing report-specific adapter before running anything:

| Work | Adapter |
|---|---|
| Competition simulation report | `Docs/报告/build_competition_report_docx.py` |
| User manual | `Docs/报告/build_user_manual_docx.py` |
| Competition highlights | `Docs/报告/build_challenge_highlights_docx.py` |

Do not create a generic exporter or route an unfamiliar report through another
report's builder without a bounded adapter-design review.

## Required Practice

1. Preserve the approved template; create a new output instead of overwriting
   it.
2. Keep Markdown tables as native Word tables and retain original image bytes.
3. Require Word `SEQ` caption fields, chapter-local numbering when applicable,
   and `w:doNotCompressPictures`.
4. Run the adapter's structural checks; run PDF/render visual QA when a renderer
   is available.
5. Stage only task-owned source/adapter/manifest paths. A generated DOCX above
   the Git host limit remains local or uses an explicitly approved LFS/release
   route; it is not compressed merely to force a Git commit.

## Stop Conditions

Stop and report the exact blocker for missing source/template/image paths,
ambiguous captions, credentials, files beyond the publication limit, a failed
OOXML/hash/field check, a broken visual review, or unavailable required tooling.

Use `Docs/Workflows/template_based_word_export.md` for the full input contract,
validation matrix, and Git closeout procedure.
