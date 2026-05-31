// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { SettingsNavPage } from "../../pages/settings/settings-nav.page";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Organization Extensions Settings", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("API: list skill registries", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.skillRegistry.listSkillRegistries({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(items)).toBe(true);
  });

  test("API: list skill registry overrides", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.skillRegistry.listSkillRegistryOverrides({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(items)).toBe(true);
  });

  test("UI: extensions settings page loads without errors", async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
    await nav.goto("organization", "extensions");

    const body = await page.textContent("body");
    expect(body).toMatch(/extension|registry|扩展|注册/i);

    const jsonErrors = consoleErrors.filter(
      (e) => e.includes("missing field") || e.includes("is not valid JSON")
    );
    expect(jsonErrors).toHaveLength(0);
  });
});
