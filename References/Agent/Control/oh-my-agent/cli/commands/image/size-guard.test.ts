import { describe, expect, it } from "vitest";
import { validateSize } from "./size-guard.js";

describe("validateSize", () => {
  it("accepts auto", () => {
    expect(validateSize("auto")).toEqual({ ok: true, size: "auto" });
  });

  it("accepts gpt-image-1 canonical sizes", () => {
    for (const s of ["1024x1024", "1024x1536", "1536x1024"]) {
      const r = validateSize(s);
      expect(r.ok).toBe(true);
      if (r.ok) expect(r.size).toBe(s);
    }
  });

  it("accepts 512x512 (16-multiple, 1:1)", () => {
    expect(validateSize("512x512")).toEqual({ ok: true, size: "512x512" });
  });

  it("accepts 2048x768 (3:1 edge of allowed aspect range)", () => {
    expect(validateSize("2304x768")).toEqual({
      ok: true,
      size: "2304x768",
    });
  });

  it("rejects non-WxH strings", () => {
    const r = validateSize("1024");
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.reason).toMatch(/WxH/);
  });

  it("rejects values not aligned to 16", () => {
    const r = validateSize("500x500");
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.reason).toMatch(/multiples of 16/);
  });

  it("rejects below minimum edge", () => {
    const r = validateSize("0x16");
    expect(r.ok).toBe(false);
  });

  it("rejects above max edge", () => {
    const r = validateSize("4096x1024");
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.reason).toMatch(/3840/);
  });

  it("rejects aspect ratio outside 1:3..3:1", () => {
    const r = validateSize("16x1024");
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.reason).toMatch(/aspect ratio/);
  });
});
