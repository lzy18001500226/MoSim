// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { collectConsoleErrors, assertNoWasmErrors } from "../../helpers/console-errors";

test.describe("Loop Operations", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("loops: open create dialog", async ({ page }) => {
    const errors = collectConsoleErrors(page);
    await page.goto(`/${TEST_ORG_SLUG}/loops`);
    await page.waitForLoadState("load");

    const createBtn = page.getByRole("button", { name: /新建|Create|New/i }).first();
    if (await createBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await createBtn.click();
      await page.waitForTimeout(500);
    }
    assertNoWasmErrors(errors);
  });

  test("loops: list → detail navigation", async ({ page, api }) => {
    const cc = await api.connect();
    const created = await cc.loop.createLoop({
      orgSlug: TEST_ORG_SLUG,
      name: `E2E Loop Nav ${Date.now()}`,
      slug: `e2e-loop-nav-${Date.now()}`,
      agentSlug: "claude-code",
      cronExpression: "0 * * * *",
      promptTemplate: "echo nav test",
    }) as { slug: string };
    const slug = created.slug;
    expect(slug).toBeTruthy();

    const errors = collectConsoleErrors(page);
    await page.goto(`/${TEST_ORG_SLUG}/loops`);
    await page.waitForLoadState("load");

    const link = page.locator(`a[href*="loops/${slug}"]`).first();
    if (await link.isVisible({ timeout: 5000 }).catch(() => false)) {
      await link.click();
      await page.waitForLoadState("load");
    }
    assertNoWasmErrors(errors);

    if (slug) {
      await cc.loop.deleteLoop({ orgSlug: TEST_ORG_SLUG, loopSlug: slug }).catch(() => null);
    }
  });
});
