import type { Locator, Page } from "@playwright/test";
import { gotoHash, expectHashMatches, waitForHash } from "../helpers/nav";

/**
 * Page Object for login page.
 * Route: #/login (hash router)
 */
export class LoginPage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorBanner: Locator;

  constructor(private page: Page) {
    this.emailInput = page.locator("input#email");
    this.passwordInput = page.locator("input#password");
    this.submitButton = page.locator('button[type="submit"]');
    this.errorBanner = page.locator('[class*="destructive"]').first();
  }

  async goto(): Promise<void> {
    await gotoHash(this.page, "/login");
    await this.emailInput.waitFor({ state: "visible", timeout: 20_000 });
  }

  async login(email: string, password: string): Promise<void> {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async waitForLoginRedirect(orgSlug: string): Promise<void> {
    await this.page.waitForFunction(
      (slug) => {
        const h = window.location.hash;
        return h.includes(`/${slug}/`) || h.includes("/onboarding") || h.includes("/workspace");
      },
      orgSlug,
      { timeout: 30_000 }
    );
  }

  async expectOnLoginPage(): Promise<void> {
    await expectHashMatches(this.page, /\/login/);
  }
}
