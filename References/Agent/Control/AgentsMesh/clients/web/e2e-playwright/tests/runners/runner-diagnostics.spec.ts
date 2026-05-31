// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Runner Diagnostics API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list runner pods", async ({ api, db }) => {
    const id = db.queryValue(
      `SELECT id FROM runners WHERE organization_id = (SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}') LIMIT 1`
    );
    if (!id) return;
    const cc = await api.connect();
    const res = await cc.pod.listPods({
      orgSlug: TEST_ORG_SLUG,
      runnerId: Number(id),
    }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("list runner logs", async ({ api, db }) => {
    const id = db.queryValue(
      `SELECT id FROM runners WHERE organization_id = (SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}') LIMIT 1`
    );
    if (!id) return;
    const cc = await api.connect();
    const res = await cc.runner.listRunnerLogs({
      orgSlug: TEST_ORG_SLUG,
      id: Number(id),
    }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("list runner tokens", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.runner.listRunnerTokens({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("create and delete runner token", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.runner.createRunnerToken({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E test token",
    }) as { id?: number; token?: string };
    expect(created.token).toBeTruthy();
    if (created.id != null) {
      await cc.runner.deleteRunnerToken({
        orgSlug: TEST_ORG_SLUG,
        id: Number(created.id),
      });
    }
  });
});
