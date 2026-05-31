// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { CLEANUP, HASH_PASSWORD123 } from "../../helpers/test-data";
import { clearAuthRateLimit } from "../../helpers/redis";
import { ConnectError } from "../../helpers/connect-client";

test.describe("Password Reset Flow", () => {
  test.beforeEach(async () => {
    clearAuthRateLimit();
  });

  /**
   * TC-PWRST-001: Request password reset
   */
  test("forgot password returns success for valid email", async ({ api }) => {
    const cc = api.connectWithToken("");
    const res = await cc.auth.forgotPassword({ email: "dev@agentsmesh.local" }) as { message?: string };
    expect(res.message).toBeTruthy();
  });

  test("forgot password returns success for non-existent email (no enumeration)", async ({ api }) => {
    const cc = api.connectWithToken("");
    // Security: same response for non-existent emails
    const res = await cc.auth.forgotPassword({ email: "nonexistent@test.local" }) as { message?: string };
    expect(res.message).toBeTruthy();
  });

  /**
   * TC-PWRST-002: Reset password with valid token
   */
  test("reset password with valid token succeeds", async ({ api, db }) => {
    const email = "pwreset-e2e@test.local";

    // Setup: create user with reset token
    db.setup(`
      INSERT INTO users (email, username, password_hash, name, is_email_verified, password_reset_token, password_reset_expires_at)
      VALUES ('${email}', 'pwresete2e', '${HASH_PASSWORD123}', 'PW Reset User', true, 'test-reset-token-12345', NOW() + INTERVAL '1 hour')
      ON CONFLICT (email) DO UPDATE SET
        password_reset_token = 'test-reset-token-12345',
        password_reset_expires_at = NOW() + INTERVAL '1 hour'
    `);

    const cc = api.connectWithToken("");
    const res = await cc.auth.resetPassword({
      token: "test-reset-token-12345",
      newPassword: "NewTestPass456!",
    }) as { message?: string };
    expect(res).toBeTruthy();

    // Verify login with new password works
    const loginRes = await cc.auth.login({
      email,
      password: "NewTestPass456!",
    }) as { token: string };
    expect(loginRes.token).toBeTruthy();

    db.cleanup(CLEANUP.userByEmail(email));
  });

  /**
   * TC-PWRST-003: Reset password with invalid token
   */
  test("reset password with invalid token fails", async ({ api }) => {
    const cc = api.connectWithToken("");
    await expect(
      cc.auth.resetPassword({
        token: "invalid-reset-token-xyz",
        newPassword: "NewTestPass456!",
      })
    ).rejects.toBeInstanceOf(ConnectError);
  });

  test("reset password with empty token fails", async ({ api }) => {
    const cc = api.connectWithToken("");
    await expect(
      cc.auth.resetPassword({
        token: "",
        newPassword: "NewTestPass456!",
      })
    ).rejects.toBeInstanceOf(ConnectError);
  });

  test("reset password with weak new password fails", async ({ api }) => {
    const cc = api.connectWithToken("");
    await expect(
      cc.auth.resetPassword({
        token: "some-token",
        newPassword: "123",
      })
    ).rejects.toBeInstanceOf(ConnectError);
  });
});
