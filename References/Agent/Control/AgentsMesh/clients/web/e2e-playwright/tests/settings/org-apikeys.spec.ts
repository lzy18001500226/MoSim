// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { SettingsNavPage } from "../../pages/settings/settings-nav.page";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Organization API Keys Settings", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("API: list api keys returns envelope", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.apikey.listApiKeys({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(items)).toBe(true);
  });

  test("API: create and delete api key", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.apikey.createApiKey({
      orgSlug: TEST_ORG_SLUG,
      name: `E2E Test Key ${Date.now()}`,
      scopes: ["pods:read"],
    }) as { apiKey: { id: number }; rawKey: string };
    expect(created.apiKey).toBeTruthy();
    expect(created.apiKey.id).toBeTruthy();
    expect(created.rawKey).toBeTruthy();

    await cc.apikey.deleteApiKey({ orgSlug: TEST_ORG_SLUG, id: created.apiKey.id });
  });

  test("UI: api keys settings page loads without errors", async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
    await nav.goto("organization", "api-keys");

    const body = await page.textContent("body");
    expect(body).toMatch(/API|key|密钥/i);

    const jsonErrors = consoleErrors.filter(
      (e) => e.includes("missing field") || e.includes("is not valid JSON")
    );
    expect(jsonErrors).toHaveLength(0);
  });
});
