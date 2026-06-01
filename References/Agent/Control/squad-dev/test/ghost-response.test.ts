/**
 * Ghost Response Detection & Retry Tests
 *
 * Validates that empty responses from sendAndWait (ghost responses) are
 * detected and retried with exponential backoff.
 *
 * Ghost responses occur when session.idle fires before assistant.message,
 * causing sendAndWait() to return undefined or empty content.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  withGhostRetry,
  type GhostRetryOptions,
} from '../packages/squad-cli/src/cli/shell/index.js';

// ============================================================================
// withGhostRetry — unit tests
// ============================================================================

describe('withGhostRetry — returns immediately on success', () => {
  it('returns first result when non-empty', async () => {
    const sendFn = vi.fn().mockResolvedValue('Hello world');
    const result = await withGhostRetry(sendFn);

    expect(result).toBe('Hello world');
    expect(sendFn).toHaveBeenCalledTimes(1);
  });

  it('does not call onRetry or onExhausted on success', async () => {
    const onRetry = vi.fn();
    const onExhausted = vi.fn();
    const sendFn = vi.fn().mockResolvedValue('content');

    await withGhostRetry(sendFn, { onRetry, onExhausted });

    expect(onRetry).not.toHaveBeenCalled();
    expect(onExhausted).not.toHaveBeenCalled();
  });
});

describe('withGhostRetry — retries on empty response', () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => { vi.useRealTimers(); });

  it('retries and succeeds on second attempt', async () => {
    const sendFn = vi.fn()
      .mockResolvedValueOnce('')
      .mockResolvedValueOnce('recovered');
    const onRetry = vi.fn();

    const promise = withGhostRetry(sendFn, {
      backoffMs: [10, 20, 40],
      onRetry,
    });
    // Advance past first backoff
    await vi.advanceTimersByTimeAsync(10);
    const result = await promise;

    expect(result).toBe('recovered');
    expect(sendFn).toHaveBeenCalledTimes(2);
    expect(onRetry).toHaveBeenCalledWith(1, 3);
  });

  it('retries and succeeds on third attempt', async () => {
    const sendFn = vi.fn()
      .mockResolvedValueOnce('')
      .mockResolvedValueOnce('')
      .mockResolvedValueOnce('finally');

    const promise = withGhostRetry(sendFn, { backoffMs: [10, 20, 40] });
    await vi.advanceTimersByTimeAsync(10);
    await vi.advanceTimersByTimeAsync(20);
    const result = await promise;

    expect(result).toBe('finally');
    expect(sendFn).toHaveBeenCalledTimes(3);
  });
});

describe('withGhostRetry — exhaustion', () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => { vi.useRealTimers(); });

  it('returns empty and calls onExhausted after all retries fail', async () => {
    const sendFn = vi.fn().mockResolvedValue('');
    const onExhausted = vi.fn();
    const onRetry = vi.fn();

    const promise = withGhostRetry(sendFn, {
      maxRetries: 3,
      backoffMs: [10, 20, 40],
      onRetry,
      onExhausted,
    });
    // Advance past all backoffs
    await vi.advanceTimersByTimeAsync(10);
    await vi.advanceTimersByTimeAsync(20);
    await vi.advanceTimersByTimeAsync(40);
    const result = await promise;

    expect(result).toBe('');
    expect(sendFn).toHaveBeenCalledTimes(4); // 1 initial + 3 retries
    expect(onRetry).toHaveBeenCalledTimes(3);
    expect(onRetry).toHaveBeenCalledWith(1, 3);
    expect(onRetry).toHaveBeenCalledWith(2, 3);
    expect(onRetry).toHaveBeenCalledWith(3, 3);
    expect(onExhausted).toHaveBeenCalledWith(3);
  });

  it('respects custom maxRetries', async () => {
    const sendFn = vi.fn().mockResolvedValue('');
    const onExhausted = vi.fn();

    const promise = withGhostRetry(sendFn, {
      maxRetries: 1,
      backoffMs: [10],
      onExhausted,
    });
    await vi.advanceTimersByTimeAsync(10);
    const result = await promise;

    expect(result).toBe('');
    expect(sendFn).toHaveBeenCalledTimes(2); // 1 initial + 1 retry
    expect(onExhausted).toHaveBeenCalledWith(1);
  });
});

describe('withGhostRetry — debug logging', () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => { vi.useRealTimers(); });

  it('logs ghost response metadata on retry', async () => {
    const log = vi.fn();
    const sendFn = vi.fn()
      .mockResolvedValueOnce('')
      .mockResolvedValueOnce('ok');

    const promise = withGhostRetry(sendFn, {
      backoffMs: [10],
      debugLog: log,
      promptPreview: 'fix the streaming pipeline',
    });
    await vi.advanceTimersByTimeAsync(10);
    await promise;

    expect(log).toHaveBeenCalledWith(
      'ghost response detected',
      expect.objectContaining({
        attempt: 1,
        promptPreview: 'fix the streaming pipeline',
        timestamp: expect.any(String),
      }),
    );
  });

  it('logs exhaustion metadata when all retries fail', async () => {
    const log = vi.fn();
    const sendFn = vi.fn().mockResolvedValue('');

    const promise = withGhostRetry(sendFn, {
      maxRetries: 1,
      backoffMs: [10],
      debugLog: log,
      promptPreview: 'a very long prompt that should be truncated to eighty characters for the debug log entry preview field',
    });
    await vi.advanceTimersByTimeAsync(10);
    await promise;

    expect(log).toHaveBeenCalledWith(
      'ghost response: all retries exhausted',
      expect.objectContaining({
        promptPreview: expect.any(String),
      }),
    );
    // Verify truncation to 80 chars
    const exhaustedCall = log.mock.calls.find(
      (c: unknown[]) => c[0] === 'ghost response: all retries exhausted',
    );
    expect(exhaustedCall).toBeDefined();
    expect((exhaustedCall![1] as { promptPreview: string }).promptPreview.length).toBeLessThanOrEqual(80);
  });
});

describe('withGhostRetry — exponential backoff', () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => { vi.useRealTimers(); });

  it('uses default backoff timings 1s, 2s, 4s', async () => {
    const timestamps: number[] = [];
    const sendFn = vi.fn(async () => {
      timestamps.push(Date.now());
      return '';
    });

    const promise = withGhostRetry(sendFn);
    // Total backoff: 1000 + 2000 + 4000 = 7000ms
    await vi.advanceTimersByTimeAsync(7000);
    await promise;

    expect(timestamps).toHaveLength(4); // 1 initial + 3 retries
    const deltas = timestamps.map((t, i) => i === 0 ? 0 : t - timestamps[i - 1]!);
    expect(deltas[0]).toBe(0);      // immediate first attempt
    expect(deltas[1]).toBe(1000);   // 1s backoff
    expect(deltas[2]).toBe(2000);   // 2s backoff
    expect(deltas[3]).toBe(4000);   // 4s backoff
  });
});

// ============================================================================
// Integration: simulated dispatch with ghost retry
// ============================================================================

type EventHandler = (event: { type: string; [key: string]: unknown }) => void;

interface MockSquadSession {
  sendAndWait: ReturnType<typeof vi.fn>;
  on: ReturnType<typeof vi.fn>;
  off: ReturnType<typeof vi.fn>;
  _listeners: Map<string, Set<EventHandler>>;
  _emit: (eventName: string, event: { type: string; [key: string]: unknown }) => void;
}

function createGhostMockSession(responses: Array<{ deltas: string[]; fallback?: string }>): MockSquadSession {
  const listeners = new Map<string, Set<EventHandler>>();
  let callCount = 0;

  const session: MockSquadSession = {
    _listeners: listeners,
    on: vi.fn((event: string, handler: EventHandler) => {
      if (!listeners.has(event)) listeners.set(event, new Set());
      listeners.get(event)!.add(handler);
    }),
    off: vi.fn((event: string, handler: EventHandler) => {
      listeners.get(event)?.delete(handler);
    }),
    _emit(eventName: string, event: { type: string; [key: string]: unknown }) {
      for (const handler of listeners.get(eventName) ?? []) {
        handler(event);
      }
    },
    sendAndWait: vi.fn(async () => {
      const response = responses[callCount] ?? { deltas: [], fallback: undefined };
      callCount++;
      for (const d of response.deltas) {
        session._emit('message_delta', { type: 'message_delta', deltaContent: d });
      }
      if (response.fallback !== undefined) {
        return { data: { content: response.fallback } };
      }
      return undefined;
    }),
  };

  return session;
}

/** Mirrors the dispatch logic from index.ts — send + accumulate + ghost retry. */
async function simulateDispatchWithRetry(
  session: MockSquadSession,
  message: string,
  options?: GhostRetryOptions,
): Promise<string> {
  let accumulated = '';

  const onDelta = (event: { type: string; [key: string]: unknown }): void => {
    const val = event['deltaContent'] ?? event['delta'] ?? event['content'];
    const delta = typeof val === 'string' ? val : '';
    if (!delta) return;
    accumulated += delta;
  };

  session.on('message_delta', onDelta);

  try {
    accumulated = await withGhostRetry(async () => {
      accumulated = '';
      const result = await session.sendAndWait({ prompt: message }, 600000);
      const data = (result as Record<string, unknown> | undefined)?.['data'] as Record<string, unknown> | undefined;
      const fallback = typeof data?.['content'] === 'string' ? data['content'] as string : '';
      if (!accumulated && fallback) accumulated = fallback;
      return accumulated;
    }, { backoffMs: [10, 20, 40], ...options });
  } finally {
    try { session.off('message_delta', onDelta); } catch { /* ignore */ }
  }

  return accumulated;
}

describe('Ghost response — integration with dispatch simulation', () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => { vi.useRealTimers(); });

  it('returns content on first attempt with no ghost', async () => {
    const session = createGhostMockSession([
      { deltas: ['Hello', ' world'] },
    ]);
    const result = await simulateDispatchWithRetry(session, 'say hello');

    expect(result).toBe('Hello world');
    expect(session.sendAndWait).toHaveBeenCalledTimes(1);
  });

  it('detects ghost and retries successfully', async () => {
    const session = createGhostMockSession([
      { deltas: [] },                        // ghost: no deltas, no fallback
      { deltas: ['recovered content'] },      // success on retry
    ]);
    const onRetry = vi.fn();

    const promise = simulateDispatchWithRetry(session, 'test', { onRetry });
    await vi.advanceTimersByTimeAsync(10);
    const result = await promise;

    expect(result).toBe('recovered content');
    expect(session.sendAndWait).toHaveBeenCalledTimes(2);
    expect(onRetry).toHaveBeenCalledWith(1, 3);
  });

  it('uses fallback content to avoid false ghost detection', async () => {
    const session = createGhostMockSession([
      { deltas: [], fallback: 'fallback response' },
    ]);
    const result = await simulateDispatchWithRetry(session, 'test');

    expect(result).toBe('fallback response');
    expect(session.sendAndWait).toHaveBeenCalledTimes(1);
  });

  it('reports all retry attempts then shows exhaustion message', async () => {
    const session = createGhostMockSession([
      { deltas: [] },
      { deltas: [] },
      { deltas: [] },
      { deltas: [] },
    ]);
    const onRetry = vi.fn();
    const onExhausted = vi.fn();

    const promise = simulateDispatchWithRetry(session, 'test', { onRetry, onExhausted });
    await vi.advanceTimersByTimeAsync(10);
    await vi.advanceTimersByTimeAsync(20);
    await vi.advanceTimersByTimeAsync(40);
    const result = await promise;

    expect(result).toBe('');
    expect(session.sendAndWait).toHaveBeenCalledTimes(4);
    expect(onRetry).toHaveBeenCalledTimes(3);
    expect(onExhausted).toHaveBeenCalledWith(3);
  });

  it('ghost on first two attempts, success on third', async () => {
    const session = createGhostMockSession([
      { deltas: [] },
      { deltas: [] },
      { deltas: ['third', ' time'] },
    ]);

    const promise = simulateDispatchWithRetry(session, 'persist');
    await vi.advanceTimersByTimeAsync(10);
    await vi.advanceTimersByTimeAsync(20);
    const result = await promise;

    expect(result).toBe('third time');
    expect(session.sendAndWait).toHaveBeenCalledTimes(3);
  });
});
