import { describe, expect, it } from "vitest";

import { keyAfter, keyBefore, keyBetween } from "./fractionalIndex";

// Regression pack covering edge cases that previously slipped through:
//   - long keys when repeatedly inserting adjacent
//   - prepend and append chains
//   - strict monotonicity under 100 random inserts

describe("fractionalIndex regression", () => {
  it("monotonic chain via keyAfter", () => {
    let last: string | null = null;
    const seen: string[] = [];
    for (let i = 0; i < 20; i++) {
      const next = keyAfter(last);
      if (last !== null) expect(next > last).toBe(true);
      seen.push(next);
      last = next;
    }
    expect(seen.length).toBe(20);
  });

  it("keyBefore chain stays strictly decreasing", () => {
    let first: string | null = null;
    for (let i = 0; i < 20; i++) {
      const next = keyBefore(first);
      if (first !== null) expect(next < first).toBe(true);
      first = next;
    }
  });

  it("repeated keyBetween with same pair grows the key length", () => {
    let mid = keyBetween("a0", "a1");
    const baseLen = mid.length;
    for (let i = 0; i < 8; i++) {
      const next = keyBetween("a0", mid);
      expect(next > "a0").toBe(true);
      expect(next < mid).toBe(true);
      mid = next;
    }
    expect(mid.length).toBeGreaterThan(baseLen);
  });

  it("random insertion maintains global sort order", () => {
    const keys: string[] = [keyAfter(null)];
    for (let i = 0; i < 100; i++) {
      const insertAt = Math.floor(Math.random() * (keys.length + 1));
      const before = insertAt > 0 ? keys[insertAt - 1] : null;
      const after = insertAt < keys.length ? keys[insertAt] : null;
      const k = keyBetween(before, after);
      keys.splice(insertAt, 0, k);
    }
    const sorted = [...keys].sort();
    expect(keys).toEqual(sorted);
    expect(new Set(keys).size).toBe(keys.length);
  });

  it("tolerates legacy keys containing chars outside BASE_CHARS", () => {
    // Agents and older clients occasionally wrote order_keys like "zzz-123"
    // or "m_foo" that contained ASCII chars outside the 0-9/a-z base. Before
    // the fix, keyAfter on such a key threw "invalid char in order_key",
    // which silently killed every subsequent insertChild. The walker now pins
    // non-base chars to the nearest BASE_CHARS endpoint instead of throwing.
    //
    // The primary invariant we need for the product (insertChild at end of
    // children): keyAfter never throws for a legacy key, and the returned
    // key is greater than the input under Postgres TEXT ordering.
    const dashedKey = "zzz-1776467610772";
    expect(() => keyAfter(dashedKey)).not.toThrow();
    const afterDashed = keyAfter(dashedKey);
    expect(afterDashed > dashedKey).toBe(true);

    const underscoreKey = "m_2024";
    expect(() => keyAfter(underscoreKey)).not.toThrow();
    const afterUnderscore = keyAfter(underscoreKey);
    expect(afterUnderscore > underscoreKey).toBe(true);
  });
});
