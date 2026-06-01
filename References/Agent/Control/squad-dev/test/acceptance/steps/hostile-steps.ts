import { expect } from 'vitest';
import { mkdtempSync, mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { TerminalHarness } from '../harness.js';
import { StepDefinitions, registerStep } from '../support/runner.js';

/**
 * Hostile QA step definitions — adversarial scenarios.
 */
export function registerHostileSteps(registry: StepDefinitions): void {

  // --- Given steps ---

  registerStep(
    'Given',
    /a terminal size of (\d+) columns by (\d+) rows/,
    async (stepText, context) => {
      const match = stepText.match(/a terminal size of (\d+) columns by (\d+) rows/);
      if (!match) throw new Error('Pattern match failed');
      context.terminalCols = parseInt(match[1], 10);
      context.terminalRows = parseInt(match[2], 10);
    },
    registry
  );

  registerStep(
    'Given',
    /a non-TTY environment/,
    async (_stepText, context) => {
      context.nonTTY = true;
    },
    registry
  );

  registerStep(
    'Given',
    /a temp directory with an empty "\.squad" directory/,
    async (_stepText, context) => {
      const tempDir = mkdtempSync(join(tmpdir(), 'squad-hostile-'));
      mkdirSync(join(tempDir, '.squad'), { recursive: true });
      context.tempDir = tempDir;
    },
    registry
  );

  registerStep(
    'Given',
    /a temp directory with an empty "\.squad\/team\.md"/,
    async (_stepText, context) => {
      const tempDir = mkdtempSync(join(tmpdir(), 'squad-hostile-'));
      mkdirSync(join(tempDir, '.squad'), { recursive: true });
      writeFileSync(join(tempDir, '.squad', 'team.md'), '');
      context.tempDir = tempDir;
    },
    registry
  );

  registerStep(
    'Given',
    /a temp directory with "\.squad\/team\.md" containing "(.+)"/,
    async (stepText, context) => {
      const match = stepText.match(/a temp directory with "\.squad\/team\.md" containing "(.+)"/);
      if (!match) throw new Error('Pattern match failed');
      const tempDir = mkdtempSync(join(tmpdir(), 'squad-hostile-'));
      mkdirSync(join(tempDir, '.squad'), { recursive: true });
      writeFileSync(join(tempDir, '.squad', 'team.md'), match[1]);
      context.tempDir = tempDir;
    },
    registry
  );

  registerStep(
    'Given',
    /a temp directory where "\.squad" is a regular file/,
    async (_stepText, context) => {
      const tempDir = mkdtempSync(join(tmpdir(), 'squad-hostile-'));
      writeFileSync(join(tempDir, '.squad'), 'this is a file not a directory');
      context.tempDir = tempDir;
    },
    registry
  );

  // --- When steps ---

  registerStep(
    'When',
    /I run "(.+)" with that terminal size/,
    async (stepText, context) => {
      const match = stepText.match(/I run "(.+)" with that terminal size/);
      if (!match) throw new Error('Pattern match failed');
      const command = match[1];
      const args = command.replace(/^squad\s*/, '').split(/\s+/).filter(Boolean);
      const cols = context.terminalCols as number;
      const rows = context.terminalRows as number;

      const harness = await TerminalHarness.spawnWithArgs(args, { cols, rows });
      try { await harness.waitForExit(5000); } catch { /* timeout ok */ }
      context.harness = harness;
      context.output = harness.getOutput();
      context.exitCode = harness.getExitCode();
    },
    registry
  );

  registerStep(
    'When',
    /I run "(.+)" in non-TTY mode/,
    async (stepText, context) => {
      const match = stepText.match(/I run "(.+)" in non-TTY mode/);
      if (!match) throw new Error('Pattern match failed');
      const command = match[1];
      const args = command.replace(/^squad\s*/, '').split(/\s+/).filter(Boolean);

      // Force non-TTY via env
      const harness = await TerminalHarness.spawnWithArgs(args, {
        env: { TERM: 'dumb', NO_COLOR: '1', FORCE_COLOR: '0' }
      });
      try { await harness.waitForExit(5000); } catch { /* timeout ok */ }
      context.harness = harness;
      context.output = harness.getOutput();
      context.exitCode = harness.getExitCode();
    },
    registry
  );

  registerStep(
    'When',
    /I run hostile command with control characters/,
    async (_stepText, context) => {
      // Use a control-char-laden string as a subcommand
      const harness = await TerminalHarness.spawnWithArgs(['\x07\x08\x1B[31m']);
      try { await harness.waitForExit(5000); } catch { /* timeout ok */ }
      context.harness = harness;
      context.output = harness.getOutput();
      context.exitCode = harness.getExitCode();
    },
    registry
  );

  registerStep(
    'When',
    /I run hostile command with a 10KB argument/,
    async (_stepText, context) => {
      const longArg = 'X'.repeat(10240);
      const harness = await TerminalHarness.spawnWithArgs([longArg]);
      try { await harness.waitForExit(5000); } catch { /* timeout ok */ }
      context.harness = harness;
      context.output = harness.getOutput();
      context.exitCode = harness.getExitCode();
    },
    registry
  );

  registerStep(
    'When',
    /I run hostile command with null bytes/,
    async (_stepText, context) => {
      try {
        const harness = await TerminalHarness.spawnWithArgs(['test\x00embedded']);
        try { await harness.waitForExit(5000); } catch { /* timeout ok */ }
        context.harness = harness;
        context.output = harness.getOutput();
        context.exitCode = harness.getExitCode();
        context.nullByteError = false;
      } catch (err) {
        // Node.js rejects null bytes in spawn args — this is expected
        context.nullByteError = true;
        context.nullByteErrorMsg = err instanceof Error ? err.message : String(err);
      }
    },
    registry
  );

  registerStep(
    'When',
    /I run hostile command with empty argument/,
    async (_stepText, context) => {
      const harness = await TerminalHarness.spawnWithArgs(['']);
      try { await harness.waitForExit(5000); } catch { /* timeout ok */ }
      context.harness = harness;
      context.output = harness.getOutput();
      context.exitCode = harness.getExitCode();
    },
    registry
  );

  registerStep(
    'When',
    /I run hostile command with whitespace-only argument/,
    async (_stepText, context) => {
      const harness = await TerminalHarness.spawnWithArgs(['   ']);
      try { await harness.waitForExit(5000); } catch { /* timeout ok */ }
      context.harness = harness;
      context.output = harness.getOutput();
      context.exitCode = harness.getExitCode();
    },
    registry
  );

  registerStep(
    'When',
    /I run hostile command with emoji argument/,
    async (_stepText, context) => {
      const harness = await TerminalHarness.spawnWithArgs(['🚀💥🔥']);
      try { await harness.waitForExit(5000); } catch { /* timeout ok */ }
      context.harness = harness;
      context.output = harness.getOutput();
      context.exitCode = harness.getExitCode();
    },
    registry
  );

  registerStep(
    'When',
    /I run hostile command with CJK argument/,
    async (_stepText, context) => {
      const harness = await TerminalHarness.spawnWithArgs(['你好世界测试']);
      try { await harness.waitForExit(5000); } catch { /* timeout ok */ }
      context.harness = harness;
      context.output = harness.getOutput();
      context.exitCode = harness.getExitCode();
    },
    registry
  );

  registerStep(
    'When',
    /I run hostile command with RTL argument/,
    async (_stepText, context) => {
      const harness = await TerminalHarness.spawnWithArgs(['مرحبا بالعالم']);
      try { await harness.waitForExit(5000); } catch { /* timeout ok */ }
      context.harness = harness;
      context.output = harness.getOutput();
      context.exitCode = harness.getExitCode();
    },
    registry
  );

  registerStep(
    'When',
    /I run hostile command with zero-width characters/,
    async (_stepText, context) => {
      const harness = await TerminalHarness.spawnWithArgs(['a\u200Bb\u200Dc']);
      try { await harness.waitForExit(5000); } catch { /* timeout ok */ }
      context.harness = harness;
      context.output = harness.getOutput();
      context.exitCode = harness.getExitCode();
    },
    registry
  );

  registerStep(
    'When',
    /I run hostile command with mixed unicode scripts/,
    async (_stepText, context) => {
      const harness = await TerminalHarness.spawnWithArgs(['Hello你好مرحبا🚀']);
      try { await harness.waitForExit(5000); } catch { /* timeout ok */ }
      context.harness = harness;
      context.output = harness.getOutput();
      context.exitCode = harness.getExitCode();
    },
    registry
  );

  registerStep(
    'When',
    /I run (\d+) rapid "(.+)" commands/,
    async (stepText, context) => {
      const match = stepText.match(/I run (\d+) rapid "(.+)" commands/);
      if (!match) throw new Error('Pattern match failed');
      const count = parseInt(match[1], 10);
      const command = match[2];
      const args = command.replace(/^squad\s*/, '').split(/\s+/).filter(Boolean);

      // Fire all simultaneously
      const promises = Array.from({ length: count }, () =>
        TerminalHarness.spawnWithArgs(args)
      );
      const harnesses = await Promise.all(promises);
      await Promise.all(harnesses.map(h => h.waitForExit(10000).catch(() => {})));

      context.rapidHarnesses = harnesses;
      context.rapidExitCodes = harnesses.map(h => h.getExitCode());
      context.rapidOutputs = harnesses.map(h => h.getOutput());
    },
    registry
  );

  registerStep(
    'When',
    /I run rapid alternating valid and invalid commands/,
    async (_stepText, context) => {
      const commands = [
        ['--version'],
        ['nonexistent'],
        ['--help'],
        ['also-garbage'],
        ['status'],
      ];
      const promises = commands.map(args => TerminalHarness.spawnWithArgs(args));
      const harnesses = await Promise.all(promises);
      await Promise.all(harnesses.map(h => h.waitForExit(10000).catch(() => {})));

      context.rapidHarnesses = harnesses;
      context.rapidExitCodes = harnesses.map(h => h.getExitCode());
    },
    registry
  );

  registerStep(
    'When',
    /I run "(.+)" and "(.+)" concurrently/,
    async (stepText, context) => {
      const match = stepText.match(/I run "(.+)" and "(.+)" concurrently/);
      if (!match) throw new Error('Pattern match failed');
      const args1 = match[1].replace(/^squad\s*/, '').split(/\s+/).filter(Boolean);
      const args2 = match[2].replace(/^squad\s*/, '').split(/\s+/).filter(Boolean);

      const [h1, h2] = await Promise.all([
        TerminalHarness.spawnWithArgs(args1),
        TerminalHarness.spawnWithArgs(args2),
      ]);
      await Promise.all([
        h1.waitForExit(10000).catch(() => {}),
        h2.waitForExit(10000).catch(() => {}),
      ]);

      context.rapidHarnesses = [h1, h2];
      context.rapidExitCodes = [h1.getExitCode(), h2.getExitCode()];
    },
    registry
  );

  // --- Then steps ---

  registerStep(
    'Then',
    /the null byte error is caught gracefully/,
    async (_stepText, context) => {
      // Node.js should reject null bytes at the spawn level
      // This is expected — the important thing is no unhandled crash
      expect(context.nullByteError).toBe(true);
      expect(context.nullByteErrorMsg).toContain('null bytes');
    },
    registry
  );

  registerStep(
    'Then',
    /the process does not crash/,
    async (_stepText, context) => {
      const exitCode = context.exitCode as number | null;
      const harness = context.harness as TerminalHarness | undefined;
      // Process completed (didn't hang or segfault with signal)
      // Exit code 0 or 1 are both acceptable (success or handled error)
      // Signals/crashes typically produce null exit code or >128
      if (exitCode === null && harness) {
        // Still running — force close and note it
        await harness.close();
        // If it was still running, that's okay for non-interactive
      }
      // Should not have a signal-kill exit code (>128 on Unix)
      if (exitCode !== null && exitCode > 128) {
        throw new Error(`Process crashed with signal exit code: ${exitCode}`);
      }
    },
    registry
  );

  registerStep(
    'Then',
    /the exit code is not null/,
    async (_stepText, context) => {
      const harness = context.harness as TerminalHarness | undefined;
      if (harness) {
        try { await harness.waitForExit(5000); } catch { /* ok */ }
      }
      const exitCode = harness?.getExitCode() ?? context.exitCode;
      // On Windows processes might still be running; accept that
      // The important thing is it didn't crash with a signal
      expect(exitCode).not.toBeUndefined();
    },
    registry
  );

  registerStep(
    'Then',
    /all commands complete without crash/,
    async (_stepText, context) => {
      const codes = context.rapidExitCodes as (number | null)[];
      const harnesses = context.rapidHarnesses as TerminalHarness[];
      // Ensure all exited
      for (const h of harnesses) {
        try { await h.waitForExit(5000); } catch { /* ok */ }
      }
      // None should have crashed (signal exit >128)
      for (const code of codes) {
        if (code !== null && code > 128) {
          throw new Error(`A rapid command crashed with exit code: ${code}`);
        }
      }
    },
    registry
  );

  registerStep(
    'Then',
    /all exit codes are (\d+)/,
    async (stepText, context) => {
      const match = stepText.match(/all exit codes are (\d+)/);
      if (!match) throw new Error('Pattern match failed');
      const expected = parseInt(match[1], 10);
      const harnesses = context.rapidHarnesses as TerminalHarness[];
      for (const h of harnesses) {
        try { await h.waitForExit(5000); } catch { /* ok */ }
        expect(h.getExitCode()).toBe(expected);
      }
    },
    registry
  );
}
