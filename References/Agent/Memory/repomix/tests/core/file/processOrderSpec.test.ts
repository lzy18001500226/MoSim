import { describe, expect, it, vi } from 'vitest';
import { processFiles } from '../../../src/core/file/fileProcess.js';
import type { RawFile } from '../../../src/core/file/fileTypes.js';
import { createMockConfig } from '../../testing/testUtils.js';

// Behavior-level regression tests for the file-processing transform order.
//
// fileProcess.ts documents the pipeline as:
//   [removeComments → compress] (worker) → truncateBase64 → removeEmptyLines → trim → showLineNumbers
//
// The order matters — a perf optimization that parallelizes or reorders the
// lightweight pass could silently break invariants users rely on:
//
//   - line numbers must reflect the *final* post-cleanup line count
//     (showLineNumbers runs LAST; removeEmptyLines runs BEFORE it)
//   - trim must precede line numbering so that leading/trailing whitespace
//     does not consume early line numbers
//
// These specs assert the observable consequences of that order against the
// real `processFiles` entrypoint. Heavy-path (compress/removeComments) is not
// exercised here — those are gated by separate worker dispatch and have their
// own coverage; the transforms most likely to be reshuffled by a future
// perf pass live in `applyLightweightTransforms`.

describe('file process transform order spec', () => {
  it('numbers lines AFTER removing empty lines, not before', async () => {
    // 5 logical lines on disk; 3 of them are blank. removeEmptyLines should
    // collapse to 2, and showLineNumbers should then emit `1:` and `2:`.
    // If the order were inverted, the visible numbers would be 1 and 5 (or
    // there would be numbered empty rows in the output).
    const rawFiles: RawFile[] = [
      {
        path: 'sample.ts',
        content: 'first\n\n\n\nsecond\n',
      },
    ];

    const config = createMockConfig({
      output: { removeEmptyLines: true, showLineNumbers: true },
    });

    const [processed] = await processFiles(rawFiles, config, vi.fn());

    const lines = processed.content.split('\n');
    expect(lines).toEqual(['1: first', '2: second']);
  });

  it('trims surrounding whitespace BEFORE numbering lines', async () => {
    // Input has 2 leading and 2 trailing blank lines, then real content.
    // String-level trim() strips ALL of that surrounding whitespace from the
    // payload, leaving a single line to number. If line-numbering ran first,
    // we would see `1:` on a blank line, `3: real content` further down, etc.
    const rawFiles: RawFile[] = [
      {
        path: 'sample.ts',
        content: '\n\n\nreal content\n\n\n',
      },
    ];

    const config = createMockConfig({
      output: { showLineNumbers: true },
    });

    const [processed] = await processFiles(rawFiles, config, vi.fn());

    // After trim → single line "real content" → "1: real content"
    expect(processed.content).toBe('1: real content');
  });

  it('fires `truncateBase64` on a qualifying base64 run', async () => {
    // Narrower spec: this only verifies truncateBase64 runs and produces a
    // truncated output. A full ORDER claim against this transform (truncate
    // must precede line numbering) is hard to make observable: the
    // standalone-base64 regex is unanchored, base64 runs stay on a single
    // line, and a line-number prefix like "1: " does not break the contiguity
    // of the run itself. So a swap of truncateBase64's position is NOT
    // covered by any current spec — only the line-numbering pipeline order
    // (removeEmptyLines / trim / showLineNumbers) is.
    //
    // The pattern requires enough diversity (see truncateBase64.ts:
    // MIN_BASE64_LENGTH_STANDALONE=256, MIN_CHAR_DIVERSITY=10,
    // MIN_CHAR_TYPE_COUNT=3) — a monotonous 'A'.repeat() does not qualify, so
    // we synthesize a varied 512-char run.
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const longBase64 = charset.repeat(Math.ceil(512 / charset.length)).slice(0, 512);
    const rawFiles: RawFile[] = [
      {
        path: 'sample.ts',
        content: `const blob = "${longBase64}";\nconst y = 1;\n`,
      },
    ];

    const config = createMockConfig({
      output: { truncateBase64: true },
    });

    const [processed] = await processFiles(rawFiles, config, vi.fn());

    // The original 512-char run must not be present verbatim — truncateBase64
    // replaced it with a placeholder-ish form.
    expect(processed.content).not.toContain(longBase64);
    // The non-base64 surrounding content survives.
    expect(processed.content).toContain('const y = 1;');
  });

  it('numbers lines using the file final length, padding the line-number column accordingly', async () => {
    // The padding width is derived from the final line count. A reorder that
    // numbered BEFORE removeEmptyLines would compute padding off the
    // pre-cleanup length (5) instead of the post-cleanup length (2), making
    // the test below fail because of an extra leading space.
    const rawFiles: RawFile[] = [{ path: 'sample.ts', content: 'first\n\n\nsecond\n' }];

    const config = createMockConfig({
      output: { removeEmptyLines: true, showLineNumbers: true },
    });

    const [processed] = await processFiles(rawFiles, config, vi.fn());

    // With 2 final lines, padding length is 1, so prefixes are `1:` / `2:`
    // (no extra leading spaces).
    expect(processed.content).toBe('1: first\n2: second');
  });
});
