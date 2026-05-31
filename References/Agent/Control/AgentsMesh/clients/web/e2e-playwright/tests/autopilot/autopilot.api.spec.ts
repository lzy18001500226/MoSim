// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Autopilot API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * TC-AUTOPILOT-001: List autopilot controllers
   */
  test("list autopilot controllers", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.autopilot.listAutopilotControllers({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(items)).toBe(true);
  });
});
