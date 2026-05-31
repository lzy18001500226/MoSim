// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Ticket Detail Page", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  let createdSlug: string | null = null;

  test.afterEach(async ({ api }) => {
    if (createdSlug) {
      const cc = await api.connect();
      await cc.ticket.deleteTicket({ orgSlug: TEST_ORG_SLUG, ticketSlug: createdSlug }).catch(() => {});
      createdSlug = null;
    }
  });

  test("API: get single ticket returns proto message", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.ticket.createTicket({
      orgSlug: TEST_ORG_SLUG,
      title: "E2E Detail Test Ticket",
    }) as { slug: string };
    createdSlug = created.slug;
    expect(createdSlug).toBeTruthy();

    const detail = await cc.ticket.getTicket({
      orgSlug: TEST_ORG_SLUG,
      ticketSlug: createdSlug,
    }) as { slug: string; title: string };
    expect(detail.slug).toBe(createdSlug);
    expect(detail.title).toBe("E2E Detail Test Ticket");
  });

  test("UI: ticket detail page renders without errors", async ({ page, api }) => {
    const cc = await api.connect();
    const created = await cc.ticket.createTicket({
      orgSlug: TEST_ORG_SLUG,
      title: "E2E UI Detail Ticket",
    }) as { slug: string };
    createdSlug = created.slug;

    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    await page.goto(`/${TEST_ORG_SLUG}/tickets/${createdSlug}`);
    await page.waitForLoadState("load");

    // Wait for React hydration to surface the title text. Pure body.textContent
    // immediately after `load` can still capture inline JS chunks Next.js
    // ships in `<script>` tags before they're stripped by render.
    await expect(page.getByText("E2E UI Detail Ticket").first()).toBeVisible({ timeout: 10_000 });
    const body = await page.textContent("body");
    expect(body).toContain("E2E UI Detail Ticket");

    const jsonErrors = consoleErrors.filter(
      (e) => e.includes("missing field") || e.includes("is not valid JSON")
    );
    expect(jsonErrors).toHaveLength(0);
  });

  test("UI: navigate from ticket list to detail without errors", async ({ page, api }) => {
    const cc = await api.connect();
    const created = await cc.ticket.createTicket({
      orgSlug: TEST_ORG_SLUG,
      title: "E2E Nav Detail Ticket",
    }) as { slug: string };
    createdSlug = created.slug;

    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    await page.goto(`/${TEST_ORG_SLUG}/tickets`);
    await page.waitForLoadState("load");

    const ticketLink = page.locator(`a[href*="${createdSlug}"], [data-ticket-slug="${createdSlug}"]`).first();
    if (await ticketLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      await ticketLink.click();
      await page.waitForLoadState("load");

      const jsonErrors = consoleErrors.filter(
        (e) => e.includes("missing field") || e.includes("is not valid JSON") || e.includes("Failed to fetch")
      );
      expect(jsonErrors).toHaveLength(0);
    }
  });

  test("UI: ticket board page loads without errors", async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    await page.goto(`/${TEST_ORG_SLUG}/tickets`);
    await page.waitForLoadState("load");

    const jsonErrors = consoleErrors.filter(
      (e) => e.includes("missing field") || e.includes("is not valid JSON") || e.includes("Failed to fetch board")
    );
    expect(jsonErrors).toHaveLength(0);
  });
});
