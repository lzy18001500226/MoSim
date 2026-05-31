// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { makeConnectClient } from "../../helpers/connect-client";

test.describe("Runner API CRUD", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list runners returns array", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.runner.listRunners({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(items)).toBe(true);
  });

  test("list runners without auth returns 401", async () => {
    const cc = makeConnectClient("bad-token");
    await expect(
      cc.runner.listRunners({ orgSlug: TEST_ORG_SLUG }),
    ).rejects.toMatchObject({ status: 401 });
  });

  test("list available runners", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.runner.listAvailableRunners({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("get runner by id", async ({ api, db }) => {
    const id = db.queryValue(
      `SELECT id FROM runners WHERE organization_id = (SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}') LIMIT 1`
    );
    expect(id, "dev seed must include at least one runner").toBeTruthy();

    const cc = await api.connect();
    const res = await cc.runner.getRunner({ orgSlug: TEST_ORG_SLUG, id: Number(id) }) as { runner: { id?: number } };
    expect(res.runner?.id).toBeTruthy();
  });

  test("get non-existent runner returns 404", async ({ api }) => {
    const cc = await api.connect();
    await expect(
      cc.runner.getRunner({ orgSlug: TEST_ORG_SLUG, id: 999999 }),
    ).rejects.toMatchObject({ status: 404 });
  });

  test("update runner description", async ({ api, db }) => {
    db.setup(`
      INSERT INTO runners (organization_id, node_id, description, status, max_concurrent_pods, is_enabled)
      SELECT id, 'test-runner-config', 'Config Test', 'offline', 5, true
      FROM organizations WHERE slug = '${TEST_ORG_SLUG}'
      ON CONFLICT (organization_id, node_id) DO UPDATE SET description = NULL
    `);
    const id = db.queryValue(
      `SELECT id FROM runners WHERE node_id = 'test-runner-config'`
    );

    const cc = await api.connect();
    await cc.runner.updateRunner({
      orgSlug: TEST_ORG_SLUG,
      id: Number(id),
      description: "Updated by E2E test",
    });

    const desc = db.queryValue(
      `SELECT description FROM runners WHERE node_id = 'test-runner-config'`
    );
    expect(desc).toContain("Updated by E2E");

    db.cleanup(`DELETE FROM runners WHERE node_id = 'test-runner-config'`);
  });

  test("disable and enable runner", async ({ api, db }) => {
    db.setup(`
      INSERT INTO runners (organization_id, node_id, description, status, max_concurrent_pods, is_enabled)
      SELECT id, 'test-runner-disable', 'Disable Test', 'offline', 5, true
      FROM organizations WHERE slug = '${TEST_ORG_SLUG}'
      ON CONFLICT (organization_id, node_id) DO UPDATE SET is_enabled = true
    `);
    const id = db.queryValue(
      `SELECT id FROM runners WHERE node_id = 'test-runner-disable'`
    );

    const cc = await api.connect();
    await cc.runner.updateRunner({ orgSlug: TEST_ORG_SLUG, id: Number(id), isEnabled: false });

    let flag = db.queryValue(
      `SELECT is_enabled::text FROM runners WHERE node_id = 'test-runner-disable'`
    );
    expect(flag).toBe("false");

    await cc.runner.updateRunner({ orgSlug: TEST_ORG_SLUG, id: Number(id), isEnabled: true });

    flag = db.queryValue(
      `SELECT is_enabled::text FROM runners WHERE node_id = 'test-runner-disable'`
    );
    expect(flag).toBe("true");

    db.cleanup(`DELETE FROM runners WHERE node_id = 'test-runner-disable'`);
  });

  test("delete runner", async ({ api, db }) => {
    db.setup(`
      INSERT INTO runners (organization_id, node_id, description, status, max_concurrent_pods, is_enabled)
      SELECT id, 'test-runner-delete', 'Delete Test', 'offline', 5, true
      FROM organizations WHERE slug = '${TEST_ORG_SLUG}'
      ON CONFLICT (organization_id, node_id) DO NOTHING
    `);
    const id = db.queryValue(
      `SELECT id FROM runners WHERE node_id = 'test-runner-delete'`
    );

    const cc = await api.connect();
    await cc.runner.deleteRunner({ orgSlug: TEST_ORG_SLUG, id: Number(id) });

    await expect(
      cc.runner.getRunner({ orgSlug: TEST_ORG_SLUG, id: Number(id) }),
    ).rejects.toMatchObject({ status: 404 });
  });
});
