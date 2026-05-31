import { test, expect } from "../../fixtures";
import { LoginPage } from "../../pages/login.page";
import { TEST_USER, TEST_ORG_SLUG } from "../../helpers/env";
import { resolve } from "node:path";
import { rmSync } from "node:fs";

// Fresh Electron profile so the login page is actually shown.
const FRESH_USER_DATA = resolve(__dirname, "../../.auth/electron-userdata-login");

test.use({
  skipAuthRestore: true,
  userDataDir: FRESH_USER_DATA,
});

test.beforeAll(() => {
  rmSync(FRESH_USER_DATA, { recursive: true, force: true });
});

test.describe("Auth · login", () => {
  test("rejects invalid credentials and stays on login", async ({ page }) => {
    const login = new LoginPage(page);
    await login.expectOnLoginPage();
    await login.login("wrong@example.com", "wrongpass");
    await expect(login.errorBanner).toBeVisible({ timeout: 10_000 });
    await login.expectOnLoginPage();
  });

  test("logs in with valid credentials and reaches dashboard", async ({ page }) => {
    const login = new LoginPage(page);
    await login.expectOnLoginPage();
    await login.login(TEST_USER.email, TEST_USER.password);
    await login.waitForLoginRedirect(TEST_ORG_SLUG);
    const hash = await page.evaluate(() => window.location.hash);
    expect(hash).not.toContain("/login");
  });
});
