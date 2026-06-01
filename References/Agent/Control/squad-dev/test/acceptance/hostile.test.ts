/**
 * Hostile QA acceptance test runner.
 * Runs adversarial Gherkin feature files that probe CLI resilience.
 */

import { afterEach } from 'vitest';
import { join } from 'node:path';
import { createRegistry, runFeature } from './support/runner.js';
import { registerCLISteps } from './steps/cli-steps.js';
import { registerHostileSteps } from './steps/hostile-steps.js';
import { TerminalHarness } from './harness.js';

// Create step definition registry — hostile steps FIRST (more specific patterns
// must be checked before cli-steps' generic `I run "(.+)"` pattern).
const registry = createRegistry();
registerHostileSteps(registry);
registerCLISteps(registry);

// Cleanup harnesses after each test
afterEach(async (context) => {
  const harness = (context as Record<string, unknown>).harness as TerminalHarness | undefined;
  if (harness) {
    await harness.close();
  }
  const rapidHarnesses = (context as Record<string, unknown>).rapidHarnesses as TerminalHarness[] | undefined;
  if (rapidHarnesses) {
    await Promise.all(rapidHarnesses.map(h => h.close()));
  }
});

const featuresDir = join(__dirname, 'features');

// Hostile QA scenarios
runFeature(join(featuresDir, 'hostile-tiny-terminal.feature'), registry);
runFeature(join(featuresDir, 'hostile-no-config.feature'), registry);
runFeature(join(featuresDir, 'hostile-invalid-input.feature'), registry);
runFeature(join(featuresDir, 'hostile-corrupt-config.feature'), registry);
runFeature(join(featuresDir, 'hostile-pipe-mode.feature'), registry);
runFeature(join(featuresDir, 'hostile-utf8.feature'), registry);
runFeature(join(featuresDir, 'hostile-rapid-input.feature'), registry);
