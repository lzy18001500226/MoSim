// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("MCP Servers API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list marketplace MCP servers", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.market.listMarketMcpServers({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("search marketplace MCP servers", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.market.listMarketMcpServers({
      orgSlug: TEST_ORG_SLUG,
      query: "postgres",
    }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("MCP settings tab loads", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/settings?scope=organization&tab=extensions`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/MCP|extension|扩展/i);
  });

  test("MCP templates page shows templates", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/settings?scope=organization&tab=extensions`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toBeTruthy();
  });
});
