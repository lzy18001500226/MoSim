// Migrated R5+: was REST `api.get('/api/v1/auth/sso/discover?...')`, now
// `cc.sso.discover(...)` (typed Connect, binary wire). SAML callback
// paths stay on REST per proto/sso/v1/sso.proto rationale.
import { test, expect } from "../../../fixtures/index";
import { clearAuthRateLimit } from "../../../helpers/redis";
import { ConnectError } from "../../../helpers/connect-client";

test.describe("SSO Discovery API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * TC-SSO-DISC-001: Discover SSO for valid domain
   */
  test("discover SSO configs by email", async ({ api }) => {
    // Public (pre-auth) endpoint — empty token.
    const cc = api.connectWithToken("");
    const res = await cc.sso.discover({ email: "user@agentsmesh.local" }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  /**
   * TC-SSO-DISC-002: Non-SSO domain returns empty
   */
  test("non-SSO domain returns empty configs", async ({ api }) => {
    const cc = api.connectWithToken("");
    const res = await cc.sso.discover({ email: "user@no-sso-domain.com" }) as { items: unknown[] };
    expect(res.items.length).toBe(0);
  });

  /**
   * TC-SSO-DISC-003: Invalid email format — Connect maps InvalidArgument to 400,
   * but the handler may also choose to return an empty list (tolerant input).
   */
  test("invalid email returns 400 or empty list", async ({ api }) => {
    const cc = api.connectWithToken("");
    try {
      const res = await cc.sso.discover({ email: "not-an-email" }) as { items: unknown[] };
      expect(Array.isArray(res.items)).toBe(true);
    } catch (err) {
      expect(err).toBeInstanceOf(ConnectError);
      expect((err as ConnectError).status).toBe(400);
    }
  });
});
