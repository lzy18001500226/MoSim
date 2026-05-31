import { test, expect } from "../../fixtures";

test.describe("App boot", () => {
  test("window title matches AgentsMesh", async ({ page }) => {
    expect(await page.title()).toMatch(/AgentsMesh/);
  });

  test("session is restored (already on dashboard)", async ({ page }) => {
    // global.setup logged in → userData + localStorage restored → no login page.
    const hash = await page.evaluate(() => window.location.hash);
    expect(hash).not.toContain("/login");
  });
});
