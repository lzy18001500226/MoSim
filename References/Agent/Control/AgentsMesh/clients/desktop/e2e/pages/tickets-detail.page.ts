import type { Locator, Page } from "@playwright/test";
import { TEST_ORG_SLUG } from "../helpers/env";
import { gotoHash, expectHashMatches } from "../helpers/nav";

/**
 * Page Object for a ticket detail view with sidebar of Pods/PRs/Sub-tickets/Activity.
 * Route: #/:org/tickets/:slug
 */
export class TicketDetailPage {
  readonly title: Locator;
  readonly spawnPodButton: Locator;
  readonly podsSidebar: Locator;
  readonly prsSidebar: Locator;
  readonly subTicketsSidebar: Locator;
  readonly activityLog: Locator;
  readonly closeButton: Locator;

  constructor(private page: Page) {
    this.title = page.getByRole("heading").first();
    this.spawnPodButton = page.getByRole("button", { name: /spawn pod|启动 pod/i });
    this.podsSidebar = page.locator('[data-section="pods"]');
    this.prsSidebar = page.locator('[data-section="prs"]');
    this.subTicketsSidebar = page.locator('[data-section="sub-tickets"]');
    this.activityLog = page.locator('[data-section="activity"]');
    this.closeButton = page.getByRole("button", { name: /close ticket|关闭/i });
  }

  async goto(slug: string): Promise<void> {
    await gotoHash(this.page, `/${TEST_ORG_SLUG}/tickets/${slug}`);
  }

  async expectOnPage(slug?: string): Promise<void> {
    const re = slug ? new RegExp(`/tickets/${slug}`) : /\/tickets\//;
    await expectHashMatches(this.page, re);
  }

  async spawnPod(): Promise<void> {
    await this.spawnPodButton.click();
  }
}
