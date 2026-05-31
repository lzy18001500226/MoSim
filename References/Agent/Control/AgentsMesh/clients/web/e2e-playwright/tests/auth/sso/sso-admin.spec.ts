// Migrated R5+: was REST `api.get/post/delete('/api/v1/admin/sso/configs')`,
// now `cc.ssoAdmin.*` (typed Connect, binary wire). Admin endpoints carry
// no org_slug — tenant is the whole platform, gated by is_system_admin.
import { test, expect } from "../../../fixtures/index";
import { ADMIN_USER } from "../../../helpers/env";
import { clearAuthRateLimit } from "../../../helpers/redis";
import { ConnectError } from "../../../helpers/connect-client";

/**
 * SSO Admin API tests — require system admin auth.
 */
test.describe("SSO Admin API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * TC-SSO-ADM-001: List SSO configs (admin)
   */
  test("admin lists SSO configs", async ({ api }) => {
    await api.loginAs(ADMIN_USER.email, ADMIN_USER.password);
    const cc = await api.connect();
    const res = await cc.ssoAdmin.listSSOConfigs({}) as { data: unknown[]; total: bigint };
    expect(Array.isArray(res.data)).toBe(true);
  });

  /**
   * TC-SSO-ADM-004: Non-admin gets 403
   */
  test("non-admin gets 403 on SSO admin endpoint", async ({ api }) => {
    // Default login is non-admin user.
    const cc = await api.connect();
    await expect(
      cc.ssoAdmin.listSSOConfigs({}),
    ).rejects.toMatchObject({ status: 403 });
  });

  /**
   * TC-SSO-ADM-003: Create and delete SSO config.
   * Connect maps the OIDC discovery failure to Internal (500) or
   * InvalidArgument (400). Both are acceptable; 0 = success path.
   */
  test("admin creates SSO config (or server error if OIDC validation fails)", async ({ api, db }) => {
    await api.loginAs(ADMIN_USER.email, ADMIN_USER.password);
    const cc = await api.connect();

    let createdId: bigint | null = null;
    try {
      const created = await cc.ssoAdmin.createSSOConfig({
        name: "E2E Test SSO",
        domain: "e2e-test-sso.example.com",
        protocol: "oidc",
        oidcClientId: "test-client-id",
        oidcClientSecret: "test-client-secret",
        oidcIssuerUrl: "https://e2e-test-sso.example.com",
      }) as { id: bigint };
      createdId = created.id;
      expect(createdId).toBeTruthy();
    } catch (err) {
      // OIDC discovery failure → Internal (500) or InvalidArgument (400).
      expect(err).toBeInstanceOf(ConnectError);
      expect([400, 500]).toContain((err as ConnectError).status);
    }

    if (createdId != null) {
      await cc.ssoAdmin.deleteSSOConfig({ id: createdId });
    }

    try { db.cleanup(`DELETE FROM sso_configs WHERE domain = 'e2e-test-sso.example.com'`); } catch { /* ignore */ }
  });

  /**
   * TC-SSO-ADM-005: Duplicate domain+protocol returns conflict.
   * Connect maps AlreadyExists → 409, InvalidArgument → 400.
   */
  test("duplicate domain+protocol returns error", async ({ api, db }) => {
    await api.loginAs(ADMIN_USER.email, ADMIN_USER.password);
    const cc = await api.connect();

    let firstId: bigint | null = null;
    try {
      const r1 = await cc.ssoAdmin.createSSOConfig({
        name: "E2E Dup SSO",
        domain: "e2e-dup-sso.example.com",
        protocol: "oidc",
        oidcClientId: "dup-client",
        oidcClientSecret: "dup-secret",
        oidcIssuerUrl: "https://e2e-dup-sso.example.com",
      }) as { id: bigint };
      firstId = r1.id;
    } catch {
      // First create failed (OIDC discovery error) — skip duplicate assertion.
      firstId = null;
    }

    if (firstId != null) {
      try {
        await cc.ssoAdmin.createSSOConfig({
          name: "E2E Dup SSO 2",
          domain: "e2e-dup-sso.example.com",
          protocol: "oidc",
          oidcClientId: "dup-client-2",
          oidcClientSecret: "dup-secret-2",
          oidcIssuerUrl: "https://e2e-dup-sso.example.com",
        });
        throw new Error("expected duplicate createSSOConfig to reject");
      } catch (err) {
        expect(err).toBeInstanceOf(ConnectError);
        expect([400, 409]).toContain((err as ConnectError).status);
      }
      await cc.ssoAdmin.deleteSSOConfig({ id: firstId });
    }

    try { db.cleanup(`DELETE FROM sso_configs WHERE domain = 'e2e-dup-sso.example.com'`); } catch { /* ignore */ }
  });
});
