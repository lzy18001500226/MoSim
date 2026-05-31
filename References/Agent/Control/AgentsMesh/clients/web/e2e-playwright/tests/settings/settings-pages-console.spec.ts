import { test, expect } from "../../fixtures/index";
import { SettingsNavPage } from "../../pages/settings/settings-nav.page";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Settings Git & Notifications Pages", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("UI: git settings page loads without errors", async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
    await nav.goto("personal", "git");

    const body = await page.textContent("body");
    expect(body).toMatch(/git|credential|凭据|provider/i);

    const jsonErrors = consoleErrors.filter(
      (e) => e.includes("missing field") || e.includes("is not valid JSON")
    );
    expect(jsonErrors).toHaveLength(0);
  });

  test("UI: org billing settings page loads without errors", async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
    await nav.goto("organization", "billing");

    const body = await page.textContent("body");
    expect(body).toMatch(/billing|plan|subscription|订阅|付费/i);

    const jsonErrors = consoleErrors.filter(
      (e) => e.includes("missing field") || e.includes("is not valid JSON")
    );
    expect(jsonErrors).toHaveLength(0);
  });

  test("UI: org runners settings page loads without errors", async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
    await nav.goto("organization", "runners");

    const body = await page.textContent("body");
    expect(body).toMatch(/runner|token|运行器/i);

    const jsonErrors = consoleErrors.filter(
      (e) => e.includes("missing field") || e.includes("is not valid JSON")
    );
    expect(jsonErrors).toHaveLength(0);
  });
});
