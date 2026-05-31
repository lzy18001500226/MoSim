import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

/**
 * Journey: Organization Management UI
 *
 * The raw-REST lifecycle journey (invite → accept → role-change → remove)
 * was deleted alongside the REST handlers — invitation operations now
 * round-trip through `proto.invitation.v1.InvitationService`, which the
 * Playwright ApiFixture (a JSON fetch wrapper) cannot drive. Coverage:
 * connect handler unit tests + service integration tests + the UI test
 * below.
 */
test.describe("Journey: Organization Management", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("org settings visible in UI", async ({ page }) => {
    await page.goto(
      `/${TEST_ORG_SLUG}/settings?scope=organization&tab=general`
    );
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/Dev Organization|dev-org|organization|组织/i);

    await page.goto(
      `/${TEST_ORG_SLUG}/settings?scope=organization&tab=members`
    );
    await page.waitForLoadState("load");
    const membersBody = await page.textContent("body");
    expect(membersBody).toMatch(/member|成员|invite|邀请/i);
  });
});
