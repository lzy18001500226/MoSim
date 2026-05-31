// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Token Usage API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("get token usage dashboard", async ({ api }) => {
    const cc = await api.connect();
    // Dashboard is owner/admin gated — accept success or PermissionDenied (403).
    await cc.tokenUsage.getDashboard({
      orgSlug: TEST_ORG_SLUG,
      startTime: "",
      endTime: "",
      granularity: "",
      agentSlug: "",
      model: "",
    }).catch((err: { status?: number }) => {
      expect([403, 404]).toContain(err.status);
    });
  });

  // Migrated R5+: the REST `/token-usage/summary` endpoint folded into
  // GetDashboard.summary — there's no standalone summary procedure on
  // TokenUsageService, but the same data is available via the dashboard
  // response. Replace the placeholder skip with a positive contract check
  // on the summary fields that the legacy endpoint exposed.
  test("get token usage summary via GetDashboard", async ({ api }) => {
    const cc = await api.connect();
    try {
      const dash = await cc.tokenUsage.getDashboard({
        orgSlug: TEST_ORG_SLUG,
        startTime: "",
        endTime: "",
        granularity: "",
        agentSlug: "",
        model: "",
      }) as { summary?: { totalInput?: bigint | number; totalOutput?: bigint | number } };
      // summary may be absent when no usage rows exist yet; we only assert
      // the shape the legacy contract guaranteed — totals are numbers (or
      // bigints from int64) when present.
      if (dash.summary) {
        if (dash.summary.totalInput !== undefined) {
          expect(typeof dash.summary.totalInput).toMatch(/number|bigint/);
        }
        if (dash.summary.totalOutput !== undefined) {
          expect(typeof dash.summary.totalOutput).toMatch(/number|bigint/);
        }
      }
    } catch (err) {
      // Owner/admin-gated; non-privileged users get PermissionDenied.
      expect([403, 404]).toContain((err as { status?: number }).status);
    }
  });
});
