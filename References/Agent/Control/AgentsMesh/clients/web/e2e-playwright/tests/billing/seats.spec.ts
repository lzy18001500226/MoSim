// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Billing Seats", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * TC-SEAT-001: Get seat info
   */
  test("get seat information", async ({ api }) => {
    const cc = await api.connect();
    const seats = await cc.billing.getSeatUsage({ orgSlug: TEST_ORG_SLUG }) as { totalSeats?: number };
    expect(seats).toBeTruthy();
  });

  /**
   * TC-SEAT-004: Purchase seats (may fail due to payment requirement)
   */
  test("purchase seats returns appropriate status", async ({ api }) => {
    const cc = await api.connect();
    // 200 if seats added, 400/402 if payment needed or limit.
    await cc.billing.purchaseSeats({
      orgSlug: TEST_ORG_SLUG,
      seats: 1,
    }).catch((err: { status?: number }) => {
      expect([400, 402]).toContain(err.status);
    });
  });
});
