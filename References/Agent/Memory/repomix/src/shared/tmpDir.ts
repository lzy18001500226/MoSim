import os from 'node:os';
import path from 'node:path';

// Shared umbrella directory under $TMPDIR for all repomix temp artifacts
// (MCP outputs, token-count cache, future ephemeral state). Centralised here
// so a single grep finds every consumer and the umbrella never drifts.
export const REPOMIX_TMP_DIR_NAME = 'repomix';

/**
 * Returns `$TMPDIR/repomix`. Callers append their own subdirectory and are
 * responsible for creating it (recursive mkdir, mkdtemp, permissions etc.)
 * because each consumer has different needs.
 */
export const getRepomixTmpDir = (): string => {
  return path.join(os.tmpdir(), REPOMIX_TMP_DIR_NAME);
};
