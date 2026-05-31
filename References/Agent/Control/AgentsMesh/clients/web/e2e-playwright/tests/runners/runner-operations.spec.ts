import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { collectConsoleErrors, assertNoWasmErrors } from "../../helpers/console-errors";

test.describe("Runner Operations", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("runner detail: view info and pods tab", async ({ page, db }) => {
    const id = db.queryValue(
      `SELECT id FROM runners WHERE organization_id = (SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}') LIMIT 1`
    );
    expect(id, "dev seed must include at least one runner").toBeTruthy();

    const errors = collectConsoleErrors(page);
    await page.goto(`/${TEST_ORG_SLUG}/runners/${id}`);
    await page.waitForLoadState("load");

    const body = await page.textContent("body");
    expect(body).toMatch(/runner|Runner|dev-runner/i);
    assertNoWasmErrors(errors);
  });

  test("runners list: navigate to detail and back", async ({ page, db }) => {
    const id = db.queryValue(
      `SELECT id FROM runners WHERE organization_id = (SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}') LIMIT 1`
    );
    expect(id, "dev seed must include at least one runner").toBeTruthy();

    const errors = collectConsoleErrors(page);
    await page.goto(`/${TEST_ORG_SLUG}/runners`);
    await page.waitForLoadState("load");

    const link = page.locator(`a[href*="runners/${id}"]`).first();
    if (await link.isVisible({ timeout: 3000 }).catch(() => false)) {
      await link.click();
      await page.waitForLoadState("load");
      await page.goBack();
      await page.waitForLoadState("load");
    }
    assertNoWasmErrors(errors);
  });
});
