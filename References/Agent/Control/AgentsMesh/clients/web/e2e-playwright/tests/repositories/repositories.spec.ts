// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Repositories API & UI", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list repositories", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.repository.listRepositories({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(items)).toBe(true);
  });

  test("repositories page loads in UI", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/repositories`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/repositor|仓库|代码库/i);
  });
});
