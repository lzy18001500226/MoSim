# Template-Based Word Export

> Use this workflow to build or verify a project-owned Chinese Word report or
> handbook from Markdown and an approved `.docx` template. It owns the reusable
> process, not a single report's narrative or visual design.

## 1. When To Use It

Use this workflow when a task asks to generate, rebuild, validate, or publish a
Word document whose source is project Markdown and whose layout is controlled by
an approved Word template.

Do not use it to rewrite report conclusions, infer experimental evidence, or
replace manual visual review of a final Word layout.

## 2. Required Inputs And Contract

Identify these inputs before running a builder:

```text
Markdown source
approved template (.docx)
named report-specific builder
new output path
build/QA manifest directory
```

The source contract is intentionally small:

1. One document title uses `#`.
2. Chapters use `##`; subsections use `###` and `####`.
3. An image is a local Markdown image followed by its figure caption on the
   next non-empty line:

   ```markdown
   ![optional alt text](relative/path/to/image.png)
   图 12-20　Figure title
   ```

4. A Markdown table has a preceding table caption:

   ```markdown
   表 12-20　Table title
   | Column A | Column B |
   |---|---|
   | value | value |
   ```

5. Formula-capable builders use fenced `latex` blocks for display equations.
6. Every referenced image must exist below the project root and retain its
   original file bytes.

An adapter may have a documented exception, such as an explicit table-caption
map. Encode that exception in the adapter and validate it; do not silently guess
captions, image paths, or heading levels.

## 3. Current Adapters

The builders are deliberately specialized. Do not merge them into a generic
engine until a third report type proves a stable common abstraction.

| Source family | Builder | Intended behavior |
|---|---|---|
| Competition simulation report | `Docs/报告/build_competition_report_docx.py` | Uses Pandoc for native Word tables and Office Math, then applies chapter-local Word fields and image-hash validation. |
| User manual | `Docs/报告/build_user_manual_docx.py` | Parses the manual's declared Markdown blocks and explicit table exceptions, then restores template page chrome after `python-docx` saves. |
| Competition highlights | `Docs/报告/build_challenge_highlights_docx.py` | Builds the short highlights draft with native tables, original images, and continuous Word caption fields. |

The adapter is part of the source contract. A new report type first needs a
small adapter selection/design review; it must not be forced through an
unrelated builder just because both inputs are Markdown.

## 4. Preflight

1. Read the report source, template, selected builder, and this workflow.
2. Inspect only the task-owned Git paths. Do not use broad worktree status or
   stage unrelated changes.
3. Check that the template exists and will not be overwritten.
4. Check image references, expected figure/table captions, fenced formulas when
   applicable, and the intended output/manifest paths.
5. Check each source image and planned output against the Git host's per-file
   limit. Treat 100 MiB as the conservative publication threshold unless a
   stricter release rule applies.
6. Check the selected builder's dependencies with a bounded command, for
   example:

   ```powershell
   python Docs/报告/build_competition_report_docx.py --help
   ```

Stop for missing input, a source image outside the repository, a credential-like
artifact, a required renderer that cannot be located, or an ambiguous adapter
selection. Do not substitute a template or downsample an image to hide a
publication problem.

## 5. Build

Run the named adapter with the approved source and template. For the current
competition report:

```powershell
python Docs/报告/build_competition_report_docx.py --export-pdf
```

The builder must create native Word tables, preserve image bytes, set
`w:doNotCompressPictures`, request field updates with `w:updateFields`, and
emit Word `SEQ` fields for captions. For chapter-local numbering, the chapter
field must remain available to the caption field even when the template renders
the chapter number itself.

Run external processes with bounded progress/time limits. If a process reaches
the limit without an observable result, stop it, retain its log/partial manifest,
and report a build blocker rather than leaving an unbounded Word or Pandoc
process running.

## 6. Required Validation

Validation has structural and visual layers. A successful file write alone is
not acceptance.

### 6.1 Structural Validation

Record the following in the build manifest or terminal evidence:

- output exists, is non-empty, and opens as a ZIP/OOXML package;
- expected native `w:tbl` tables, image references, and Office Math objects
  exist where the selected adapter supports them;
- figure/table `SEQ` fields exist, reset at the intended heading level, and
  have no zero or missing displayed result after Word updates fields;
- every source image SHA-256 is present among `word/media/` payloads; extra
  template media is allowed;
- template header, footer, page, and style assets are preserved when the
  adapter promises to preserve them;
- the generated `.docx` is not accidentally staged when it exceeds the
  publication limit.

### 6.2 Visual Validation

When Word/PDF export and a renderer are available, export PDF, render all pages
or a documented review set, and inspect for blank pages, missing figures,
broken tables, caption gaps, and obvious overflow. If no renderer is available,
report the result as structurally verified with visual layout still unverified.

Do not claim live simulation, runtime, or performance acceptance from a report
export or its screenshots.

## 7. Publication

Keep the source Markdown, template, builder, workflow/skill links, and build
manifest reviewable. The generated Word output follows its own size rule:

| Output condition | Publication action |
|---|---|
| Within the Git host file limit | Stage only the reviewed report paths, validate the cached diff, then commit and push. |
| Above the Git host file limit | Keep the exact output local and use an exact ignore for that generated filename. Commit the reproducible source, builder, and manifest. Use Git LFS or release attachments only after an explicit publication decision. |

Never reduce image resolution, strip figures, or replace native Word tables with
plain Markdown solely to make a generated `.docx` fit Git. Never commit tokens,
credentials, temporary Office files, or renderer caches.

Before publication, run the per-task Git closeout in
`Docs/Workflows/pre_submit_check.md`: exact-path stage, staged-path review,
`git diff --cached --check`, credential scan, commit, push, and upstream sync
verification.

## 8. Expected Outputs And Blockers

Expected outputs are the `.docx`, the adapter's build manifest, optional PDF/
rendered QA artifacts, and an exact path-scoped Git record for source changes.

Report a blocker with the source/template/adapter/output paths and the failed
check when any of these occur:

- source/template/image path is missing or outside the repository;
- caption or table association is ambiguous;
- the generated file exceeds the host limit without an approved release path;
- a source image or generated payload contains credentials or an unsupported
  large binary;
- structural checks fail, or visual QA shows layout damage;
- Git staging, credential scan, commit, or push cannot complete.
