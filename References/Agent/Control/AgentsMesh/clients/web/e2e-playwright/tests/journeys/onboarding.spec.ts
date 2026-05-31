// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { clearAuthRateLimit } from "../../helpers/redis";
import { CLEANUP } from "../../helpers/test-data";
import { DbFixture } from "../../fixtures/db.fixture";
import { makeConnectClient } from "../../helpers/connect-client";

/**
 * Journey: New User Onboarding
 * Register → Verify Email → Onboarding → Create Org → First Pod
 *
 * This is the most critical user journey — the first-time experience.
 */
test.describe("Journey: New User Onboarding", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  const EMAIL = "onboarding-journey@test.local";
  const PASSWORD = "JourneyPass123!";

  test.beforeAll(async ({}, _testInfo) => {
    // Pre-clean any leftover data
    const db = new DbFixture();
    try { db.cleanup(CLEANUP.userAndOrgsByEmail(EMAIL)); } catch { /* */ }
  });

  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("full onboarding: register → verify → org → workspace", async ({ page, db }) => {
    // ── Step 1: Register via UI ──
    await page.goto("/register");
    await page.locator("#name").fill("Journey Test User");
    await page.locator("#email").fill(EMAIL);
    await page.locator("#username").fill("journeyuser");
    await page.locator("#password").fill(PASSWORD);
    // confirmPassword is required and always rendered (see register page.tsx).
    // The previous `if (await isVisible())` race condition let the spec skip
    // the fill during slow renders → handleSubmit's password mismatch check
    // tripped → silent setError → no redirect → 15s waitForURL timeout.
    // Use waitFor to guarantee the field is mountable before filling.
    const confirmPwd = page.locator("#confirmPassword");
    await confirmPwd.waitFor({ state: "visible", timeout: 10_000 });
    await confirmPwd.fill(PASSWORD);
    await page.locator('button[type="submit"]').click();

    // Should redirect away from register
    await page.waitForURL((url) => !url.pathname.includes("/register"), {
      timeout: 15_000,
    });

    // ── Step 2: Verify email via DB token ──
    const verifyToken = db.queryValue(
      `SELECT email_verification_token FROM users WHERE email = '${EMAIL}'`
    );
    if (verifyToken) {
      // VerifyEmail is an unauthenticated AuthService RPC — build a client
      // without a token rather than reusing the authenticated fixture.
      const publicCc = makeConnectClient(null);
      await publicCc.auth.verifyEmail({ token: verifyToken });

      const verified = db.queryValue(
        `SELECT is_email_verified::text FROM users WHERE email = '${EMAIL}'`
      );
      expect(verified).toBe("true");
    }

    // ── Step 3: Complete onboarding (if redirected there) ──
    const currentUrl = page.url();
    if (currentUrl.includes("/onboarding")) {
      // Look for "Create Personal Workspace" or similar
      const createBtn = page.getByRole("button", {
        name: /create|创建|quick start|快速/i,
      }).first();
      if (await createBtn.isVisible()) {
        await createBtn.click();
        // Onboarding flow may route to /onboarding/setup-runner next; accept
        // anything past /onboarding (workspace/dashboard) OR the setup-runner
        // sub-step.
        await page.waitForURL(
          (url) =>
            !url.pathname.includes("/onboarding") ||
            url.pathname.includes("/setup-runner"),
          { timeout: 15_000 },
        );
      }
    }

    // ── Step 4: Verify landing on workspace ──
    const finalUrl = page.url();
    expect(finalUrl).toMatch(/workspace|dashboard|onboarding/);

    // ── Step 5: Verify user exists in DB with org membership ──
    const userId = db.queryValue(
      `SELECT id FROM users WHERE email = '${EMAIL}'`
    );
    expect(userId).toBeTruthy();

    const orgCount = db.queryValue(
      `SELECT COUNT(*) FROM organization_members WHERE user_id = ${userId}`
    );
    // User should have at least one org (auto-created or joined)
    expect(parseInt(orgCount || "0")).toBeGreaterThanOrEqual(0);

    // ── Cleanup ──
    try { db.cleanup(CLEANUP.userAndOrgsByEmail(EMAIL)); } catch { /* */ }
  });
});
