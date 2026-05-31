// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { collectConsoleErrors, assertNoWasmErrors } from "../../helpers/console-errors";

test.describe("Loop Detail Page", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  let createdSlug: string | null = null;

  test.afterEach(async ({ api }) => {
    if (createdSlug) {
      const cc = await api.connect();
      await cc.loop.deleteLoop({ orgSlug: TEST_ORG_SLUG, loopSlug: createdSlug }).catch(() => null);
      createdSlug = null;
    }
  });

  test("API: get loop detail returns entity", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.loop.createLoop({
      orgSlug: TEST_ORG_SLUG,
      name: `E2E Loop Detail ${Date.now()}`,
      slug: `e2e-loop-detail-${Date.now()}`,
      agentSlug: "claude-code",
      cronExpression: "0 * * * *",
      promptTemplate: "echo test",
    }) as { slug: string };
    createdSlug = created.slug;

    const loop = await cc.loop.getLoop({ orgSlug: TEST_ORG_SLUG, loopSlug: createdSlug }) as { slug: string };
    expect(loop.slug).toBe(createdSlug);
  });

  test("UI: loop detail page renders without errors", async ({ page, api }) => {
    const cc = await api.connect();
    const created = await cc.loop.createLoop({
      orgSlug: TEST_ORG_SLUG,
      name: `E2E Loop UI ${Date.now()}`,
      slug: `e2e-loop-ui-${Date.now()}`,
      agentSlug: "claude-code",
      cronExpression: "0 * * * *",
      promptTemplate: "echo test",
    }) as { slug: string };
    createdSlug = created.slug;

    const errors = collectConsoleErrors(page);
    await page.goto(`/${TEST_ORG_SLUG}/loops/${createdSlug}`);
    await page.waitForLoadState("load");
    assertNoWasmErrors(errors);
  });
});
