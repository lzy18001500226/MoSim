import { describe, expect, it } from "vitest";

import { computeColumn } from "./computeColumn";

describe("computeColumn", () => {
  it("evaluates simple arithmetic", () => {
    expect(computeColumn("1 + 2", {})).toBe(3);
    expect(computeColumn("10 / 4", {})).toBe(2.5);
    expect(computeColumn("2 * 3 + 4", {})).toBe(10);
    expect(computeColumn("2 * (3 + 4)", {})).toBe(14);
  });

  it("substitutes column references", () => {
    expect(computeColumn("{done} / {total}", { done: 3, total: 4 })).toBe(0.75);
    expect(computeColumn("{a} + {b} * {c}", { a: 1, b: 2, c: 3 })).toBe(7);
  });

  it("missing refs default to 0 (no throw)", () => {
    expect(computeColumn("{missing} + 5", {})).toBe(5);
    expect(computeColumn("{missing} * {missing}", {})).toBe(0);
  });

  it("handles unary minus", () => {
    expect(computeColumn("-5 + 3", {})).toBe(-2);
    expect(computeColumn("-{v}", { v: 4 })).toBe(-4);
  });

  it("returns null on malformed input", () => {
    expect(computeColumn("1 + ", {})).toBeNull();
    expect(computeColumn("1 & 2", {})).toBeNull();
    expect(computeColumn("{unclosed", {})).toBeNull();
  });

  it("division by zero returns null (Infinity filtered)", () => {
    expect(computeColumn("1 / 0", {})).toBeNull();
  });
});
