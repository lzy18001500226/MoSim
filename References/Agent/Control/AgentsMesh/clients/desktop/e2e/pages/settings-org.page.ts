import type { Locator, Page } from "@playwright/test";
import { TEST_ORG_SLUG } from "../helpers/env";
import { gotoHash, expectHashMatches } from "../helpers/nav";

/**
 * Page Object for Organization Settings (multi-tab).
 * Route: #/:org/settings
 */
export class SettingsOrgPage {
  readonly generalTab: Locator;
  readonly peopleTab: Locator;
  readonly runnersTab: Locator;
  readonly reposTab: Locator;
  readonly agentsTab: Locator;
  readonly billingTab: Locator;
  readonly apiKeysTab: Locator;
  readonly auditTab: Locator;
  readonly dangerTab: Locator;

  constructor(private page: Page) {
    this.generalTab = page.getByRole("tab", { name: /general|综合/i });
    this.peopleTab = page.getByRole("tab", { name: /members|people|成员/i });
    this.runnersTab = page.getByRole("tab", { name: /runners/i });
    this.reposTab = page.getByRole("tab", { name: /repositories|code/i });
    this.agentsTab = page.getByRole("tab", { name: /agents/i });
    this.billingTab = page.getByRole("tab", { name: /billing|usage/i });
    this.apiKeysTab = page.getByRole("tab", { name: /api keys/i });
    this.auditTab = page.getByRole("tab", { name: /audit/i });
    this.dangerTab = page.getByRole("tab", { name: /danger/i });
  }

  async goto(): Promise<void> {
    await gotoHash(this.page, `/${TEST_ORG_SLUG}/settings`);
  }

  async expectOnPage(): Promise<void> {
    await this.page.waitForFunction(
      (slug) => window.location.hash.includes(`/${slug}/settings`),
      TEST_ORG_SLUG,
      { timeout: 20_000 }
    );
  }
}
