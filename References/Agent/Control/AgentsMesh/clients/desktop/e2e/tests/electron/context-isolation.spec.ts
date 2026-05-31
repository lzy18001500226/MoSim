import { test, expect } from "../../fixtures";

test.describe("Electron · context isolation", () => {
  test("node globals are NOT leaked to the renderer", async ({ page }) => {
    const leak = await page.evaluate(() => ({
      hasProcess: typeof (globalThis as unknown as { process?: unknown }).process !== "undefined",
      hasRequire: typeof (globalThis as unknown as { require?: unknown }).require !== "undefined",
      hasBuffer: typeof (globalThis as unknown as { Buffer?: unknown }).Buffer !== "undefined",
    }));
    expect(leak.hasProcess).toBe(false);
    expect(leak.hasRequire).toBe(false);
    expect(leak.hasBuffer).toBe(false);
  });
});
