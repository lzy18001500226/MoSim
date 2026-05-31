import { test, expect } from "@playwright/test";
import { TEST_USER } from "../../helpers/env";
import { LoginPage } from "../../pages/login.page";

// Regression cover for issue #346: popout terminal redirected to /login
// for already-logged-in users in a fresh BrowserWindow because the new
// window's wasm core started anonymous and never ran bootstrap. The
// fix wires popout/layout.tsx → AuthBootstrap (init wasm + bootstrap)
// → RequireAuth (login bounce w/ ?redirect=).
//
// We use a synthetic podKey: even if no real pod exists, the auth gate
// runs first — it either lets the page render or redirects. The bug
// would manifest as a /login redirect for an authenticated session,
// independent of pod existence.

const SYNTH_POD_KEY = "popout-redirect-test-pod";
const POPOUT_PATH = `/popout/terminal/${SYNTH_POD_KEY}`;

test.describe("Popout terminal auth gating", () => {
  test("authenticated user lands on popout without /login bounce", async ({
    page,
  }) => {
    await page.goto(POPOUT_PATH);

    // Give bootstrap + RequireAuth a moment to settle. If the bug
    // regressed we'd be on /login; instead the URL must keep its
    // popout shape.
    await page.waitForTimeout(2_000);
    expect(page.url()).toContain(POPOUT_PATH);
    expect(page.url()).not.toContain("/login");
  });

  test.describe("anonymous", () => {
    test.use({ storageState: { cookies: [], origins: [] } });

    test("anonymous popout deep link bounces through /login with ?redirect=", async ({
      page,
    }) => {
      await page.goto(POPOUT_PATH);

      // RequireAuth replaces the URL with /login?redirect=<encoded popout>.
      await page.waitForURL((url) => url.pathname === "/login", {
        timeout: 15_000,
      });
      const redirectParam = new URL(page.url()).searchParams.get("redirect");
      expect(redirectParam).toBe(POPOUT_PATH);
    });

    test("login restores the original popout URL via ?redirect=", async ({
      page,
    }) => {
      await page.goto(POPOUT_PATH);
      await page.waitForURL((url) => url.pathname === "/login", {
        timeout: 15_000,
      });

      const loginPage = new LoginPage(page);
      await loginPage.login(TEST_USER.email, TEST_USER.password);

      // Post-login navigation must honor ?redirect= ahead of getDefaultRoute.
      await page.waitForURL(
        (url) => url.pathname === POPOUT_PATH,
        { timeout: 15_000 }
      );
      expect(page.url()).toContain(POPOUT_PATH);
    });
  });
});
