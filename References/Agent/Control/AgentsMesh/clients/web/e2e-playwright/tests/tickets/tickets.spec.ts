// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Tickets API & UI", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list tickets", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.ticket.listTickets({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("get ticket board", async ({ api }) => {
    const cc = await api.connect();
    const board = await cc.ticket.getBoard({ orgSlug: TEST_ORG_SLUG }) as { columns: unknown[] };
    expect(Array.isArray(board.columns)).toBe(true);
  });

  test("create and delete ticket", async ({ api }) => {
    const cc = await api.connect();
    const ticket = await cc.ticket.createTicket({
      orgSlug: TEST_ORG_SLUG,
      title: "E2E Test Ticket",
    }) as { slug: string };
    expect(ticket.slug).toBeTruthy();

    await cc.ticket.deleteTicket({ orgSlug: TEST_ORG_SLUG, ticketSlug: ticket.slug });
  });

  test("tickets page loads in UI", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/tickets`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/ticket|工单|任务/i);
  });
});
