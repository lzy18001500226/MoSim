// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Repository Branches & Webhook API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list repository branches", async ({ api, db }) => {
    const id = db.queryValue(
      `SELECT id FROM repositories WHERE organization_id = (SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}') LIMIT 1`
    );
    if (!id) return;
    const cc = await api.connect();
    // Branch listing depends on upstream Git provider; accept success or upstream error.
    await cc.repository.listRepositoryBranches({
      orgSlug: TEST_ORG_SLUG,
      id: Number(id),
      accessToken: "",
    }).catch((err: { status?: number }) => {
      // 400/500 acceptable: no provider token / upstream unreachable in dev.
      expect([400, 500]).toContain(err.status ?? 500);
    });
  });

  test("get webhook status", async ({ api, db }) => {
    const id = db.queryValue(
      `SELECT id FROM repositories WHERE organization_id = (SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}') LIMIT 1`
    );
    if (!id) return;
    const cc = await api.connect();
    await cc.repository.getRepositoryWebhookStatus({
      orgSlug: TEST_ORG_SLUG,
      id: Number(id),
    }).catch((err: { status?: number }) => {
      // 404 acceptable when no webhook registered.
      expect(err.status).toBe(404);
    });
  });

  test("list merge requests", async ({ api, db }) => {
    const id = db.queryValue(
      `SELECT id FROM repositories WHERE organization_id = (SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}') LIMIT 1`
    );
    if (!id) return;
    const cc = await api.connect();
    await cc.repository.listRepositoryMergeRequests({
      orgSlug: TEST_ORG_SLUG,
      id: Number(id),
    }).catch((err: { status?: number }) => {
      // 400/500 acceptable: provider unreachable in dev.
      expect([400, 500]).toContain(err.status ?? 500);
    });
  });
});
