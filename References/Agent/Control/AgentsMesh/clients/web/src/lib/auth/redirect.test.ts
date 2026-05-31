import { describe, it, expect } from "vitest";
import { safeRedirectPath, loginUrlWithRedirect } from "./redirect";

describe("safeRedirectPath", () => {
  it("accepts a regular relative path", () => {
    expect(safeRedirectPath("/popout/terminal/abc")).toBe("/popout/terminal/abc");
  });

  it("preserves query strings", () => {
    expect(safeRedirectPath("/runners/authorize?key=xyz")).toBe("/runners/authorize?key=xyz");
  });

  it("preserves hash fragments", () => {
    expect(safeRedirectPath("/dashboard#section")).toBe("/dashboard#section");
  });

  it("rejects protocol-relative `//host` (cross-origin escape)", () => {
    expect(safeRedirectPath("//evil.com/path")).toBeNull();
  });

  it("rejects `/\\host` (browser-normalized protocol-relative)", () => {
    expect(safeRedirectPath("/\\evil.com")).toBeNull();
  });

  it("rejects absolute http/https URLs", () => {
    expect(safeRedirectPath("https://evil.com")).toBeNull();
    expect(safeRedirectPath("http://evil.com")).toBeNull();
  });

  it("rejects javascript: scheme", () => {
    expect(safeRedirectPath("javascript:alert(1)")).toBeNull();
  });

  it("rejects data: scheme", () => {
    expect(safeRedirectPath("data:text/html,<script>")).toBeNull();
  });

  it("rejects empty string", () => {
    expect(safeRedirectPath("")).toBeNull();
  });

  it("rejects null and undefined", () => {
    expect(safeRedirectPath(null)).toBeNull();
    expect(safeRedirectPath(undefined)).toBeNull();
  });

  it("rejects bare relative paths (must start with /)", () => {
    expect(safeRedirectPath("popout/x")).toBeNull();
  });
});

describe("loginUrlWithRedirect", () => {
  it("encodes the target in the redirect query param", () => {
    expect(loginUrlWithRedirect("/popout/terminal/abc?x=1")).toBe(
      "/login?redirect=%2Fpopout%2Fterminal%2Fabc%3Fx%3D1"
    );
  });

  it("falls back to bare /login when target is unsafe", () => {
    expect(loginUrlWithRedirect("https://evil.com")).toBe("/login");
    expect(loginUrlWithRedirect("//evil.com")).toBe("/login");
    expect(loginUrlWithRedirect("")).toBe("/login");
  });
});
