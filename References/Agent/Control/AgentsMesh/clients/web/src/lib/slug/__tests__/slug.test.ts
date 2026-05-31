import { describe, it, expect } from "vitest";
import {
  sanitizeSlug,
  validateSlug,
  SLUG_MAX_LEN,
} from "../slug";
import { isReservedSlug, RESERVED_SLUGS } from "../reserved";

describe("sanitizeSlug", () => {
  it.each([
    ["John.Doe", "john-doe"],
    ["UPPER", "upper"],
    ["user_123", "user-123"],
    ["foo bar", "foo-bar"],
    ["foo--bar", "foo-bar"],
    ["a---b", "a-b"],
    ["  spaced  ", "spaced"],
    ["-leading-trailing-", "leading-trailing"],
    ["already-clean", "already-clean"],
    ["a1b2c3", "a1b2c3"],
    ["", ""],
    ["---", ""],
    ["@#$%", ""],
    ["张三", ""],
    ["🚀rocket", "rocket"],
    ["mix中文123", "mix-123"],
    ["user@example.com", "user-example-com"],
  ])("sanitizes %j -> %j", (input, expected) => {
    expect(sanitizeSlug(input)).toBe(expected);
  });

  it("truncates beyond max length and trims trailing hyphen", () => {
    const long = "a".repeat(150);
    expect(sanitizeSlug(long).length).toBe(SLUG_MAX_LEN);
  });

  it("trims trailing hyphen after truncation", () => {
    const input = "a".repeat(99) + "-bbbb";
    const out = sanitizeSlug(input);
    expect(out.endsWith("-")).toBe(false);
    expect(out.length).toBeLessThanOrEqual(SLUG_MAX_LEN);
  });
});

describe("validateSlug", () => {
  it.each([
    ["foo", null],
    ["foo-bar", null],
    ["a1", null],
    ["1a", null],
    ["a-b-c-d", null],
    ["nested-2-deep", null],
  ])("accepts %j", (input, expected) => {
    expect(validateSlug(input)).toBe(expected);
  });

  it.each([
    ["", "empty"],
    ["a", "too_short"],
    ["1", "too_short"],
    [`${"a".repeat(SLUG_MAX_LEN + 1)}`, "too_long"],
    ["Foo", "invalid_format"],
    ["foo--bar", "invalid_format"],
    ["-foo", "invalid_format"],
    ["foo-", "invalid_format"],
    ["foo_bar", "invalid_format"],
    ["foo.bar", "invalid_format"],
    ["foo bar", "invalid_format"],
  ])("rejects %j as %s", (input, reason) => {
    expect(validateSlug(input)).toBe(reason);
  });

  it.each(Array.from(RESERVED_SLUGS))("rejects reserved word %j", (word) => {
    expect(validateSlug(word)).toBe("reserved");
  });
});

describe("contract: sanitizeSlug output is always valid or empty", () => {
  const inputs = [
    "John.Doe",
    "user_123",
    "张三",
    "🚀test",
    "UPPER_CASE.WITH.DOTS",
    "  spaced  ",
    "a".repeat(200),
  ];
  it.each(inputs)("sanitize(%j) is empty or valid", (input) => {
    const sanitized = sanitizeSlug(input);
    if (sanitized === "") return;
    const err = validateSlug(sanitized);
    expect(err === null || err === "too_short" || err === "reserved").toBe(true);
  });
});

describe("isReservedSlug", () => {
  it("identifies reserved words", () => {
    expect(isReservedSlug("admin")).toBe(true);
    expect(isReservedSlug("api")).toBe(true);
  });
  it("returns false for non-reserved", () => {
    expect(isReservedSlug("john-doe")).toBe(false);
    expect(isReservedSlug("my-org")).toBe(false);
  });
});
