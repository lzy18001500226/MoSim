import { test, expect } from "../../../fixtures/index";
import { getWebBaseUrl } from "../../../helpers/env";

/**
 * SSO Callback UI tests.
 * Maps to: TC-SSO-CB-001~004
 */
test.describe("SSO Callback", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  const baseUrl = getWebBaseUrl();

  /**
   * TC-SSO-CB-001: Error access_denied shows friendly message
   */
  test("callback with error=access_denied shows error", async ({ page }) => {
    await page.goto("/auth/sso/callback?error=access_denied");
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/denied|拒绝|error|错误|failed|失败/i);
  });

  /**
   * TC-SSO-CB-002: Unknown error shows generic message
   */
  test("callback with unknown error shows message", async ({ page }) => {
    await page.goto("/auth/sso/callback?error=unknown_error");
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/error|错误|failed|失败/i);
  });

  /**
   * TC-SSO-CB-003: Missing token shows error
   */
  test("callback without token or error shows error", async ({ page }) => {
    await page.goto("/auth/sso/callback");
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/error|错误|invalid|无效|login|登录/i);
  });
});
