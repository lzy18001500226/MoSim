import type { Locator, Page } from "@playwright/test";
import { gotoHash, expectHashMatches } from "../helpers/nav";

/**
 * Page Object for Personal Settings.
 * Routes: #/settings, #/settings/general, #/settings/git, #/settings/notifications
 */
export class SettingsPersonalPage {
  readonly generalLink: Locator;
  readonly gitLink: Locator;
  readonly notificationsLink: Locator;
  readonly emailInput: Locator;
  readonly saveButton: Locator;

  constructor(private page: Page) {
    this.generalLink = page.getByRole("link", { name: /profile|general|个人/i });
    this.gitLink = page.getByRole("link", { name: /git|credentials/i });
    this.notificationsLink = page.getByRole("link", { name: /notifications|通知/i });
    this.emailInput = page.locator("input#email, input[name=email]");
    this.saveButton = page.getByRole("button", { name: /save|保存/i });
  }

  async goto(): Promise<void> {
    await gotoHash(this.page, `/settings/general`);
  }

  async gotoGit(): Promise<void> {
    await gotoHash(this.page, `/settings/git`);
  }

  async gotoNotifications(): Promise<void> {
    await gotoHash(this.page, `/settings/notifications`);
  }

  async expectOnPage(): Promise<void> {
    await expectHashMatches(this.page, /\/settings(\/|$)/);
  }
}
