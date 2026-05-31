import { test, expect } from "../../fixtures/index";
import { SettingsNavPage } from "../../pages/settings/settings-nav.page";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Organization Usage Settings", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("UI: usage settings page loads without errors", async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
    await nav.goto("organization", "usage");

    const body = await page.textContent("body");
    expect(body).toMatch(/usage|token|用量|消耗/i);

    const jsonErrors = consoleErrors.filter(
      (e) => e.includes("missing field") || e.includes("is not valid JSON")
    );
    expect(jsonErrors).toHaveLength(0);
  });
});
