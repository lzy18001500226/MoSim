// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { RegisterPage } from "../../pages/register.page";
import { CLEANUP } from "../../helpers/test-data";
import { clearAuthRateLimit } from "../../helpers/redis";
import { ConnectError } from "../../helpers/connect-client";

test.describe("Registration Flow", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test.beforeEach(async () => {
    clearAuthRateLimit();
  });

  /**
   * TC-REG-004: Register page UI elements
   */
  test("register page displays all required elements", async ({ page }) => {
    const registerPage = new RegisterPage(page);
    await registerPage.goto();

    await expect(registerPage.nameInput).toBeVisible();
    await expect(registerPage.emailInput).toBeVisible();
    await expect(registerPage.usernameInput).toBeVisible();
    await expect(registerPage.passwordInput).toBeVisible();
    await expect(registerPage.submitButton).toBeVisible();
    await expect(registerPage.loginLink).toBeVisible();
  });

  /**
   * TC-REG-001: Successful registration (API)
   */
  test("successful registration creates user and returns token", async ({ api, db }) => {
    const email = "newuser-e2e@test.local";
    try { db.cleanup(CLEANUP.userByEmail(email)); } catch { /* ignore */ }

    const cc = api.connectWithToken("");
    const res = await cc.auth.register({
      email,
      username: "newusere2e",
      password: "TestPass123!",
      name: "E2E Test User",
    }) as { token: string; user: { email: string } };

    expect(res.token).toBeTruthy();
    expect(res.user.email).toBe(email);

    db.cleanup(CLEANUP.userByEmail(email));
  });

  /**
   * TC-REG-002: Registration fails with existing email (API)
   */
  test("registration fails with existing email", async ({ api }) => {
    const cc = api.connectWithToken("");
    await expect(
      cc.auth.register({
        email: "dev@agentsmesh.local",
        username: "anotheruser",
        password: "TestPass123!",
        name: "Another User",
      })
    ).rejects.toMatchObject({ status: 409 });
  });

  /**
   * TC-REG-003: Registration fails with weak password (API)
   */
  test("registration fails with weak password", async ({ api }) => {
    const cc = api.connectWithToken("");
    await expect(
      cc.auth.register({
        email: "weakpwd@test.local",
        username: "weakpwduser",
        password: "123",
        name: "Weak Password User",
      })
    ).rejects.toBeInstanceOf(ConnectError);
  });

  /**
   * TC-REG-004: Register page UI interaction flow
   */
  test("register page UI flow", async ({ page, db }) => {
    const email = "uiregister@test.local";
    try { db.cleanup(CLEANUP.userAndOrgsByEmail(email)); } catch { /* ignore */ }

    const registerPage = new RegisterPage(page);
    await registerPage.goto();
    await registerPage.register({
      name: "UI Register Test", email,
      username: "uiregistertest", password: "TestPass123!",
      confirmPassword: "TestPass123!",
    });

    await page.waitForURL((url) => !url.pathname.includes("/register"), {
      timeout: 15_000,
    });

    try { db.cleanup(CLEANUP.userAndOrgsByEmail(email)); } catch { /* ignore */ }
  });
});
