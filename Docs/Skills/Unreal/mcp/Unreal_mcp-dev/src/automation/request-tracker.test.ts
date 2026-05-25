import { afterEach, describe, expect, it, vi } from 'vitest';
import { RequestTracker } from './request-tracker.js';

afterEach(() => {
  vi.useRealTimers();
});

describe('RequestTracker coalescing', () => {
  it('uses stable keys for equivalent nested payloads', () => {
    const tracker = new RequestTracker(10);

    const first = tracker.createCoalesceKey('get_actor', {
      filter: { tags: ['enemy', 'flying'], bounds: { z: 10, x: 1 } }
    });
    const second = tracker.createCoalesceKey('get_actor', {
      filter: { bounds: { x: 1, z: 10 }, tags: ['enemy', 'flying'] }
    });

    expect(first).toBe(second);
  });

  it('does not coalesce different nested payloads', () => {
    const tracker = new RequestTracker(10);

    const first = tracker.createCoalesceKey('get_actor', { filter: { bounds: { x: 1 } } });
    const second = tracker.createCoalesceKey('get_actor', { filter: { bounds: { x: 2 } } });

    expect(first).not.toBe(second);
  });

  it('does not coalesce mutating actions', () => {
    const tracker = new RequestTracker(10);

    expect(tracker.createCoalesceKey('set_actor_transform', { actor: 'Cube' })).toBe('');
  });

  it('clears absolute timeout when the request timeout fires', async () => {
    vi.useFakeTimers();
    const tracker = new RequestTracker(10);

    const { promise } = tracker.createRequest('get_actor', {}, 100);
    expect(vi.getTimerCount()).toBe(2);
    const rejection = expect(promise).rejects.toThrow(/timed out after 100ms/);

    await vi.advanceTimersByTimeAsync(100);

    await rejection;
    expect(tracker.getPendingCount()).toBe(0);
    expect(vi.getTimerCount()).toBe(0);
  });
});
