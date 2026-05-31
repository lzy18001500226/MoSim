// Migrated R5+: was REST `api.postPublic('/api/v1/auth/sso/{domain}/ldap')`,
// now `cc.sso.ldapAuth(...)` (typed Connect, binary wire). The domain that
// was a path param in REST becomes the `domain` field in LdapAuthRequest.
import { test, expect } from "../../../fixtures/index";
import { clearAuthRateLimit } from "../../../helpers/redis";
import { ConnectError } from "../../../helpers/connect-client";

test.describe("SSO LDAP API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * TC-SSO-LDAP-001: LDAP auth with invalid credentials.
   * Connect: Unauthenticated→401 (bad creds) or NotFound→404 (domain absent).
   */
  test("LDAP auth with invalid credentials returns 401", async ({ api }) => {
    const cc = api.connectWithToken("");
    try {
      await cc.sso.ldapAuth({
        domain: "nonexistent.example.com",
        username: "baduser",
        password: "badpass",
      });
      throw new Error("expected ldapAuth to reject");
    } catch (err) {
      expect(err).toBeInstanceOf(ConnectError);
      // 401 (invalid creds) or 404 (domain not found) — either is valid.
      expect([401, 404]).toContain((err as ConnectError).status);
    }
  });

  /**
   * TC-SSO-LDAP-002: LDAP auth with non-existent domain → 404 NotFound.
   */
  test("LDAP auth for non-existent domain returns 404", async ({ api }) => {
    const cc = api.connectWithToken("");
    try {
      await cc.sso.ldapAuth({
        domain: "no-such-domain.test",
        username: "user",
        password: "pass",
      });
      throw new Error("expected ldapAuth to reject");
    } catch (err) {
      expect(err).toBeInstanceOf(ConnectError);
      expect((err as ConnectError).status).toBe(404);
    }
  });
});
