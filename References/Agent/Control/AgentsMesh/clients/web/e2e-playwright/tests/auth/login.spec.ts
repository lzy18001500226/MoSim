import { test, expect } from "@playwright/test";
import { LoginPage } from "../../pages/login.page";
import { TEST_USER } from "../../helpers/env";

test.describe("Login Flow", () => {
  // Disable storageState for login tests — we need unauthenticated state
  test.use({ storageState: { cookies: [], origins: [] } });

  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    await loginPage.goto();
  });

  /**
   * TC-LOGIN-004: Login page UI elements
   */
  test("login page displays all required elements", async () => {
    await expect(loginPage.emailInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.submitButton).toBeVisible();
    await expect(loginPage.registerLink).toBeVisible();
  });

  /**
   * TC-LOGIN-001: Successful login
   */
  test("successful login redirects to workspace", async ({ page }) => {
    await loginPage.login(TEST_USER.email, TEST_USER.password);

    // Should redirect away from /login
    await page.waitForURL((url) => !url.pathname.includes("/login"), {
      timeout: 15_000,
    });

    // Should land on workspace or dashboard
    expect(page.url()).toMatch(/\/(dev-org|workspace|dashboard)/);
  });

  /**
   * TC-LOGIN-002: Invalid credentials
   */
  test("invalid credentials show error message", async ({ page }) => {
    await loginPage.login("wrong@example.com", "wrongpassword");

    // Should stay on login page
    await page.waitForTimeout(2_000);
    expect(page.url()).toContain("/login");

    // Error message should be visible
    const error = await loginPage.getErrorText();
    expect(error).toBeTruthy();
  });

  /**
   * TC-LOGIN-003: Empty form submission
   */
  test("empty form shows validation errors", async ({ page }) => {
    // Try to submit without filling anything — HTML5 validation should prevent
    await loginPage.submitButton.click();

    // Should remain on login page
    expect(page.url()).toContain("/login");

    // The email input should have validation state (required attribute)
    const emailRequired = await loginPage.emailInput.getAttribute("required");
    expect(emailRequired).not.toBeNull();
  });
});
