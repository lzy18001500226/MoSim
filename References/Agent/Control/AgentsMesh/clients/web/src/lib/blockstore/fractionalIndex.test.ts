import { describe, expect, it } from "vitest";

import { keyAfter, keyBefore, keyBetween } from "./fractionalIndex";

describe("fractionalIndex", () => {
  it("returns a key that sorts strictly between inputs", () => {
    const mid = keyBetween("a0", "a2");
    expect(mid > "a0").toBe(true);
    expect(mid < "a2").toBe(true);
  });

  it("keyAfter appends past the last key", () => {
    const first = keyAfter(null);
    const next = keyAfter(first);
    expect(next > first).toBe(true);
  });

  it("keyBefore prepends before the first key", () => {
    const last = keyBefore(null);
    const prior = keyBefore(last);
    expect(prior < last).toBe(true);
  });

  it("supports adjacent digits by extending the key", () => {
    // "a0" and "a1" are adjacent — keyBetween must produce a longer key.
    const mid = keyBetween("a0", "a1");
    expect(mid > "a0").toBe(true);
    expect(mid < "a1").toBe(true);
    expect(mid.length).toBeGreaterThan(2);
  });

  it("throws when a >= b", () => {
    expect(() => keyBetween("b", "a")).toThrow();
  });
});
