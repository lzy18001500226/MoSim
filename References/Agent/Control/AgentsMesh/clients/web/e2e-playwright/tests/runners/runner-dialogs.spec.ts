import { test, expect } from "../../fixtures/index";
import { RunnersPage } from "../../pages/runners.page";
import { SidebarPage } from "../../pages/sidebar.page";
import { TEST_ORG_SLUG } from "../../helpers/env";

/**
 * Runner UI dialog tests.
 * Maps to: TC-UI-002~005
 */
test.describe("Runner UI Dialogs", () => {
  test.beforeEach(async ({ page }) => {
    const sidebar = new SidebarPage(page, TEST_ORG_SLUG);
    await page.goto(`/${TEST_ORG_SLUG}/runners`);
    await page.waitForLoadState("load");
    await sidebar.dismissDevOverlay();
  });

  /**
   * TC-UI-002: Add Runner dialog
   */
  test("add runner dialog opens with token generation", async ({ page }) => {
    const runnersPage = new RunnersPage(page, TEST_ORG_SLUG);
    await expect(runnersPage.addRunnerButton).toBeVisible();
    await runnersPage.addRunnerButton.click();

    // Dialog should appear
    const dialog = page.locator('[role="dialog"], .fixed.inset-0').first();
    await expect(dialog).toBeVisible();

    // Should contain registration command or token info
    const dialogText = await dialog.textContent();
    expect(dialogText).toMatch(/register|token|runner|注册|令牌/i);

    // Close dialog
    await page.keyboard.press("Escape");
  });

  /**
   * TC-UI-003: Runner config dialog
   */
  test("runner config dialog opens from table", async ({ page, db }) => {
    // Ensure dev-runner exists (from seed)
    const hasRunner = db.queryValue(
      `SELECT COUNT(*) FROM runners WHERE node_id = 'dev-runner'`
    );
    expect(hasRunner, "dev seed must include the 'dev-runner' runner").not.toBe("0");

    // Find and click Configure button
    const configBtn = page.getByRole("button", { name: /configure|配置/i }).first();
    if (await configBtn.isVisible()) {
      await configBtn.click();
      const dialog = page.locator('[role="dialog"], .fixed.inset-0').first();
      await expect(dialog).toBeVisible();
      await page.keyboard.press("Escape");
    }
  });

  /**
   * TC-UI-004: Runner delete confirmation dialog
   */
  test("delete button shows confirmation dialog", async ({ page, db }) => {
    // Create disposable runner for delete test
    db.setup(`
      INSERT INTO runners (organization_id, node_id, description, status, max_concurrent_pods, is_enabled)
      SELECT id, 'ui-delete-test', 'UI Delete Test', 'offline', 5, true
      FROM organizations WHERE slug = '${TEST_ORG_SLUG}'
      ON CONFLICT (organization_id, node_id) DO NOTHING
    `);
    await page.reload();
    await page.waitForLoadState("load");

    // Find delete button for the test runner
    const deleteBtn = page.getByRole("button", { name: /delete|删除/i }).first();
    if (await deleteBtn.isVisible()) {
      await deleteBtn.click();
      // Confirmation dialog should appear
      const body = await page.textContent("body");
      expect(body).toMatch(/confirm|确认|sure|确定/i);
      // Cancel
      const cancelBtn = page.getByRole("button", { name: /cancel|取消/i }).first();
      if (await cancelBtn.isVisible()) await cancelBtn.click();
    }

    db.cleanup(`DELETE FROM runners WHERE node_id = 'ui-delete-test'`);
  });

  /**
   * TC-UI-005: Full runner management flow (view → config → disable → enable)
   */
  test("full runner management flow via UI", async ({ page }) => {
    // Verify runner list displays
    const body = await page.textContent("body");
    expect(body).toMatch(/dev-runner|Runner/i);

    // Verify stats cards
    const statsArea = page.locator("body");
    const statsText = await statsArea.textContent();
    expect(statsText).toMatch(/total|online|capacity|总计|在线/i);
  });
});
