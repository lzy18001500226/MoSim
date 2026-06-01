# E2E Acceptance Tests

This directory contains end-to-end acceptance tests for the Squad CLI using a Gherkin-style BDD approach.

## Structure

```
test/acceptance/
├── harness.ts              # Terminal harness for spawning CLI
├── acceptance.test.ts      # Main test runner
├── features/               # Gherkin feature files
│   ├── version.feature
│   ├── help.feature
│   ├── status.feature
│   ├── error-handling.feature
│   └── doctor.feature
├── steps/                  # Step definitions
│   └── cli-steps.ts
└── support/                # Test infrastructure
    ├── gherkin.ts          # Minimal Gherkin parser
    └── runner.ts           # Test runner helpers
```

## Running Tests

```bash
# Run all acceptance tests
npm test -- test/acceptance/acceptance.test.ts

# Run UX gates
npm test -- test/ux-gates.test.ts

# Run both
npm test -- test/acceptance/acceptance.test.ts test/ux-gates.test.ts
```

## Writing New Tests

### 1. Create a Feature File

Create `test/acceptance/features/my-feature.feature`:

```gherkin
Feature: My new feature

  Scenario: User runs my command
    When I run "squad my-command"
    Then the output contains "Success"
    And the exit code is 0
```

### 2. Add to Test Runner

Edit `test/acceptance/acceptance.test.ts`:

```typescript
runFeature(join(featuresDir, 'my-feature.feature'), registry);
```

### 3. Use Existing Step Definitions

Available steps:

**Given:**
- `Given the current directory has a ".squad" directory`

**When:**
- `When I run "squad [args]"`

**Then:**
- `Then the output contains "text"`
- `Then the output matches pattern "regex"`
- `Then the exit code is 0`

### 4. Add Custom Step Definitions (if needed)

Edit `test/acceptance/steps/cli-steps.ts`:

```typescript
registerStep(
  'Then',
  /my custom assertion pattern/,
  async (stepText, context) => {
    // Your assertion logic
  },
  registry
);
```

## Architecture Notes

### Terminal Harness

Uses `child_process.spawn` with pipes (not node-pty) for cross-platform compatibility. Key features:

- Spawns CLI: `node packages/squad-cli/dist/cli-entry.js [args]`
- Captures stdout/stderr in append-only buffer
- ANSI code stripping for clean assertions
- Environment control (TERM=dumb, NO_COLOR=1)

### Test Scope

**Covered:**
- CLI argument parsing (--version, --help)
- Command dispatch and routing
- Output format validation
- Exit codes
- Error messages

**Not Covered:**
- Interactive shell (requires Copilot SDK)
- Long-running daemons (loop, triage)
- Complex Ink UI interactions (use ink-testing-library)

## Debugging

To see raw CLI output:

```typescript
const harness = await TerminalHarness.spawnWithArgs(['--help']);
await harness.waitForExit();
console.log('Raw output:', harness.captureRawFrame());
console.log('Stripped output:', harness.captureFrame());
```

## CI Integration

Tests require the CLI to be built first:

```bash
npm run build
npm test -- test/acceptance/
```

This is handled automatically by the standard test flow.
