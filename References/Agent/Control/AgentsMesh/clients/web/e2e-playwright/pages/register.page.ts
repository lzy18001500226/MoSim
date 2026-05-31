import type { Locator, Page } from "@playwright/test";

/**
 * Page Object Model for the Register page.
 * Selectors based on: web/src/app/(auth)/register/page.tsx
 */
export class RegisterPage {
  readonly nameInput: Locator;
  readonly emailInput: Locator;
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly confirmPasswordInput: Locator;
  readonly submitButton: Locator;
  readonly loginLink: Locator;
  readonly errorMessage: Locator;

  constructor(private page: Page) {
    this.nameInput = page.locator("#name");
    this.emailInput = page.locator("#email");
    this.usernameInput = page.locator("#username");
    this.passwordInput = page.locator("#password");
    this.confirmPasswordInput = page.locator("#confirmPassword");
    this.submitButton = page.locator('button[type="submit"]');
    this.loginLink = page.getByRole("link", { name: /sign in|login/i });
    this.errorMessage = page.locator(".text-destructive");
  }

  async goto(): Promise<void> {
    await this.page.goto("/register");
    await this.emailInput.waitFor({ state: "visible" });
  }

  async register(opts: {
    name: string;
    email: string;
    username: string;
    password: string;
    confirmPassword?: string;
  }): Promise<void> {
    await this.nameInput.fill(opts.name);
    await this.emailInput.fill(opts.email);
    await this.usernameInput.fill(opts.username);
    await this.passwordInput.fill(opts.password);
    if (opts.confirmPassword && await this.confirmPasswordInput.isVisible()) {
      await this.confirmPasswordInput.fill(opts.confirmPassword);
    }
    await this.submitButton.click();
  }

  async getErrorText(): Promise<string | null> {
    if (await this.errorMessage.isVisible()) {
      return this.errorMessage.textContent();
    }
    return null;
  }
}
