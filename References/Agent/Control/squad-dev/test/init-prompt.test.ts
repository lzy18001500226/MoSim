/**
 * Tests for squad init prompt storage.
 * Verifies that `squad init "prompt"` stores the prompt for REPL auto-casting.
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { existsSync, readFileSync, mkdirSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { runInit } from '../packages/squad-cli/src/cli/core/init.js';

describe('squad init with prompt', () => {
  let testDir: string;

  beforeEach(() => {
    testDir = join(tmpdir(), `squad-init-prompt-test-${Date.now()}`);
    mkdirSync(testDir, { recursive: true });
  });

  afterEach(() => {
    try { rmSync(testDir, { recursive: true, force: true }); } catch { /* ignore */ }
  });

  it('stores .init-prompt when prompt option is provided', async () => {
    await runInit(testDir, { prompt: 'Build a snake game' });
    const promptFile = join(testDir, '.squad', '.init-prompt');
    expect(existsSync(promptFile)).toBe(true);
    expect(readFileSync(promptFile, 'utf-8')).toBe('Build a snake game');
  });

  it('does not create .init-prompt when no prompt is provided', async () => {
    await runInit(testDir);
    const promptFile = join(testDir, '.squad', '.init-prompt');
    expect(existsSync(promptFile)).toBe(false);
  });

  it('stores multi-line prompt from file content', async () => {
    const longPrompt = 'Build a snake game\nUsing HTML5 canvas\nWith high scores';
    await runInit(testDir, { prompt: longPrompt });
    const promptFile = join(testDir, '.squad', '.init-prompt');
    expect(existsSync(promptFile)).toBe(true);
    expect(readFileSync(promptFile, 'utf-8')).toBe(longPrompt);
  });
});
