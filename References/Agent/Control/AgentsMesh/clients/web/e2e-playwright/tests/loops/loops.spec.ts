// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Loops API & UI", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list loops", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.loop.listLoops({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(items)).toBe(true);
  });

  test("loops page loads in UI", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/loops`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/loop|循环|定时/i);
  });
});
