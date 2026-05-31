import type { Locator, Page } from "@playwright/test";
import { TEST_ORG_SLUG } from "../helpers/env";
import { gotoHash, expectHashMatches } from "../helpers/nav";

/**
 * Page Object for Tickets list (Kanban/List view).
 * Route: #/:org/tickets
 */
export class TicketsBoardPage {
  readonly createButton: Locator;
  readonly kanbanColumns: Locator;
  readonly ticketCards: Locator;
  readonly viewSwitcher: Locator;

  constructor(private page: Page) {
    this.createButton = page.getByRole("button", { name: /new ticket|create ticket|新建/i }).first();
    this.kanbanColumns = page.locator('[data-column-status], [class*="kanban-column"]');
    this.ticketCards = page.locator('[data-ticket-slug], [class*="ticket-card"]');
    this.viewSwitcher = page.getByRole("tablist", { name: /view/i }).first();
  }

  async goto(): Promise<void> {
    await gotoHash(this.page, `/${TEST_ORG_SLUG}/tickets`);
  }

  async expectOnPage(): Promise<void> {
    await expectHashMatches(this.page, /\/tickets(\?|#|$)/);
  }

  async openTicketBySlug(slug: string): Promise<void> {
    await this.page.locator(`[data-ticket-slug="${slug}"]`).first().click();
    await expectHashMatches(this.page, new RegExp(`/tickets/${slug}`));
  }
}
