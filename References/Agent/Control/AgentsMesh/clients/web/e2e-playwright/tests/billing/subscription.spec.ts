// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Billing Subscription", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * TC-SUB-001: Get subscription status
   */
  test("get subscription status", async ({ api }) => {
    const cc = await api.connect();
    const sub = await cc.billing.getSubscription({ orgSlug: TEST_ORG_SLUG }) as { id?: number };
    expect(sub).toBeTruthy();
  });

  /**
   * TC-SUB-001: Subscription status UI display
   */
  test("billing settings page shows subscription info", async ({ page }) => {
    await page.goto(
      `/${TEST_ORG_SLUG}/settings?scope=organization&tab=billing`
    );
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/pro|free|enterprise|plan|订阅|方案/i);
  });

  /**
   * TC-SUB-002: Get available plans
   */
  test("list available plans", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.billing.listPlans({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(items)).toBe(true);
  });

  /**
   * TC-SUB-005: Reactivate subscription (may fail if not cancelled)
   */
  test("reactivate returns appropriate status", async ({ api }) => {
    const cc = await api.connect();
    // 200 if was cancelled, 400 if active — both valid.
    await cc.billing.reactivateSubscription({ orgSlug: TEST_ORG_SLUG }).catch((err: { status?: number }) => {
      expect(err.status).toBe(400);
    });
  });

  /**
   * TC-SUB-007: Auto-renew toggle
   */
  test("toggle auto-renew setting", async ({ api }) => {
    const cc = await api.connect();
    await cc.billing.updateAutoRenew({
      orgSlug: TEST_ORG_SLUG,
      autoRenew: true,
    }).catch((err: { status?: number }) => {
      expect([400, 404]).toContain(err.status);
    });
  });
});
