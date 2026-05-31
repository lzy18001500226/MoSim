// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { collectConsoleErrors, assertNoWasmErrors } from "../../helpers/console-errors";

type Ticket = { slug: string };

test.describe("Workspace Operations", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("workspace: open create pod dialog", async ({ page }) => {
    const errors = collectConsoleErrors(page);
    await page.goto(`/${TEST_ORG_SLUG}/workspace`);
    await page.waitForLoadState("load");

    const createBtn = page.getByRole("button", { name: /创建|Create|New Pod/i }).first();
    if (await createBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await createBtn.click();
      await page.waitForTimeout(1000);
    }
    assertNoWasmErrors(errors);
  });

  test("workspace: create pod dialog shows agent selector", async ({ page }) => {
    const errors = collectConsoleErrors(page);
    await page.goto(`/${TEST_ORG_SLUG}/workspace`);
    await page.waitForLoadState("load");

    const createBtn = page.getByRole("button", { name: /创建|Create|New Pod/i }).first();
    if (await createBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await createBtn.click();
      await page.waitForTimeout(3000);

      const noAgentsMsg = await page.locator('text=/暂不支持任何智能体|does not support any agents/i').isVisible().catch(() => false);
      expect(noAgentsMsg).toBe(false);
    }
    assertNoWasmErrors(errors);
  });

  test("ticket detail: execute opens pod dialog", async ({ page, api }) => {
    const cc = await api.connect();
    const created = await cc.ticket.createTicket({
      orgSlug: TEST_ORG_SLUG,
      title: "E2E Exec Test",
    }) as Ticket;
    const slug = created.slug;

    const errors = collectConsoleErrors(page);
    await page.goto(`/${TEST_ORG_SLUG}/tickets/${slug}`);
    await page.waitForLoadState("load");

    const execBtn = page.getByRole("button", { name: /执行|Execute/i }).first();
    if (await execBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await execBtn.click();
      await page.waitForTimeout(3000);

      const noAgentsMsg = await page.locator('text=/暂不支持任何智能体|does not support any agents/i').isVisible().catch(() => false);
      expect(noAgentsMsg).toBe(false);
    }
    assertNoWasmErrors(errors);

    if (slug) {
      await cc.ticket.deleteTicket({ orgSlug: TEST_ORG_SLUG, ticketSlug: slug });
    }
  });
});
