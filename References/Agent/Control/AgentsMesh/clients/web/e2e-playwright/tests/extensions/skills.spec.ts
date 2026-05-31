// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Extensions Skills API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list marketplace skills", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.market.listMarketSkills({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("extensions settings page loads", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/settings?scope=organization&tab=extensions`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/extension|skill|扩展|技能/i);
  });
});
