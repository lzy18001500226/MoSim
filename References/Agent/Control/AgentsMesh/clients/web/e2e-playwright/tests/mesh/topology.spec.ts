// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Mesh Topology API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * TC-MESH-001: Get mesh topology (empty or populated)
   */
  test("get mesh topology returns structure", async ({ api }) => {
    const cc = await api.connect();
    const topology = await cc.mesh.getMeshTopology({ orgSlug: TEST_ORG_SLUG }) as {
      nodes: unknown[]; edges: unknown[]; channels: unknown[]; runners: unknown[];
    };
    expect(topology).toBeTruthy();
    expect(Array.isArray(topology.nodes)).toBe(true);
    expect(Array.isArray(topology.edges)).toBe(true);
  });

  /**
   * TC-MESH-001: Mesh page loads in UI
   */
  test("mesh page loads correctly", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/mesh`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/mesh|topology|网格|拓扑/i);
  });
});
