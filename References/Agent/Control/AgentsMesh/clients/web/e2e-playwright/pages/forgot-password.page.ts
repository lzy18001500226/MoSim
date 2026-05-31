import type { Locator, Page } from "@playwright/test";

/**
 * Page Object Model for the Forgot Password page.
 * Selectors based on: web/src/app/(auth)/forgot-password/page.tsx
 */
export class ForgotPasswordPage {
  readonly emailInput: Locator;
  readonly submitButton: Locator;
  readonly backToLoginLink: Locator;
  readonly successMessage: Locator;

  constructor(private page: Page) {
    this.emailInput = page.locator("#email");
    this.submitButton = page.locator('button[type="submit"]');
    this.backToLoginLink = page.getByRole("link", {
      name: /back|sign in|login/i,
    });
    this.successMessage = page.locator("[role='alert'], .text-green, .bg-green");
  }

  async goto(): Promise<void> {
    await this.page.goto("/forgot-password");
    await this.emailInput.waitFor({ state: "visible" });
  }

  async requestReset(email: string): Promise<void> {
    await this.emailInput.fill(email);
    await this.submitButton.click();
  }
}
