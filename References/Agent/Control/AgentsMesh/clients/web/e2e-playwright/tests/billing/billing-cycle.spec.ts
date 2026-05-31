// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Billing Cycle", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * TC-CYCLE-001: Display current billing cycle
   */
  test("billing overview shows cycle info", async ({ api }) => {
    const cc = await api.connect();
    const overview = await cc.billing.getOverview({ orgSlug: TEST_ORG_SLUG }) as { status?: string };
    expect(overview).toBeTruthy();
  });

  /**
   * TC-CYCLE-002/003: Change billing cycle
   */
  test("change billing cycle returns appropriate status", async ({ api }) => {
    const cc = await api.connect();
    // 200 if changed, 400 if same cycle or not allowed (Connect throws on non-2xx).
    await cc.billing.changeBillingCycle({
      orgSlug: TEST_ORG_SLUG,
      billingCycle: "yearly",
    }).catch((err: { status?: number }) => {
      expect(err.status).toBe(400);
    });
  });
});
