// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Autopilot Detail Page", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("API: list autopilot controllers", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.autopilot.listAutopilotControllers({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(items)).toBe(true);
  });

  test("UI: mesh page with autopilot loads without errors", async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    await page.goto(`/${TEST_ORG_SLUG}/mesh`);
    await page.waitForLoadState("load");

    const jsonErrors = consoleErrors.filter(
      (e) => e.includes("missing field") || e.includes("is not valid JSON")
    );
    expect(jsonErrors).toHaveLength(0);
  });
});
