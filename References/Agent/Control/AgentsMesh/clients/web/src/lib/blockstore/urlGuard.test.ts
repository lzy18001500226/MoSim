import { describe, expect, it } from "vitest";

import { isSafeURL, sanitizeURL } from "./urlGuard";

// Centralised URL guard — protects <iframe src>, <img src>, <a href> from
// javascript: and other non-http schemes that survive browser defaults in
// certain contexts. Every renderer that accepts user-authored URLs routes
// through these helpers.
describe("isSafeURL", () => {
  it("accepts http and https absolute URLs", () => {
    expect(isSafeURL("http://example.com")).toBe(true);
    expect(isSafeURL("https://example.com/path?q=1")).toBe(true);
  });

  it("rejects non-http schemes", () => {
    expect(isSafeURL("javascript:alert(1)")).toBe(false);
    expect(isSafeURL("data:text/html,<script>")).toBe(false);
    expect(isSafeURL("file:///etc/passwd")).toBe(false);
    expect(isSafeURL("vbscript:msgbox(1)")).toBe(false);
    expect(isSafeURL("mailto:foo@bar.com")).toBe(false);
  });

  it("rejects relative or malformed input", () => {
    expect(isSafeURL("")).toBe(false);
    expect(isSafeURL("not a url")).toBe(false);
    expect(isSafeURL("/relative/path")).toBe(false);
  });

  it("rejects non-string input", () => {
    // @ts-expect-error — guard handles runtime junk from user-authored data
    expect(isSafeURL(null)).toBe(false);
    // @ts-expect-error — guard handles runtime junk from user-authored data
    expect(isSafeURL(undefined)).toBe(false);
    // @ts-expect-error — guard handles runtime junk from user-authored data
    expect(isSafeURL(123)).toBe(false);
  });
});

describe("sanitizeURL", () => {
  it("returns the URL when safe", () => {
    expect(sanitizeURL("https://example.com")).toBe("https://example.com");
  });

  it("returns empty string for unsafe inputs", () => {
    expect(sanitizeURL("javascript:alert(1)")).toBe("");
    expect(sanitizeURL("")).toBe("");
  });
});
