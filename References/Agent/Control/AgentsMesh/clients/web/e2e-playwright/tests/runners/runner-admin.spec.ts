// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { ADMIN_USER, TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

/**
 * Runner admin tests — require system admin auth. Goes through AdminService
 * (proto.admin.v1) — distinct from the org-scoped RunnerService.
 */
test.describe("Runner Admin API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("admin lists all runners across orgs", async ({ api }) => {
    await api.loginAs(ADMIN_USER.email, ADMIN_USER.password);
    const cc = await api.connect();
    const res = await cc.admin.listRunners({}) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("non-admin gets permission_denied on admin runners endpoint", async ({ api }) => {
    // Default login is non-admin user
    const cc = await api.connect();
    // Connect maps the admin interceptor's permission check to HTTP 403.
    await expect(
      cc.admin.listRunners({}),
    ).rejects.toMatchObject({ status: 403 });
  });

  test("admin gets single runner detail", async ({ api, db }) => {
    db.setup(`
      INSERT INTO runners (organization_id, node_id, description, status, max_concurrent_pods, is_enabled)
      SELECT id, 'admin-single-test', 'Admin Single Test', 'offline', 5, true
      FROM organizations WHERE slug = '${TEST_ORG_SLUG}'
      ON CONFLICT (organization_id, node_id) DO NOTHING
    `);
    const id = db.queryValue(
      `SELECT id FROM runners WHERE node_id = 'admin-single-test'`
    );

    await api.loginAs(ADMIN_USER.email, ADMIN_USER.password);
    const cc = await api.connect();
    const runner = await cc.admin.getRunner({ runnerId: Number(id) }) as { id?: number };
    expect(runner.id).toBeTruthy();

    db.cleanup(`DELETE FROM runners WHERE node_id = 'admin-single-test'`);
  });

  test("admin disables and enables runner", async ({ api, db }) => {
    db.setup(`
      INSERT INTO runners (organization_id, node_id, description, status, max_concurrent_pods, is_enabled)
      SELECT id, 'admin-disable-test', 'Admin Disable Test', 'offline', 5, true
      FROM organizations WHERE slug = '${TEST_ORG_SLUG}'
      ON CONFLICT (organization_id, node_id) DO UPDATE SET is_enabled = true
    `);
    const id = db.queryValue(
      `SELECT id FROM runners WHERE node_id = 'admin-disable-test'`
    );

    await api.loginAs(ADMIN_USER.email, ADMIN_USER.password);
    const cc = await api.connect();

    await cc.admin.disableRunner({ runnerId: Number(id) });
    expect(db.queryValue(
      `SELECT is_enabled::text FROM runners WHERE node_id = 'admin-disable-test'`
    )).toBe("false");

    await cc.admin.enableRunner({ runnerId: Number(id) });
    expect(db.queryValue(
      `SELECT is_enabled::text FROM runners WHERE node_id = 'admin-disable-test'`
    )).toBe("true");

    db.cleanup(`DELETE FROM runners WHERE node_id = 'admin-disable-test'`);
  });

  test("admin deletes runner", async ({ api, db }) => {
    db.setup(`
      INSERT INTO runners (organization_id, node_id, description, status, max_concurrent_pods, is_enabled)
      SELECT id, 'admin-delete-test', 'Admin Delete Test', 'offline', 5, true
      FROM organizations WHERE slug = '${TEST_ORG_SLUG}'
      ON CONFLICT (organization_id, node_id) DO NOTHING
    `);
    const id = db.queryValue(
      `SELECT id FROM runners WHERE node_id = 'admin-delete-test'`
    );

    await api.loginAs(ADMIN_USER.email, ADMIN_USER.password);
    const cc = await api.connect();
    await cc.admin.deleteRunner({ runnerId: Number(id) });

    await expect(
      cc.admin.getRunner({ runnerId: Number(id) }),
    ).rejects.toMatchObject({ status: 404 });
  });
});
