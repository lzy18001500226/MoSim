import { test, expect } from "../../fixtures";

test.describe("Electron · storage persistence", () => {
  test("localStorage is populated after auth-state restore", async ({ page }) => {
    const keys = await page.evaluate(() => Object.keys(window.localStorage));
    const agentsmeshKeys = keys.filter((k) => k.startsWith("agentsmesh-"));
    expect(agentsmeshKeys.length).toBeGreaterThan(0);
  });

  test("can round-trip a custom value via localStorage", async ({ page }) => {
    const roundtripKey = "e2e-roundtrip-probe";
    const value = String(Date.now());
    await page.evaluate(({ k, v }) => window.localStorage.setItem(k, v), { k: roundtripKey, v: value });
    const read = await page.evaluate((k) => window.localStorage.getItem(k), roundtripKey);
    expect(read).toBe(value);
    await page.evaluate((k) => window.localStorage.removeItem(k), roundtripKey);
  });
});
