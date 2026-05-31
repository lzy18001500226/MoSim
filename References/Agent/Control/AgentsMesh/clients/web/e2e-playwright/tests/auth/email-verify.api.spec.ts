// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { CLEANUP, HASH_PASSWORD123 } from "../../helpers/test-data";
import { clearAuthRateLimit } from "../../helpers/redis";
import { ConnectError } from "../../helpers/connect-client";

test.describe("Email Verification", () => {
  test.beforeEach(async () => {
    clearAuthRateLimit();
  });

  /**
   * TC-VERIFY-001: Verify email with valid token
   */
  test("verify email with valid token succeeds", async ({ api, db }) => {
    const email = "verify-e2e@test.local";

    db.setup(`
      INSERT INTO users (email, username, password_hash, name, is_email_verified,
        email_verification_token, email_verification_expires_at)
      VALUES ('${email}', 'verifye2e', '${HASH_PASSWORD123}', 'Verify User', false,
        'test-verify-token-12345', NOW() + INTERVAL '1 hour')
      ON CONFLICT (email) DO UPDATE SET
        is_email_verified = false,
        email_verification_token = 'test-verify-token-12345',
        email_verification_expires_at = NOW() + INTERVAL '1 hour'
    `);

    const cc = api.connectWithToken("");
    const res = await cc.auth.verifyEmail({ token: "test-verify-token-12345" }) as { message?: string };
    expect(res).toBeTruthy();

    // DB verification
    const verified = db.queryValue(
      `SELECT is_email_verified::text FROM users WHERE email = '${email}'`
    );
    expect(verified).toBe("true");

    db.cleanup(CLEANUP.userByEmail(email));
  });

  /**
   * TC-VERIFY-002: Verify email with invalid token
   */
  test("verify email with invalid token fails", async ({ api }) => {
    const cc = api.connectWithToken("");
    await expect(
      cc.auth.verifyEmail({ token: "invalid-verification-token-xyz" })
    ).rejects.toBeInstanceOf(ConnectError);
  });

  test("verify email with empty token fails", async ({ api }) => {
    const cc = api.connectWithToken("");
    await expect(
      cc.auth.verifyEmail({ token: "" })
    ).rejects.toBeInstanceOf(ConnectError);
  });

  /**
   * TC-VERIFY-003: Resend verification email
   */
  test("resend verification for valid email succeeds", async ({ api, db }) => {
    const email = "resend-e2e@test.local";

    db.setup(`
      INSERT INTO users (email, username, password_hash, name, is_email_verified)
      VALUES ('${email}', 'resende2e', '${HASH_PASSWORD123}', 'Resend User', false)
      ON CONFLICT (email) DO UPDATE SET is_email_verified = false
    `);

    const cc = api.connectWithToken("");
    const res = await cc.auth.resendVerification({ email }) as { message?: string };
    expect(res).toBeTruthy();

    db.cleanup(CLEANUP.userByEmail(email));
  });

  test("resend verification for non-existent email returns success (no enumeration)", async ({ api }) => {
    const cc = api.connectWithToken("");
    const res = await cc.auth.resendVerification({ email: "nonexistent@test.local" }) as { message?: string };
    expect(res).toBeTruthy();
  });
});
