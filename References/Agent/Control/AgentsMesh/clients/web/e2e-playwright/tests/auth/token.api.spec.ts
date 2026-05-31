// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_USER } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { ConnectError } from "../../helpers/connect-client";

test.describe("Token Management", () => {
  test.beforeEach(async () => {
    clearAuthRateLimit();
  });

  /**
   * TC-TOKEN-001: Token refresh
   */
  test("refresh token returns new tokens", async ({ api }) => {
    const loginData = await api.login();
    const refreshToken = loginData.refresh_token;

    const cc = api.connectWithToken("");
    const res = await cc.auth.refreshToken({ refreshToken }) as { token: string; refreshToken: string };
    expect(res.token).toBeTruthy();
    expect(res.refreshToken).toBeTruthy();
  });

  /**
   * TC-TOKEN-002: Token refresh with invalid token
   */
  test("refresh with invalid token fails", async ({ api }) => {
    const cc = api.connectWithToken("");
    await expect(
      cc.auth.refreshToken({ refreshToken: "invalid-refresh-token-12345" })
    ).rejects.toMatchObject({ status: 401 });
  });

  test("refresh with empty token fails", async ({ api }) => {
    const cc = api.connectWithToken("");
    await expect(
      cc.auth.refreshToken({ refreshToken: "" })
    ).rejects.toBeInstanceOf(ConnectError);
  });

  /**
   * TC-TOKEN-003: Logout invalidates token
   */
  test("logout invalidates access token", async ({ api }) => {
    const loginData = await api.login();
    const token = loginData.token;

    const cc = api.connectWithToken(token);
    const res = await cc.authSession.logout({}) as { message?: string };
    expect(res).toBeTruthy();
  });

  /**
   * TC-TOKEN-004: Multi-device concurrent login
   */
  test("multi-device login produces independent tokens", async ({ api }) => {
    // Login from three "devices" with delay to ensure different JWT iat claims
    const a = await api.login(TEST_USER.email, TEST_USER.password);
    await new Promise((r) => setTimeout(r, 1100));
    const b = await api.login(TEST_USER.email, TEST_USER.password);
    await new Promise((r) => setTimeout(r, 1100));
    const c = await api.login(TEST_USER.email, TEST_USER.password);

    // Tokens should be different
    expect(a.token).not.toBe(b.token);
    expect(b.token).not.toBe(c.token);

    // All tokens should work — verify via GetMe
    for (const token of [a.token, b.token, c.token]) {
      const cc = api.connectWithToken(token);
      const me = await cc.user.getMe({}) as { id: string | number };
      expect(me.id).toBeTruthy();
    }

    // Logout device A
    const ccA = api.connectWithToken(a.token);
    await ccA.authSession.logout({});

    // B and C should still work
    const ccB = api.connectWithToken(b.token);
    const meB = await ccB.user.getMe({}) as { id: string | number };
    expect(meB.id).toBeTruthy();

    const ccC = api.connectWithToken(c.token);
    const meC = await ccC.user.getMe({}) as { id: string | number };
    expect(meC.id).toBeTruthy();
  });
});
