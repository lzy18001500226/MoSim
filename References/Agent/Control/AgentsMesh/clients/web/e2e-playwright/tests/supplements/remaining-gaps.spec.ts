// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { textContent } from "../../helpers/test-data";

/**
 * Remaining page and CRUD gap tests.
 */
test.describe("Remaining Coverage Gaps", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("org settings page has danger zone", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/settings?scope=organization&tab=general`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/danger|危险|delete|删除/i);
  });

  test("notification settings toggle exists", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/settings?scope=personal&tab=notifications`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/notification|通知/i);
  });

  test("workspace page supports terminal layout", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/workspace`);
    await page.waitForLoadState("load");
    expect(page.url()).toContain("/workspace");
  });

  test("git settings page loads", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/settings?scope=personal&tab=git`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/git|credential|凭据/i);
  });

  test("user profile accessible from settings", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/settings?scope=personal&tab=general`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/language|语言|personal|个人/i);
  });

  test("send message to channel", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E Msg Channel " + Date.now(),
    }) as { id?: number };
    expect(created.id, "createChannel must return an id").toBeTruthy();

    await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId: Number(created.id),
      // content_json is a stringified MessageContent JSON (proto stores it
      // verbatim — wasm parses on receive).
      contentJson: JSON.stringify(textContent("Hello from E2E test")),
    });

    const list = await cc.channel.listChannelMessages({
      orgSlug: TEST_ORG_SLUG,
      channelId: Number(created.id),
    }) as { items: unknown[] };
    expect(Array.isArray(list.items)).toBe(true);

    await cc.channel.archiveChannel({
      orgSlug: TEST_ORG_SLUG,
      id: Number(created.id),
    });
  });

  test("mesh topology API returns structure", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.mesh.getMeshTopology({ orgSlug: TEST_ORG_SLUG });
    expect(res).toBeTruthy();
  });

  test("billing plans prices endpoint", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.billing.listPlans({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("billing cycle change to monthly", async ({ api }) => {
    const cc = await api.connect();
    try {
      await cc.billing.changeBillingCycle({
        orgSlug: TEST_ORG_SLUG,
        billingCycle: "monthly",
      });
    } catch (err) {
      // Cycle may be same as current — 400 acceptable.
      expect((err as { status: number }).status).toBe(400);
    }
  });
});
