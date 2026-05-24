import { afterEach, describe, expect, it, vi } from 'vitest';
import type { Logger } from './logger.js';
import { createElicitationHelper } from './elicitation.js';

describe('createElicitationHelper timeout env parsing', () => {
  const originalPrimary = process.env.MCP_ELICITATION_TIMEOUT_MS;
  const originalFallback = process.env.ELICITATION_TIMEOUT_MS;

  afterEach(() => {
    if (originalPrimary === undefined) {
      delete process.env.MCP_ELICITATION_TIMEOUT_MS;
    } else {
      process.env.MCP_ELICITATION_TIMEOUT_MS = originalPrimary;
    }

    if (originalFallback === undefined) {
      delete process.env.ELICITATION_TIMEOUT_MS;
    } else {
      process.env.ELICITATION_TIMEOUT_MS = originalFallback;
    }
  });

  it('rejects partial numeric timeout strings', () => {
    process.env.MCP_ELICITATION_TIMEOUT_MS = '120000ms';
    delete process.env.ELICITATION_TIMEOUT_MS;
    const helper = createElicitationHelper({}, { debug: vi.fn() } as unknown as Logger);

    expect(helper.getDefaultTimeoutMs()).toBe(180000);
  });

  it('accepts positive decimal integer timeout strings', () => {
    process.env.MCP_ELICITATION_TIMEOUT_MS = '120000';
    delete process.env.ELICITATION_TIMEOUT_MS;
    const helper = createElicitationHelper({}, { debug: vi.fn() } as unknown as Logger);

    expect(helper.getDefaultTimeoutMs()).toBe(120000);
  });
});
