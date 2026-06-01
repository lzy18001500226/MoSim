import { describe, expect, it } from "vitest";
import { detectTrap } from "./detect-trap.js";

describe("detectTrap", () => {
  // Refusal — exitCode 2, ok false

  it("refuses demographic gift trap (year-old dad)", () => {
    // "birthday gift for 42 year old dad": "dad" is a relational noun so no escape
    const result = detectTrap({ topic: "birthday gift for 42 year old dad" });
    expect(result.ok).toBe(false);
    expect(result.exitCode).toBe(2);
    expect(result.reason).toBe("demographic-shopping");
  });

  it("refuses demographic gift trap (best headphones for husbands)", () => {
    const result = detectTrap({ topic: "best headphones for husbands" });
    expect(result.ok).toBe(false);
    expect(result.exitCode).toBe(2);
    expect(result.reason).toBe("demographic-shopping");
  });

  it("refuses demographic gift trap (what to buy for a 50 year old dad)", () => {
    const result = detectTrap({ topic: "what to buy for a 50 year old dad" });
    expect(result.ok).toBe(false);
    expect(result.exitCode).toBe(2);
    expect(result.reason).toBe("demographic-shopping");
  });

  it("refuses single-noun too-broad topic (sneakers)", () => {
    const result = detectTrap({ topic: "sneakers" });
    expect(result.ok).toBe(false);
    expect(result.exitCode).toBe(2);
    expect(result.reason).toBe("single-noun-too-broad");
  });

  // Pass — exitCode 0, ok true

  it("accepts qualifier escape (budget + hobby descriptor)", () => {
    const result = detectTrap({
      topic:
        "birthday gift for 42 year old coding obsessed husband, budget $200",
    });
    expect(result.ok).toBe(true);
    expect(result.exitCode).toBe(0);
  });

  it("accepts specific non-demographic topic (VS Code performance pain points)", () => {
    const result = detectTrap({ topic: "VS Code performance pain points" });
    expect(result.ok).toBe(true);
    expect(result.exitCode).toBe(0);
  });

  // Validation — exitCode 4

  it("rejects empty topic with reason empty", () => {
    const result = detectTrap({ topic: "" });
    expect(result.ok).toBe(false);
    expect(result.exitCode).toBe(4);
    expect(result.reason).toBe("empty");
  });

  it("rejects topic longer than 200 characters with reason too-long", () => {
    const result = detectTrap({ topic: "x".repeat(201) });
    expect(result.ok).toBe(false);
    expect(result.exitCode).toBe(4);
    expect(result.reason).toBe("too-long");
  });

  // Force bypass

  it("bypasses demographic refusal when force is true", () => {
    const result = detectTrap({
      topic: "birthday gift for 42 year old dad",
      force: true,
    });
    expect(result.ok).toBe(true);
    expect(result.exitCode).toBe(0);
  });
});
