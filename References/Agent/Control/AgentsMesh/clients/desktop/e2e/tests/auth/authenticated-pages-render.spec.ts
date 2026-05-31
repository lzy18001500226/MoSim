import { test, expect } from "../../fixtures";
import { TEST_USER, TEST_ORG_SLUG } from "../../helpers/env";
import { gotoHash } from "../../helpers/nav";

// H1 regression guard: GeneralSettingsPage / RunnerAuthorizePage / InvitePage
// destructured `user` (and `token`, `organizations`) from `useAuthStore()`
// — but auth Store state no longer has those keys; they're memory-only via
// selector hooks (useCurrentUser, useAuthOrganizations, useIsAuthenticated).
// Result: dead destructure → undefined → page renders blank `username` /
// `email` / can't proceed.
//
// This spec asserts: after login, the personal-settings page actually
// surfaces the dev-user's email — the smoke "all-pages-no-error" suite
// would have missed this because it only verifies render-without-throw,
// not content. Two pages tested back-to-back so both "user destructure"
// fixes are covered.

test.describe("Auth · authenticated pages render real user", () => {
  test("settings/general shows dev user's email and username", async ({ page }) => {
    // The fixture restores the seeded auth snapshot, so we land on
    // dashboard. From there navigate to the personal General settings.
    await gotoHash(page, "/settings/general");
    // Page heading sanity check — render did happen.
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible({ timeout: 10_000 });
    // The dev user's email is rendered into the Account Info card.
    // Without the H1 fix, the `<p className="font-medium">{user?.email || "-"}</p>`
    // line falls through to "-" because `user` is undefined.
    await expect(page.getByText(TEST_USER.email)).toBeVisible({ timeout: 5000 });
  });

  test("dashboard route uses dev org slug (not /login)", async ({ page }) => {
    // Sanity: with proper bootstrap + isAuthenticated, RootRedirect lands
    // us in /{orgSlug}/workspace, not /login. Catches a useIsAuthenticated
    // regression — would route to /login if the hook returned false
    // despite a fresh session.
    await page.waitForTimeout(500);
    const hash = await page.evaluate(() => window.location.hash);
    expect(hash).not.toContain("/login");
    expect(hash).toMatch(new RegExp(`/${TEST_ORG_SLUG}/|/onboarding|/workspace`));
  });
});
