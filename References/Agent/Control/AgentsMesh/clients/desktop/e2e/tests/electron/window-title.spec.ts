import { test, expect } from "../../fixtures";

test.describe("Electron · window", () => {
  test("main window title matches AgentsMesh", async ({ page }) => {
    expect(await page.title()).toMatch(/AgentsMesh/);
  });

  test("renderer viewport is at least the declared minimum", async ({ page }) => {
    const size = await page.evaluate(() => ({
      w: window.innerWidth,
      h: window.innerHeight,
    }));
    expect(size.w).toBeGreaterThanOrEqual(800);
    expect(size.h).toBeGreaterThanOrEqual(500);
  });
});
