// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { collectConsoleErrors, assertNoWasmErrors } from "../../helpers/console-errors";

test.describe("Support Tickets", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("API: list support tickets", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.supportTicket.listSupportTickets({}) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("API: support ticket detail (if exists)", async ({ api, db }) => {
    const id = db.queryValue("SELECT id FROM support_tickets LIMIT 1");
    const cc = await api.connect();
    if (!id) {
      const res = await cc.supportTicket.listSupportTickets({}) as { items: unknown[] };
      expect(Array.isArray(res.items)).toBe(true);
      return;
    }
    const res = await cc.supportTicket.getSupportTicket({ id: Number(id) }) as { ticket?: unknown };
    expect(res.ticket).toBeTruthy();
  });

  test("UI: support page loads without errors", async ({ page }) => {
    const errors = collectConsoleErrors(page);
    await page.goto(`/${TEST_ORG_SLUG}/support`);
    await page.waitForLoadState("load");
    assertNoWasmErrors(errors);
  });

  test("UI: support page open new ticket dialog", async ({ page }) => {
    const errors = collectConsoleErrors(page);
    await page.goto(`/${TEST_ORG_SLUG}/support`);
    await page.waitForLoadState("load");

    const newBtn = page.getByRole("button", { name: /新建|New|Create|提交/i }).first();
    if (await newBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await newBtn.click();
      await page.waitForTimeout(500);
    }
    assertNoWasmErrors(errors);
  });
});
