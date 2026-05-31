// Migrated R5+: SAML metadata fetch + assertion callback intentionally
// STAY ON REST — per proto/sso/v1/sso.proto preamble: "The OIDC/SAML
// browser-redirect flows stay on REST (they terminate in `Location:`
// redirects, not protobuf bodies — Connect's unary contract cannot model
// that)." Use fetchWithRetry directly to assert on raw HTTP status.
import { test, expect } from "../../../fixtures/index";
import { clearAuthRateLimit } from "../../../helpers/redis";

test.describe("SSO SAML API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * TC-SSO-SAML-002: SAML metadata for non-existent domain returns 404.
   * REST-only — SAML metadata is XML, not proto.
   */
  test("SAML metadata for non-existent domain returns 404", async ({ api }) => {
    const res = await api.fetchWithRetry(
      `${api.getBaseUrl()}/api/v1/auth/sso/nonexistent.example.com/saml/metadata`,
      { method: "GET" },
    );
    expect(res.status).toBe(404);
  });
});
