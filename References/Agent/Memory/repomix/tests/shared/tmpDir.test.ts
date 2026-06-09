import os from 'node:os';
import path from 'node:path';
import { describe, expect, it } from 'vitest';
import { getRepomixTmpDir, REPOMIX_TMP_DIR_NAME } from '../../src/shared/tmpDir.js';

describe('shared/tmpDir', () => {
  it('returns a path under os.tmpdir() ending with the umbrella name', () => {
    const dir = getRepomixTmpDir();
    expect(dir.startsWith(os.tmpdir())).toBe(true);
    expect(path.basename(dir)).toBe(REPOMIX_TMP_DIR_NAME);
    expect(REPOMIX_TMP_DIR_NAME).toBe('repomix');
  });
});
