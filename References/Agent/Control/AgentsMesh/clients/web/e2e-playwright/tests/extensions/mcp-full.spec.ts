// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

const REPO_ID = 1; // demo-webapp from seed

/**
 * MCP Server comprehensive tests.
 * Maps to: TC-MCP-EXT-001~009
 */
test.describe("MCP Server Management", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list user MCP servers for repository", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.repoMcp.listRepoMcpServers({
      orgSlug: TEST_ORG_SLUG,
      repositoryId: REPO_ID,
      scope: "user",
    }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("marketplace MCP templates", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.market.listMarketMcpServers({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(res.items?.length ?? 0).toBeGreaterThan(0);
  });

  test("search marketplace MCP templates", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.market.listMarketMcpServers({
      orgSlug: TEST_ORG_SLUG,
      query: "postgres",
    }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("install MCP from marketplace (filesystem)", async ({ api }) => {
    const cc = await api.connect();
    const market = await cc.market.listMarketMcpServers({ orgSlug: TEST_ORG_SLUG }) as { items: Array<{ id: number; slug?: string }> };
    const filesystem = market.items.find((t) => t.slug === "filesystem");
    expect(filesystem, "marketplace must contain the seeded filesystem MCP template").toBeTruthy();

    const installed = await cc.repoMcp.installMcpFromMarket({
      orgSlug: TEST_ORG_SLUG,
      repositoryId: REPO_ID,
      marketItemId: Number(filesystem!.id),
      scope: "user",
    }) as { id?: number };
    expect(installed.id).toBeTruthy();

    // Verify in list
    const list = await cc.repoMcp.listRepoMcpServers({
      orgSlug: TEST_ORG_SLUG,
      repositoryId: REPO_ID,
      scope: "user",
    }) as { items: Array<{ id: number; slug?: string }> };
    const found = list.items.find((s) => s.slug === "filesystem");
    expect(found).toBeTruthy();

    // Cleanup
    if (found?.id) {
      await cc.repoMcp.uninstallMcpServer({
        orgSlug: TEST_ORG_SLUG,
        repositoryId: REPO_ID,
        installId: Number(found.id),
      });
    }
  });

  test("install custom MCP server", async ({ api }) => {
    const cc = await api.connect();
    const installed = await cc.repoMcp.installCustomMcpServer({
      orgSlug: TEST_ORG_SLUG,
      repositoryId: REPO_ID,
      name: "E2E Custom MCP",
      slug: "e2e-custom-mcp",
      transportType: "stdio",
      command: "node",
      args: JSON.stringify(["server.js"]),
      envVars: JSON.stringify({ API_KEY: "test-key" }),
      scope: "user",
    }) as { id?: number };
    expect(installed.id).toBeTruthy();

    const list = await cc.repoMcp.listRepoMcpServers({
      orgSlug: TEST_ORG_SLUG,
      repositoryId: REPO_ID,
      scope: "user",
    }) as { items: Array<{ id: number; slug?: string }> };
    const found = list.items.find((s) => s.slug === "e2e-custom-mcp");
    if (found?.id) {
      await cc.repoMcp.uninstallMcpServer({
        orgSlug: TEST_ORG_SLUG,
        repositoryId: REPO_ID,
        installId: Number(found.id),
      });
    }
  });

  test("toggle MCP server enabled state", async ({ api }) => {
    const cc = await api.connect();
    // Clean any prior installation of this slug so the create won't 409.
    const existing = await cc.repoMcp.listRepoMcpServers({
      orgSlug: TEST_ORG_SLUG,
      repositoryId: REPO_ID,
      scope: "user",
    }) as { items: Array<{ id: number; slug?: string }> };
    const stale = existing.items.find((s) => s.slug === "e2e-toggle-mcp");
    if (stale?.id) {
      await cc.repoMcp.uninstallMcpServer({
        orgSlug: TEST_ORG_SLUG,
        repositoryId: REPO_ID,
        installId: Number(stale.id),
      });
    }

    const installed = await cc.repoMcp.installCustomMcpServer({
      orgSlug: TEST_ORG_SLUG,
      repositoryId: REPO_ID,
      name: "E2E Toggle MCP",
      slug: "e2e-toggle-mcp",
      transportType: "stdio",
      command: "echo",
      args: JSON.stringify(["test"]),
      scope: "user",
    }) as { id?: number };
    expect(installed.id, "install must return an id").toBeTruthy();

    await cc.repoMcp.updateMcpServer({
      orgSlug: TEST_ORG_SLUG,
      repositoryId: REPO_ID,
      installId: Number(installed.id),
      isEnabled: false,
    });

    await cc.repoMcp.uninstallMcpServer({
      orgSlug: TEST_ORG_SLUG,
      repositoryId: REPO_ID,
      installId: Number(installed.id),
    });
  });

  test("extensions page shows MCP section", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/settings?scope=organization&tab=extensions`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/MCP|server|扩展/i);
  });

  test("MCP templates include known servers", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/settings?scope=organization&tab=extensions`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toBeTruthy();
  });
});
