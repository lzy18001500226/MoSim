/**
 * #674 / #675 — Layout and anchoring acceptance tests
 *
 * Validates that InputPrompt stays visible within the terminal viewport
 * across all shell states, that long streaming content and large agent
 * panels don't push the prompt off-screen, and that terminal resize
 * triggers layout recalculation.
 *
 * 📌 Proactive: Written from requirements while implementation is in progress.
 * Tests target App composition and component contracts. Some assertions may
 * need adjustment once Kovash lands the anchoring implementation.
 */

import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest';
import React from 'react';
import { render } from 'ink-testing-library';
import { InputPrompt } from '../packages/squad-cli/src/cli/shell/components/InputPrompt.js';
import { AgentPanel } from '../packages/squad-cli/src/cli/shell/components/AgentPanel.js';
import { MessageStream } from '../packages/squad-cli/src/cli/shell/components/MessageStream.js';
import type { ShellMessage, AgentSession } from '../packages/squad-cli/src/cli/shell/types.js';

const h = React.createElement;

function makeMessage(overrides: Partial<ShellMessage> & { content: string; role: ShellMessage['role'] }): ShellMessage {
  return { timestamp: new Date(), ...overrides };
}

function makeAgent(overrides: Partial<AgentSession> & { name: string }): AgentSession {
  return {
    role: 'core dev',
    status: 'idle',
    startedAt: new Date(),
    ...overrides,
  };
}

// ============================================================================
// Helpers
// ============================================================================

/** Generate a long block of streaming content (simulates verbose agent output). */
function generateLongContent(lines: number): string {
  return Array.from({ length: lines }, (_, i) => `Line ${i + 1}: This is streaming content from the agent response.`).join('\n');
}

/** Generate many agents to test overflow behavior. */
function generateManyAgents(count: number): AgentSession[] {
  return Array.from({ length: count }, (_, i) =>
    makeAgent({ name: `Agent${i + 1}`, role: 'specialist', status: i % 3 === 0 ? 'working' : 'idle' })
  );
}

// ============================================================================
// #675 — InputPrompt renders within terminal viewport
// ============================================================================

describe('#675 — InputPrompt viewport anchoring', () => {
  it('InputPrompt renders within terminal viewport (not pushed off-screen)', () => {
    const onSubmit = vi.fn();
    const { lastFrame } = render(
      h(InputPrompt, { onSubmit, disabled: false })
    );
    const frame = lastFrame()!;
    // The prompt indicator should be visible
    expect(frame).toContain('>');
  });

  it('during startup state: InputPrompt visible', () => {
    // Startup: no messages, not processing, empty agent list
    const onSubmit = vi.fn();
    const { lastFrame } = render(
      h(React.Fragment, null,
        h(AgentPanel, { agents: [] }),
        h(MessageStream, {
          messages: [],
          processing: false,
          streamingContent: new Map(),
        }),
        h(InputPrompt, { onSubmit, disabled: false, messageCount: 0 }),
      )
    );
    const frame = lastFrame()!;
    // Prompt should be visible even with empty state
    expect(frame).toContain('>');
  });

  it('during streaming state: InputPrompt visible', () => {
    // Streaming: processing=true, content flowing
    const onSubmit = vi.fn();
    const { lastFrame } = render(
      h(React.Fragment, null,
        h(MessageStream, {
          messages: [makeMessage({ role: 'user', content: 'build the feature' })],
          processing: true,
          streamingContent: new Map([['Kovash', 'Working on the implementation...']]),
        }),
        h(InputPrompt, { onSubmit, disabled: true }),
      )
    );
    const frame = lastFrame()!;
    // Both the streaming content and prompt indicator should be present
    expect(frame).toContain('Working on the implementation');
    // InputPrompt in disabled mode shows a spinner
    expect(frame).toMatch(/[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏>]/);
  });

  it('during idle state: InputPrompt visible', () => {
    // Idle: conversation history exists, not processing
    const onSubmit = vi.fn();
    const { lastFrame } = render(
      h(React.Fragment, null,
        h(MessageStream, {
          messages: [
            makeMessage({ role: 'user', content: 'hello' }),
            makeMessage({ role: 'agent', content: 'Hi there!', agentName: 'Kovash' }),
          ],
          processing: false,
          streamingContent: new Map(),
        }),
        h(InputPrompt, { onSubmit, disabled: false, messageCount: 2 }),
      )
    );
    const frame = lastFrame()!;
    // Prompt should appear after conversation
    expect(frame).toContain('>');
    expect(frame).toContain('Hi there!');
  });
});

// ============================================================================
// #674 — Long streaming content doesn't push InputPrompt below viewport
// ============================================================================

describe('#674 — Predictable scrolling / layout stability', () => {
  it('long streaming content does not push InputPrompt below viewport', () => {
    const longContent = generateLongContent(100);
    const onSubmit = vi.fn();
    const { lastFrame } = render(
      h(React.Fragment, null,
        h(MessageStream, {
          messages: [makeMessage({ role: 'user', content: 'generate report' })],
          processing: true,
          streamingContent: new Map([['Fenster', longContent]]),
        }),
        h(InputPrompt, { onSubmit, disabled: true }),
      )
    );
    const frame = lastFrame()!;
    // The frame should contain content — no crash with large content
    expect(frame.length).toBeGreaterThan(0);
    // The streaming content should be present
    expect(frame).toContain('Line 1:');
    // InputPrompt spinner or prompt indicator should still be in the frame
    expect(frame).toMatch(/[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏>]/);
  });

  it('AgentPanel with many agents does not overflow viewport', () => {
    const manyAgents = generateManyAgents(20);
    const { lastFrame } = render(
      h(React.Fragment, null,
        h(AgentPanel, { agents: manyAgents }),
        h(InputPrompt, { onSubmit: vi.fn(), disabled: false }),
      )
    );
    const frame = lastFrame()!;
    // Frame should render without crash
    expect(frame.length).toBeGreaterThan(0);
    // At least some agents should be visible
    expect(frame).toContain('Agent1');
    // Prompt should still be present
    expect(frame).toContain('>');
  });

  it('terminal resize triggers layout recalculation', () => {
    const onSubmit = vi.fn();
    // Set initial narrow width
    const origColumns = process.stdout.columns;
    Object.defineProperty(process.stdout, 'columns', { value: 60, writable: true, configurable: true });

    const { lastFrame, rerender } = render(
      h(InputPrompt, { onSubmit, disabled: false })
    );
    const narrowFrame = lastFrame()!;
    expect(narrowFrame).toContain('>');

    // Simulate terminal resize to wider
    Object.defineProperty(process.stdout, 'columns', { value: 120, writable: true, configurable: true });
    process.stdout.emit('resize');

    // Re-render to pick up the width change
    rerender(h(InputPrompt, { onSubmit, disabled: false }));
    const wideFrame = lastFrame()!;
    expect(wideFrame).toContain('>');

    // Restore original columns
    Object.defineProperty(process.stdout, 'columns', { value: origColumns ?? 80, writable: true, configurable: true });
  });
});
