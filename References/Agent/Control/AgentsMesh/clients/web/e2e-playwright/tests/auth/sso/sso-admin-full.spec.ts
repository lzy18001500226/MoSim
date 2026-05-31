// Migrated R5+: was REST `api.get/post/put/delete('/api/v1/admin/sso/configs')`,
// now `cc.ssoAdmin.*` (typed Connect, binary wire). Admin gated by
// is_system_admin; no org_slug field.
import { test, expect } from "../../../fixtures/index";
import { ADMIN_USER } from "../../../helpers/env";
import { clearAuthRateLimit } from "../../../helpers/redis";

/**
 * SSO Admin UI + API supplements.
 * Maps to: TC-SSO-ADM-001~009
 */
test.describe("SSO Admin Full", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /** TC-SSO-ADM-001: List SSO configs */
  test("list SSO configs with pagination", async ({ api }) => {
    await api.loginAs(ADMIN_USER.email, ADMIN_USER.password);
    const cc = await api.connect();
    const res = await cc.ssoAdmin.listSSOConfigs({}) as { data: unknown[]; total: bigint };
    expect(res).toBeTruthy();
    expect(Array.isArray(res.data)).toBe(true);
  });

  /** TC-SSO-ADM-002: Get single config (non-existent) — Connect: NotFound→404. */
  test("get non-existent SSO config returns 404", async ({ api }) => {
    await api.loginAs(ADMIN_USER.email, ADMIN_USER.password);
    const cc = await api.connect();
    await expect(
      cc.ssoAdmin.getSSOConfig({ id: BigInt(999999) }),
    ).rejects.toMatchObject({ status: 404 });
  });

  /** TC-SSO-ADM-003: Full CRUD with LDAP (avoids OIDC discovery). */
  test("SSO config CRUD with LDAP protocol", async ({ api }) => {
    await api.loginAs(ADMIN_USER.email, ADMIN_USER.password);
    const cc = await api.connect();

    // Create LDAP config (doesn't need external IdP)
    const created = await cc.ssoAdmin.createSSOConfig({
      name: "E2E LDAP CRUD",
      domain: "e2e-ldap-crud.example.com",
      protocol: "ldap",
      ldapHost: "ldap.example.com",
      ldapPort: 389,
      ldapBaseDn: "dc=example,dc=com",
      ldapBindDn: "cn=admin,dc=example,dc=com",
      ldapBindPassword: "test-password",
    }) as { id: bigint };
    expect(created.id).toBeTruthy();
    const id = created.id;

    // Read
    const got = await cc.ssoAdmin.getSSOConfig({ id }) as { id: bigint };
    expect(got.id).toBe(id);

    // Update
    const updated = await cc.ssoAdmin.updateSSOConfig({
      id,
      name: "E2E LDAP CRUD Updated",
      ldapHost: "ldap2.example.com",
      ldapPort: 636,
      ldapBaseDn: "dc=example,dc=com",
      ldapBindDn: "cn=admin,dc=example,dc=com",
      ldapBindPassword: "updated-password",
    }) as { name: string };
    expect(updated.name).toBe("E2E LDAP CRUD Updated");

    // Delete
    await cc.ssoAdmin.deleteSSOConfig({ id });

    // Confirm deleted → 404 NotFound
    await expect(
      cc.ssoAdmin.getSSOConfig({ id }),
    ).rejects.toMatchObject({ status: 404 });
  });

  /** TC-SSO-ADM-004: Unauthorized access */
  test("non-admin cannot access SSO admin endpoints", async ({ api }) => {
    // Default user is non-admin
    const cc = await api.connect();
    await expect(
      cc.ssoAdmin.listSSOConfigs({}),
    ).rejects.toMatchObject({ status: 403 });
  });

  /** TC-SSO-ADM-005: Enable/disable config */
  test("enable and disable SSO config", async ({ api }) => {
    await api.loginAs(ADMIN_USER.email, ADMIN_USER.password);
    const cc = await api.connect();

    // LDAP doesn't depend on an external IdP — create must succeed.
    const created = await cc.ssoAdmin.createSSOConfig({
      name: "E2E Toggle SSO",
      domain: `e2e-toggle-${Date.now()}.example.com`,
      protocol: "ldap",
      ldapHost: "ldap.example.com",
      ldapPort: 389,
      ldapBaseDn: "dc=example,dc=com",
      ldapBindDn: "cn=admin,dc=example,dc=com",
      ldapBindPassword: "test",
    }) as { id: bigint };
    const id = created.id;
    expect(id, "SSO config must be created").toBeTruthy();

    // Enable
    const enabled = await cc.ssoAdmin.enableSSOConfig({ id }) as { isEnabled: boolean };
    expect(enabled.isEnabled).toBe(true);

    // Disable
    const disabled = await cc.ssoAdmin.disableSSOConfig({ id }) as { isEnabled: boolean };
    expect(disabled.isEnabled).toBe(false);

    // Cleanup
    await cc.ssoAdmin.deleteSSOConfig({ id });
  });
});
